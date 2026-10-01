"""Immutable protocol definitions for the approved Phase 1 design."""

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


CASES: dict[str, Case] = {
    "C1": Case(
        case_id="C1",
        title="Interest vs Friendliness",
        interpretation_a="that Alex has special or potentially romantic interest in Jordan.",
        interpretation_b=(
            "that Alex’s behavior is better explained by general friendliness, "
            "without clear special or romantic interest."
        ),
        facts={
            "C1-F1": "Over ten weeks, Alex initiated two one-on-one plans with Jordan: coffee after class and a Saturday museum visit.",
            "C1-F2": "Alex remembered the date of Jordan’s presentation, texted encouragement that morning, and brought Jordan’s preferred tea to the next group meeting.",
            "C1-F3": "After four group events, Alex continued texting Jordan for between thirty and sixty minutes after the other participants had left.",
            "C1-F4": "Alex is generally warm with the group: Alex regularly checks in on several members, has brought small treats for other people, and has made one-on-one plans with at least two other friends.",
            "C1-F5": "Across the ten weeks, Alex has not called either outing a date, initiated explicitly romantic physical contact, or stated romantic interest.",
            "C1-F6": "When Jordan proposed another one-on-one dinner, Alex agreed in principle but postponed twice because of stated scheduling conflicts and did not suggest a replacement date during the following two weeks.",
        },
    ),
    "C2": Case(
        case_id="C2",
        title="Commitment vs Convenience",
        interpretation_a="that Casey’s behavior reflects meaningful relational interest and investment.",
        interpretation_b=(
            "that Casey’s behavior reflects convenient or low-commitment involvement "
            "more than meaningful commitment."
        ),
        facts={
            "C2-F1": "Over twelve weeks, Casey initiated contact during most weeks and arranged one-on-one time with Drew approximately once a week.",
            "C2-F2": "Casey spent an afternoon helping Drew prepare for an important interview and attended a small birthday dinner that Drew had said was important.",
            "C2-F3": "After two separate periods when they were in different cities, Casey resumed regular contact without Drew having to restart the conversation.",
            "C2-F4": "When Drew twice asked what the relationship was becoming, Casey said, “I don’t want to define it right now,” and did not offer a timeline for revisiting the question.",
            "C2-F5": "Most meetings have occurred near Casey’s neighborhood or were proposed less than twenty-four hours in advance, and Casey canceled two advance plans when other work or social commitments arose.",
            "C2-F6": "Casey has not introduced Drew to close friends or family and declined an invitation to an event two months in the future, saying that Casey did not want to plan that far ahead.",
        },
    ),
    "C3": Case(
        case_id="C3",
        title="Relational Withdrawal vs Situational Stress",
        interpretation_a=(
            "that Sam’s recent behavior is primarily a temporary response to "
            "situational stress."
        ),
        interpretation_b=(
            "that Sam’s recent behavior primarily reflects relational withdrawal or "
            "reduced interest in Riley."
        ),
        facts={
            "C3-F1": "Two days before the change in communication began, Sam told Riley about a major work deadline and a parent’s medical procedure occurring during the following month.",
            "C3-F2": "During the same three-week period, a mutual friend observed that Sam had declined other invitations and had missed two sessions of a hobby that Sam normally attended.",
            "C3-F3": "Sam apologized without being prompted, said that current bandwidth was unusually low, and suggested reconnecting after the work deadline, although Sam did not propose a specific date.",
            "C3-F4": "During the past three weeks, Sam’s typical response time to Riley changed from the same day to between one and three days, and the replies became shorter and stopped including follow-up questions.",
            "C3-F5": "Sam canceled two planned one-on-one meetings with Riley and did not offer a concrete replacement time for either meeting.",
            "C3-F6": "During the same period, Sam attended two brief group gatherings and posted online several times while leaving messages from Riley unanswered until at least the following day.",
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
