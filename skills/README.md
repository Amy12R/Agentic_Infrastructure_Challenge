# Skills — Project Chimera (Runtime)

## What a “Skill” is (in Chimera)
A **Skill** is a reusable runtime capability invoked by Chimera agents during execution.
Skills are NOT developer tools. They run inside the Planner → Worker → Judge flow and must be
called using explicit, versioned contracts.

## Non-negotiable rules
- Every Skill MUST define explicit `input_schema` and `output_schema`.
- Every Skill contract MUST include:
  - `id`, `name`, `version`
  - `spec_version`
  - `created_at`
  - `failure_modes` (at least one)
- Skills MUST NOT perform **externally visible or irreversible actions** unless the Task includes an approved interface contract and any required HITL approvals.
- Every Skill invocation MUST be traceable via telemetry and tied to Objective → Plan → Task.
- High-risk skills (publishing/engagement) MUST be designed for HITL gating and auditability.

## Skills in this repository
1. `skill_trend_scan_v1` — find trending topics and sources
2. `skill_write_post_v1` — generate platform-ready text outputs
3. `skill_generate_media_v1` — generate or request media artifacts (image/video/script/storyboard metadata)
4. `skill_publish_and_engage_v1` — publish content and perform engagement actions (high risk)

## Testing expectation (later tasks)
Tests will validate:
- contracts include required top-level fields and valid JSON structure
- input validation matches the contract schemas
- output shapes match declared output schemas (including `spec_version` and `contract_version`)
- failure codes match declared failure modes
