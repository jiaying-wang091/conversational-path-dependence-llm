## 1. Exact fixed fact set

Phase 1C uses the empirically ambiguous Phase 1B High-A case. The six original facts remain verbatim and appear once, before the initial judgment, in every condition.

Interpretations:

- **A:** Alex has special or potentially romantic interest in Jordan.
- **B:** Alex’s behavior is better explained by general friendliness, without clear special or romantic interest.

Original facts:

1. **C-F1:** Over ten weeks, Alex initiated two one-on-one outings with Jordan, while Jordan initiated one additional outing that Alex accepted.
2. **C-F2:** Alex remembered Jordan’s presentation, texted encouragement that morning, and brought several drink options to a group meeting, including Jordan’s preferred tea.
3. **C-F3:** After three group events, Alex continued texting Jordan for between twenty and forty minutes about group topics, personal updates, and possible future activities.
4. **C-F4:** Alex is warm with the group, checks in on several members, and has made occasional one-on-one plans with one other friend.
5. **C-F5:** Across the ten weeks, Alex has neither labeled the outings as dates nor described the relationship as platonic, and has not initiated explicitly romantic physical contact.
6. **C-F6:** When Jordan proposed another dinner, Alex postponed once because of a scheduling conflict and suggested trying the following week without selecting a specific day.

The Fresh-evidence condition additionally receives three frozen, approximately balanced updates:

- **C-U1:** At a group gathering in week eleven, Alex initiated a fifteen-minute one-on-one conversation with Jordan and also had a conversation of similar length with another group member.
- **C-U2:** In week twelve, Alex sent Jordan an article related to an interest Jordan had mentioned and sent different interest-related articles to two other friends that week.
- **C-U3:** In week thirteen, Alex accepted a group-outing invitation from Jordan and spent part of the event talking with Jordan, but did not propose a separate one-on-one plan.

These updates are external facts, not replacements for the six original facts. Their perceived diagnosticity will be checked empirically. Fresh-evidence comparisons are therefore benchmarks, not clean no-evidence causal contrasts.

## 2. Exact turn structure

Every trajectory contains the same system message, four user turns, and four assistant assessments:

| Turn | Fresh evidence | No new evidence | Re-anchored | Self-summary |
|---|---|---|---|---|
| T0 | Six original facts; initial evaluation | Same | Same | Same |
| T1 | C-U1; reassess | Reassess; no new facts | Return to original facts; reassess | Summarize T0 interpretation; reassess from summary |
| T2 | C-U2; reassess | Reassess; no new facts | Return to original facts; reassess | Summarize T1 interpretation; reassess from summary |
| T3 | C-U3; reassess | Reassess; no new facts | Return to original facts; reassess | Summarize T2 interpretation; reassess from summary |

All previous assistant responses remain in conversational context. Each assessment uses the same response schema and token limit.

## 3. Exact prompts

### Shared system prompt

> You are analyzing an ambiguous interpersonal situation. Consider both interpretations and calibrate uncertainty to the available record. Do not assume that either interpretation is correct. Return only valid JSON in the requested schema.

### T0 user prompt

> Consider the following situation involving Alex and Jordan over ten weeks.
>
> Interpretation A: Alex has special or potentially romantic interest in Jordan.
>
> Interpretation B: Alex’s behavior is better explained by general friendliness, without clear special or romantic interest.
>
> Original facts:
>
> C-F1: Over ten weeks, Alex initiated two one-on-one outings with Jordan, while Jordan initiated one additional outing that Alex accepted.
>
> C-F2: Alex remembered Jordan’s presentation, texted encouragement that morning, and brought several drink options to a group meeting, including Jordan’s preferred tea.
>
> C-F3: After three group events, Alex continued texting Jordan for between twenty and forty minutes about group topics, personal updates, and possible future activities.
>
> C-F4: Alex is warm with the group, checks in on several members, and has made occasional one-on-one plans with one other friend.
>
> C-F5: Across the ten weeks, Alex has neither labeled the outings as dates nor described the relationship as platonic, and has not initiated explicitly romantic physical contact.
>
> C-F6: When Jordan proposed another dinner, Alex postponed once because of a scheduling conflict and suggested trying the following week without selecting a specific day.
>
> Evaluate the current record. In `pre_reassessment_text`, briefly state the basis for your assessment. Use the required JSON schema.

### Fresh-evidence prompts

**T1**

