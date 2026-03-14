# Hackathon 5 — Customer Success Digital FTE
### Stage 2: Backend Service Architecture

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Hackathon](https://img.shields.io/badge/hackathon-stage%202-purple)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-teal)
![AI Agent](https://img.shields.io/badge/AI-Customer%20Success%20Agent-orange)
![Database](https://img.shields.io/badge/database-SQLAlchemy%20%2F%20PostgreSQL-blueviolet)
![License](https://img.shields.io/badge/license-MIT-green)

**Project Owner:** Mehreen Asghar
**Stage:** 2 — Backend Service Architecture with Persistence
**Hackathon:** Hackathon 5

> **Stage 2 introduces a real backend service, database persistence, and a structured MCP tool architecture.
> The Stage 1 prototype is preserved unchanged as a fallback and demo mode.**

---

## 🎥 Stage 2 Demo Video

This demo shows the Stage 2 backend system running end-to-end — FastAPI receiving multi-channel messages, the agent workflow processing them, MCP tools executing, tickets being created in the database, and channel-specific responses being returned.

[![Watch the Stage 2 Demo](assets/stage2-thumbnail.png)](PASTE_STAGE2_VIDEO_LINK_HERE)

This demo shows:
- FastAPI backend running
- Multi-channel handling (Gmail, WhatsApp, Web Form)
- MCP tool execution
- Knowledge base lookup
- Escalation detection
- Ticket creation
- Conversation persistence

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Channels["📥 Inbound Channels"]
        G[Gmail]
        W[WhatsApp Business]
        F[Web Form]
    end

    subgraph API["⚡ FastAPI — src/api/"]
        E1[POST /support/gmail]
        E2[POST /support/whatsapp]
        E3[POST /support/webform]
        E4[POST /support/message]
        HLT[GET /health]
    end

    subgraph Handlers["🔀 Channel Handlers — src/channels/"]
        CH[GmailHandler · WhatsAppHandler · WebFormHandler]
    end

    subgraph Workflow["🤖 Agent Workflow — src/agents/"]
        WF[workflow.py — 9-step pipeline]
        ESC[EscalationEngine]
        AGT[CustomerSuccessAgent]
    end

    subgraph MCP["🛠 MCP Tool Registry — src/mcp/"]
        REG[tool_registry.py]
        T1[search_kb]
        T2[create_ticket]
        T3[get_customer_context]
        T4[escalate_issue]
        T5[send_channel_response]
    end

    subgraph Services["⚙️ Services — src/services/"]
        KS[KnowledgeService]
        TS[TicketService]
        CS[ConversationService]
    end

    subgraph DB["🗄️ Database — src/db/"]
        MOD[SQLAlchemy Models]
        CRUD[CRUD Operations]
        PG[(SQLite / PostgreSQL)]
    end

    G --> E1
    W --> E2
    F --> E3
    E1 & E2 & E3 & E4 --> CH
    CH --> WF
    WF --> ESC
    WF --> REG
    REG --> T1 & T2 & T3 & T4 & T5
    T1 & T2 & T3 --> KS & TS & CS
    KS & TS & CS --> CRUD
    CRUD --> PG
    WF --> AGT
    AGT -->|AgentResponse JSON| Channels
```

Stage 2 introduces full persistence — every conversation, message, and ticket is stored in the database and survives service restarts.

MCP tools are decoupled from the agent via a central registry — adding or replacing a tool requires no changes to the workflow.

Channel-specific responses are formatted and returned by the backend: formal email replies, concise WhatsApp messages, and structured web form responses.

---

## 📋 Project Overview

**Customer success teams** at SaaS companies spend the majority of their time answering repetitive, routine inquiries — billing questions, password resets, refund requests. These consume agent time that should be reserved for complex, high-value customer relationships.

This project builds a **Customer Success Digital FTE** — an AI agent backend that:

- Receives customer messages from Email, WhatsApp, and Web Form channels
- Identifies customers and retrieves their history from a database
- Detects escalation triggers before attempting to auto-respond
- Searches a persistent knowledge base for relevant answers
- Creates and tracks support tickets through their full lifecycle
- Persists every conversation turn for audit and continuity
- Returns channel-appropriate formatted responses

---

## 🧭 Business Goal

Replace repetitive tier-1 support work with an autonomous AI agent that:

- Handles password resets, billing queries, integration how-tos, and plan questions automatically
- Escalates legal threats, refund requests, angry customers, and security issues to the right human team — immediately
- Gives VIP/Enterprise accounts priority escalation with an account manager
- Records every interaction for quality assurance and analytics

The result: customer success agents spend their time on complex, relationship-critical work rather than answering the same questions 50 times a day.

---

## 🚀 What Stage 2 Adds Beyond Stage 1

| Concern | Stage 1 (Prototype) | Stage 2 (Service) |
|---|---|---|
| Runtime | `python script` | `uvicorn src.api.main:app` |
| Storage | In-memory dicts | SQLite / PostgreSQL — 7 tables |
| API | None | FastAPI with 5 endpoints + OpenAPI docs |
| Channels | Python function args | Normalized handlers with payload validation |
| MCP Tools | Plain functions | `@register` decorator + `call_tool()` dispatcher |
| Conversations | Stateless | Persisted with full message history |
| Tickets | `TICKET_STORE` dict | `tickets` table with full lifecycle |
| Metrics | None | `agent_metrics` table per interaction |
| Tests | 36 unit tests | +123 new tests (API, DB, tools, workflow) |
| Configuration | Hardcoded | Environment variables + `.env` support |

---

## ⚡ API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health + DB connectivity check |
| `POST` | `/support/message` | Generic unified message endpoint (any channel) |
| `POST` | `/support/gmail` | Gmail channel — accepts simulated webhook payload |
| `POST` | `/support/whatsapp` | WhatsApp Business — accepts simulated Twilio payload |
| `POST` | `/support/webform` | Web form — accepts support form submission |
| `GET` | `/docs` | Swagger UI (OpenAPI) |
| `GET` | `/redoc` | ReDoc API documentation |

### Example Request — Gmail

```json
POST /support/gmail
{
  "from_email": "sarah.mitchell@brightflow.com",
  "from_name": "Sarah Mitchell",
  "subject": "Password reset help",
  "body": "Hi, I've forgotten my password and I'm locked out of my account.",
  "customer_id": "CUST-001"
}
```

### Example Response

```json
{
  "success": true,
  "channel": "email",
  "customer": "Sarah Mitchell",
  "intent": "account",
  "escalated": false,
  "kb_used": true,
  "kb_topic": "password_reset",
  "ticket": {
    "ticket_ref": "TKT-AB12CD34",
    "status": "auto-resolved",
    "priority": "low",
    "escalated": false,
    "channel": "email",
    "created_at": "2026-03-14T10:30:00Z"
  },
  "response": "Dear Sarah,\n\nThank you for contacting Nexora Customer Success...",
  "conversation_id": "uuid-v4-..."
}
```

---

## 🗄️ Database Schema

Seven PostgreSQL-ready tables (SQLite in development):

| Table | Purpose |
|---|---|
| `customers` | Customer accounts with tier and VIP flag |
| `customer_identifiers` | Channel identifiers (email address, phone number) |
| `conversations` | Support conversation threads per customer per channel |
| `messages` | Individual messages — customer and agent turns |
| `tickets` | Support tickets with priority, status, escalation tracking |
| `knowledge_base` | 10 searchable KB articles, seeded on startup |
| `agent_metrics` | Per-interaction performance data (latency, KB used, escalated) |

Switch to PostgreSQL with one environment variable:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/nexora_support
```

See [specs/database-schema.md](specs/database-schema.md) for full column definitions.

---

## 🤖 Agent Workflow

The 9-step processing pipeline that runs for every inbound message:

```
message received
  → 1. channel validation
  → 2. customer identification (DB lookup or auto-create)
  → 3. conversation thread (get active or create new)
  → 4. customer context (MCP: get_customer_context)
  → 5. intent classification (billing / account / integration / plan / team / general)
  → 6. escalation detection
       ├── YES → create_ticket (escalated) + escalate_issue → holding response
       └── NO  → search_kb → create_ticket → send_channel_response
  → 7. store conversation history (customer message + agent response)
  → 8. record agent metrics
  → 9. return AgentResponse JSON
```

See [specs/agent-workflow.md](specs/agent-workflow.md) for the full pipeline diagram.

---

## 🛠 MCP Tool Layer

All agent actions are dispatched through the tool registry:

| Tool | Purpose |
|---|---|
| `search_kb` | Scored keyword search — DB KB with Stage 1 fallback |
| `create_ticket` | Create and persist a support ticket with full metadata |
| `get_customer_context` | Retrieve customer profile, tier, VIP flag, and ticket history |
| `escalate_issue` | Update ticket status, route to team, generate holding response |
| `send_channel_response` | Format response for the target channel style |

Tools are registered with `@register("tool_name")` and invoked via `call_tool("tool_name", ...)`. Adding a new tool requires no changes to the workflow.

---

## 📡 Multi-Channel Support

| Channel | Handler | Response Style |
|---|---|---|
| **Email (Gmail)** | `GmailHandler` | Formal, detailed (up to 400 words), `Dear {name}` salutation |
| **WhatsApp** | `WhatsAppHandler` | Short, conversational (80 words max), `Hi {name}! 👍` |
| **Web Form** | `WebFormHandler` | Structured, balanced (200 words), reference included |

Each handler normalizes its channel-specific payload to a unified `NormalizedMessage` before passing to the workflow.

---

## 📊 Escalation Logic

| Trigger | Severity | Assigned Team | SLA |
|---|---|---|---|
| Security issue / data breach | **critical** | Security | 2 hours |
| Legal complaint / attorney | **high** | Legal & Customer Success | 2 hours |
| VIP/Enterprise complaint | **high** | Account Management | 2 hours |
| Angry customer | **medium** | Senior Customer Success | 1 business day |
| Refund request | **medium** | Billing | 1 business day |
| Pricing negotiation | **medium** | Sales & Account Management | 1 business day |

---

## ✅ Testing Summary

| Test File | Coverage | Tests |
|---|---|---|
| `tests/test_agent.py` | Stage 1 prototype (preserved) | 36 |
| `tests/test_api.py` | FastAPI endpoints — all channels | 26 |
| `tests/test_db.py` | Database CRUD — all 7 tables | 30 |
| `tests/test_tools.py` | MCP tool registry + all 5 tools | 33 |
| `tests/test_workflow.py` | Agent pipeline + escalation engine | 34 |
| **Total** | | **159** |

Run all tests:

```bash
pip install -r requirements.txt
pytest tests/ -v
```

---

## 📁 Repository Structure

```
hackathon5-customer-success-digital-fte-stage2/
├── README.md
├── requirements.txt
├── assets/
│   └── stage2-thumbnail.png          ← Demo video thumbnail
├── context/                           ← Stage 1 business context (preserved)
│   ├── brand-voice.md
│   ├── company-profile.md
│   ├── escalation-rules.md
│   ├── product-docs.md
│   └── sample-tickets.json
├── specs/
│   ├── customer-success-fte-spec.md  ← Stage 1 spec
│   ├── agent-skills.md
│   ├── prompt-history.md
│   ├── discovery-log.md
│   ├── stage2-architecture.md        ← Stage 2 architecture
│   ├── database-schema.md            ← DB table definitions
│   ├── agent-workflow.md             ← Pipeline diagram
│   └── integration-plan.md          ← Stage 3 roadmap
├── src/
│   ├── agent/                         ← Stage 1 prototype (unchanged)
│   │   ├── customer_success_agent.py
│   │   └── mcp_server.py
│   ├── api/                           ← FastAPI backend
│   │   ├── main.py
│   │   ├── health.py
│   │   └── support_api.py
│   ├── agents/                        ← Stage 2 agent workflow
│   │   ├── customer_success_agent.py
│   │   ├── workflow.py
│   │   └── escalation_engine.py
│   ├── channels/                      ← Channel handlers
│   │   ├── gmail_handler.py
│   │   ├── whatsapp_handler.py
│   │   └── webform_handler.py
│   ├── db/                            ← Database layer
│   │   ├── database.py
│   │   ├── models.py
│   │   └── crud.py
│   ├── mcp/                           ← MCP tool framework
│   │   ├── tool_registry.py
│   │   └── tools/
│   │       ├── kb_search.py
│   │       ├── create_ticket.py
│   │       ├── get_customer_context.py
│   │       ├── escalate_issue.py
│   │       └── send_channel_response.py
│   ├── services/
│   │   ├── knowledge_service.py
│   │   ├── ticket_service.py
│   │   └── conversation_service.py
│   └── schemas/
│       ├── message_schema.py
│       ├── ticket_schema.py
│       └── response_schema.py
└── tests/
    ├── test_agent.py                  ← Stage 1 (36 tests)
    ├── test_api.py                    ← Stage 2 API (26 tests)
    ├── test_db.py                     ← Stage 2 DB (30 tests)
    ├── test_tools.py                  ← Stage 2 MCP tools (33 tests)
    └── test_workflow.py               ← Stage 2 workflow (34 tests)
```

---

## 🚀 How to Run Stage 2

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn src.api.main:app --reload

# Open Swagger UI
# → http://localhost:8000/docs

# Run all tests
pytest tests/ -v
```

On startup the service automatically:
1. Creates all database tables
2. Registers all MCP tools
3. Seeds the knowledge base (10 articles)
4. Seeds sample customers (CUST-001 through CUST-005)

---

## 🚫 What Is Not Yet Implemented

| Feature | Reason |
|---|---|
| Real Gmail API delivery | Stage 3 — requires OAuth2 + Google Cloud Pub/Sub |
| Real Twilio WhatsApp send | Stage 3 — requires Twilio credentials |
| Claude API / LLM responses | Stage 3 — LLM integration planned |
| Real MCP protocol (stdio) | Stage 3 — using Claude Agent SDK |
| Escalation notifications (Slack) | Stage 3 — notification webhooks |
| Kafka async processing | Out of scope for Stage 2 |
| Kubernetes deployment | Stage 3 — production infrastructure |
| Authentication / API keys | Out of scope for hackathon |

See [specs/integration-plan.md](specs/integration-plan.md) for the full Stage 3 roadmap.

---

*Hackathon 5 · Customer Success Digital FTE · Stage 2 · Mehreen Asghar*
