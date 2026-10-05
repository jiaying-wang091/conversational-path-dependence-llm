"""Descriptive longitudinal analysis for the frozen Phase 1C protocol."""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean, median


CONDITIONS = (
    "fresh_evidence",
    "no_new_evidence",
    "re_anchored",
    "self_summary",
)

OUTCOMES = (
    "directional_belief_d",
    "absolute_drift_from_t0",
    "confidence",
    "confidence_change_from_t0",
    "original_fact_citation_rate",
    "original_fact_omission_rate",
    "unsupported_interpretation_rate",
    "factual_hallucination_rate",
    "prior_abstraction_reference_rate",
    "abstraction_as_evidence_rate",
    "recommendation_intensity",
)

PRIMARY_CONTRASTS = (
    ("no_new_vs_re_anchored", "no_new_evidence", "re_anchored", "primary"),
    ("self_summary_vs_no_new", "self_summary", "no_new_evidence", "primary"),
    ("self_summary_vs_re_anchored", "self_summary", "re_anchored", "primary"),
    ("fresh_vs_no_new", "fresh_evidence", "no_new_evidence", "descriptive_benchmark"),
)


def _mean_available(values: list[float | int | None]) -> float | None:
    present = [value for value in values if value is not None]
    return mean(present) if present else None


def _median_available(values: list[float | int | None]) -> float | None:
    present = [value for value in values if value is not None]
    return median(present) if present else None


def _slope(rows: list[dict], outcome: str) -> float | None:
    points = [(row["turn"], row[outcome]) for row in rows if row[outcome] is not None]
    if len(points) < 2:
        return None
    xbar = mean(x for x, _ in points)
    ybar = mean(y for _, y in points)
    denominator = sum((x - xbar) ** 2 for x, _ in points)
    if denominator == 0:
        return None
    return sum((x - xbar) * (y - ybar) for x, y in points) / denominator


