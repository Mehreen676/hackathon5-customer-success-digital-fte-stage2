"""
Agent Workflow — Customer Success Digital FTE (Stage 2)

Implements the unified message processing pipeline. This is the core of
Stage 2 — a stateful, database-backed workflow that replaces the stateless
Stage 1 prototype.

Pipeline:
    1. channel detection (already normalized by channel handler)
    2. customer identification / creation
    3. conversation thread management
    4. escalation detection
    5. knowledge base search
    6. response generation (rule-based in Stage 2; LLM in Stage 3)
    7. ticket creation
    8. conversation history storage
    9. metrics recording

All MCP tools are invoked through the tool registry.
"""

import logging
import time

from sqlalchemy.orm import Session

from src.agents.escalation_engine import classify_intent, detect_escalation
from src.mcp.tool_registry import call_tool

logger = logging.getLogger(__name__)

VALID_CHANNELS = {"email", "whatsapp", "web_form"}


def process_message(
    customer_id: str,
    channel: str,
    content: str,
    db: Session,
    customer_name: str = "",
    customer_email: str | None = None,
) -> dict:
    """
    Main Stage 2 agent entry point. Processes one inbound customer message
    through the full service pipeline.

    Args:
        customer_id: External customer ID (e.g. "CUST-001") or identifier string.
        channel: Originating channel — email | whatsapp | web_form.
        content: Raw customer message text.
        db: SQLAlchemy database session.
        customer_name: Optional display name for new customers.
        customer_email: Optional email for new customers.

    Returns:
        dict with response text, ticket, escalation status, and metadata.
    """
    start_time = time.monotonic()

    # ------------------------------------------------------------------
    # Step 1: Validate channel
    # ------------------------------------------------------------------
    if channel not in VALID_CHANNELS:
        return {
            "success": False,
            "error": f"Unknown channel '{channel}'. Supported: {sorted(VALID_CHANNELS)}",
        }

    # ------------------------------------------------------------------
    # Step 2: Identify or create customer
    # ------------------------------------------------------------------
    from src.db import crud

    customer = crud.get_or_create_customer(
        db=db,
        external_id=customer_id,
        name=customer_name or "Valued Customer",
        email=customer_email,
    )

    # ------------------------------------------------------------------
    # Step 3: Get or create conversation thread
    # ------------------------------------------------------------------
    conversation = crud.get_or_create_conversation(db, customer.id, channel)

    # ------------------------------------------------------------------
    # Step 4: Retrieve customer context via MCP tool
    # ------------------------------------------------------------------
    customer_ctx = call_tool("get_customer_context", customer_id=customer.id, db=db)
    display_name = customer_ctx.get("name", "Valued Customer")

    # ------------------------------------------------------------------
    # Step 5: Classify intent
    # ------------------------------------------------------------------
    intent = classify_intent(content)

    # ------------------------------------------------------------------
    # Step 6: Escalation detection
    # ------------------------------------------------------------------
    escalation = detect_escalation(content, customer_ctx)

    if escalation:
        # ----- ESCALATION PATH -----

        # Create escalated ticket
        ticket_data = call_tool(
            "create_ticket",
            customer_id=customer.id,
            channel=channel,
            subject=f"[{intent.upper()}] {content[:80]}",
            description=content,
            priority=escalation["severity"],
            status="escalated",
            conversation_id=conversation.id,
            escalated=True,
            escalation_reason=escalation["reason"],
            escalation_severity=escalation["severity"],
            db=db,
        )

        # Generate holding response via escalate_issue tool
        escalation_result = call_tool(
            "escalate_issue",
            ticket_id=ticket_data["ticket_id"],
            ticket_ref=ticket_data["ticket_ref"],
            reason=escalation["reason"],
            severity=escalation["severity"],
            channel=channel,
            customer_name=display_name,
            db=db,
        )

        response_text = escalation_result["holding_response"]

        # Update conversation status
        crud.escalate_conversation(db, conversation.id)

        # Store conversation turn
        crud.create_message(db, conversation.id, "customer", content, channel)
        crud.create_message(db, conversation.id, "agent", response_text, channel)

        # Record metrics
        elapsed_ms = (time.monotonic() - start_time) * 1000
        crud.create_metric(
            db=db,
            channel=channel,
            ticket_id=ticket_data["ticket_id"],
            conversation_id=conversation.id,
            intent=intent,
            escalated=True,
            escalation_reason=escalation["reason"],
            kb_used=False,
            processing_time_ms=elapsed_ms,
        )

        logger.info(
            "ESCALATED | customer=%s | reason=%s | severity=%s | ticket=%s",
            customer_id, escalation["reason"], escalation["severity"], ticket_data["ticket_ref"]
        )

        return {
            "success": True,
            "escalated": True,
            "escalation_reason": escalation["reason"],
            "escalation_severity": escalation["severity"],
            "ticket": ticket_data,
            "response": response_text,
            "channel": channel,
            "customer": display_name,
            "intent": intent,
            "kb_used": False,
            "kb_topic": None,
            "conversation_id": conversation.id,
        }

    # ------------------------------------------------------------------
    # Step 7: Knowledge base search (non-escalated path)
    # ------------------------------------------------------------------
    kb_result = call_tool("search_kb", query=content, db=db)

    if kb_result["matched"]:
        top_match = kb_result["results"][0]
        response_body = top_match["content"]
        kb_topic = top_match["topic"]
        ticket_status = "auto-resolved"
    else:
        response_body = (
            "I don't have specific information about that in my current knowledge base. "
            "I've logged your query and a specialist will provide a detailed answer shortly."
        )
        kb_topic = None
        ticket_status = "pending_review"

    # ------------------------------------------------------------------
    # Step 8: Create ticket
    # ------------------------------------------------------------------
    ticket_data = call_tool(
        "create_ticket",
        customer_id=customer.id,
        channel=channel,
        subject=f"[{intent.upper()}] {content[:80]}",
        description=content,
        priority="low",
        status=ticket_status,
        conversation_id=conversation.id,
        db=db,
    )

    # ------------------------------------------------------------------
    # Step 9: Format channel-appropriate response
    # ------------------------------------------------------------------
    formatted = call_tool(
        "send_channel_response",
        message_body=response_body,
        channel=channel,
        customer_name=display_name,
        ticket_ref=ticket_data["ticket_ref"],
    )

    response_text = formatted["response"]

    # ------------------------------------------------------------------
    # Step 10: Store conversation history
    # ------------------------------------------------------------------
    crud.create_message(db, conversation.id, "customer", content, channel)
    crud.create_message(db, conversation.id, "agent", response_text, channel)

    # ------------------------------------------------------------------
    # Step 11: Record metrics
    # ------------------------------------------------------------------
    elapsed_ms = (time.monotonic() - start_time) * 1000
    crud.create_metric(
        db=db,
        channel=channel,
        ticket_id=ticket_data["ticket_id"],
        conversation_id=conversation.id,
        intent=intent,
        escalated=False,
        kb_used=kb_result["matched"],
        kb_topic=kb_topic,
        processing_time_ms=elapsed_ms,
    )

    logger.info(
        "AUTO-RESPONDED | customer=%s | intent=%s | kb=%s | ticket=%s | %.1fms",
        customer_id, intent, kb_topic or "no_match", ticket_data["ticket_ref"], elapsed_ms
    )

    return {
        "success": True,
        "escalated": False,
        "escalation_reason": None,
        "escalation_severity": None,
        "ticket": ticket_data,
        "response": response_text,
        "channel": channel,
        "customer": display_name,
        "intent": intent,
        "kb_used": kb_result["matched"],
        "kb_topic": kb_topic,
        "conversation_id": conversation.id,
    }
