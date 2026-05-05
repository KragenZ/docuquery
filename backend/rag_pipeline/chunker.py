"""Chunking — splits pages into overlapping windows with metadata."""
import os
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def chunk_pages(pages: List[Dict[str, Any]], doc_id: str) -> List[Document]:
    docs = []
    for page in pages:
        raw = _splitter.split_text(page["text"])
        for idx, chunk in enumerate(raw):
            if len(chunk.strip()) < 50:
                continue
            docs.append(Document(
                page_content=chunk,
                metadata={
                    "doc_id": doc_id,
                    "source": page["source"],
                    "page_number": page["page_number"],
                    "total_pages": page["total_pages"],
                    "chunk_index": idx,
                    "file_path": page["file_path"],
                },
            ))
    return docs
