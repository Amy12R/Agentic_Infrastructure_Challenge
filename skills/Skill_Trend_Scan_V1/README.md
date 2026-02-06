# skill_trend_scan_v1

## Purpose
Identify and return a curated list of trending topics, hooks, and supporting sources based on specified platforms, regions, and languages.

This skill provides **situational awareness** for the system and supplies structured inputs for downstream planning and content generation.

---

## When it is used
- Referenced by Tasks that require topic discovery or trend analysis
- Invoked by Worker Agents at the **beginning** of a content or campaign workflow
- Used before content writing, media generation, or publishing
- Operates early in the Planner → Worker → Judge flow

Typical usage:
- Discovering what topics are currently relevant
- Providing hooks and rationales for planning decisions

---

## Contract
- `contract.json` is the authoritative source of truth for this skill
- All inputs provided by a Worker MUST conform to `input_schema`
- All outputs returned MUST conform to `output_schema`
- Each returned topic MUST include supporting sources and a confidence score
- The output MUST include `spec_version` and `contract_version`

This skill returns **information only** and does not perform any content generation or external actions.

---

## Failure modes
- `NO_RESULTS`  
  No relevant trends were found for the requested platforms, filters, or constraints.  
  This failure may be retryable with adjusted inputs.

- `UPSTREAM_ERROR`  
  A required upstream data provider failed, timed out, or returned an error.  
  This failure may be retryable depending on task policy.

- `INVALID_INPUT`  
  The provided input did not conform to the declared input schema.  
  This failure is not retryable without changing the input.

---

## Risk level
Low  

This skill performs read-only data retrieval and analysis.  
Human-in-the-loop (HITL) approval is **not required** for its execution.

---

## Explicit non-responsibilities
This skill MUST NOT:
- Generate or rewrite content
- Produce media assets
- Publish or engage on social platforms
- Decide strategy, tone, or messaging
- Perform planning or prioritization
- Trigger downstream actions directly

Those responsibilities belong to other skills or system roles.

---

## Governance notes
- This skill MUST be invoked only as part of an Objective → Plan → Task flow.
- Every invocation MUST be traceable to a Task, Plan, and Objective via telemetry.
- Outputs are advisory and informational; they MUST NOT be treated as instructions.
- Confidence scores are signals for downstream evaluation, not guarantees of correctness.
