# ABOUTME: Verifies flat-stream sliding-window planning before MLX evaluation code consumes it.
# ABOUTME: Prevents the first evaluation-accounting experiment from silently double-counting or skipping targets.

from dataclasses import astuple
from pathlib import Path
import importlib.util
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "validation" / "eval_windowing.py"


def load_module():
    spec = importlib.util.spec_from_file_location("eval_windowing", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load eval_windowing module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EvalWindowingTest(unittest.TestCase):
    def test_stride_equal_seq_len_matches_non_overlapping_windows(self) -> None:
        module = load_module()
        windows = module.build_flat_stream_windows(total_targets=8, seq_len=4, stride=4)
        self.assertEqual(
            [(0, 4, 0), (4, 8, 4)],
            [astuple(window) for window in windows],
        )

    def test_sliding_windows_cover_each_target_exactly_once(self) -> None:
        module = load_module()
        windows = module.build_flat_stream_windows(total_targets=9, seq_len=4, stride=2)
        self.assertEqual(
            [(0, 4, 0), (2, 6, 4), (4, 8, 6), (5, 9, 8)],
            [astuple(window) for window in windows],
        )
        covered = []
        for window in windows:
            covered.extend(range(window.score_start, window.end))
        self.assertEqual(list(range(9)), covered)

    def test_invalid_stride_larger_than_seq_len_raises(self) -> None:
        module = load_module()
        with self.assertRaises(ValueError):
            module.build_flat_stream_windows(total_targets=16, seq_len=4, stride=5)

    def test_local_score_starts_match_suffixes_to_count(self) -> None:
        module = load_module()
        windows = module.build_flat_stream_windows(total_targets=9, seq_len=4, stride=2)
        self.assertEqual([0, 2, 2, 3], module.local_score_starts(windows))

    def test_suffix_mask_scores_only_new_targets(self) -> None:
        module = load_module()
        mask = module.build_suffix_mask([0, 2, 2, 3], window_len=4)
        self.assertEqual(
            [
                [True, True, True, True],
                [False, False, True, True],
                [False, False, True, True],
                [False, False, False, True],
            ],
            mask.tolist(),
        )


if __name__ == "__main__":
    unittest.main()
