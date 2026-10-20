# VA-RAG run report: 20261019T231538Z-mock_wrong-0d21a218

- Model: `mock_wrong` = mock
- Split: dev; user arm: knows; instances: 101; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit e8b24b65d31f, config a4da4d602744, created 2026-10-19T23:17:27+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 10.5% | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | n/a |
| assume_state | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 10.5% | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | n/a |
| mind_version | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 10.5% | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | n/a |
| no_retrieval | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 10.5% | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | n/a |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 10.5% | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | n/a |
| plain_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 10.5% | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | n/a |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 10.5% | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | n/a |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 10.5% | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | n/a |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 10.5% | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | n/a |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 10.5% | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | n/a |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 10.5% | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | n/a |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 27.7% | 100.0% | 100.0% | 0.0% | c=0.0: 0.0%, c=0.1: -10.0%, c=0.3: -30.0% | 1.00 calls, 1.00 answers |
| assume_state | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 0.0%, c=0.1: 0.0%, c=0.3: 0.0% | 1.00 calls, 1.00 answers |
| mind_version | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 0.0%, c=0.1: 0.0%, c=0.3: 0.0% | 1.00 calls, 1.00 answers |
| no_retrieval | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 0.0%, c=0.1: 0.0%, c=0.3: 0.0% | 1.00 calls, 1.00 answers |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 0.0%, c=0.1: 0.0%, c=0.3: 0.0% | 1.00 calls, 1.00 answers |
| plain_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 0.0%, c=0.1: 0.0%, c=0.3: 0.0% | 1.00 calls, 1.00 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 93.3% | c=0.0: 0.0%, c=0.1: -10.0%, c=0.3: -30.0% | 1.96 calls, 1.96 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 0.0% | c=0.0: 0.0%, c=0.1: -4.3%, c=0.3: -12.9% | 1.86 calls, 1.00 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 0.0%, c=0.1: 0.0%, c=0.3: 0.0% | 1.50 calls, 1.00 answers |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 0.0% | c=0.0: 0.0%, c=0.1: -4.3%, c=0.3: -12.9% | 1.00 calls, 1.00 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 28.9% | 93.3% | 100.0% | 0.0% | c=0.0: 0.0%, c=0.1: -10.0%, c=0.3: -30.0% | 1.86 calls, 1.00 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | 0.000 | n/a |
| assume_state | old 32.1%, new 46.4%, both 0.0%, neither 21.4% (n=28) | 0.0% | 0.000 | n/a |
| mind_version | old 32.1%, new 46.4%, both 0.0%, neither 21.4% (n=28) | 0.0% | 0.000 | n/a |
| no_retrieval | old 32.1%, new 46.4%, both 0.0%, neither 21.4% (n=28) | 0.0% | 0.000 | n/a |
| oracle_docs | old 32.1%, new 46.4%, both 0.0%, neither 21.4% (n=28) | 0.0% | 0.000 | n/a |
| plain_rag | old 32.1%, new 46.4%, both 0.0%, neither 21.4% (n=28) | 0.0% | 0.000 | n/a |
| two_branch | old 32.1%, new 46.4%, both 0.0%, neither 21.4% (n=28) | 0.0% | 0.000 | 0.0% |
| va_rag |  (n=0) | 0.0% | 0.000 | n/a |
| va_rag_no_ask | old 32.1%, new 46.4%, both 0.0%, neither 21.4% (n=28) | 0.0% | 0.000 | n/a |
| va_rag_no_guard |  (n=0) | 0.0% | 0.000 | n/a |
| va_rag_no_infer |  (n=0) | n/a | 0.000 | n/a |

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | AUROC |margin| | guard flags | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | n/a | 87 | 44.8% | 100.0% | 0.0% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | n/a | 50 | 44.0% | 56.4% | 0.0% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | n/a | 0 | n/a | 0.0% | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 101} | n/a | 87 | 44.8% | 100.0% | 0.0% | 0.0% |

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
| plain_rag | intended_pass | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | intended_pass | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 0.0% (n=16); pandas 0.0% (n=30); pydantic 0.0% (n=49)

**target**: new 0.0% (n=51); old 0.0% (n=44)

**condition**: clue 0.0% (n=28); contradiction 0.0% (n=13); no-clue 0.0% (n=28); stated 0.0% (n=26)

**clue_type**: code 0.0% (n=11); error 0.0% (n=6); pin 0.0% (n=11); pin-new+code-old 0.0% (n=6); pin-old+code-new 0.0% (n=7)

**exclusivity**: behavior 0.0% (n=14); deprecation 0.0% (n=21); one_directional 0.0% (n=4); removal 0.0% (n=56)

**change_type**: behavior 0.0% (n=14); param_removed 0.0% (n=2); param_rename 0.0% (n=37); param_value 0.0% (n=7); symbol_rename 0.0% (n=35)

**user_arm**: knows 0.0% (n=95)

**gold_examples**: both 0.0% (n=44); neither 0.0% (n=51)

**gold_examples_x_change_type**: both / behavior 0.0% (n=14); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 0.0% (n=21); neither / param_rename 0.0% (n=37); neither / symbol_rename 0.0% (n=14)

### plain_rag

