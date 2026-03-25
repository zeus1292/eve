from pathlib import Path
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models.session import ProductContext
from config import settings

PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "maturity_classification.txt"


class MaturityClassifier:
    def __init__(self) -> None:
        self._llm = ChatAnthropic(
            model="claude-haiku-4-5-20251001",
            api_key=settings.anthropic_api_key,
            max_tokens=16,
        )
        template = PROMPT_PATH.read_text()
        self._chain = PromptTemplate.from_template(template) | self._llm | StrOutputParser()

    async def classify(self, context: ProductContext) -> str:
        context_str = (
            f"Product: {context.product_name}\n"
            f"Domain: {context.domain}\n"
            f"AI Modality: {', '.join(context.ai_modality)}\n"
            f"Tech Stack: {', '.join(context.tech_stack)}\n"
            f"Summary: {context.raw_summary}\n"
            f"Maturity Hint: {context.maturity_hint or 'unknown'}"
        )
        result = await self._chain.ainvoke({"context": context_str})
        cleaned = result.strip().lower()
        return "production" if "production" in cleaned else "draft"
