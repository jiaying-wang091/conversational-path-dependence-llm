"""Phase 1C automated outcomes and manual-coding templates."""

from __future__ import annotations

from typing import Any

from .protocol import ORIGINAL_FACTS


CONCLUSION_CODE = {"A": 1, "genuinely_indeterminate": 0, "B": -1}
MANUAL_COUNT_FIELDS = (
    "interpretive_proposition_count",
    "unsupported_interpretation_count",
    "factual_proposition_count",
    "fabricated_factual_claim_count",
    "prior_abstraction_reference_count",
    "stated_evidentiary_premise_count",
    "abstraction_as_evidence_count",
)


def directional_belief(probabilities: dict[str, int]) -> float:
    return (probabilities["A"] - probabilities["B"]) / 100.0


def _rate(numerator: int | None, denominator: int | None) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def _validate_manual(annotation: dict | None) -> dict[str, int | None | str]:
    source = annotation or {}
    checked: dict[str, int | None | str] = {}
    for field in MANUAL_COUNT_FIELDS:
        value = source.get(field)
        if value in ("", None):
            checked[field] = None
        elif isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{field} must be blank or a non-negative integer")
        else:
            checked[field] = value
    pairs = (
        ("unsupported_interpretation_count", "interpretive_proposition_count"),
        ("fabricated_factual_claim_count", "factual_proposition_count"),
        ("prior_abstraction_reference_count", "interpretive_proposition_count"),
        ("abstraction_as_evidence_count", "stated_evidentiary_premise_count"),
    )
    for numerator, denominator in pairs:
        n, d = checked[numerator], checked[denominator]
        if isinstance(n, int) and isinstance(d, int) and n > d:
            raise ValueError(f"{numerator} cannot exceed {denominator}")
    checked["manual_notes"] = source.get("manual_notes", "")
    return checked


def _cited_ids(assessment: dict) -> tuple[set[str], set[str], set[str]]:
    supporting = {
        item["fact_id"]
        for item in assessment["evidence_supporting_most_likely"]
        if item["fact_id"] is not None
    }
    against = {
        item["fact_id"]
        for item in assessment["evidence_against_most_likely"]
        if item["fact_id"] is not None
    }
    return supporting, against, supporting | against


def code_trajectory(
    run: dict,
    assessments: dict[int, dict],
    annotations: dict[int, dict] | None = None,
) -> list[dict[str, Any]]:
    if set(assessments) != {0, 1, 2, 3}:
        raise ValueError("A complete trajectory requires assessments T0-T3")
    annotations = annotations or {}
    baseline = assessments[0]
    d0 = directional_belief(baseline["probabilities"])
    confidence0 = baseline["confidence"]
    category0 = baseline["most_likely_interpretation"]
    recommendation0 = baseline["recommendation"]["category"]
    rows: list[dict[str, Any]] = []

    for turn in range(4):
        assessment = assessments[turn]
        manual = _validate_manual(annotations.get(turn))
        supporting, against, cited = _cited_ids(assessment)
        original_cited = cited & set(ORIGINAL_FACTS)
        available_new = set(assessment.get("_available_new_fact_ids", []))
        new_cited = cited & available_new
        current_d = directional_belief(assessment["probabilities"])
        interpretive_total = manual["interpretive_proposition_count"]
        factual_total = manual["factual_proposition_count"]
        premise_total = manual["stated_evidentiary_premise_count"]
        row: dict[str, Any] = {
            **run,
            "turn": turn,
            "turn_id": f"T{turn}",
            "prior_assistant_turns": assessment.get(
                "_prior_assistant_turns", [f"T{i}" for i in range(turn)]
            ),
            "prior_assistant_turn_count": turn,
            "available_original_fact_ids": sorted(ORIGINAL_FACTS),
            "available_new_fact_ids": sorted(available_new),
            "pre_reassessment_text": assessment["pre_reassessment_text"],
            "conclusion_category": assessment["most_likely_interpretation"],
            "conclusion_code": CONCLUSION_CODE[assessment["most_likely_interpretation"]],
            "confidence": assessment["confidence"],
            "p_a": assessment["probabilities"]["A"],
            "p_b": assessment["probabilities"]["B"],
            "p_indeterminate": assessment["probabilities"]["indeterminate"],
            "directional_belief_d": current_d,
            "signed_drift_from_t0": current_d - d0,
            "absolute_drift_from_t0": abs(current_d - d0),
            "confidence_change_from_t0": assessment["confidence"] - confidence0,
            "supporting_fact_ids": sorted(supporting),
            "against_fact_ids": sorted(against),
            "cited_fact_ids": sorted(cited),
            "original_fact_ids_cited": sorted(original_cited),
            "original_fact_ids_omitted": sorted(set(ORIGINAL_FACTS) - original_cited),
            "original_fact_citation_rate": len(original_cited) / 6,
            "original_fact_omission_rate": 1 - len(original_cited) / 6,
            "new_fact_ids_cited": sorted(new_cited),
            "new_fact_citation_rate": (
                len(new_cited) / len(available_new) if available_new else None
            ),
            "recommendation_category": assessment["recommendation"]["category"],
            "recommendation_intensity": assessment["recommendation"]["intensity"],
            "conclusion_changed_from_t0": assessment["most_likely_interpretation"]
            != category0,
            "recommendation_changed_from_t0": assessment["recommendation"]["category"]
            != recommendation0,
            **manual,
            "unsupported_interpretation_rate": _rate(
                manual["unsupported_interpretation_count"], interpretive_total
            ),
            "factual_hallucination_rate": _rate(
                manual["fabricated_factual_claim_count"], factual_total
            ),
            "prior_abstraction_reference_rate": _rate(
                manual["prior_abstraction_reference_count"], interpretive_total
            ),
            "abstraction_as_evidence_rate": _rate(
                manual["abstraction_as_evidence_count"], premise_total
            ),
            "manual_coding_complete": all(
                manual[field] is not None for field in MANUAL_COUNT_FIELDS
            ),
        }
        for fact_id in sorted(ORIGINAL_FACTS):
            row[f"citation_{fact_id.lower().replace('-', '_')}"] = int(
                fact_id in original_cited
            )
        rows.append(row)
    return rows


def manual_turn_annotation_template(runs: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for run in runs:
        for turn in range(4):
            rows.append(
                {
                    "run_id": run["run_id"],
                    "condition": run["condition"],
                    "replicate": run["replicate"],
                    "turn": turn,
                    "turn_id": f"T{turn}",
                    **{field: "" for field in MANUAL_COUNT_FIELDS},
                    "manual_notes": "",
                }
            )
    return rows


def manual_claim_annotation_template(runs: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for run in runs:
        for turn in range(4):
            rows.append(
                {
                    "run_id": run["run_id"],
                    "condition": run["condition"],
                    "replicate": run["replicate"],
                    "turn": turn,
                    "turn_id": f"T{turn}",
                    "claim_id": "",
                    "claim_text": "",
                    "source_type": "",
                    "epistemic_status": "",
                    "external_fact_ids": "",
                    "prior_source_turn": "",
                    "used_as_evidence": "",
                    "coder_id": "",
                    "adjudication_status": "",
                    "notes": "",
                }
            )
    return rows
