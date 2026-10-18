# Domain docs

This repo uses a **single-context** domain doc layout.

## Layout

The project's domain docs:

- `GLOSSARY.md` at the repo root — the canonical vocabulary for the project.
- `docs/adr/` at the repo root — the project's Architecture Decision Records, one file per decision.
- `docs/adr/archived/` at the repo root — the project ADRs no longer in force, kept as the historical record.

The workflow's own docs are kit-owned and live under `.agents/kit/`:

- `.agents/kit/GLOSSARY.md` — the vocabulary of the agent workflow.
- `.agents/kit/adr/` — the workflow's ADRs.
- `.agents/kit/adr/archived/` — the workflow ADRs no longer in force.

A project never edits a kit-owned file; a change to one is made in the agent-kit repo.

## Consumer rules

When a skill needs domain context:

1. Read `GLOSSARY.md` first and use its terms verbatim in specs, tickets, and code comments. Workflow terms are in `.agents/kit/GLOSSARY.md`.
2. If a term is missing, propose adding it to `GLOSSARY.md` rather than inventing a synonym.
3. Before making an architectural decision, check `docs/adr/` for prior decisions that constrain it.
4. When a new architectural decision is made, record it as a new ADR in `docs/adr/` using the existing numbering and format.
5. A decision about this project is a project ADR. A decision that changes the workflow is a change to the agent kit, made in the agent-kit repo and recorded as an ADR in `.agents/kit/adr/`.

## ADR format

Each project ADR lives at `docs/adr/NNNN-short-title.md`; once it is superseded it moves to `docs/adr/archived/NNNN-short-title.md`, which either party may do. The workflow's ADRs follow the same format, at `.agents/kit/adr/` and `.agents/kit/adr/archived/`. Each contains:

- **Title**
- **Status** (proposed / accepted / superseded)
- **Context**
- **Decision**
- **Consequences**

Numbers are never reused: take the highest number under `docs/adr/` and `docs/adr/archived/` together, and increment it. The workflow's ADRs are numbered on their own under `.agents/kit/adr/`, and a project never renumbers them.

This five-field form is a deliberate local choice: the `domain-modeling` skill's `ADR-FORMAT.md` defaults to a three-sentence minimum, which this repo does not use. The ADRs in `.agents/kit/adr/` and `docs/adr/` are the reference for the shape.

A **Decision** records the intent of the choice — what was decided and why — not the mechanism that carries it out. *How* a decision is implemented belongs to the document that owns that mechanism, because a mechanism named in an accepted ADR couples the record to an implementation detail and lets the ADR silently go false: nothing revisits an accepted ADR when the mechanism changes. The guardrails clause of workflow ADR 0006 is the reference — it states that an agent's `dev` commit is refused, and leaves the check itself to `.agents/kit/workflow.md`.

A change to a decision recorded in an ADR is a new ADR that supersedes it. The ADRs run in parallel: each decides one subject, and none restates the others. A superseded project ADR moves to `docs/adr/archived/` once no decision in it remains in force; a superseded workflow ADR moves to `.agents/kit/adr/archived/` in the agent-kit repo. A change to the agent workflow's state machine or vocabulary always needs a new ADR in `.agents/kit/adr/`; routine wording changes inside `.agents/kit/workflow.md` do not.
