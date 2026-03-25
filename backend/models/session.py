from pydantic import BaseModel, Field
from enum import Enum
from typing import Any
from datetime import datetime, timezone
import uuid


class SessionStatus(str, Enum):
    created = "created"
    ingesting = "ingesting"
    questioning = "questioning"
    generating = "generating"
    complete = "complete"
    error = "error"


class ProductContext(BaseModel):
    product_name: str = "Unknown Product"
    domain: str = ""
    ai_modality: list[str] = []
    tech_stack: list[str] = []
    key_features: list[str] = []
    intended_users: str = ""
    maturity_hint: str | None = None
    raw_summary: str = ""


class SessionState(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: SessionStatus = SessionStatus.created
    context: ProductContext | None = None
    questionnaire_answers: dict[str, Any] = {}
    eval_plan: str | None = None
    maturity: str = "draft"
    error: str | None = None
