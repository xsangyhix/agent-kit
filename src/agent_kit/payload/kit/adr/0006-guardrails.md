# 0006 — Workflow guardrails

- **Status**: accepted
- **Context**: ADR 0002 put guardrails behind the workflow, after nothing had stopped an agent from committing on `dev` and the branch had to be repaired by hand. Each check has been reimplemented since, and will be again; the decision is that the checks exist and refuse, not the script that performs them.
- **Decision**: Versioned pre-commit hooks refuse a `dev` commit made in an Agent session, refuse a commit when the tracker path is gitignored, and validate the tracker's file invariants. *How* each check is implemented is owned by `.agents/kit/workflow.md`, which is free to change alongside the mechanisms it describes.
- **Consequences**: The workflow is enforced rather than merely documented, and the enforcement is versioned with the repository instead of living in one clone's `.git/hooks/`. Naming a mechanism here would couple the record to an implementation detail and let the decision go false in silence.
