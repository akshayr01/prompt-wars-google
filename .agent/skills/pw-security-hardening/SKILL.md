---
name: pw-security-hardening
description: Use this skill when the user wants to fix security issues, improve the Security score, run a pre-submission security check, or add input validation, CORS, CSP, rate limiting, or secret management.
---

# pw-security-hardening

## Goal
Fix every security issue that caused low scores in PromptWars. Run this before every submission attempt.

## Instructions

### Step 1: Secret Scan (Run First)
```bash
# Run in terminal
grep -rn "AIza\|sk-\|password\s*=\|api_key\s*=\|secret\s*=" src/ main.py --include="*.py"
# Any output = CRITICAL issue — move to env vars immediately
```

### Step 2: Validation Module
Create `src/utils/validation.py`:
```python
import re
import html
from fastapi import HTTPException

def validate_input(text, max_length: int = 5000) -> str:
    """Validate and sanitize user input."""
    if not text or not isinstance(text, str):
        raise HTTPException(status_code=400, detail="Text is required and must be a string")
    text = text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty or whitespace only")
    if len(text) > max_length:
        raise HTTPException(status_code=400, detail=f"Text must be under {max_length} characters")
    return text

def sanitize_html_input(text: str) -> str:
    """Remove HTML tags and escape special characters."""
    clean = re.sub(r'<[^>]+>', '', text)
    return html.escape(clean)

def validate_language_code(lang: str) -> str:
    """Validate ISO 639-1 language code."""
    VALID_LANGS = {"en", "hi", "te", "ta", "kn", "mr", "bn", "gu", "pa", "or"}
    if lang not in VALID_LANGS:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {lang}")
    return lang
```

### Step 3: Middleware Stack in main.py
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI(title="PromptWars App", version="1.0.0")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://www.gstatic.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com; "
        "img-src 'self' data: https:;"
    )
    return response

# Health endpoint (no rate limit)
@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
```

### Step 4: Rate Limiting on Endpoints
```python
@app.post("/process")
@limiter.limit("10/minute")
async def process(request: Request, data: InputModel):
    text = validate_input(data.text)
    # ... rest of handler
```

### Step 5: .gitignore Check
Ensure `.gitignore` contains:
```
.env
*.env
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
.DS_Store
```

### Step 6: Pydantic Models (type safety = security)
```python
# src/models/schemas.py
from pydantic import BaseModel, Field, validator
from typing import Optional

class ProcessRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Input text")
    language: Optional[str] = Field(None, pattern="^[a-z]{2}$")
    
    @validator("text")
    def text_not_whitespace(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be whitespace only")
        return v.strip()

class ProcessResponse(BaseModel):
    severity: str
    action: str
    evacuate: bool
    contacts: list[str]
    detected_language: Optional[str]
    translated_text: Optional[str]
    result_id: Optional[str]
```

## Output Format
```
🔍 Security Scan Results:
  🔴 CRITICAL: [N] hardcoded secrets found → FIXED
  ✅ CORS middleware: present
  ✅ CSP headers: present
  ✅ Input validation: present
  ✅ Rate limiting: present
  ✅ .env in .gitignore: confirmed
  ✅ Pydantic models: all endpoints covered

Security score: READY FOR SUBMISSION
```
