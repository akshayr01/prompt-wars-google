# AGENTS.md — PromptWars Bangalore

## 🎯 Mission
Build a Gemini-powered app for **societal benefit** in 3 hours.
Win condition: iterate fast, read every score breakdown, and hit 100s on as many criteria as possible.

Real winner data from Hyderabad (1st Runner Up, 98.13%):
- Attempt 1: 85.25% (Rank 4)
- Attempt 2: 96.25% — added Google Translate, Cloud Logging, security hardening
- Attempt 3: 98.13% — added Firestore, Cloud Storage, Vertex AI, modular architecture
- Final: 8 Google Cloud services, 50+ tests, 6 perfect 100s

**Every decision optimises for this exact scoring rubric (in priority order):**
1. Google Services (depth + count — the biggest differentiator)
2. Security (most-missed criterion — address it explicitly)
3. Code Quality (modular architecture wins here)
4. Testing (50+ tests won Hyderabad — automate this)
5. Efficiency (response time, lazy loading)
6. Accessibility (a11y quick wins)

---

## 🏗️ Stack (Non-Negotiable)

| Layer | Choice | Why |
|---|---|---|
| Language | Python (FastAPI) or Node.js | Fastest Cloud Run deployment |
| AI | Gemini 1.5 Flash via Vertex AI SDK | Scores Google Services + AI criterion |
| Translation | Google Cloud Translation API | Hyderabad winner added this for +11% |
| Persistence | Firestore | Hyderabad winner added this for final +2% |
| File Storage | Cloud Storage | Extra Google Service point |
| Observability | Cloud Logging | Hyderabad winner added explicitly |
| Deployment | Cloud Run | Required for scoring |
| Auth (optional) | Firebase Auth | If time permits |

---

## 🔒 Security Rules (CRITICAL — was weak spot in round 1)

These are MANDATORY, not optional:

```python
# NEVER do this
API_KEY = "AIzaSy..."

# ALWAYS do this
import os
API_KEY = os.environ["GEMINI_API_KEY"]
```

Checklist (agent enforces before every submission):
- [ ] Zero hardcoded secrets anywhere in source
- [ ] All secrets in environment variables
- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` exists with all var names (no values)
- [ ] CORS headers set explicitly and restrictively
- [ ] Content-Security-Policy header on all responses
- [ ] Input validation on EVERY user-supplied field
- [ ] `textContent` never `innerHTML` for user data
- [ ] Rate limiting on API endpoints
- [ ] HTTPS only — no HTTP fallback

Python security template (always use):
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os, logging, re

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)

def validate_input(text: str, max_length: int = 5000) -> str:
    if not text or not isinstance(text, str):
        raise HTTPException(400, "Invalid input")
    text = text.strip()
    if len(text) > max_length:
        raise HTTPException(400, f"Input exceeds {max_length} chars")
    return text
```

---

## 🌐 Google Services Integration (DEPTH MATTERS MORE THAN COUNT)

Target: minimum 5 Google Cloud services, ideally 8.

Priority order (highest scoring impact first):

### 1. Vertex AI (Gemini) — Core AI
```python
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project=os.environ["GCP_PROJECT"], location="us-central1")
model = GenerativeModel("gemini-1.5-flash")

async def call_gemini(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        raise HTTPException(500, "AI generation failed")
```

### 2. Cloud Translation API — Add for languages/multilingual
```python
from google.cloud import translate_v2 as translate

translate_client = translate.Client()

def translate_text(text: str, target_lang: str = "en") -> str:
    result = translate_client.translate(text, target_language=target_lang)
    return result["translatedText"]
```

### 3. Cloud Logging — Add immediately, costs nothing
```python
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler

logging_client = google.cloud.logging.Client()
logging_client.setup_logging()
logger = logging.getLogger(__name__)

# Use throughout app
logger.info("Request processed", extra={"user_input_length": len(text), "lang": lang})
```

### 4. Firestore — For persistence/history
```python
from google.cloud import firestore

db = firestore.Client()

async def save_result(result: dict) -> str:
    doc_ref = db.collection("results").document()
    doc_ref.set({**result, "timestamp": firestore.SERVER_TIMESTAMP})
    return doc_ref.id

async def get_history(limit: int = 10) -> list:
    docs = db.collection("results").order_by(
        "timestamp", direction=firestore.Query.DESCENDING
    ).limit(limit).stream()
    return [doc.to_dict() for doc in docs]
```

### 5. Cloud Storage — For file uploads/exports
```python
from google.cloud import storage

storage_client = storage.Client()
bucket = storage_client.bucket(os.environ["GCS_BUCKET"])

def upload_result(content: str, filename: str) -> str:
    blob = bucket.blob(f"results/{filename}")
    blob.upload_from_string(content, content_type="application/json")
    return blob.public_url
```

### 6. Google Cloud Translation (v3 advanced)
```python
from google.cloud import translate_v3 as translate

def detect_and_translate(text: str) -> dict:
    client = translate.TranslationServiceClient()
    parent = f"projects/{os.environ['GCP_PROJECT']}/locations/global"
    detection = client.detect_language(parent=parent, content=text)
    translation = client.translate_text(
        parent=parent, contents=[text], target_language_code="en"
    )
    return {
        "detected_language": detection.languages[0].language_code,
        "translated_text": translation.translations[0].translated_text
    }
```

