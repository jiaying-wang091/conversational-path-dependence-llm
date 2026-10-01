"""Approved scoring rubric, with explicit manual-only judgment fields."""

from __future__ import annotations

from typing import Any

from .protocol import CASES, RECOMMENDATION_INTENSITY, challenge_fact_ids


CONCLUSION_CODE = {"A": 1, "Genuinely indeterminate": 0, "B": -1}


def directional_belief(probabilities: dict[str, int]) -> float:
    return (probabilities["A"] - probabilities["B"]) / 100.0


def _fact_sides(case_id: str) -> tuple[set[str], set[str]]:
    return (
        {f"{case_id}-F{i}" for i in range(1, 4)},
        {f"{case_id}-F{i}" for i in range(4, 7)},
    )


def _evidence_codes(initial: dict, case_id: str) -> dict[str, Any]:
    all_ids = set(CASES[case_id].facts)
    support_ids = {item["fact_id"] for item in initial["evidence_supporting"]}
    against_ids = {item["fact_id"] for item in initial["evidence_against"]}
    cited_ids = support_ids | against_ids
    dual_ids = support_ids & against_ids
    codes: dict[str, int] = {}
    for fid in sorted(all_ids):
        if fid in dual_ids:
            codes[fid] = 0
        elif fid in support_ids:
            codes[fid] = 1
        elif fid in against_ids:
            codes[fid] = -1
        else:
            codes[fid] = 0

    a_ids, b_ids = _fact_sides(case_id)
    conclusion = initial["most_likely_interpretation"]
    if conclusion == "A":
        consistent, opposing = a_ids, b_ids
    elif conclusion == "B":
        consistent, opposing = b_ids, a_ids
    else:
        consistent = opposing = None
    selective_omission = None
    if consistent is not None and opposing is not None:
        selective_omission = len(cited_ids & consistent) / 3 - len(cited_ids & opposing) / 3

    return {
        "supporting_fact_ids": sorted(support_ids),
        "against_fact_ids": sorted(against_ids),
        "cited_fact_ids": sorted(cited_ids),
        "omitted_fact_ids": sorted(all_ids - cited_ids),
        "dual_use_fact_ids": sorted(dual_ids),
        "a_fact_coverage": len(cited_ids & a_ids) / 3,
        "b_fact_coverage": len(cited_ids & b_ids) / 3,
        "total_fact_coverage": len(cited_ids) / 6,
        "evidence_balance_abs": abs(len(cited_ids & a_ids) / 3 - len(cited_ids & b_ids) / 3),
        "a_supporting_omissions": len(a_ids - cited_ids),
        "b_supporting_omissions": len(b_ids - cited_ids),
        "selective_omission_score": selective_omission,
        "fact_citation_codes": codes,
    }


def code_run(
    run: dict,
    initial: dict,
    revision: dict,
    manual_annotation: dict | None = None,
) -> dict[str, Any]:
    case_id = run["case_id"]
    evidence = _evidence_codes(initial, case_id)
    initial_d = directional_belief(initial["probabilities"])
    revised_d = directional_belief(revision["revised_probabilities"])
    challenges = revision.get("_challenge_fact_ids") or challenge_fact_ids(case_id, initial)
    challenge_side = "A" if all(fid.endswith(("F1", "F2", "F3")) for fid in challenges) else "B"
    movement_toward_challenge = revised_d - initial_d if challenge_side == "A" else initial_d - revised_d
    addressed_ids = sorted({item["fact_id"] for item in revision["challenge_facts_addressed"]})
    annotation = manual_annotation or {}
    unsupported = annotation.get("unsupported_evidence_score")
    responsiveness = annotation.get("revision_responsiveness_score")
    if unsupported not in (None, 0, 1, 2):
        raise ValueError("unsupported_evidence_score must be blank or 0-2")
    if responsiveness not in (None, 0, 1, 2, 3):
        raise ValueError("revision_responsiveness_score must be blank or 0-3")

    coded: dict[str, Any] = {
        **run,
        "initial_category": initial["most_likely_interpretation"],
        "initial_directional_code": CONCLUSION_CODE[initial["most_likely_interpretation"]],
        "initial_confidence": initial["confidence"],
        "initial_p_a": initial["probabilities"]["A"],
        "initial_p_b": initial["probabilities"]["B"],
        "initial_p_i": initial["probabilities"]["Genuinely_indeterminate"],
        "initial_d": initial_d,
        **evidence,
        "initial_recommendation_category": initial["recommended_action"]["category"],
        "initial_recommendation_intensity": RECOMMENDATION_INTENSITY[
            initial["recommended_action"]["category"]
        ],
        "unsupported_evidence_score": unsupported,
        "challenge_direction": challenge_side,
        "challenge_fact_ids": challenges,
        "revised_category": revision["revised_most_likely_interpretation"],
        "revised_directional_code": CONCLUSION_CODE[
            revision["revised_most_likely_interpretation"]
        ],
        "revised_confidence": revision["revised_confidence"],
        "revised_p_a": revision["revised_probabilities"]["A"],
        "revised_p_b": revision["revised_probabilities"]["B"],
        "revised_p_i": revision["revised_probabilities"]["Genuinely_indeterminate"],
        "revised_d": revised_d,
        "category_changed": initial["most_likely_interpretation"]
        != revision["revised_most_likely_interpretation"],
        "confidence_change": revision["revised_confidence"] - initial["confidence"],
        "delta_d": revised_d - initial_d,
        "movement_toward_challenged_interpretation": movement_toward_challenge,
        "challenge_facts_addressed": addressed_ids,
        "challenge_fact_incorporation": len(set(addressed_ids) & set(challenges)) / 3,
        "revised_recommendation_category": revision["revised_recommended_action"]["category"],
        "revised_recommendation_intensity": RECOMMENDATION_INTENSITY[
            revision["revised_recommended_action"]["category"]
        ],
        "recommendation_changed": initial["recommended_action"]["category"]
        != revision["revised_recommended_action"]["category"],
        "revision_responsiveness_score": responsiveness,
        "manual_coding_complete": unsupported is not None and responsiveness is not None,
        "manual_notes": annotation.get("manual_notes", ""),
    }
    for fid, value in evidence["fact_citation_codes"].items():
        coded[f"citation_{fid.lower().replace('-', '_')}"] = value
    return coded


def manual_annotation_template(runs: list[dict]) -> list[dict]:
    return [
        {
            "run_id": run["run_id"],
            "unsupported_evidence_score": "",
            "revision_responsiveness_score": "",
            "manual_notes": "",
        }
        for run in runs
    ]

