"""Sahayak AI — Emergency triage powered by Gemini.

FastAPI application with routes and middleware. All logic in src/.
"""

import os
import uuid
import logging
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()  # Must be before any other imports that read env vars

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.gemini import call_gemini
from src.pipeline import run_pipeline
from src.storage import save_result, get_recent_results, get_result
from src.schemas import AnalyzeRequest, AnalyzeResponse, HealthResponse, ErrorResponse, ChatRequest, ChatResponse
from src.translate import translate_to_english, translate_from_english

# Logging setup — use Cloud Logging if available, else local
try:
    import google.cloud.logging as cloud_logging

    client = cloud_logging.Client()
    client.setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Cloud Logging initialized")
except Exception:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    logger.info("Using local logging (Cloud Logging not available)")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# FastAPI app
app = FastAPI(
    title="Sahayak AI",
    description="Emergency triage powered by Gemini",
    version="1.0.0",
)
app.state.limiter = limiter

# Middleware stack
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGIN", "*").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    max_age=3600,
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Add security headers to every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self'; "
        "img-src 'self' data:; "
        "frame-ancestors 'none';"
    )
    return response


# Exception handlers
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded", "detail": "Too many requests. Try again later.", "status_code": 429},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with structured JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Request error", "detail": str(exc.detail), "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions with 500 error."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc), "status_code": 500},
    )


# Routes
@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve the main frontend page."""
    return FileResponse("static/index.html")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint returning status and Google services list."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        google_services=["Gemini 1.5 Flash", "Cloud Logging"],
    )


@app.get("/history")
async def get_history():
    """Get recent triage results from local storage."""
    results = get_recent_results(limit=10)
    return {"results": results, "count": len(results)}


@app.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit("10/minute")
async def analyze_emergency(request: Request, data: AnalyzeRequest):
    """Analyze emergency text and return structured triage response.

    Runs the full 5-node LangGraph pipeline powered by Gemini,
    saves the result locally, and returns the structured response.
    """
    logger.info("Analyze request received", extra={"input_length": len(data.input)})

    # Generate unique result ID
    result_id = str(uuid.uuid4())[:8]

    # Translate input to English for the pipeline (auto-detect language)
    english_input, source_lang = translate_to_english(data.input)
    logger.info("Language processing", extra={"source_lang": source_lang, "translated": source_lang != "en"})

    # Run the triage pipeline with optional location
    state = run_pipeline(english_input, data.location or "Unknown")

    # Check for pipeline errors
    if state.get("error"):
        logger.error(f"Pipeline error: {state['error']}")
        raise HTTPException(status_code=500, detail=state["error"])

    # Translate situation and actions back to user's language if needed
    situation_text = state.get("situation", data.input)
    actions_list = state.get("refined_actions") or state.get("actions", [])
    if source_lang != "en":
        situation_text = translate_from_english(situation_text, source_lang)
        actions_list = [translate_from_english(a, source_lang) for a in actions_list]

    # Build response
    response_dict = {
        "situation": situation_text,
        "category": state.get("category", "other"),
        "severity": state.get("severity", "medium"),
        "priority": state.get("priority", "urgent"),
        "actions": actions_list,
        "contacts": state.get("contacts", []),
        "confidence": state.get("confidence", "medium"),
        "reasoning": state.get("reasoning", "Standard triage protocols applied."),
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "result_id": result_id,
        "detected_language": source_lang,
    }

    # Save to local storage (non-blocking, don't fail if this errors)
    try:
        save_result(response_dict, result_id)
        from src.utils.session_logger import log_interaction
        log_interaction(data.input, str(response_dict))
    except Exception as e:
        logger.error(f"Storage or log failed: {e}")

    logger.info(
        f"Analyzed: {response_dict['category']} {response_dict['severity']}",
        extra={"result_id": result_id, "category": response_dict["category"]},
    )

    return AnalyzeResponse(**response_dict)


@app.post("/analyze/{result_id}/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat_followup(request: Request, result_id: str, data: ChatRequest):
    """Ask a follow-up question regarding a specific triage result."""
    # Load previous context
    result = get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found or expired.")

    # Format prompt for Gemini
    prompt = (
        "You are a helpful emergency triage assistant answering a follow-up question.\n\n"
        f"Original Emergency: {result.get('situation', 'Unknown')}\n"
        f"Recommended Category: {result.get('category', 'Unknown')}\n"
        f"Recommended Actions: {', '.join(result.get('actions', []))}\n\n"
        f"User Follow-up Question: {data.question}\n\n"
        "Provide a clear, concise, actionable, and safe answer focusing ONLY on the user's question."
    )

    try:
        answer = call_gemini(prompt)
        from src.utils.session_logger import log_interaction
        log_interaction(data.question, answer)
        return ChatResponse(answer=answer)
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to general a follow-up answer.")


# Mount static files AFTER routes so API routes take priority
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info("Sahayak AI started", extra={"version": "1.0.0"})
