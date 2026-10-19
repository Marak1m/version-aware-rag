# VA-RAG run report: 20261019T111345Z-mock_wrong-304f1dc6

- Model: `mock_wrong` = mock
- Split: dev; user arm: knows; instances: 83; concepts: 16
- Scoring of deprecation concepts: primary strict (both reported)
- Commit 9952d4723572, config 8b052d05716c, created 2026-10-19T11:15:14+00:00

> 16 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | strict | lenient | wrong_version | portable | broken | no_code | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 11.0% | 100.0% | 0.0% | 0.0% | 0.0% | n/a |
| assume_state | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 11.0% | 100.0% | 0.0% | 0.0% | 0.0% | n/a |
| mind_version | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 11.0% | 100.0% | 0.0% | 0.0% | 0.0% | n/a |
| no_retrieval | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 11.0% | 100.0% | 0.0% | 0.0% | 0.0% | n/a |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 11.0% | 100.0% | 0.0% | 0.0% | 0.0% | n/a |
| plain_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 11.0% | 100.0% | 0.0% | 0.0% | 0.0% | n/a |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 11.0% | 100.0% | 0.0% | 0.0% | 0.0% | n/a |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 11.0% | 100.0% | 0.0% | 0.0% | 0.0% | n/a |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 11.0% | 100.0% | 0.0% | 0.0% | 0.0% | n/a |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 11.0% | 100.0% | 0.0% | 0.0% | 0.0% | n/a |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 11.0% | 100.0% | 0.0% | 0.0% | 0.0% | n/a |

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 33.7% | 100.0% | 0.0% | c=0.0: 0.0%, c=0.1: -10.0%, c=0.3: -30.0% | 1.00 calls, 1.00 answers |
| assume_state | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | c=0.0: 0.0%, c=0.1: 0.0%, c=0.3: 0.0% | 1.00 calls, 1.00 answers |
| mind_version | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | c=0.0: 0.0%, c=0.1: 0.0%, c=0.3: 0.0% | 1.00 calls, 1.00 answers |
| no_retrieval | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | c=0.0: 0.0%, c=0.1: 0.0%, c=0.3: 0.0% | 1.00 calls, 1.00 answers |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | c=0.0: 0.0%, c=0.1: 0.0%, c=0.3: 0.0% | 1.00 calls, 1.00 answers |
| plain_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | c=0.0: 0.0%, c=0.1: 0.0%, c=0.3: 0.0% | 1.00 calls, 1.00 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 98.2% | c=0.0: 0.0%, c=0.1: -10.0%, c=0.3: -30.0% | 1.99 calls, 1.99 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 100.0% | 0.0% | 0.0% | c=0.0: 0.0%, c=0.1: -3.4%, c=0.3: -10.2% | 1.92 calls, 1.00 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | c=0.0: 0.0%, c=0.1: 0.0%, c=0.3: 0.0% | 1.60 calls, 1.00 answers |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 100.0% | 0.0% | 0.0% | c=0.0: 0.0%, c=0.1: -3.4%, c=0.3: -10.2% | 1.00 calls, 1.00 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 34.1% | 98.2% | 0.0% | c=0.0: 0.0%, c=0.1: -10.0%, c=0.3: -30.0% | 1.92 calls, 1.00 answers |

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
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 29, "INFER": 54} | n/a | 76 | 44.7% | 100.0% | 0.0% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"UNCERTAIN": 29, "INFER": 54} | n/a | 50 | 44.0% | 64.7% | 0.0% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 29, "INFER": 54} | n/a | 0 | n/a | 0.0% | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 83} | n/a | 76 | 44.7% | 100.0% | 0.0% | 0.0% |

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

**library**: numpy 0.0% (n=14); pandas 0.0% (n=26); pydantic 0.0% (n=42)

**target**: new 0.0% (n=43); old 0.0% (n=39)

**condition**: clue 0.0% (n=28); no-clue 0.0% (n=28); stated 0.0% (n=26)

**clue_type**: code 0.0% (n=11); error 0.0% (n=6); pin 0.0% (n=11)

**exclusivity**: behavior 0.0% (n=12); deprecation 0.0% (n=18); one_directional 0.0% (n=4); removal 0.0% (n=48)

**change_type**: behavior 0.0% (n=12); param_removed 0.0% (n=2); param_rename 0.0% (n=32); param_value 0.0% (n=6); symbol_rename 0.0% (n=30)

**user_arm**: knows 0.0% (n=82)

**gold_examples**: both 0.0% (n=38); neither 0.0% (n=44)

**gold_examples_x_change_type**: both / behavior 0.0% (n=12); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=6); both / symbol_rename 0.0% (n=18); neither / param_rename 0.0% (n=32); neither / symbol_rename 0.0% (n=12)

### plain_rag

**library**: numpy 0.0% (n=14); pandas 0.0% (n=26); pydantic 0.0% (n=42)