def _trajectory_groups(coded_rows: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in coded_rows:
        groups[row["run_id"]].append(row)
    for rows in groups.values():
        rows.sort(key=lambda item: item["turn"])
    return groups


def turn_condition_summaries(coded_rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for row in coded_rows:
        groups[(row["condition"], row["turn"])].append(row)
    output: list[dict] = []
    for (condition, turn), rows in sorted(groups.items()):
        categories = Counter(row["conclusion_category"] for row in rows)
        output.append(
            {
                "condition": condition,
                "turn": turn,
                "turn_id": f"T{turn}",
                "observed_trajectories": len(rows),
                "count_a": categories["A"],
                "count_b": categories["B"],
                "count_indeterminate": categories["genuinely_indeterminate"],
                **{
                    f"mean_{outcome}": _mean_available([row[outcome] for row in rows])
                    for outcome in OUTCOMES
                },
                **{
                    f"median_{outcome}": _median_available([row[outcome] for row in rows])
                    for outcome in OUTCOMES
                },
                "manual_coding_complete_count": sum(
                    bool(row["manual_coding_complete"]) for row in rows
                ),
            }
        )
    return output


def trajectory_slope_rows(coded_rows: list[dict]) -> list[dict]:
    output: list[dict] = []
    for run_id, rows in sorted(_trajectory_groups(coded_rows).items()):
        base = rows[0]
        output.append(
            {
                "run_id": run_id,
                "condition": base["condition"],
                "replicate": base["replicate"],
                **{f"slope_{outcome}": _slope(rows, outcome) for outcome in OUTCOMES},
            }
        )
    return output


def condition_slope_summaries(slope_rows: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in slope_rows:
        groups[row["condition"]].append(row)
    output: list[dict] = []
    for condition in CONDITIONS:
        rows = groups[condition]
        output.append(
            {
                "condition": condition,
                "trajectory_count": len(rows),
                **{
                    f"mean_slope_{outcome}": _mean_available(
                        [row[f"slope_{outcome}"] for row in rows]
                    )
                    for outcome in OUTCOMES
                },
            }
        )
    return output


def within_condition_changes(coded_rows: list[dict]) -> list[dict]:
    groups = _trajectory_groups(coded_rows)
    by_condition: dict[str, list[dict]] = defaultdict(list)
    for rows in groups.values():
        by_condition[rows[0]["condition"]].append(
            {
                outcome: (
                    rows[-1][outcome] - rows[0][outcome]
                    if rows[-1][outcome] is not None and rows[0][outcome] is not None
                    else None
                )
                for outcome in OUTCOMES
            }
        )
    return [
        {
            "condition": condition,
            "contrast": "T3_minus_T0",
            "trajectory_count": len(by_condition[condition]),
            **{
                f"mean_change_{outcome}": _mean_available(
                    [row[outcome] for row in by_condition[condition]]
                )
                for outcome in OUTCOMES
            },
        }
        for condition in CONDITIONS
    ]


def planned_contrasts(
    slope_summaries: list[dict], change_rows: list[dict]
) -> list[dict]:
    slopes = {row["condition"]: row for row in slope_summaries}
    changes = {row["condition"]: row for row in change_rows}
    output: list[dict] = []
    for name, left, right, status in PRIMARY_CONTRASTS:
        for outcome in OUTCOMES:
            left_slope = slopes[left][f"mean_slope_{outcome}"]
            right_slope = slopes[right][f"mean_slope_{outcome}"]
            left_change = changes[left][f"mean_change_{outcome}"]
            right_change = changes[right][f"mean_change_{outcome}"]
            output.append(
                {
                    "contrast": name,
                    "left_condition": left,
                    "right_condition": right,
                    "analysis_status": status,
                    "outcome": outcome,
                    "difference_in_mean_longitudinal_slope": (
                        left_slope - right_slope
                        if left_slope is not None and right_slope is not None
                        else None
                    ),
                    "difference_in_mean_T3_minus_T0_change": (
                        left_change - right_change
                        if left_change is not None and right_change is not None
                        else None
                    ),
                }
            )
    return output


def condition_turn_interactions(turn_rows: list[dict]) -> list[dict]:
    index = {(row["condition"], row["turn"]): row for row in turn_rows}
    output: list[dict] = []
    for name, left, right, status in PRIMARY_CONTRASTS:
        for turn in (1, 2, 3):
            for outcome in OUTCOMES:
                field = f"mean_{outcome}"
                values = (
                    index[(left, turn)][field],
                    index[(left, 0)][field],
                    index[(right, turn)][field],
                    index[(right, 0)][field],
                )
                interaction = None
                if all(value is not None for value in values):
                    left_t, left_0, right_t, right_0 = values
                    interaction = (left_t - left_0) - (right_t - right_0)
                output.append(
                    {
                        "contrast": name,
                        "left_condition": left,
                        "right_condition": right,
                        "analysis_status": status,
                        "turn": turn,
                        "turn_id": f"T{turn}",
                        "outcome": outcome,
                        "condition_by_turn_difference_in_differences": interaction,
                    }
                )
    return output


def monotonicity_summaries(coded_rows: list[dict]) -> list[dict]:
    by_condition: dict[str, list[list[dict]]] = defaultdict(list)
    for rows in _trajectory_groups(coded_rows).values():
        by_condition[rows[0]["condition"]].append(rows)
    output: list[dict] = []
    for condition in CONDITIONS:
        trajectories = by_condition[condition]
        confidence_monotonic = [
            all(rows[index]["confidence"] <= rows[index + 1]["confidence"] for index in range(3))
            and any(rows[index]["confidence"] < rows[index + 1]["confidence"] for index in range(3))
            for rows in trajectories
        ]
        drift_monotonic = [
            all(
                rows[index]["absolute_drift_from_t0"]
                <= rows[index + 1]["absolute_drift_from_t0"]
                for index in range(3)
            )
            and any(
                rows[index]["absolute_drift_from_t0"]
                < rows[index + 1]["absolute_drift_from_t0"]
                for index in range(3)
            )
            for rows in trajectories
        ]
        output.append(
            {
                "condition": condition,
                "trajectory_count": len(trajectories),
                "monotonically_increasing_confidence_count": sum(confidence_monotonic),
                "monotonically_increasing_confidence_rate": mean(confidence_monotonic),
                "monotonically_increasing_absolute_drift_count": sum(drift_monotonic),
                "monotonically_increasing_absolute_drift_rate": mean(drift_monotonic),
            }
        )
    return output


def transition_rows(coded_rows: list[dict], field: str) -> list[dict]:
    output: list[dict] = []
    by_condition: dict[str, list[list[dict]]] = defaultdict(list)
    for rows in _trajectory_groups(coded_rows).values():
        by_condition[rows[0]["condition"]].append(rows)
    for condition in CONDITIONS:
        for from_turn, to_turn in ((0, 1), (1, 2), (2, 3), (0, 3)):
            counts = Counter(
                (rows[from_turn][field], rows[to_turn][field])
                for rows in by_condition[condition]
            )
            for (from_value, to_value), count in sorted(counts.items()):
                output.append(
                    {
                        "condition": condition,
                        "field": field,
                        "from_turn": from_turn,
                        "to_turn": to_turn,
                        "from_value": from_value,
                        "to_value": to_value,
                        "count": count,
                    }
                )
    return output


def fresh_update_effects(coded_rows: list[dict]) -> list[dict]:
    fresh = [
        rows
        for rows in _trajectory_groups(coded_rows).values()
        if rows[0]["condition"] == "fresh_evidence"
    ]
    output: list[dict] = []
    for turn in (1, 2, 3):
        output.append(
            {
                "condition": "fresh_evidence",
                "turn": turn,
                "turn_id": f"T{turn}",
                "update_fact_id": f"C-U{turn}",
                "mean_signed_d_change_from_previous_turn": mean(
                    rows[turn]["directional_belief_d"]
                    - rows[turn - 1]["directional_belief_d"]
                    for rows in fresh
                ),
                "mean_absolute_d_change_from_previous_turn": mean(
                    abs(
                        rows[turn]["directional_belief_d"]
                        - rows[turn - 1]["directional_belief_d"]
                    )
                    for rows in fresh
                ),
                "mean_confidence_change_from_previous_turn": mean(
                    rows[turn]["confidence"] - rows[turn - 1]["confidence"]
                    for rows in fresh
                ),
                "mean_new_fact_citation_rate": _mean_available(
                    [rows[turn]["new_fact_citation_rate"] for rows in fresh]
                ),
            }
        )
    return output


def lagged_abstraction_rows(coded_rows: list[dict]) -> list[dict]:
    output: list[dict] = []
    for run_id, rows in sorted(_trajectory_groups(coded_rows).items()):
        for turn in (0, 1, 2):
            output.append(
                {
                    "run_id": run_id,
                    "condition": rows[0]["condition"],
                    "turn_t": turn,
                    "turn_t_plus_1": turn + 1,
                    "d_t": rows[turn]["directional_belief_d"],
                    "prior_abstraction_reference_rate_t": rows[turn][
                        "prior_abstraction_reference_rate"
                    ],
                    "abstraction_as_evidence_rate_t": rows[turn][
                        "abstraction_as_evidence_rate"
                    ],
                    "additional_absolute_drift_at_t_plus_1": rows[turn + 1][
                        "absolute_drift_from_t0"
                    ]
                    - rows[turn]["absolute_drift_from_t0"],
                    "additional_confidence_at_t_plus_1": rows[turn + 1]["confidence"]
                    - rows[turn]["confidence"],
                    "analysis_status": "exploratory_descriptive_not_causal",
                }
            )
    return output
