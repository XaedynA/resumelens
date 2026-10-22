# ResumeLens — Resume Analyzer

![Quality checks](https://github.com/XaedynA/resumelens/actions/workflows/tests.yml/badge.svg)
A local-first full-stack resume matching portfolio project built with **React, FastAPI, Python, and SQLite**.

![Stack](https://img.shields.io/badge/React-FastAPI-89e4b3)

## Features
- Upload a resume as PDF, DOCX, or TXT, or paste plain text.
- Paste a job description and receive transparent, evidence-linked requirement coverage.
- See matching skills, potential gaps, source passages from both texts, and actionable resume suggestions.
- Optional SQLite history (stores job title, score, coverage, and matched/missing skill names; **no source passages in new records**).
- Automated Python tests with GitHub Actions.
- Modern responsive dashboard.

**Important:** A percentage appears only when at least three recognized job requirements exist. It measures dictionary-recognized mentions, not candidate suitability. This version does not call an external AI model. It is a deterministic NLP-style baseline that can be extended with optional AI assistance later. Never invent qualifications to improve a score.

## Requirements
- Python **3.10+** (3.12 recommended)
- Node.js **22.12+** and npm

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
npm ci
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
Files are parsed on your local backend. Only save if you select the history checkbox. New history records store job title, score, coverage, and skill names, without source passages. Earlier versions saved evidence excerpts: existing databases may still contain resume text. Clear history with `DELETE /api/history` to remove old records; backups may retain copies. Avoid uploading sensitive documents to a deployed public instance without adding authentication, retention policies, and security controls.

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

## API reliability and validation

| Route | Behavior |
| --- | --- |
| `GET /api/health` | Local health check |
| `POST /api/analyze` | Rejects blank inputs and text over 100,000 characters; saving is opt-in |
| `POST /api/extract` | PDF, DOCX and UTF-8 TXT; 2 MB file limit; rejects invalid/empty/oversized extraction |
| `GET /api/history` | Latest 50 summaries |
| `DELETE /api/history` | Deletes all local history records |

PDFs are limited to 50 pages; DOCX expanded content to 10 MB and 1,000 ZIP entries. Table cells are extracted from DOCX resumes. Parsing runs in a worker thread to keep the event loop responsive. PDF parsing is not a sandbox: only use trusted local documents; a hosted service needs isolated workers, CPU/memory limits, authentication, request-body limits at the proxy, and quotas.

Set `VITE_API_URL` before building to point to another backend. The default is `http://127.0.0.1:8000`. CORS allows the two local Vite origins. Do not expose the unauthenticated history API publicly.

CI runs backend regression tests on Python 3.11/3.12 and builds the React frontend with Node 22. JUnit and coverage reports are retained for 14 days. The suite covers malformed documents, blank and oversized input, zipped expansion limits, DOCX tables, opt-in storage and deletion.

## Public deployment

Set backend `PUBLIC_DEMO=true` and frontend build variable `VITE_PUBLIC_DEMO=true` to disable shared history. Set `ALLOWED_ORIGINS` to the exact frontend HTTPS origin and `VITE_API_URL` to the backend HTTPS origin. Use sample documents for a public portfolio demo. Run the API with `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT`. Build the frontend with `npm ci --prefix frontend && npm run build --prefix frontend`; publish `frontend/dist`.
