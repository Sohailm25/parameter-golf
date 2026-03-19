# ABOUTME: Verifies parsing, scoring, and dedupe behavior for the bird-cli X signal review hook.
# ABOUTME: Keeps the external-signal workflow stable without requiring live X access in unit tests.

from pathlib import Path
import importlib.util
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "review_x_signal.py"


def load_module():
    spec = importlib.util.spec_from_file_location("review_x_signal", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load review_x_signal module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReviewXSignalTest(unittest.TestCase):
    def test_parse_bird_output_handles_warnings_before_json(self) -> None:
        module = load_module()
        raw = """
⚠️ No Twitter cookies found in Safari.
⚠️ No Twitter cookies found in Chrome.
[
  {
    "id": "1",
    "text": "parameter-golf sliding window val_bpb 1.1910",
    "createdAt": "Thu Mar 19 13:25:24 +0000 2026",
    "replyCount": 0,
    "retweetCount": 0,
    "likeCount": 2,
    "conversationId": "1",
    "author": {"username": "user", "name": "User"}
  }
]
"""
        tweets = module.parse_bird_output(raw)
        self.assertEqual("1", tweets[0]["id"])

    def test_signal_score_prefers_concrete_metric_tweet_over_promo(self) -> None:
        module = load_module()
        high_signal = {
            "id": "2",
            "text": (
                "parameter-golf reversal by step 500; relu^2 beats silu^2 at BPB@500 "
                "after AttnRes and SwiGLU tests"
            ),
            "replyCount": 0,
            "retweetCount": 0,
            "likeCount": 2,
            "author": {"username": "vuk", "name": "Vuk"},
        }
        promo = {
            "id": "3",
            "text": "LIVE deep dive free trial $49/mo learn AI research parameter-golf course",
            "replyCount": 0,
            "retweetCount": 0,
            "likeCount": 1,
            "author": {"username": "promo", "name": "Promo"},
        }
        self.assertGreater(
            module.score_tweet_signal(high_signal),
            module.score_tweet_signal(promo),
        )

    def test_same_tweet_dedupes_and_accumulates_queries(self) -> None:
        module = load_module()
        state = module.build_empty_state()
        tweet = {
            "id": "4",
            "text": "parameter-golf seq4096 sliding window val_bpb",
            "createdAt": "Thu Mar 19 13:25:24 +0000 2026",
            "replyCount": 0,
            "retweetCount": 0,
            "likeCount": 0,
            "author": {"username": "user", "name": "User"},
        }
        state = module.merge_tweet_into_state(
            state,
            tweet,
            query="parameter-golf",
            scan_time="2026-03-19T18:00:00Z",
        )
        state = module.merge_tweet_into_state(
            state,
            tweet,
            query="sliding window",
            scan_time="2026-03-19T18:01:00Z",
        )
        entry = state["tweets"]["4"]
        self.assertEqual(["parameter-golf", "sliding window"], entry["source_queries"])


if __name__ == "__main__":
    unittest.main()
