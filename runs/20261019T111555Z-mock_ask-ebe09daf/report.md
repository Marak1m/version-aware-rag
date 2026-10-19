# VA-RAG run report: 20261019T111555Z-mock_ask-ebe09daf

- Model: `mock_ask` = mock
- Split: dev; user arm: knows; instances: 83; concepts: 16
- Scoring of deprecation concepts: primary strict (both reported)
- Commit 9952d4723572, config 8b052d05716c, created 2026-10-19T11:16:03+00:00

> 16 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | strict | lenient | wrong_version | portable | broken | no_code | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assume_state | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 100.0% | n/a |
| plain_rag | 100.0% [100.0%, 100.0%] (Wilson 79.6%, 100.0%) | 100.0% | 100.0% | 0.0% | 4.9% | 0.0% | 0.0% | 0.0% |

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assume_state | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 33.7% | 100.0% | 0.0% | c=0.0: 0.0%, c=0.1: -10.0%, c=0.3: -30.0% | 1.00 calls, 0.00 answers |
| plain_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 33.7% | 100.0% | 0.0% | c=0.0: 100.0%, c=0.1: 90.0%, c=0.3: 70.0% | 2.00 calls, 1.00 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| assume_state |  (n=0) | n/a | 0.000 | n/a |
| plain_rag |  (n=0) | n/a | 0.000 | n/a |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### plain_rag

**library**: numpy 100.0% (n=14); pandas 100.0% (n=26); pydantic 100.0% (n=42)

**target**: new 100.0% (n=43); old 100.0% (n=39)

**condition**: clue 100.0% (n=28); no-clue 100.0% (n=28); stated 100.0% (n=26)

**clue_type**: code 100.0% (n=11); error 100.0% (n=6); pin 100.0% (n=11)

**exclusivity**: behavior 100.0% (n=12); deprecation 100.0% (n=18); one_directional 100.0% (n=4); removal 100.0% (n=48)

**change_type**: behavior 100.0% (n=12); param_removed 100.0% (n=2); param_rename 100.0% (n=32); param_value 100.0% (n=6); symbol_rename 100.0% (n=30)

**user_arm**: knows 100.0% (n=82)

**gold_examples**: both 100.0% (n=38); neither 100.0% (n=44)

**gold_examples_x_change_type**: both / behavior 100.0% (n=12); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=6); both / symbol_rename 100.0% (n=18); neither / param_rename 100.0% (n=32); neither / symbol_rename 100.0% (n=12)

## What size of difference this run can show

82 targeted instances over 15 concepts (5.5 per concept). Estimated intra-concept correlation rho = 0.000; observed discordant rate against va_rag = n/a. Miller's formula at 80% power, two-sided 5%:

| discordant rate | rho | detectable difference |
| --- | --- | --- |
| 0.20 | 0.25 | 20.1 points |
| 0.20 | 0.50 | 24.9 points |
| 0.30 | 0.50 | 30.5 points |
