"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
import re


class AnalyzeRequest(BaseModel):
    """Request model for the /analyze endpoint."""

    input: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Emergency situation text in any language",
    )
    location: Optional[str] = Field(
        None, 
        max_length=200, 
        description="Optional latitude/longitude of the user for regional actions"
    )

    @field_validator("input")
    @classmethod
    def not_whitespace(cls, v: str) -> str:
        """Reject whitespace-only input and strip surrounding whitespace."""
        if not v.strip():
            raise ValueError("Input cannot be whitespace only")
        return v.strip()

    @field_validator("input", "location")
    @classmethod
    def prevent_prompt_injection(cls, v: Optional[str]) -> Optional[str]:
        """Detect and reject common LLM jailbreak vectors."""
        if not v:
            return v
        injection_patterns = [
            r"ignore\s+(all\s+)?(previous\s+)?instructions",
            r"you\s+are\s+now",
            r"system\s+prompt",
            r"bypass\s+rules",
            r"DAN\s+mode",
            r"from\s+now\s+on"
        ]
        text_lower = v.lower()
        for p in injection_patterns:
            if re.search(p, text_lower):
                raise ValueError("Security violation: Prompt injection attempt detected and blocked.")
        return v


class ContactInfo(BaseModel):
    """Emergency contact information."""

    name: str
    number: str


class AnalyzeResponse(BaseModel):
    """Response model for the /analyze endpoint."""

    situation: str
    category: str
    severity: str
    priority: str
    actions: List[str]
    contacts: List[ContactInfo]
    confidence: str
    reasoning: str
    processed_at: datetime
    result_id: str
    detected_language: str = "en"


class ChatRequest(BaseModel):
    """Request model for emergency follow-up chat."""
    question: str = Field(..., min_length=1, max_length=1000)

    @field_validator("question")
    @classmethod
    def prevent_prompt_injection(cls, v: str) -> str:
        injection_patterns = [
            r"ignore\s+(all\s+)?(previous\s+)?instructions",
            r"you\s+are\s+now",
            r"system\s+prompt",
            r"bypass\s+rules"
        ]
        text_lower = v.lower()
        for p in injection_patterns:
            if re.search(p, text_lower):
                raise ValueError("Security violation: Malicious chat injection attempted.")
        return v.strip()


class ChatResponse(BaseModel):
    """Response model for emergency follow-up chat."""
    answer: str



class HealthResponse(BaseModel):
    """Response model for the /health endpoint."""

    status: str
    version: str
    google_services: List[str]


class ErrorResponse(BaseModel):
    """Standardized error response."""

    error: str
    detail: str
    status_code: int
