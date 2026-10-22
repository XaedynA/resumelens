from contextlib import asynccontextmanager
from datetime import datetime, timezone
from io import BytesIO
import json
import os
import sqlite3
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pypdf import PdfReader
from docx import Document
from .analyzer import analyze

DB = Path(os.getenv("RESUME_DB_PATH", str(Path(__file__).resolve().parent.parent / "history.sqlite3")))
MAX_BYTES = 2 * 1024 * 1024

def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

@asynccontextmanager
async def lifespan(app):
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS analyses (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          created_at TEXT NOT NULL, job_title TEXT NOT NULL,
          score INTEGER, result_json TEXT NOT NULL
        )""")
    yield

app = FastAPI(title="ResumeLens API", version="1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_methods=["GET", "POST"], allow_headers=["*"])

class AnalysisRequest(BaseModel):
    resume_text: str = Field(min_length=1, max_length=100000)
    job_description: str = Field(min_length=1, max_length=100000)
    job_title: str = Field(default="Untitled role", max_length=200)
    save: bool = False

def save_result(title, result):
    with connect() as db:
        db.execute("INSERT INTO analyses(created_at,job_title,score,result_json) VALUES(?,?,?,?)",
                   (datetime.now(timezone.utc).isoformat(), title, result["score"], json.dumps(result)))

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/analyze")
def analyze_text(payload: AnalysisRequest):
    result = analyze(payload.resume_text, payload.job_description)
    if payload.save:
        save_result(payload.job_title, result)
    return result

@app.post("/api/extract")
async def extract(file: UploadFile = File(...)):
    name = (file.filename or "").lower()
    if not name.endswith((".pdf", ".docx", ".txt")):
        raise HTTPException(400, "Only PDF, DOCX, and TXT files are supported.")
    raw = await file.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, "File is too large (2 MB limit).")
    try:
        if name.endswith(".pdf"):
            text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(raw)).pages)
        elif name.endswith(".docx"):
            text = "\n".join(p.text for p in Document(BytesIO(raw)).paragraphs)
        else:
            text = raw.decode("utf-8")
    except Exception:
        raise HTTPException(422, "Could not extract text from this file.")
    if not text.strip():
        raise HTTPException(422, "No selectable text found. Scanned PDFs are not supported.")
    return {"text": text[:100000]}

@app.get("/api/history")
def history():
    with connect() as db:
        rows = db.execute("SELECT id, created_at, job_title, score FROM analyses ORDER BY id DESC LIMIT 50").fetchall()
    return [dict(row) for row in rows]
