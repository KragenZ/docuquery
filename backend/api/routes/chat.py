import uuid
import json
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from rag_pipeline.retriever import retrieve
from rag_pipeline.vector_store import store_exists
from models.llm import get_llm
from models.prompts import rag_prompt, compare_prompt

load_dotenv()

router = APIRouter()

SESSIONS_DIR = Path("data/sessions")
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


class QueryRequest(BaseModel):
    question: str
    doc_ids: List[str]
    session_id: Optional[str] = None
    compare_mode: bool = False  # triggers multi-doc comparison prompt


class Citation(BaseModel):
    source: str
    page_number: int
    excerpt: str
    doc_id: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
    session_id: str


def _session_path(session_id: str) -> Path:
    return SESSIONS_DIR / f"{session_id}.json"


def _load_history(session_id: str) -> List[dict]:
    p = _session_path(session_id)
    if not p.exists():
        return []
    with open(p) as f:
        return json.load(f)


def _save_message(session_id: str, role: str, content: str) -> None:
    history = _load_history(session_id)
    history.append({"role": role, "content": content})
    with open(_session_path(session_id), "w") as f:
        json.dump(history, f, indent=2)


@router.post("/query", response_model=QueryResponse)
async def query_documents(req: QueryRequest):
    # validate at least one doc is ready
    ready = [d for d in req.doc_ids if store_exists(d)]
    if not ready:
        raise HTTPException(
            status_code=400,
            detail="None of the selected documents are ready. Please wait for processing to complete."
        )

    session_id = req.session_id or str(uuid.uuid4())

    # retrieve relevant chunks
    results = retrieve(req.question, ready, k=5)
    if not results:
        return QueryResponse(
            answer="I couldn't find relevant information in the selected documents.",
            citations=[],
            session_id=session_id,
        )

    # build context string for the prompt
    context_parts = []
    citations = []
    for doc, score in results:
        m = doc.metadata
        excerpt = doc.page_content.strip()
        context_parts.append(
            f"[Source: {m['source']}, Page {m['page_number']}]\n{excerpt}"
        )
        citations.append(Citation(
            source=m["source"],
            page_number=m["page_number"],
            excerpt=excerpt[:300],  # truncate for UI
            doc_id=m["doc_id"],
            score=round(float(score), 4),
        ))

    context = "\n\n---\n\n".join(context_parts)

    # pick prompt based on mode
    if req.compare_mode and len(ready) > 1:
        from api.routes.documents import _load_registry
        registry = _load_registry()
        doc_names = [d["filename"] for d in registry if d["id"] in ready]
        prompt = compare_prompt
        prompt_input = {
            "context": context,
            "question": req.question,
            "doc_names": ", ".join(doc_names),
        }
    else:
        prompt = rag_prompt
        prompt_input = {"context": context, "question": req.question}

    llm = get_llm()
    chain = prompt | llm
    response = chain.invoke(prompt_input)
    answer = response.content

    # persist to session history
    _save_message(session_id, "user", req.question)
    _save_message(session_id, "assistant", answer)

    return QueryResponse(answer=answer, citations=citations, session_id=session_id)
