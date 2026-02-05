# Technical Specification — Project Chimera

## Purpose and Scope

This document defines the abstract data schemas, interface contracts, and invariant rules
required to support the functional behaviors described in `specs/functional.md`.

It specifies **what data shapes and guarantees MUST exist**, not **how they are implemented**.
No storage technologies, execution engines, infrastructure components, security mechanisms,
or deployment architectures are implied unless explicitly stated.

All definitions in this document exist to constrain agent behavior, enforce specification
authority, and prevent implicit assumptions during implementation.

---

## Conventions

- Field types use a minimal type system: `string`, `number`, `boolean`, `object`, `array`, `enum`, `timestamp` (ISO-8601).
- All top-level entities and interface outputs MUST include:
  - `spec_version` — semantic version of the governing repository specification.
  - `contract_version` — semantic version of the specific schema or contract.
- Identifiers are opaque, stable strings (UUID-style), referenced generically as `id`.
- Traceability fields (`objective_id`, `plan_id`, `task_id`, `content_id`) enable end-to-end auditing.
- JSON examples are illustrative only and MUST NOT be interpreted as prescriptive storage schemas.
- All error responses MUST conform to the `ErrorContract` defined in this document.

---

## Schema Versioning & Traceability

- Every contract document and runtime artifact MUST record:
  - `spec_version`
  - `contract_version`
- All decisions, evaluations, and executions MUST be traceable to the spec version
  active at the time they occurred.
- Traceability invariants:
  - A `Plan` MUST reference `objective_id`.
  - A `Task` MUST reference `plan_id`.
  - A `SkillInvocation` MUST reference `task_id` when executed to satisfy a Task.

### Example Header Fragment (Illustrative Only)

```json
{
  "spec_version": "1.0.0",
  "contract_version": "1.0.0"
}


---

## Core Data Entities
### Objective

### Purpose
A human-defined, high-level intent that establishes what the system is expected to achieve, along with explicit constraints and success conditions. Objectives are the root of all downstream planning, execution, and evaluation.

### Canonical Fields
- `id` (string) — required  
- `owner_id` (string) — required (human operator or system identifier)  
- `title` (string) — required  
- `description` (string) — optional, human-readable context  
- `constraints` (object) — optional (e.g., success criteria, prohibited actions, policy boundaries)  
- `spec_version` (string) — required  
- `contract_version` (string) — required  
- `created_at` (timestamp) — required  
- `status` (enum: draft, active, completed, cancelled) — required  

### Invariants
- When `status` is `active`, `constraints` MUST include at least one of:
  - `success_criteria`
  - `prohibitions`
- Objectives MUST be immutable once `status` transitions to `completed` or `cancelled`.
- Every `Plan` MUST reference a valid `objective_id`.

### Example
```json
{
  "id": "obj_123",
  "owner_id": "human_42",
  "title": "Produce 3 informational posts on topic X",
  "description": "High-level objective with allowed channels and prohibited content.",
  "constraints": {
    "success_criteria": ["3 posts produced", "no policy violations"],
    "prohibitions": ["no financial advice", "no PII exposure"]
  },
  "spec_version": "1.0.0",
  "contract_version": "1.0.0",
  "created_at": "2026-02-05T12:00:00Z",
  "status": "active"
}

