from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from path_dependence.runner import ExperimentConfig, build_manifest, execute


class RunnerSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = ExperimentConfig.from_path(Path("config.example.json"))

    def test_default_manifest_remains_full_75_runs(self) -> None:
        manifest = build_manifest(self.config)
        self.assertEqual(len(manifest), 75)
        self.assertEqual({row["case_id"] for row in manifest}, {"C1", "C2", "C3"})
        self.assertEqual({row["replicate"] for row in manifest}, {1, 2, 3, 4, 5})

    def test_case_1_one_replicate_smoke_manifest_has_five_runs(self) -> None:
        manifest = build_manifest(self.config, case_ids=["C1"], replicates=1)
        self.assertEqual(len(manifest), 5)
        self.assertEqual({row["case_id"] for row in manifest}, {"C1"})
        self.assertEqual(
            {row["condition"] for row in manifest},
            {"neutral", "negative_first", "positive_first", "commit_a", "commit_b"},
        )
        self.assertEqual({row["replicate"] for row in manifest}, {1})

    def test_execution_gate_blocks_before_provider_creation(self) -> None:
        with patch("path_dependence.runner.provider_from_config") as provider:
            with self.assertRaisesRegex(RuntimeError, "--execute-paid-api"):
                execute(
                    self.config,
                    paid_api_confirmed=False,
                    case_ids=["C1"],
                    replicates=1,
                )
            provider.assert_not_called()

    def test_replicate_override_cannot_exceed_approved_five(self) -> None:
        with self.assertRaisesRegex(ValueError, "between 1 and 5"):
            build_manifest(self.config, case_ids=["C1"], replicates=6)


if __name__ == "__main__":
    unittest.main()
