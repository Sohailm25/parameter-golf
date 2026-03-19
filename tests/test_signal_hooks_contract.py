# ABOUTME: Verifies that the repo keeps the X and arXiv research-hook workflow Sohail requested.
# ABOUTME: Prevents the iteration-intelligence contract from drifting back into one-off browsing.

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8") if (ROOT / "AGENTS.md").exists() else ""
QUERY_FILE = ROOT / "research" / "research-queries.md"


class SignalHooksContractTest(unittest.TestCase):
    def test_agents_mentions_x_and_arxiv_hooks(self) -> None:
        required_phrases = [
            "bird-cli",
            "scripts/review_x_signal.py",
            "scripts/review_arxiv.py",
            "scripts/review_iteration_signal.py",
            "research/research-queries.md",
        ]
        missing = [phrase for phrase in required_phrases if phrase not in AGENTS]
        self.assertEqual([], missing)

    def test_research_queries_template_has_pending_section(self) -> None:
        if not QUERY_FILE.exists():
            self.fail("missing research/research-queries.md")
        text = QUERY_FILE.read_text(encoding="utf-8")
        self.assertIn("# Research Queries", text)
        self.assertIn("## Pending", text)


if __name__ == "__main__":
    unittest.main()
