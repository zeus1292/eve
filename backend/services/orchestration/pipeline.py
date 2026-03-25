from pathlib import Path
from datetime import date
from typing import AsyncIterator
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models.session import SessionState
from config import settings

PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "eval_generation.txt"


class EvalPipeline:
    def __init__(self) -> None:
        self._llm = ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=settings.anthropic_api_key,
            max_tokens=8192,
            streaming=True,
        )
        self._template = PROMPT_PATH.read_text()

    async def stream(self, session: SessionState) -> AsyncIterator[str]:
        context = session.context
        answers = session.questionnaire_answers
        maturity = session.maturity

        attribute_weights = answers.get("attribute_weights", {})
        priority_order = answers.get("priority_order", list(attribute_weights.keys()))
        domain_specifics = answers.get("domain_specifics", {})

        phase_2_section = self._build_phase2_section(maturity)

        weights_str = "\n".join(
            f"- {attr}: {weight}/5" for attr, weight in sorted(attribute_weights.items(), key=lambda x: -x[1])
        ) or "Not specified — use sensible defaults for this domain."

        priority_str = ", ".join(priority_order) if priority_order else "Not specified"

        answers_str = "\n".join(
            f"- {k}: {v}" for k, v in {**answers, **domain_specifics}.items()
            if k not in ("attribute_weights", "priority_order", "domain_specifics")
        ) or "No additional answers provided."

        prompt = PromptTemplate.from_template(self._template)
        chain = prompt | self._llm | StrOutputParser()

        async for chunk in chain.astream({
            "context": self._format_context(context),
            "maturity": maturity,
            "attribute_weights": weights_str,
            "priority_order": priority_str,
            "questionnaire_answers": answers_str,
            "product_name": context.product_name if context else "AI Application",
            "date": date.today().isoformat(),
            "maturity_label": "Production" if maturity == "production" else "Draft / Prototype",
            "domain": context.domain if context else "AI Application",
            "phase_2_section": phase_2_section,
        }):
            yield chunk

    def _format_context(self, context) -> str:
        if not context:
            return "No context provided."
        return (
            f"Product Name: {context.product_name}\n"
            f"Domain: {context.domain}\n"
            f"AI Modality: {', '.join(context.ai_modality)}\n"
            f"Tech Stack: {', '.join(context.tech_stack)}\n"
            f"Key Features: {', '.join(context.key_features)}\n"
            f"Intended Users: {context.intended_users}\n"
            f"Summary: {context.raw_summary}"
        )

    def _build_phase2_section(self, maturity: str) -> str:
        if maturity != "production":
            return ""
        return """## Phase 2: Non-Functional & Edge Case Evals

[Generate non-functional evals for performance, safety, reliability, and edge cases specific to this product's domain and scale.]"""
