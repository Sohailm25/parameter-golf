# ABOUTME: Verifies that AGENTS.md preserves the research-operating rigor expected for this competition repo.
# ABOUTME: Prevents the workspace from degrading into a lightweight folder without the required experiment discipline.

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8") if (ROOT / "AGENTS.md").exists() else ""

REQUIRED_SECTIONS = [
    "### 3. The Research Documents Are the Spec",
    "### 4. Execution Order",
    "### 5. Experiment Design Defaults",
    "### 6. Run Design Guardrails",
    "### 7. Required Experiment Lanes",
    "### 8. Results Registration",
    "### 9. Iteration Archive And Golden Set",
    "### 10. Branch Truth",
]

REQUIRED_PHRASES = [
    "smallest experiment",
    "confirmatory split",
    "THOUGHT_LOG.md",
    "tmux",
    "results/RESULTS_INDEX.md",
    "leaderboard.md",
    "atomic change",
    "golden set",
]


class AgentsRigorTest(unittest.TestCase):
    def test_agents_contains_required_rigor_sections(self) -> None:
        missing = [section for section in REQUIRED_SECTIONS if section not in AGENTS]
        self.assertEqual([], missing)

    def test_agents_contains_core_rigor_phrases(self) -> None:
        missing = [phrase for phrase in REQUIRED_PHRASES if phrase not in AGENTS]
        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
