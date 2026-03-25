from fastapi import APIRouter, HTTPException
from models.session import SessionState, SessionStatus
from services.storage.session_store import session_store

router = APIRouter(prefix="/session", tags=["session"])


@router.post("")
async def create_session():
    session = SessionState()
    await session_store.create(session)
    return {"session_id": session.session_id, "status": session.status}


@router.get("/{session_id}")
async def get_session(session_id: str):
    session = await session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
