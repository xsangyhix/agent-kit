# Glossary

Canonical vocabulary for this project. Skills read this file first and use its terms verbatim. If a term is missing, propose adding it here rather than inventing a synonym. The agent workflow's own terms are in `.agents/kit/GLOSSARY.md`.

## Terms

- **Payload** — the files under `src/agent_kit/payload/` that the tool installs into a project; the source of truth for everything the kit ships. _Avoid_: kit files, templates (they are one part of it).
- **Installed copy** — `.agents/kit/` and `.agents/skills/` in this repo, produced from the payload by `agent-kit update`; never edited by hand.
- **Skills snapshot** — the vendored copy of Matt Pocock's skills at a pinned commit, recorded in `UPSTREAM`. _Avoid_: skill library (the concept; the snapshot is the pinned copy).
