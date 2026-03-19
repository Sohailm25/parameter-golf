# ABOUTME: Verifies the dedupe and re-review behavior for the official PR review script.
# ABOUTME: Keeps the repo's PR intelligence loop deterministic and resistant to duplicate backlog spam.

from pathlib import Path
import importlib.util
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "review_openai_prs.py"


def load_module():
    spec = importlib.util.spec_from_file_location("review_openai_prs", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load review_openai_prs module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReviewOpenAiPrsTest(unittest.TestCase):
    def test_same_pr_does_not_duplicate_candidate_experiments(self) -> None:
        module = load_module()
        state = module.build_empty_state()
        pr = {
            "number": 77,
            "title": "[record bpb=1.195] sliding window + LoRA TTT",
            "html_url": "https://github.com/openai/parameter-golf/pull/77",
            "updated_at": "2026-03-19T11:58:26Z",
            "body": "doc isolated eval and sliding window with LoRA TTT",
            "user": {"login": "samacqua"},
            "head": {"sha": "abc123"},
        }
        state = module.merge_pull_request_into_state(state, pr, scan_time="2026-03-19T12:00:00Z")
        state = module.merge_pull_request_into_state(state, pr, scan_time="2026-03-19T12:01:00Z")

        experiment = state["candidate_experiments"]["eval-document-isolated-sliding-window"]
        self.assertEqual([77], experiment["source_prs"])

    def test_lora_ttt_pr_populates_distinct_ttt_lane(self) -> None:
        module = load_module()
        state = module.build_empty_state()
        pr = {
            "number": 77,
            "title": "[record bpb=1.195] sliding window + LoRA TTT",
            "html_url": "https://github.com/openai/parameter-golf/pull/77",
            "updated_at": "2026-03-19T11:58:26Z",
            "body": (
                "document masking, sliding window, then per-document LoRA test-time training "
                "with reset between documents"
            ),
            "user": {"login": "samacqua"},
            "head": {"sha": "abc123"},
        }

        state = module.merge_pull_request_into_state(state, pr, scan_time="2026-03-19T12:00:00Z")

        self.assertIn("eval-document-isolated-sliding-window", state["candidate_experiments"])
        self.assertIn("eval-document-reset-ttt", state["candidate_experiments"])
        self.assertEqual(
            [77],
            state["candidate_experiments"]["eval-document-reset-ttt"]["source_prs"],
        )

    def test_changed_head_sha_marks_pr_for_rereview(self) -> None:
        module = load_module()
        state = module.build_empty_state()
        original = {
            "number": 65,
            "title": "Record: Mixed Quant (int6+int8) + Sliding Window, val_bpb=1.1630",
            "html_url": "https://github.com/openai/parameter-golf/pull/65",
            "updated_at": "2026-03-19T11:10:43Z",
            "body": "mixed precision int6 int8 selective quantization and stride 64 sliding window",
            "user": {"login": "aquariouseworkman"},
            "head": {"sha": "oldsha"},
        }
        updated = dict(original)
        updated["head"] = {"sha": "newsha"}
        updated["updated_at"] = "2026-03-19T13:10:43Z"

        state = module.merge_pull_request_into_state(state, original, scan_time="2026-03-19T12:00:00Z")
        state["pull_requests"]["65"]["status"] = "reviewed"
        state = module.merge_pull_request_into_state(state, updated, scan_time="2026-03-19T13:11:00Z")

        self.assertEqual("recheck_needed", state["pull_requests"]["65"]["status"])

    def test_multiple_prs_feed_one_backlog_entry(self) -> None:
        module = load_module()
        state = module.build_empty_state()
        prs = [
            {
                "number": 53,
                "title": "1.1888 BPB via SP-4096 compression + stride-64 sliding window",
                "html_url": "https://github.com/openai/parameter-golf/pull/53",
                "updated_at": "2026-03-19T07:00:00Z",
                "body": "SP-4096 tokenizer and stride-64 sliding window",
                "user": {"login": "a"},
                "head": {"sha": "sha53"},
            },
            {
                "number": 78,
                "title": "Record: 8192 Vocab Size, NorMuon, Selective Quantization; 1.186 val_bpb",
                "html_url": "https://github.com/openai/parameter-golf/pull/78",
                "updated_at": "2026-03-19T12:14:57Z",
                "body": "vocab size 8192 tokenizer selective quantization",
                "user": {"login": "b"},
                "head": {"sha": "sha78"},
            },
        ]
        for pr in prs:
            state = module.merge_pull_request_into_state(state, pr, scan_time="2026-03-19T14:00:00Z")

        experiment = state["candidate_experiments"]["tok-vocab-scaling"]
        self.assertEqual([53, 78], experiment["source_prs"])

    def test_rule_metadata_refreshes_when_definition_changes(self) -> None:
        module = load_module()
        state = module.build_empty_state()
        state["candidate_experiments"]["eval-document-isolated-sliding-window"] = {
            "title": "Old title",
            "lane": "evaluation",
            "status": "candidate",
            "atomic_change": "Old atomic change",
            "why_it_matters": "Old why",
            "source_prs": [77],
            "bd_issue_id": "",
        }

        pr = {
            "number": 77,
            "title": "[record bpb=1.195] sliding window + LoRA TTT",
            "html_url": "https://github.com/openai/parameter-golf/pull/77",
            "updated_at": "2026-03-19T11:58:26Z",
            "body": "document masking and sliding window",
            "user": {"login": "samacqua"},
            "head": {"sha": "abc123"},
        }

        state = module.merge_pull_request_into_state(state, pr, scan_time="2026-03-19T12:00:00Z")

        experiment = state["candidate_experiments"]["eval-document-isolated-sliding-window"]
        self.assertEqual("Document-isolated sliding-window accounting", experiment["title"])
        self.assertIn("before adding any evaluation-time adaptation", experiment["atomic_change"])
        self.assertIn("ablation suggests much of the gain", experiment["why_it_matters"])


if __name__ == "__main__":
    unittest.main()
