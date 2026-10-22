import os
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from app.analyzer import analyze, extract_skills
from app import main

def test_no_false_confidence_for_single_word():
    result = analyze("Cybersecurity student", "Cybersecurity")
    assert result["score"] is None
    assert result["coverage"] == {"matched": 1, "recognized": 1}

def test_evidence_and_missing():
    result = analyze("Built Python tools and SQL reports.", "Required Python, SQL, Docker and AWS.")
    assert result["score"] == 50
    assert result["requirements"][0]["priority"] == "core"
    assert next(x for x in result["requirements"] if x["skill"] == "Python")["resume_evidence"]
    assert "Docker" in result["missing_skills"]

def test_synonyms_and_boundaries():
    assert "Testing" in extract_skills("Selenium and pytest")
    assert "Java" not in extract_skills("JavaScript")
    assert "Threat Detection" in extract_skills("intrusion detection")

def test_preferred_requirement():
    result = analyze("Python and Docker", "Python required\nDocker preferred\nAWS required")
    assert next(x for x in result["requirements"] if x["skill"] == "Docker")["priority"] == "preferred"

def test_api_end_to_end(monkeypatch):
    with tempfile.TemporaryDirectory() as folder:
        monkeypatch.setattr(main, "DB", Path(folder)/"test.sqlite3")
        with TestClient(main.app) as client:
            assert client.get("/api/health").json()["status"] == "ok"
            resp = client.post("/api/analyze", json={"resume_text":"Python, SQL, Docker", "job_description":"Python SQL Docker AWS", "save":True, "job_title":"Developer"})
            assert resp.status_code == 200
            assert resp.json()["score"] == 75
            hist = client.get("/api/history").json()
            assert len(hist) == 1 and hist[0]["job_title"] == "Developer"
            assert client.post("/api/extract", files={"file": ("resume.txt", b"Python developer", "text/plain")}).json()["text"] == "Python developer"
