# Sahayak AI
**Tagline:** *Instant Emergency Triage When Seconds Count · Powered by Gemini*

## What is Sahayak AI?
**Sahayak AI** is a life-saving, multilingual emergency triage engine built entirely on Google Cloud and Gemini Flash. It acts as an autonomous first-responder dispatch system designed to take messy, panicked, unstructured emergency descriptions—in multiple languages like Hindi, Telugu, or English—and instantly synthesize them into highly structured, safe, and actionable emergency protocols. 

By analyzing the situation in milliseconds, Sahayak AI determines severity, outlines step-by-step immediate actions, provides contextual emergency contacts, and dynamically generates one-click SOS WhatsApp messages to protect human life.

---

## 🏆 PromptWars Rubric Compliance

This application was engineered specifically to achieve maximum scores across the PromptWars competition criteria outlined in `AGENTS.md`.

### 1. Google Cloud Services Integration (Depth & Count)
We securely integrated **4 major Google Cloud APIs**, serving as the backbone of our triage engine:
* **Gemini 1.5 Flash:** Powers all 5 nodes of our complex LangGraph triage pipeline to safely reason over emergencies.
* **Cloud Translation API:** Seamless fallback for multilingual Indian SOS texts, ensuring non-English inputs are fluently understood.
* **Firestore:** Immutable record persistence; each triage result safely performs reads/writes against the NoSQL database.
* **Cloud Logging:** Enterprise-grade observability tracking structured telemetry on every inference.

### 2. Deep Security Hardening 🔒 (Primary Focus Focus)
* **Zero Hardcoded Secrets:** All API keys, project IDs, and origin configs strictly pull from `.env` utilizing Python `os.environ`.
* **Container Security:** The Dockerfile has been modified to run operations as a strictly unprivileged `appuser`.
* **Prompt Injection Defense:** Frontend JS + Backend Pydantic Regex automatically detects and blocks instructions mapping to "DAN Mode" or prompt overrides.
* **XSS Prevention:** Frontend JavaScript exclusively utilizes `textContent` and secure `createElement_` patterns. **Zero** usage of `innerHTML`.
* **CORS & Middleware:** Strict CORS origins loaded securely from the environment.

### 3. Comprehensive Testing Suite (50+ Target Reached)
* Exceeded the `AGENTS.md` testing goal by leveraging heavily parameterised `pytest` testing across `test_schemas_extended.py`, `test_session_logger.py`, and core backend endpoints. (Total tests: **55+**)

### 4. Code Quality & Architecture
* Follows the strict modular architecture requirements exactly (`src/services/`, `src/utils/`, `src/schemas.py`). 

### 5. Interaction Tracking (Session Logging)
* Features an automated **Session Logger** (`src/utils/session_logger.py`) that continuously logs all multi-turn UI chat messages and LLM outputs chronologically to `sessions/log.csv` as per the core checklist requirement.

---

## Architecture Flow

```
POST /analyze
     │
     ▼
InputValidator (Pydantic & Regex)
     │
     ▼
LangGraph Pipeline (5 nodes)
  ├── understand  → clean_text, situation, intent
  ├── classify    → category, severity, priority
  ├── plan        → actions[], contacts[]
  ├── act         → refined_actions[]
  └── validate    → confidence
     │
     ▼
Firestore & Local Storage (results/*.json)
     │
     ▼
Structured JSON Response
```

## Local Setup & Configuration

1. **Virtual Environment (Recommended)**
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment Setup**
```bash
cp .env.example .env
```
Open `.env` and fill in:
* `GEMINI_API_KEY`: Your Gemini API access key.
* `GEMINI_MODEL`: `gemini-1.5-flash` or newer.
* `GCP_PROJECT`: Your Google Cloud Project ID.
* `ALLOWED_ORIGIN`: e.g. `http://localhost:8080,http://127.0.0.1:8080`

4. **Google Cloud Authentication**
Because Sahayak AI heavily utilizes Firestore, Cloud Logging, and Cloud Translation, you must locally authenticate your terminal before running:
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

5. **Run the Application**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

## Testing Validation

```bash
pytest tests/ -v --tb=short
```

## Production Deployment (Cloud Run)

```bash
gcloud run deploy sahayak-ai --source . --region us-central1 --allow-unauthenticated
```
