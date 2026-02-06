# skill_generate_media_v1

## Purpose
Generate or request media-related artifacts (images, videos, scripts, or storyboards) based on a prompt, and return structured metadata describing the generated assets.

This skill is responsible for **media creation requests**, not for publishing or distributing content.

---

## When it is used
- Referenced by Tasks that require visual or audiovisual assets to support generated content
- Invoked by Worker Agents after text content or creative direction has been defined
- Used **before** any publishing or engagement actions
- Operates in the middle of the Planner → Worker → Judge flow

Typical usage:
- After a topic or post has been written
- Before content is reviewed, approved, or published

---

## Contract
- `contract.json` is the authoritative source of truth for this skill
- All inputs provided by a Worker MUST conform to `input_schema`
- All outputs returned MUST conform to `output_schema`
- The skill returns **metadata references**, not assumptions about storage, hosting, or publication
- The skill MUST include `spec_version` and `contract_version` in its output

This skill does **not** guarantee that assets are publicly accessible or published.

---

## Failure modes
- `UPSTREAM_ERROR`  
  The underlying media generation service failed, timed out, or returned an error.  
  This failure may be retryable depending on task policy.

- `INVALID_INPUT`  
  The provided input did not conform to the declared input schema.  
  This failure is not retryable without changing the input.

---

## Risk level
Medium  

This skill may consume external compute or third-party services but does **not** perform irreversible external actions.  
Human-in-the-loop (HITL) approval is **not required by default**, but downstream tasks using the generated assets may require approval depending on context.

---

## Explicit non-responsibilities
This skill MUST NOT:
- Publish media to social platforms
- Interact with users or audiences
- Perform engagement actions
- Decide branding, strategy, or content direction
- Bypass Planner, Judge, or approval mechanisms

Those responsibilities belong to other skills or system roles.

---

## Governance notes
- This skill MUST be invoked only as part of an Objective → Plan → Task flow (no “free-running” generation).
- Every invocation MUST be traceable to a Task/Plan/Objective via telemetry.
- Outputs MUST remain metadata-only: returning a `uri` is allowed, but it MUST NOT imply public hosting or publication.
- If the input prompt requests disallowed content, the skill MUST fail safely (for example using `INVALID_INPUT` or a policy-related failure code if you add one later).
