from pydantic import BaseModel


class EvalItem(BaseModel):
    name: str
    description: str
    measurement_method: str
    sla_threshold: str
    priority: str  # Critical | High | Medium | Low
    effort: str    # Low | Medium | High
    phase: int     # 1 or 2


class EvalPlan(BaseModel):
    session_id: str
    product_name: str
    maturity: str
    markdown: str
    evals: list[EvalItem] = []
