# ABOUTME: Verifies that iteration tracking is a first-class part of the scaffold.
# ABOUTME: Ensures full script snapshots and leaderboard registration stay part of the repo contract.

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
LEADERBOARD = (
    (ROOT / "leaderboard.md").read_text(encoding="utf-8")
    if (ROOT / "leaderboard.md").exists()
    else ""
)
ITERATIONS_README = (
    (ROOT / "iterations" / "README.md").read_text(encoding="utf-8")
    if (ROOT / "iterations" / "README.md").exists()
    else ""
)


class IterationArchiveContractTest(unittest.TestCase):
    def test_leaderboard_declares_snapshot_contract(self) -> None:
        required_phrases = [
            "iterations/archive",
            "iterations/golden",
            "full file snapshot",
            "atomic change",
            "Parent",
            "Iteration ID",
        ]
        missing = [phrase for phrase in required_phrases if phrase not in LEADERBOARD]
        self.assertEqual([], missing)

    def test_iterations_readme_declares_workflow(self) -> None:
        required_phrases = [
            "leaderboard.md",
            "golden set",
            "atomic change",
            "full file snapshot",
        ]
        missing = [
            phrase for phrase in required_phrases if phrase not in ITERATIONS_README
        ]
        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
