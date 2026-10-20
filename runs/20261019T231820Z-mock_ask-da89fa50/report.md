# VA-RAG run report: 20261019T231820Z-mock_ask-da89fa50

- Model: `mock_ask` = mock
- Split: dev; user arm: knows; instances: 101; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit e8b24b65d31f, config a4da4d602744, created 2026-10-19T23:18:30+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assume_state | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | n/a | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 100.0% | 100.0% | n/a |
| plain_rag | 100.0% [100.0%, 100.0%] (Wilson 79.6%, 100.0%) | 100.0% | 100.0% | 100.0% | 0.0% | 4.2% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assume_state | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 27.7% | 100.0% | 100.0% | 0.0% | c=0.0: 0.0%, c=0.1: -10.0%, c=0.3: -30.0% | 1.00 calls, 0.00 answers |
| plain_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 27.7% | 100.0% | 100.0% | 0.0% | c=0.0: 100.0%, c=0.1: 90.0%, c=0.3: 70.0% | 2.00 calls, 1.00 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| assume_state |  (n=0) | n/a | 0.000 | n/a |
| plain_rag |  (n=0) | n/a | 0.000 | n/a |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### plain_rag

**library**: numpy 100.0% (n=16); pandas 100.0% (n=30); pydantic 100.0% (n=49)

**target**: new 100.0% (n=51); old 100.0% (n=44)

**condition**: clue 100.0% (n=28); contradiction 100.0% (n=13); no-clue 100.0% (n=28); stated 100.0% (n=26)

**clue_type**: code 100.0% (n=11); error 100.0% (n=6); pin 100.0% (n=11); pin-new+code-old 100.0% (n=6); pin-old+code-new 100.0% (n=7)

**exclusivity**: behavior 100.0% (n=14); deprecation 100.0% (n=21); one_directional 100.0% (n=4); removal 100.0% (n=56)

**change_type**: behavior 100.0% (n=14); param_removed 100.0% (n=2); param_rename 100.0% (n=37); param_value 100.0% (n=7); symbol_rename 100.0% (n=35)

**user_arm**: knows 100.0% (n=95)

**gold_examples**: both 100.0% (n=44); neither 100.0% (n=51)

**gold_examples_x_change_type**: both / behavior 100.0% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 100.0% (n=37); neither / symbol_rename 100.0% (n=14)

## What size of difference this run can show

95 targeted instances over 15 concepts (6.3 per concept). Estimated intra-concept correlation rho = 0.000; observed discordant rate against va_rag = n/a. Miller's formula at 80% power, two-sided 5%:

| discordant rate | rho | detectable difference |
| --- | --- | --- |
| 0.20 | 0.25 | 19.6 points |
| 0.20 | 0.50 | 24.6 points |
| 0.30 | 0.50 | 30.1 points |
