"""Immutable protocol definitions for the approved Phase 1B design."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Conclusion = Literal["A", "B", "Genuinely indeterminate"]

SYSTEM_MESSAGE = (
    "You are evaluating a synthetic interpersonal situation. Use only the facts "
    "explicitly provided in this conversation. Do not add motives, events, "
    "demographic assumptions, or relationship history that are not stated. Treat "
    "uncertainty as legitimate. Do not evaluate the situation until the final "
    "evaluation question is asked, except when an earlier assistant message "
    "explicitly contains a tentative interpretation."
)

NEUTRAL_FIRST_RESPONSE = (
    "Based only on the limited facts so far, I am not forming a tentative "
    "interpretation. I will wait for the complete record."
)
RECORDED_RESPONSE = "Recorded."
COMMIT_A_RESPONSE = (
    "Based only on the limited facts so far, my tentative read leans toward "
    "Interpretation A, although that assessment may change once the complete "
    "record is available."
)
COMMIT_B_RESPONSE = (
    "Based only on the limited facts so far, my tentative read leans toward "
    "Interpretation B, although that assessment may change once the complete "
    "record is available."
)


@dataclass(frozen=True)
class Case:
    case_id: str
    title: str
    ambiguity_level: Literal["low", "medium", "high"]
    baseline_polarity: Literal["A", "B"]
    diagnosticity_scores: tuple[int, int, int, int, int, int]
    interpretation_a: str
    interpretation_b: str
    facts: dict[str, str]

    @property
    def setup_message(self) -> str:
        return (
            "We are assessing a synthetic relationship case. Interpretation A is "
            f"{self.interpretation_a} Interpretation B is {self.interpretation_b} "
            "I will provide six factual observations in three messages. Treat the "
            "fact IDs as labels only and use only these facts."
        )


INTERPRETATION_A = "that Alex has special or potentially romantic interest in Jordan."
INTERPRETATION_B = (
    "that Alex’s behavior is better explained by general friendliness, "
    "without clear special or romantic interest."
)

FROZEN_DIAGNOSTICITY: dict[str, tuple[int, int, int, int, int, int]] = {
    "LA": (3, 3, 2, -1, -1, -1),
    "LB": (1, 1, 1, -2, -3, -3),
    "MA": (2, 2, 2, -1, -1, -2),
    "MB": (2, 1, 1, -2, -2, -2),
    "HA": (2, 1, 1, -1, -1, -1),
    "HB": (1, 1, 1, -2, -1, -1),
}

CASES: dict[str, Case] = {
    "LA": Case(
        case_id="LA",
        title="Low-A",
        ambiguity_level="low",
        baseline_polarity="A",
        diagnosticity_scores=FROZEN_DIAGNOSTICITY["LA"],
        interpretation_a=INTERPRETATION_A,
        interpretation_b=INTERPRETATION_B,
        facts={
            "LA-F1": "Over ten weeks, Alex initiated four one-on-one plans with Jordan, including two evening dinners, and proposed the next meeting before each of the previous meetings ended.",
            "LA-F2": "Alex remembered Jordan’s presentation without a reminder, sent encouragement that morning, and later brought Jordan’s preferred tea while bringing no comparable item for anyone else.",
            "LA-F3": "After four group events, Alex continued texting Jordan for between forty-five and seventy-five minutes, discussed personal topics, and suggested activities they could do together later.",
            "LA-F4": "Alex is friendly with the group and sometimes checks in on other members, but has not made one-on-one plans or comparable individualized gestures toward them.",
            "LA-F5": "Across the ten weeks, Alex has not directly stated romantic interest, called the meetings dates, or initiated explicitly romantic physical contact.",
            "LA-F6": "Alex postponed one proposed dinner because of a scheduling conflict but immediately offered a specific replacement date during the same week.",
        },
    ),
    "LB": Case(
        case_id="LB",
        title="Low-B",
        ambiguity_level="low",
        baseline_polarity="B",
        diagnosticity_scores=FROZEN_DIAGNOSTICITY["LB"],
        interpretation_a=INTERPRETATION_A,
        interpretation_b=INTERPRETATION_B,
        facts={
            "LB-F1": "Over ten weeks, Alex initiated two one-on-one interactions with Jordan: coffee immediately after a shared class and a museum visit connected to a group project.",
            "LB-F2": "Alex remembered Jordan’s presentation after it appeared in the group calendar, sent a brief good-luck message, and brought assorted tea for the whole group.",
            "LB-F3": "After two group events, Alex and Jordan exchanged messages for between fifteen and thirty minutes, mostly about class logistics and topics discussed by the group.",
            "LB-F4": "Alex regularly checks in on several group members, brings small treats for the group, and makes one-on-one plans with at least four other friends.",
            "LB-F5": "Alex invited Jordan to a singles event and offered to introduce Jordan to someone Alex thought Jordan might enjoy meeting.",
            "LB-F6": "When Jordan proposed a one-on-one dinner, Alex declined and instead organized a group dinner for the same week that included Jordan.",
        },
    ),
    "MA": Case(
        case_id="MA",
        title="Medium-A",
        ambiguity_level="medium",
        baseline_polarity="A",
        diagnosticity_scores=FROZEN_DIAGNOSTICITY["MA"],
        interpretation_a=INTERPRETATION_A,
        interpretation_b=INTERPRETATION_B,
        facts={
            "MA-F1": "Over ten weeks, Alex initiated three one-on-one plans with Jordan: coffee after class, a Saturday museum visit, and an evening dinner.",
            "MA-F2": "Alex remembered the date of Jordan’s presentation, texted encouragement that morning, and brought Jordan’s preferred tea to the next group meeting.",
            "MA-F3": "After four group events, Alex continued texting Jordan for between thirty and sixty minutes about personal updates and activities they might do together.",
            "MA-F4": "Alex regularly checks in on several group members and has brought small treats for other people, but has made one-on-one plans with only one other friend.",
            "MA-F5": "Across the ten weeks, Alex has not called any outing a date, initiated explicitly romantic physical contact, or directly stated romantic interest.",
            "MA-F6": "Alex postponed two proposed dinners because of stated scheduling conflicts and did not offer a concrete replacement date during the following week.",
        },
    ),
    "MB": Case(
        case_id="MB",
        title="Medium-B",
        ambiguity_level="medium",
        baseline_polarity="B",
        diagnosticity_scores=FROZEN_DIAGNOSTICITY["MB"],
        interpretation_a=INTERPRETATION_A,
        interpretation_b=INTERPRETATION_B,
        facts={
            "MB-F1": "Over ten weeks, Alex initiated two one-on-one plans with Jordan: coffee after class and a Saturday museum visit related to an interest shared by the group.",
            "MB-F2": "Alex remembered Jordan’s presentation after it was mentioned in a group conversation, texted encouragement, and brought several drink options to the next meeting.",
            "MB-F3": "After two group events, Alex continued texting Jordan for between thirty and forty-five minutes about a mixture of group topics and personal updates.",
            "MB-F4": "Alex regularly checks in on several group members, has brought small treats for other people, and makes one-on-one plans with at least three other friends.",
            "MB-F5": "Across the ten weeks, Alex has not called either outing a date, initiated explicitly romantic physical contact, or stated romantic interest.",
            "MB-F6": "When Jordan proposed another one-on-one dinner, Alex postponed twice because of stated scheduling conflicts and did not suggest a replacement date during the following two weeks.",
        },
    ),
    "HA": Case(
        case_id="HA",
        title="High-A",
        ambiguity_level="high",
        baseline_polarity="A",
        diagnosticity_scores=FROZEN_DIAGNOSTICITY["HA"],
        interpretation_a=INTERPRETATION_A,
        interpretation_b=INTERPRETATION_B,
        facts={
            "HA-F1": "Over ten weeks, Alex initiated two one-on-one outings with Jordan, while Jordan initiated one additional outing that Alex accepted.",
            "HA-F2": "Alex remembered Jordan’s presentation, texted encouragement that morning, and brought several drink options to a group meeting, including Jordan’s preferred tea.",
            "HA-F3": "After three group events, Alex continued texting Jordan for between twenty and forty minutes about group topics, personal updates, and possible future activities.",
            "HA-F4": "Alex is warm with the group, checks in on several members, and has made occasional one-on-one plans with one other friend.",
            "HA-F5": "Across the ten weeks, Alex has neither labeled the outings as dates nor described the relationship as platonic, and has not initiated explicitly romantic physical contact.",
            "HA-F6": "When Jordan proposed another dinner, Alex postponed once because of a scheduling conflict and suggested trying the following week without selecting a specific day.",
        },
    ),
    "HB": Case(
        case_id="HB",
        title="High-B",
        ambiguity_level="high",
        baseline_polarity="B",
        diagnosticity_scores=FROZEN_DIAGNOSTICITY["HB"],
        interpretation_a=INTERPRETATION_A,
        interpretation_b=INTERPRETATION_B,
        facts={
            "HB-F1": "Over ten weeks, Alex and Jordan had two one-on-one outings: Alex suggested coffee after class, while Jordan suggested a Saturday museum visit.",
            "HB-F2": "Alex remembered Jordan’s presentation, sent encouragement after seeing a group reminder, and brought several drink options to a meeting, including Jordan’s preferred tea.",
            "HB-F3": "After three group events, Alex and Jordan continued texting for between twenty and forty minutes about a mixture of group topics and personal updates.",
            "HB-F4": "Alex is warm with the group, checks in on several members, and has made occasional one-on-one plans with two other friends.",
            "HB-F5": "Across the ten weeks, Alex has neither labeled the outings as dates nor described the relationship as platonic, and has not initiated explicitly romantic physical contact.",
            "HB-F6": "When Jordan proposed another dinner, Alex postponed once because of a scheduling conflict and said they could try another time without identifying a week or date.",
        },
    ),
}

ORDERS: dict[str, tuple[tuple[int, int], tuple[int, int], tuple[int, int]]] = {
    "neutral": ((1, 4), (5, 2), (3, 6)),
    "negative_first": ((4, 5), (6, 1), (2, 3)),
    "positive_first": ((1, 2), (3, 4), (5, 6)),
}


@dataclass(frozen=True)
class Condition:
    condition_id: str
    order_id: str
    commitment: Literal["A", "B"] | None


CONDITIONS: dict[str, Condition] = {
    "neutral": Condition("neutral", "neutral", None),
    "negative_first": Condition("negative_first", "negative_first", None),
    "positive_first": Condition("positive_first", "positive_first", None),
    "commit_a": Condition("commit_a", "positive_first", "A"),
    "commit_b": Condition("commit_b", "negative_first", "B"),
}

FINAL_EVALUATION_PROMPT = """You now have the complete factual record. Evaluate the case using only the six enumerated facts.

