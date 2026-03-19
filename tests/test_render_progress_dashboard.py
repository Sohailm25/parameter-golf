# ABOUTME: Verifies dashboard rendering from telemetry records without depending on live experiment outputs.
# ABOUTME: Keeps progress visualization reproducible and append-only.

from pathlib import Path
import importlib.util
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "render_progress_dashboard.py"


def load_module():
    spec = importlib.util.spec_from_file_location("render_progress_dashboard", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load render_progress_dashboard module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RenderProgressDashboardTest(unittest.TestCase):
    def test_build_dashboard_html_contains_summary_sections(self) -> None:
        module = load_module()
        html = module.build_dashboard_html(
            runs=[
                {"run_id": "run-1", "lane": "evaluation", "horizon": "proxy", "label": "doc eval"}
            ],
            observations=[
                {
                    "run_id": "run-1",
                    "metric_name": "val_bpb",
                    "metric_value": 1.191,
                    "step": 500,
                    "recorded_at": "2026-03-19T00:00:00Z",
                }
            ],
            links=[],
            generated_at="2026-03-19T00:00:00Z",
        )
        self.assertIn("Telemetry Dashboard", html)
        self.assertIn("Best val_bpb Over Time", html)
        self.assertIn("Run Count By Lane", html)

    def test_render_dashboard_writes_unique_directory_and_manifest(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            manifest = root / "render_registry.jsonl"
            figures_root = root / "renders"
            render_path = module.render_dashboard(
                runs=[],
                observations=[],
                links=[],
                manifest_path=manifest,
                figures_root=figures_root,
                generated_at="2026-03-19T00:00:00Z",
            )
            self.assertTrue(render_path.is_file())
            self.assertTrue(manifest.is_file())


if __name__ == "__main__":
    unittest.main()
