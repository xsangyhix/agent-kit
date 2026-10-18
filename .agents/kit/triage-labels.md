# Triage labels

This repo uses the five canonical triage roles with their default label strings.

| Role | Label string |
| --- | --- |
| Needs triage | `needs-triage` |
| Needs more info | `needs-info` |
| Ready for an agent | `ready-for-agent` |
| Ready for a human | `ready-for-human` |
| Won't fix | `wontfix` |

## What a label is

A label is a **planning marker**, independent of an issue's status. Status says where the work is in the workflow (`.agents/kit/workflow.md`); a label says how to treat it when planning, filtering and reviewing. `wontfix` is the clearest case: it marks an issue the user will not revisit as *do not plan on this*, so it can be filtered out of a planning or retrospective pass without hiding that it exists. It is also the one label that survives a close, because it records *why* the issue closed: a decision not to revisit it, rather than an approval.

Labels are:

- written as a `Labels:` line near the top of an issue file,
- optional while the issue is active,
- removed when the issue closes, except `wontfix`.

Being an independent axis means a label is **not** derived from the status, and the two are not required to correspond. The pairings below are conventions.

## Conventional pairings

| Status | Label |
| --- | --- |
| `draft` | `needs-triage` |
| `awaiting-agent` | `ready-for-agent` |
| `questioning` | `needs-info` |
| `in-progress` | `ready-for-agent` |
| `in-review` | `ready-for-human` |
| `review-feedback` | `needs-info` |
| `blocked` | — (add `wontfix` if you do not intend to revisit) |
| `done` | `wontfix` if the close is a decision not to revisit; otherwise — |

`wontfix` attaches in whatever state the decision is made — conventionally `blocked` — and is the one label a closed issue keeps.

## Notes

- The label string equals the role name; no overrides are configured.
- Because the issue tracker is local markdown, labels are `Labels:` lines rather than a platform feature.
- The `triage` skill reads and writes these labels. Triage input is raw issues only — see `.agents/kit/GLOSSARY.md`.
