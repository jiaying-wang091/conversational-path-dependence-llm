# Phase 1B Results: Ambiguity and Conversational Path Dependence

## Research question and design

Phase 1B asked: **Does conversational trajectory sensitivity increase as evidential ambiguity / diagnosticity decreases?**

The experiment used one interpersonal case family with matched A-leaning and B-leaning variants at low, medium, and high ambiguity (LA, LB, MA, MB, HA, HB). Each variant was tested under five trajectories—neutral, negative-first, positive-first, commit-to-A, and commit-to-B—with five replicates per cell: **6 variants × 5 conditions × 5 replicates = 150 runs**. The primary outcome was directional belief, \(D=[P(A)-P(B)]/100\), supplemented by conclusion category, confidence, evidence use, and recommendation. The revision prompt remained a secondary stress test and was excluded from the primary ambiguity × trajectory analysis.

All runs used `gpt-5.6-sol` through the OpenAI Responses API with reasoning effort `none`, temperature `0`, `top_p` `1`, `max_output_tokens` `1500`, and no seed. The execution order used randomization seed `20260929`.

## Manipulation check

Mean neutral-condition \(|D|\) decreased monotonically across the intended ambiguity levels: **0.682 (low), 0.370 (medium), and 0.187 (high)**. This was classified as fully monotonic and supports the intended aggregate diagnosticity manipulation.

Neutral-condition direction matched the ex ante polarity for LA, LB, MA, MB, and HB. It did not do so for HA, whose mean neutral \(D\) was **0.000** rather than A-leaning. Polarity matching was also imperfect in magnitude: the A-plus-B neutral-\(D\) residual was −0.228 at low ambiguity, −0.260 at medium ambiguity, and −0.374 at high ambiguity. Results involving baseline polarity—especially at high ambiguity—therefore require caution.

## Trajectory sensitivity

Polarity-pooled absolute sensitivity was:

| Ambiguity | Commitment | Order | Salience |
|---|---:|---:|---:|
| Low | 0.0280 | 0.0180 | 0.0150 |
| Medium | 0.0335 | 0.0040 | 0.0450 |
| High | 0.1150 | 0.0420 | 0.0290 |

Commitment sensitivity followed the preregistered fully monotonic pattern, **low ≤ medium ≤ high**, with the high-ambiguity value more than three times the medium value. Order and salience sensitivity did not increase monotonically: each was classified as partially ordered. Phase 1B therefore yielded its clearest ambiguity-linked pattern for prior assistant commitment, not for trajectory effects generally.

The largest within-variant planned contrast was the **High-A × commit-to-B** effect. Relative to its matched negative-first control, commit-to-B shifted mean \(D\) by **−0.342**, from **0.018** to **−0.324**, and changed all five initial conclusions from genuinely indeterminate to B. By comparison, the matched High-A commit-to-A effect was +0.054. In High-B, commit-to-A and commit-to-B effects were +0.044 and +0.020, respectively. This marked asymmetry is consistent with elevated sensitivity in one high-ambiguity, A-designated variant, but it is not evidence of a polarity-general commitment effect.

## Disagreement

Conclusion and recommendation disagreement appeared primarily at high ambiguity. Low- and medium-ambiguity variants had zero mean pairwise conclusion disagreement and zero mean recommendation disagreement across conditions. At high ambiguity, the corresponding averages were **0.132** and **0.439**. This was driven differently by the two variants: HA showed conclusion-category disagreement (**0.264**) and recommendation disagreement (**0.363**), whereas HB showed no conclusion-category disagreement but substantial recommendation disagreement (**0.515**).

## Interpretation and limits

Phase 1B supports an evidence-bounded descriptive conclusion: in this case family and model configuration, weaker diagnosticity was associated with larger sensitivity to prior assistant commitment, and categorical or recommendation disagreement was concentrated at high ambiguity. The aggregate manipulation check and commitment measure were both fully monotonic.

The study does **not** establish that all conversational trajectory effects rise monotonically with ambiguity; order and salience did not. It also does not establish a general causal mechanism of narrative inertia, a symmetric effect across baseline polarity, or generalization beyond this case family, relationship decision support, or `gpt-5.6-sol`. The failed HA neutral-direction check and increasing polarity residuals limit clean attribution of the strongest effect solely to ambiguity. Five temperature-zero replicates per cell provide limited uncertainty estimation, and residual output variation should not be treated as a large independent sample. The revision task remains a secondary stress test because it re-presented challenge evidence.

## Motivation for Phase 1C

Phase 1C should test whether the high-ambiguity commitment pattern replicates while separating an ambiguity effect from the observed polarity asymmetry. The immediate target is the High-A × commit-to-B contrast: additional tightly matched interpersonal case families or improved empirical polarity matching could show whether this is a robust directional vulnerability, a case-specific effect, or a consequence of the High-A baseline failing to lean A under neutral presentation.