```
### Objective

### Purpose
An ordered, reviewable decomposition of an Objective into discrete Tasks.  
A Plan represents *intentional structure*, not execution. It exists to make agent behavior predictable, inspectable, and auditable before work is performed.

### Canonical Fields
- `id` (string) — required  
- `objective_id` (string) — required  
- `author_agent_id` (string) — required (Planner Agent identifier)  
- `tasks` (array of objects) — required (ordered task references or task skeletons)  
- `summary` (string) — optional, human-readable overview  
- `spec_version` (string) — required  
- `contract_version` (string) — required  
- `created_at` (timestamp) — required  
- `revision_of` (string) — optional (reference to prior plan if this is a revision)  
- `status` (enum: draft, pending_review, approved, revised, deprecated) — required  

### Invariants
- Every Plan MUST reference exactly one valid `objective_id`.
- Each entry in `tasks` MUST include a `task_id` and an explicit `task_order` integer.
- Tasks within a Plan MUST be ordered deterministically by `task_order`.
- A Plan with `status` set to `approved` MUST NOT be modified; changes require creation of a new Plan with `revision_of` referencing the prior Plan.
- The Plan’s `spec_version` MUST match the referenced Objective’s `spec_version`, unless an explicit divergence is recorded and approved by a Human Operator.

### Example
```json
{
  "id": "plan_456",
  "objective_id": "obj_123",
  "author_agent_id": "planner_7",
  "tasks": [
    {"task_id": "task_a", "task_order": 1},
    {"task_id": "task_b", "task_order": 2}
  ],
  "summary": "Decompose objective into research and content creation tasks.",
  "spec_version": "1.0.0",
  "contract_version": "1.0.0",
  "created_at": "2026-02-05T12:10:00Z",
  "status": "pending_review"
}
```

---

### Task

#### Purpose
A Task is the smallest executable unit of work derived from a Plan.  
Each Task represents a single, well-scoped intent that MUST be executed using an explicit SkillContract and MUST declare its inputs, outputs, and risk characteristics.

Tasks are the boundary at which autonomy is tightly constrained: no task may execute without clear contracts, traceability, and required approvals.

#### Canonical Fields
- `id` (string) — required  
- `plan_id` (string) — required  
- `intent` (string) — required (human-readable description of what the task is meant to accomplish)  
- `input_schema` (object) — required (machine-readable schema defining required inputs)  
- `output_schema` (object) — required (machine-readable schema defining expected outputs)  
- `skill_contract_id` (string) — optional (required if task invokes a skill or external action)  
- `risk_level` (enum: low, medium, high) — required  
- `requires_approval` (boolean) — required  
- `spec_version` (string) — required  
- `contract_version` (string) — required  
- `created_at` (timestamp) — required  
- `status` (enum: open, in_progress, blocked, completed, failed) — required  

#### Invariants
- Every Task MUST reference a valid `plan_id`.
- `input_schema` and `output_schema` MUST be explicit and machine-readable.
- If `risk_level` is `high`, then `requires_approval` MUST be `true`.
- A Task that invokes a Skill MUST specify `skill_contract_id`.
- Tasks MUST NOT perform external or irreversible actions unless:
  - `requires_approval` is `true`, and  
  - a valid Approval record exists prior to execution.
- Tasks MAY NOT transition to `in_progress` if required approvals are missing.

#### Example
```json
{
  "id": "task_a",
  "plan_id": "plan_456",
  "intent": "Gather three credible reference sources related to the topic",
  "input_schema": {
    "type": "object",
    "properties": {
      "topic": { "type": "string" }
    },
    "required": ["topic"]
  },
  "output_schema": {
    "type": "array",
    "items": { "type": "string" }
  },
  "skill_contract_id": "skill_search_v1",
  "risk_level": "low",
  "requires_approval": false,
  "spec_version": "1.0.0",
  "contract_version": "1.0.0",
  "created_at": "2026-02-05T12:11:00Z",
  "status": "open"
}
```

---

### SkillContract

#### Purpose
A SkillContract defines the canonical interface for a reusable capability (“skill”).  
It specifies the required input schema, output schema, and failure semantics so that planners and workers can invoke the skill without hidden assumptions.

A SkillContract describes *what the skill accepts and returns*, not how the skill is implemented.

#### Canonical Fields
- `id` (string) — required  
- `name` (string) — required  
- `description` (string) — optional  
- `input_schema` (object) — required (machine-readable schema defining inputs)  
- `output_schema` (object) — required (machine-readable schema defining outputs)  
- `failure_modes` (array of objects) — optional (each includes `code`, `description`, `retryable`)  
- `version` (string) — required (contract-level semantic version)  
- `spec_version` (string) — required  
- `created_at` (timestamp) — required  
- `owner_id` (string) — optional  

#### Invariants
- A Task that references `skill_contract_id` MUST validate that its `input_schema` is compatible with the SkillContract’s `input_schema`.
- SkillContracts MUST be explicit and bounded; unbounded free-text schemas are disallowed for skills that can cause irreversible or external effects.
- Any change to `input_schema` or `output_schema` MUST result in a new `version`.
- If `failure_modes` are declared, any `failure_code` returned by a SkillInvocation MUST match one of the declared `failure_modes.code` values.

#### Example
```json
{
  "id": "skill_search_v1",
  "name": "search_references",
  "description": "Return curated reference titles and URLs for a given topic.",
  "input_schema": {
    "type": "object",
    "properties": {
      "topic": { "type": "string" }
    },
    "required": ["topic"]
  },
  "output_schema": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "title": { "type": "string" },
        "url": { "type": "string" }
      },
      "required": ["title", "url"]
    }
  },
  "failure_modes": [
    { "code": "NO_RESULTS", "description": "No results found", "retryable": false },
    { "code": "UPSTREAM_ERROR", "description": "External provider error", "retryable": true }
  ],
  "version": "1.0.0",
  "spec_version": "1.0.0",
  "created_at": "2026-02-01T09:00:00Z",
  "owner_id": "system"
}
```

---
### SkillInvocation

#### Purpose
A SkillInvocation is the concrete execution record of a SkillContract performed to satisfy a specific Task.  
It captures who invoked the skill, what inputs were provided, what outputs were produced, and the outcome (success/failure/partial), enabling traceability and auditing without implying any particular runtime or infrastructure.

#### Canonical Fields
- `id` (string) — required  
- `task_id` (string) — required  
- `skill_contract_id` (string) — required  
- `caller_agent_id` (string) — required (Worker Agent identifier)  
- `input` (object) — required (MUST conform to SkillContract.input_schema)  
- `output` (object) — optional (MUST conform to SkillContract.output_schema if present)  
- `outcome` (enum: success, failure, partial) — required  
- `failure_code` (string) — optional (MUST map to a declared SkillContract.failure_modes.code)  
- `spec_version` (string) — required  
- `contract_version` (string) — required  
- `started_at` (timestamp) — required  
- `ended_at` (timestamp) — optional  
- `metadata` (object) — optional (non-functional metadata; MUST NOT be required for correctness)

#### Invariants
- Every SkillInvocation MUST reference a valid `task_id` and `skill_contract_id`.
- `input` MUST validate against the referenced SkillContract `input_schema`.
- If `output` is present, it MUST validate against the referenced SkillContract `output_schema`.
- If `outcome` is `failure` and `failure_code` is present, `failure_code` MUST match one of the SkillContract’s declared `failure_modes.code`.
- If the referenced Task requires approval (`requires_approval: true`), then a valid Approval record MUST exist prior to invoking the skill.
- SkillInvocations MUST include the `spec_version` and `contract_version` active at invocation time.

#### Example
```json
{
  "id": "invoke_789",
  "task_id": "task_a",
  "skill_contract_id": "skill_search_v1",
  "caller_agent_id": "worker_11",
  "input": { "topic": "agentic infrastructure" },
  "output": [
    { "title": "Spec-driven agents", "url": "https://example.com/article" }
  ],
  "outcome": "success",
  "spec_version": "1.0.0",
  "contract_version": "1.0.0",
  "started_at": "2026-02-05T12:12:00Z",
  "ended_at": "2026-02-05T12:12:03Z",
  "metadata": { "notes": "Curated results only; no duplicates." }
}
```

---

### Judgment

#### Purpose
A Judgment is an evaluation artifact produced by a Judge Agent.  
It records an explicit assessment of an artifact (Task output, SkillInvocation, or Plan) against specification-defined criteria, enabling traceable acceptance, rejection, or rework decisions.

Judgments are authoritative quality and safety gates; they do not modify artifacts directly but determine allowed next actions.

#### Canonical Fields
- `id` (string) — required  
- `artifact_id` (string) — required (identifier of the evaluated artifact)  
- `artifact_type` (enum: task_output, skill_invocation, plan) — required  
- `evaluator_id` (string) — required (Judge Agent identifier)  
- `outcome` (enum: accept, reject, request_rework) — required  
- `reasons` (array of strings) — optional (human-readable explanations)  
- `evidence` (object) — optional (references to logs, outputs, or telemetry; MUST include spec context if present)  
- `spec_version` (string) — required  
- `contract_version` (string) — required  
- `created_at` (timestamp) — required  
- `next_action` (enum: none, replan, reinvoke_skill, escalate_to_human) — required  

#### Invariants
- Every Judgment MUST reference a valid `artifact_id` and `artifact_type`.
- `outcome` MUST be one of `accept`, `reject`, or `request_rework`.
- If `outcome` is `reject`, at least one entry in `reasons` MUST be provided.
- `next_action` MUST be derivable from `outcome` and governing specification rules.
- Judgments MUST NOT directly mutate Plans, Tasks, or SkillInvocations; they only authorize or block subsequent actions.
- All Judgments MUST record the active `spec_version` and `contract_version`.

#### Example
```json
{
  "id": "judg_321",
  "artifact_id": "invoke_789",
  "artifact_type": "skill_invocation",
  "evaluator_id": "judge_2",
  "outcome": "accept",
  "reasons": ["Meets relevance and source requirements."],
  "evidence": {
    "logs_ref": "telemetry_001",
    "spec_version": "1.0.0"
  },
  "spec_version": "1.0.0",
  "contract_version": "1.0.0",
  "created_at": "2026-02-05T12:13:00Z",
  "next_action": "none"
}
```

---

### Approval

#### Purpose
An Approval is a human-in-the-loop authorization record that explicitly permits or denies an action requiring human consent.  
Approvals act as mandatory gates for tasks, plans, or skill invocations that carry external, irreversible, or high-impact effects.

An Approval does not execute actions; it authorizes whether an action may proceed.

#### Canonical Fields
- `id` (string) — required  
- `target_type` (enum: task, plan, skill_invocation) — required  
- `target_id` (string) — required  
- `approver_id` (string) — required (human operator identifier)  
- `decision` (enum: approved, rejected) — required  
- `rationale` (string) — optional (REQUIRED when `decision` is `rejected`)  
- `created_at` (timestamp) — required  
- `spec_version` (string) — required  
- `contract_version` (string) — required  
- `required_by` (string) — required (reference to the spec section or rule mandating approval)  
- `expires_at` (timestamp) — optional  

#### Invariants
- An Approval MUST reference a valid `target_id` and `target_type`.
- If `decision` is `rejected`, `rationale` MUST be provided.
- Tasks or SkillInvocations that require approval MUST NOT transition to execution unless an Approval exists with `decision: approved`.
- Approvals MUST be evaluated against the `spec_version` active at the time of approval.
- Expired Approvals MUST be treated as non-existent for authorization purposes.

#### Example
```json
{
  "id": "appr_555",
  "target_type": "task",
  "target_id": "task_critical",
  "approver_id": "human_42",
  "decision": "approved",
  "rationale": "Reviewed sources and constraints; safe to proceed.",
  "created_at": "2026-02-05T12:20:00Z",
  "spec_version": "1.0.0",
  "contract_version": "1.0.0",
  "required_by": "specs/technical.md#approval-invariants",
  "expires_at": "2026-02-06T12:20:00Z"
}
```

---

## Content / Video Metadata (ERD-Level Schema)

### ContentArtifact
Represents produced content (e.g., video, post, draft) generated by the system.

**Purpose:**  
Provide a canonical metadata record for content artifacts without implying live publishing or platform integration.

**Canonical fields:**
- `id` (string) — required
- `task_id` (string) — required
- `objective_id` (string) — required
- `content_type` (enum: video, image, text, mixed) — required
- `title` (string) — optional
- `description` (string) — optional
- `status` (enum: draft, reviewed, approved, rejected) — required
- `created_by` (string) — required (agent or human id)
- `created_at` (timestamp) — required
- `spec_version` (string) — required
- `contract_version` (string) — required

**Invariants:**
- ContentArtifact MUST be traceable to exactly one Task.
- ContentArtifact creation does not imply external publication.
- State transitions MAY require Approval depending on governing spec rules.

**ERD Relationship Summary:**
- Objective 1 ── * Plan  
- Plan 1 ── * Task  
- Task 1 ── * SkillInvocation  
- Task 1 ── * ContentArtifact  
- ContentArtifact 1 ── * Judgment  
- Task / Plan / SkillInvocation 0..1 ── Approval

---

## Interface Contracts

### Submit Objective

#### Purpose
Create a new Objective that defines a human-authored, high-level intent for the system.
This interface establishes the root artifact from which all planning, execution, evaluation,
and auditing flows originate.

#### Input
```json
{
  "title": "string",
  "description": "string (optional)",
  "owner_id": "string",
  "constraints": {
    "success_criteria": ["string"],
    "prohibitions": ["string"]
  },
  "spec_version": "string",
  "contract_version": "string"
}
```
#### Output
```json
{
  "objective_id": "string",
  "status": "draft | active",
  "created_at": "timestamp",
  "spec_version": "string",
  "contract_version": "string"
}
```
#### Errors

All errors returned by this interface MUST conform to the `ErrorContract`.

- **INVALID_INPUT** — Required fields are missing, malformed, or violate schema rules.
- **SPEC_VERSION_MISMATCH** — Submitted `spec_version` does not match or is incompatible with the active repository specification.
- **DUPLICATE_OBJECTIVE** — An equivalent Objective already exists under the same owner or scope.

#### Invariants

- A successful call MUST create exactly one `Objective`.
- The returned `objective_id` MUST be globally unique and immutable.
- The `Objective` MUST record the provided `spec_version` and `contract_version`.
- When an `Objective` is created with status `active`, at least one constraint  
  (`success_criteria` or `prohibitions`) MUST be present.
- This interface MUST NOT perform planning, task generation, skill execution,  
  or any external side effects.

#### Notes

- Validation rules for objective equivalence and deduplication are policy-driven  
  and defined outside this interface.
- Authentication, authorization, transport protocol, and UI concerns are explicitly out of scope.
- This interface defines **what must be true**, not **how it is implemented**.


### Generate Plan

#### Purpose
Generate an ordered, reviewable decomposition of an existing `Objective` into a `Plan` containing discrete `Task` definitions, strictly validated against the active specifications.

This interface is used by a Planner Agent and MUST enforce spec authority before any plan is accepted.

---

#### Input

```json
{
  "objective_id": "string",
  "planner_agent_id": "string",
  "summary": "string (optional)",
  "spec_version": "string",
  "contract_version": "string"
}
```
#### Output
```json
{
  "plan_id": "string",
  "objective_id": "string",
  "status": "draft | pending_review",
  "created_at": "timestamp",
  "spec_version": "string",
  "contract_version": "string"
}
```
#### Output Semantics

- A newly created `Plan` is returned with status `draft` or `pending_review`.
- The `Plan` MUST reference the governing `objective_id`.
- No `Task` is executed as part of this interface.

#### Errors

All errors returned by this interface MUST conform to the `ErrorContract`.

- **OBJECTIVE_NOT_FOUND** — The referenced `objective_id` does not exist.
- **SPEC_VERSION_MISMATCH** — The submitted `spec_version` is incompatible with the Objective or repository specification.
- **PLAN_VALIDATION_ERROR** — The proposed `Plan` violates one or more specification constraints.
- **NOT_AUTHORIZED** — The caller is not permitted to generate a `Plan` for the Objective.

#### Invariants

- A successful call MUST create exactly one `Plan`.
- The created `Plan` MUST reference exactly one `objective_id`.
- The `Plan` MUST NOT include `Task`s that violate:
  - Spec-defined constraints
  - Declared non-goals
  - Skill contract requirements
- If the `Plan` includes any `Task` with `risk_level = high`, the `Plan` MUST be marked `pending_review`.
- The `Plan` MUST record the `spec_version` and `contract_version` used at creation time.
- This interface MUST NOT execute `Task`s, invoke `Skill`s, or cause external side effects.

#### Notes

- Task definitions may be included inline within the `Plan` or created as separate `Task` entities, but MUST remain logically linked.
- Validation logic for plan correctness is specification-driven and deterministic; heuristic planning is disallowed.
- The interface defines **what constitutes a valid Plan**, not **how planning is performed**.
- Transport protocol, authentication, and UI concerns are explicitly out of scope.


### Invoke Skill

#### Purpose
Execute a `SkillContract` in order to satisfy a specific `Task`.
This interface records a concrete `SkillInvocation` and enforces all contract, approval, and specification constraints before execution.

This interface defines *what conditions must be met to invoke a skill* and *what is recorded as a result*, not how the skill is implemented or executed.

#### Input
```json
{
  "task_id": "string",
  "skill_contract_id": "string",
  "caller_agent_id": "string",
  "input": "object (MUST conform to SkillContract.input_schema)",
  "spec_version": "string",
  "contract_version": "string"
}
```
#### Output`
```json 
{
  "skill_invocation_id": "string",
  "task_id": "string",
  "outcome": "success | failure | partial",
  "failure_code": "string (optional)",
  "started_at": "timestamp",
  "ended_at": "timestamp (optional)",
  "spec_version": "string",
  "contract_version": "string"
}
```
#### Errors

