# VA-RAG run report: 20261019T111520Z-mock_blend-6366f7ab

- Model: `mock_blend` = mock
- Split: dev; user arm: knows; instances: 83; concepts: 16
- Scoring of deprecation concepts: primary strict (both reported)
- Commit 9952d4723572, config 8b052d05716c, created 2026-10-19T11:15:53+00:00

> 16 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | strict | lenient | wrong_version | portable | broken | no_code | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| plain_rag | 7.3% [0.0%, 17.4%] (Wilson 1.2%, 29.8%) | 7.3% | 18.3% | 9.8% | 0.0% | 82.9% | 0.0% | 0.0% |
| va_rag | 92.7% [82.6%, 100.0%] (Wilson 70.2%, 98.8%) | 92.7% | 92.7% | 0.0% | 4.9% | 7.3% | 0.0% | 0.0% |
| va_rag_no_guard | 7.3% [0.0%, 17.4%] (Wilson 1.2%, 29.8%) | 7.3% | 18.3% | 9.8% | 0.0% | 82.9% | 0.0% | 0.0% |

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| plain_rag | 51.2% [24.3%, 76.7%] (Wilson 24.8%, 69.9%) | 22.0% [0.0%, 43.9%] (Wilson 7.0%, 45.2%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | c=0.0: 7.3%, c=0.1: 7.3%, c=0.3: 7.3% | 1.00 calls, 1.00 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 100.0% | 0.0% | 0.0% | c=0.0: 92.7%, c=0.1: 89.3%, c=0.3: 82.4% | 1.92 calls, 1.00 answers |
| va_rag_no_guard | 51.2% [24.3%, 76.7%] (Wilson 24.8%, 69.9%) | 22.0% [0.0%, 43.9%] (Wilson 7.0%, 45.2%) | 0.0% | 100.0% | 100.0% | 0.0% | 0.0% | c=0.0: 7.3%, c=0.1: 3.9%, c=0.3: -2.9% | 1.00 calls, 1.00 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| plain_rag | old 7.1%, new 42.9%, both 50.0%, neither 0.0% (n=28) | 21.4% | 0.000 | n/a |
| va_rag |  (n=0) | 71.4% | 0.000 | n/a |
| va_rag_no_guard |  (n=0) | 21.4% | 0.000 | n/a |

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | AUROC |margin| | guard flags | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 29, "INFER": 54} | n/a | 76 | 44.7% | 100.0% | 92.1% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 29, "INFER": 54} | n/a | 0 | n/a | 0.0% | n/a | n/a |

Risk-coverage sweep on |margin| for `va_rag` (coverage = answered without a question, risk = wrong-version commits among them):

| threshold | coverage | risk |
| --- | --- | --- |
| 11.50 | 1.9% | 0.0% |
| 3.00 | 27.8% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |

## Primary contrasts: va_rag against each baseline

Paired bootstrap on per-concept differences (va_rag minus baseline); exact McNemar on instance pairs, Holm-adjusted across the contrasts.

| Baseline | Metric | Difference | 95% bootstrap | discordant (va_rag only / baseline only) | McNemar p | Holm p |
| --- | --- | --- | --- | --- | --- | --- |
| plain_rag | intended_pass | +86.7 pts | [+76.7, +96.7] | 70 / 0 | 0.0000 | 0.0000 |
| plain_rag | blend_exec | -20.0 pts | [-40.0, +0.0] | 0 / 18 | 0.0000 | 0.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 78.6% (n=14); pandas 88.5% (n=26); pydantic 100.0% (n=42)

**target**: new 86.0% (n=43); old 100.0% (n=39)

**condition**: clue 92.9% (n=28); no-clue 92.9% (n=28); stated 92.3% (n=26)

**clue_type**: code 81.8% (n=11); error 100.0% (n=6); pin 100.0% (n=11)

**exclusivity**: behavior 50.0% (n=12); deprecation 100.0% (n=18); one_directional 100.0% (n=4); removal 100.0% (n=48)

**change_type**: behavior 50.0% (n=12); param_removed 100.0% (n=2); param_rename 100.0% (n=32); param_value 100.0% (n=6); symbol_rename 100.0% (n=30)

**user_arm**: knows 92.7% (n=82)

**gold_examples**: both 84.2% (n=38); neither 100.0% (n=44)

**gold_examples_x_change_type**: both / behavior 50.0% (n=12); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=6); both / symbol_rename 100.0% (n=18); neither / param_rename 100.0% (n=32); neither / symbol_rename 100.0% (n=12)

### plain_rag

**library**: numpy 0.0% (n=14); pandas 0.0% (n=26); pydantic 14.3% (n=42)

**target**: new 0.0% (n=43); old 15.4% (n=39)

**condition**: clue 7.1% (n=28); no-clue 7.1% (n=28); stated 7.7% (n=26)

**clue_type**: code 0.0% (n=11); error 0.0% (n=6); pin 18.2% (n=11)

**exclusivity**: behavior 0.0% (n=12); deprecation 16.7% (n=18); one_directional 0.0% (n=4); removal 6.2% (n=48)

**change_type**: behavior 0.0% (n=12); param_removed 0.0% (n=2); param_rename 18.8% (n=32); param_value 0.0% (n=6); symbol_rename 0.0% (n=30)

**user_arm**: knows 7.3% (n=82)

**gold_examples**: both 0.0% (n=38); neither 13.6% (n=44)

**gold_examples_x_change_type**: both / behavior 0.0% (n=12); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=6); both / symbol_rename 0.0% (n=18); neither / param_rename 18.8% (n=32); neither / symbol_rename 0.0% (n=12)

## What size of difference this run can show

82 targeted instances over 15 concepts (5.5 per concept). Estimated intra-concept correlation rho = 0.362; observed discordant rate against va_rag = 0.854. Miller's formula at 80% power, two-sided 5%:

| discordant rate | rho | detectable difference |
| --- | --- | --- |
| 0.20 | 0.25 | 20.1 points |
| 0.20 | 0.50 | 24.9 points |
| 0.30 | 0.50 | 30.5 points |
| 0.85 | 0.36 | 46.2 points (observed) |