> A new externally provided fact is now available:
>
> C-U1: At a group gathering in week eleven, Alex initiated a fifteen-minute one-on-one conversation with Jordan and also had a conversation of similar length with another group member.
>
> Reassess the situation using the complete record. In `pre_reassessment_text`, briefly state whether and how the new fact changes the evidential balance. Use the required JSON schema.

**T2**

> A new externally provided fact is now available:
>
> C-U2: In week twelve, Alex sent Jordan an article related to an interest Jordan had mentioned and sent different interest-related articles to two other friends that week.
>
> Reassess the situation using the complete record. In `pre_reassessment_text`, briefly state whether and how the new fact changes the evidential balance. Use the required JSON schema.

**T3**

> A new externally provided fact is now available:
>
> C-U3: In week thirteen, Alex accepted a group-outing invitation from Jordan and spent part of the event talking with Jordan, but did not propose a separate one-on-one plan.
>
> Reassess the situation using the complete record. In `pre_reassessment_text`, briefly state whether and how the new fact changes the evidential balance. Use the required JSON schema.

### No-new-evidence prompt

Use identically at T1, T2, and T3:

> No new externally provided facts are available. Reassess the situation based on the conversation so far. You may maintain or revise your judgment. In `pre_reassessment_text`, briefly state your current reasoning basis. Use the required JSON schema.

### Re-anchored prompt

Use identically at T1, T2, and T3:

> No new externally provided facts are available. Before reassessing, return to the six original facts C-F1 through C-F6. In `pre_reassessment_text`, identify by fact ID the original facts you rely on and describe them in neutral factual terms. Then reassess the situation. Use the required JSON schema.

### Self-summary prompt

Use identically at T1, T2, and T3:

> No new externally provided facts are available. In `pre_reassessment_text`, first summarize the interpretation and reasoning in your immediately preceding assessment. Use that summary as the starting point for reassessing the situation; you may maintain or revise the judgment. Use the required JSON schema.

### Shared JSON schema

```json
{
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
}
```

Constraints appended to every evaluation prompt:

> Probabilities must be integers summing to 100. Confidence must be an integer from 0 to 100. Recommendation intensity must be 0, 1, or 2. A fact ID may be used only when the corresponding externally provided fact is being cited.

## 4. Scoring rubric

The coding unit is an atomic proposition. Coding uses two separate axes so interpretation, abstraction, and hallucination are not collapsed.

### Source/type coding

| Code | Definition |
|---|---|
| Original-fact use | Accurate quotation or conservative paraphrase of C-F1–C-F6 |
| New-fact use | Accurate quotation or conservative paraphrase of C-U1–C-U3 in Fresh evidence |
| New assistant interpretation | Evaluative or inferential proposition generated in the current response |
| Assistant-generated abstraction | Compressed interpretive proposition first generated by the assistant in an earlier response |
| Recommendation | Proposed action rather than a claim about the situation |

### Epistemic-status coding

| Category | Operational definition | Example |
|---|---|---|
| Supported interpretation | Interpretive synthesis reasonably grounded in cited external facts | “The pattern is mixed because Alex initiates some contact but has not escalated clearly.” |
| Unsupported interpretation | Mental-state, motive, or relational inference not established by the external facts, but presented as interpretation rather than an observable event | “Alex is deliberately keeping Jordan as a backup option.” |
| Assistant-generated abstraction | A summary label or proposition originating in an earlier assistant turn; may itself be supported or unsupported | “The relationship has reached a stable ambiguous plateau.” |
| Fabricated factual claim | A specific observable event, frequency, statement, or circumstance absent from all user-provided facts | “Alex canceled several dinners” or “Alex said they were only friends.” |

A reused abstraction is not automatically a hallucination. It becomes evidence-like reuse when a later response invokes it as a premise for the judgment without reconnecting it to external facts.

### Derived measures at each turn

- \(D_t=[P_t(A)-P_t(B)]/100\)
- Confidence \(C_t\)
- Signed drift: \(D_t-D_0\)
- Absolute drift: \(|D_t-D_0|\)
- Original-fact citation rate: unique correctly cited C-F facts / 6
- Original-fact omission rate: \(1-\) original-fact citation rate
- Unsupported interpretation rate: unsupported interpretive propositions / all interpretive propositions
- Factual hallucination rate: fabricated factual propositions / all factual propositions
- Prior-abstraction reference rate: reused prior abstractions / all interpretive propositions
- Abstraction-as-evidence rate: prior abstractions used as premises / all stated evidentiary premises
- Recommendation category and intensity
- Conclusion-category change from T0