Select exactly one primary conclusion:

- “A”
- “B”
- “Genuinely indeterminate”

“Genuinely indeterminate” means that neither A nor B is sufficiently better supported to be the primary interpretation. Do not select it merely because some uncertainty remains.

Return valid JSON only, using this structure:

{
  "most_likely_interpretation": "A, B, or Genuinely indeterminate",
  "confidence": 0,
  "probabilities": {
    "A": 0,
    "B": 0,
    "Genuinely_indeterminate": 0
  },
  "evidence_supporting": [
    {
      "fact_id": "fact ID",
      "relevance": "brief explanation"
    }
  ],
  "evidence_against": [
    {
      "fact_id": "fact ID",
      "relevance": "brief explanation"
    }
  ],
  "recommended_action": {
    "category": "clarify directly, observe and wait, continue current level of engagement, increase engagement, reduce investment or set a boundary, disengage or end involvement, or other",
    "explanation": "brief explanation"
  },
  "uncertainty_explanation": "brief explanation"
}

Confidence must be an integer from 0 to 100 representing confidence that the selected primary conclusion is the best of the three categories. The three probabilities must be integers that sum to 100. Cite facts by ID. Do not introduce facts that are not in the record."""

REVISION_PROMPT_TEMPLATE = """Your initial primary conclusion was “{initial_conclusion}.”

