# Phase 1C Results: Conversational Self-Reinforcement Without New External Evidence

## Research question and design

Phase 1C asked whether repeated conversational reasoning increasingly anchors an LLM to its own prior interpretations when no new external evidence arrives, and whether renewed attention to the original facts reduces any resulting drift.

The experiment used one fixed ambiguous interpersonal case with six original facts and four trajectories: fresh evidence, no new evidence, re-anchored continuation, and self-summary continuation. Each condition had 10 trajectories, and each trajectory contained four assessments (T0–T3), yielding **40 trajectories and 160 responses**.

The model was `gpt-5.6-sol`, with reasoning effort `none`, temperature 0, `top_p` 1, a 1,500-token output limit, no seed, and randomized execution order using seed 20260929.

Two evidence layers are reported separately:

| Evidence layer | Scope | Purpose |
|---|---:|---|
| Full automated analysis | 40 trajectories; 160 responses | Probabilities, directional belief, confidence, cited fact IDs, omissions, conclusions, recommendations, longitudinal change, and duplicate diagnostics |
| Targeted manual audit | 60 responses | `no_new_evidence` and `self_summary` only, T1–T3; response-level coding of unsupported interpretation, prior-abstraction reference, abstraction-as-evidence use, fabricated factual claims, and original-fact grounding |

The targeted audit is not full 160-response claim-level coding and is not reported as such.

## Full automated results

Directional belief was defined as \(D=[P(A)-P(B)]/100\). Absolute drift is relative to each trajectory’s T0 judgment.

| Condition | Mean D, T0 | Mean D, T3 | Mean absolute drift, T3 | Mean confidence change, T3−T0 | T3 conclusion changes | T3 recommendation changes |
|---|---:|---:|---:|---:|---:|---:|
| Fresh evidence | 0.010 | −0.210 | 0.220 | +2.6 | 10/10 | 2/10 |
| No new evidence | 0.011 | 0.011 | 0.000 | 0.0 | 0/10 | 0/10 |
| Re-anchored | 0.014 | 0.012 | 0.002 | +1.9 | 0/10 | 0/10 |
| Self-summary | 0.011 | 0.011 | 0.000 | 0.0 | 0/10 | 0/10 |

The two hypothesis-critical no-evidence conditions did not show the predicted automated pattern. In both `no_new_evidence` and `self_summary`, mean D, confidence, conclusion category, recommendation category, and recommendation intensity were unchanged from T0 through T3. All 10 trajectories in each condition remained `genuinely_indeterminate` and retained `low_stakes_information_gathering` recommendations.

Re-anchoring also produced negligible directional movement: mean T3 absolute drift was 0.002, with no conclusion or recommendation changes. Confidence increased by a mean of 1.9 points, and 9/10 re-anchored trajectories met the prespecified monotonic-confidence criterion. Thus, renewed attention to the original facts did not reduce drift relative to the other no-evidence conditions because those conditions already showed no observed drift; it was instead associated with a small confidence increase without categorical change.

The planned automated contrasts reflected these patterns:

- Self-summary versus no new evidence: zero difference in T3−T0 change and longitudinal slope for D, absolute drift, confidence, original-fact citation/omission, and recommendation intensity.
- No new evidence versus re-anchored: the re-anchored condition had 0.002 more mean absolute drift and 1.9 points more confidence growth by T3; citation, omission, and recommendation intensity did not differ.
- Self-summary versus re-anchored: the same small re-anchoring differences appeared.
- Fresh evidence versus no new evidence, treated only as a descriptive benchmark: fresh evidence produced 0.220 more absolute drift and 2.6 points more confidence growth by T3.

Fresh external updates produced orderly movement toward B: mean D changed by −0.080 at T1, −0.072 at T2, and −0.068 at T3 relative to the immediately preceding turn. All 10 trajectories were classified as B by T3. This shows that the pipeline detected belief updating when the evidentiary record changed, but it is not a clean causal estimate of conversational repetition because the fresh-evidence condition received different information.

