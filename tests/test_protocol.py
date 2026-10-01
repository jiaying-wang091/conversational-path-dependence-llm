from __future__ import annotations

import unittest

from path_dependence.protocol import (
    CASES,
    CONDITIONS,
    challenge_fact_ids,
    evidence_batches,
    initial_transcript,
    revision_prompt,
)
from path_dependence.validation import assert_protocol_valid


class ProtocolTests(unittest.TestCase):
    def test_complete_protocol_is_valid(self) -> None:
        report = assert_protocol_valid()
        self.assertTrue(report["valid"])
        self.assertEqual(report["cell_count"], 15)
        self.assertEqual(report["expected_runs_at_five_replicates"], 75)

    def test_every_cell_contains_each_verbatim_fact_once(self) -> None:
        for case_id, case in CASES.items():
            for condition_id in CONDITIONS:
                combined = "\n\n".join(evidence_batches(case_id, condition_id))
                for fact_id, fact in case.facts.items():
                    self.assertEqual(combined.count(f"{fact_id}: {fact}"), 1)

    def test_commitments_are_order_matched(self) -> None:
        for case_id in CASES:
            self.assertEqual(
                evidence_batches(case_id, "commit_a"),
                evidence_batches(case_id, "positive_first"),
            )
            self.assertEqual(
                evidence_batches(case_id, "commit_b"),
                evidence_batches(case_id, "negative_first"),
            )

    def test_transcript_roles_are_fixed(self) -> None:
        expected = ["system", "user", "user", "assistant", "user", "assistant", "user", "assistant", "user"]
        for case_id in CASES:
            for condition_id in CONDITIONS:
                self.assertEqual(
                    [message["role"] for message in initial_transcript(case_id, condition_id)],
                    expected,
                )

    def test_adaptive_challenge_selection(self) -> None:
        base = {"probabilities": {"A": 45, "B": 45, "Genuinely_indeterminate": 10}}
        a = {**base, "most_likely_interpretation": "A"}
        b = {**base, "most_likely_interpretation": "B"}
        indeterminate = {**base, "most_likely_interpretation": "Genuinely indeterminate"}
        self.assertEqual(challenge_fact_ids("C1", a), ["C1-F4", "C1-F5", "C1-F6"])
        self.assertEqual(challenge_fact_ids("C1", b), ["C1-F1", "C1-F2", "C1-F3"])
        self.assertEqual(challenge_fact_ids("C1", indeterminate), ["C1-F1", "C1-F2", "C1-F3"])
        prompt, ids = revision_prompt("C1", a)
        self.assertEqual(ids, ["C1-F4", "C1-F5", "C1-F6"])
        self.assertIn("These are not new facts.", prompt)


if __name__ == "__main__":
    unittest.main()

