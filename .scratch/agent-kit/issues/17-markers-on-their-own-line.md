Labels: ready-for-agent
Status: awaiting-agent

## Description

Found in the 2026-10-18 code review of the agent-kit effort. `installer.find_block` counts marker **substrings**, so an `AGENTS.md` that only *mentions* a marker in its prose, e.g. `` `<!-- agent-kit:begin -->` ``, is reported as a broken block, and `init` and `update` refuse ("found 1 begin and 0 end"). The refusal is safe but surprising, and a project documenting the kit in its own `AGENTS.md` cannot get past it.

The user decided on 2026-10-18 during the review: a marker counts only when it stands on a line of its own. This amends design §5's marker rules. Record the rule in `README.md` (the kit's design record per `docs/agents/project.md`); do not edit the rc-machines design file.

The rule:

- A line is a begin (end) marker when the line, with trailing whitespace and a trailing `\r` removed, equals `<!-- agent-kit:begin -->` (`<!-- agent-kit:end -->`) exactly. Leading whitespace means it is *not* a marker.
- Counting, the "one each, begin before end" check, and the refusal messages of §5 apply to marker lines only.
- Text between the marker lines is the block, as today; the lock's `agents_block` hash rule does not change.
- Marker text inside a line of prose, or indented, is ordinary text: it is preserved outside the block and never counted.

Backwards compatibility: every `AGENTS.md` the kit has written has its markers on their own lines, so existing installs (rc-machines, this repo) are unaffected. Prove it by running `update` against this repo with no local changes.

Test-Driven Development.

## Blocked by

- agent-kit/13-shared-test-support

## Acceptance criteria

- [ ] An `AGENTS.md` mentioning a marker inline (and indented) with no real block: `init` appends the block and exits 0; the mention is preserved byte for byte.
- [ ] The same mention alongside a real block: `init` and `update` replace only the real block.
- [ ] One-only, duplicate and end-before-begin marker *lines* still refuse with exit 1 and the existing messages.
- [ ] A marker line with trailing spaces or a CRLF ending still counts.
- [ ] `PYTHONPATH=src py -3.14 -m agent_kit update` in this repo reports no local changes.
- [ ] `README.md` states the whole-line rule.
- [ ] The whole suite passes: `py -3.14 -m unittest discover -s tests -t . -v`.

## Out of scope

- Changing the marker strings.
- Line-ending handling of the written block (agent-kit/15-agents-md-line-endings).
