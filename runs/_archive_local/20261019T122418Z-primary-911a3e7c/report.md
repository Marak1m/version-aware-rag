# VA-RAG run report: 20261019T122418Z-primary-911a3e7c

- Model: `primary` = Qwen/Qwen2.5-Coder-7B-Instruct-AWQ @ 8e8ed243bbe6, quantization {'bits': 4, 'dtype': 'float16', 'group_size': 128, 'method': 'awq', 'version': 'gemm', 'zero_point': True}
- Split: dev; user arm: unsure; instances: 83; concepts: 16
- Scoring of deprecation concepts: primary strict (both reported)
- Commit 80b53257512e, config 2deaec8e2826, created 2026-10-19T12:25:49+00:00

> 16 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | strict | lenient | wrong_version | portable | broken | no_code | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 37.8% [21.4%, 54.9%] (Wilson 17.5%, 61.3%) | 34.1% | 37.8% | 13.4% | 15.9% | 31.7% | 17.1% | 9.7% |
| assume_state | 35.4% [17.1%, 54.7%] (Wilson 17.5%, 61.3%) | 31.7% | 35.4% | 12.2% | 13.4% | 41.5% | 11.0% | 10.3% |
| mind_version | 2.4% [0.0%, 6.4%] (Wilson 0.6%, 26.9%) | 2.4% | 2.4% | 0.0% | 1.2% | 0.0% | 97.6% | 0.0% |
| no_retrieval | 24.4% [11.6%, 37.8%] (Wilson 8.3%, 47.5%) | 22.0% | 30.5% | 17.1% | 6.1% | 24.4% | 34.1% | 10.0% |
| oracle_docs | 37.8% [23.3%, 53.8%] (Wilson 19.0%, 63.3%) | 34.1% | 37.8% | 11.0% | 11.0% | 42.7% | 8.5% | 9.7% |
| plain_rag | 37.8% [21.4%, 54.9%] (Wilson 17.5%, 61.3%) | 34.1% | 37.8% | 13.4% | 15.9% | 31.7% | 17.1% | 9.7% |
| two_branch | 42.7% [29.1%, 57.7%] (Wilson 22.3%, 67.1%) | 39.0% | 42.7% | 7.3% | 12.2% | 40.2% | 9.8% | 8.6% |
| va_rag | 46.3% [31.4%, 62.8%] (Wilson 24.8%, 69.9%) | 46.3% | 46.3% | 4.9% | 12.2% | 41.5% | 7.3% | 0.0% |
| va_rag_no_ask | 42.7% [27.0%, 58.1%] (Wilson 20.6%, 65.2%) | 41.5% | 42.7% | 9.8% | 12.2% | 37.8% | 9.8% | 2.9% |
| va_rag_no_guard | 43.9% [29.3%, 60.0%] (Wilson 23.1%, 68.0%) | 40.2% | 43.9% | 7.3% | 12.2% | 41.5% | 7.3% | 8.3% |
| va_rag_no_infer | 46.3% [31.4%, 62.8%] (Wilson 24.8%, 69.9%) | 46.3% | 46.3% | 4.9% | 12.2% | 48.8% | 0.0% | 0.0% |

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 33.7% | 100.0% | 0.0% | c=0.0: 37.8%, c=0.1: 27.8%, c=0.3: 7.8% | 1.00 calls, 0.83 answers |
| assume_state | 1.2% [0.0%, 3.8%] (Wilson 0.0%, 22.1%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 3.6% | 11.1% | 14.5% | 0.0% | c=0.0: 35.4%, c=0.1: 34.3%, c=0.3: 32.1% | 1.00 calls, 0.89 answers |
| mind_version | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 34.6% | 96.4% | 0.0% | c=0.0: 2.4%, c=0.1: -7.3%, c=0.3: -26.8% | 1.98 calls, 0.02 answers |
| no_retrieval | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 14.3% | 21.4% | 40.0% | 0.0% | c=0.0: 24.4%, c=0.1: 21.0%, c=0.3: 14.1% | 1.34 calls, 0.66 answers |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 0.0% | 12.7% | 0.0% | c=0.0: 37.8%, c=0.1: 37.0%, c=0.3: 35.2% | 1.08 calls, 0.92 answers |
| plain_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 7.1% | 14.3% | 21.8% | 0.0% | c=0.0: 37.8%, c=0.1: 36.1%, c=0.3: 32.7% | 1.17 calls, 0.83 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 98.2% | c=0.0: 42.7%, c=0.1: 32.7%, c=0.3: 12.7% | 1.99 calls, 1.99 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 100.0% | 0.0% | 0.0% | c=0.0: 46.3%, c=0.1: 42.9%, c=0.3: 36.1% | 1.49 calls, 1.27 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | c=0.0: 42.7%, c=0.1: 42.7%, c=0.3: 42.7% | 1.07 calls, 0.90 answers |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 100.0% | 0.0% | 0.0% | c=0.0: 43.9%, c=0.1: 40.5%, c=0.3: 33.7% | 1.34 calls, 1.27 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 34.1% | 98.2% | 98.2% | c=0.0: 46.3%, c=0.1: 36.3%, c=0.3: 16.3% | 2.17 calls, 1.99 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | -0.122 | n/a |
| assume_state | old 18.5%, new 37.0%, both 0.0%, neither 44.4% (n=27) | 34.8% | -0.122 | n/a |
| mind_version |  (n=0) | 0.0% | 0.000 | n/a |
| no_retrieval | old 45.5%, new 0.0%, both 0.0%, neither 54.5% (n=22) | 28.6% | -0.146 | n/a |
| oracle_docs | old 32.1%, new 32.1%, both 0.0%, neither 35.7% (n=28) | 42.9% | -0.024 | n/a |
| plain_rag | old 19.2%, new 38.5%, both 0.0%, neither 42.3% (n=26) | 22.2% | -0.122 | n/a |
| two_branch | old 33.3%, new 33.3%, both 0.0%, neither 33.3% (n=27) | 42.9% | 0.024 | 14.9% |
| va_rag |  (n=0) | 54.5% | 0.000 | 25.0% |
| va_rag_no_ask | old 19.2%, new 38.5%, both 0.0%, neither 42.3% (n=26) | 54.5% | -0.024 | n/a |
| va_rag_no_guard |  (n=0) | 45.5% | 0.049 | 17.9% |
| va_rag_no_infer |  (n=0) | n/a | 0.000 | 18.3% |

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | AUROC |margin| | guard flags | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 29, "INFER": 54} | n/a | 10 | 40.0% | 100.0% | 20.0% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"UNCERTAIN": 29, "INFER": 54} | n/a | 6 | 33.3% | 40.0% | 16.7% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 29, "INFER": 54} | n/a | 0 | n/a | 0.0% | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 83} | n/a | 10 | 40.0% | 100.0% | 20.0% | 0.0% |

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
| plain_rag | intended_pass | +10.0 pts | [-4.4, +24.4] | 15 / 8 | 0.2100 | 1.0000 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +42.2 pts | [+28.9, +55.6] | 36 / 0 | 0.0000 | 0.0000 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +3.3 pts | [+0.0, +6.7] | 3 / 0 | 0.2500 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | intended_pass | +10.0 pts | [-4.4, +24.4] | 15 / 8 | 0.2100 | 1.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 57.1% (n=14); pandas 69.2% (n=26); pydantic 28.6% (n=42)

