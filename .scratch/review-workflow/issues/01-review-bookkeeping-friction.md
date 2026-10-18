Labels: needs-triage
Status: draft

## Description

The user keeps the tracker's bookkeeping by hand, and it is tiring. One ticket went through seven review rounds in a single session, and every round opened with two hand-edited header lines before the comment itself could be written.

Tracked home for note R1 of the front-loader retro of 2026-10-15 in the rc-machines repo (`.scratch/front-loader/retro-2026-10-15-issue-001-session.md`), which is the primary source and decided nothing. This issue exists so the finding is not re-derived from the note each time the workflow is revisited.

The facts the note carries:

- On every round the user flips `Status: in-review → review-feedback` and rewrites `Labels:` by hand; the agent flips it back on submission. The same hand-editing happens when the user releases a ticket and when they approve one.
- One round's header used `Status: waiting-for-agent`, which is not one of the eight states. `.agents/kit/check_tracker.py` (payload `src/agent_kit/payload/kit/check_tracker.py`) would have refused the commit, but nothing said so at edit time: the invalid status sat in the working tree until the agent read it and corrected it.
- One round's comments arrived with the header left at `in-review`, so the ticket read "the user is reviewing" while the user was handing it back. The agent found the comments by polling the file.
- A label is not derived from the status, so each status edit implies a second, conventional edit.
- Added 2026-10-16: a refusal from `.agents/kit/check_tracker.py` (payload `src/agent_kit/payload/kit/check_tracker.py`) names the file and the problem but not the line, and the human is the one reading it. Line-addressed refusals wait on a tool that can point at a line.

Directions to consider, none of them decided here:

- take the transitions the agent can infer off the user's hands where the workflow allows it;
- give the user one action that performs the transition, instead of two header lines;
- validate the header when it is written, not only at commit time;
- make the tracker readable and editable somewhere that can point at a line.

A change to the state machine or to the vocabulary needs an ADR superseding the one that decides it (`.agents/kit/adr/0004-workflow-state-machine.md`, payload `src/agent_kit/payload/kit/adr/0004-workflow-state-machine.md`; `.agents/kit/domain.md`, payload `src/agent_kit/payload/kit/domain.md`).
