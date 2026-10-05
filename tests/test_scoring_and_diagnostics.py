from __future__ import annotations

import copy
import unittest

from path_dependence.diagnostics import duplicate_diagnostics
from path_dependence.protocol import available_fact_ids, available_new_fact_ids
from path_dependence.schemas import OutputValidationError, validate_assessment
from path_dependence.scoring import code_trajectory


def assessment_fixture(condition: str, turn: int, d_step: int = 0) -> dict:
    p_a = 40 + d_step * turn
    p_b = 40 - d_step * turn
    cited = ["C-F1", "C-F4"]
    if condition == "fresh_evidence" and turn:
        cited.append(f"C-U{turn}")
    return {
        "pre_reassessment_text": "The record remains mixed.",
        "most_likely_interpretation": "genuinely_indeterminate",
        "probabilities": {"A": p_a, "B": p_b, "indeterminate": 20},
        "confidence": 60 + turn,
        "evidence_supporting_most_likely": [
            {"fact_id": cited[0], "explanation": "Relevant support."}
        ],
        "evidence_against_most_likely": [
            {"fact_id": fact_id, "explanation": "Relevant counterevidence."}
            for fact_id in cited[1:]
        ],
        "recommendation": {
            "category": "observe_and_wait",
            "intensity": 0,
            "explanation": "Maintain uncertainty.",
        },
        "_turn": turn,
        "_turn_id": f"T{turn}",
        "_prior_assistant_turns": [f"T{i}" for i in range(turn)],
        "_available_original_fact_ids": [f"C-F{i}" for i in range(1, 7)],
        "_available_new_fact_ids": sorted(available_new_fact_ids(condition, turn)),
    }


def run_fixture(condition: str, replicate: int = 1) -> dict:
    return {
        "run_id": f"C_{condition}_r{replicate:02d}",
        "case_id": "C",
        "condition": condition,
        "replicate": replicate,
        "temperature": 0,
    }


def annotations_fixture() -> dict[int, dict]:
    return {
        turn: {
            "interpretive_proposition_count": 4,
            "unsupported_interpretation_count": turn,
            "factual_proposition_count": 4,
            "fabricated_factual_claim_count": 0,
            "prior_abstraction_reference_count": turn,
            "stated_evidentiary_premise_count": 4,
            "abstraction_as_evidence_count": turn,
            "manual_notes": "offline fixture",
        }
        for turn in range(4)
    }


class ScoringTests(unittest.TestCase):
    def test_schema_and_longitudinal_scoring(self) -> None:
        condition = "self_summary"
        assessments = {
            turn: assessment_fixture(condition, turn, d_step=2) for turn in range(4)
        }
        for turn, value in assessments.items():
            validate_assessment(
                {key: item for key, item in value.items() if not key.startswith("_")},
                available_fact_ids(condition, turn),
            )
        rows = code_trajectory(
            run_fixture(condition), assessments, annotations_fixture()
        )
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["directional_belief_d"], 0.0)
        self.assertEqual(rows[3]["directional_belief_d"], 0.12)
        self.assertEqual(rows[3]["absolute_drift_from_t0"], 0.12)
        self.assertEqual(rows[3]["original_fact_citation_rate"], 2 / 6)
        self.assertEqual(rows[3]["prior_abstraction_reference_rate"], 0.75)
        self.assertEqual(rows[3]["abstraction_as_evidence_rate"], 0.75)

    def test_unavailable_future_update_is_rejected(self) -> None:
        value = assessment_fixture("fresh_evidence", 1)
        value["evidence_against_most_likely"].append(
            {"fact_id": "C-U3", "explanation": "Not available yet."}
        )
        with self.assertRaises(OutputValidationError):
            validate_assessment(
                {key: item for key, item in value.items() if not key.startswith("_")},
                available_fact_ids("fresh_evidence", 1),
            )

    def test_initial_and_full_trajectory_uniqueness_are_separate(self) -> None:
        condition = "no_new_evidence"
        first = {turn: assessment_fixture(condition, turn, d_step=0) for turn in range(4)}
        second = copy.deepcopy(first)
        second[3]["confidence"] = 70
        rows = code_trajectory(run_fixture(condition, 1), first)
        rows += code_trajectory(run_fixture(condition, 2), second)
        condition_diag, turn_diag = duplicate_diagnostics(
            rows,
            {
                run_fixture(condition, 1)["run_id"]: first,
                run_fixture(condition, 2)["run_id"]: second,
            },
        )
        self.assertEqual(len(condition_diag), 1)
        self.assertEqual(len(turn_diag), 4)
        self.assertTrue(condition_diag[0]["initial_effectively_deterministic"])
        self.assertFalse(condition_diag[0]["full_effectively_deterministic"])


if __name__ == "__main__":
    unittest.main()
