import json
from pathlib import Path
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models.session import ProductContext
from config import settings

PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "context_extraction.txt"


class TextIngester:
    def __init__(self) -> None:
        self._llm = ChatAnthropic(
            model="claude-haiku-4-5-20251001",
            api_key=settings.anthropic_api_key,
            max_tokens=2048,
        )
        template = PROMPT_PATH.read_text()
        self._chain = PromptTemplate.from_template(template) | self._llm | StrOutputParser()

    async def extract(self, text: str) -> ProductContext:
        raw = await self._chain.ainvoke({"input_text": text})
        try:
            data = json.loads(raw.strip())
            return ProductContext(**data)
        except Exception:
            # Graceful fallback — keep the raw text as summary
            return ProductContext(raw_summary=text[:2000])