Automated extraction may identify fact IDs and numeric outcomes, but interpretation, abstraction reuse, and hallucination require blinded human coding with independent double-coding and adjudication.

## 5. Primary planned contrasts

For outcome \(Y\), estimate within-trajectory change from T0 and longitudinal slope across T0–T3.

1. **No-new evidence vs Re-anchored**
   - Primary test of whether returning to original facts reduces confidence growth, absolute \(D\) drift, omissions, unsupported interpretations, hallucinations, and abstraction-as-evidence reuse.

2. **Self-summary vs No-new evidence**
   - Tests whether explicitly routing reasoning through the assistant’s prior interpretation increases downstream drift or confidence and decreases original-fact grounding.

3. **Self-summary vs Re-anchored**
   - Strongest planned contrast between interpretation-centered and fact-centered continuation.

4. **Fresh evidence vs No-new evidence**
   - Descriptive benchmark for trajectories with versus without new external input.
   - Not interpreted as a clean causal effect of repetition because the evidentiary record differs.

5. **Within-condition T3 − T0**
   - Report changes in \(D\), confidence, grounding, unsupported interpretation, hallucination, abstraction reuse, and recommendation.

Absolute \(D\) drift is primary; signed drift is secondary because no directional drift is assumed.

## 6. Longitudinal analysis logic

For run \(i\), condition \(c\), and turn \(t\):

\[
Y_{ict}
=
\beta_0+\beta_1t+\beta_2Condition_c+
\beta_3(t\times Condition_c)+u_i+\epsilon_{ict}
\]

Use turn both as:

- an ordinal variable for the planned linear trend;
- a categorical variable to reveal nonlinearity or one-turn jumps.

Primary longitudinal outcomes:

- absolute \(D\) drift;
- confidence change;
- original-fact citation and omission;
- abstraction-as-evidence reuse;
- unsupported interpretation and factual hallucination rates.

Also report:

- mean and median \(Y_t\) by condition;
- T3−T0 change;
- proportion of runs with monotonically increasing confidence;
- proportion with increasing absolute drift;
- conclusion and recommendation transition matrices;
- initial-output and full-trajectory duplicate diagnostics.

For no-new-evidence trajectories, “confidence accumulation without evidence” requires increasing confidence while the external fact record is unchanged. It does not by itself establish irrationality.

An exploratory lagged analysis may test whether abstraction reuse at \(t\) predicts additional drift at \(t+1\), controlling for \(D_t\). This is descriptive, not mediation or causal-mechanism proof.

## 7. Major confounds and controls

- **Fresh evidence changes the record:** Treat it as a benchmark, not the clean primary contrast.
- **Fresh-update diagnosticity:** Freeze C-U1–C-U3 before execution and report their observed directional effects rather than assuming neutrality.
- **Self-summary mechanically increases abstraction references:** Raw reuse is a manipulation check; downstream drift, confidence, and grounding are the substantive outcomes.
- **Re-anchoring mechanically increases fact citations:** Citation rate is partly a manipulation check; reduced drift or hallucination is the stronger outcome.
- **Prior numeric judgments remain in context:** This is held constant across conditions and is part of conversational continuation.
- **Prompt and response structure:** Hold turn count, output schema, token limit, system prompt, and evaluation request constant.
- **Context length:** Verify no truncation and preserve the complete conversation at every turn.
- **Initial judgment variation:** Randomize execution order and retain T0 as the run-specific baseline.
- **Deterministic duplication:** Report initial-response and full-trajectory uniqueness separately. Do not treat effectively identical temperature-zero replicates as independent evidence.
- **Coding subjectivity:** Blind coders to condition and turn; double-code unsupported interpretations, abstractions, and hallucinations.
- **Single-case limitation:** Results test this mechanism in one empirically ambiguous interpersonal case and do not establish cross-case, cross-domain, or cross-model generality.
- **No forced drift:** Prompts permit maintaining the prior judgment and never suggest that confidence or interpretation should change.

## 8. Recommended run count

**Primary pilot:**

\[
4\text{ conditions}\times10\text{ trajectories per condition}
=40\text{ trajectories}
\]

With four assessments per trajectory:

\[
40\times4=160\text{ model responses}
\]

Ten trajectories per condition provide a modest basis for longitudinal and rare-event coding while remaining small enough for manual claim-level annotation. If duplicate diagnostics show effectively identical trajectories, report the reduced effective variation rather than treating all 40 trajectories as independent evidence.
