# ABOUTME: Verifies that the repo scaffold includes the persistent PR review workflow Sohail requested.
# ABOUTME: Prevents the official-PR intelligence loop from drifting back into ad hoc browsing.

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8") if (ROOT / "AGENTS.md").exists() else ""
STATE_PATH = ROOT / "research" / "pr_review_state.json"


class PrReviewContractTest(unittest.TestCase):
    def test_agents_mentions_pr_review_workflow(self) -> None:
        required_phrases = [
            "research/pr_review_state.json",
            "research/atomic_experiment_backlog.md",
            "scripts/review_openai_prs.py",
            "subagent",
            "no new PRs",
        ]
        missing = [phrase for phrase in required_phrases if phrase not in AGENTS]
        self.assertEqual([], missing)

    def test_state_file_has_required_top_level_keys(self) -> None:
        if not STATE_PATH.exists():
            self.fail("missing state file")
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        for key in [
            "repo",
            "last_full_scan_at",
            "last_reviewed_updated_at",
            "seen_pr_numbers",
            "seen_commit_shas",
            "pull_requests",
            "candidate_experiments",
        ]:
            self.assertIn(key, state)


if __name__ == "__main__":
    unittest.main()
