# AI Research Agent MVP

A simple beginner-friendly AI research web app built with **FastAPI + HTML/CSS/JS**.

## Features
- Enter a research topic
- Generate a structured markdown research report
- Export report as PDF
- Automatically save reports locally in `/reports`
- Modern dark responsive UI

## Project Structure

```text
Research-agent7/
├── backend/
│   └── main.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── reports/
├── requirements.txt
└── README.md
```

## How It Works
1. User enters a topic in the browser.
2. Frontend sends `POST /api/research` to FastAPI.
3. Backend generates a structured markdown report.
4. Backend saves:
   - `.md` report
   - `.pdf` version
5. Frontend displays report and download links.

## Setup & Run Locally

### 1) Create virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows PowerShell
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Start the app

```bash
uvicorn backend.main:app --reload
```

### 4) Open in browser

Go to:

```text
http://127.0.0.1:8000
```

## API Endpoints
- `GET /api/health` - health check
- `POST /api/research` - generate markdown + PDF report
- `GET /api/reports/{filename}` - download saved report files

## Notes
- This MVP uses deterministic template-based report generation (no external LLM key required).
- You can later replace `build_markdown_report()` in `backend/main.py` with a real AI model call.
