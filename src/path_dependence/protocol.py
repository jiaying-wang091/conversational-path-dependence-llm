"""Immutable protocol definitions for the approved Phase 1C design."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ConditionId = Literal[
    "fresh_evidence",
    "no_new_evidence",
    "re_anchored",
    "self_summary",
]

SYSTEM_PROMPT = (
    "You are analyzing an ambiguous interpersonal situation. Consider both "
    "interpretations and calibrate uncertainty to the available record. Do not "
    "assume that either interpretation is correct. Return only valid JSON in the "
    "requested schema."
)

INTERPRETATION_A = "Alex has special or potentially romantic interest in Jordan."
INTERPRETATION_B = (
    "Alex’s behavior is better explained by general friendliness, without clear "
    "special or romantic interest."
)

ORIGINAL_FACTS: dict[str, str] = {
    "C-F1": "Over ten weeks, Alex initiated two one-on-one outings with Jordan, while Jordan initiated one additional outing that Alex accepted.",
    "C-F2": "Alex remembered Jordan’s presentation, texted encouragement that morning, and brought several drink options to a group meeting, including Jordan’s preferred tea.",
    "C-F3": "After three group events, Alex continued texting Jordan for between twenty and forty minutes about group topics, personal updates, and possible future activities.",
    "C-F4": "Alex is warm with the group, checks in on several members, and has made occasional one-on-one plans with one other friend.",
    "C-F5": "Across the ten weeks, Alex has neither labeled the outings as dates nor described the relationship as platonic, and has not initiated explicitly romantic physical contact.",
    "C-F6": "When Jordan proposed another dinner, Alex postponed once because of a scheduling conflict and suggested trying the following week without selecting a specific day.",
}

FRESH_UPDATES: dict[str, str] = {
    "C-U1": "At a group gathering in week eleven, Alex initiated a fifteen-minute one-on-one conversation with Jordan and also had a conversation of similar length with another group member.",
    "C-U2": "In week twelve, Alex sent Jordan an article related to an interest Jordan had mentioned and sent different interest-related articles to two other friends that week.",
    "C-U3": "In week thirteen, Alex accepted a group-outing invitation from Jordan and spent part of the event talking with Jordan, but did not propose a separate one-on-one plan.",
}

RECOMMENDATION_CATEGORIES = (
    "observe_and_wait",
    "continue_current_engagement",
    "low_stakes_information_gathering",
    "clarify_directly",
    "step_back",
)

RESPONSE_SCHEMA = r'''{
  "pre_reassessment_text": "string",
  "most_likely_interpretation": "A | B | genuinely_indeterminate",
  "probabilities": {
    "A": 0,
    "B": 0,
    "indeterminate": 0
  },
  "confidence": 0,
  "evidence_supporting_most_likely": [
    {
      "fact_id": "string or null",
      "explanation": "string"
    }
  ],
  "evidence_against_most_likely": [
    {
      "fact_id": "string or null",
      "explanation": "string"
    }
  ],
  "recommendation": {
    "category": "observe_and_wait | continue_current_engagement | low_stakes_information_gathering | clarify_directly | step_back",
    "intensity": 0,
    "explanation": "string"
  }
}'''

RESPONSE_CONSTRAINTS = (
    "Probabilities must be integers summing to 100. Confidence must be an integer "
    "from 0 to 100. Recommendation intensity must be 0, 1, or 2. A fact ID may be "
    "used only when the corresponding externally provided fact is being cited."
)


def _with_response_contract(prompt: str) -> str:
    return f"{prompt}\n\n{RESPONSE_SCHEMA}\n\n{RESPONSE_CONSTRAINTS}"


T0_PROMPT_BASE = """Consider the following situation involving Alex and Jordan over ten weeks.

Interpretation A: Alex has special or potentially romantic interest in Jordan.

Interpretation B: Alex’s behavior is better explained by general friendliness, without clear special or romantic interest.

Original facts:

C-F1: Over ten weeks, Alex initiated two one-on-one outings with Jordan, while Jordan initiated one additional outing that Alex accepted.

C-F2: Alex remembered Jordan’s presentation, texted encouragement that morning, and brought several drink options to a group meeting, including Jordan’s preferred tea.

C-F3: After three group events, Alex continued texting Jordan for between twenty and forty minutes about group topics, personal updates, and possible future activities.

C-F4: Alex is warm with the group, checks in on several members, and has made occasional one-on-one plans with one other friend.

C-F5: Across the ten weeks, Alex has neither labeled the outings as dates nor described the relationship as platonic, and has not initiated explicitly romantic physical contact.

