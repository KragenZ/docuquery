import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter()

SESSIONS_DIR = Path("data/sessions")


@router.get("/{session_id}")
async def get_session(session_id: str):
    p = SESSIONS_DIR / f"{session_id}.json"
    if not p.exists():
        raise HTTPException(status_code=404, detail="Session not found")
    with open(p) as f:
        return {"session_id": session_id, "messages": json.load(f)}


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    p = SESSIONS_DIR / f"{session_id}.json"
    if p.exists():
        p.unlink()
    return {"deleted": session_id}


@router.get("/")
async def list_sessions():
    SESSIONS_DIR.mkdir(exist_ok=True)
    sessions = []
    for f in sorted(SESSIONS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        sessions.append({"session_id": f.stem, "modified": f.stat().st_mtime})
    return sessions
