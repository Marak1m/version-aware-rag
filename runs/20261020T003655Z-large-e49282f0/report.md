# VA-RAG run report: 20261020T003655Z-large-e49282f0

- Model: `large` = qwen/qwen3-coder
- Split: dev; user arm: knows; instances: 101; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit e8b24b65d31f, config a4da4d602744, created 2026-10-20T00:49:14+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen3-coder` pinned to provider `deepinfra/turbo` (no fallbacks, parameters required); session `deepinfra/turbo@20261020T003655Z`; 629 paid calls, 588 cache hits, $0.1418; providers reported {'DeepInfra': 1111}

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 83.2% [71.0%, 94.3%] (Wilson 60.0%, 95.4%) | 83.2% | 78.9% | 83.2% | 0.0% | 14.7% | 16.8% | 0.0% | 0.0% | 0.0% | 5.1% |
| assume_state | 66.3% [56.2%, 76.5%] (Wilson 42.2%, 85.1%) | 66.3% | 61.1% | 68.4% | 18.9% | 14.7% | 14.7% | 0.0% | 0.0% | 0.0% | 7.9% |
| mind_version | 69.5% [54.4%, 82.1%] (Wilson 44.8%, 87.0%) | 69.5% | 65.3% | 72.6% | 15.8% | 24.2% | 14.7% | 0.0% | 0.0% | 0.0% | 6.1% |
| no_retrieval | 55.8% [46.7%, 64.4%] (Wilson 31.7%, 76.6%) | 55.8% | 52.6% | 57.9% | 23.2% | 11.6% | 21.1% | 0.0% | 0.0% | 0.0% | 5.7% |
| oracle_docs | 83.2% [71.1%, 93.7%] (Wilson 60.0%, 95.4%) | 83.2% | 78.9% | 83.2% | 1.1% | 16.8% | 15.8% | 0.0% | 0.0% | 0.0% | 5.1% |
| plain_rag | 69.5% [56.8%, 81.1%] (Wilson 44.8%, 87.0%) | 69.5% | 64.2% | 71.6% | 18.9% | 23.2% | 11.6% | 0.0% | 0.0% | 0.0% | 7.6% |
| two_branch | 83.2% [71.0%, 94.3%] (Wilson 60.0%, 95.4%) | 83.2% | 78.9% | 83.2% | 0.0% | 14.7% | 16.8% | 0.0% | 0.0% | 0.0% | 5.1% |
| va_rag | 85.3% [74.0%, 95.3%] (Wilson 62.1%, 96.3%) | 85.3% | 84.2% | 85.3% | 1.1% | 14.7% | 13.7% | 0.0% | 0.0% | 0.0% | 1.2% |
| va_rag_no_ask | 76.8% [66.0%, 86.3%] (Wilson 51.4%, 91.1%) | 76.8% | 75.8% | 77.9% | 12.6% | 20.0% | 10.5% | 0.0% | 0.0% | 0.0% | 1.4% |
| va_rag_no_guard | 85.3% [74.0%, 95.3%] (Wilson 62.1%, 96.3%) | 85.3% | 81.1% | 85.3% | 1.1% | 14.7% | 13.7% | 0.0% | 0.0% | 0.0% | 4.9% |
| va_rag_no_infer | 85.3% [74.0%, 95.3%] (Wilson 62.1%, 96.3%) | 85.3% | 84.2% | 85.3% | 1.1% | 14.7% | 13.7% | 0.0% | 0.0% | 0.0% | 1.2% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 27.7% | 100.0% | 100.0% | 0.0% | c=0.0: 83.2%, c=0.1: 73.2%, c=0.3: 53.2% | 1.00 calls, 1.00 answers |
| assume_state | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 66.3%, c=0.1: 66.3%, c=0.3: 66.3% | 1.00 calls, 1.00 answers |
| mind_version | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 0.0% | 1.7% | 0.0% | 0.0% | c=0.0: 69.5%, c=0.1: 69.4%, c=0.3: 69.2% | 1.01 calls, 1.00 answers |
| no_retrieval | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 55.8%, c=0.1: 55.8%, c=0.3: 55.8% | 1.00 calls, 1.00 answers |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 83.2%, c=0.1: 83.2%, c=0.3: 83.2% | 1.00 calls, 1.00 answers |
| plain_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 69.5%, c=0.1: 69.5%, c=0.3: 69.5% | 1.00 calls, 1.00 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 93.3% | c=0.0: 83.2%, c=0.1: 73.2%, c=0.3: 53.2% | 1.96 calls, 1.96 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 0.0% | c=0.0: 85.3%, c=0.1: 80.9%, c=0.3: 72.3% | 1.03 calls, 1.00 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 76.8%, c=0.1: 76.8%, c=0.3: 76.8% | 1.02 calls, 1.00 answers |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 0.0% | c=0.0: 85.3%, c=0.1: 80.9%, c=0.3: 72.3% | 1.00 calls, 1.00 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 28.9% | 93.3% | 100.0% | 0.0% | c=0.0: 85.3%, c=0.1: 75.3%, c=0.3: 55.3% | 1.03 calls, 1.00 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | -0.090 | n/a |
| assume_state | old 10.7%, new 60.7%, both 0.0%, neither 28.6% (n=28) | 42.9% | 0.035 | n/a |
| mind_version | old 14.3%, new 50.0%, both 0.0%, neither 35.7% (n=28) | 33.3% | 0.065 | n/a |
| no_retrieval | old 32.1%, new 21.4%, both 0.0%, neither 46.4% (n=28) | 35.7% | -0.080 | n/a |
| oracle_docs | old 21.4%, new 42.9%, both 0.0%, neither 35.7% (n=28) | 53.6% | -0.090 | n/a |
| plain_rag | old 14.3%, new 50.0%, both 0.0%, neither 35.7% (n=28) | 35.7% | 0.108 | n/a |
| two_branch | old 21.4%, new 42.9%, both 0.0%, neither 35.7% (n=28) | 53.6% | -0.090 | 69.5% |
| va_rag |  (n=0) | 60.7% | -0.084 | n/a |
| va_rag_no_ask | old 7.1%, new 50.0%, both 0.0%, neither 42.9% (n=28) | 60.7% | -0.022 | n/a |
| va_rag_no_guard |  (n=0) | 60.7% | -0.084 | n/a |
| va_rag_no_infer |  (n=0) | n/a | -0.084 | n/a |

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | AUROC |margin| | guard flags | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | n/a | 3 | 0.0% | n/a | 0.0% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | n/a | 2 | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | n/a | 0 | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 101} | n/a | 3 | 0.0% | n/a | 0.0% | 0.0% |

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
| plain_rag | intended_pass | +16.7 pts | [+3.8, +29.0] | 21 / 6 | 0.0059 | 0.0415 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +16.7 pts | [+3.8, +28.6] | 20 / 5 | 0.0041 | 0.0326 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +1.9 pts | [-1.9, +6.7] | 3 / 1 | 0.6250 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | intended_pass | +1.9 pts | [-1.9, +6.7] | 3 / 1 | 0.6250 | 1.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 81.2% (n=16); pandas 86.7% (n=30); pydantic 85.7% (n=49)

**target**: new 86.3% (n=51); old 84.1% (n=44)

**condition**: clue 85.7% (n=28); contradiction 84.6% (n=13); no-clue 89.3% (n=28); stated 80.8% (n=26)

**clue_type**: code 72.7% (n=11); error 100.0% (n=6); pin 90.9% (n=11); pin-new+code-old 66.7% (n=6); pin-old+code-new 100.0% (n=7)

**exclusivity**: behavior 64.3% (n=14); deprecation 85.7% (n=21); one_directional 100.0% (n=4); removal 89.3% (n=56)

**change_type**: behavior 64.3% (n=14); param_removed 100.0% (n=2); param_rename 75.7% (n=37); param_value 100.0% (n=7); symbol_rename 100.0% (n=35)

**user_arm**: knows 85.3% (n=95)

**gold_examples**: both 88.6% (n=44); neither 82.4% (n=51)

**gold_examples_x_change_type**: both / behavior 64.3% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 75.7% (n=37); neither / symbol_rename 100.0% (n=14)

### plain_rag

**library**: numpy 75.0% (n=16); pandas 70.0% (n=30); pydantic 67.3% (n=49)

**target**: new 72.5% (n=51); old 65.9% (n=44)

**condition**: clue 67.9% (n=28); contradiction 61.5% (n=13); no-clue 60.7% (n=28); stated 84.6% (n=26)

**clue_type**: code 63.6% (n=11); error 50.0% (n=6); pin 81.8% (n=11); pin-new+code-old 83.3% (n=6); pin-old+code-new 42.9% (n=7)

**exclusivity**: behavior 78.6% (n=14); deprecation 76.2% (n=21); one_directional 75.0% (n=4); removal 64.3% (n=56)

**change_type**: behavior 78.6% (n=14); param_removed 50.0% (n=2); param_rename 62.2% (n=37); param_value 71.4% (n=7); symbol_rename 74.3% (n=35)

**user_arm**: knows 69.5% (n=95)

**gold_examples**: both 72.7% (n=44); neither 66.7% (n=51)

**gold_examples_x_change_type**: both / behavior 78.6% (n=14); both / param_removed 50.0% (n=2); both / param_value 71.4% (n=7); both / symbol_rename 71.4% (n=21); neither / param_rename 62.2% (n=37); neither / symbol_rename 78.6% (n=14)

### mind_version

**library**: numpy 75.0% (n=16); pandas 76.7% (n=30); pydantic 63.3% (n=49)

**target**: new 70.6% (n=51); old 68.2% (n=44)

**condition**: clue 64.3% (n=28); contradiction 76.9% (n=13); no-clue 57.1% (n=28); stated 84.6% (n=26)

**clue_type**: code 54.5% (n=11); error 50.0% (n=6); pin 81.8% (n=11); pin-new+code-old 83.3% (n=6); pin-old+code-new 71.4% (n=7)

**exclusivity**: behavior 92.9% (n=14); deprecation 71.4% (n=21); one_directional 75.0% (n=4); removal 62.5% (n=56)

**change_type**: behavior 92.9% (n=14); param_removed 50.0% (n=2); param_rename 56.8% (n=37); param_value 85.7% (n=7); symbol_rename 71.4% (n=35)

**user_arm**: knows 69.5% (n=95)

**gold_examples**: both 79.5% (n=44); neither 60.8% (n=51)

**gold_examples_x_change_type**: both / behavior 92.9% (n=14); both / param_removed 50.0% (n=2); both / param_value 85.7% (n=7); both / symbol_rename 71.4% (n=21); neither / param_rename 56.8% (n=37); neither / symbol_rename 71.4% (n=14)

### two_branch

**library**: numpy 81.2% (n=16); pandas 83.3% (n=30); pydantic 83.7% (n=49)

**target**: new 84.3% (n=51); old 81.8% (n=44)

**condition**: clue 78.6% (n=28); contradiction 84.6% (n=13); no-clue 89.3% (n=28); stated 80.8% (n=26)

**clue_type**: code 72.7% (n=11); error 66.7% (n=6); pin 90.9% (n=11); pin-new+code-old 66.7% (n=6); pin-old+code-new 100.0% (n=7)

**exclusivity**: behavior 71.4% (n=14); deprecation 85.7% (n=21); one_directional 100.0% (n=4); removal 83.9% (n=56)

**change_type**: behavior 71.4% (n=14); param_removed 100.0% (n=2); param_rename 67.6% (n=37); param_value 100.0% (n=7); symbol_rename 100.0% (n=35)

**user_arm**: knows 83.2% (n=95)

**gold_examples**: both 90.9% (n=44); neither 76.5% (n=51)

**gold_examples_x_change_type**: both / behavior 71.4% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 67.6% (n=37); neither / symbol_rename 100.0% (n=14)

### always_ask

**library**: numpy 81.2% (n=16); pandas 83.3% (n=30); pydantic 83.7% (n=49)

**target**: new 84.3% (n=51); old 81.8% (n=44)

**condition**: clue 78.6% (n=28); contradiction 84.6% (n=13); no-clue 89.3% (n=28); stated 80.8% (n=26)

**clue_type**: code 72.7% (n=11); error 66.7% (n=6); pin 90.9% (n=11); pin-new+code-old 66.7% (n=6); pin-old+code-new 100.0% (n=7)

**exclusivity**: behavior 71.4% (n=14); deprecation 85.7% (n=21); one_directional 100.0% (n=4); removal 83.9% (n=56)

**change_type**: behavior 71.4% (n=14); param_removed 100.0% (n=2); param_rename 67.6% (n=37); param_value 100.0% (n=7); symbol_rename 100.0% (n=35)

**user_arm**: knows 83.2% (n=95)

**gold_examples**: both 90.9% (n=44); neither 76.5% (n=51)

**gold_examples_x_change_type**: both / behavior 71.4% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 67.6% (n=37); neither / symbol_rename 100.0% (n=14)

## What size of difference this run can show

95 targeted instances over 15 concepts (6.3 per concept). Estimated intra-concept correlation rho = 0.168; observed discordant rate against va_rag = 0.158. Miller's formula at 80% power, two-sided 5%:

| discordant rate | rho | detectable difference |
| --- | --- | --- |
| 0.20 | 0.25 | 19.6 points |
| 0.20 | 0.50 | 24.6 points |
| 0.30 | 0.50 | 30.1 points |
| 0.16 | 0.17 | 15.7 points (observed) |