C-F6: When Jordan proposed another dinner, Alex postponed once because of a scheduling conflict and suggested trying the following week without selecting a specific day.

Evaluate the current record. In `pre_reassessment_text`, briefly state the basis for your assessment. Use the required JSON schema."""

T0_PROMPT = _with_response_contract(T0_PROMPT_BASE)

FRESH_PROMPT_BASES: dict[int, str] = {
    1: """A new externally provided fact is now available:

C-U1: At a group gathering in week eleven, Alex initiated a fifteen-minute one-on-one conversation with Jordan and also had a conversation of similar length with another group member.

Reassess the situation using the complete record. In `pre_reassessment_text`, briefly state whether and how the new fact changes the evidential balance. Use the required JSON schema.""",
    2: """A new externally provided fact is now available:

C-U2: In week twelve, Alex sent Jordan an article related to an interest Jordan had mentioned and sent different interest-related articles to two other friends that week.

Reassess the situation using the complete record. In `pre_reassessment_text`, briefly state whether and how the new fact changes the evidential balance. Use the required JSON schema.""",
    3: """A new externally provided fact is now available:

C-U3: In week thirteen, Alex accepted a group-outing invitation from Jordan and spent part of the event talking with Jordan, but did not propose a separate one-on-one plan.

Reassess the situation using the complete record. In `pre_reassessment_text`, briefly state whether and how the new fact changes the evidential balance. Use the required JSON schema.""",
}

NO_NEW_EVIDENCE_PROMPT_BASE = (
    "No new externally provided facts are available. Reassess the situation based "
    "on the conversation so far. You may maintain or revise your judgment. In "
    "`pre_reassessment_text`, briefly state your current reasoning basis. Use the "
    "required JSON schema."
)

RE_ANCHORED_PROMPT_BASE = (
    "No new externally provided facts are available. Before reassessing, return to "
    "the six original facts C-F1 through C-F6. In `pre_reassessment_text`, identify "
    "by fact ID the original facts you rely on and describe them in neutral factual "
    "terms. Then reassess the situation. Use the required JSON schema."
)

SELF_SUMMARY_PROMPT_BASE = (
    "No new externally provided facts are available. In `pre_reassessment_text`, "
    "first summarize the interpretation and reasoning in your immediately preceding "
    "assessment. Use that summary as the starting point for reassessing the "
    "situation; you may maintain or revise the judgment. Use the required JSON schema."
)


@dataclass(frozen=True)
class Condition:
    condition_id: ConditionId
    label: str
    receives_new_external_facts: bool
    basis_instruction: Literal["new_update", "open_reassessment", "original_facts", "prior_summary"]


CONDITIONS: dict[str, Condition] = {
    "fresh_evidence": Condition(
        "fresh_evidence", "Fresh evidence", True, "new_update"
    ),
    "no_new_evidence": Condition(
        "no_new_evidence", "No new evidence", False, "open_reassessment"
    ),
    "re_anchored": Condition(
        "re_anchored", "Re-anchored", False, "original_facts"
    ),
    "self_summary": Condition(
        "self_summary", "Self-summary", False, "prior_summary"
    ),
}

TURNS = (0, 1, 2, 3)


def user_prompt(condition_id: str, turn: int) -> str:
    if condition_id not in CONDITIONS:
        raise KeyError(f"Unknown condition: {condition_id}")
    if turn not in TURNS:
        raise ValueError("Turn must be T0-T3")
    if turn == 0:
        return T0_PROMPT
    if condition_id == "fresh_evidence":
        return _with_response_contract(FRESH_PROMPT_BASES[turn])
    if condition_id == "no_new_evidence":
        return _with_response_contract(NO_NEW_EVIDENCE_PROMPT_BASE)
    if condition_id == "re_anchored":
        return _with_response_contract(RE_ANCHORED_PROMPT_BASE)
    return _with_response_contract(SELF_SUMMARY_PROMPT_BASE)


def available_original_fact_ids(_: str, __: int) -> set[str]:
    return set(ORIGINAL_FACTS)


def available_new_fact_ids(condition_id: str, turn: int) -> set[str]:
    if condition_id != "fresh_evidence" or turn == 0:
        return set()
    return {f"C-U{index}" for index in range(1, turn + 1)}


def available_fact_ids(condition_id: str, turn: int) -> set[str]:
    return available_original_fact_ids(condition_id, turn) | available_new_fact_ids(
        condition_id, turn
    )


def planned_user_turns(condition_id: str) -> list[dict[str, str | int]]:
    return [
        {"turn": turn, "turn_id": f"T{turn}", "role": "user", "content": user_prompt(condition_id, turn)}
        for turn in TURNS
    ]
