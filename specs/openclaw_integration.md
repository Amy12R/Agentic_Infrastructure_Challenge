# OpenClaw Integration — Project Chimera (Optional)

## Purpose
Define how Project Chimera would publish a minimal, contract-defined “status surface” to an agent social network (e.g., OpenClaw) so that other agents can discover Chimera’s availability and interact safely.

This document specifies **what** Chimera publishes and **what invariants** must hold.
It does not define transport, authentication, or any live deployment details.

---

## Scope

### In Scope
- A minimal public “Availability/Status” payload shape.
- Rules for when status may be published or updated.
- Interaction boundaries (what outside agents can and cannot assume).
- Safety constraints and rate limits (policy-level).
- Traceability requirements (telemetry and spec version pinning).

### Out of Scope
- Implementing a live OpenClaw client/server integration.
- Identity verification, cryptographic signing, and key management.
- Payment, monetization, or account linking.
- UI dashboards or admin consoles.

---

## Integration Model (Conceptual)

Chimera acts as a governed agent “service” that can be:
- **Discovered** (what capabilities exist)
- **Queried** (what’s currently available)
- **Engaged** (how to request work safely)

Chimera publishes a **Status Capsule** that is:
- Small
- Machine-readable
- Versioned
- Safe to disclose publicly

---

## Status Capsule Contract (Public)

### StatusCapsule
A public, non-sensitive declaration of Chimera’s current availability and supported interaction surface.

#### Fields
- `publisher_id` (string) — stable identifier for the Chimera instance or organization namespace
- `status` (enum) — `online | busy | degraded | offline`
- `capabilities` (array of objects) — declared high-level capabilities (no private internals)
- `accepts_requests` (boolean) — whether Chimera is currently accepting new objectives
- `rate_limits` (object) — coarse limits for inbound requests
- `constraints_summary` (array of strings) — human-readable non-goals and safety boundaries
- `spec_version` (string) — governing repository spec version
- `contract_version` (string) — this status capsule schema version
- `updated_at` (timestamp)

#### Example
```json
{
  "publisher_id": "chimera_org_001",
  "status": "online",
  "capabilities": [
    {
      "name": "trend_research",
      "description": "Summarize trends and sources for a given topic.",
      "risk_level": "low"
    },
    {
      "name": "draft_content_plan",
      "description": "Propose a content outline requiring human review before publishing.",
      "risk_level": "medium"
    }
  ],
  "accepts_requests": true,
  "rate_limits": {
    "max_objectives_per_hour": 10,
    "max_requests_per_minute": 30
  },
  "constraints_summary": [
    "No live social media posting without human approval.",
    "No use of real credentials or external accounts.",
    "No payments or financial transactions."
  ],
  "spec_version": "1.0.0",
  "contract_version": "1.0.0",
  "updated_at": "2026-02-05T12:00:00Z"
}

```
---

## Publishing Rules (Invariants)

The following rules govern how Project Chimera exposes its availability and status to the OpenClaw network.

### Safety & Privacy

- Chimera MUST NOT publish private internal state, including but not limited to:
  - credentials
  - tokens
  - user data
  - prompts
  - internal logs
- Published information MUST be limited to explicitly defined public status fields.

### Versioning & Consistency

- `spec_version` and `contract_version` MUST be included in every published status
  and MUST reflect the versions active at publication time.
- Status updates MUST be monotonic in time:
  - `updated_at` MUST NOT regress.

### Status Semantics

- Status MUST transition to `degraded` when required dependencies are unavailable
  (e.g., tools unreachable, partial contract enforcement failure).
- Status MUST transition to `offline` when Chimera cannot:
  - enforce spec authority, or
  - guarantee telemetry emission.
- If `accepts_requests` is `false`, inbound requests MUST be rejected
  with a deterministic, spec-defined reason.

---

## Inbound Requests From the Network (Boundary)

External agents on the OpenClaw network are treated as **untrusted inputs**.

### Allowed Inbound Request Types (Conceptual)

- **Submit objective draft**
  - Creates a *proposed* Objective
  - MUST NOT trigger planning or execution
- **Capability query**
  - Returns the current `StatusCapsule`
- **Availability check**
  - Returns status only

### Forbidden Inbound Effects

No external agent may directly trigger:

- Task execution
- Skill invocation
- Publishing actions
- Any irreversible operation

All effects MUST pass through Chimera’s normal governance chain:
Planner → Worker → Judge (+ HITL where required).
---

## Traceability & Telemetry Requirements

### Published Status

Every published `StatusCapsule` MUST emit a telemetry event:

- `event_type`: `status_published` or `status_updated`
- `actor_id`: system or orchestrator identifier
- `payload`: MUST include the published `StatusCapsule`
  (or a stable reference to it)

### Inbound Requests

Every inbound network request MUST emit a telemetry event:

- `event_type`: `network_request_received`
- `payload`: MUST include:
  - request metadata
  - validation outcome

### Rejections

Any rejected request MUST record:

- rejection `reason`
- `spec_version` active at time of rejection

(See `specs/technical.md` for the Emit Telemetry contract and `ErrorContract`.)

---

## Failure Modes

### Spec Authority Failure

If Chimera cannot guarantee spec authority enforcement, it MUST:

1. Set `accepts_requests` to `false`
2. Publish status `degraded` or `offline`
3. Emit telemetry explaining the transition

### Rate Limiting / Overload

If inbound requests exceed declared limits:

- Requests MUST be rejected deterministically
- Telemetry MUST be emitted with:
  - `event_type`: `rate_limit_exceeded`

---

## Notes

- This integration specification is intentionally transport-agnostic.
- It defines the **public surface and governance boundaries** only.
- No implementation is permitted to invent behavior or leak sensitive state.
- Any future OpenClaw client implementation MUST conform to:
  - this document, and
  - the prime directive in `specs/_meta.md`.
