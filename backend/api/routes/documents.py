import uuid
import json
import os
import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv

from rag_pipeline.loader import load_pdf, get_pdf_metadata
from rag_pipeline.chunker import chunk_pages
from rag_pipeline.vector_store import add_documents, delete_store, store_exists

load_dotenv()

router = APIRouter()

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "data/uploads"))
REGISTRY_FILE = Path("data/documents.json")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# --- simple JSON-based document registry (no DB needed for now) ---

def _load_registry() -> List[dict]:
    if not REGISTRY_FILE.exists():
        return []
    with open(REGISTRY_FILE) as f:
        return json.load(f)


def _save_registry(docs: List[dict]) -> None:
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_FILE, "w") as f:
        json.dump(docs, f, indent=2)


def _process_pdf(doc_id: str, file_path: str) -> None:
    pages = load_pdf(file_path)
    chunks = chunk_pages(pages, doc_id)
    add_documents(doc_id, chunks)

    # update status in registry
    docs = _load_registry()
    for d in docs:
        if d["id"] == doc_id:
            d["status"] = "ready"
            d["chunk_count"] = len(chunks)
            break
    _save_registry(docs)


# --- routes ---

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    doc_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{doc_id}.pdf"

    # save file to disk
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    # get basic metadata without blocking
    meta = get_pdf_metadata(str(save_path))

    doc_entry = {
        "id": doc_id,
        "filename": file.filename,
        "status": "processing",
        "chunk_count": 0,
        **meta,
    }

    docs = _load_registry()
    docs.append(doc_entry)
    _save_registry(docs)

    # process in background so upload returns fast
    background_tasks.add_task(_process_pdf, doc_id, str(save_path))

    return {"id": doc_id, "filename": file.filename, "status": "processing"}


@router.get("/")
async def list_documents():
    return _load_registry()


@router.get("/{doc_id}")
async def get_document(doc_id: str):
    docs = _load_registry()
    doc = next((d for d in docs if d["id"] == doc_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    docs = _load_registry()
    doc = next((d for d in docs if d["id"] == doc_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # remove file + vector store
    pdf_path = UPLOAD_DIR / f"{doc_id}.pdf"
    if pdf_path.exists():
        pdf_path.unlink()
    delete_store(doc_id)

    docs = [d for d in docs if d["id"] != doc_id]
    _save_registry(docs)
    return {"deleted": doc_id}
