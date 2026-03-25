from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import re

from config import settings
from api.routes import session, ingest, questionnaire, eval_plan

app = FastAPI(title="Eval Framework Builder API", version="0.1.0")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def is_allowed_origin(origin: str) -> bool:
    allowed = settings.cors_origins_list
    if origin in allowed:
        return True
    # Allow all Vercel preview URLs
    if re.match(r"https://[a-z0-9-]+-[a-z0-9]+-[a-z]+\.vercel\.app", origin):
        return True
    return False


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://[a-z0-9-]+-[a-z0-9]+-[a-z]+\.vercel\.app",
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session.router)
app.include_router(ingest.router)
app.include_router(questionnaire.router)
app.include_router(eval_plan.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
