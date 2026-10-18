# Agent workflow

Version: 3

This document defines how an agent works on an issue, from first draft to done. It is a state machine: every issue is in exactly one state, and every transition is performed by exactly one actor. A transition may be open to either party, but each performance of it still has exactly one actor.

Vocabulary is defined in `.agents/kit/GLOSSARY.md`. Layout, templates and paths are in `.agents/kit/issue-tracker.md`. This document is the process.

## States

| State | Meaning | Set by | Label convention |
| --- | --- | --- | --- |
| `draft` | Created but not released. The agent ignores it. | user | `needs-triage` |
| `awaiting-agent` | Released and pickable: the agent decides whether to ask or to begin. | user | `ready-for-agent` |
| `questioning` | The agent is asking and waiting for answers. | agent | `needs-info` |
| `in-progress` | The agent is working. | agent | `ready-for-agent` |
| `in-review` | Submitted; the user is reviewing. | agent | `ready-for-human` |
| `review-feedback` | The user has asked for changes. | user | `needs-info` |
| `blocked` | Held; nobody has decided how to handle it. Not pickable. | either | — (add `wontfix` if not revisiting) |
| `done` | Closed: approved, or the user will not revisit it. Terminal. | user | `wontfix` if that is why it closed; removed otherwise |

The "Set by" column is the point of this document: a state the agent owns, the agent sets without asking.

## Transitions

```
draft            ──(user releases)──▶                 awaiting-agent

awaiting-agent   ──(agent asks)──▶                    questioning
awaiting-agent   ──(agent ready)──▶                   in-progress

questioning      ──(user answers)──▶                  awaiting-agent

in-progress      ──(agent finishes)──▶                in-review
in-progress      ──(agent blocked)──▶                 blocked

in-review        ──(user approves)──▶                 done
in-review        ──(user wants changes)──▶            review-feedback
in-review        ──(either party finds a blocker)──▶  blocked

review-feedback  ──(agent resumes)──▶                 in-progress

blocked          ──(user unblocks)──▶                 awaiting-agent

any non-done     ──(user will not revisit)──▶         done

done             ──(agent closes)──▶                  issues/closed/
```

That is the complete list. If a needed transition is missing, that is a gap in this document, not a licence to improvise — raise it with the user.

## Picking up work

The agent picks up issues in `awaiting-agent`. `draft` and `blocked` are never pickable. Either party may set `blocked`; only the user brings a ticket out of it — by unblocking it to `awaiting-agent`, or by closing it as one they will not revisit.

`Blocked by` edges are respected independently of the state: the agent does not start a ticket whose listed blockers are not `done`. A ticket that cannot proceed, and that nobody has decided how to handle, is set to `blocked`.

More than one ticket may be pickable at once. The `Blocked by` edges are the only constraint: the agent chooses among the unblocked ones by its own judgement. Nothing ranks them — not a recorded priority, not the numbering. When the user names a ticket, that decides the choice.

## Definition of ready

`draft ──(user releases)──▶ awaiting-agent` is the user's transition, so this is the bar they hold work to before releasing it — and the one the agent applies when cutting tickets.

An issue is ready to release when:

- the problem is stated and the acceptance criteria are checkable;
- **the happy path is not the only path**: what happens on invalid configuration, at construction time, and on misuse is answered rather than discovered during implementation;
- backwards compatibility is addressed explicitly — which existing components, callers or releases this touches, and how they are covered;
- the blockers are known, and any not yet `done` are recorded under `## Blocked by`;
- **what is out of scope is written down**, because scope that is only implied gets rediscovered mid-implementation.

## Issue file format

The header is:

```
Labels: <label>
Status: <state>
```

There is no H1: the filename carries the number and the slug. `Labels` is optional while the issue is active; it is removed when the issue closes, except `wontfix`, which stays to record a close that is a decision not to revisit. Templates are in `.agents/kit/issue-tracker.md`.

Sections:

- `## Description` — what the issue is about.
- `## Blocked by` — tickets that gate this one, or `None`. Omit for specs.
- `## Acceptance criteria` — what done looks like, as checkboxes.
- `## Questions` — numbered questions from the agent, each followed by the user's answer.
- `## Review` — comments from the user, and the agent's responses.

## Rules for the agent

1. **Never touch `dev`.** Work only on your own branch; a pre-commit hook refuses an agent session's commit on `dev`. Before your first edit, confirm the branch: if you are not on your own branch, stop and ask.
2. **Branch naming**: `agent/<feature-slug>`, branched off `dev`, where feature-slug is the `.scratch/<feature>/` directory name. Use `agent/<NN>-<slug>` only when tickets within one effort run in parallel.
3. **Commits**: you decide, but each commit is small and logical. Stage everything the commit is to carry, and read the staged set back before you commit: unstaged content is not in the commit, and a file edited after it was staged is committed in its earlier form.
4. **English**: everywhere — replies, commit messages, issue files.
5. **Push**: not required; the user handles pushing.
6. **Tests**: Test-Driven Development only. The project's test command is in `docs/agents/project.md`.
7. **Project rules**: `docs/agents/project.md` holds this project's own rules. Read it before your first edit.
8. **Glossary**: any new term goes into `GLOSSARY.md`.
9. **ADRs**: an architectural decision goes into `docs/adr/`. A change to the state machine or to the vocabulary needs a new ADR in `.agents/kit/adr/`; routine wording inside this file does not.
10. **Draft issues**: ignored. If asked to work on one, ask the user to release it (`Status: awaiting-agent`).
11. **Creating issues**: the user creates raw issues. You create tickets, defaulting to `awaiting-agent`; create a `draft` only when explicitly asked.
12. **Paths in issue files**: repo-root-relative (`src/app/module.py`), never relative to the file.
13. **Follow-ups**: a follow-up a ticket raises becomes a ticket of its own, referenced by its identifier — `<feature>/<NN>-<short-slug>`, the filename without `.md` — never by a path, which goes stale when the follow-up closes and moves to `issues/closed/`. A closed ticket is never amended to track the follow-up's later status: the identifier is the record.

## Review and close

Review happens as comments in the issue file, under `## Review`. There is no separate merge-request document.

The user approves by setting `Status: done`. That status change *is* the approval — there is no separate sign-off line to look for.

The user may also close a ticket they will not revisit, by setting `Status: done` from any state that is not `done`. That is not an approval and needs no review round: the `wontfix` label records why it closed, and stays.

Either way the agent performs the close: remove the `Labels:` line unless it is `wontfix`, move the file to `.scratch/<feature>/issues/closed/`, and stage the moved file.

## Guardrails

`.agents/kit/hooks/pre-commit` is the pre-commit hook. `agent-kit init` installs it once per clone by setting:

```
git config core.hooksPath .agents/kit/hooks
```

It:

- refuses a `dev` commit made in an **Agent session** (one of the variables named in `.agents/kit/harness.sh` is non-empty — `AI_AGENT` or `OPENCODE` by default) — the human's own release commit goes through;
- prints, on every `dev` commit, the mode it decided on, so the presence-detection above fails open *visibly* rather than silently;
- refuses a commit when `.scratch` is gitignored, which is what made the issue tracker unwritable;
- validates the tracker's invariants by running `.agents/kit/check_tracker.py`, which can also be run by hand at any time;
- runs the project's local hook, `.agents/hooks.local/pre-commit`, last, if it exists;
- reports a missing `.agents/kit/harness.sh` and falls back to the default agent markers.

If the tracker check refuses a commit, the message names the file and the problem. Fix the file; do not reach for `--no-verify`.
