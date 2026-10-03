from __future__ import annotations

import unittest

from path_dependence.protocol import (
    CASES,
    CONDITIONS,
    FROZEN_DIAGNOSTICITY,
    ORDERS,
    challenge_fact_ids,
    evidence_batches,
    initial_transcript,
    revision_prompt,
)
from path_dependence.validation import EXPECTED_DIAGNOSTICITY, assert_protocol_valid


class ProtocolTests(unittest.TestCase):
    def test_complete_phase1b_protocol_is_valid(self) -> None:
        report = assert_protocol_valid()
        self.assertTrue(report["valid"])
        self.assertEqual(report["variant_count"], 6)
        self.assertEqual(report["condition_count"], 5)
        self.assertEqual(report["cell_count"], 30)
        self.assertEqual(report["expected_runs_at_five_replicates"], 150)

    def test_all_six_variants_and_exactly_six_facts(self) -> None:
        self.assertEqual(set(CASES), {"LA", "LB", "MA", "MB", "HA", "HB"})
        for variant_id, variant in CASES.items():
            self.assertEqual(
                set(variant.facts), {f"{variant_id}-F{i}" for i in range(1, 7)}
            )
            self.assertEqual(len(set(variant.facts.values())), 6)

    def test_every_cell_contains_each_verbatim_fact_once_in_correct_order(self) -> None:
        for variant_id, variant in CASES.items():
            for condition_id, condition in CONDITIONS.items():
                batches = evidence_batches(variant_id, condition_id)
                combined = "\n\n".join(batches)
                for fact_id, fact in variant.facts.items():
                    self.assertEqual(combined.count(f"{fact_id}: {fact}"), 1)
                observed_numbers = [
                    int(line.split(":", 1)[0].rsplit("F", 1)[1])
                    for batch in batches
                    for line in batch.split("\n\n")
                ]
                expected_numbers = [
                    number for pair in ORDERS[condition.order_id] for number in pair
                ]
                self.assertEqual(observed_numbers, expected_numbers)

    def test_commitments_are_exactly_order_matched(self) -> None:
        for variant_id in CASES:
            self.assertEqual(
                evidence_batches(variant_id, "commit_a"),
                evidence_batches(variant_id, "positive_first"),
            )
            self.assertEqual(
                evidence_batches(variant_id, "commit_b"),
                evidence_batches(variant_id, "negative_first"),
            )

    def test_frozen_diagnosticity_and_pair_symmetry(self) -> None:
        self.assertEqual(FROZEN_DIAGNOSTICITY, EXPECTED_DIAGNOSTICITY)
        expected = {"low": (5, 11), "medium": (2, 10), "high": (1, 7)}
        pairs = {"low": ("LA", "LB"), "medium": ("MA", "MB"), "high": ("HA", "HB")}
        for level, (a_id, b_id) in pairs.items():
            a_scores = CASES[a_id].diagnosticity_scores
            b_scores = CASES[b_id].diagnosticity_scores
            self.assertEqual(sum(a_scores), -sum(b_scores))
            self.assertEqual(abs(sum(a_scores)), expected[level][0])
            self.assertEqual(sum(abs(value) for value in a_scores), expected[level][1])
            self.assertEqual(sum(abs(value) for value in b_scores), expected[level][1])

    def test_transcript_roles_are_fixed(self) -> None:
        expected = ["system", "user", "user", "assistant", "user", "assistant", "user", "assistant", "user"]
        for variant_id in CASES:
            for condition_id in CONDITIONS:
                self.assertEqual(
                    [message["role"] for message in initial_transcript(variant_id, condition_id)],
                    expected,
                )

    def test_adaptive_challenge_selection(self) -> None:
        base = {"probabilities": {"A": 45, "B": 45, "Genuinely_indeterminate": 10}}
        a = {**base, "most_likely_interpretation": "A"}
        b = {**base, "most_likely_interpretation": "B"}
        indeterminate = {**base, "most_likely_interpretation": "Genuinely indeterminate"}
        self.assertEqual(challenge_fact_ids("LA", a), ["LA-F4", "LA-F5", "LA-F6"])
        self.assertEqual(challenge_fact_ids("LA", b), ["LA-F1", "LA-F2", "LA-F3"])
        self.assertEqual(
            challenge_fact_ids("LA", indeterminate), ["LA-F1", "LA-F2", "LA-F3"]
        )
        prompt, ids = revision_prompt("LA", a)
        self.assertEqual(ids, ["LA-F4", "LA-F5", "LA-F6"])
        self.assertIn("These are not new facts.", prompt)


if __name__ == "__main__":
    unittest.main()