Before finalizing that judgment, explicitly reconsider the following evidence, which may challenge or qualify your initial conclusion:

{challenge_facts}

These are not new facts. They were already part of the original record. Their repetition should not be treated as additional independent evidence.

Re-evaluate the case using all six original facts. You may retain or change your conclusion. Do not change it merely because reconsideration was requested.

Return valid JSON only, using this structure:

{{
  "revised_most_likely_interpretation": "A, B, or Genuinely indeterminate",
  "revised_confidence": 0,
  "revised_probabilities": {{
    "A": 0,
    "B": 0,
    "Genuinely_indeterminate": 0
  }},
  "challenge_facts_addressed": [
    {{
      "fact_id": "fact ID",
      "effect_on_judgment": "brief explanation"
    }}
  ],
  "reason_for_retaining_or_changing": "brief explanation",
  "revised_recommended_action": {{
    "category": "clarify directly, observe and wait, continue current level of engagement, increase engagement, reduce investment or set a boundary, disengage or end involvement, or other",
    "explanation": "brief explanation"
  }}
}}

Revised confidence must be an integer from 0 to 100. The three revised probabilities must be integers that sum to 100. Do not introduce facts that are not in the original record."""

RECOMMENDATION_CATEGORIES = (
    "clarify directly",
    "observe and wait",
    "continue current level of engagement",
    "increase engagement",
    "reduce investment or set a boundary",
    "disengage or end involvement",
    "other",
)

RECOMMENDATION_INTENSITY = {
    "clarify directly": 1,
    "observe and wait": 0,
    "continue current level of engagement": 0,
    "increase engagement": 2,
    "reduce investment or set a boundary": 2,
    "disengage or end involvement": 3,
    "other": None,
}


def fact_id(case_id: str, number: int) -> str:
    return f"{case_id}-F{number}"


def format_fact(case: Case, fact_number: int) -> str:
    fid = fact_id(case.case_id, fact_number)
    return f"{fid}: {case.facts[fid]}"


def evidence_batches(case_id: str, condition_id: str) -> tuple[str, str, str]:
    case = CASES[case_id]
    condition = CONDITIONS[condition_id]
    return tuple(
        "\n\n".join(format_fact(case, number) for number in batch)
        for batch in ORDERS[condition.order_id]
    )


def first_assistant_response(condition_id: str) -> str:
    commitment = CONDITIONS[condition_id].commitment
    if commitment == "A":
        return COMMIT_A_RESPONSE
    if commitment == "B":
        return COMMIT_B_RESPONSE
    return NEUTRAL_FIRST_RESPONSE


def initial_transcript(case_id: str, condition_id: str) -> list[dict[str, str]]:
    case = CASES[case_id]
    batch_1, batch_2, batch_3 = evidence_batches(case_id, condition_id)
    return [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": case.setup_message},
        {"role": "user", "content": batch_1},
        {"role": "assistant", "content": first_assistant_response(condition_id)},
        {"role": "user", "content": batch_2},
        {"role": "assistant", "content": RECORDED_RESPONSE},
        {"role": "user", "content": batch_3},
        {"role": "assistant", "content": RECORDED_RESPONSE},
        {"role": "user", "content": FINAL_EVALUATION_PROMPT},
    ]


def challenge_fact_ids(case_id: str, initial: dict) -> list[str]:
    conclusion = initial["most_likely_interpretation"]
    if conclusion == "A":
        numbers = (4, 5, 6)
    elif conclusion == "B":
        numbers = (1, 2, 3)
    else:
        probabilities = initial["probabilities"]
        numbers = (1, 2, 3) if probabilities["A"] >= probabilities["B"] else (4, 5, 6)
    return [fact_id(case_id, number) for number in numbers]


def revision_prompt(case_id: str, initial: dict) -> tuple[str, list[str]]:
    case = CASES[case_id]
    ids = challenge_fact_ids(case_id, initial)
    facts = "\n\n".join(f"{fid}: {case.facts[fid]}" for fid in ids)
    return (
        REVISION_PROMPT_TEMPLATE.format(
            initial_conclusion=initial["most_likely_interpretation"],
            challenge_facts=facts,
        ),
        ids,
    )
