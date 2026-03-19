# ABOUTME: Verifies minimal validation helpers for log parsing and artifact-size accounting.
# ABOUTME: Prevents the repo from claiming confirmatory discipline while keeping validation as placeholders.

from pathlib import Path
import importlib.util
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
LOG_AUDIT_PATH = ROOT / "validation" / "log_audit.py"
ARTIFACT_SIZE_PATH = ROOT / "validation" / "artifact_size.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {name} module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidationHelpersTest(unittest.TestCase):
    def test_log_audit_extracts_final_exact_metrics(self) -> None:
        module = load_module(LOG_AUDIT_PATH, "log_audit")
        log_text = "\n".join(
            [
                "step:500/1000 val_loss:2.1000 val_bpb:1.2500 train_time:1000ms step_avg:2.00ms",
                "final_int8_zlib_roundtrip_exact val_loss:2.01234567 val_bpb:1.19876543",
            ]
        )
        summary = module.summarize_log_text(log_text)
        self.assertEqual(1.19876543, summary["final_exact"]["val_bpb"])
        self.assertEqual(500, summary["best_step_val_bpb"]["step"])

    def test_artifact_size_sums_file_bytes(self) -> None:
        module = load_module(ARTIFACT_SIZE_PATH, "artifact_size")
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            first = root / "a.bin"
            second = root / "b.bin"
            first.write_bytes(b"1234")
            second.write_bytes(b"123456")
            total = module.total_bytes([first, second])
            self.assertEqual(10, total)
            audit = module.build_artifact_audit([first, second], byte_cap=16)
            self.assertEqual(10, audit["total_bytes"])
            self.assertTrue(audit["within_cap"])


if __name__ == "__main__":
    unittest.main()