All errors returned by this interface MUST conform to the `ErrorContract`.

- **TASK_NOT_FOUND** — The referenced `task_id` does not exist.
- **SKILL_CONTRACT_NOT_FOUND** — The referenced `skill_contract_id` does not exist.
- **MISSING_APPROVAL** — The Task requires approval and no valid Approval record exists.
- **SKILL_INPUT_VALIDATION_ERROR** — Input does not conform to the SkillContract input schema.
- **SPEC_VERSION_MISMATCH** — Submitted `spec_version` is incompatible with the active specification.
- **SKILL_EXECUTION_ERROR** — The skill failed during execution.

#### Invariants

- A successful call MUST create exactly one `SkillInvocation`.
- The `SkillInvocation` MUST reference a valid `task_id` and `skill_contract_id`.
- `input` MUST validate against the referenced SkillContract `input_schema`.
- If `outcome` is `failure` and `failure_code` is present, it MUST match a declared failure mode of the SkillContract.
- If the referenced `Task.requires_approval` is `true`, a valid Approval with decision `approved` MUST exist before invocation.
- The `SkillInvocation` MUST record the active `spec_version` and `contract_version`.
- This interface MUST NOT bypass Judgment or Approval mechanisms defined elsewhere in the specification.

#### Notes

- Skill execution MAY be synchronous or asynchronous; timing semantics are out of scope.
- Retry behavior is governed by declared SkillContract failure modes, not by this interface.
- Transport protocol, authentication, execution environment, and infrastructure details are explicitly out of scope.
- This interface defines **what is permitted and recorded**, not **how the skill runs internally**.


