"""Descriptive, counterbalanced Phase 1B analysis."""

from __future__ import annotations

import itertools
from collections import Counter, defaultdict
from statistics import mean

from .diagnostics import initial_behavioral_signature
from .protocol import CASES


LEVELS = ("low", "medium", "high")
POLARITIES = ("A", "B")


def _pairwise_disagreement(values: list[str]) -> float | None:
    pairs = list(itertools.combinations(values, 2))
    if not pairs:
        return None
    return sum(left != right for left, right in pairs) / len(pairs)


def _mean_available(values: list[float | int | None]) -> float | None:
    available = [value for value in values if value is not None]
    return mean(available) if available else None


def condition_summaries(coded_rows: list[dict], diagnostics: list[dict]) -> list[dict]:
    diagnostic_index = {(row["case_id"], row["condition"]): row for row in diagnostics}
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in coded_rows:
        groups[(row["case_id"], row["condition"])].append(row)

    summaries: list[dict] = []
    for (variant_id, condition), rows in sorted(groups.items()):
        variant = CASES[variant_id]
        categories = Counter(row["initial_category"] for row in rows)
        recommendations = [row["initial_recommendation_category"] for row in rows]
        diagnostic = diagnostic_index[(variant_id, condition)]
        summaries.append(
            {
                "variant_id": variant_id,
                "case_id": variant_id,
                "ambiguity_level": variant.ambiguity_level,
                "baseline_polarity": variant.baseline_polarity,
                "condition": condition,
                "observed_runs": len(rows),
                "unique_initial_behavior_patterns": diagnostic[
                    "initial_behavioral_unique_count"
                ],
                "unique_full_behavior_patterns": diagnostic["full_behavioral_unique_count"],
                "treat_replicates_as_independent": not diagnostic[
                    "full_effectively_deterministic"
                ],
                "count_a": categories["A"],
                "count_b": categories["B"],
                "count_indeterminate": categories["Genuinely indeterminate"],
                "mean_initial_d": mean(row["initial_d"] for row in rows),
                "mean_initial_confidence": mean(row["initial_confidence"] for row in rows),
                "mean_selective_omission": _mean_available(
                    [row["selective_omission_score"] for row in rows]
                ),
                "mean_omitted_fact_count": mean(len(row["omitted_fact_ids"]) for row in rows),
                "mean_total_fact_coverage": mean(row["total_fact_coverage"] for row in rows),
                "mean_recommendation_intensity": _mean_available(
                    [row["initial_recommendation_intensity"] for row in rows]
                ),
                "within_cell_conclusion_disagreement_rate": _pairwise_disagreement(
                    [row["initial_category"] for row in rows]
                ),
                "within_cell_recommendation_disagreement_rate": _pairwise_disagreement(
                    recommendations
                ),
                "secondary_mean_delta_d": mean(row["delta_d"] for row in rows),
                "secondary_mean_challenge_incorporation": mean(
                    row["challenge_fact_incorporation"] for row in rows
                ),
            }
        )
    return summaries


def planned_contrasts(condition_rows: list[dict]) -> list[dict]:
    index = {(row["variant_id"], row["condition"]): row for row in condition_rows}
    definitions = (
        ("order_effect", "positive_first", "negative_first", "primary"),
        ("positive_vs_neutral", "positive_first", "neutral", "primary"),
        ("negative_vs_neutral", "negative_first", "neutral", "primary"),
        ("commit_a_effect", "commit_a", "positive_first", "primary"),
        ("commit_b_effect", "commit_b", "negative_first", "primary"),
        ("commitment_direction_total", "commit_a", "commit_b", "descriptive_total"),
    )
    contrasts: list[dict] = []
    for variant_id in sorted({row["variant_id"] for row in condition_rows}):
        variant = CASES[variant_id]
        for name, left, right, status in definitions:
            left_row = index[(variant_id, left)]
            right_row = index[(variant_id, right)]
            deterministic = not left_row["treat_replicates_as_independent"] or not right_row[
                "treat_replicates_as_independent"
            ]
            selective_left = left_row["mean_selective_omission"]
            selective_right = right_row["mean_selective_omission"]
            recommendation_left = left_row["mean_recommendation_intensity"]
            recommendation_right = right_row["mean_recommendation_intensity"]
            contrasts.append(
                {
                    "variant_id": variant_id,
                    "case_id": variant_id,
                    "ambiguity_level": variant.ambiguity_level,
                    "baseline_polarity": variant.baseline_polarity,
                    "contrast": name,
                    "left_condition": left,
                    "right_condition": right,
                    "analysis_status": status,
                    "difference_mean_initial_d": left_row["mean_initial_d"]
                    - right_row["mean_initial_d"],
                    "absolute_difference_mean_initial_d": abs(
                        left_row["mean_initial_d"] - right_row["mean_initial_d"]
                    ),
                    "difference_mean_initial_confidence": left_row[
                        "mean_initial_confidence"
                    ]
                    - right_row["mean_initial_confidence"],
                    "difference_mean_selective_omission": (
                        selective_left - selective_right
                        if selective_left is not None and selective_right is not None
                        else None
                    ),
                    "difference_mean_omitted_fact_count": left_row[
                        "mean_omitted_fact_count"
                    ]
                    - right_row["mean_omitted_fact_count"],
                    "difference_mean_recommendation_intensity": (
                        recommendation_left - recommendation_right
                        if recommendation_left is not None and recommendation_right is not None
                        else None
                    ),
                    "inferential_independence_warning": deterministic,
                }
            )
    return contrasts


