# Project Chimera Constitution

**Version:** 1.0.0  
**Ratification Date:** 2026-02-06

---

## Purpose and Scope

This constitution defines the high-level governance, safety, and traceability invariants that apply to Project Chimera — a spec-driven system for designing, governing, and executing autonomous influencer agents operating as a hierarchical swarm (Planner → Worker → Judge) under a single human operator.

It applies to all system artifacts, agents, human operators, and processes that create, evaluate, or cause external effects on behalf of Chimera. Implementation details and developer workflows belong to complementary specifications.

---

## Authority & Source of Truth

- The canonical authority for system behavior and constraints is the project specification set. The following spec documents are the authoritative sources of truth:
  - `meta.md`
  - `functional.md`
  - `technical.md`

- When a conflict exists between implementation artifacts and the authoritative specs, the specs take precedence. Implementations MUST be revised or halted until the discrepancy is resolved by an approved spec amendment.

---

## Role Separation Invariants

### Roles and primary responsibilities:

- **Planner** — defines intent decomposition into discrete, reviewable plans and acceptance criteria. Produces structured plans referencing specific spec sections and traceability identifiers.
- **Worker** — executes approved, bounded tasks according to declared contracts and input/output schemas. Produces auditable outputs and invocation records; MUST NOT unilaterally change plan intent.
- **Judge** — evaluates artifacts (plans, task outputs, skill invocations) against spec-defined criteria and emits one of: Accept, Reject (with reasons), Request Rework (with guidance). Judge decisions are authoritative gating artifacts.
- **Human Operator** — supervisory authority for escalation, final approvals where required, and constitutional/amendment sign-off.

### Invariants:

- Each artifact (Objective, Plan, Task, SkillInvocation, Judgment, Approval) MUST record its governing `spec_version` and `contract_version` at creation time.
- Planner MUST NOT execute tasks; Worker MUST NOT approve their own outputs; Judge MUST NOT perform the Planner or Worker roles for the same artifact being judged.
- Role behavior is auditable and traceable to an explicit actor identifier.

---

## Human-In-The-Loop (HITL) Governance

- HITL is mandatory and non-bypassable for any action that is high-risk or irreversible. Examples (non-exhaustive):
  - Publishing or posting to external platforms
  - Deleting production data or records
  - Expenditure of funds or initiation of payments
  - Actions involving political, medical, legal, or financial claims

- Decision routing by confidence is a governance guideline: high-confidence automation may be permitted where explicitly authorized by spec; medium/low confidence MUST require human review or be blocked by the Judge. Any exception MUST be explicitly documented in the spec and approved by the Human Operator.

- Human approvals MUST be recorded as an explicit Approval artifact that references the governing spec clause, the target artifact, approver identity, timestamp, decision, and rationale.

---

## External Interaction Boundary

- External effects (network publication, platform posting, data deletion, billing calls, credentialed API operations) MAY occur only via:
  - explicitly defined SkillContracts, and
  - approved tool interfaces and MCP contracts described in the specs.
- Direct implementation of platform APIs or any ad-hoc external integration by runtime agents is prohibited unless a SkillContract exists and the action is authorized by an Approval where required.
- Any new external integration MUST be introduced as a spec change with associated contract, failure modes, and HITL requirements before it can be invoked.

---

## Traceability & Audit Requirements

- Every substantive decision and action MUST be recorded with:
  - artifact identifiers (`objective_id`, `plan_id`, `task_id`, `skill_invocation_id`),
  - governing `spec_version` and `contract_version`,
  - actor id (agent or human), role, timestamp (ISO-8601),
  - input and output references (or pointers to their storage),
  - confidence score and risk level when applicable,
  - explicit links to the spec clause(s) used for evaluation.

- Judgments, Approvals, and SkillInvocations are first-class audit artifacts and MUST be retained according to the retention policy defined in the specs.
- Ambiguity handling: If a required spec clause is missing, ambiguous, or conflicting, all downstream execution MUST pause and the ambiguity MUST be resolved by a spec amendment or an explicit human operator decision recorded as an Approval referencing the decision rationale.

---

## Change Control & Amendment Process

- **Scope:** This constitution and the project specs are authoritative governance artifacts. Changes to either MUST follow controlled amendment procedures.

- **Amendment steps (high-level):**
  1. **Propose:** Draft amendment referencing affected sections and rationale; include migration/compatibility impact and proposed spec, version, or contract_version changes.
  2. **Review:** Internal technical review and safety assessment; include Judge evaluation for procedural impacts.
  3. **Human Approval:** The Human Operator (or delegated authority defined in the specs) MUST sign off the amendment.
  4. **Ratify & Publish:** Record the ratification date, increment semantic version according to impact (MAJOR for breaking governance changes, MINOR for new principles or expansions, PATCH for clarifications), and publish updated specs with an audit entry.
  5. **Propagate:** Update dependent artifacts and record follow-up tasks required for compliance.

- No amendment takes effect retroactively unless explicitly stated and approved; changes apply from the ratification timestamp forward for new artifacts and behaviors, unless a migration path is documented.

---

## Enforcement & Compliance

- Compliance is enforced by a combination of spec validation, automated checks, audit reviews, and human oversight. Non-compliant actions MUST be documented as audit exceptions and remediated by the Human Operator with corrective plans and approval.
- Any deviation that causes external harm, data loss, or legal exposure MUST trigger immediate escalation and an incident review recorded against the affected artifacts and specs.

---

## Final Principles

- Specs are authoritative, traceability is mandatory, HITL is non-bypassable for high-risk actions, and external effects are contract-first. Ambiguity halts execution until resolved by spec or explicit human approval.
