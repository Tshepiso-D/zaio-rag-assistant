"""
Part 2: Given a question, retrieve relevant chunks across both knowledge
sources and generate a grounded answer, or refuse if nothing relevant is found.
"""
from dataclasses import dataclass, field
from typing import List, Dict

from app.config import TOP_K, MAX_RELEVANT_DISTANCE, FALLBACK_MESSAGE
from app.vector_store import KnowledgeBase
from app.llm import generate_answer

_kb = None


def get_kb() -> KnowledgeBase:
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
    return _kb


@dataclass
class RagResult:
    answer: str
    source: str
    retrieved: List[Dict] = field(default_factory=list)


def answer_question(question: str, top_k: int = TOP_K) -> RagResult:
    kb = get_kb()

    if kb.count() == 0:
        return RagResult(answer=FALLBACK_MESSAGE, source="")

    results = kb.query(question, top_k=top_k)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        return RagResult(answer=FALLBACK_MESSAGE, source="")

    # Filter to chunks that are actually relevant (cosine distance below threshold)
    relevant = [
        {"text": doc, "meta": meta, "distance": dist}
        for doc, meta, dist in zip(documents, metadatas, distances)
        if dist <= MAX_RELEVANT_DISTANCE
    ]

    if not relevant:
        return RagResult(answer=FALLBACK_MESSAGE, source="", retrieved=[])

    context_chunks = [
        {"text": r["text"], "display_source": r["meta"]["display_source"]}
        for r in relevant
    ]

    answer = generate_answer(question, context_chunks)

    if answer.strip() == FALLBACK_MESSAGE:
        return RagResult(answer=FALLBACK_MESSAGE, source="", retrieved=relevant)

    # Best (most relevant) chunk determines the primary cited source
    best = min(relevant, key=lambda r: r["distance"])
    source = best["meta"]["display_source"]

    return RagResult(answer=answer, source=source, retrieved=relevant)