def polarity_pooled_sensitivity(contrast_rows: list[dict]) -> list[dict]:
    index = {
        (row["ambiguity_level"], row["baseline_polarity"], row["contrast"]): row
        for row in contrast_rows
    }
    output: list[dict] = []
    for level in LEVELS:
        commitment_rows = [
            index[(level, polarity, contrast)]
            for polarity in POLARITIES
            for contrast in ("commit_a_effect", "commit_b_effect")
        ]
        order_rows = [index[(level, polarity, "order_effect")] for polarity in POLARITIES]
        salience_rows = [
            index[(level, polarity, contrast)]
            for polarity in POLARITIES
            for contrast in ("positive_vs_neutral", "negative_vs_neutral")
        ]
        output.append(
            {
                "ambiguity_level": level,
                "commitment_sensitivity": mean(
                    abs(row["difference_mean_initial_d"]) for row in commitment_rows
                ),
                "order_sensitivity": mean(
                    abs(row["difference_mean_initial_d"]) for row in order_rows
                ),
                "salience_sensitivity": mean(
                    abs(row["difference_mean_initial_d"]) for row in salience_rows
                ),
                "any_inferential_independence_warning": any(
                    row["inferential_independence_warning"]
                    for row in commitment_rows + order_rows + salience_rows
                ),
            }
        )
    return output


def neutral_manipulation_checks(condition_rows: list[dict]) -> list[dict]:
    neutral = {
        (row["ambiguity_level"], row["baseline_polarity"]): row
        for row in condition_rows
        if row["condition"] == "neutral"
    }
    output: list[dict] = []
    for level in LEVELS:
        a_row = neutral[(level, "A")]
        b_row = neutral[(level, "B")]
        d_a = a_row["mean_initial_d"]
        d_b = b_row["mean_initial_d"]
        output.append(
            {
                "ambiguity_level": level,
                "a_variant": a_row["variant_id"],
                "b_variant": b_row["variant_id"],
                "neutral_mean_d_a": d_a,
                "neutral_mean_d_b": d_b,
                "polarity_symmetry_residual_d_a_plus_d_b": d_a + d_b,
                "mean_neutral_absolute_d": (abs(d_a) + abs(d_b)) / 2,
                "a_direction_matches_ex_ante": d_a > 0,
                "b_direction_matches_ex_ante": d_b < 0,
            }
        )
    return output


def _monotonic_classification(low: float, medium: float, high: float) -> str:
    if low == medium == high:
        return "flat"
    if low <= medium <= high:
        return "fully_monotonic"
    if low >= medium >= high:
        return "reversed"
    return "partially_ordered"


def monotonicity_results(
    sensitivity_rows: list[dict], manipulation_rows: list[dict]
) -> list[dict]:
    sensitivity = {row["ambiguity_level"]: row for row in sensitivity_rows}
    manipulation = {row["ambiguity_level"]: row for row in manipulation_rows}
    definitions = {
        "commitment_sensitivity": {
            level: sensitivity[level]["commitment_sensitivity"] for level in LEVELS
        },
        "order_sensitivity": {
            level: sensitivity[level]["order_sensitivity"] for level in LEVELS
        },
        "salience_sensitivity": {
            level: sensitivity[level]["salience_sensitivity"] for level in LEVELS
        },
        "neutral_absolute_d_manipulation_check": {
            level: manipulation[level]["mean_neutral_absolute_d"] for level in LEVELS
        },
    }
    output: list[dict] = []
    for metric, values in definitions.items():
        if metric == "neutral_absolute_d_manipulation_check":
            observed = _monotonic_classification(
                values["high"], values["medium"], values["low"]
            )
            expected_direction = "low > medium > high"
        else:
            observed = _monotonic_classification(
                values["low"], values["medium"], values["high"]
            )
            expected_direction = "low <= medium <= high"
        output.append(
            {
                "metric": metric,
                "low": values["low"],
                "medium": values["medium"],
                "high": values["high"],
                "expected_direction": expected_direction,
                "classification": observed,
            }
        )
    return output


