import json
import shutil
import asyncio
from pathlib import Path
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models.session import ProductContext
from config import settings

PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "git_summarization.txt"

SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", "__pycache__",
    ".next", "venv", ".venv", "env", ".env", "coverage",
    ".pytest_cache", ".mypy_cache",
}
PRIORITY_FILES = {
    "readme.md", "readme.rst", "readme.txt",
    "package.json", "pyproject.toml", "requirements.txt",
    "docker-compose.yml", "dockerfile",
}
PRIORITY_PATTERNS = {"*config*", "*prompt*", "*eval*", "*.env.example"}
CODE_EXTENSIONS = {".py", ".ts", ".js", ".tsx", ".jsx", ".go", ".rs", ".java"}
MAX_FILE_BYTES = 100 * 1024  # 100KB
MAX_TOTAL_CHARS = 50_000


class GitIngester:
    def __init__(self) -> None:
        self._llm = ChatAnthropic(
            model="claude-haiku-4-5-20251001",
            api_key=settings.anthropic_api_key,
            max_tokens=2048,
        )
        template = PROMPT_PATH.read_text()
        self._chain = PromptTemplate.from_template(template) | self._llm | StrOutputParser()

    async def extract(self, url: str, session_id: str) -> ProductContext:
        tmp_dir = Path(f"/tmp/eval_guide_{session_id}")
        try:
            await asyncio.wait_for(
                asyncio.to_thread(self._clone, url, tmp_dir),
                timeout=settings.git_clone_timeout_seconds,
            )
            repo_content = self._collect_files(tmp_dir)
            raw = await self._chain.ainvoke({"repo_content": repo_content})
            try:
                data = json.loads(raw.strip())
                return ProductContext(**data)
            except Exception:
                return ProductContext(raw_summary=repo_content[:2000])
        except asyncio.TimeoutError:
            raise ValueError(f"Git clone timed out after {settings.git_clone_timeout_seconds}s. Is the repository accessible?")
        except Exception as e:
            raise ValueError(f"Failed to clone repository: {str(e)}")
        finally:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir, ignore_errors=True)

    def _clone(self, url: str, dest: Path) -> None:
        import git
        git.Repo.clone_from(url, str(dest), depth=1, multi_options=["--single-branch"])

    def _collect_files(self, repo_dir: Path) -> str:
        priority: list[tuple[str, str]] = []
        secondary: list[tuple[str, str]] = []

        for path in repo_dir.rglob("*"):
            if not path.is_file():
                continue
            # Skip directories in the skip list
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            # Skip large files
            if path.stat().st_size > MAX_FILE_BYTES:
                continue

            rel = path.relative_to(repo_dir)
            name_lower = path.name.lower()

            try:
                text = path.read_text(errors="replace")
            except Exception:
                continue

            entry = (str(rel), text)

            if name_lower in PRIORITY_FILES:
                priority.insert(0, entry)
            elif any(path.match(pat) for pat in PRIORITY_PATTERNS):
                priority.append(entry)
            elif path.suffix in CODE_EXTENSIONS and len(path.parts) <= 3:
                # Top-level code files only
                secondary.append(entry)

        combined = ""
        for rel_path, content in (priority + secondary):
            block = f"\n\n### {rel_path}\n```\n{content[:3000]}\n```"
            if len(combined) + len(block) > MAX_TOTAL_CHARS:
                combined += "\n\n[Additional files truncated due to size limit]"
                break
            combined += block

        return combined or "No readable files found in repository."
