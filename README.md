Quillium — PDF → Quizzes & Study Cards
=====================================

Overview
--------
Quillium converts PDF documents into interactive learning content: multiple-choice quizzes, study (flash) cards and a progress dashboard. The stack is a FastAPI backend for PDF processing and MCQ generation, and a Next.js + Tailwind CSS frontend.

Key features
- Upload a PDF and extract text
- Generate meaningful MCQs (English first, then translated to requested language)
- Produce study cards from MCQs
- Track simple progress (quizzes taken, accuracy, flashcards studied)
- Supports 50+ target languages for translation

Repository layout
-----------------
- backend/
  - app/: FastAPI app modules (main.py, mcq_generator.py, pdf_processor.py, etc.)
  - requirements.txt: backend Python deps
  - run.py: (helper, if present) launcher for the backend
- frontend/: Next.js + Tailwind frontend
  - src/app/: Next app routes and components
  - src/lib/: frontend utilities and API client
  - public/: static assets
- README.md (this file)

Prerequisites
-------------
- Node.js (v18+ recommended) and npm
- Python 3.10+ (or compatible) and pip

Environment variables
---------------------
Create a `.env` in `backend/` or set environment variables for the backend. Important variables:

- `GEMINI_API_KEY` — API key used for the Gemini / google-generativeai calls (set this to your key).
- `BACKEND_HOST` — host for backend (default `0.0.0.0`).
- `BACKEND_PORT` — port for backend (default `8000`).
- `ALLOWED_ORIGINS` — comma separated list of allowed origins, e.g. `http://localhost:3000`.

Frontend needs (optional):
- `NEXT_PUBLIC_API_URL` — the backend base URL used by the frontend (default `http://localhost:8000`).

Example `.env` (backend/.env)

GEMINI_API_KEY=your_api_key_here
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000

Setup & Run
-----------
Backend (Windows PowerShell):
```powershell
cd c:\Users\Jessy\quil2\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# then run server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Frontend (Windows PowerShell):
```powershell
cd c:\Users\Jessy\quil2\frontend
npm install
npm run dev
# open http://localhost:3000
```

How to use
----------
1. Open the frontend in your browser (by default http://localhost:3000).
2. Upload a PDF from the home page.
3. Choose a target language (defaults to English). The backend generates MCQs in English then translates to the selected language.
4. After processing you can take the quiz, open study cards, and view progress.

Developer notes
---------------
- MCQ generation and translation live in `backend/app/mcq_generator.py`.
- PDF text extraction uses PyMuPDF in `backend/app/pdf_processor.py`.
- Frontend navigation and header are in `frontend/src/app/components/layout`.
- The `RootLayoutClient.tsx` contains a small hash -> route redirect so the original "See Features" button works unchanged.

Troubleshooting
---------------
- If translations always return English, ensure `GEMINI_API_KEY` is set and valid.
- If uploads fail with CORS, confirm `ALLOWED_ORIGINS` includes your frontend origin.
- If `npm run dev` doesn't pick up changes, stop the dev server and restart it.