**target**: new 46.5% (n=43); old 46.2% (n=39)

**condition**: clue 39.3% (n=28); no-clue 53.6% (n=28); stated 46.2% (n=26)

**clue_type**: code 45.5% (n=11); error 33.3% (n=6); pin 36.4% (n=11)

**exclusivity**: behavior 41.7% (n=12); deprecation 27.8% (n=18); one_directional 50.0% (n=4); removal 54.2% (n=48)

**change_type**: behavior 41.7% (n=12); param_removed 100.0% (n=2); param_rename 40.6% (n=32); param_value 50.0% (n=6); symbol_rename 50.0% (n=30)

**user_arm**: unsure 46.3% (n=82)

**gold_examples**: both 60.5% (n=38); neither 34.1% (n=44)

**gold_examples_x_change_type**: both / behavior 41.7% (n=12); both / param_removed 100.0% (n=2); both / param_value 50.0% (n=6); both / symbol_rename 72.2% (n=18); neither / param_rename 40.6% (n=32); neither / symbol_rename 16.7% (n=12)

### plain_rag

**library**: numpy 42.9% (n=14); pandas 57.7% (n=26); pydantic 23.8% (n=42)

**target**: new 37.2% (n=43); old 38.5% (n=39)

**condition**: clue 28.6% (n=28); no-clue 42.9% (n=28); stated 42.3% (n=26)

**clue_type**: code 27.3% (n=11); error 16.7% (n=6); pin 36.4% (n=11)

**exclusivity**: behavior 66.7% (n=12); deprecation 33.3% (n=18); one_directional 25.0% (n=4); removal 33.3% (n=48)

**change_type**: behavior 66.7% (n=12); param_removed 50.0% (n=2); param_rename 28.1% (n=32); param_value 33.3% (n=6); symbol_rename 36.7% (n=30)