---
### Record Judgment

#### Purpose
Record an evaluation produced by a Judge Agent for a specified artifact.
This interface captures an authoritative assessment (accept, reject, or request rework) and determines the permitted next action without mutating the evaluated artifact.

#### Input
```json
{
  "artifact_id": "string",
  "artifact_type": "task_output | skill_invocation | plan",
  "evaluator_id": "string",
  "outcome": "accept | reject | request_rework",
  "reasons": ["string"],
  "evidence": "object (optional; SHOULD reference logs or artifacts and include spec context)",
  "spec_version": "string",
  "contract_version": "string"
}
```
#### Output
```json
{
  "judgment_id": "string",
  "artifact_id": "string",
  "outcome": "accept | reject | request_rework",
  "created_at": "timestamp",
  "next_action": "none | replan | reinvoke_skill | escalate_to_human",
  "spec_version": "string",
  "contract_version": "string"
}
```
#### Errors

All errors returned by this interface MUST conform to the `ErrorContract`.

- **ARTIFACT_NOT_FOUND** — The referenced `artifact_id` does not exist.
- **INVALID_JUDGMENT** — The `outcome`, `artifact_type`, or required fields are invalid.
- **SPEC_VERSION_MISMATCH** — Submitted `spec_version` is incompatible with the active specification.
- **NOT_AUTHORIZED** — The caller is not permitted to record judgments.

