Labels: ready-for-agent
Status: awaiting-agent

## Description

The README's install and upgrade examples hardcode a developer's absolute Windows path (`D:\Marcin\PycharmProjects\agent-kit`), which is meaningless to anyone else. Generalise the examples so they are copy-pasteable from a fresh checkout or a released package.

## Blocked by

None.

## Acceptance criteria

- [ ] The `pipx install` / `uv tool install` examples no longer contain `D:\Marcin\PycharmProjects\agent-kit`; they use a placeholder such as `<path-to-this-repo>` (or the published package name once released).
- [ ] The upgrade examples (`pipx install --force`, `uv tool install --force`) stay consistent with the install examples.
- [ ] The suite still passes and `py -3.14 tools/check_payload_sync.py` still exits 0.

## Out of scope

- Changing the README's "Credits and licenses" wording (agent-kit/25-choose-a-license).
- Anything under `src/agent_kit/payload/` (README is not payload).
