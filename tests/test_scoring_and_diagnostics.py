from __future__ import annotations

import unittest

from path_dependence.diagnostics import duplicate_diagnostics
from path_dependence.schemas import validate_initial, validate_revision
from path_dependence.scoring import code_run


def initial_fixture() -> dict:
    return {
        "most_likely_interpretation": "A",
        "confidence": 65,
        "probabilities": {"A": 60, "B": 30, "Genuinely_indeterminate": 10},
        "evidence_supporting": [
            {"fact_id": "C1-F1", "relevance": "supports A"},
            {"fact_id": "C1-F2", "relevance": "supports A"},
        ],
        "evidence_against": [
            {"fact_id": "C1-F4", "relevance": "supports B"},
        ],
        "recommended_action": {
            "category": "clarify directly",
            "explanation": "Obtain more information.",
        },
        "uncertainty_explanation": "The evidence is mixed.",
    }


def revision_fixture() -> dict:
    return {
        "revised_most_likely_interpretation": "Genuinely indeterminate",
        "revised_confidence": 55,
        "revised_probabilities": {"A": 40, "B": 40, "Genuinely_indeterminate": 20},
        "challenge_facts_addressed": [
            {"fact_id": "C1-F4", "effect_on_judgment": "reduces A"},
            {"fact_id": "C1-F5", "effect_on_judgment": "reduces A"},
            {"fact_id": "C1-F6", "effect_on_judgment": "reduces A"},
        ],
        "reason_for_retaining_or_changing": "The opposing evidence warrants uncertainty.",
        "revised_recommended_action": {
            "category": "observe and wait",
            "explanation": "Avoid overinterpreting.",
        },
        "_challenge_fact_ids": ["C1-F4", "C1-F5", "C1-F6"],
    }


class ScoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.run = {
            "run_id": "C1_neutral_r01",
            "case_id": "C1",
            "condition": "neutral",
            "replicate": 1,
            "temperature": 0,
        }

    def test_schema_and_scoring(self) -> None:
        initial = validate_initial(initial_fixture(), {f"C1-F{i}" for i in range(1, 7)})
        revision_raw = revision_fixture()
        revision_for_validation = {key: value for key, value in revision_raw.items() if not key.startswith("_")}
        revision = validate_revision(
            revision_for_validation,
            {f"C1-F{i}" for i in range(1, 7)},
            {"C1-F4", "C1-F5", "C1-F6"},
        )
        revision["_challenge_fact_ids"] = revision_raw["_challenge_fact_ids"]
        coded = code_run(
            self.run,
            initial,
            revision,
            {"unsupported_evidence_score": 0, "revision_responsiveness_score": 3},
        )
        self.assertEqual(coded["initial_d"], 0.3)
        self.assertEqual(coded["revised_d"], 0.0)
        self.assertEqual(coded["movement_toward_challenged_interpretation"], 0.3)
        self.assertEqual(coded["challenge_fact_incorporation"], 1.0)
        self.assertTrue(coded["category_changed"])

    def test_initial_and_full_behavioral_uniqueness_are_separate(self) -> None:
        initial = initial_fixture()
        revision = revision_fixture()
        row1 = code_run(self.run, initial, revision)
        run2 = {**self.run, "run_id": "C1_neutral_r02", "replicate": 2}
        revision2 = revision_fixture()
        revision2["revised_confidence"] = 56
        row2 = code_run(run2, initial, revision2)
        diagnostics = duplicate_diagnostics(
            [row1, row2],
            {
                self.run["run_id"]: (initial, revision),
                run2["run_id"]: (initial, revision2),
            },
        )[0]
        self.assertEqual(diagnostics["initial_behavioral_unique_count"], 1)
        self.assertEqual(diagnostics["full_behavioral_unique_count"], 2)
        self.assertTrue(diagnostics["initial_effectively_deterministic"])
        self.assertFalse(diagnostics["full_effectively_deterministic"])


if __name__ == "__main__":
    unittest.main()

