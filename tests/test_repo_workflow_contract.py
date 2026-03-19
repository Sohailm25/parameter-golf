# ABOUTME: Verifies that AGENTS.md codifies the main-branch source-of-truth workflow.
# ABOUTME: Prevents branch sprawl from becoming the default operating mode again.

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8") if (ROOT / "AGENTS.md").exists() else ""


class RepoWorkflowContractTest(unittest.TestCase):
    def test_agents_mentions_source_of_truth_branch_policy(self) -> None:
        required_phrases = [
            "source-of-truth branch",
            "`main`",
            "merge the task branch",
            "delete the previous task branch",
            "one active remote branch",
        ]
        missing = [phrase for phrase in required_phrases if phrase not in AGENTS]
        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