#### Invariants

- A successful call MUST create exactly one `Judgment`.
- `artifact_id` and `artifact_type` MUST reference a valid, existing artifact.
- `outcome` MUST be one of `accept`, `reject`, or `request_rework`.
- If `outcome` is `reject`, at least one entry in `reasons` MUST be provided.
- `next_action` MUST be derivable from `outcome` and the governing specification rules.
- Judgments MUST NOT directly mutate `Plan`s, `Task`s, or `SkillInvocation`s.
- The `Judgment` MUST record the active `spec_version` and `contract_version`.

#### Notes

- Evidence is optional but SHOULD be provided for `reject` and `request_rework` outcomes to support traceability.
- The determination of `next_action` is specification-driven and deterministic, not heuristic.
- Transport protocol, authentication, and UI concerns are explicitly out of scope.
- This interface defines **what is recorded and authorized**, not **how evaluation is performed**.

---

### Approve Target

#### Purpose
Record a human-in-the-loop authorization decision for a specified target.
This interface explicitly permits or denies execution of actions that require human consent due to external, irreversible, or high-impact effects.

Approvals authorize actions; they do not execute them.

#### Input
```json
{
  "target_type": "task | plan | skill_invocation",
  "target_id": "string",
  "approver_id": "string",
  "decision": "approved | rejected",
  "rationale": "string (required when decision is rejected)",
  "spec_version": "string",
  "contract_version": "string"
}
```
#### Output
```json
{
  "approval_id": "string",
  "target_type": "task | plan | skill_invocation",
  "target_id": "string",
  "decision": "approved | rejected",
  "created_at": "timestamp",
  "spec_version": "string",
  "contract_version": "string"
}
```
#### Errors

