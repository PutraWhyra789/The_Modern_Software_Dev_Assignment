# Week 5 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
### Automation A: Warp Drive saved prompts, rules, MCP servers

### Goals
Reusable AI prompts for test running and docs sync,
accessible from any Warp session via Warp Drive.

### Design
- `test-runner`: Runs pytest + coverage, diagnoses failures automatically
- `docs-sync`: Regenerates docs/API.md from live OpenAPI schema

### Warp Drive Share Links
- test-runner: [paste link dari Warp Drive]
- docs-sync: [paste link dari Warp Drive]

### Before vs After
- Before: Manually type pytest commands, manually update API.md
- After: One prompt invocation handles both, with AI-driven diagnosis

### How It Resolves Pain Points
Eliminates repetitive command typing and manual documentation drift
between API implementation and docs/API.md.

---

### Automation B: Multi‑agent workflows in Warp 

### Goals
Run Task #7 and Task #8 concurrently in separate Warp tabs
to reduce total implementation time.

### Roles
- Tab 1 Agent: Error handling + response envelopes (Task #7)
- Tab 2 Agent: Pagination for all collections (Task #8)

### Coordination Strategy
Used git worktree to give each agent an isolated working directory,
preventing file conflicts on shared backend files.

### Concurrency Wins
Both tasks completed in parallel — estimated 2x faster than sequential.

### Risks/Failures
- Risk: Both agents modify `main.py` → resolved via worktree isolation
- Monitored each tab manually before merging changes

### Autonomy Levels
- Task #7: Full autonomy for implementation, manual review before commit
- Task #8: Full autonomy for implementation, manual review before commit

### Before vs After
- Before: Implement Task #7 → test → then Task #8 → test (sequential)
- After: Both tasks run simultaneously, merge after review

### How It Resolves Pain Points
Halves implementation time for independent backend tasks.

---

## Tasks Completed
- Task #7: Error handling & response envelopes (easy-medium)
- Task #8: Pagination for all collections (easy)


### (Optional) Automation C: Any Additional Automations
a. Design of each automation, including goals, inputs/outputs, steps
> TODO

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> TODO

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> TODO

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> TODO

e. How you used the automation (what pain point it resolves or accelerates)
> TODO
