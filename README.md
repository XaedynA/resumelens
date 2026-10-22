# ResumeLens — Resume Analyzer

A local-first full-stack resume matching portfolio project built with **React, FastAPI, Python, and SQLite**.

![Stack](https://img.shields.io/badge/React-FastAPI-89e4b3)

## Features
- Upload a resume as PDF, DOCX, or TXT, or paste plain text.
- Paste a job description and receive transparent, evidence-linked requirement coverage.
- See matching skills, potential gaps, source passages from both texts, and actionable resume suggestions.
- Optional SQLite history (stores job title, score, and result summary; **not resume text**).
- Automated Python tests with GitHub Actions.
- Modern responsive dashboard.

**Important:** A percentage appears only when at least three recognized job requirements exist. It measures dictionary-recognized mentions, not candidate suitability. This version does not call an external AI model. It is a deterministic NLP-style baseline that can be extended with optional AI assistance later. Never invent qualifications to improve a score.

## Requirements
- Python **3.10+** (3.12 recommended)
- Node.js **18+** and npm

## Quick start

Open **Terminal 1**:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open **Terminal 2**:

```bash
cd frontend
npm install
npm run dev
```

Visit **http://127.0.0.1:5173**.

Backend docs: http://127.0.0.1:8000/docs

## Run tests
```bash
cd backend
source .venv/bin/activate
python -m pytest -v
```

## Architecture
`frontend/` React + Vite UI → `backend/app/main.py` FastAPI → `backend/app/analyzer.py` matching engine → optional SQLite database.

## Privacy
Files are parsed on your local backend. Only save if you select the history checkbox. History stores analysis results and job title, not raw resumes. Avoid uploading sensitive documents to a deployed public instance without adding authentication, retention policies, and security controls.

## Limitations
- Scanned PDFs without selectable text are not supported.
- Skill detection uses a finite dictionary and can miss synonyms or context.
- Skills mentioned in a resume are not verified.
- The score is for educational guidance only and should not be used to screen candidates. A missing keyword does not mean the applicant lacks the skill.

## Upgraded analysis
- Recognizes synonyms for common IT, cybersecurity, support, data, and programming skills.
- Distinguishes preferred from core requirements when those terms appear on the same line.
- Shows supporting excerpts from the job posting and resume.
- Suppresses unreliable percentages when fewer than three recognizable requirements exist.
- Offers transparent, evidence-based suggestions without fabricating experience.

## Roadmap
- User-controlled optional LLM feedback
- More robust extraction and synonym matching
- Skill evidence citations from resume sections
- Export a personalized improvement checklist

## License
MIT