All errors returned by this interface MUST conform to the `ErrorContract`.

- **TARGET_NOT_FOUND** — The referenced `target_id` does not exist.
- **NOT_AUTHORIZED** — The caller is not permitted to approve or reject the target.
- **INVALID_DECISION** — The provided `decision` or required fields are invalid.
- **SPEC_VERSION_MISMATCH** — Submitted `spec_version` is incompatible with the active specification.

#### Invariants

- A successful call MUST create exactly one `Approval`.
- `target_type` and `target_id` MUST reference a valid, existing artifact.
- If `decision` is `rejected`, `rationale` MUST be provided.
- Approvals MUST be evaluated against the active `spec_version` at decision time.
- Targets that require approval MUST NOT transition to execution unless an `Approval` exists with `decision: approved`.
- Approvals MUST NOT directly execute actions or mutate the target artifact.

#### Notes

- Approval expiration and re-approval policies are specification-driven and defined outside this interface.
- Transport protocol, authentication, authorization mechanisms, and UI concerns are explicitly out of scope.
- This interface defines **what authorization is recorded**, not **how human approval is obtained**.


---

## ErrorContract

#### Purpose
Define a standard, machine-readable structure for all errors returned by interfaces in this specification.
The ErrorContract ensures consistent error handling, traceability, and debuggability across agents and tools without exposing implementation details.

