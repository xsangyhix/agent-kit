"""The only harness-specific facts (design §6)."""

from collections import namedtuple

Harness = namedtuple("Harness", ["name", "skills_dir", "agent_markers"])

HARNESSES = {
    "opencode": Harness(
        name="opencode",
        skills_dir=".agents/skills",
        agent_markers=("AI_AGENT", "OPENCODE"),
    ),
}
DEFAULT_HARNESS = "opencode"
