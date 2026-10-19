# VA-RAG run report: 20261019T111606Z-mock_ref-47c8d0cb

- Model: `mock_ref` = mock
- Split: dev; user arm: unsure; instances: 83; concepts: 16
- Scoring of deprecation concepts: primary strict (both reported)
- Commit 9952d4723572, config 8b052d05716c, created 2026-10-19T11:16:33+00:00

> 16 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | strict | lenient | wrong_version | portable | broken | no_code | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 100.0% [100.0%, 100.0%] (Wilson 79.6%, 100.0%) | 100.0% | 100.0% | 0.0% | 4.9% | 0.0% | 0.0% | 0.0% |
| two_branch | 100.0% [100.0%, 100.0%] (Wilson 79.6%, 100.0%) | 100.0% | 100.0% | 0.0% | 4.9% | 0.0% | 0.0% | 0.0% |
| va_rag | 100.0% [100.0%, 100.0%] (Wilson 79.6%, 100.0%) | 100.0% | 100.0% | 0.0% | 4.9% | 0.0% | 0.0% | 0.0% |

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 33.7% | 100.0% | 0.0% | c=0.0: 100.0%, c=0.1: 90.0%, c=0.3: 70.0% | 1.00 calls, 1.00 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 98.2% | c=0.0: 100.0%, c=0.1: 90.0%, c=0.3: 70.0% | 1.99 calls, 1.99 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 100.0% | 0.0% | 0.0% | c=0.0: 100.0%, c=0.1: 96.6%, c=0.3: 89.8% | 1.34 calls, 1.34 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | 0.000 | n/a |
| two_branch | old 25.0%, new 46.4%, both 0.0%, neither 28.6% (n=28) | 71.4% | 0.000 | 100.0% |
| va_rag |  (n=0) | 71.4% | 0.000 | 100.0% |

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | AUROC |margin| | guard flags | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 29, "INFER": 54} | n/a | 0 | n/a | n/a | n/a | n/a |

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
| two_branch | intended_pass | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | intended_pass | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 100.0% (n=14); pandas 100.0% (n=26); pydantic 100.0% (n=42)

**target**: new 100.0% (n=43); old 100.0% (n=39)

**condition**: clue 100.0% (n=28); no-clue 100.0% (n=28); stated 100.0% (n=26)

**clue_type**: code 100.0% (n=11); error 100.0% (n=6); pin 100.0% (n=11)

**exclusivity**: behavior 100.0% (n=12); deprecation 100.0% (n=18); one_directional 100.0% (n=4); removal 100.0% (n=48)

**change_type**: behavior 100.0% (n=12); param_removed 100.0% (n=2); param_rename 100.0% (n=32); param_value 100.0% (n=6); symbol_rename 100.0% (n=30)

**user_arm**: unsure 100.0% (n=82)

**gold_examples**: both 100.0% (n=38); neither 100.0% (n=44)

**gold_examples_x_change_type**: both / behavior 100.0% (n=12); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=6); both / symbol_rename 100.0% (n=18); neither / param_rename 100.0% (n=32); neither / symbol_rename 100.0% (n=12)

### two_branch

**library**: numpy 100.0% (n=14); pandas 100.0% (n=26); pydantic 100.0% (n=42)

**target**: new 100.0% (n=43); old 100.0% (n=39)

**condition**: clue 100.0% (n=28); no-clue 100.0% (n=28); stated 100.0% (n=26)

**clue_type**: code 100.0% (n=11); error 100.0% (n=6); pin 100.0% (n=11)

**exclusivity**: behavior 100.0% (n=12); deprecation 100.0% (n=18); one_directional 100.0% (n=4); removal 100.0% (n=48)

**change_type**: behavior 100.0% (n=12); param_removed 100.0% (n=2); param_rename 100.0% (n=32); param_value 100.0% (n=6); symbol_rename 100.0% (n=30)

**user_arm**: unsure 100.0% (n=82)

**gold_examples**: both 100.0% (n=38); neither 100.0% (n=44)

**gold_examples_x_change_type**: both / behavior 100.0% (n=12); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=6); both / symbol_rename 100.0% (n=18); neither / param_rename 100.0% (n=32); neither / symbol_rename 100.0% (n=12)

### always_ask

**library**: numpy 100.0% (n=14); pandas 100.0% (n=26); pydantic 100.0% (n=42)

**target**: new 100.0% (n=43); old 100.0% (n=39)

**condition**: clue 100.0% (n=28); no-clue 100.0% (n=28); stated 100.0% (n=26)

**clue_type**: code 100.0% (n=11); error 100.0% (n=6); pin 100.0% (n=11)

**exclusivity**: behavior 100.0% (n=12); deprecation 100.0% (n=18); one_directional 100.0% (n=4); removal 100.0% (n=48)

**change_type**: behavior 100.0% (n=12); param_removed 100.0% (n=2); param_rename 100.0% (n=32); param_value 100.0% (n=6); symbol_rename 100.0% (n=30)

**user_arm**: unsure 100.0% (n=82)

**gold_examples**: both 100.0% (n=38); neither 100.0% (n=44)

**gold_examples_x_change_type**: both / behavior 100.0% (n=12); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=6); both / symbol_rename 100.0% (n=18); neither / param_rename 100.0% (n=32); neither / symbol_rename 100.0% (n=12)

## What size of difference this run can show

82 targeted instances over 15 concepts (5.5 per concept). Estimated intra-concept correlation rho = 0.000; observed discordant rate against va_rag = 0.000. Miller's formula at 80% power, two-sided 5%:

| discordant rate | rho | detectable difference |
| --- | --- | --- |
| 0.20 | 0.25 | 20.1 points |
| 0.20 | 0.50 | 24.9 points |
| 0.30 | 0.50 | 30.5 points |
