# VA-RAG run report: 20261019T123451Z-vllm_large-24d6e0c6

- Model: `vllm_large` = Qwen/Qwen2.5-Coder-14B-Instruct-AWQ @ eb3172f06a6d, quantization {'bits': 4, 'dtype': 'float16', 'group_size': 128, 'method': 'awq', 'version': 'gemm', 'zero_point': True}
- Split: dev; user arm: knows; instances: 83; concepts: 16
- Scoring of deprecation concepts: primary strict (both reported)
- Commit 80b53257512e, config 2deaec8e2826, created 2026-10-19T12:36:27+00:00

> 16 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | strict | lenient | wrong_version | portable | broken | no_code | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 67.1% [48.8%, 83.3%] (Wilson 40.7%, 84.1%) | 58.5% | 67.1% | 3.7% | 19.5% | 29.3% | 0.0% | 12.7% |
| assume_state | 52.4% [34.6%, 70.3%] (Wilson 27.4%, 72.6%) | 45.1% | 54.9% | 17.1% | 19.5% | 30.5% | 0.0% | 14.0% |
| mind_version | 56.1% [37.8%, 74.3%] (Wilson 30.1%, 75.2%) | 48.8% | 57.3% | 19.5% | 23.2% | 24.4% | 0.0% | 13.0% |
| no_retrieval | 48.8% [32.1%, 64.6%] (Wilson 23.1%, 68.0%) | 45.1% | 54.9% | 24.4% | 25.6% | 26.8% | 0.0% | 7.5% |
| oracle_docs | 65.9% [48.5%, 81.7%] (Wilson 39.7%, 83.3%) | 57.3% | 65.9% | 6.1% | 19.5% | 28.0% | 0.0% | 13.0% |
| plain_rag | 54.9% [37.2%, 72.1%] (Wilson 29.2%, 74.3%) | 47.6% | 57.3% | 20.7% | 23.2% | 24.4% | 0.0% | 13.3% |
| two_branch | 67.1% [48.8%, 83.3%] (Wilson 40.7%, 84.1%) | 58.5% | 67.1% | 3.7% | 19.5% | 29.3% | 0.0% | 12.7% |
| va_rag | 69.5% [51.1%, 86.6%] (Wilson 42.7%, 85.6%) | 64.6% | 69.5% | 1.2% | 19.5% | 29.3% | 0.0% | 7.0% |
| va_rag_no_ask | 62.2% [45.1%, 76.9%] (Wilson 34.8%, 79.4%) | 57.3% | 62.2% | 9.8% | 19.5% | 28.0% | 0.0% | 7.8% |
| va_rag_no_guard | 68.3% [50.0%, 84.9%] (Wilson 41.7%, 84.8%) | 59.8% | 68.3% | 2.4% | 19.5% | 29.3% | 0.0% | 12.5% |
| va_rag_no_infer | 69.5% [51.1%, 86.6%] (Wilson 42.7%, 85.6%) | 64.6% | 69.5% | 1.2% | 19.5% | 29.3% | 0.0% | 7.0% |

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 33.7% | 100.0% | 0.0% | c=0.0: 67.1%, c=0.1: 57.1%, c=0.3: 37.1% | 1.00 calls, 1.00 answers |
| assume_state | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | c=0.0: 52.4%, c=0.1: 52.4%, c=0.3: 52.4% | 1.00 calls, 1.00 answers |
| mind_version | 1.2% [0.0%, 3.8%] (Wilson 0.0%, 22.1%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 0.0% | 3.6% | 0.0% | c=0.0: 56.1%, c=0.1: 55.9%, c=0.3: 55.4% | 1.02 calls, 1.00 answers |
| no_retrieval | 1.2% [0.0%, 3.8%] (Wilson 0.0%, 22.1%) | 1.2% [0.0%, 3.8%] (Wilson 0.0%, 22.1%) | 0.0% | 0.0% | 0.0% | 3.6% | 0.0% | c=0.0: 48.8%, c=0.1: 48.5%, c=0.3: 48.0% | 1.02 calls, 1.00 answers |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | c=0.0: 65.9%, c=0.1: 65.9%, c=0.3: 65.9% | 1.00 calls, 1.00 answers |
| plain_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | c=0.0: 54.9%, c=0.1: 54.9%, c=0.3: 54.9% | 1.00 calls, 1.00 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 98.2% | c=0.0: 67.1%, c=0.1: 57.1%, c=0.3: 37.1% | 1.99 calls, 1.99 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 100.0% | 0.0% | 0.0% | c=0.0: 69.5%, c=0.1: 66.1%, c=0.3: 59.3% | 1.05 calls, 1.00 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | c=0.0: 62.2%, c=0.1: 62.2%, c=0.3: 62.2% | 1.04 calls, 1.00 answers |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 100.0% | 0.0% | 0.0% | c=0.0: 68.3%, c=0.1: 64.9%, c=0.3: 58.0% | 1.00 calls, 1.00 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 34.1% | 98.2% | 0.0% | c=0.0: 69.5%, c=0.1: 59.5%, c=0.3: 39.5% | 1.05 calls, 1.00 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | -0.073 | n/a |
| assume_state | old 32.1%, new 32.1%, both 0.0%, neither 35.7% (n=28) | 35.7% | -0.024 | n/a |
| mind_version | old 32.1%, new 32.1%, both 0.0%, neither 35.7% (n=28) | 30.8% | 0.098 | n/a |
| no_retrieval | old 35.7%, new 0.0%, both 0.0%, neither 64.3% (n=28) | 30.8% | -0.098 | n/a |
| oracle_docs | old 28.6%, new 35.7%, both 0.0%, neither 35.7% (n=28) | 50.0% | -0.098 | n/a |
| plain_rag | old 32.1%, new 32.1%, both 0.0%, neither 35.7% (n=28) | 32.1% | 0.073 | n/a |
| two_branch | old 25.0%, new 39.3%, both 0.0%, neither 35.7% (n=28) | 53.6% | -0.073 | 53.7% |
| va_rag |  (n=0) | 60.7% | -0.073 | n/a |
| va_rag_no_ask | old 32.1%, new 32.1%, both 0.0%, neither 35.7% (n=28) | 60.7% | -0.024 | n/a |
| va_rag_no_guard |  (n=0) | 57.1% | -0.049 | n/a |
| va_rag_no_infer |  (n=0) | n/a | -0.073 | n/a |

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | AUROC |margin| | guard flags | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 29, "INFER": 54} | n/a | 4 | 25.0% | 100.0% | 25.0% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"UNCERTAIN": 29, "INFER": 54} | n/a | 3 | 33.3% | 20.0% | 33.3% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 29, "INFER": 54} | n/a | 0 | n/a | 0.0% | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 83} | n/a | 4 | 25.0% | 100.0% | 25.0% | 0.0% |

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
| plain_rag | intended_pass | +15.6 pts | [+1.1, +30.0] | 17 / 5 | 0.0169 | 0.1352 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +14.4 pts | [-1.1, +30.0] | 17 / 6 | 0.0347 | 0.2428 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +2.2 pts | [+0.0, +5.6] | 2 / 0 | 0.5000 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | intended_pass | +2.2 pts | [+0.0, +5.6] | 2 / 0 | 0.5000 | 1.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 64.3% (n=14); pandas 96.2% (n=26); pydantic 54.8% (n=42)

