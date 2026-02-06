# skill_publish_and_engage_v1

## Purpose
Publish approved content and perform controlled engagement actions (such as replying, liking, or following) on external social platforms.

This skill is the **only** runtime capability allowed to cause irreversible, externally visible effects on third-party platforms.

---

## When it is used
- Referenced by Tasks that require interaction with external social platforms
- Invoked by Worker Agents **only after** Judge evaluation and required human-in-the-loop (HITL) approval
- Executed at the final stage of the Planner → Worker → Judge flow

Typical usage:
- Publishing approved posts or media
- Responding to existing posts or users
- Performing limited engagement actions under explicit instruction

---

## Contract
- `contract.json` is the authoritative source of truth for all inputs and outputs
- All inputs MUST conform to the declared `input_schema`
- All outputs MUST conform to the declared `output_schema`
- An approved `interface_contract_id` is REQUIRED for any execution
- The output MUST include `spec_version` and `contract_version`

This skill MUST NOT execute if required approvals or interface contracts are missing.

---

## Failure modes
- `MISSING_APPROVAL`  
  The requested action requires human approval, but no valid HITL Approval record exists.

- `INTERFACE_CONTRACT_MISSING`  
  No approved interface contract was provided for the external platform interaction.

- `UPSTREAM_ERROR`  
  The external platform integration failed, timed out, or returned an error.  
  This failure may be retryable according to task policy.

- `INVALID_INPUT`  
  The provided input did not conform to the declared input schema.

---

## Risk level
High  

This skill performs irreversible actions on external systems and **always requires governance**.  
Human-in-the-loop (HITL) approval is mandatory whenever required by the governing specification or task risk level.

---

## Explicit non-responsibilities
This skill MUST NOT:
- Generate or modify content
- Decide strategy, tone, or messaging
- Perform planning or prioritization
- Bypass Judge decisions or HITL approval
- Access external systems without an approved interface contract
- Perform bulk, autonomous, or self-directed engagement

Any attempt to do so is a specification violation.

---

## Governance notes
- All executions of this skill MUST be traceable via telemetry
- Every invocation MUST be associated with a Task, Plan, and Objective
- This skill exists to **centralize and constrain risk**, not to optimize speed or reach
