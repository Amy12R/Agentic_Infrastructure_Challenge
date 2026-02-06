# skill_write_post_v1

## Purpose
Generate platform-ready text content from a given topic, optional tone guidance, and explicit constraints.  
This skill produces **draft copy** (and optional hashtags/CTA notes) but does not publish anything.

---

## When it is used
- Referenced by Tasks that require turning a topic or plan outline into written post text
- Invoked by Worker Agents after a topic has been selected (often after `skill_trend_scan_v1`)
- Used **before** media generation and **always before** publishing/engagement
- Operates in the middle of the Planner → Worker → Judge flow

Typical usage:
- Produce multiple post variants for review
- Adapt copy for a specific platform (X, Instagram, TikTok, YouTube)

---

## Contract
- `contract.json` is the authoritative source of truth for this skill
- All inputs MUST conform to the declared `input_schema`
- Outputs MUST conform to the declared `output_schema`
- The skill MUST return:
  - `spec_version`
  - `contract_version`
  - `items` containing one or more text variants
- The skill MAY include `hashtags`, `cta`, and `safety_notes`, but only `text` is required per item

This skill creates **text drafts** only; it does not perform external actions.

---

## Failure modes
- `POLICY_CONFLICT`  
  The requested tone/constraints/topic combination conflicts with safety or policy rules.  
  Not retryable without changing the request.

- `INVALID_INPUT`  
  The provided input did not conform to the declared input schema.  
  Not retryable without changing the input.

- `GENERATION_ERROR`  
  Content generation failed unexpectedly (model error, timeout, etc.).  
  May be retryable depending on task policy.

---

## Risk level
Medium  

This skill can produce content that may be sensitive depending on the topic, but it does **not** cause irreversible external effects.  
Human-in-the-loop (HITL) approval is **not required to run** this skill by default, but Judge review and/or HITL may be required **before any downstream publishing**.

---

## Explicit non-responsibilities
This skill MUST NOT:
- Publish or schedule posts on any platform
- Reply, like, follow, or engage with users
- Fetch live data from external sources (trend discovery belongs elsewhere)
- Decide campaign goals or strategy
- Bypass Planner/Judge decisions or HITL approval requirements

Those responsibilities belong to other skills or system roles.

---

## Governance notes
- This skill MUST be invoked only as part of an Objective → Plan → Task flow.
- Every invocation MUST be traceable to a Task, Plan, and Objective via telemetry.
- Outputs are **draft artifacts** and MUST be evaluated by the Judge against acceptance criteria before any external action is permitted.
- If a request conflicts with safety rules, the skill MUST fail safely using `POLICY_CONFLICT` rather than producing “almost compliant” content.
