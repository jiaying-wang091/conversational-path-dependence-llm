"""Exact and behavioral duplicate-output diagnostics."""

from __future__ import annotations

import itertools
import json
from collections import defaultdict
from typing import Any, Callable


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _model_output_only(value: dict) -> dict:
    return {key: item for key, item in value.items() if not key.startswith("_")}


def initial_behavioral_signature(row: dict) -> tuple:
    return (
        row["initial_category"],
        row["initial_confidence"],
        row["initial_p_a"],
        row["initial_p_b"],
        row["initial_p_i"],
        tuple(row["supporting_fact_ids"]),
        tuple(row["against_fact_ids"]),
        tuple(row["omitted_fact_ids"]),
        row["initial_recommendation_category"],
    )


def full_behavioral_signature(row: dict) -> tuple:
    return initial_behavioral_signature(row) + (
        row["revised_category"],
        row["revised_confidence"],
        row["revised_p_a"],
        row["revised_p_b"],
        row["revised_p_i"],
        tuple(row["challenge_fact_ids"]),
        tuple(row["challenge_facts_addressed"]),
        row["revised_recommendation_category"],
        row["category_changed"],
        row["recommendation_changed"],
    )


def _duplicate_rate(values: list[Any], key: Callable[[Any], Any] = lambda value: value) -> float | None:
    pairs = list(itertools.combinations(values, 2))
    if not pairs:
        return None
    return sum(key(left) == key(right) for left, right in pairs) / len(pairs)


def duplicate_diagnostics(
    coded_rows: list[dict], parsed_by_run: dict[str, tuple[dict, dict]]
) -> list[dict]:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in coded_rows:
        groups[(row["case_id"], row["condition"])].append(row)

    diagnostics: list[dict] = []
    for (case_id, condition), rows in sorted(groups.items()):
        rows.sort(key=lambda row: row["replicate"])
        initial_exact = [
            canonical_json(_model_output_only(parsed_by_run[row["run_id"]][0])) for row in rows
        ]
        full_exact = [
            canonical_json(
                {
                    "initial": _model_output_only(parsed_by_run[row["run_id"]][0]),
                    "revision": _model_output_only(parsed_by_run[row["run_id"]][1]),
                }
            )
            for row in rows
        ]
        initial_behavior = [initial_behavioral_signature(row) for row in rows]
        full_behavior = [full_behavioral_signature(row) for row in rows]
        diagnostics.append(
            {
                "case_id": case_id,
                "condition": condition,
                "replicate_count": len(rows),
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
                    "Repeated behaviorally identical temperature-0 outputs are a reproducibility "
                    "diagnostic, not independent evidence."
                    if len(set(full_behavior)) == 1
                    else "Residual model nondeterminism observed; report the full distribution."
                ),
            }
        )
    return diagnostics
