# ABOUTME: Verifies the repo exposes a single first-step onboarding path for fresh agents.
# ABOUTME: Prevents startup knowledge from living only in scattered docs and old session logs.

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
START_HERE = (ROOT / "START_HERE.md").read_text(encoding="utf-8") if (ROOT / "START_HERE.md").exists() else ""


class OnboardingContractTest(unittest.TestCase):
    def test_start_here_contains_required_bootstrap_steps(self) -> None:
        required_phrases = [
            "CURRENT_STATE.md",
            "bd ready",
            "scripts/review_iteration_signal.py",
            "scripts/experiment_runner.py launch",
            "scripts/experiment_runner.py promote",
            "scripts/render_progress_dashboard.py",
        ]
        missing = [phrase for phrase in required_phrases if phrase not in START_HERE]
        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
