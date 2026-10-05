from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from path_dependence.runner import ExperimentConfig, build_manifest, execute, write_manifest
from path_dependence.storage import read_jsonl


class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = ExperimentConfig.from_path(Path("config.example.json"))

    def test_default_manifest_is_40_trajectories_and_160_responses(self) -> None:
        manifest = build_manifest(self.config)
        self.assertEqual(len(manifest), 40)
        self.assertEqual(sum(row["planned_model_responses"] for row in manifest), 160)
        self.assertEqual(
            {row["condition"] for row in manifest},
            {"fresh_evidence", "no_new_evidence", "re_anchored", "self_summary"},
        )
        self.assertEqual({row["replicate"] for row in manifest}, set(range(1, 11)))
        self.assertTrue(all(row["approved_decoding"] for row in manifest))

    def test_filtered_manifest_for_future_smoke_test(self) -> None:
        manifest = build_manifest(
            self.config, condition_ids=["no_new_evidence"], replicates=1
        )
        self.assertEqual(len(manifest), 1)
        self.assertEqual(manifest[0]["planned_model_responses"], 4)

    def test_written_plans_contain_four_user_turns(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            write_manifest(self.config, Path(directory))
            plans = read_jsonl(Path(directory) / "planned_conversations.jsonl")
            self.assertEqual(len(plans), 40)
            self.assertTrue(all(len(plan["user_turns"]) == 4 for plan in plans))
            self.assertTrue(all(len(plan["assistant_turn_placeholders"]) == 4 for plan in plans))

    def test_execution_gate_blocks_before_provider_creation(self) -> None:
        with patch("path_dependence.runner.provider_from_config") as provider:
            with self.assertRaisesRegex(RuntimeError, "--execute-paid-api"):
                execute(self.config, paid_api_confirmed=False)
            provider.assert_not_called()

    def test_replicate_override_cannot_exceed_ten(self) -> None:
        with self.assertRaisesRegex(ValueError, "between 1 and 10"):
            build_manifest(self.config, replicates=11)


if __name__ == "__main__":
    unittest.main()
