# 0005 — Issue labels

- **Status**: accepted
- **Context**: ADR 0002 made a label an axis independent of the status, and fixed that labels are removed at close. The second half threw information away: `wontfix` marks a close that is a decision not to revisit, and stripping it left the `closed/` list unable to say why a ticket ended. The closed file is the record of that decision, and the label is the cheapest place to keep it.
- **Decision**:
  - **Vocabulary.** The labels are the five canonical triage roles, each string equal to its role name: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.
  - **A planning marker.** A label says how to treat a unit when planning, filtering and reviewing; the status says where the work is. The two are not derived from each other, and are not required to correspond.
  - **Lifecycle.** A label is optional while the unit is active. At close every label is removed **except `wontfix`**, which stays: it records that the close was a decision not to revisit, not an approval.
- **Consequences**: `.agents/kit/triage-labels.md` carries the vocabulary and the conventional pairings, `.agents/kit/GLOSSARY.md` the terms, and the close instruction in `.agents/kit/issue-tracker.md` the mechanics. The guardrail refuses a closed unit that carries any other label. Tickets closed before this decision carry no label; they are the record of a rule that has changed, and are not backfilled.
