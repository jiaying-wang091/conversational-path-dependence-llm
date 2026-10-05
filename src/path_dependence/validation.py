"""Protocol-level safeguards that run before any Phase 1C model execution."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .protocol import (
    CONDITIONS,
    FRESH_PROMPT_BASES,
    FRESH_UPDATES,
    NO_NEW_EVIDENCE_PROMPT_BASE,
    ORIGINAL_FACTS,
    RE_ANCHORED_PROMPT_BASE,
    RESPONSE_CONSTRAINTS,
    RESPONSE_SCHEMA,
    SELF_SUMMARY_PROMPT_BASE,
    SYSTEM_PROMPT,
    T0_PROMPT,
    TURNS,
    available_fact_ids,
    planned_user_turns,
    user_prompt,
)


class ProtocolValidationError(RuntimeError):
    """Raised when an immutable Phase 1C constraint is violated."""


EXPECTED_CONDITIONS = {
    "fresh_evidence",
    "no_new_evidence",
    "re_anchored",
    "self_summary",
}

EXPECTED_ORIGINAL_FACTS = {
    "C-F1": "Over ten weeks, Alex initiated two one-on-one outings with Jordan, while Jordan initiated one additional outing that Alex accepted.",
    "C-F2": "Alex remembered Jordan’s presentation, texted encouragement that morning, and brought several drink options to a group meeting, including Jordan’s preferred tea.",
    "C-F3": "After three group events, Alex continued texting Jordan for between twenty and forty minutes about group topics, personal updates, and possible future activities.",
    "C-F4": "Alex is warm with the group, checks in on several members, and has made occasional one-on-one plans with one other friend.",
    "C-F5": "Across the ten weeks, Alex has neither labeled the outings as dates nor described the relationship as platonic, and has not initiated explicitly romantic physical contact.",
    "C-F6": "When Jordan proposed another dinner, Alex postponed once because of a scheduling conflict and suggested trying the following week without selecting a specific day.",
}

EXPECTED_FRESH_UPDATES = {
    "C-U1": "At a group gathering in week eleven, Alex initiated a fifteen-minute one-on-one conversation with Jordan and also had a conversation of similar length with another group member.",
    "C-U2": "In week twelve, Alex sent Jordan an article related to an interest Jordan had mentioned and sent different interest-related articles to two other friends that week.",
    "C-U3": "In week thirteen, Alex accepted a group-outing invitation from Jordan and spent part of the event talking with Jordan, but did not propose a separate one-on-one plan.",
}


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def protocol_report() -> dict:
    errors: list[str] = []
    if set(CONDITIONS) != EXPECTED_CONDITIONS:
        errors.append("Protocol must contain exactly the four approved trajectory conditions")
    if ORIGINAL_FACTS != EXPECTED_ORIGINAL_FACTS:
        errors.append("Original fact set differs from the frozen Phase 1C protocol")
    if FRESH_UPDATES != EXPECTED_FRESH_UPDATES:
        errors.append("Fresh-evidence updates differ from the frozen Phase 1C protocol")
    if len(ORIGINAL_FACTS) != 6 or len(set(ORIGINAL_FACTS.values())) != 6:
        errors.append("The original record must contain exactly six unique facts")
    if len(FRESH_UPDATES) != 3 or len(set(FRESH_UPDATES.values())) != 3:
        errors.append("The fresh-evidence benchmark must contain exactly three unique updates")
    if "Do not treat earlier assistant wording as additional evidence." in RE_ANCHORED_PROMPT_BASE:
        errors.append("Re-anchored prompt contains the removed explicit prior-wording instruction")

    t0_hashes: set[str] = set()
    condition_reports: list[dict] = []
    for condition_id in CONDITIONS:
        turns = planned_user_turns(condition_id)
        if len(turns) != 4 or [item["turn"] for item in turns] != list(TURNS):
            errors.append(f"{condition_id} must contain exactly T0-T3")
        t0 = user_prompt(condition_id, 0)
        t0_hashes.add(_sha256(t0))
        for turn in TURNS:
            prompt = user_prompt(condition_id, turn)
            if RESPONSE_SCHEMA not in prompt or RESPONSE_CONSTRAINTS not in prompt:
                errors.append(f"{condition_id}/T{turn} lacks the shared response contract")
            expected_ids = set(ORIGINAL_FACTS)
            if condition_id == "fresh_evidence":
                expected_ids |= {f"C-U{i}" for i in range(1, turn + 1)}
            if available_fact_ids(condition_id, turn) != expected_ids:
                errors.append(f"{condition_id}/T{turn} fact availability differs")
        condition_reports.append(
            {
                "condition": condition_id,
                "t0_prompt_sha256": _sha256(t0),
                "turn_prompt_sha256": {
                    f"T{turn}": _sha256(user_prompt(condition_id, turn))
                    for turn in TURNS
                },
                "available_fact_ids_by_turn": {
                    f"T{turn}": sorted(available_fact_ids(condition_id, turn))
                    for turn in TURNS
                },
            }
        )

    if len(t0_hashes) != 1 or T0_PROMPT != user_prompt("fresh_evidence", 0):
        errors.append("T0 must be identical across all four conditions")

    for turn, base in FRESH_PROMPT_BASES.items():
        if EXPECTED_FRESH_UPDATES[f"C-U{turn}"] not in base:
            errors.append(f"Fresh T{turn} does not contain its exact frozen update")
    if "No new externally provided facts are available." not in NO_NEW_EVIDENCE_PROMPT_BASE:
        errors.append("No-new-evidence prompt changed")
    if "return to the six original facts C-F1 through C-F6" not in RE_ANCHORED_PROMPT_BASE:
        errors.append("Re-anchored prompt no longer manipulates renewed fact attention")
    if "immediately preceding assessment" not in SELF_SUMMARY_PROMPT_BASE:
        errors.append("Self-summary prompt changed")

    planned_trajectories = len(CONDITIONS) * 10
    planned_model_responses = planned_trajectories * len(TURNS)
    if planned_trajectories != 40 or planned_model_responses != 160:
        errors.append("Full protocol must contain 40 trajectories and 160 responses")

    canonical_original = "\n".join(
        f"{fact_id}: {ORIGINAL_FACTS[fact_id]}" for fact_id in sorted(ORIGINAL_FACTS)
    )
    canonical_updates = "\n".join(
        f"{fact_id}: {FRESH_UPDATES[fact_id]}" for fact_id in sorted(FRESH_UPDATES)
    )
    return {
        "valid": not errors,
        "errors": errors,
        "phase": "1C",
        "case_count": 1,
        "original_fact_count": len(ORIGINAL_FACTS),
        "fresh_update_count": len(FRESH_UPDATES),
        "condition_count": len(CONDITIONS),
        "turns_per_trajectory": len(TURNS),
        "planned_trajectories_at_ten_replicates": planned_trajectories,
        "planned_model_responses": planned_model_responses,
        "system_prompt_sha256": _sha256(SYSTEM_PROMPT),
        "original_fact_set_sha256": _sha256(canonical_original),
        "fresh_update_set_sha256": _sha256(canonical_updates),
        "shared_schema_sha256": _sha256(RESPONSE_SCHEMA),
        "conditions": condition_reports,
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
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return path
