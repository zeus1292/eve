from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
from models.session import SessionStatus
from services.storage.session_store import session_store
from services.questionnaire.engine import QuestionnaireEngine

router = APIRouter(prefix="/questionnaire", tags=["questionnaire"])
engine = QuestionnaireEngine()


@router.get("/{session_id}")
async def get_next_questions(session_id: str):
    session = await session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.context:
        raise HTTPException(status_code=400, detail="No context ingested yet")

    session.status = SessionStatus.questioning
    await session_store.update(session)

    result = await engine.get_next(session)
    return result


class AnswerRequest(BaseModel):
    answers: dict[str, Any]
    stage: str


@router.post("/{session_id}/answer")
async def submit_answers(session_id: str, request: AnswerRequest):
    session = await session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.questionnaire_answers.update(request.answers)
    await session_store.update(session)

    result = await engine.advance(session, request.stage, request.answers)
    return result


@router.post("/{session_id}/finalize")
async def finalize_questionnaire(session_id: str, body: dict[str, Any]):
    session = await session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.questionnaire_answers.update(body)
    session.maturity = body.get("maturity", "draft")
    await session_store.update(session)

    return {"session_id": session_id, "ready_for_generation": True}
