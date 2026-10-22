from contextlib import asynccontextmanager, closing
from datetime import datetime, timezone
import json
import os
import sqlite3
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from .analyzer import analyze

DB = Path(os.getenv("RESUME_DB_PATH", str(Path(__file__).resolve().parent.parent / "history.sqlite3")))
PUBLIC_DEMO = os.getenv("PUBLIC_DEMO", "false").lower() == "true"
MAX_BYTES = 2 * 1024 * 1024

def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

@asynccontextmanager
async def lifespan(app):
    if PUBLIC_DEMO:
        yield
        return
    with closing(connect()) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS analyses (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          created_at TEXT NOT NULL, job_title TEXT NOT NULL,
          score INTEGER, result_json TEXT NOT NULL
        )""")
        db.commit()
    yield

app = FastAPI(title="ResumeLens API", version="1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if x.strip()],
                   allow_methods=["GET", "POST", "DELETE"], allow_headers=["*"])

class AnalysisRequest(BaseModel):
    resume_text: str = Field(min_length=1, max_length=100000)
    job_description: str = Field(min_length=1, max_length=100000)
    job_title: str = Field(default="Untitled role", max_length=200)
    save: bool = False

    @field_validator("resume_text", "job_description")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("Text must contain non-whitespace characters")
        return value

def save_result(title, result):
    # History needs metadata only: do not persist source passages or resume evidence.
    summary = {key: result[key] for key in ("score", "coverage", "matched_skills", "missing_skills")}
    with closing(connect()) as db:
        db.execute("INSERT INTO analyses(created_at,job_title,score,result_json) VALUES(?,?,?,?)",
                   (datetime.now(timezone.utc).isoformat(), title, result["score"], json.dumps(summary)))
        db.commit()

@app.get("/api/health")
def health():
    return {"status": "ok", "history_enabled": not PUBLIC_DEMO}

@app.post("/api/analyze")
def analyze_text(payload: AnalysisRequest):
    if PUBLIC_DEMO and payload.save:
        raise HTTPException(403, "History is disabled on this public demo.")
    result = analyze(payload.resume_text, payload.job_description)
    if payload.save:
        save_result(payload.job_title, result)
    return result

@app.post("/api/extract")
def extract(file: UploadFile = File(...)):
    # A sync route runs CPU-bound parsing in FastAPI's worker thread pool.
    from .extraction import extract_text
    try:
        raw = file.file.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise HTTPException(413, "File is too large (2 MB limit).")
        return {"text": extract_text(file.filename or "", raw)}
    finally:
        file.file.close()

@app.get("/api/history")
def history():
    if PUBLIC_DEMO:
        return []
    with closing(connect()) as db:
        rows = db.execute("SELECT id, created_at, job_title, score FROM analyses ORDER BY id DESC LIMIT 50").fetchall()
    return [dict(row) for row in rows]

@app.delete("/api/history", status_code=204)
def clear_history():
    if PUBLIC_DEMO:
        raise HTTPException(403, "History is disabled on this public demo.")
    with closing(connect()) as db:
        db.execute("DELETE FROM analyses")
        db.commit()
