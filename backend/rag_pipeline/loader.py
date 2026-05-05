"""RAG pipeline loader — pulls text out of PDFs page by page."""
import fitz
from pathlib import Path
from typing import List, Dict, Any


def load_pdf(file_path: str) -> List[Dict[str, Any]]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    doc = fitz.open(str(path))
    pages = []

    for i in range(len(doc)):
        text = doc[i].get_text("text")
        if not text.strip():
            continue
        pages.append({
            "text": text,
            "page_number": i + 1,
            "source": path.name,
            "file_path": str(path),
            "total_pages": len(doc),
        })

    doc.close()
    return pages


def get_pdf_metadata(file_path: str) -> Dict[str, Any]:
    path = Path(file_path)
    doc = fitz.open(str(path))
    meta = doc.metadata
    count = len(doc)
    doc.close()
    return {
        "title": meta.get("title") or path.stem,
        "author": meta.get("author", "Unknown"),
        "page_count": count,
        "file_size_kb": round(path.stat().st_size / 1024, 1),
    }
