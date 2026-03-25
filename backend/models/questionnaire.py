from pydantic import BaseModel
from typing import Any


class Question(BaseModel):
    question_id: str
    attribute: str
    question_text: str
    type: str  # single_choice | multi_choice | scale_1_5 | free_text
    options: list[str] = []
    follow_up_condition: dict[str, Any] | None = None


class QuestionnaireState(BaseModel):
    session_id: str
    stage: str = "INIT"
    questions: list[Question] = []
    answers: dict[str, Any] = {}
    attribute_weights: dict[str, int] = {}
    priority_order: list[str] = []
    maturity: str = "draft"
    complete: bool = False
