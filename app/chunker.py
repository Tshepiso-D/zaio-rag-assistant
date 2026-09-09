"""
Splits long text into overlapping chunks, trying to break on sentence/paragraph
boundaries where possible so each chunk stays semantically coherent.
"""
import re
from typing import List

from app.config import CHUNK_SIZE, CHUNK_OVERLAP

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    sentences = _SENTENCE_SPLIT_RE.split(text)
    chunks: List[str] = []
    current = ""

    for sentence in sentences:
        candidate = f"{current} {sentence}".strip() if current else sentence
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current.strip())
            # start new chunk, carrying over the tail of the previous chunk as overlap
            overlap_text = current[-overlap:] if current and overlap > 0 else ""
            current = f"{overlap_text} {sentence}".strip()
            # handle a single sentence longer than chunk_size: hard-split it
            while len(current) > chunk_size:
                chunks.append(current[:chunk_size].strip())
                current = current[chunk_size - overlap:]

    if current.strip():
        chunks.append(current.strip())

    return chunks