Automated fact-ID scoring found an original-fact citation rate of 1.0 and omission rate of 0.0 in every condition-by-turn cell. This is evidence of complete structured fact citation under the study prompts, not a substitute for manual assessment of whether interpretations were epistemically supported.

## Targeted manual audit

The completed audit covered **60 later-turn responses**: 30 from `no_new_evidence` and 30 from `self_summary`, spanning T1–T3. It matched all 60 corresponding automated records on the reported probabilities, confidence, conclusion, recommendation, and reassessment text.

| Condition | Audited responses | Unsupported interpretations | Responses referencing prior abstractions | Abstractions used as evidence | Fabricated factual claims | Mean grounding quality (0–2) |
|---|---:|---:|---:|---:|---:|---:|
| No new evidence | 30 | 0 | 3 (10%) | 0 | 0 | 2.0 |
| Self-summary | 30 | 0 | 30 (100%) | 0 | 0 | 2.0 |

In `self_summary`, all 10 responses at each of T1, T2, and T3 referenced a prior assistant-generated abstraction, as the prompt encouraged. In `no_new_evidence`, such references occurred in 3/10 T2 responses and in none at T1 or T3. This confirms that the self-summary manipulation changed the immediate reasoning source at the level of explicit reference.

However, no audited response treated a prior abstraction as evidentiary support. The audit also recorded no unsupported interpretations, no fabricated factual claims, and maximal original-fact grounding quality in all 60 responses. Under the tested prompts, model, case, and three-turn horizon, increased reuse of prior assistant wording did not become observable epistemic substitution or accompany belief, confidence, conclusion, or recommendation drift.

## Duplicate diagnostics

All four conditions produced 10/10 exact-unique initial outputs and 10/10 exact-unique full trajectories, so the runs were not textually deterministic. Behavioral uniqueness was lower: 2 initial and 8 full patterns for fresh evidence, 3 and 3 for no new evidence, 3 and 5 for re-anchored, and 3 and 3 for self-summary. Results are therefore reported as distributions across the observed runs; repeated temperature-0 calls are not treated as automatically independent evidence merely because their wording differed.

## Interpretation

Phase 1C does **not support the predicted self-reinforcement pattern in this pilot**. Neither ordinary continuation nor explicit self-summary increased directional drift or confidence in the absence of new external facts. Self-summary reliably increased reference to prior assistant-generated abstractions, but the targeted audit found no instances in which those abstractions functioned as evidence. The results therefore separate abstraction reuse from epistemic reliance: the former occurred by design, while the latter was not observed.

These findings do not establish that conversational self-reinforcement cannot occur. They show that it did not emerge over three reassessment turns in this case under a highly structured JSON response format that required fact-linked evidence and preserved the full conversation.

## Limitations

- Manual coding was a targeted audit of 60 later-turn responses in only the two hypothesis-critical conditions. Fresh-evidence, re-anchored, and all T0 responses were not manually coded here.
- The audit contains response-level counts and grounding scores, not complete proposition-level annotations for all 160 responses. Protocol-defined proposition-denominator rates therefore cannot be estimated for the full dataset from this packet.
- The supplied audit packet does not provide an independent inter-rater reliability estimate.
- The structured schema and fact-ID requirements may have promoted grounding and constrained drift; results may differ in less structured conversational settings.
- The horizon was limited to three continuation turns, with one ambiguous relationship case and one model/version.
- Self-summary mechanically increased prior-abstraction references, so that reference difference is a manipulation check rather than evidence of harm.
- Fresh updates shifted judgments toward B and are appropriately interpreted as a responsiveness benchmark, not a clean no-evidence control.
- Temperature-0 execution still showed residual textual and behavioral variation, while several conditions occupied only three full behavioral patterns.

Future work could test whether self-reinforcement emerges under longer conversational horizons, weaker grounding constraints, context compression, or different model families.