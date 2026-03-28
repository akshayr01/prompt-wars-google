---
name: pw-google-services
description: Use this skill when the user wants to add Google Cloud services, increase the Google Services score, or integrate Vertex AI, Firestore, Cloud Logging, Cloud Translation, Cloud Storage, or Cloud Run into the project.
---

# pw-google-services

## Goal
Integrate all 8 Google Cloud services that the Hyderabad PromptWars winner used to achieve 98.13%. Each service added increases the Google Services score.

## The 8 Services (in implementation order)

### Service 1: Vertex AI — Gemini 1.5 Flash (Core, Do First)

```python
# src/services/gemini_service.py
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import os
import logging

logger = logging.getLogger(__name__)

vertexai.init(
    project=os.environ["GCP_PROJECT_ID"],
    location=os.environ.get("GCP_REGION", "us-central1")
)

model = GenerativeModel(
    "gemini-1.5-flash",
    generation_config=GenerationConfig(
        temperature=0.2,
        max_output_tokens=1024,
    )
)

async def generate_structured_response(prompt: str, system_prompt: str = "") -> str:
    """Call Gemini via Vertex AI and return text response."""
    try:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = model.generate_content(full_prompt)
        logger.info("Gemini call successful", extra={"prompt_length": len(prompt)})
        return response.text
    except Exception as e:
        logger.error(f"Gemini call failed: {e}")
        raise RuntimeError(f"AI generation failed: {e}")
```

requirements.txt entry: `google-cloud-aiplatform>=1.38.0`

---

### Service 2: Cloud Logging (Add Immediately — Easy Win)

```python
# src/utils/logging_config.py
import google.cloud.logging
import logging

def setup_cloud_logging():
    """Initialize Google Cloud Logging."""
    try:
        client = google.cloud.logging.Client()
        client.setup_logging(log_level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info("Cloud Logging initialized")
    except Exception:
        # Fallback to local logging in development
        logging.basicConfig(level=logging.INFO)

# In main.py — call at startup:
# from src.utils.logging_config import setup_cloud_logging
# setup_cloud_logging()
```

Log structured data everywhere:
```python
logger.info("Request processed", extra={
    "endpoint": "/process",
    "input_language": detected_lang,
    "processing_time_ms": elapsed,
    "user_agent": request.headers.get("user-agent", "unknown")
})
```

requirements.txt entry: `google-cloud-logging>=3.8.0`

---

### Service 3: Cloud Translation API

```python
# src/services/translate_service.py
from google.cloud import translate_v3 as translate
import os
import logging

logger = logging.getLogger(__name__)

_client = None

def get_translate_client():
    global _client
    if _client is None:
        _client = translate.TranslationServiceClient()
    return _client

SUPPORTED_LANGUAGES = ["en", "hi", "te", "ta", "kn", "mr", "bn", "gu"]

def detect_language(text: str) -> str:
    """Detect the language of input text. Returns ISO 639-1 code."""
    client = get_translate_client()
    parent = f"projects/{os.environ['GCP_PROJECT_ID']}/locations/global"
    try:
        response = client.detect_language(parent=parent, content=text)
        detected = response.languages[0].language_code
        logger.info(f"Language detected: {detected}")
        return detected
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        return "unknown"

def translate_to_english(text: str) -> dict:
    """Translate any text to English. Returns dict with original and translated."""
    client = get_translate_client()
    parent = f"projects/{os.environ['GCP_PROJECT_ID']}/locations/global"
    try:
        response = client.translate_text(
            parent=parent,
            contents=[text],
            target_language_code="en",
            mime_type="text/plain"
        )
        return {
            "original": text,
            "translated": response.translations[0].translated_text,
            "detected_language": response.translations[0].detected_language_code
        }
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return {"original": text, "translated": text, "detected_language": "en"}
```

requirements.txt entry: `google-cloud-translate>=3.13.0`

---

### Service 4: Firestore — Persistence

