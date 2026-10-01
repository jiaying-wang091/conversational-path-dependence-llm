"""Descriptive, case-blocked analysis for the approved pilot."""

from __future__ import annotations

import itertools
from collections import Counter, defaultdict
from statistics import mean

from .diagnostics import initial_behavioral_signature


def _pairwise_disagreement(values: list[str]) -> float | None:
    pairs = list(itertools.combinations(values, 2))
    if not pairs:
        return None
    return sum(left != right for left, right in pairs) / len(pairs)


def condition_summaries(coded_rows: list[dict], diagnostics: list[dict]) -> list[dict]:
    diagnostic_index = {(d["case_id"], d["condition"]): d for d in diagnostics}
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in coded_rows:
        groups[(row["case_id"], row["condition"])].append(row)

    summaries: list[dict] = []
    for (case_id, condition), rows in sorted(groups.items()):
        categories = Counter(row["initial_category"] for row in rows)
        recommendations = [row["initial_recommendation_category"] for row in rows]
        diagnostic = diagnostic_index[(case_id, condition)]
        summaries.append(
            {
                "case_id": case_id,
                "condition": condition,
                "observed_runs": len(rows),
                "unique_initial_behavior_patterns": diagnostic["initial_behavioral_unique_count"],
                "unique_full_behavior_patterns": diagnostic["full_behavioral_unique_count"],
                "treat_replicates_as_independent": not diagnostic["full_effectively_deterministic"],
                "count_a": categories["A"],
                "count_b": categories["B"],
                "count_indeterminate": categories["Genuinely indeterminate"],
                "mean_initial_d": mean(row["initial_d"] for row in rows),
                "mean_initial_confidence": mean(row["initial_confidence"] for row in rows),
                "mean_selective_omission": mean(
                    row["selective_omission_score"]
                    for row in rows
                    if row["selective_omission_score"] is not None
                )
                if any(row["selective_omission_score"] is not None for row in rows)
                else None,
                "recommendation_disagreement_rate": _pairwise_disagreement(recommendations),
                "secondary_mean_delta_d": mean(row["delta_d"] for row in rows),
                "secondary_mean_challenge_incorporation": mean(
                    row["challenge_fact_incorporation"] for row in rows
                ),
            }
        )
    return summaries


def planned_contrasts(condition_rows: list[dict]) -> list[dict]:
    index = {(row["case_id"], row["condition"]): row for row in condition_rows}
    definitions = (
        ("order_effect", "positive_first", "negative_first", "primary"),
        ("positive_vs_neutral", "positive_first", "neutral", "primary"),
        ("negative_vs_neutral", "negative_first", "neutral", "primary"),
        ("commit_a_effect", "commit_a", "positive_first", "primary"),
        ("commit_b_effect", "commit_b", "negative_first", "primary"),
        ("commitment_direction_total", "commit_a", "commit_b", "descriptive_total"),
    )
    contrasts: list[dict] = []
    for case_id in sorted({row["case_id"] for row in condition_rows}):
        for name, left, right, status in definitions:
            left_row = index[(case_id, left)]
            right_row = index[(case_id, right)]
            deterministic = not left_row["treat_replicates_as_independent"] or not right_row[
                "treat_replicates_as_independent"
            ]
            contrasts.append(
                {
                    "case_id": case_id,
                    "contrast": name,
                    "left_condition": left,
                    "right_condition": right,
                    "analysis_status": status,
                    "difference_mean_initial_d": left_row["mean_initial_d"]
                    - right_row["mean_initial_d"],
                    "difference_mean_initial_confidence": left_row["mean_initial_confidence"]
                    - right_row["mean_initial_confidence"],
                    "inferential_independence_warning": deterministic,
                }
            )
    return contrasts


def case_instability(coded_rows: list[dict]) -> list[dict]:
    by_case: dict[str, list[dict]] = defaultdict(list)
    for row in coded_rows:
        by_case[row["case_id"]].append(row)
    output: list[dict] = []
    for case_id, rows in sorted(by_case.items()):
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
        output.append(
            {
                "case_id": case_id,
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
