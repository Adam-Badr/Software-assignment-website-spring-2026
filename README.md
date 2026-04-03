# Collaborative Document Editor with AI Writing Assistant PoC

This is our Software group repository by Adam, Ghaliah, Eldana and Abhra. 

## Technologies used

**Frontend**
- HTML
- CSS
- JavaScript

**Backend**
- Python
- FastAPI
- Uvicorn

## Repository Structure

```text
Software-assignment-website/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── auth.py
│   │   │   ├── permissions.py
│   │   │   └── store.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   └── routes/
│   │       ├── ai.py
│   │       ├── auth.py
│   │       └── documents.py
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── app.js
    └── styles.css
```

## What the PoC Supports

The PoC can currently do the following:

- user registration
- user login
- JWT-protected API access
- create document
- list accessible documents
- load document
- update document title/content
- register collaboration session
- invoke AI action asynchronously
- poll AI job status
- accept or reject AI suggestion

**Supported AI actions**
- rewrite
- summarize
- translate
- restructure

## What the PoC Does Not Fully Implement

Due to this being a minimal PoC, we intentionally do not implement:

- real-time collaborative editing over WebSocket
- cursor synchronization
- conflict resolution
- persistent database storage
- real external LLM integration
- full permissions UI
- revision history storage

Where appropriate, we have placeholders.

## Prerequisites

- Python 3.11+ or 3.12
- a terminal
- a web browser

No database or external AI provider is required.

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Adam-Badr/Software-assignment-website
cd Software-assignment-website
```

### 2. Start the backend

Open a terminal:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

On Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend should start on:

```text
http://localhost:8000
```

You can verify it by opening:

```text
http://localhost:8000/health
```

Expected response:

```json
{ "status": "ok" }
```

### 3. Start the frontend

Open a second terminal:

```bash
cd frontend
python -m http.server 5500
```

Then open this in your browser:

```text
http://localhost:5500/index.html
```

## How to Use the PoC

Run the following flow in the browser:

1. Register a new user  
2. Log in with the same credentials  
3. Create a document  
4. Refresh the document list  
5. Load the document  
6. Edit the title or content  
7. Save the document  
8. Paste some text into the AI Assistant area  
9. Choose an AI action  
10. Click **Invoke AI**  
11. Wait for polling to complete  
12. Click **Accept Suggestion** or **Reject Suggestion**  
13. Save the document again if you accepted the AI output  

## API Contract Alignment

The PoC is designed to validate the documented API contracts. It includes these endpoint groups.

**Authentication**
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

**Documents**
- `POST /api/v1/documents`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{document_id}`
- `PATCH /api/v1/documents/{document_id}`
- `DELETE /api/v1/documents/{document_id}`

**Collaboration session**
- `POST /api/v1/documents/{document_id}/session`

**AI**
- `POST /api/v1/documents/{document_id}/ai/invoke`
- `GET /api/v1/ai/jobs/{job_id}`
- `POST /api/v1/ai/jobs/{job_id}/accept`

## Notes on Storage

This PoC uses in-memory storage for:

- users
- documents
- permissions
- sessions
- AI jobs

That means all data is lost when the backend server stops. This is acceptable for the purpose of the proof of concept because the objective is to validate API contracts and end-to-end wiring without persistance.

## Authentication Notes

Protected endpoints require:

```text
Authorization: Bearer <jwt_token>
```

The frontend stores the token in browser local storage after login and sends it automatically on protected requests.

## AI Notes

The AI assistant in this PoC is mocked inside the backend. It does not call a real LLM provider.

This is intentional. The objective is to validate:

- the async request pattern
- job polling
- suggestion handling
- accept/reject workflow
- API contract shape

