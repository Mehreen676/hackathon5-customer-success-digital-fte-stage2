# Prompt History & Build Decisions — Customer Success Digital FTE

**Stage:** 1 Prototype
**Author:** Mehreen Asghar
**For:** Hackathon 5 judges

This document logs the key decisions made while building the Stage 1 prototype — including what was chosen, why, and what was deliberately left out.

---

## Iteration 1: Define the Problem

**Starting point:**
Customer success teams at SaaS companies handle large volumes of repetitive, routine support tickets. The cost and delay of routing everything through human agents is high. Most tier-1 inquiries (password resets, billing questions, how-to questions) have standard answers.

**Decision:** Build a Digital FTE — an AI agent that handles tier-1 inquiries autonomously while detecting when human escalation is required.

**Why "Digital FTE" framing?**
It sets the right expectation: this is not just a chatbot. It is a full support agent that triages, looks up information, creates tickets, and routes work — exactly like a new hire would, but faster and without fatigue.

---

## Iteration 2: Define Stage 1 Scope

**Problem:** It's tempting to build the full system immediately (real Gmail, Twilio, database, LLM, Kubernetes). But that is months of work and a Stage 1 hackathon prototype needs to prove the *concept* quickly.

**Decision:** Stage 1 = simulated pipeline only. No real API integrations. Rule-based triage. In-memory data.

**What this validates:**
- Is the agent flow correct?
- Does triage logic catch the right cases?
- Does channel formatting work?
- Are the MCP tool interfaces well-designed?

**What it does NOT validate:** performance at scale, real LLM quality, production security.

**Why this was the right call:** Prototype-first avoids over-engineering before the design is stable. The agent flow can be validated in Stage 1 without spending a week on OAuth2 setup.

---

## Iteration 3: Architecture Decision — One Agent, Multiple Channels

**Option A:** Build a separate agent per channel (EmailAgent, WhatsAppAgent, WebFormAgent).
**Option B:** Build one core agent that adapts output by channel.

**Decision:** Option B — single agent core.

**Reasoning:** Triage logic, KB search, and ticket creation are identical across channels. Only the response formatting differs. Separate agents would duplicate 80% of the logic. A single agent with a channel formatting layer is cleaner and more maintainable.

---

## Iteration 4: Triage Order Decision

**Early mistake:** In the first draft, the KB search ran before escalation check. This meant that for a legal complaint, the agent would pull refund policy content, then realize it needed to escalate — wasted steps, and risk of using KB content in a sensitive context.

**Decision:** Escalation check always runs FIRST. KB search only runs if no escalation is triggered.

**Rule established:** `identify → triage → (if escalate: escalate path) → (else: KB → respond)`

---

## Iteration 5: MCP Tool Design

**Decision:** Structure all agent capabilities as MCP tools from the start, even in Stage 1.

**Why:** In Stage 2, Claude API will be integrated. Claude can call MCP tools. If the tool interfaces are already well-defined in Stage 1, wiring them to real Claude calls in Stage 2 is straightforward — no redesign needed.

**Tools defined:**
1. `search_kb` — KB lookup
2. `create_ticket` — ticket creation
3. `get_history` — customer context
4. `send_response` — channel formatting + delivery
5. `escalate_to_human` — escalation + holding response

**Interface contract:** Every tool takes a dict of inputs and returns a dict of outputs. Clean, testable, and ready for MCP protocol wrapping in Stage 2.

---

## Iteration 6: KB Format Decision

**Option A:** Structured JSON knowledge base with categories and metadata.
**Option B:** Flat markdown files organized by topic.

**Decision:** Markdown files for Stage 1.

**Reasoning:** Markdown is human-readable, easy to update, and the content can be scanned with simple keyword search. Stage 2 will embed the markdown content into a vector store (e.g., Chroma or Pinecone) for semantic search. The transition from markdown → vector embeddings is straightforward.

---

## Iteration 7: Escalation Language

**Early draft escalation responses:** "Your ticket has been escalated."
**Problem:** Cold, clinical, does not acknowledge the customer's frustration.

**Revised approach:** Escalation responses use empathy-first language.
> "I'm really sorry to hear about your experience. I've flagged this as a priority and a team member will be in touch shortly."

**Decision:** Escalation holding responses must always acknowledge the customer's feelings before mentioning the handoff.

---

## Iteration 8: Test Strategy

**Decision:** One focused test file (`tests/test_agent.py`) covering the four critical behaviors:
- Escalation detection (positive and negative cases)
- KB lookup (match and no-match cases)
- Channel formatting (email vs WhatsApp vs web form)
- Ticket creation (fields, status, ID format)

**Why not more tests?** This is a Stage 1 prototype. Test coverage should prove the core logic works, not achieve 100% coverage on simulated code. Over-testing a prototype is wasted effort.

---

## Limitations Accepted in Stage 1

| Limitation | Accepted Because |
|---|---|
| No real LLM calls | Prototype validates flow without API dependency |
| Keyword-only triage | Deterministic and testable — sufficient for demo |
| In-memory data | No DB needed for proof of concept |
| No multi-turn memory | Each ticket is independent in Stage 1 |
| No auth | Not a prototype concern |
| English only | Sufficient for hackathon scope |

---

## Stage 2 Notes (For Future Work Only — Not Implemented)

These are notes for the next stage — nothing below is built.

- Replace rule-based triage with Claude API call for intent classification
- Replace keyword KB search with vector embeddings (Chroma or Pinecone)
- Connect Gmail API for real email ingestion (OAuth2 + Gmail webhooks)
- Connect Twilio for WhatsApp Business API
- Add PostgreSQL to persist tickets and conversation history
- Add Kafka for async message processing at volume
- Add JWT-based API authentication
- Build CRM integration (Salesforce or HubSpot)

---

*End of prompt history — Stage 1 complete.*
