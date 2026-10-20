# VA-RAG run report: 20261019T231735Z-mock_blend-5f1448ab

- Model: `mock_blend` = mock
- Split: dev; user arm: knows; instances: 101; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit e8b24b65d31f, config a4da4d602744, created 2026-10-19T23:18:17+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| plain_rag | 7.4% [0.0%, 18.0%] (Wilson 1.2%, 29.8%) | 7.4% | 7.4% | 17.9% | 9.5% | 0.0% | 83.2% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag | 91.6% [80.0%, 100.0%] (Wilson 69.0%, 98.5%) | 91.6% | 91.6% | 91.6% | 0.0% | 4.2% | 8.4% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_no_guard | 7.4% [0.0%, 18.0%] (Wilson 1.2%, 29.8%) | 7.4% | 7.4% | 17.9% | 9.5% | 0.0% | 83.2% | 0.0% | 0.0% | 0.0% | 0.0% |

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| plain_rag | 51.6% [24.7%, 77.0%] (Wilson 24.8%, 69.9%) | 22.1% [0.0%, 44.2%] (Wilson 7.0%, 45.2%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 7.4%, c=0.1: 7.4%, c=0.3: 7.4% | 1.00 calls, 1.00 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 0.0% | c=0.0: 91.6%, c=0.1: 87.3%, c=0.3: 78.6% | 1.86 calls, 1.00 answers |
| va_rag_no_guard | 51.6% [24.7%, 77.0%] (Wilson 24.8%, 69.9%) | 22.1% [0.0%, 44.2%] (Wilson 7.0%, 45.2%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 0.0% | c=0.0: 7.4%, c=0.1: 3.1%, c=0.3: -5.6% | 1.00 calls, 1.00 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| plain_rag | old 7.1%, new 42.9%, both 50.0%, neither 0.0% (n=28) | 21.4% | -0.001 | n/a |
| va_rag |  (n=0) | 71.4% | -0.023 | n/a |
| va_rag_no_guard |  (n=0) | 21.4% | -0.001 | n/a |

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | AUROC |margin| | guard flags | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | n/a | 87 | 44.8% | 100.0% | 92.0% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | n/a | 0 | n/a | 0.0% | n/a | n/a |

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
| plain_rag | intended_pass | +85.7 pts | [+73.3, +96.2] | 80 / 0 | 0.0000 | 0.0000 |
| plain_rag | blend_exec | -20.0 pts | [-40.0, +0.0] | 0 / 21 | 0.0000 | 0.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 75.0% (n=16); pandas 86.7% (n=30); pydantic 100.0% (n=49)

**target**: new 84.3% (n=51); old 100.0% (n=44)

**condition**: clue 92.9% (n=28); contradiction 84.6% (n=13); no-clue 92.9% (n=28); stated 92.3% (n=26)

**clue_type**: code 81.8% (n=11); error 100.0% (n=6); pin 100.0% (n=11); pin-new+code-old 83.3% (n=6); pin-old+code-new 85.7% (n=7)

**exclusivity**: behavior 42.9% (n=14); deprecation 100.0% (n=21); one_directional 100.0% (n=4); removal 100.0% (n=56)

**change_type**: behavior 42.9% (n=14); param_removed 100.0% (n=2); param_rename 100.0% (n=37); param_value 100.0% (n=7); symbol_rename 100.0% (n=35)

**user_arm**: knows 91.6% (n=95)

**gold_examples**: both 81.8% (n=44); neither 100.0% (n=51)

**gold_examples_x_change_type**: both / behavior 42.9% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 100.0% (n=37); neither / symbol_rename 100.0% (n=14)

### plain_rag

**library**: numpy 0.0% (n=16); pandas 0.0% (n=30); pydantic 14.3% (n=49)

**target**: new 0.0% (n=51); old 15.9% (n=44)

**condition**: clue 7.1% (n=28); contradiction 7.7% (n=13); no-clue 7.1% (n=28); stated 7.7% (n=26)

**clue_type**: code 0.0% (n=11); error 0.0% (n=6); pin 18.2% (n=11); pin-new+code-old 16.7% (n=6); pin-old+code-new 0.0% (n=7)

**exclusivity**: behavior 0.0% (n=14); deprecation 14.3% (n=21); one_directional 0.0% (n=4); removal 7.1% (n=56)

**change_type**: behavior 0.0% (n=14); param_removed 0.0% (n=2); param_rename 18.9% (n=37); param_value 0.0% (n=7); symbol_rename 0.0% (n=35)

**user_arm**: knows 7.4% (n=95)

**gold_examples**: both 0.0% (n=44); neither 13.7% (n=51)

**gold_examples_x_change_type**: both / behavior 0.0% (n=14); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 0.0% (n=21); neither / param_rename 18.9% (n=37); neither / symbol_rename 0.0% (n=14)

## What size of difference this run can show

95 targeted instances over 15 concepts (6.3 per concept). Estimated intra-concept correlation rho = 0.418; observed discordant rate against va_rag = 0.842. Miller's formula at 80% power, two-sided 5%:

| discordant rate | rho | detectable difference |
| --- | --- | --- |
| 0.20 | 0.25 | 19.6 points |
| 0.20 | 0.50 | 24.6 points |
| 0.30 | 0.50 | 30.1 points |
| 0.84 | 0.42 | 47.4 points (observed) |
