"""
Response Schemas — API response envelope models (Stage 2)
"""

from pydantic import BaseModel

from src.schemas.ticket_schema import TicketOut


class AgentResponse(BaseModel):
    """Full agent response envelope returned by all /support/* endpoints."""

    success: bool
    channel: str
    customer: str
    intent: str | None = None
    escalated: bool
    escalation_reason: str | None = None
    escalation_severity: str | None = None
    kb_used: bool
    kb_topic: str | None = None
    ticket: TicketOut
    response: str
    conversation_id: str


class HealthResponse(BaseModel):
    """Response body for GET /health."""

    status: str
    version: str
    stage: str
    db: str


class ErrorResponse(BaseModel):
    """Standard error envelope."""

    success: bool = False
    error: str
    detail: str | None = None
