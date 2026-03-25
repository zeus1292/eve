import json
import io
from pathlib import Path
from fastapi import UploadFile, HTTPException
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models.session import ProductContext
from config import settings

PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "context_extraction.txt"

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".py", ".ts", ".js", ".tsx", ".jsx", ".java", ".go", ".rs"}
MAX_BYTES = settings.max_file_size_mb * 1024 * 1024


class FileIngester:
    def __init__(self) -> None:
        self._llm = ChatAnthropic(
            model="claude-haiku-4-5-20251001",
            api_key=settings.anthropic_api_key,
            max_tokens=2048,
        )
        template = PROMPT_PATH.read_text()
        self._chain = PromptTemplate.from_template(template) | self._llm | StrOutputParser()
        self._splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)

    async def extract(self, upload: UploadFile) -> ProductContext:
        suffix = Path(upload.filename or "").suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

        content = await upload.read()
        if len(content) > MAX_BYTES:
            raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB.")

        text = self._parse(content, suffix)
        text = self._truncate(text)

        raw = await self._chain.ainvoke({"input_text": text})
        try:
            data = json.loads(raw.strip())
            return ProductContext(**data)
        except Exception:
            return ProductContext(raw_summary=text[:2000])

    def _parse(self, content: bytes, suffix: str) -> str:
        if suffix == ".pdf":
            return self._parse_pdf(content)
        return content.decode("utf-8", errors="replace")

    def _parse_pdf(self, content: bytes) -> str:
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(content))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(pages)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Could not parse PDF: {str(e)}. Scanned PDFs are not supported.")

    def _truncate(self, text: str, max_chars: int = 12000) -> str:
        if len(text) <= max_chars:
            return text
        chunks = self._splitter.split_text(text)
        # Take first few chunks that fit under max_chars
        result = ""
        for chunk in chunks:
            if len(result) + len(chunk) > max_chars:
                break
            result += chunk + "\n\n"
        return result
