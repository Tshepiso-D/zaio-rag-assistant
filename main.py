"""
Part 3 & 5: JSON API for the ZAIO Student Assistant.

Run with:
    uvicorn main:app --reload --port 8000
"""
import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from app.rag import answer_question
from app.config import FALLBACK_MESSAGE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("zaio-rag-api")

app = FastAPI(
    title="ZAIO Student Assistant API",
    description="RAG assistant answering student questions from the Student Handbook and the ZAIO website.",
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def question_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("question must not be empty")
        return v.strip()


class AskResponse(BaseModel):
    answer: str
    source: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest):
    logger.info("Question received: %s", payload.question)
    result = answer_question(payload.question)
    return AskResponse(answer=result.answer, source=result.source)


# --- Graceful error handling (Part 5: n8n needs predictable JSON on failure) ---

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error while processing request")
    return JSONResponse(
        status_code=500,
        content={
            "answer": FALLBACK_MESSAGE,
            "source": "",
            "error": "internal_error",
            "detail": str(exc),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "answer": FALLBACK_MESSAGE,
            "source": "",
            "error": "invalid_request",
            "detail": exc.errors(),
        },
    )
