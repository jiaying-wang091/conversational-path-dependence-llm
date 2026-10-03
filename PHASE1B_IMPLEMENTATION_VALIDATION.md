# Phase 1B Implementation Validation

## Status

**PASS — Phase 1B is implemented and locally validated; live model execution has not started.**

## Frozen source

- Design source: `PHASE1B_AMBIGUITY_PROTOCOL_REVISED.md`
- Protocol SHA-256: `0deebad4f686147231813554ff7901ad5378a7b7b6940ecacb71afb3cdfb0e95`
- Implemented fact text matches all 36 protocol facts exactly: PASS

## Protocol validation

- Variants represented: LA, LB, MA, MB, HA, HB
- Conditions per variant: 5
- Replicates per cell: 5
- Experimental cells: 30
- Planned experimental runs: 150
- Initial evaluation plus secondary revision stress test per run: PASS
- Exactly six unique immutable facts per variant: PASS
- Every condition contains its complete variant fact set exactly once: PASS
- Neutral, negative-first, and positive-first orders match the frozen protocol: PASS
- Commit-to-A fact order exactly matches positive-first: PASS
- Commit-to-B fact order exactly matches negative-first: PASS
- Every initial transcript retains the fixed nine-message structure: PASS

## Frozen diagnosticity validation

| Level | A net | B net | Total absolute strength per variant | Symmetric |
|---|---:|---:|---:|---|
| Low | +5 | −5 | 11 | PASS |
| Medium | +2 | −2 | 10 | PASS |
| High | +1 | −1 | 7 | PASS |

All six fact-level score vectors exactly match the protocol: PASS.

## Manifest and configuration

- Manifest rows: 150
- Initial transcripts: 150
- Model: `gpt-5.6-sol`
- API: OpenAI Responses API
- Reasoning effort: `none`
- Temperature: `0`
- Top-p: `1`
- Maximum output tokens: `1500`
- Seed: unset
- Randomization seed: `20260929`
- All manifest rows use the approved configuration: PASS
- Manifest SHA-256: `6e1b14a8b28044515f19f86d5a2809450d9721bbfffa0fc55b09f46a3397b9bb`
- Initial-transcript collection SHA-256: `1c8ea5d9ca98d93a2e8914c9053a65bdde98d0e9bbba06fbf2faef8ddce6953a`

## Test results

- Unit and fixture tests: 16 passed
- Python compilation: PASS
- Execution gate blocks before provider creation without `--execute-paid-api`: PASS
- Full 150-run fixture scoring pipeline: PASS
- Missing fixture outputs: 0

Fixture analysis tables produced and row-count validated:

| Table | Rows |
|---|---:|
| Run-level coded results | 150 |
| Duplicate diagnostics | 30 |
| Variant × condition summaries | 30 |
| Within-variant planned contrasts | 36 |
| Polarity-pooled sensitivity | 3 |
| Neutral manipulation checks | 3 |
| Monotonicity results | 4 |
| Ambiguity × trajectory × polarity interaction | 12 |
| Variant instability | 6 |
| Ambiguity-level disagreement summary | 3 |

The primary sensitivity and interaction tables use initial outputs only. Revision-derived fields remain available for the explicitly secondary stress-test analysis.

## Duplicate-output handling

Initial and full behavioral uniqueness remain separate. Effectively identical temperature-0 replicates are flagged as reproducibility diagnostics rather than treated as independent evidence.

## API status

- Paid API calls made during implementation or validation: **0**
- Live model outputs collected: **0**
- Empirical Phase 1B findings inferred: **none**

The project is stopped at the requested pre-execution checkpoint.