**target**: new 65.1% (n=43); old 74.4% (n=39)

**condition**: clue 64.3% (n=28); no-clue 75.0% (n=28); stated 69.2% (n=26)

**clue_type**: code 45.5% (n=11); error 83.3% (n=6); pin 72.7% (n=11)

**exclusivity**: behavior 66.7% (n=12); deprecation 66.7% (n=18); one_directional 50.0% (n=4); removal 72.9% (n=48)

**change_type**: behavior 66.7% (n=12); param_removed 100.0% (n=2); param_rename 46.9% (n=32); param_value 100.0% (n=6); symbol_rename 86.7% (n=30)

**user_arm**: knows 69.5% (n=82)

**gold_examples**: both 89.5% (n=38); neither 52.3% (n=44)

**gold_examples_x_change_type**: both / behavior 66.7% (n=12); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=6); both / symbol_rename 100.0% (n=18); neither / param_rename 46.9% (n=32); neither / symbol_rename 66.7% (n=12)

### plain_rag

**library**: numpy 64.3% (n=14); pandas 73.1% (n=26); pydantic 40.5% (n=42)

**target**: new 46.5% (n=43); old 64.1% (n=39)

**condition**: clue 57.1% (n=28); no-clue 53.6% (n=28); stated 53.8% (n=26)

**clue_type**: code 45.5% (n=11); error 66.7% (n=6); pin 63.6% (n=11)

**exclusivity**: behavior 100.0% (n=12); deprecation 61.1% (n=18); one_directional 25.0% (n=4); removal 43.8% (n=48)

