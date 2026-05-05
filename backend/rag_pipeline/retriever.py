import os
from typing import List, Tuple
from langchain_core.documents import Document
from rag_pipeline.vector_store import merge_stores

K = int(os.getenv("RETRIEVER_K", "5"))


def retrieve(query: str, doc_ids: List[str], k: int = K) -> List[Tuple[Document, float]]:
    store = merge_stores(doc_ids)
    if store is None:
        return []

    # try MMR first — keeps results diverse, avoids repetitive chunks
    try:
        emb = store.embedding_function(query)
        results = store.max_marginal_relevance_search_with_score_by_vector(
            emb, k=k, fetch_k=min(k * 3, 20)
        )
    except Exception:
        # fallback to plain similarity search
        results = store.similarity_search_with_score(query, k=k)

    results.sort(key=lambda x: x[1])
    return results
