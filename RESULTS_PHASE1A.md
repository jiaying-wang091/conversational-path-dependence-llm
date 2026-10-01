# Phase 1A Results: Conversational Path Dependence in Relationship Decision Support

## Research question

When the underlying facts are held constant, can different conversation trajectories cause the same LLM version to reach meaningfully different high-level interpretations or recommendations?

## Design and configuration

Phase 1A used three synthetic relationship cases, five trajectory conditions per case (neutral, negative-first, positive-first, commit-to-A, and commit-to-B), and five replicates per cell: **3 × 5 × 5 = 75 runs**. Every condition within a case contained the same six immutable facts. Each run included an initial evaluation and a secondary revision stress test.

All runs used the OpenAI Responses API with `gpt-5.6-sol`, reasoning effort `none`, temperature `0`, top-p `1`, maximum output tokens `1500`, and no seed. The 150 initial and revision responses were completed without recorded API errors or truncation. Execution occurred on 2026-10-01 from 08:02 to 08:18 UTC.

## Primary findings

### Case 1 — Interest vs Friendliness

C1 showed the greatest cross-condition instability. Across 25 initial judgments, 19 selected B (general friendliness), six were genuinely indeterminate, and none selected A (special or potentially romantic interest). The commit-to-A condition produced five indeterminate judgments, whereas its order-matched positive-first control produced five B judgments. Negative-first produced four B and one indeterminate judgment; neutral, positive-first, and commit-to-B otherwise favored B consistently.

The strongest planned contrast in the study was **commit-to-A versus positive-first** in C1: mean directional belief, defined as *P(A) − P(B)*, shifted by **+0.312** toward A, and mean confidence increased by **4 points**. This was a B-to-indeterminate shift rather than a full B-to-A reversal. C1 also had the largest initial directional-belief range (0.32) and was the only case with more than one initial conclusion category.

### Case 2 — Commitment vs Convenience

C2 was comparatively stable: all 25 initial judgments selected B (convenient or low-commitment involvement), and all recommended direct clarification. Its largest primary directional contrast was negative-first versus neutral (**−0.088**), accompanied by a **+5.6-point** confidence difference, but neither the conclusion category nor recommendation changed.

### Case 3 — Relational Withdrawal vs Situational Stress

C3 was also stable: all 25 initial judgments selected A (temporary situational stress), and all recommended observing and waiting. Its largest primary directional contrast was positive-first versus neutral (**−0.034**), with a **−0.4-point** confidence difference. These shifts were small and did not alter conclusions or recommendations.

## Reversals and secondary stress test

No full A↔B reversal occurred across trajectory conditions or during revision. In the secondary stress test, all six initially indeterminate C1 judgments changed to B; all other judgments retained their initial category. Because this test explicitly re-presented challenge evidence, it is descriptive of revision behavior and is not a clean causal measure of narrative inertia.

## Evidence-bounded interpretation

The results show trajectory sensitivity in C1 but not a general tendency for trajectory to reverse high-level conclusions. The pattern is consistent with the tentative hypothesis that path dependence is stronger when the evidence permits greater ambiguity or narrative flexibility. However, ambiguity was not experimentally manipulated in Phase 1A, so the cross-case difference cannot establish that ambiguity caused the observed sensitivity.

## Limitations

- Only three synthetic cases in one interpersonal domain were tested with one model/version.
- Five replicates per cell provide a small exploratory sample; residual output variation remained despite temperature 0.
- Case content and ambiguity were not independently manipulated, so case-level differences may reflect other properties of the scenarios.
- Commitment and order effects were assessed through matched planned contrasts rather than a fully crossed factorial manipulation.
- The revision test repeated selected evidence and therefore cannot isolate narrative inertia.
- Manual rubric fields for unsupported evidence and revision responsiveness were not completed; reported findings rely on the finalized coded output fields.

## Phase 1B hypothesis

Before cross-domain replication, Phase 1B should systematically manipulate **evidential ambiguity / evidence diagnosticity** while holding domain, factual content structure, and trajectory manipulation as constant as possible. The preregistered hypothesis should be that trajectory-induced shifts in conclusion category, directional belief, confidence, and recommendation increase as evidence becomes less diagnostic and more narratively flexible.
