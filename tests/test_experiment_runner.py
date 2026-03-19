# ABOUTME: Verifies the experiment runner can build launch and promotion plans around the repo workflow.
# ABOUTME: Prevents the experiment loop from staying manual and inconsistent across sessions.

from pathlib import Path
import importlib.util
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "experiment_runner.py"


def load_module():
    spec = importlib.util.spec_from_file_location("experiment_runner", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load experiment_runner module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExperimentRunnerTest(unittest.TestCase):
    def test_build_launch_plan_sets_run_id_and_log_path_for_torch(self) -> None:
        module = load_module()
        plan = module.build_launch_plan(
            lane="baselines",
            label="naive baseline smoke",
            issue_id="parametergolf-7cm",
            topic="baseline reproduction",
            script_path="train_gpt.py",
            script_args=[],
            env_pairs=["ITERATIONS=10"],
            branch="main",
            commit="abc1234",
            device="local-m4",
            horizon="smoke",
            phase="pre",
        )
        self.assertIn("baselines", plan["run_id"])
        self.assertEqual("logs/" + plan["run_id"] + ".txt", plan["log_path"])
        self.assertEqual("10", plan["env"]["ITERATIONS"])
        self.assertEqual(plan["run_id"], plan["env"]["RUN_ID"])

    def test_build_launch_plan_sets_log_path_for_mlx(self) -> None:
        module = load_module()
        plan = module.build_launch_plan(
            lane="baselines",
            label="mlx baseline smoke",
            issue_id="parametergolf-7cm",
            topic="baseline reproduction",
            script_path="train_gpt_mlx.py",
            script_args=[],
            env_pairs=[],
            branch="main",
            commit="abc1234",
            device="local-m4",
            horizon="smoke",
            phase="pre",
        )
        self.assertTrue(plan["log_path"].endswith(f"{plan['run_id']}.txt"))
        self.assertIn("logs", plan["log_path"])

    def test_build_promotion_link_records_run_to_iteration(self) -> None:
        module = load_module()
        records = module.build_promotion_link_records(
            run_id="run-1",
            iteration_id="iter-1",
            result_path="results/baselines/example.md",
            created_at="2026-03-19T00:00:00Z",
        )
        relations = [record["relation"] for record in records]
        self.assertIn("promoted_to", relations)
        self.assertIn("documented_in", relations)

    def test_build_log_link_record_targets_run_log(self) -> None:
        module = load_module()
        record = module.build_log_link_record(
            run_id="run-1",
            log_path="logs/run-1.txt",
            created_at="2026-03-19T00:00:00Z",
        )
        self.assertEqual("logged_to", record["relation"])
        self.assertEqual("run_log", record["target_type"])
        self.assertEqual("logs/run-1.txt", record["target_id"])

    def test_build_run_outcome_metric_rows_capture_process_metadata(self) -> None:
        module = load_module()
        rows = module.build_run_outcome_metric_rows(
            returncode=0,
            ingested_metric_rows=7,
            log_bytes=128,
        )
        rows_by_name = {row["metric_name"]: row for row in rows}
        self.assertEqual(0.0, rows_by_name["process_returncode"]["metric_value"])
        self.assertEqual(7.0, rows_by_name["ingested_metric_rows"]["metric_value"])
        self.assertEqual(128.0, rows_by_name["log_bytes"]["metric_value"])

    def test_append_results_index_note_appends_under_matching_lane_section(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            results_index = Path(tmp_dir) / "RESULTS_INDEX.md"
            results_index.write_text(
                "\n".join(
                    [
                        "# Results Index",
                        "",
                        "## Infrastructure",
                        "",
                        "| Artifact | Lane | Status | Path |",
                        "|---|---|---|---|",
                        "| Existing infra artifact | infrastructure | pass | `results/infrastructure/existing.md` |",
                        "",
                        "## Baselines",
                        "",
                        "| Artifact | Lane | Status | Path |",
                        "|---|---|---|---|",
                        "",
                        "## Evaluation",
                        "",
                        "| Artifact | Lane | Status | Path |",
                        "|---|---|---|---|",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            module.append_results_index_note(
                results_index_path=results_index,
                result_path="results/baselines/example.md",
                lane="baselines",
                status="pass",
                summary="Baseline smoke artifact",
            )
            text = results_index.read_text(encoding="utf-8")
            self.assertIn(
                "| Baseline smoke artifact | baselines | pass | `results/baselines/example.md` |",
                text,
            )
            baselines_section = text.split("## Baselines", maxsplit=1)[1].split(
                "## Evaluation",
                maxsplit=1,
            )[0]
            self.assertIn("results/baselines/example.md", baselines_section)
            infrastructure_section = text.split(
                "## Infrastructure",
                maxsplit=1,
            )[1].split("## Baselines", maxsplit=1)[0]
            self.assertNotIn("results/baselines/example.md", infrastructure_section)

    def test_append_scratchpad_entry_writes_section(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            scratchpad = Path(tmp_dir) / "SCRATCHPAD.md"
            scratchpad.write_text("# Scratchpad\n", encoding="utf-8")
            module.append_scratchpad_entry(
                scratchpad_path=scratchpad,
                heading="PRE-RUN: baseline",
                lines=["- Command: `.venv/bin/python train_gpt.py`"],
            )
            text = scratchpad.read_text(encoding="utf-8")
            self.assertIn("PRE-RUN: baseline", text)
            self.assertIn("train_gpt.py", text)

    def test_cli_help_runs_from_repo_root(self) -> None:
        result = subprocess.run(
            [str(ROOT / ".venv" / "bin" / "python"), str(SCRIPT_PATH), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, msg=result.stderr)
        self.assertIn("launch", result.stdout)
        self.assertIn("promote", result.stdout)


if __name__ == "__main__":
    unittest.main()
