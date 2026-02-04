
# Architecture Strategy — Project Chimera (Task 1.2) 
- The diagram is below

## Purpose
This document records the **key architectural decisions** for Project Chimera before any implementation begins.
It is intentionally decision-focused and aligned with the SRS. This file acts as a bridge between the SRS and the upcoming specifications and tests.

---

## 1. Agent Pattern Decision

### Chosen Pattern
**Hierarchical Swarm (Planner → Worker → Judge), supervised by a single Orchestrator**.

### Why This Pattern Fits Chimera
- Chimera operates at **high volume** (many parallel content and engagement tasks).
- It carries **high brand and safety risk**, requiring strong governance.
- The system must scale to **thousands of agents supervised by one human**.
- Parallel workers allow speed, while the Judge enforces consistency and safety.
- Optimistic Concurrency Control prevents actions based on stale state.

### Patterns Explicitly Rejected
- **Sequential Chain**: Too slow and fragile for real-time engagement.
- **Flat Swarm (no Planner/Judge)**: Lacks strategy and safety enforcement.
- **Single Monolithic Agent**: Difficult to scale, debug, and govern.

---

## 2. Human-in-the-Loop (HITL) / Safety Layer

### Placement of Human Approval
Human review occurs **at the Judge checkpoint**, never at the Worker level.

### Approval Routing Logic
- **High confidence (>0.90)** → Auto-approved by Judge.
- **Medium confidence (0.70–0.90)** → Routed to HITL dashboard for async human approval.
- **Low confidence (<0.70)** → Automatically rejected and retried by Planner.

### Mandatory Human Review
Regardless of confidence score, content touching:
- Politics
- Health advice
- Financial advice
- Legal claims

is always escalated to a human reviewer.

### Why This Design Works
- Humans focus only on exceptions.
- The swarm continues working while reviews are pending.
- Safety and brand governance remain centralized and auditable.

---

## 3. Database Strategy for High-Velocity Video Metadata

### What “High-Velocity Metadata” Means
This refers to fast-arriving operational data such as:
- Video generation runs and retries
- Asset versions and URLs
- Publishing status and platform IDs
- Engagement snapshots
- Approval and moderation records

### Chosen Approach
**PostgreSQL is the system of record for video metadata**, supported by:
- **Redis** for queues and short-lived state
- **Weaviate** for semantic memory (not raw metadata)

### Why SQL Is Preferred
- Strong relational integrity across agents, campaigns, assets, and approvals
- Clear audit trails (“what was approved and when”)
- Natural fit for dashboards and reporting
- Compatible with spec-driven development and testing

### Why Not NoSQL (for now)
- The project does not require massive unstructured analytics ingestion yet.
- Relational consistency is more valuable than schema flexibility at this stage.
- NoSQL can be added later as a downstream analytics pipeline if needed.

---

## Architectural Overview Diagram

```mermaid
flowchart TD
  %% ===== Core control plane =====
  H[Human Operator / Super-Orchestrator]
  O[Central Orchestrator<br>Dashboard + Global State View]

  H -->|sets goals / reviews exceptions| O

  %% ===== Swarm roles =====
  P[Planner<br>decomposes goals into tasks]
  W[Worker Pool<br>stateless executors]
  J[Judge<br>quality + safety gate]

  O --> P
  P -->|push tasks| TQ[(Task Queue<br>Redis)]
  TQ -->|pop tasks| W
  W -->|result artifact + confidence score| RQ[(Review Queue<br>Redis)]
  RQ --> J

  %% ===== HITL routing =====
  J -->|High confidence| AUTO[Auto-Approve]
  J -->|Medium confidence| HITL[HITL Review Queue<br>Dashboard]
  J -->|Low confidence| RETRY[Reject / Retry<br>replan]

  HITL -->|Approve / Edit| AUTO
  HITL -->|Reject| RETRY
  RETRY --> P

  %% ===== Execution layer (via MCP tools) =====
  AUTO --> ACT[Execute Action via MCP Tools<br>post / reply / publish]

  %% ===== Persistence / Memory =====
  PG[(PostgreSQL<br>metadata + configs + logs)]
  WV[(Weaviate<br>semantic memory)]
  RS[(Redis<br>queues + short-term state)]

  O -->|read/write| PG
  P -->|retrieve persona + memories| WV
  W -->|tool calls + short-term state| RS
  RS --- TQ
  RS --- RQ
  ACT -->|write publish records| PG

  %% ===== External world behind MCP =====
  subgraph EXT["External Systems behind MCP Servers"]
  SM[Social Platforms<br>X, Instagram, TikTok]
  GEN[Media Generators<br>Image and Video]
  WEB[News and Web Data]
end


  ACT --> SM
  ACT --> GEN
  P --> WEB
