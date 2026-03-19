# ABOUTME: Verifies append-only telemetry registration for runs, metrics, and ID links.
# ABOUTME: Prevents the repo's experiment history from degrading into overwritten ad hoc notes.

from pathlib import Path
import importlib.util
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "register_run.py"


def load_module():
    spec = importlib.util.spec_from_file_location("register_run", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load register_run module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RegisterRunTest(unittest.TestCase):
    def test_build_run_id_contains_lane_and_label(self) -> None:
        module = load_module()
        run_id = module.build_run_id("evaluation", "doc isolated eval")
        self.assertIn("evaluation", run_id)
        self.assertIn("doc-isolated-eval", run_id)

    def test_append_jsonl_record_rejects_duplicate_unique_key(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "runs.jsonl"
            module.append_jsonl_record(path, {"run_id": "run-1"}, unique_key="run_id")
            with self.assertRaises(SystemExit):
                module.append_jsonl_record(path, {"run_id": "run-1"}, unique_key="run_id")

    def test_build_link_record_preserves_id_mapping(self) -> None:
        module = load_module()
        record = module.build_link_record(
            source_type="run",
            source_id="run-1",
            relation="promoted_to",
            target_type="iteration",
            target_id="iter-1",
            note="best proxy result",
            created_at="2026-03-19T00:00:00Z",
        )
        self.assertEqual("run-1", record["source_id"])
        self.assertEqual("iter-1", record["target_id"])
        self.assertEqual("promoted_to", record["relation"])


if __name__ == "__main__":
    unittest.main()
