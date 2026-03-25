from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from services.storage.session_store import session_store
from services.orchestration.pipeline import EvalPipeline
from models.session import SessionStatus

router = APIRouter(prefix="/eval-plan", tags=["eval-plan"])
pipeline = EvalPipeline()


@router.get("/{session_id}")
async def generate_eval_plan(session_id: str):
    session = await session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.context:
        raise HTTPException(status_code=400, detail="No context ingested yet")

    session.status = SessionStatus.generating
    await session_store.update(session)

    async def stream_plan():
        full_text = ""
        try:
            async for chunk in pipeline.stream(session):
                full_text += chunk
                yield f"data: {chunk}\n\n"

            # Persist completed plan
            session.eval_plan = full_text
            session.status = SessionStatus.complete
            await session_store.update(session)
            yield "data: [DONE]\n\n"
        except Exception as e:
            session.status = SessionStatus.error
            session.error = str(e)
            await session_store.update(session)
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        stream_plan(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{session_id}/download")
async def download_eval_plan(session_id: str):
    session = await session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.eval_plan:
        raise HTTPException(status_code=400, detail="Eval plan not yet generated")

    filename = f"eval-framework-{session.context.product_name.lower().replace(' ', '-') if session.context else session_id}.md"

    return StreamingResponse(
        iter([session.eval_plan]),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
