# ABOUTME: Verifies parsing and query-draining behavior for the arXiv review hook.
# ABOUTME: Keeps the research-query queue reliable without depending on live arXiv responses in unit tests.

from pathlib import Path
import importlib.util
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "review_arxiv.py"


def load_module():
    spec = importlib.util.spec_from_file_location("review_arxiv", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load review_arxiv module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReviewArxivTest(unittest.TestCase):
    def test_parse_atom_feed_extracts_entries(self) -> None:
        module = load_module()
        xml_text = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/1234.5678v1</id>
    <updated>2026-03-19T00:00:00Z</updated>
    <published>2026-03-18T00:00:00Z</published>
    <title>Dynamic Evaluation for Small Language Models</title>
    <summary>Applies test-time training to transformers.</summary>
    <author><name>Jane Doe</name></author>
    <link href="http://arxiv.org/abs/1234.5678v1" rel="alternate" type="text/html" />
    <category term="cs.LG" />
  </entry>
</feed>
"""
        entries = module.parse_atom_feed(xml_text)
        self.assertEqual("1234.5678v1", entries[0]["arxiv_id"])
        self.assertIn("Dynamic Evaluation", entries[0]["title"])

    def test_pending_queries_are_loaded_and_cleared(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            query_path = Path(tmp_dir) / "research-queries.md"
            query_path.write_text(
                "# Research Queries\n\n## Pending\n- dynamic evaluation transformer\n- small-model quantization\n",
                encoding="utf-8",
            )
            pending = module.load_pending_queries(query_path)
            self.assertEqual(
                ["dynamic evaluation transformer", "small-model quantization"],
                pending,
            )
            module.clear_pending_queries(query_path)
            cleared = query_path.read_text(encoding="utf-8")
            self.assertIn("## Pending", cleared)
            self.assertNotIn("dynamic evaluation transformer", cleared)

    def test_evaluation_lane_queries_include_dynamic_eval(self) -> None:
        module = load_module()
        queries = module.default_queries_for_lane("evaluation", topic="")
        self.assertTrue(any("dynamic evaluation" in query.lower() for query in queries))
        self.assertTrue(any("test-time training" in query.lower() for query in queries))

    def test_non_ml_categories_are_filtered_from_selected_papers(self) -> None:
        module = load_module()
        papers = [
            {
                "arxiv_id": "1",
                "title": "Decay properties of a hexaquark multiplet",
                "summary": "Not about machine learning.",
                "updated": "2026-03-19T00:00:00Z",
                "published": "2026-03-18T00:00:00Z",
                "authors": ["A"],
                "url": "https://arxiv.org/abs/1",
                "categories": ["hep-ph"],
            },
            {
                "arxiv_id": "2",
                "title": "Dynamic Evaluation for Small Language Models",
                "summary": "About online adaptation for transformers.",
                "updated": "2026-03-19T00:00:00Z",
                "published": "2026-03-18T00:00:00Z",
                "authors": ["B"],
                "url": "https://arxiv.org/abs/2",
                "categories": ["cs.LG"],
            },
        ]
        selected = module.select_top_papers(
            papers,
            lane="evaluation",
            topic="dynamic evaluation",
            max_papers=5,
        )
        self.assertEqual(["2"], [paper["arxiv_id"] for paper in selected])

    def test_carry_forward_keeps_only_ml_relevant_prior_papers(self) -> None:
        module = load_module()
        previous_state = {
            "papers": {
                "1": {
                    "arxiv_id": "1",
                    "categories": ["hep-ph"],
                },
                "2": {
                    "arxiv_id": "2",
                    "categories": ["cs.LG"],
                },
                "3": {
                    "arxiv_id": "3",
                    "categories": ["cs.DM"],
                },
            }
        }
        carried = module.carry_forward_relevant_papers(previous_state, selected_ids=set())
        self.assertEqual(["2"], sorted(carried.keys()))

    def test_build_local_paper_paths_include_pdf_and_text_targets(self) -> None:
        module = load_module()
        pdf_path, text_path = module.build_local_paper_paths("1904.08378v1")
        self.assertTrue(str(pdf_path).endswith("1904.08378v1.pdf"))
        self.assertTrue(str(text_path).endswith("1904.08378v1.txt"))


if __name__ == "__main__":
    unittest.main()