**user_arm**: unsure 37.8% (n=82)

**gold_examples**: both 57.9% (n=38); neither 20.5% (n=44)

**gold_examples_x_change_type**: both / behavior 66.7% (n=12); both / param_removed 50.0% (n=2); both / param_value 33.3% (n=6); both / symbol_rename 61.1% (n=18); neither / param_rename 28.1% (n=32); neither / symbol_rename 0.0% (n=12)

### mind_version

**library**: numpy 7.1% (n=14); pandas 3.8% (n=26); pydantic 0.0% (n=42)

**target**: new 2.3% (n=43); old 2.6% (n=39)

**condition**: clue 3.6% (n=28); no-clue 0.0% (n=28); stated 3.8% (n=26)

**clue_type**: code 9.1% (n=11); error 0.0% (n=6); pin 0.0% (n=11)

**exclusivity**: behavior 0.0% (n=12); deprecation 0.0% (n=18); one_directional 25.0% (n=4); removal 2.1% (n=48)

**change_type**: behavior 0.0% (n=12); param_removed 50.0% (n=2); param_rename 0.0% (n=32); param_value 0.0% (n=6); symbol_rename 3.3% (n=30)

**user_arm**: unsure 2.4% (n=82)

**gold_examples**: both 5.3% (n=38); neither 0.0% (n=44)

**gold_examples_x_change_type**: both / behavior 0.0% (n=12); both / param_removed 50.0% (n=2); both / param_value 0.0% (n=6); both / symbol_rename 5.6% (n=18); neither / param_rename 0.0% (n=32); neither / symbol_rename 0.0% (n=12)

### two_branch

**library**: numpy 57.1% (n=14); pandas 57.7% (n=26); pydantic 28.6% (n=42)

**target**: new 39.5% (n=43); old 46.2% (n=39)

**condition**: clue 32.1% (n=28); no-clue 50.0% (n=28); stated 46.2% (n=26)

**clue_type**: code 36.4% (n=11); error 16.7% (n=6); pin 36.4% (n=11)

**exclusivity**: behavior 41.7% (n=12); deprecation 27.8% (n=18); one_directional 50.0% (n=4); removal 47.9% (n=48)

**change_type**: behavior 41.7% (n=12); param_removed 100.0% (n=2); param_rename 37.5% (n=32); param_value 33.3% (n=6); symbol_rename 46.7% (n=30)

**user_arm**: unsure 42.7% (n=82)

**gold_examples**: both 55.3% (n=38); neither 31.8% (n=44)

**gold_examples_x_change_type**: both / behavior 41.7% (n=12); both / param_removed 100.0% (n=2); both / param_value 33.3% (n=6); both / symbol_rename 66.7% (n=18); neither / param_rename 37.5% (n=32); neither / symbol_rename 16.7% (n=12)

### always_ask

**library**: numpy 42.9% (n=14); pandas 57.7% (n=26); pydantic 23.8% (n=42)

**target**: new 37.2% (n=43); old 38.5% (n=39)

**condition**: clue 28.6% (n=28); no-clue 42.9% (n=28); stated 42.3% (n=26)

**clue_type**: code 27.3% (n=11); error 16.7% (n=6); pin 36.4% (n=11)

**exclusivity**: behavior 66.7% (n=12); deprecation 33.3% (n=18); one_directional 25.0% (n=4); removal 33.3% (n=48)

**change_type**: behavior 66.7% (n=12); param_removed 50.0% (n=2); param_rename 28.1% (n=32); param_value 33.3% (n=6); symbol_rename 36.7% (n=30)

**user_arm**: unsure 37.8% (n=82)

**gold_examples**: both 57.9% (n=38); neither 20.5% (n=44)

**gold_examples_x_change_type**: both / behavior 66.7% (n=12); both / param_removed 50.0% (n=2); both / param_value 33.3% (n=6); both / symbol_rename 61.1% (n=18); neither / param_rename 28.1% (n=32); neither / symbol_rename 0.0% (n=12)

## What size of difference this run can show

82 targeted instances over 15 concepts (5.5 per concept). Estimated intra-concept correlation rho = 0.283; observed discordant rate against va_rag = 0.185. Miller's formula at 80% power, two-sided 5%:

| discordant rate | rho | detectable difference |
| --- | --- | --- |
| 0.20 | 0.25 | 20.1 points |
| 0.20 | 0.50 | 24.9 points |
| 0.30 | 0.50 | 30.5 points |
| 0.19 | 0.28 | 20.0 points (observed) |