**change_type**: behavior 100.0% (n=12); param_removed 50.0% (n=2); param_rename 34.4% (n=32); param_value 50.0% (n=6); symbol_rename 60.0% (n=30)

**user_arm**: knows 54.9% (n=82)

**gold_examples**: both 73.7% (n=38); neither 38.6% (n=44)

**gold_examples_x_change_type**: both / behavior 100.0% (n=12); both / param_removed 50.0% (n=2); both / param_value 50.0% (n=6); both / symbol_rename 66.7% (n=18); neither / param_rename 34.4% (n=32); neither / symbol_rename 50.0% (n=12)

### mind_version

**library**: numpy 64.3% (n=14); pandas 73.1% (n=26); pydantic 42.9% (n=42)

**target**: new 48.8% (n=43); old 64.1% (n=39)

**condition**: clue 60.7% (n=28); no-clue 53.6% (n=28); stated 53.8% (n=26)

**clue_type**: code 45.5% (n=11); error 83.3% (n=6); pin 63.6% (n=11)

**exclusivity**: behavior 100.0% (n=12); deprecation 66.7% (n=18); one_directional 25.0% (n=4); removal 43.8% (n=48)

**change_type**: behavior 100.0% (n=12); param_removed 50.0% (n=2); param_rename 34.4% (n=32); param_value 50.0% (n=6); symbol_rename 63.3% (n=30)

**user_arm**: knows 56.1% (n=82)

**gold_examples**: both 73.7% (n=38); neither 40.9% (n=44)

**gold_examples_x_change_type**: both / behavior 100.0% (n=12); both / param_removed 50.0% (n=2); both / param_value 50.0% (n=6); both / symbol_rename 66.7% (n=18); neither / param_rename 34.4% (n=32); neither / symbol_rename 58.3% (n=12)

### two_branch

**library**: numpy 64.3% (n=14); pandas 92.3% (n=26); pydantic 52.4% (n=42)

**target**: new 62.8% (n=43); old 71.8% (n=39)

**condition**: clue 57.1% (n=28); no-clue 75.0% (n=28); stated 69.2% (n=26)

**clue_type**: code 36.4% (n=11); error 66.7% (n=6); pin 72.7% (n=11)

**exclusivity**: behavior 66.7% (n=12); deprecation 66.7% (n=18); one_directional 50.0% (n=4); removal 68.8% (n=48)

**change_type**: behavior 66.7% (n=12); param_removed 100.0% (n=2); param_rename 43.8% (n=32); param_value 100.0% (n=6); symbol_rename 83.3% (n=30)

**user_arm**: knows 67.1% (n=82)

**gold_examples**: both 86.8% (n=38); neither 50.0% (n=44)

**gold_examples_x_change_type**: both / behavior 66.7% (n=12); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=6); both / symbol_rename 94.4% (n=18); neither / param_rename 43.8% (n=32); neither / symbol_rename 66.7% (n=12)

### always_ask

**library**: numpy 64.3% (n=14); pandas 92.3% (n=26); pydantic 52.4% (n=42)

**target**: new 62.8% (n=43); old 71.8% (n=39)

**condition**: clue 57.1% (n=28); no-clue 75.0% (n=28); stated 69.2% (n=26)

**clue_type**: code 36.4% (n=11); error 66.7% (n=6); pin 72.7% (n=11)

**exclusivity**: behavior 66.7% (n=12); deprecation 66.7% (n=18); one_directional 50.0% (n=4); removal 68.8% (n=48)

**change_type**: behavior 66.7% (n=12); param_removed 100.0% (n=2); param_rename 43.8% (n=32); param_value 100.0% (n=6); symbol_rename 83.3% (n=30)

**user_arm**: knows 67.1% (n=82)

**gold_examples**: both 86.8% (n=38); neither 50.0% (n=44)

**gold_examples_x_change_type**: both / behavior 66.7% (n=12); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=6); both / symbol_rename 94.4% (n=18); neither / param_rename 43.8% (n=32); neither / symbol_rename 66.7% (n=12)

## What size of difference this run can show

82 targeted instances over 15 concepts (5.5 per concept). Estimated intra-concept correlation rho = 0.410; observed discordant rate against va_rag = 0.132. Miller's formula at 80% power, two-sided 5%:

| discordant rate | rho | detectable difference |
| --- | --- | --- |
| 0.20 | 0.25 | 20.1 points |
| 0.20 | 0.50 | 24.9 points |
| 0.30 | 0.50 | 30.5 points |
| 0.13 | 0.41 | 18.9 points (observed) |
