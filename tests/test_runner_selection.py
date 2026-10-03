from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from path_dependence.runner import ExperimentConfig, build_manifest, execute


class RunnerSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = ExperimentConfig.from_path(Path("config.example.json"))

    def test_default_manifest_is_full_150_runs(self) -> None:
        manifest = build_manifest(self.config)
        self.assertEqual(len(manifest), 150)
        self.assertEqual(
            {row["variant_id"] for row in manifest}, {"LA", "LB", "MA", "MB", "HA", "HB"}
        )
        self.assertEqual({row["replicate"] for row in manifest}, {1, 2, 3, 4, 5})
        self.assertTrue(all(row["approved_initial_decoding"] for row in manifest))

    def test_single_variant_one_replicate_scope_has_five_runs(self) -> None:
        manifest = build_manifest(self.config, case_ids=["LA"], replicates=1)
        self.assertEqual(len(manifest), 5)
        self.assertEqual({row["variant_id"] for row in manifest}, {"LA"})
        self.assertEqual(
            {row["condition"] for row in manifest},
            {"neutral", "negative_first", "positive_first", "commit_a", "commit_b"},
        )
        self.assertEqual({row["replicate"] for row in manifest}, {1})

    def test_manifest_includes_frozen_variant_metadata(self) -> None:
        row = build_manifest(
            self.config, case_ids=["LB"], condition_ids=["neutral"], replicates=1
        )[0]
        self.assertEqual(row["ambiguity_level"], "low")
        self.assertEqual(row["baseline_polarity"], "B")
        self.assertEqual(row["diagnosticity_scores"], [1, 1, 1, -2, -3, -3])
        self.assertEqual(row["diagnosticity_net_score"], -5)
        self.assertEqual(row["diagnosticity_total_absolute_strength"], 11)

    def test_execution_gate_blocks_before_provider_creation(self) -> None:
        with patch("path_dependence.runner.provider_from_config") as provider:
            with self.assertRaisesRegex(RuntimeError, "--execute-paid-api"):
                execute(
                    self.config,
                    paid_api_confirmed=False,
                    case_ids=["LA"],
                    replicates=1,
                )
            provider.assert_not_called()

    def test_replicate_override_cannot_exceed_five(self) -> None:
        with self.assertRaisesRegex(ValueError, "between 1 and 5"):
            build_manifest(self.config, case_ids=["LA"], replicates=6)


if __name__ == "__main__":
    unittest.main()