#### Structure
```json
{
  "error_code": "string",
  "error_message": "string",
  "details": "object (optional)",
  "spec_version": "string",
  "contract_version": "string",
  "timestamp": "timestamp",
  "actor_id": "string (optional)"
}
```
#### Field Semantics

- `error_code` — Machine-readable identifier (e.g., `MISSING_APPROVAL`, `SPEC_VERSION_MISMATCH`).
- `error_message` — Human-readable summary describing the failure.
- `details` — Optional structured data for diagnostics and testing (MUST NOT include secrets).
- `spec_version` — Specification version governing the action at the time of error.
- `contract_version` — Version of the `ErrorContract` schema.
- `timestamp` — Time the error was generated (ISO-8601).
- `actor_id` — Optional identifier of the agent or human that caused the error.

#### Invariants

- All interface errors MUST conform to this structure.
- `error_code`, `error_message`, `spec_version`, `contract_version`, and `timestamp` are REQUIRED.
- `error_code` values MUST be stable and documented by the interface that emits them.
- Errors MUST NOT cause side effects or mutate system state.
- Errors MUST be safe to log and transmit.

#### Common Error Codes (Non-Exhaustive)

- `INVALID_INPUT`
- `SPEC_VERSION_MISMATCH`
- `NOT_AUTHORIZED`
- `OBJECTIVE_NOT_FOUND`
- `PLAN_VALIDATION_ERROR`
- `TASK_NOT_FOUND`
- `SKILL_CONTRACT_NOT_FOUND`
- `MISSING_APPROVAL`
- `INVALID_JUDGMENT`
- `ARTIFACT_NOT_FOUND`
- `SKILL_EXECUTION_ERROR`
- `SEQUENCE_CONFLICT`
- `DUPLICATE_OBJECTIVE`

