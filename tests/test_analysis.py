from __future__ import annotations

import unittest

from path_dependence.analysis import case_instability, condition_summaries, planned_contrasts
from path_dependence.diagnostics import duplicate_diagnostics
from path_dependence.scoring import code_run
from test_scoring_and_diagnostics import initial_fixture, revision_fixture


class AnalysisTests(unittest.TestCase):
    def test_all_planned_contrasts_and_deduplicated_instability(self) -> None:
        conditions = ["neutral", "negative_first", "positive_first", "commit_a", "commit_b"]
        coded = []
        parsed = {}
        for condition in conditions:
            for replicate in (1, 2):
                run = {
                    "run_id": f"C1_{condition}_r{replicate:02d}",
                    "case_id": "C1",
                    "condition": condition,
                    "replicate": replicate,
                    "temperature": 0,
                }
                initial = initial_fixture()
                revision = revision_fixture()
                coded.append(code_run(run, initial, revision))
                parsed[run["run_id"]] = (initial, revision)

        diagnostics = duplicate_diagnostics(coded, parsed)
        summaries = condition_summaries(coded, diagnostics)
        contrasts = planned_contrasts(summaries)
        instability = case_instability(coded)
        self.assertEqual(len(summaries), 5)
        self.assertEqual(len(contrasts), 6)
        self.assertEqual(instability[0]["unique_initial_behavior_patterns_across_cells"], 5)
        self.assertTrue(all(item["full_effectively_deterministic"] for item in diagnostics))
        self.assertTrue(all(item["inferential_independence_warning"] for item in contrasts))


if __name__ == "__main__":
    unittest.main()
