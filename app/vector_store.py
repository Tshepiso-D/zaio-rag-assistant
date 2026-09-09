"""
Handles embedding generation and storage/retrieval in ChromaDB.

Every stored chunk carries metadata:
  - source: "Student Handbook" or "ZAIO Website"
  - page:   int (handbook only)
  - url:    str (website only)
"""
import uuid
from typing import List, Dict, Any

import chromadb
from sentence_transformers import SentenceTransformer

from app.config import CHROMA_DB_DIR, EMBEDDING_MODEL_NAME, COLLECTION_NAME, TOP_K

_model = None


def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embedding_model()
    return model.encode(texts, show_progress_bar=False, normalize_embeddings=True).tolist()


class KnowledgeBase:
    """Thin wrapper around a persistent Chroma collection."""

    def __init__(self, persist_dir: str = CHROMA_DB_DIR, collection_name: str = COLLECTION_NAME):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def reset(self):
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[str], metadatas: List[Dict[str, Any]], batch_size: int = 64):
        """Embed and store chunks with their metadata, in batches."""
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size]
            embeddings = embed_texts(batch_chunks)
            ids = [str(uuid.uuid4()) for _ in batch_chunks]
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=batch_chunks,
                metadatas=batch_meta,
            )

    def query(self, question: str, top_k: int = TOP_K) -> Dict[str, Any]:
        query_embedding = embed_texts([question])[0]
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

    def count(self) -> int:
        return self.collection.count()
