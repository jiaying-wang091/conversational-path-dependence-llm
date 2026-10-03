"""Protocol-level safeguards that run before any model execution."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from .protocol import (
    CASES,
    CONDITIONS,
    FROZEN_DIAGNOSTICITY,
    ORDERS,
    evidence_batches,
    initial_transcript,
)


class ProtocolValidationError(RuntimeError):
    """Raised when an immutable experimental constraint is violated."""


EXPECTED_VARIANTS = {"LA", "LB", "MA", "MB", "HA", "HB"}
EXPECTED_CONDITIONS = {"neutral", "negative_first", "positive_first", "commit_a", "commit_b"}
EXPECTED_DIAGNOSTICITY = {
    "LA": (3, 3, 2, -1, -1, -1),
    "LB": (1, 1, 1, -2, -3, -3),
    "MA": (2, 2, 2, -1, -1, -2),
    "MB": (2, 1, 1, -2, -2, -2),
    "HA": (2, 1, 1, -1, -1, -1),
    "HB": (1, 1, 1, -2, -1, -1),
}
EXPECTED_PAIR_TOTALS = {
    "low": {"net_abs": 5, "total_abs": 11},
    "medium": {"net_abs": 2, "total_abs": 10},
    "high": {"net_abs": 1, "total_abs": 7},
}


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def protocol_report() -> dict:
    errors: list[str] = []
    cell_reports: list[dict] = []

    if set(CASES) != EXPECTED_VARIANTS:
        errors.append("Protocol must contain exactly LA, LB, MA, MB, HA, and HB")
    if set(CONDITIONS) != EXPECTED_CONDITIONS:
        errors.append("Protocol must contain exactly five approved conditions")
    if CONDITIONS["commit_a"].order_id != "positive_first":
        errors.append("commit_a must match positive_first fact order")
    if CONDITIONS["commit_b"].order_id != "negative_first":
        errors.append("commit_b must match negative_first fact order")
    if FROZEN_DIAGNOSTICITY != EXPECTED_DIAGNOSTICITY:
        errors.append("Frozen diagnosticity mapping differs from the approved protocol")

    diagnosticity_reports: list[dict] = []
    for variant_id, variant in CASES.items():
        expected_ids = {f"{variant_id}-F{i}" for i in range(1, 7)}
        if set(variant.facts) != expected_ids:
            errors.append(f"{variant_id} fact IDs differ from F1-F6")
        if len(variant.facts) != 6 or len(set(variant.facts.values())) != 6:
            errors.append(f"{variant_id} must contain exactly six unique immutable facts")
        if variant.diagnosticity_scores != EXPECTED_DIAGNOSTICITY.get(variant_id):
            errors.append(f"{variant_id} diagnosticity scores differ from the frozen protocol")
        if any(score <= 0 for score in variant.diagnosticity_scores[:3]):
            errors.append(f"{variant_id} F1-F3 must have positive diagnosticity scores")
        if any(score >= 0 for score in variant.diagnosticity_scores[3:]):
            errors.append(f"{variant_id} F4-F6 must have negative diagnosticity scores")

        net_score = sum(variant.diagnosticity_scores)
        total_abs = sum(abs(score) for score in variant.diagnosticity_scores)
        expected_sign = 1 if variant.baseline_polarity == "A" else -1
        if net_score * expected_sign <= 0:
            errors.append(f"{variant_id} net score has the wrong baseline-polarity direction")
        diagnosticity_reports.append(
            {
                "variant_id": variant_id,
                "ambiguity_level": variant.ambiguity_level,
                "baseline_polarity": variant.baseline_polarity,
                "scores": list(variant.diagnosticity_scores),
                "net_score": net_score,
                "absolute_net_score": abs(net_score),
                "total_absolute_evidence_strength": total_abs,
            }
        )

        reference_multiset = Counter(variant.facts.values())
        for condition_id in CONDITIONS:
            batches = evidence_batches(variant_id, condition_id)
            transcript = initial_transcript(variant_id, condition_id)
            observed_texts: list[str] = []
            observed_ids: list[str] = []
            for batch in batches:
                for line in batch.split("\n\n"):
                    fid, text = line.split(": ", 1)
                    observed_ids.append(fid)
                    observed_texts.append(text)

            exact_complete = Counter(observed_texts) == reference_multiset
            ids_once = Counter(observed_ids) == Counter(expected_ids)
            if not exact_complete:
                errors.append(
                    f"{variant_id}/{condition_id} does not contain the verbatim complete fact set"
                )
            if not ids_once:
                errors.append(f"{variant_id}/{condition_id} does not contain each fact ID once")
            if len(transcript) != 9:
                errors.append(f"{variant_id}/{condition_id} transcript must contain 9 messages")
            if [message["role"] for message in transcript] != [
                "system", "user", "user", "assistant", "user", "assistant", "user", "assistant", "user"
            ]:
                errors.append(f"{variant_id}/{condition_id} role sequence changed")

            fact_payload = "\n".join(
                f"{fid}: {variant.facts[fid]}" for fid in sorted(expected_ids)
            )
            cell_reports.append(
                {
                    "variant_id": variant_id,
                    "condition_id": condition_id,
                    "order_id": CONDITIONS[condition_id].order_id,
                    "commitment": CONDITIONS[condition_id].commitment,
                    "fact_ids_in_order": observed_ids,
                    "all_fact_ids_once": ids_once,
                    "verbatim_complete_fact_set": exact_complete,
                    "canonical_fact_set_sha256": _sha256(fact_payload),
                    "transcript_sha256": _sha256(
                        json.dumps(transcript, ensure_ascii=False, sort_keys=True)
                    ),
                }
            )

    pair_reports: list[dict] = []
    pair_ids = {"low": ("LA", "LB"), "medium": ("MA", "MB"), "high": ("HA", "HB")}
    for level, ids in pair_ids.items():
        left, right = (CASES[variant_id] for variant_id in ids)
        left_net = sum(left.diagnosticity_scores)
        right_net = sum(right.diagnosticity_scores)
        left_total = sum(abs(score) for score in left.diagnosticity_scores)
        right_total = sum(abs(score) for score in right.diagnosticity_scores)
        expected = EXPECTED_PAIR_TOTALS[level]
        symmetric = (
            left_net == -right_net
            and abs(left_net) == expected["net_abs"]
            and left_total == right_total == expected["total_abs"]
        )
        if not symmetric:
            errors.append(f"{level} A/B pair violates frozen diagnosticity symmetry")
        pair_reports.append(
            {
                "ambiguity_level": level,
                "a_variant": ids[0],
                "b_variant": ids[1],
                "a_net_score": left_net,
                "b_net_score": right_net,
                "absolute_net_score": abs(left_net),
                "total_absolute_evidence_strength": left_total,
                "symmetric": symmetric,
            }
        )

    for variant_id in CASES:
        if evidence_batches(variant_id, "commit_a") != evidence_batches(
            variant_id, "positive_first"
        ):
            errors.append(f"{variant_id} commit_a differs from positive_first order")
        if evidence_batches(variant_id, "commit_b") != evidence_batches(
            variant_id, "negative_first"
        ):
            errors.append(f"{variant_id} commit_b differs from negative_first order")

    expected_runs = len(cell_reports) * 5
    if expected_runs != 150:
        errors.append(f"Full protocol must generate exactly 150 runs, observed {expected_runs}")

    return {
        "valid": not errors,
        "errors": errors,
        "phase": "1B",
        "variant_count": len(CASES),
        "condition_count": len(CONDITIONS),
        "cell_count": len(cell_reports),
        "expected_runs_at_five_replicates": expected_runs,
        "conditions": {key: asdict(value) for key, value in CONDITIONS.items()},
        "orders": {key: value for key, value in ORDERS.items()},
        "diagnosticity": diagnosticity_reports,
        "polarity_pair_symmetry": pair_reports,
        "cells": cell_reports,
    }


def assert_protocol_valid() -> dict:
    report = protocol_report()
    if not report["valid"]:
        raise ProtocolValidationError("; ".join(report["errors"]))
    return report


def write_validation_report(output_dir: Path) -> Path:
    report = assert_protocol_valid()
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "protocol_validation.json"
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path
