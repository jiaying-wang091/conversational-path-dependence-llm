from __future__ import annotations

import unittest

from path_dependence.protocol import (
    CONDITIONS,
    FRESH_UPDATES,
    ORIGINAL_FACTS,
    RE_ANCHORED_PROMPT_BASE,
    RESPONSE_CONSTRAINTS,
    RESPONSE_SCHEMA,
    T0_PROMPT,
    available_fact_ids,
    planned_user_turns,
    user_prompt,
)
from path_dependence.validation import assert_protocol_valid


class ProtocolTests(unittest.TestCase):
    def test_complete_phase1c_protocol_is_valid(self) -> None:
        report = assert_protocol_valid()
        self.assertTrue(report["valid"])
        self.assertEqual(report["original_fact_count"], 6)
        self.assertEqual(report["condition_count"], 4)
        self.assertEqual(report["planned_trajectories_at_ten_replicates"], 40)
        self.assertEqual(report["planned_model_responses"], 160)

    def test_fixed_fact_sets(self) -> None:
        self.assertEqual(set(ORIGINAL_FACTS), {f"C-F{i}" for i in range(1, 7)})
        self.assertEqual(set(FRESH_UPDATES), {f"C-U{i}" for i in range(1, 4)})
        self.assertEqual(len(set(ORIGINAL_FACTS.values())), 6)
        self.assertEqual(len(set(FRESH_UPDATES.values())), 3)

    def test_t0_and_response_contract_are_identical(self) -> None:
        for condition in CONDITIONS:
            self.assertEqual(user_prompt(condition, 0), T0_PROMPT)
            for turn in range(4):
                prompt = user_prompt(condition, turn)
                self.assertIn(RESPONSE_SCHEMA, prompt)
                self.assertIn(RESPONSE_CONSTRAINTS, prompt)

    def test_turn_structure_and_fact_availability(self) -> None:
        for condition in CONDITIONS:
            turns = planned_user_turns(condition)
            self.assertEqual([item["turn"] for item in turns], [0, 1, 2, 3])
            for turn in range(4):
                expected = set(ORIGINAL_FACTS)
                if condition == "fresh_evidence":
                    expected |= {f"C-U{i}" for i in range(1, turn + 1)}
                self.assertEqual(available_fact_ids(condition, turn), expected)

    def test_reanchored_prompt_has_only_renewed_fact_attention_manipulation(self) -> None:
        self.assertIn("return to the six original facts C-F1 through C-F6", RE_ANCHORED_PROMPT_BASE)
        self.assertNotIn(
            "Do not treat earlier assistant wording as additional evidence.",
            RE_ANCHORED_PROMPT_BASE,
        )


if __name__ == "__main__":
    unittest.main()