```python
# src/services/firestore_service.py
from google.cloud import firestore
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

_db = None

def get_db():
    global _db
    if _db is None:
        _db = firestore.Client()
    return _db

async def save_result(collection: str, data: dict) -> str:
    """Save a result document and return its ID."""
    try:
        db = get_db()
        doc_ref = db.collection(collection).document()
        doc_ref.set({
            **data,
            "created_at": firestore.SERVER_TIMESTAMP,
            "id": doc_ref.id
        })
        logger.info(f"Saved to Firestore: {collection}/{doc_ref.id}")
        return doc_ref.id
    except Exception as e:
        logger.error(f"Firestore save failed: {e}")
        raise

async def get_recent(collection: str, limit: int = 10) -> list:
    """Get recent documents from a collection."""
    try:
        db = get_db()
        docs = (
            db.collection(collection)
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
            .stream()
        )
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        logger.error(f"Firestore read failed: {e}")
        return []

async def get_by_id(collection: str, doc_id: str) -> dict | None:
    """Get a specific document by ID."""
    try:
        db = get_db()
        doc = db.collection(collection).document(doc_id).get()
        return {"id": doc.id, **doc.to_dict()} if doc.exists else None
    except Exception as e:
        logger.error(f"Firestore get failed: {e}")
        return None
```

requirements.txt entry: `google-cloud-firestore>=2.14.0`

---

### Service 5: Cloud Storage

```python
# src/services/storage_service.py
from google.cloud import storage
import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

_client = None

def get_storage_client():
    global _client
    if _client is None:
        _client = storage.Client()
    return _client

def upload_json(data: dict, prefix: str = "results") -> str:
    """Upload a JSON result to Cloud Storage. Returns public URL."""
    try:
        client = get_storage_client()
        bucket = client.bucket(os.environ["GCS_BUCKET_NAME"])
        filename = f"{prefix}/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{id(data)}.json"
        blob = bucket.blob(filename)
        blob.upload_from_string(
            json.dumps(data, ensure_ascii=False, indent=2),
            content_type="application/json"
        )
        logger.info(f"Uploaded to GCS: {filename}")
        return f"gs://{os.environ['GCS_BUCKET_NAME']}/{filename}"
    except Exception as e:
        logger.error(f"GCS upload failed: {e}")
        raise

def upload_text(content: str, filename: str, content_type: str = "text/plain") -> str:
    """Upload any text content to Cloud Storage."""
    try:
        client = get_storage_client()
        bucket = client.bucket(os.environ["GCS_BUCKET_NAME"])
        blob = bucket.blob(filename)
        blob.upload_from_string(content, content_type=content_type)
        return blob.public_url
    except Exception as e:
        logger.error(f"GCS text upload failed: {e}")
        raise
```

requirements.txt entry: `google-cloud-storage>=2.13.0`

---

### Service 6: Cloud Run (Deployment Target)

Dockerfile (always use this exact version):
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
```

Deploy command:
```bash
gcloud run deploy promptwars-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=$GCP_PROJECT_ID,GEMINI_API_KEY=$GEMINI_API_KEY,GCS_BUCKET_NAME=$GCS_BUCKET_NAME
```

---

### Services 7 & 8: Cloud Natural Language API + Secret Manager (bonus)

```python
# Secret Manager (replaces env vars — premium Google Services signal)
from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{os.environ['GCP_PROJECT_ID']}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Natural Language API (entity/sentiment analysis)
from google.cloud import language_v1

def analyze_sentiment(text: str) -> dict:
    client = language_v1.LanguageServiceClient()
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(request={"document": document}).document_sentiment
    return {"score": sentiment.score, "magnitude": sentiment.magnitude}
```

---

## .env.example (always ship this)
```
GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1
GCS_BUCKET_NAME=your-bucket-name
GEMINI_API_KEY=your-key-here
```

## requirements.txt (complete)
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
google-cloud-aiplatform>=1.38.0
google-cloud-logging>=3.8.0
google-cloud-translate>=3.13.0
google-cloud-firestore>=2.14.0
google-cloud-storage>=2.13.0
google-cloud-secret-manager>=2.18.0
slowapi>=0.1.9
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-asyncio>=0.23.0
httpx>=0.26.0
```

## Constraints
- Always use lazy initialization (`_client = None` pattern) — avoids startup failures if a service is unreachable
- Always log every service call (proves usage to judges)
- Never call multiple services sequentially if they can run concurrently — use `asyncio.gather()`
- Show "Powered by Google Cloud" badge in the UI footer