---




## 📊 Session Logging (Interaction Tracking)

Capture every interaction in a CSV file for auditing and session history. 

**Generic Implementation Pattern:**
```python
import csv, os
from datetime import datetime

def log_interaction(user_input: str, model_output: str, session_file: str = "sessions/log.csv"):
    """Generic function to append interaction to CSV with Sl. no."""
    os.makedirs("sessions", exist_ok=True)
    file_exists = os.path.isfile(session_file)
    
    # Get next Sl. no. accurately by counting existing rows
    sl_no = 1
    if file_exists:
        with open(session_file, 'r', encoding='utf-8') as f:
            sl_no = sum(1 for _ in f) # Sl. no is row count (includes header)

    with open(session_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Sl. no.", "Input", "Output", "Datetime"])
        
        writer.writerow([
            sl_no, 
            user_input.replace("\n", " "), 
            model_output.replace("\n", " "), 
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
```

---

## 📁 Project Structure (Modular — Required for Code Quality Score)

```
project-root/
├── AGENTS.md
├── README.md
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
├── main.py                     ← FastAPI app entry, routes only
├── src/
│   ├── __init__.py
│   ├── services/
│   │   ├── gemini_service.py   ← all Vertex AI / Gemini calls
│   │   ├── translate_service.py← Google Translate logic
│   │   ├── firestore_service.py← all Firestore operations
│   │   └── storage_service.py  ← Cloud Storage operations
│   ├── models/
│   │   └── schemas.py          ← Pydantic request/response models
│   ├── utils/
│   │   ├── validation.py       ← input sanitization
│   │   └── logging_config.py   ← Cloud Logging setup
│   └── config.py               ← env vars, constants
├── tests/
│   ├── test_gemini_service.py
│   ├── test_translate_service.py
│   ├── test_firestore_service.py
│   ├── test_validation.py
│   └── test_api_endpoints.py   ← integration tests
├── static/
│   ├── index.html
│   ├── styles.css
│   └── app.js
└── .agent/
    └── skills/
        ├── pw-google-services/
        ├── pw-security-hardening/
        ├── pw-test-generator/
        ├── pw-deploy-cloud-run/
        ├── pw-accessibility/
        └── pw-iterate-from-score/
```

---

## 🧪 Testing (50+ Tests Won Hyderabad)

Always generate tests alongside every service. Use `pytest`.

Minimum test counts per module:
- Each service: 8-10 tests (happy path + error cases + edge cases)
- API endpoints: 5 tests each (200, 400, 422, 500, large input)
- Validation utils: 10+ tests
- Total target: 50+

Run before every submission:
```bash
pytest tests/ -v --tb=short 2>&1 | tail -20
```

---

## ⚡ Dockerfile (Cloud Run Ready)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
```

---

## 🔄 Iteration Protocol (Based on Winner's Strategy)

**The winning loop — do this every attempt:**

1. Submit → Read score breakdown line by line
2. Find LOWEST scoring criterion
3. Use the `pw-iterate-from-score` skill with the exact score
4. Fix that criterion specifically — don't touch what's already 100
5. Run `pw-test-generator` skill to add tests for anything changed
6. Run `pw-security-hardening` skill
7. Run `pw-accessibility` skill
8. Commit: `git commit -m "attempt N: fix [criterion]"`
9. Deploy via `pw-deploy-cloud-run` skill
10. Submit

**Never patch blindly — always read the score first.**

---

## ✅ Pre-Submission Checklist (Run Before Every Attempt)

Security:
- [ ] `grep -r "AIza\|sk-\|api_key\s*=" src/` returns nothing
- [ ] `.env` in `.gitignore`
- [ ] CORS middleware present
- [ ] Input validation on all endpoints

Google Services:
- [ ] Vertex AI (Gemini) — integrated and called
- [ ] Cloud Logging — logs every request
- [ ] Firestore — at least one read + one write
- [ ] Cloud Translation — used if multilingual
- [ ] Cloud Storage — used if file handling needed
- [ ] Session Logging — interactions captured in `sessions/<datetime>.csv`
- [ ] Cloud Run — deployed and URL accessible

Testing:
- [ ] `pytest tests/ -v` passes with 0 failures
- [ ] Test count ≥ 50 (run: `pytest tests/ --collect-only | grep "test session" -A5`)

Code Quality:
- [ ] Services are in `src/services/` (modular)
- [ ] No function longer than 40 lines
- [ ] All functions have docstrings
- [ ] Pydantic models for all request/response

Accessibility:
- [ ] All buttons have `aria-label`
- [ ] All inputs have `<label>`
- [ ] Tab navigation works
- [ ] Contrast ratio passes (white on dark or dark on light)

Deployment:
- [ ] `docker build -t app .` succeeds locally
- [ ] Cloud Run URL is public (`--allow-unauthenticated`)
- [ ] App loads in browser at deployed URL
- [ ] README has one-command deploy instruction
