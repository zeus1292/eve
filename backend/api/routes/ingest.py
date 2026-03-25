from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from models.session import SessionStatus
from services.storage.session_store import session_store
from services.ingestion.text_ingester import TextIngester
from services.ingestion.file_ingester import FileIngester
from services.ingestion.git_ingester import GitIngester
from services.orchestration.context_builder import ContextBuilder

router = APIRouter(prefix="/ingest", tags=["ingest"])

text_ingester = TextIngester()
file_ingester = FileIngester()
git_ingester = GitIngester()
context_builder = ContextBuilder()


class TextIngestRequest(BaseModel):
    session_id: str
    text: str


class GitIngestRequest(BaseModel):
    session_id: str
    url: str


@router.post("/text")
async def ingest_text(request: TextIngestRequest):
    session = await session_store.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = SessionStatus.ingesting
    await session_store.update(session)

    context = await text_ingester.extract(request.text)
    session.context = context_builder.merge(session.context, context)
    session.status = SessionStatus.created
    await session_store.update(session)

    return {"session_id": session.session_id, "status": session.status, "context": session.context}


@router.post("/file")
async def ingest_file(
    session_id: str = Form(...),
    files: list[UploadFile] = File(...),
):
    session = await session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = SessionStatus.ingesting
    await session_store.update(session)

    for upload in files[:3]:  # max 3 files
        context = await file_ingester.extract(upload)
        session.context = context_builder.merge(session.context, context)

    session.status = SessionStatus.created
    await session_store.update(session)

    return {"session_id": session.session_id, "status": session.status, "files_processed": len(files[:3])}


@router.post("/git")
async def ingest_git(request: GitIngestRequest):
    session = await session_store.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.status = SessionStatus.ingesting
    await session_store.update(session)

    context = await git_ingester.extract(request.url, request.session_id)
    session.context = context_builder.merge(session.context, context)
    session.status = SessionStatus.created
    await session_store.update(session)

    return {"session_id": session.session_id, "status": session.status, "context": session.context}
