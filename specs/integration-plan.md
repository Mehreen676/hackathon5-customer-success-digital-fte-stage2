# Integration Plan — Customer Success Digital FTE

**Author:** Mehreen Asghar
**Stage:** 2 → 3 Integration Roadmap

---

## Current State (Stage 2)

Stage 2 is a fully functional backend service with:

- FastAPI REST API with 5 endpoints
- SQLite / PostgreSQL database persistence
- MCP tool registry with 5 tools
- Channel handlers for Gmail, WhatsApp, and Web Form
- Stateful conversation and ticket management
- Agent metrics tracking

**All channel delivery is simulated** — responses are returned as JSON.
No live API calls to Gmail, WhatsApp, or any external service.

---

## Stage 3 Integration Targets

### 1. Gmail API Integration

**Current:** Simulated via POST /support/gmail payload
**Stage 3 plan:**
- Google Cloud Pub/Sub push subscription for new email events
- OAuth2 service account authentication
- Gmail thread replies via `users.messages.send`
- Parse HTML email bodies with BeautifulSoup

**Trigger:** Gmail push notification → POST /support/gmail (same endpoint)

---

### 2. WhatsApp Business API (Twilio)

**Current:** Simulated via POST /support/whatsapp payload
**Stage 3 plan:**
- Twilio webhook for inbound WhatsApp messages
- `twilio.rest.Client` for outbound message delivery
- Media message support (images, documents)
- Twilio Messaging Service SID configuration

**Trigger:** Twilio webhook → POST /support/whatsapp (same endpoint)

---

### 3. Claude API — LLM Response Generation

**Current:** Rule-based keyword matching + KB template responses
**Stage 3 plan:**
- `anthropic.Anthropic` client for response generation
- System prompt: Nexora brand voice + agent persona
- Context: customer profile + conversation history + KB result
- Intent classification via Claude (replaces keyword matching)
- Fallback to rule-based if Claude API is unavailable

**Model:** claude-sonnet-4-6

---

### 4. Real MCP Protocol

**Current:** Function-based tool registry (MCP simulated)
**Stage 3 plan:**
- Claude Agent SDK with real MCP server
- Tools exposed over stdio or HTTP transport
- Claude calls tools autonomously during response generation
- Tool results feed back into Claude's context

---

### 5. Escalation Notifications

**Current:** Escalations logged to database only
**Stage 3 plan:**
- Slack webhook: post to #customer-escalations channel
- PagerDuty: critical severity tickets trigger on-call alert
- Email notification to assigned team distribution list

---

### 6. CRM Integration

**Current:** Customer data stored in local database only
**Stage 3 plan:**
- Salesforce / HubSpot contact sync
- Bidirectional ticket sync
- Opportunity flagging for pricing negotiation escalations

---

## Stage 2 → Stage 3 Migration Path

All Stage 2 endpoints remain unchanged.
Stage 3 adds real delivery behind the same API interface.

```
Stage 2 endpoint:    POST /support/gmail
                          ↓ normalizes payload
Stage 2:          agent workflow → returns JSON response (simulated)
                          ↓ (Stage 3 addition)
Stage 3:          + calls Gmail API to send the reply thread
                  + sends Slack notification if escalated
                  + updates Salesforce CRM record
```

The response schema stays the same. Stage 3 adds side effects only.

---

## Environment Variables Required for Stage 3

```bash
# Claude API
ANTHROPIC_API_KEY=sk-ant-...

# Gmail
GMAIL_SERVICE_ACCOUNT_JSON=/path/to/credentials.json
GMAIL_USER_EMAIL=support@nexora.io

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/...

# PagerDuty
PAGERDUTY_ROUTING_KEY=...

# Database (Production)
DATABASE_URL=postgresql://user:pass@host:5432/nexora_support
```

---

## Risk Assessment

| Risk                        | Likelihood | Impact | Mitigation                          |
|-----------------------------|------------|--------|-------------------------------------|
| Claude API rate limits      | Medium     | High   | Fallback to rule-based responses    |
| Gmail OAuth token expiry    | Medium     | Medium | Service account with domain-wide delegation |
| Twilio delivery failure     | Low        | Medium | Retry queue + fallback SMS          |
| Database migration          | Low        | High   | Alembic migrations with rollback    |
| WhatsApp policy violations  | Low        | High   | Follow Business API approved templates |
