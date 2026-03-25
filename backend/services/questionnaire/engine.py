import json
from pathlib import Path
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models.session import SessionState
from models.questionnaire import Question, QuestionnaireState
from services.questionnaire.steerlm_attributes import STAGES, FUNCTIONAL_ATTRIBUTES, NON_FUNCTIONAL_ATTRIBUTES
from services.questionnaire.question_bank import FALLBACK_QUESTIONS
from services.orchestration.maturity_classifier import MaturityClassifier
from config import settings

PROMPT_PATH = Path(__file__).parent.parent.parent / "prompts" / "questionnaire_generation.txt"

STAGE_SEQUENCE = ["MATURITY_CONFIRM", "FUNCTIONAL_ATTRS", "CONDITIONAL_ATTRS", "DOMAIN_SPECIFIC", "COMPLETE"]


class QuestionnaireEngine:
    def __init__(self) -> None:
        self._llm = ChatAnthropic(
            model="claude-haiku-4-5-20251001",
            api_key=settings.anthropic_api_key,
            max_tokens=2048,
        )
        template = PROMPT_PATH.read_text()
        self._chain = PromptTemplate.from_template(template) | self._llm | StrOutputParser()
        self._classifier = MaturityClassifier()

    async def get_next(self, session: SessionState) -> dict:
        """Return the next set of questions for the current stage."""
        state = self._get_state(session)
        stage = state.get("stage", "MATURITY_CONFIRM")

        if stage == "COMPLETE":
            return {"stage": "COMPLETE", "questions": [], "complete": True}

        questions = await self._generate_questions(session, stage)
        return {
            "stage": stage,
            "questions": [q.model_dump() for q in questions],
            "complete": False,
            "maturity_suggestion": await self._classifier.classify(session.context) if session.context else "draft",
        }

    async def advance(self, session: SessionState, completed_stage: str, answers: dict) -> dict:
        """Process answers for a completed stage and return next stage info."""
        current_idx = STAGE_SEQUENCE.index(completed_stage) if completed_stage in STAGE_SEQUENCE else 0
        next_stage = STAGE_SEQUENCE[min(current_idx + 1, len(STAGE_SEQUENCE) - 1)]

        # Skip CONDITIONAL_ATTRS for draft products
        if next_stage == "CONDITIONAL_ATTRS" and session.maturity == "draft":
            next_stage = "DOMAIN_SPECIFIC"

        session.questionnaire_answers["_stage"] = next_stage
        from services.storage.session_store import session_store
        await session_store.update(session)

        if next_stage == "COMPLETE":
            return {"stage": "COMPLETE", "questions": [], "complete": True}

        questions = await self._generate_questions(session, next_stage)
        return {
            "stage": next_stage,
            "questions": [q.model_dump() for q in questions],
            "complete": False,
        }

    def _get_state(self, session: SessionState) -> dict:
        return {
            "stage": session.questionnaire_answers.get("_stage", "MATURITY_CONFIRM"),
        }

    async def _generate_questions(self, session: SessionState, stage: str) -> list[Question]:
        try:
            context_str = self._format_context(session)
            answers_str = json.dumps({
                k: v for k, v in session.questionnaire_answers.items() if not k.startswith("_")
            }, indent=2)

            attribute = self._stage_to_attribute(stage)
            raw = await self._chain.ainvoke({
                "context": context_str,
                "stage": stage,
                "attribute": attribute,
                "answers_so_far": answers_str,
            })
            data = json.loads(raw.strip())
            return [Question(**q) for q in data]
        except Exception:
            # Fall back to static questions
            return FALLBACK_QUESTIONS.get(stage, [])

    def _format_context(self, session: SessionState) -> str:
        if not session.context:
            return "No context available yet."
        c = session.context
        return (
            f"Product: {c.product_name}\nDomain: {c.domain}\n"
            f"AI Modality: {', '.join(c.ai_modality)}\nSummary: {c.raw_summary[:500]}"
        )

    def _stage_to_attribute(self, stage: str) -> str:
        mapping = {
            "MATURITY_CONFIRM": "maturity",
            "FUNCTIONAL_ATTRS": "correctness, task_completion, format_adherence, groundedness",
            "CONDITIONAL_ATTRS": "latency, safety, bias, coherence, cost",
            "DOMAIN_SPECIFIC": "domain-specific edge cases",
        }
        return mapping.get(stage, stage)
