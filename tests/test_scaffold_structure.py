# ABOUTME: Verifies that the Parameter Golf workspace keeps its research scaffold intact.
# ABOUTME: Prevents future edits from silently weakening the repo structure Sohail asked to standardize.

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DIRECTORIES = {
    "background-work",
    "background-work/papers",
    "background-work/papers/files",
    "configs",
    "history",
    "iterations",
    "iterations/archive",
    "iterations/golden",
    "iterations/templates",
    "journal",
    "journal/logs",
    "knowledge",
    "knowledge/general",
    "knowledge/general/accomplishments",
    "knowledge/general/insights",
    "knowledge/general/learnings",
    "knowledge/general/references",
    "notebooks",
    "prompts",
    "research",
    "researchdocs",
    "results",
    "results/infrastructure",
    "results/baselines",
    "results/optimizer_sweeps",
    "results/architecture",
    "results/quantization",
    "results/compression",
    "results/tokenizer",
    "results/evaluation",
    "results/autoresearch",
    "results/golden",
    "results/figures",
    "research/pr_snapshots",
    "scratch",
    "scripts",
    "sessions",
    "tests",
    "validation",
}

REQUIRED_FILES = {
    ".gitattributes",
    ".gitignore",
    ".pre-commit-config.yaml",
    "AGENTS.md",
    "CURRENT_STATE.md",
    "DECISIONS.md",
    "README.md",
    "SCRATCHPAD.md",
    "THOUGHT_LOG.md",
    "leaderboard.md",
    "requirements.txt",
    "requirements.lock.txt",
    "background-work/COMPETITION_POLICY.md",
    "background-work/GAPS_SYNTHESIS.md",
    "background-work/IMPLEMENTATION_GROUNDING.md",
    "background-work/PROPOSAL_REVIEW.md",
    "background-work/REFERENCES.md",
    "background-work/RESEARCH_POSITIONING.md",
    "background-work/papers/DOWNLOAD_MANIFEST.md",
    "configs/experiment.yaml",
    "history/20260319-initial-strategy-synthesis.md",
    "history/20260319-parameter-golf-scaffold-adaptation.md",
    "history/PREREG.md",
    "iterations/README.md",
    "iterations/archive/.gitkeep",
    "iterations/golden/.gitkeep",
    "iterations/templates/.gitkeep",
    "journal/current_state.md",
    "knowledge/general/accomplishments/.gitkeep",
    "knowledge/general/insights/.gitkeep",
    "knowledge/general/learnings/.gitkeep",
    "knowledge/general/references/.gitkeep",
    "notebooks/.gitkeep",
    "prompts/README.md",
    "prompts/autoresearch_program_template.md",
    "research/approach-space-20260319.md",
    "research/atomic_experiment_backlog.md",
    "research/autoresearch-fit-20260319.md",
    "research/challenge-review-20260319.md",
    "research/pr_review_log.md",
    "research/pr_review_state.json",
    "researchdocs/dynamiceval.md",
    "researchdocs/parameter_golf_strategy.md",
    "results/RESULTS_INDEX.md",
    "results/architecture/.gitkeep",
    "results/autoresearch/.gitkeep",
    "results/baselines/.gitkeep",
    "results/compression/.gitkeep",
    "results/evaluation/.gitkeep",
    "results/figures/.gitkeep",
    "results/golden/.gitkeep",
    "results/infrastructure/.gitkeep",
    "results/optimizer_sweeps/.gitkeep",
    "results/quantization/.gitkeep",
    "results/tokenizer/.gitkeep",
    "scratch/.gitkeep",
    "scripts/download_reference_papers.py",
    "scripts/register_iteration.py",
    "scripts/review_openai_prs.py",
    "sessions/SESSION_TEMPLATE.md",
    "validation/README.md",
    "validation/__init__.py",
}


class ScaffoldStructureTest(unittest.TestCase):
    def test_required_directories_exist(self) -> None:
        missing = sorted(
            str(path) for path in REQUIRED_DIRECTORIES if not (ROOT / path).is_dir()
        )
        self.assertEqual([], missing)

    def test_required_files_exist(self) -> None:
        missing = sorted(
            str(path) for path in REQUIRED_FILES if not (ROOT / path).is_file()
        )
        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
