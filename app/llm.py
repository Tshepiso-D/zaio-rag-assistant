"""
Thin wrapper around the Anthropic Messages API for answer generation.
Generation is strictly grounded in the retrieved context passed in.
"""
from typing import List, Dict
import anthropic

from app.config import ANTHROPIC_API_KEY, GENERATION_MODEL, FALLBACK_MESSAGE

SYSTEM_PROMPT = f"""You are the ZAIO Student Assistant. You answer student questions using \
ONLY the context excerpts provided below (from the Student Handbook and the ZAIO website).

Rules:
- Base your answer strictly on the provided context. Do not use outside knowledge.
- If the context does not contain enough information to answer the question, respond \
with exactly this sentence and nothing else: "{FALLBACK_MESSAGE}"
- Keep answers concise and directly address the question.
- Do not mention "the context" or "excerpts" in your answer -- answer naturally, as if \
you simply know this information.
"""


def _client() -> anthropic.Anthropic:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Export it in your environment or a .env file."
        )
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def generate_answer(question: str, context_chunks: List[Dict]) -> str:
    """
    context_chunks: list of {"text": str, "display_source": str}
    """
    if not context_chunks:
        return FALLBACK_MESSAGE

    context_block = "\n\n".join(
        f"[Source: {c['display_source']}]\n{c['text']}" for c in context_chunks
    )

    user_message = (
        f"Context:\n{context_block}\n\n"
        f"Question: {question}\n\n"
        f"Answer the question using only the context above."
    )

    client = _client()
    response = client.messages.create(
        model=GENERATION_MODEL,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return "".join(block.text for block in response.content if block.type == "text").strip()