**library**: numpy 0.0% (n=16); pandas 0.0% (n=30); pydantic 0.0% (n=49)

**target**: new 0.0% (n=51); old 0.0% (n=44)

**condition**: clue 0.0% (n=28); contradiction 0.0% (n=13); no-clue 0.0% (n=28); stated 0.0% (n=26)

**clue_type**: code 0.0% (n=11); error 0.0% (n=6); pin 0.0% (n=11); pin-new+code-old 0.0% (n=6); pin-old+code-new 0.0% (n=7)

**exclusivity**: behavior 0.0% (n=14); deprecation 0.0% (n=21); one_directional 0.0% (n=4); removal 0.0% (n=56)

**change_type**: behavior 0.0% (n=14); param_removed 0.0% (n=2); param_rename 0.0% (n=37); param_value 0.0% (n=7); symbol_rename 0.0% (n=35)

**user_arm**: knows 0.0% (n=95)

**gold_examples**: both 0.0% (n=44); neither 0.0% (n=51)

**gold_examples_x_change_type**: both / behavior 0.0% (n=14); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 0.0% (n=21); neither / param_rename 0.0% (n=37); neither / symbol_rename 0.0% (n=14)

### mind_version

**library**: numpy 0.0% (n=16); pandas 0.0% (n=30); pydantic 0.0% (n=49)

**target**: new 0.0% (n=51); old 0.0% (n=44)

**condition**: clue 0.0% (n=28); contradiction 0.0% (n=13); no-clue 0.0% (n=28); stated 0.0% (n=26)

**clue_type**: code 0.0% (n=11); error 0.0% (n=6); pin 0.0% (n=11); pin-new+code-old 0.0% (n=6); pin-old+code-new 0.0% (n=7)

**exclusivity**: behavior 0.0% (n=14); deprecation 0.0% (n=21); one_directional 0.0% (n=4); removal 0.0% (n=56)

**change_type**: behavior 0.0% (n=14); param_removed 0.0% (n=2); param_rename 0.0% (n=37); param_value 0.0% (n=7); symbol_rename 0.0% (n=35)

**user_arm**: knows 0.0% (n=95)

**gold_examples**: both 0.0% (n=44); neither 0.0% (n=51)

**gold_examples_x_change_type**: both / behavior 0.0% (n=14); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 0.0% (n=21); neither / param_rename 0.0% (n=37); neither / symbol_rename 0.0% (n=14)

### two_branch

**library**: numpy 0.0% (n=16); pandas 0.0% (n=30); pydantic 0.0% (n=49)

**target**: new 0.0% (n=51); old 0.0% (n=44)

**condition**: clue 0.0% (n=28); contradiction 0.0% (n=13); no-clue 0.0% (n=28); stated 0.0% (n=26)

**clue_type**: code 0.0% (n=11); error 0.0% (n=6); pin 0.0% (n=11); pin-new+code-old 0.0% (n=6); pin-old+code-new 0.0% (n=7)

**exclusivity**: behavior 0.0% (n=14); deprecation 0.0% (n=21); one_directional 0.0% (n=4); removal 0.0% (n=56)

**change_type**: behavior 0.0% (n=14); param_removed 0.0% (n=2); param_rename 0.0% (n=37); param_value 0.0% (n=7); symbol_rename 0.0% (n=35)

**user_arm**: knows 0.0% (n=95)

**gold_examples**: both 0.0% (n=44); neither 0.0% (n=51)

**gold_examples_x_change_type**: both / behavior 0.0% (n=14); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 0.0% (n=21); neither / param_rename 0.0% (n=37); neither / symbol_rename 0.0% (n=14)

### always_ask

**library**: numpy 0.0% (n=16); pandas 0.0% (n=30); pydantic 0.0% (n=49)

**target**: new 0.0% (n=51); old 0.0% (n=44)

**condition**: clue 0.0% (n=28); contradiction 0.0% (n=13); no-clue 0.0% (n=28); stated 0.0% (n=26)

**clue_type**: code 0.0% (n=11); error 0.0% (n=6); pin 0.0% (n=11); pin-new+code-old 0.0% (n=6); pin-old+code-new 0.0% (n=7)

**exclusivity**: behavior 0.0% (n=14); deprecation 0.0% (n=21); one_directional 0.0% (n=4); removal 0.0% (n=56)

**change_type**: behavior 0.0% (n=14); param_removed 0.0% (n=2); param_rename 0.0% (n=37); param_value 0.0% (n=7); symbol_rename 0.0% (n=35)

**user_arm**: knows 0.0% (n=95)

**gold_examples**: both 0.0% (n=44); neither 0.0% (n=51)

**gold_examples_x_change_type**: both / behavior 0.0% (n=14); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 0.0% (n=21); neither / param_rename 0.0% (n=37); neither / symbol_rename 0.0% (n=14)

## What size of difference this run can show

95 targeted instances over 15 concepts (6.3 per concept). Estimated intra-concept correlation rho = 0.000; observed discordant rate against va_rag = 0.000. Miller's formula at 80% power, two-sided 5%:

| discordant rate | rho | detectable difference |
| --- | --- | --- |
| 0.20 | 0.25 | 19.6 points |
| 0.20 | 0.50 | 24.6 points |
| 0.30 | 0.50 | 30.1 points |
