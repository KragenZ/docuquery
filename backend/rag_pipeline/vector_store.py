import os
import shutil
from pathlib import Path
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from rag_pipeline.embedder import get_embeddings

VECTOR_DIR = Path(os.getenv("VECTOR_STORE_DIR", "data/vector_store"))


def _path(doc_id: str) -> Path:
    return VECTOR_DIR / doc_id


def add_documents(doc_id: str, chunks: List[Document]) -> None:
    embeddings = get_embeddings()
    p = _path(doc_id)

    if p.exists():
        store = FAISS.load_local(str(p), embeddings, allow_dangerous_deserialization=True)
        store.add_documents(chunks)
    else:
        store = FAISS.from_documents(chunks, embeddings)
        p.mkdir(parents=True, exist_ok=True)

    store.save_local(str(p))


def load_store(doc_id: str) -> Optional[FAISS]:
    p = _path(doc_id)
    if not p.exists():
        return None
    return FAISS.load_local(str(p), get_embeddings(), allow_dangerous_deserialization=True)


def merge_stores(doc_ids: List[str]) -> Optional[FAISS]:
    embeddings = get_embeddings()
    merged = None

    for doc_id in doc_ids:
        p = _path(doc_id)
        if not p.exists():
            continue
        store = FAISS.load_local(str(p), embeddings, allow_dangerous_deserialization=True)
        if merged is None:
            merged = store
        else:
            merged.merge_from(store)

    return merged


def delete_store(doc_id: str) -> bool:
    p = _path(doc_id)
    if p.exists():
        shutil.rmtree(str(p))
        return True
    return False


def store_exists(doc_id: str) -> bool:
    return _path(doc_id).exists()
