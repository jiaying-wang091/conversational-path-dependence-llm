"""Initial, per-turn, and full-trajectory duplicate diagnostics."""

from __future__ import annotations

import itertools
import json
from collections import defaultdict
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _model_output_only(value: dict) -> dict:
    return {key: item for key, item in value.items() if not key.startswith("_")}


def turn_behavioral_signature(row: dict) -> tuple:
    return (
        row["conclusion_category"],
        row["confidence"],
        row["p_a"],
        row["p_b"],
        row["p_indeterminate"],
        tuple(row["original_fact_ids_cited"]),
        tuple(row["new_fact_ids_cited"]),
        row["recommendation_category"],
        row["recommendation_intensity"],
    )


def _duplicate_rate(values: list[Any]) -> float | None:
    pairs = list(itertools.combinations(values, 2))
    if not pairs:
        return None
    return sum(left == right for left, right in pairs) / len(pairs)


def duplicate_diagnostics(
    coded_rows: list[dict], parsed_by_run: dict[str, dict[int, dict]]
) -> tuple[list[dict], list[dict]]:
    trajectories: dict[str, list[dict]] = defaultdict(list)
    for row in coded_rows:
        trajectories[row["run_id"]].append(row)
    for rows in trajectories.values():
        rows.sort(key=lambda item: item["turn"])

    by_condition: dict[str, list[str]] = defaultdict(list)
    for run_id, rows in trajectories.items():
        by_condition[rows[0]["condition"]].append(run_id)

    condition_rows: list[dict] = []
    turn_rows: list[dict] = []
    for condition, run_ids in sorted(by_condition.items()):
        run_ids.sort()
        initial_exact = [
            canonical_json(_model_output_only(parsed_by_run[run_id][0]))
            for run_id in run_ids
        ]
        full_exact = [
            canonical_json(
                {
                    f"T{turn}": _model_output_only(parsed_by_run[run_id][turn])
                    for turn in range(4)
                }
            )
            for run_id in run_ids
        ]
        initial_behavior = [
            turn_behavioral_signature(trajectories[run_id][0]) for run_id in run_ids
        ]
        full_behavior = [
            tuple(turn_behavioral_signature(row) for row in trajectories[run_id])
            for run_id in run_ids
        ]
        condition_rows.append(
            {
                "condition": condition,
                "trajectory_count": len(run_ids),
                "initial_exact_unique_count": len(set(initial_exact)),
                "initial_exact_duplicate_rate": _duplicate_rate(initial_exact),
                "full_exact_unique_count": len(set(full_exact)),
                "full_exact_duplicate_rate": _duplicate_rate(full_exact),
                "initial_behavioral_unique_count": len(set(initial_behavior)),
                "initial_behavioral_duplicate_rate": _duplicate_rate(initial_behavior),
                "full_behavioral_unique_count": len(set(full_behavior)),
                "full_behavioral_duplicate_rate": _duplicate_rate(full_behavior),
                "initial_effectively_deterministic": len(set(initial_behavior)) == 1,
                "full_effectively_deterministic": len(set(full_behavior)) == 1,
                "independence_warning": (
                    "Repeated behaviorally identical temperature-0 trajectories are a "
                    "reproducibility diagnostic, not independent evidence."
                    if len(set(full_behavior)) == 1
                    else "Residual model nondeterminism observed; report the full distribution."
                ),
            }
        )
        for turn in range(4):
            exact = [
                canonical_json(_model_output_only(parsed_by_run[run_id][turn]))
                for run_id in run_ids
            ]
            behavior = [
                turn_behavioral_signature(trajectories[run_id][turn])
                for run_id in run_ids
            ]
            turn_rows.append(
                {
                    "condition": condition,
                    "turn": turn,
                    "turn_id": f"T{turn}",
                    "trajectory_count": len(run_ids),
                    "exact_unique_count": len(set(exact)),
                    "exact_duplicate_rate": _duplicate_rate(exact),
                    "behavioral_unique_count": len(set(behavior)),
                    "behavioral_duplicate_rate": _duplicate_rate(behavior),
                    "effectively_deterministic": len(set(behavior)) == 1,
                }
            )
    return condition_rows, turn_rows
