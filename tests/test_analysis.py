from __future__ import annotations

import unittest

from path_dependence.analysis import (
    condition_slope_summaries,
    condition_turn_interactions,
    fresh_update_effects,
    lagged_abstraction_rows,
    monotonicity_summaries,
    planned_contrasts,
    trajectory_slope_rows,
    transition_rows,
    turn_condition_summaries,
    within_condition_changes,
)
from path_dependence.protocol import CONDITIONS
from path_dependence.scoring import code_trajectory
from test_scoring_and_diagnostics import (
    annotations_fixture,
    assessment_fixture,
    run_fixture,
)


class AnalysisTests(unittest.TestCase):
    def test_complete_longitudinal_analysis_shapes(self) -> None:
        coded: list[dict] = []
        steps = {
            "fresh_evidence": 1,
            "no_new_evidence": 2,
            "re_anchored": 0,
            "self_summary": 3,
        }
        for condition in CONDITIONS:
            for replicate in (1, 2):
                assessments = {
                    turn: assessment_fixture(condition, turn, d_step=steps[condition])
                    for turn in range(4)
                }
                coded.extend(
                    code_trajectory(
                        run_fixture(condition, replicate),
                        assessments,
                        annotations_fixture(),
                    )
                )

        turn_summary = turn_condition_summaries(coded)
        slopes = trajectory_slope_rows(coded)
        slope_summary = condition_slope_summaries(slopes)
        changes = within_condition_changes(coded)
        contrasts = planned_contrasts(slope_summary, changes)
        interactions = condition_turn_interactions(turn_summary)
        monotonicity = monotonicity_summaries(coded)
        conclusion_transitions = transition_rows(coded, "conclusion_category")
        recommendation_transitions = transition_rows(coded, "recommendation_category")
        fresh = fresh_update_effects(coded)
        lagged = lagged_abstraction_rows(coded)

        self.assertEqual(len(turn_summary), 16)
        self.assertEqual(len(slopes), 8)
        self.assertEqual(len(slope_summary), 4)
        self.assertEqual(len(changes), 4)
        self.assertEqual(len(contrasts), 44)
        self.assertEqual(len(interactions), 132)
        self.assertEqual(len(monotonicity), 4)
        self.assertGreater(len(conclusion_transitions), 0)
        self.assertGreater(len(recommendation_transitions), 0)
        self.assertEqual(len(fresh), 3)
        self.assertEqual(len(lagged), 24)
        target = next(
            row
            for row in contrasts
            if row["contrast"] == "self_summary_vs_re_anchored"
            and row["outcome"] == "absolute_drift_from_t0"
        )
        self.assertGreater(target["difference_in_mean_longitudinal_slope"], 0)


if __name__ == "__main__":
    unittest.main()
