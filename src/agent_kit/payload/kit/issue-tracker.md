# Issue tracker

This repo tracks issues as **local markdown files**.

## Where issues live

Tracked units live under `.scratch/<feature>/issues/`:

```
.scratch/
  my-feature/
    retro-YYYY-MM-DD-<slug>.md   ← not a tracked unit: a retro
    issues/
      01-<short-slug>.md
      closed/
        02-<short-slug>.md
  another-feature/
    issues/
```

- One issue per file.
- Filenames are `<NN>-<short-slug>.md`, numbered from `01` in dependency order, blockers first.
- Closed issues move to `issues/closed/`.
- Documents about an effort that are **not** tracked units — retros, research notes — sit beside `issues/` under the feature, not inside it.

## Templates

### Ticket

```
Labels: ready-for-agent
Status: awaiting-agent

## Description

## Blocked by

None.

## Acceptance criteria

- [ ] ...
```

### Spec

Specs are optional; see `.agents/kit/GLOSSARY.md`. A spec is an issue like any other and uses the same header and location.

```
Labels: ready-for-agent
Status: awaiting-agent

## Problem Statement

## Solution

## User Stories

## Implementation Decisions

## Testing Decisions

## Out of Scope

## Further Notes
```

## Conventions

- **Paths** are repo-root-relative (`src/app/module.py`), never relative to the file.
- **No H1.** The filename carries the number and the slug.
- **Header** is `Labels:` then `Status:`. `Labels` is optional while active, and is removed at close except `wontfix`. States are defined in `.agents/kit/workflow.md`.
- **Body** is plain markdown: context, acceptance criteria, notes.

## Overrides to the skill defaults

The `/to-tickets` skill publishes local tickets with a template of its own. This repo diverges in three ways; apply these when following it:

| Skill default | This repo |
| --- | --- |
| `# <NN>: <title>` as the first line | no H1; the header starts with `Labels:` when present, otherwise `Status:` |
| a single `**Status:** <label>` line | `Labels:` and `Status:` on separate lines, with the label independent of the status |
| no convention for closing | close moves the file to `issues/closed/` and strips the `Labels:` line, keeping `wontfix` |

## How skills should interact with it

- **Reading**: list `.scratch/<feature>/issues/` and read the relevant files.
- **Creating**: write a new `<NN>-<short-slug>.md` under `.scratch/<feature>/issues/`.
- **Updating**: edit the markdown file in place.
- **Closing**: remove the `Labels:` line unless it is `wontfix`, move the file to `issues/closed/`, then stage the moved file. A move records the content that was already staged, so an edit made after staging — the approval's `Status: done`, for instance — is left out of the commit.

There is no external tracker; do not call `gh`, `glab`, or any other CLI.

## PRs as a request surface

Off. External pull requests are not part of the triage queue for this repo.