**target**: new 0.0% (n=43); old 0.0% (n=39)

**condition**: clue 0.0% (n=28); no-clue 0.0% (n=28); stated 0.0% (n=26)

**clue_type**: code 0.0% (n=11); error 0.0% (n=6); pin 0.0% (n=11)

**exclusivity**: behavior 0.0% (n=12); deprecation 0.0% (n=18); one_directional 0.0% (n=4); removal 0.0% (n=48)

**change_type**: behavior 0.0% (n=12); param_removed 0.0% (n=2); param_rename 0.0% (n=32); param_value 0.0% (n=6); symbol_rename 0.0% (n=30)

**user_arm**: knows 0.0% (n=82)

**gold_examples**: both 0.0% (n=38); neither 0.0% (n=44)

**gold_examples_x_change_type**: both / behavior 0.0% (n=12); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=6); both / symbol_rename 0.0% (n=18); neither / param_rename 0.0% (n=32); neither / symbol_rename 0.0% (n=12)

### mind_version

**library**: numpy 0.0% (n=14); pandas 0.0% (n=26); pydantic 0.0% (n=42)

**target**: new 0.0% (n=43); old 0.0% (n=39)

**condition**: clue 0.0% (n=28); no-clue 0.0% (n=28); stated 0.0% (n=26)

**clue_type**: code 0.0% (n=11); error 0.0% (n=6); pin 0.0% (n=11)

**exclusivity**: behavior 0.0% (n=12); deprecation 0.0% (n=18); one_directional 0.0% (n=4); removal 0.0% (n=48)

**change_type**: behavior 0.0% (n=12); param_removed 0.0% (n=2); param_rename 0.0% (n=32); param_value 0.0% (n=6); symbol_rename 0.0% (n=30)

**user_arm**: knows 0.0% (n=82)

**gold_examples**: both 0.0% (n=38); neither 0.0% (n=44)

**gold_examples_x_change_type**: both / behavior 0.0% (n=12); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=6); both / symbol_rename 0.0% (n=18); neither / param_rename 0.0% (n=32); neither / symbol_rename 0.0% (n=12)

### two_branch

**library**: numpy 0.0% (n=14); pandas 0.0% (n=26); pydantic 0.0% (n=42)

**target**: new 0.0% (n=43); old 0.0% (n=39)

**condition**: clue 0.0% (n=28); no-clue 0.0% (n=28); stated 0.0% (n=26)

**clue_type**: code 0.0% (n=11); error 0.0% (n=6); pin 0.0% (n=11)

**exclusivity**: behavior 0.0% (n=12); deprecation 0.0% (n=18); one_directional 0.0% (n=4); removal 0.0% (n=48)

**change_type**: behavior 0.0% (n=12); param_removed 0.0% (n=2); param_rename 0.0% (n=32); param_value 0.0% (n=6); symbol_rename 0.0% (n=30)

**user_arm**: knows 0.0% (n=82)

**gold_examples**: both 0.0% (n=38); neither 0.0% (n=44)

**gold_examples_x_change_type**: both / behavior 0.0% (n=12); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=6); both / symbol_rename 0.0% (n=18); neither / param_rename 0.0% (n=32); neither / symbol_rename 0.0% (n=12)

### always_ask

**library**: numpy 0.0% (n=14); pandas 0.0% (n=26); pydantic 0.0% (n=42)

**target**: new 0.0% (n=43); old 0.0% (n=39)

**condition**: clue 0.0% (n=28); no-clue 0.0% (n=28); stated 0.0% (n=26)

**clue_type**: code 0.0% (n=11); error 0.0% (n=6); pin 0.0% (n=11)

**exclusivity**: behavior 0.0% (n=12); deprecation 0.0% (n=18); one_directional 0.0% (n=4); removal 0.0% (n=48)

**change_type**: behavior 0.0% (n=12); param_removed 0.0% (n=2); param_rename 0.0% (n=32); param_value 0.0% (n=6); symbol_rename 0.0% (n=30)

**user_arm**: knows 0.0% (n=82)

**gold_examples**: both 0.0% (n=38); neither 0.0% (n=44)

**gold_examples_x_change_type**: both / behavior 0.0% (n=12); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=6); both / symbol_rename 0.0% (n=18); neither / param_rename 0.0% (n=32); neither / symbol_rename 0.0% (n=12)

## What size of difference this run can show

82 targeted instances over 15 concepts (5.5 per concept). Estimated intra-concept correlation rho = 0.000; observed discordant rate against va_rag = 0.000. Miller's formula at 80% power, two-sided 5%:

| discordant rate | rho | detectable difference |
| --- | --- | --- |
| 0.20 | 0.25 | 20.1 points |
| 0.20 | 0.50 | 24.9 points |
| 0.30 | 0.50 | 30.5 points |
