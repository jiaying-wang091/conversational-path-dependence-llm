"""Protocol-level safeguards that run before any model execution."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from .protocol import CASES, CONDITIONS, ORDERS, evidence_batches, initial_transcript


class ProtocolValidationError(RuntimeError):
    """Raised when an immutable experimental constraint is violated."""


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def protocol_report() -> dict:
    errors: list[str] = []
    cell_reports: list[dict] = []

    if set(CASES) != {"C1", "C2", "C3"}:
        errors.append("Protocol must contain exactly C1, C2, and C3")
    if set(CONDITIONS) != {"neutral", "negative_first", "positive_first", "commit_a", "commit_b"}:
        errors.append("Protocol must contain exactly five approved conditions")
    if CONDITIONS["commit_a"].order_id != "positive_first":
        errors.append("commit_a must match positive_first fact order")
    if CONDITIONS["commit_b"].order_id != "negative_first":
        errors.append("commit_b must match negative_first fact order")

    for case_id, case in CASES.items():
        expected_ids = {f"{case_id}-F{i}" for i in range(1, 7)}
        if set(case.facts) != expected_ids:
            errors.append(f"{case_id} fact IDs differ from F1-F6")
        if len(set(case.facts.values())) != 6:
            errors.append(f"{case_id} contains duplicate fact text")

        reference_multiset = Counter(case.facts.values())
        for condition_id in CONDITIONS:
            batches = evidence_batches(case_id, condition_id)
            transcript = initial_transcript(case_id, condition_id)
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
                errors.append(f"{case_id}/{condition_id} does not contain the verbatim complete fact set")
            if not ids_once:
                errors.append(f"{case_id}/{condition_id} does not contain each fact ID exactly once")
            if len(transcript) != 9:
                errors.append(f"{case_id}/{condition_id} transcript must contain 9 messages")
            if [m["role"] for m in transcript] != [
                "system", "user", "user", "assistant", "user", "assistant", "user", "assistant", "user"
            ]:
                errors.append(f"{case_id}/{condition_id} role sequence changed")

            fact_payload = "\n".join(f"{fid}: {case.facts[fid]}" for fid in sorted(expected_ids))
            cell_reports.append(
                {
                    "case_id": case_id,
                    "condition_id": condition_id,
                    "order_id": CONDITIONS[condition_id].order_id,
                    "commitment": CONDITIONS[condition_id].commitment,
                    "fact_ids_in_order": observed_ids,
                    "all_fact_ids_once": ids_once,
                    "verbatim_complete_fact_set": exact_complete,
                    "canonical_fact_set_sha256": _sha256(fact_payload),
                    "transcript_sha256": _sha256(json.dumps(transcript, ensure_ascii=False, sort_keys=True)),
                }
            )

    # Direct order matching is checked in addition to the declarative mapping.
    for case_id in CASES:
        if evidence_batches(case_id, "commit_a") != evidence_batches(case_id, "positive_first"):
            errors.append(f"{case_id} commit_a differs from positive_first order")
        if evidence_batches(case_id, "commit_b") != evidence_batches(case_id, "negative_first"):
            errors.append(f"{case_id} commit_b differs from negative_first order")

    return {
        "valid": not errors,
        "errors": errors,
        "case_count": len(CASES),
        "condition_count": len(CONDITIONS),
        "cell_count": len(cell_reports),
        "expected_runs_at_five_replicates": len(cell_reports) * 5,
        "conditions": {key: asdict(value) for key, value in CONDITIONS.items()},
        "orders": {key: value for key, value in ORDERS.items()},
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
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