#### Notes

- Interfaces MAY define additional, domain-specific error codes.
- Error handling policies (retry, escalation, mitigation) are defined by the governing specification, not by this contract.
- This contract defines **how errors are represented**, not **how they are handled or displayed**.

---

### Emit Telemetry

#### Purpose
Append a structured, tamper-evident telemetry record that captures a system decision,
state transition, or action for auditability and traceability.

This interface is the authoritative mechanism for recording what happened, who caused it,
and which specification governed the event.

#### Input
```json
{
  "event_type": "string",
  "subject_id": "string (optional)",
  "actor_id": "string",
  "payload": "object (MUST include spec_version and contract_version context)",
  "sequence_number": "number",
  "spec_version": "string",
  "contract_version": "string",
  "created_at": "timestamp"
}
```
#### Output
```json
{
  "telemetry_id": "string",
  "sequence_number": "number",
  "created_at": "timestamp"
}
```

#### Errors

All errors returned by this interface MUST conform to the `ErrorContract`.

- **INVALID_PAYLOAD** — Required fields are missing, malformed, or violate schema rules.
- **SEQUENCE_CONFLICT** — The provided `sequence_number` conflicts with an existing event.
- **SPEC_VERSION_MISMATCH** — Submitted `spec_version` is incompatible with the active specification.
- **NOT_AUTHORIZED** — The caller is not permitted to emit telemetry events.

#### Invariants

- A successful call MUST create exactly one `TelemetryEvent`.
- `event_type` and `actor_id` MUST be present on all telemetry records.
- `spec_version` and `contract_version` MUST reflect the versions active at the time of the event.
- `sequence_number` MUST be monotonic within its defined scope (objective-scoped or system-scoped).
- Telemetry events MUST NOT modify system state or trigger execution.
- Every state transition of an `Objective`, `Plan`, `Task`, `SkillInvocation`, `Judgment`, or `Approval`
  MUST result in at least one corresponding telemetry event.

#### Notes

- The scope of `sequence_number` monotonicity (per-objective or global) is implementation-defined
  but MUST be consistent.
- Telemetry storage, signing, and tamper-resistance mechanisms are explicitly out of scope.
- This interface defines **what is recorded and guaranteed**, not **how telemetry is stored or transmitted**.


