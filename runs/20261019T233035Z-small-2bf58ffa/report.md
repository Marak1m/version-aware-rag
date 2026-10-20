# VA-RAG run report: 20261019T233035Z-small-2bf58ffa

- Model: `small` = qwen/qwen-2.5-7b-instruct
- Split: dev; user arm: knows; instances: 101; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit e8b24b65d31f, config a4da4d602744, created 2026-10-19T23:41:10+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen-2.5-7b-instruct` pinned to provider `phala` (no fallbacks, parameters required); session `phala@20261019T233035Z`; 655 paid calls, 609 cache hits, $0.0668; providers reported {'Phala': 1111}

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 52.6% [33.3%, 70.0%] (Wilson 27.4%, 72.6%) | 56.2% | 46.3% | 52.6% | 9.5% | 12.6% | 31.6% | 6.3% | 0.0% | 0.0% | 12.0% |
| assume_state | 38.9% [24.4%, 54.4%] (Wilson 16.5%, 60.0%) | 39.4% | 32.6% | 38.9% | 24.2% | 11.6% | 35.8% | 1.1% | 0.0% | 0.0% | 16.2% |
| mind_version | 42.1% [27.1%, 56.8%] (Wilson 18.5%, 62.6%) | 47.1% | 32.6% | 43.2% | 23.2% | 14.7% | 24.2% | 10.5% | 0.0% | 0.0% | 22.5% |
| no_retrieval | 36.8% [23.5%, 49.0%] (Wilson 16.8%, 60.5%) | 40.7% | 35.8% | 43.2% | 22.1% | 14.7% | 32.6% | 8.4% | 0.0% | 0.0% | 2.9% |
| oracle_docs | 54.7% [35.0%, 73.0%] (Wilson 27.0%, 72.2%) | 59.1% | 44.2% | 54.7% | 10.5% | 11.6% | 27.4% | 7.4% | 0.0% | 0.0% | 19.2% |
| plain_rag | 42.1% [25.9%, 58.0%] (Wilson 18.5%, 62.6%) | 47.1% | 34.7% | 42.1% | 24.2% | 16.8% | 23.2% | 10.5% | 0.0% | 0.0% | 17.5% |
| two_branch | 52.6% [33.3%, 70.0%] (Wilson 27.4%, 72.6%) | 56.2% | 46.3% | 52.6% | 9.5% | 12.6% | 31.6% | 6.3% | 0.0% | 0.0% | 12.0% |
| va_rag | 57.9% [35.6%, 78.9%] (Wilson 33.3%, 78.1%) | 62.5% | 52.6% | 57.9% | 4.2% | 12.6% | 30.5% | 7.4% | 0.0% | 0.0% | 9.1% |
| va_rag_no_ask | 48.4% [28.9%, 66.3%] (Wilson 24.4%, 69.5%) | 50.5% | 45.3% | 48.4% | 14.7% | 10.5% | 32.6% | 4.2% | 0.0% | 0.0% | 6.5% |
| va_rag_no_guard | 53.7% [32.2%, 73.8%] (Wilson 28.2%, 73.3%) | 58.0% | 48.4% | 53.7% | 8.4% | 11.6% | 30.5% | 7.4% | 0.0% | 0.0% | 9.8% |
| va_rag_no_infer | 57.9% [35.6%, 78.9%] (Wilson 33.3%, 78.1%) | 62.5% | 52.6% | 57.9% | 4.2% | 12.6% | 30.5% | 7.4% | 0.0% | 0.0% | 9.1% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 27.7% | 100.0% | 100.0% | 0.0% | c=0.0: 52.6%, c=0.1: 42.6%, c=0.3: 22.6% | 1.00 calls, 1.00 answers |
| assume_state | 2.1% [0.0%, 5.3%] (Wilson 0.1%, 23.3%) | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 38.9%, c=0.1: 38.9%, c=0.3: 38.9% | 1.00 calls, 1.00 answers |
| mind_version | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 28.6% | 29.6% | 26.7% | 23.1% | 0.0% | c=0.0: 42.1%, c=0.1: 39.6%, c=0.3: 34.5% | 1.27 calls, 1.00 answers |
| no_retrieval | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 0.0% | 1.7% | 7.7% | 0.0% | c=0.0: 36.8%, c=0.1: 36.6%, c=0.3: 36.2% | 1.02 calls, 1.00 answers |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 54.7%, c=0.1: 54.7%, c=0.3: 54.7% | 1.00 calls, 1.00 answers |
| plain_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 42.1%, c=0.1: 42.1%, c=0.3: 42.1% | 1.00 calls, 1.00 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 93.3% | c=0.0: 52.6%, c=0.1: 42.6%, c=0.3: 22.6% | 1.96 calls, 1.96 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 0.0% | c=0.0: 57.9%, c=0.1: 53.6%, c=0.3: 44.9% | 1.10 calls, 1.00 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 48.4%, c=0.1: 48.4%, c=0.3: 48.4% | 1.07 calls, 1.00 answers |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 0.0% | c=0.0: 53.7%, c=0.1: 49.4%, c=0.3: 40.7% | 1.00 calls, 1.00 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 28.9% | 93.3% | 100.0% | 0.0% | c=0.0: 57.9%, c=0.1: 47.9%, c=0.3: 27.9% | 1.10 calls, 1.00 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | -0.068 | n/a |
| assume_state | old 28.6%, new 32.1%, both 0.0%, neither 39.3% (n=28) | 28.6% | 0.130 | n/a |
| mind_version | old 20.0%, new 35.0%, both 0.0%, neither 45.0% (n=20) | 36.8% | -0.011 | n/a |
| no_retrieval | old 25.0%, new 7.1%, both 0.0%, neither 67.9% (n=28) | 29.6% | -0.090 | n/a |
| oracle_docs | old 32.1%, new 32.1%, both 0.0%, neither 35.7% (n=28) | 46.4% | -0.019 | n/a |
| plain_rag | old 28.6%, new 35.7%, both 0.0%, neither 35.7% (n=28) | 35.7% | -0.011 | n/a |
| two_branch | old 21.4%, new 35.7%, both 0.0%, neither 42.9% (n=28) | 50.0% | -0.068 | 45.3% |
| va_rag |  (n=0) | 57.1% | -0.075 | n/a |
| va_rag_no_ask | old 32.1%, new 39.3%, both 0.0%, neither 28.6% (n=28) | 57.1% | 0.006 | n/a |
| va_rag_no_guard |  (n=0) | 53.6% | -0.086 | n/a |
| va_rag_no_infer |  (n=0) | n/a | -0.075 | n/a |

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | AUROC |margin| | guard flags | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | n/a | 10 | 90.0% | 75.0% | 40.0% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | n/a | 7 | 100.0% | 35.0% | 42.9% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | n/a | 0 | n/a | 0.0% | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 101} | n/a | 10 | 90.0% | 75.0% | 40.0% | 0.0% |

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
| plain_rag | intended_pass | +19.0 pts | [+1.0, +38.1] | 23 / 8 | 0.0107 | 0.0854 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +19.0 pts | [+0.0, +39.0] | 24 / 9 | 0.0135 | 0.0947 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +7.1 pts | [-1.0, +16.7] | 7 / 2 | 0.1797 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | intended_pass | +7.1 pts | [-1.0, +16.7] | 7 / 2 | 0.1797 | 1.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 75.0% (n=16); pandas 53.3% (n=30); pydantic 55.1% (n=49)

**target**: new 54.9% (n=51); old 61.4% (n=44)

**condition**: clue 60.7% (n=28); contradiction 53.8% (n=13); no-clue 57.1% (n=28); stated 57.7% (n=26)

**clue_type**: code 63.6% (n=11); error 66.7% (n=6); pin 54.5% (n=11); pin-new+code-old 33.3% (n=6); pin-old+code-new 71.4% (n=7)

**exclusivity**: behavior 35.7% (n=14); deprecation 61.9% (n=21); one_directional 50.0% (n=4); removal 62.5% (n=56)

**change_type**: behavior 35.7% (n=14); param_removed 100.0% (n=2); param_rename 40.5% (n=37); param_value 0.0% (n=7); symbol_rename 94.3% (n=35)

**user_arm**: knows 57.9% (n=95)

**gold_examples**: both 63.6% (n=44); neither 52.9% (n=51)

**gold_examples_x_change_type**: both / behavior 35.7% (n=14); both / param_removed 100.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 40.5% (n=37); neither / symbol_rename 85.7% (n=14)

### plain_rag

**library**: numpy 56.2% (n=16); pandas 46.7% (n=30); pydantic 34.7% (n=49)

**target**: new 37.3% (n=51); old 47.7% (n=44)

**condition**: clue 42.9% (n=28); contradiction 30.8% (n=13); no-clue 39.3% (n=28); stated 50.0% (n=26)

**clue_type**: code 27.3% (n=11); error 50.0% (n=6); pin 54.5% (n=11); pin-new+code-old 33.3% (n=6); pin-old+code-new 28.6% (n=7)

**exclusivity**: behavior 71.4% (n=14); deprecation 38.1% (n=21); one_directional 0.0% (n=4); removal 39.3% (n=56)

**change_type**: behavior 71.4% (n=14); param_removed 0.0% (n=2); param_rename 29.7% (n=37); param_value 0.0% (n=7); symbol_rename 54.3% (n=35)

**user_arm**: knows 42.1% (n=95)

**gold_examples**: both 45.5% (n=44); neither 39.2% (n=51)

**gold_examples_x_change_type**: both / behavior 71.4% (n=14); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 47.6% (n=21); neither / param_rename 29.7% (n=37); neither / symbol_rename 64.3% (n=14)

### mind_version

**library**: numpy 62.5% (n=16); pandas 40.0% (n=30); pydantic 36.7% (n=49)

**target**: new 41.2% (n=51); old 43.2% (n=44)

**condition**: clue 46.4% (n=28); contradiction 30.8% (n=13); no-clue 35.7% (n=28); stated 50.0% (n=26)

**clue_type**: code 45.5% (n=11); error 16.7% (n=6); pin 63.6% (n=11); pin-new+code-old 33.3% (n=6); pin-old+code-new 28.6% (n=7)

**exclusivity**: behavior 64.3% (n=14); deprecation 28.6% (n=21); one_directional 0.0% (n=4); removal 44.6% (n=56)

**change_type**: behavior 64.3% (n=14); param_removed 0.0% (n=2); param_rename 32.4% (n=37); param_value 0.0% (n=7); symbol_rename 54.3% (n=35)

**user_arm**: knows 42.1% (n=95)

**gold_examples**: both 43.2% (n=44); neither 41.2% (n=51)

**gold_examples_x_change_type**: both / behavior 64.3% (n=14); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 47.6% (n=21); neither / param_rename 32.4% (n=37); neither / symbol_rename 64.3% (n=14)

### two_branch

**library**: numpy 75.0% (n=16); pandas 36.7% (n=30); pydantic 55.1% (n=49)

**target**: new 49.0% (n=51); old 56.8% (n=44)

**condition**: clue 50.0% (n=28); contradiction 46.2% (n=13); no-clue 57.1% (n=28); stated 53.8% (n=26)

**clue_type**: code 45.5% (n=11); error 50.0% (n=6); pin 54.5% (n=11); pin-new+code-old 50.0% (n=6); pin-old+code-new 42.9% (n=7)

**exclusivity**: behavior 35.7% (n=14); deprecation 57.1% (n=21); one_directional 25.0% (n=4); removal 57.1% (n=56)

**change_type**: behavior 35.7% (n=14); param_removed 50.0% (n=2); param_rename 43.2% (n=37); param_value 0.0% (n=7); symbol_rename 80.0% (n=35)

**user_arm**: knows 52.6% (n=95)

**gold_examples**: both 52.3% (n=44); neither 52.9% (n=51)

**gold_examples_x_change_type**: both / behavior 35.7% (n=14); both / param_removed 50.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 81.0% (n=21); neither / param_rename 43.2% (n=37); neither / symbol_rename 78.6% (n=14)

### always_ask

**library**: numpy 75.0% (n=16); pandas 36.7% (n=30); pydantic 55.1% (n=49)

**target**: new 49.0% (n=51); old 56.8% (n=44)

**condition**: clue 50.0% (n=28); contradiction 46.2% (n=13); no-clue 57.1% (n=28); stated 53.8% (n=26)

**clue_type**: code 45.5% (n=11); error 50.0% (n=6); pin 54.5% (n=11); pin-new+code-old 50.0% (n=6); pin-old+code-new 42.9% (n=7)

**exclusivity**: behavior 35.7% (n=14); deprecation 57.1% (n=21); one_directional 25.0% (n=4); removal 57.1% (n=56)

**change_type**: behavior 35.7% (n=14); param_removed 50.0% (n=2); param_rename 43.2% (n=37); param_value 0.0% (n=7); symbol_rename 80.0% (n=35)

**user_arm**: knows 52.6% (n=95)

**gold_examples**: both 52.3% (n=44); neither 52.9% (n=51)

**gold_examples_x_change_type**: both / behavior 35.7% (n=14); both / param_removed 50.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 81.0% (n=21); neither / param_rename 43.2% (n=37); neither / symbol_rename 78.6% (n=14)

## What size of difference this run can show

95 targeted instances over 15 concepts (6.3 per concept). Estimated intra-concept correlation rho = 0.430; observed discordant rate against va_rag = 0.202. Miller's formula at 80% power, two-sided 5%:

| discordant rate | rho | detectable difference |
| --- | --- | --- |
| 0.20 | 0.25 | 19.6 points |
| 0.20 | 0.50 | 24.6 points |
| 0.30 | 0.50 | 30.1 points |
| 0.20 | 0.43 | 23.5 points (observed) |
