# Glossary

This file holds the agent workflow's vocabulary. Project terms live in the project's root `GLOSSARY.md`.

## Agent workflow

- **Idea** — an unsharpened thought, before anything is tracked. Sharpened by grilling.
- **Issue** — any tracked unit. One markdown file whose role is `raw issue`, `spec`, or `ticket`. _Avoid_: task, artifact.
- **Raw issue** — an issue that arrived from outside the workflow: a bug report or a request the agent did not create. The only input triage accepts. _Avoid_: report, request.
- **Spec** — the feature-level role of an issue: problem, solution, user stories, implementation and testing decisions, out of scope. Optional; used when an effort is large enough to need a document of its own.
- **Ticket** — the unit-of-work role of an issue: one tracer-bullet slice, declaring the tickets that block it. _Avoid_: task.
- **Follow-up** — a need a ticket raises but does not build. It becomes a ticket of its own, referenced by its identifier — `<feature>/<NN>-<short-slug>`, the filename without `.md` — never by a path, which goes stale when the follow-up closes. A closed ticket is never amended afterwards: the identifier is the record (rule 13, `.agents/kit/workflow.md`). _Avoid_: child ticket, sub-issue.
- **Retro** — findings about the agent's environment after a session. Not an issue.
- **Status** — an issue's position in the workflow; exactly one state at a time.
- **Label** — a planning marker on an issue, independent of its status, drawn from the five canonical triage roles. Removed when the issue is closed, except `wontfix`, which stays to record a close that is a decision not to revisit.
- **Agent branch** — a branch named `agent/<feature-slug>`, branched off `dev`. The agent never touches `dev`.
- **Agent session** — a shell owned by a coding-agent harness rather than by the human. The harness sets `AI_AGENT` or `OPENCODE` in the environment of every shell it starts, which is how the `dev` commit guardrail recognises one.

### Agent kit

- **Agent kit** — the project-agnostic agent setup (workflow docs, guardrails, skill library) packaged as its own repo and installed into a project with the `agent-kit` tool. _Avoid_: template, package, framework.
- **Kit-owned file** — a file the agent kit installs and replaces on update: everything under `.agents/kit/` and the harness's skills folder. A project does not edit it; a change to it is made in the kit repo.
- **Project-owned file** — a file the agent kit creates once as a starter, if it is missing, and never changes afterwards: `AGENTS.md` outside the kit block, `GLOSSARY.md`, `docs/adr/`, `docs/agents/project.md`, `.agents/hooks.local/`.
- **Kit block** — the region of `AGENTS.md` between `<!-- agent-kit:begin -->` and `<!-- agent-kit:end -->`. Kit-owned, inside a project-owned file.
- **Kit lock** — `.agents/kit.lock`: the installed kit version, the harness, and a hash of every kit-owned file, so an update can tell a local edit from a stale file.
- **Harness** — the coding-agent program that runs agent sessions (today only opencode). It decides where skills are found and which environment variables mark an agent session.
- **Local hook** — `.agents/hooks.local/pre-commit`: an optional, project-owned extension the kit's pre-commit hook runs last.

### States

- **`draft`** — created but not released; the agent ignores it. The hold state, and where the user's raw issues start.
- **`awaiting-agent`** — released and pickable: the agent decides whether to ask or to begin.
- **`questioning`** — the agent is asking and waiting for answers.
- **`in-progress`** — the agent is working.
- **`in-review`** — the agent has submitted and the user is reviewing.
- **`review-feedback`** — the user has asked for changes.
- **`blocked`** — held; nobody has decided how to handle it. Not pickable. The user leaves it either by unblocking it or by closing it as one they will not revisit.
- **`done`** — closed: approved, or a decision not to revisit. Terminal.

### Review

- **Review** — comments the user leaves in the issue file, under `## Review`.
- **Approval** — the user agreeing that submitted work is finished, by setting `Status: done`. That status change *is* the approval; there is no separate sign-off. The other path to `done` — closing a ticket the user will not revisit — is not an approval, and `wontfix` records it.
- **Close** — the agent's mechanical follow-up to a unit reaching `done`, by approval or by a decision not to revisit: remove the labels, keeping any `wontfix`, then move the file to `issues/closed/`.
