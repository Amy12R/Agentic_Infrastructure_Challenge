# Research — Tooling Strategy (Task 2.3 Sub-Task A)

**Note:** this strategy uses `{}` `mcp.json` as the source of truth.  
The `tenxfeedbackanalytics` server is intentionally excluded.  
Focused developer MCP servers: `filesystem` and `git`.  
`postgres` and `docker` are noted as optional/deferred (not configured yet).

---

## Developer Tools (MCP) vs Runtime Skills

- **Developer Tools (MCP):**  
  Local developer-facing servers and CLIs used during development, debugging, and repository operations (e.g. filesystem emulation, git helper servers). These are part of the development environment and must not be treated as production runtime capabilities.

- **Runtime Skills:**  
  Reusable production capabilities invoked by Planner/Worker agents at runtime (e.g. content-publishing skills, platform integrations). Runtime Skills require explicit SkillContracts, traceability fields, and HITL gating per the spec; they cannot assume access to developer MCP tooling.

---

## MCP Server: filesystem

- **Purpose:**  
  Provide a stable, reproducible filesystem interface for local development and file-oriented integrations via MCP (maps to entry in `{}` `mcp.json` that runs `@modelcontextprotocol/server-filesystem`).

- **Why chosen:**  
  Lightweight, standard MCP developer server for testing file reads/writes and for tools that expect an MCP filesystem backend; mirrors how developer tooling will interact with repository files without granting runtime agents direct filesystem access.

- **Typical workflows:**
  - Start a local filesystem MCP server to run file-read/write experiments against the workspace.
  - Use the server to validate file-based SkillContract inputs/outputs during offline development.
  - Exercise repository automation scripts (linting, generators) against an MCP-backed filesystem to confirm behavior.

- **Risks / guardrails:**
  - Ensure server runs only in developer environments; never expose to public networks.
  - Treat data written during development as non-production and avoid using secrets or production credentials.
  - Record `spec_version` and traceability IDs in any artifacts produced during tests.

---

## MCP Server: git

- **Purpose:**  
  Provide a git-focused MCP server useful for scripted git operations, simulated remote interactions, and programmatic repo workflows (matches entry running `@cyanheads/git-mcp-server` in `{}` `mcp.json`).

- **Why chosen:**  
  Enables deterministic, instrumented git operations in the developer toolchain (e.g., automated commits, diffs, branch ops) without granting runtime agents direct access to developer git credentials or remote repos.

- **Typical workflows:**
  - Run automated repo checks (status, diff, blame) via MCP to produce audit-ready outputs.
  - Stage/commit changes programmatically for local developer automation (pre-commit simulation, CI-local runs).
  - Simulate branch operations during feature development and review flows.

- **Risks / guardrails:**
  - Prevent accidental pushes to remote repositories — require explicit human approval for any `push` operations.
  - Avoid embedding or exposing real credentials; use tokenized or mocked remotes for tests.
  - Ensure all automated commits include traceability metadata (`objective_id / plan_id` when applicable).

---

## Optional / Deferred Servers

- **Postgres (optional / deferred):**
  - Present in `{}` `mcp.json` as a potential MCP server, but not configured here.
  - Consider adding when integration tests require a system-of-record instance for metadata or when validating DB-backed behaviors.
  - Marked deferred until schema and credentials are approved.

- **Docker (optional / deferred):**
  - Listed in `{}` `mcp.json` but left as deferred.
  - Add when containerized dev services are necessary (e.g., full stack local dev), and only after defining isolation and network guardrails.

---

## Verification evidence — how to confirm servers are running in VS Code

- **Start servers from an integrated terminal (recommended reproducible commands):**

```bash
npx -y @modelcontextprotocol/server-filesystem "{workspaceFolder}"
npx -y @cyanheads/git-mcp-server
```
- **Expected verification signals:**
  - Terminal prints a ready/listening message for each server (e.g. `server-filesystem: listening` or `git-mcp-server: ready`), and no immediate errors on startup.
  - Check VS Code Output / Extension logs for an MCP or workspace-related channel showing successful server registration.
  - Confirm process exists (Bash):

```bash
# Option 1 (recommended): show running node processes with full command line
pgrep -a node

# Option 2 (fallback): grep the process list (works on most systems)
ps aux | grep -E 'node|npx' | grep -v grep

- **Functional smoke tests:**
  - **Filesystem:** run a simple read via the MCP filesystem client or a local script that uses the MCP filesystem endpoint and confirm correct file content returns.
  - **Git:** run a small MCP-driven git status/diff command (or use the git MCP client) and verify expected repository state is returned.

- **Evidence to capture for audit/tracing:**
  - Save startup logs and note the exact `{}` `mcp.json` used (commit hash or `spec_version`) and the timestamp.
  - Include `spec_version` and any `traceability` IDs in test invocations so results are auditable.

---

## Minimal operational guardrails

- Only use these MCP developer servers in local or trusted dev environments.
- Never treat MCP developer servers as runtime production endpoints—document any transition from developer servers to runtime skills in the spec and increment `contract_version` accordingly.
- Require human approval before configuring or enabling optional servers (`postgres`, `docker`) for development with real data.