def factorial_interaction_summary(condition_rows: list[dict]) -> list[dict]:
    index = {
        (row["ambiguity_level"], row["baseline_polarity"], row["condition"]): row
        for row in condition_rows
    }
    conditions = ("negative_first", "positive_first", "commit_a", "commit_b")
    provisional: dict[tuple[str, str], dict] = {}
    for level in LEVELS:
        for condition in conditions:
            effect_a = (
                index[(level, "A", condition)]["mean_initial_d"]
                - index[(level, "A", "neutral")]["mean_initial_d"]
            )
            effect_b = (
                index[(level, "B", condition)]["mean_initial_d"]
                - index[(level, "B", "neutral")]["mean_initial_d"]
            )
            provisional[(level, condition)] = {
                "ambiguity_level": level,
                "trajectory_condition": condition,
                "effect_vs_neutral_a_polarity": effect_a,
                "effect_vs_neutral_b_polarity": effect_b,
                "trajectory_by_polarity_interaction": effect_a - effect_b,
            }

    output: list[dict] = []
    for condition in conditions:
        low_interaction = provisional[("low", condition)][
            "trajectory_by_polarity_interaction"
        ]
        previous = low_interaction
        for level in LEVELS:
            row = dict(provisional[(level, condition)])
            current = row["trajectory_by_polarity_interaction"]
            row["three_way_interaction_change_from_low"] = current - low_interaction
            row["three_way_interaction_change_from_previous_level"] = (
                0.0 if level == "low" else current - previous
            )
            output.append(row)
            previous = current
    return output


def variant_instability(coded_rows: list[dict]) -> list[dict]:
    by_variant: dict[str, list[dict]] = defaultdict(list)
    for row in coded_rows:
        by_variant[row["case_id"]].append(row)
    output: list[dict] = []
    for variant_id, rows in sorted(by_variant.items()):
        unique_by_cell: dict[tuple[str, tuple], dict] = {}
        for row in rows:
            unique_by_cell[(row["condition"], initial_behavioral_signature(row))] = row
        unique_rows = list(unique_by_cell.values())
        categories = [row["initial_category"] for row in unique_rows]
        ds = [row["initial_d"] for row in unique_rows]
        confidences = [row["initial_confidence"] for row in unique_rows]
        recommendations = [row["initial_recommendation_category"] for row in unique_rows]
        omissions = [
            row["selective_omission_score"]
            for row in unique_rows
            if row["selective_omission_score"] is not None
        ]
        variant = CASES[variant_id]
        output.append(
            {
                "variant_id": variant_id,
                "ambiguity_level": variant.ambiguity_level,
                "baseline_polarity": variant.baseline_polarity,
                "unique_initial_behavior_patterns_across_cells": len(unique_rows),
                "distinct_initial_categories": len(set(categories)),
                "pairwise_conclusion_disagreement_rate": _pairwise_disagreement(categories),
                "initial_d_range": max(ds) - min(ds),
                "initial_confidence_range": max(confidences) - min(confidences),
                "recommendation_disagreement_rate": _pairwise_disagreement(recommendations),
                "selective_omission_range": max(omissions) - min(omissions) if omissions else None,
            }
        )
    return output


def ambiguity_disagreement_summaries(instability_rows: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in instability_rows:
        groups[row["ambiguity_level"]].append(row)
    output: list[dict] = []
    for level in LEVELS:
        rows = groups[level]
        output.append(
            {
                "ambiguity_level": level,
                "variant_count": len(rows),
                "mean_pairwise_conclusion_disagreement_rate": mean(
                    row["pairwise_conclusion_disagreement_rate"] for row in rows
                ),
                "mean_recommendation_disagreement_rate": mean(
                    row["recommendation_disagreement_rate"] for row in rows
                ),
                "mean_initial_d_range": mean(row["initial_d_range"] for row in rows),
                "mean_initial_confidence_range": mean(
                    row["initial_confidence_range"] for row in rows
                ),
                "mean_distinct_initial_categories": mean(
                    row["distinct_initial_categories"] for row in rows
                ),
            }
        )
    return output


# Compatibility alias for callers built against Phase 1A.
case_instability = variant_instability
