from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from models.session import SessionState
from services.storage.session_store import session_store

router = APIRouter(prefix="/session", tags=["session"])
limiter = Limiter(key_func=get_remote_address)


@router.post("")
@limiter.limit("10/hour")
async def create_session(request: Request):
    session = SessionState()
    await session_store.create(session)
    return {"session_id": session.session_id, "status": session.status}


@router.get("/{session_id}")
async def get_session(session_id: str):
    session = await session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
