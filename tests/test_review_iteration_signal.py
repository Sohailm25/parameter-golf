# ABOUTME: Verifies the iteration-intelligence wrapper builds the expected review sequence.
# ABOUTME: Prevents the repo from silently skipping public-signal hooks between experiments.

from pathlib import Path
import importlib.util
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "review_iteration_signal.py"


def load_module():
    spec = importlib.util.spec_from_file_location("review_iteration_signal", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load review_iteration_signal module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReviewIterationSignalTest(unittest.TestCase):
    def test_wrapper_builds_pr_x_and_arxiv_commands(self) -> None:
        module = load_module()
        commands = module.build_commands(
            lane="evaluation",
            phase="pre",
            topic="dynamic eval",
        )
        flattened = [" ".join(command) for command in commands]
        self.assertTrue(any("review_openai_prs.py" in command for command in flattened))
        self.assertTrue(any("review_x_signal.py" in command for command in flattened))
        self.assertTrue(any("review_arxiv.py" in command for command in flattened))


if __name__ == "__main__":
    unittest.main()
