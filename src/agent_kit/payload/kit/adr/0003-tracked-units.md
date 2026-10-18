# 0003 — Tracked units

- **Status**: accepted
- **Context**: ADR 0002 fixed the agent workflow as a single record, and its subjects have been read and changed as one ever since. This record carries the subject 0002 decided as Vocabulary, Layout, Header and Deviations, on its own: a change to the tracker's record shape should not have to rewrite the state machine or the guardrails. 0002 is archived under `.agents/kit/adr/archived/`.
- **Decision**:
  - **Vocabulary.** `Issue` is the supertype for any tracked file. Its roles are `Raw issue` (user-created, the only input `/triage` accepts), `Spec` (feature-level, optional — earned by size), and `Ticket` (the unit of work). `Idea` is pre-tracking; `Retro` is findings and is not tracked. `task` and `artifact` are not terms.
  - **Layout.** Tracked units live at `.scratch/<feature>/issues/<NN>-<slug>.md`, numbered from `01` in dependency order; closed units move to `.scratch/<feature>/issues/closed/`.
  - **Header.** `Labels:` then `Status:`, with no H1 (the filename carries the number and the slug). `Labels` is optional while the unit is active, and is an axis independent of the status. What happens to a label at close is decided by ADR-0005.
  - **Deviations.** Where these diverge from `/to-tickets`' local-tracker defaults, `.agents/kit/issue-tracker.md` records every override in one place.
- **Consequences**: `.agents/kit/GLOSSARY.md` and `.agents/kit/issue-tracker.md` carry these in full; this record is the decision, not the mechanism. ADR 0001 remains as the historical record.
