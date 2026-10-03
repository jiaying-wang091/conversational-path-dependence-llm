from __future__ import annotations

import copy
import unittest

from path_dependence.analysis import (
    ambiguity_disagreement_summaries,
    condition_summaries,
    factorial_interaction_summary,
    monotonicity_results,
    neutral_manipulation_checks,
    planned_contrasts,
    polarity_pooled_sensitivity,
    variant_instability,
)
from path_dependence.diagnostics import duplicate_diagnostics
from path_dependence.protocol import CASES, CONDITIONS
from path_dependence.scoring import code_run
from test_scoring_and_diagnostics import initial_fixture, revision_fixture


def _replace_fact_prefix(value: object, variant_id: str) -> object:
    if isinstance(value, str):
        return value.replace("LA-F", f"{variant_id}-F")
    if isinstance(value, list):
        return [_replace_fact_prefix(item, variant_id) for item in value]
    if isinstance(value, dict):
        return {key: _replace_fact_prefix(item, variant_id) for key, item in value.items()}
    return value


class AnalysisTests(unittest.TestCase):
    def test_complete_phase1b_analysis_tables(self) -> None:
        coded: list[dict] = []
        parsed: dict[str, tuple[dict, dict]] = {}
        for variant_id, variant in CASES.items():
            for condition in CONDITIONS:
                for replicate in (1, 2):
                    run_id = f"{variant_id}_{condition}_r{replicate:02d}"
                    run = {
                        "run_id": run_id,
                        "case_id": variant_id,
                        "variant_id": variant_id,
                        "ambiguity_level": variant.ambiguity_level,
                        "baseline_polarity": variant.baseline_polarity,
                        "condition": condition,
                        "replicate": replicate,
                        "temperature": 0,
                    }
                    initial = _replace_fact_prefix(copy.deepcopy(initial_fixture()), variant_id)
                    revision = _replace_fact_prefix(copy.deepcopy(revision_fixture()), variant_id)
                    assert isinstance(initial, dict) and isinstance(revision, dict)
                    coded.append(code_run(run, initial, revision))
                    parsed[run_id] = (initial, revision)

        diagnostics = duplicate_diagnostics(coded, parsed)
        summaries = condition_summaries(coded, diagnostics)
        contrasts = planned_contrasts(summaries)
        sensitivity = polarity_pooled_sensitivity(contrasts)
        manipulation = neutral_manipulation_checks(summaries)
        monotonicity = monotonicity_results(sensitivity, manipulation)
        interaction = factorial_interaction_summary(summaries)
        instability = variant_instability(coded)
        disagreement = ambiguity_disagreement_summaries(instability)

        self.assertEqual(len(diagnostics), 30)
        self.assertEqual(len(summaries), 30)
        self.assertEqual(len(contrasts), 36)
        self.assertEqual(len(sensitivity), 3)
        self.assertEqual(len(manipulation), 3)
        self.assertEqual(len(monotonicity), 4)
        self.assertEqual(len(interaction), 12)
        self.assertEqual(len(instability), 6)
        self.assertEqual(len(disagreement), 3)
        self.assertTrue(all(row["commitment_sensitivity"] == 0 for row in sensitivity))
        self.assertTrue(all(row["classification"] == "flat" for row in monotonicity))
        self.assertTrue(all(row["full_effectively_deterministic"] for row in diagnostics))


if __name__ == "__main__":
    unittest.main()
