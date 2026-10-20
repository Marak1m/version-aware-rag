# VA-RAG run report: 20261019T232229Z-large-0e385cf8

- Model: `large` = qwen/qwen3-coder
- Split: dev; user arm: knows; instances: 10; concepts: 21; limit 10
- Scoring of deprecation concepts: primary strict (both reported)
- Commit e8b24b65d31f, config a4da4d602744, created 2026-10-19T23:30:33+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen3-coder` pinned to provider `deepinfra/turbo` (no fallbacks, parameters required); session `deepinfra/turbo@20261019T232229Z`; 71 paid calls, 47 cache hits, $0.0113; providers reported {'DeepInfra': 110}

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 100.0% [100.0%, 100.0%] (Wilson 34.2%, 100.0%) | 100.0% | 100.0% | 100.0% | 0.0% | 12.5% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| assume_state | 62.5% [57.1%, 100.0%] (Wilson 21.6%, 98.0%) | 62.5% | 62.5% | 62.5% | 25.0% | 12.5% | 12.5% | 0.0% | 0.0% | 0.0% | 0.0% |
| mind_version | 50.0% [42.9%, 100.0%] (Wilson 18.1%, 96.6%) | 50.0% | 50.0% | 50.0% | 50.0% | 12.5% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| no_retrieval | 50.0% [42.9%, 100.0%] (Wilson 18.1%, 96.6%) | 50.0% | 50.0% | 50.0% | 50.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| oracle_docs | 100.0% [100.0%, 100.0%] (Wilson 34.2%, 100.0%) | 100.0% | 100.0% | 100.0% | 0.0% | 12.5% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| plain_rag | 50.0% [42.9%, 100.0%] (Wilson 18.1%, 96.6%) | 50.0% | 50.0% | 50.0% | 50.0% | 12.5% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| two_branch | 100.0% [100.0%, 100.0%] (Wilson 34.2%, 100.0%) | 100.0% | 100.0% | 100.0% | 0.0% | 12.5% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag | 100.0% [100.0%, 100.0%] (Wilson 34.2%, 100.0%) | 100.0% | 100.0% | 100.0% | 0.0% | 12.5% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_no_ask | 62.5% [57.1%, 100.0%] (Wilson 21.6%, 98.0%) | 62.5% | 62.5% | 62.5% | 37.5% | 12.5% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_no_guard | 100.0% [100.0%, 100.0%] (Wilson 34.2%, 100.0%) | 100.0% | 100.0% | 100.0% | 0.0% | 12.5% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_no_infer | 100.0% [100.0%, 100.0%] (Wilson 34.2%, 100.0%) | 100.0% | 100.0% | 100.0% | 0.0% | 12.5% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% | 100.0% | 30.0% | 100.0% | 100.0% | 0.0% | c=0.0: 100.0%, c=0.1: 90.0%, c=0.3: 70.0% | 1.00 calls, 1.00 answers |
| assume_state | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 62.5%, c=0.1: 62.5%, c=0.3: 62.5% | 1.00 calls, 1.00 answers |
| mind_version | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 50.0%, c=0.1: 50.0%, c=0.3: 50.0% | 1.00 calls, 1.00 answers |
| no_retrieval | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 50.0%, c=0.1: 50.0%, c=0.3: 50.0% | 1.00 calls, 1.00 answers |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 100.0%, c=0.1: 100.0%, c=0.3: 100.0% | 1.00 calls, 1.00 answers |
| plain_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 50.0%, c=0.1: 50.0%, c=0.3: 50.0% | 1.00 calls, 1.00 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 66.7% | c=0.0: 100.0%, c=0.1: 90.0%, c=0.3: 70.0% | 1.80 calls, 1.80 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% | 100.0% | 75.0% | 0.0% | 100.0% | 0.0% | c=0.0: 100.0%, c=0.1: 95.0%, c=0.3: 85.0% | 1.00 calls, 1.00 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 62.5%, c=0.1: 62.5%, c=0.3: 62.5% | 1.00 calls, 1.00 answers |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% | 100.0% | 75.0% | 0.0% | 100.0% | 0.0% | c=0.0: 100.0%, c=0.1: 95.0%, c=0.3: 85.0% | 1.00 calls, 1.00 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 65.8%) | 0.0% | 100.0% | 37.5% | 66.7% | 100.0% | 0.0% | c=0.0: 100.0%, c=0.1: 90.0%, c=0.3: 70.0% | 1.00 calls, 1.00 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | 0.000 | n/a |
| assume_state | old 66.7%, new 0.0%, both 0.0%, neither 33.3% (n=3) | 50.0% | 0.067 | n/a |
| mind_version | old 33.3%, new 33.3%, both 0.0%, neither 33.3% (n=3) | 50.0% | 0.267 | n/a |
| no_retrieval | old 66.7%, new 0.0%, both 0.0%, neither 33.3% (n=3) | 50.0% | -0.267 | n/a |
| oracle_docs | old 33.3%, new 33.3%, both 0.0%, neither 33.3% (n=3) | 100.0% | 0.000 | n/a |
| plain_rag | old 33.3%, new 33.3%, both 0.0%, neither 33.3% (n=3) | 50.0% | 0.267 | n/a |
| two_branch | old 33.3%, new 33.3%, both 0.0%, neither 33.3% (n=3) | 100.0% | 0.000 | 87.5% |
| va_rag |  (n=0) | 100.0% | 0.000 | n/a |
| va_rag_no_ask | old 33.3%, new 33.3%, both 0.0%, neither 33.3% (n=3) | 100.0% | 0.067 | n/a |
| va_rag_no_guard |  (n=0) | 100.0% | 0.000 | n/a |
| va_rag_no_infer |  (n=0) | n/a | 0.000 | n/a |

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | AUROC |margin| | guard flags | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 5, "INFER": 4, "CONTEXT_CONFLICT": 1} | n/a | 0 | n/a | n/a | n/a | n/a |
| va_rag_no_ask | 100.0% | 100.0% | {"UNCERTAIN": 5, "INFER": 4, "CONTEXT_CONFLICT": 1} | n/a | 0 | n/a | 0.0% | n/a | n/a |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 5, "INFER": 4, "CONTEXT_CONFLICT": 1} | n/a | 0 | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 10} | n/a | 0 | n/a | n/a | n/a | n/a |

Risk-coverage sweep on |margin| for `va_rag` (coverage = answered without a question, risk = wrong-version commits among them):

| threshold | coverage | risk |
| --- | --- | --- |
| 6.00 | 25.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |

## Primary contrasts: va_rag against each baseline

Paired bootstrap on per-concept differences (va_rag minus baseline); exact McNemar on instance pairs, Holm-adjusted across the contrasts.

| Baseline | Metric | Difference | 95% bootstrap | discordant (va_rag only / baseline only) | McNemar p | Holm p |
| --- | --- | --- | --- | --- | --- | --- |
| plain_rag | intended_pass | +28.6 pts | [+0.0, +57.1] | 4 / 0 | 0.1250 | 1.0000 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +28.6 pts | [+0.0, +57.1] | 4 / 0 | 0.1250 | 1.0000 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | intended_pass | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 100.0% (n=8)

**target**: new 100.0% (n=4); old 100.0% (n=4)

**condition**: clue 100.0% (n=2); contradiction 100.0% (n=1); no-clue 100.0% (n=3); stated 100.0% (n=2)

**clue_type**: code 100.0% (n=1); pin 100.0% (n=1); pin-old+code-new 100.0% (n=1)

**exclusivity**: behavior 100.0% (n=1); removal 100.0% (n=7)

**change_type**: behavior 100.0% (n=1); symbol_rename 100.0% (n=7)

**user_arm**: knows 100.0% (n=8)

**gold_examples**: both 100.0% (n=8)

**gold_examples_x_change_type**: both / behavior 100.0% (n=1); both / symbol_rename 100.0% (n=7)

### plain_rag

**library**: numpy 50.0% (n=8)

**target**: new 25.0% (n=4); old 75.0% (n=4)

**condition**: clue 50.0% (n=2); contradiction 0.0% (n=1); no-clue 33.3% (n=3); stated 100.0% (n=2)

**clue_type**: code 0.0% (n=1); pin 100.0% (n=1); pin-old+code-new 0.0% (n=1)

**exclusivity**: behavior 100.0% (n=1); removal 42.9% (n=7)

**change_type**: behavior 100.0% (n=1); symbol_rename 42.9% (n=7)

**user_arm**: knows 50.0% (n=8)

**gold_examples**: both 50.0% (n=8)

**gold_examples_x_change_type**: both / behavior 100.0% (n=1); both / symbol_rename 42.9% (n=7)

### mind_version

**library**: numpy 50.0% (n=8)

**target**: new 25.0% (n=4); old 75.0% (n=4)

**condition**: clue 50.0% (n=2); contradiction 0.0% (n=1); no-clue 33.3% (n=3); stated 100.0% (n=2)

**clue_type**: code 0.0% (n=1); pin 100.0% (n=1); pin-old+code-new 0.0% (n=1)

**exclusivity**: behavior 100.0% (n=1); removal 42.9% (n=7)

**change_type**: behavior 100.0% (n=1); symbol_rename 42.9% (n=7)

**user_arm**: knows 50.0% (n=8)

**gold_examples**: both 50.0% (n=8)

**gold_examples_x_change_type**: both / behavior 100.0% (n=1); both / symbol_rename 42.9% (n=7)

### two_branch

**library**: numpy 100.0% (n=8)

**target**: new 100.0% (n=4); old 100.0% (n=4)

**condition**: clue 100.0% (n=2); contradiction 100.0% (n=1); no-clue 100.0% (n=3); stated 100.0% (n=2)

**clue_type**: code 100.0% (n=1); pin 100.0% (n=1); pin-old+code-new 100.0% (n=1)

**exclusivity**: behavior 100.0% (n=1); removal 100.0% (n=7)

**change_type**: behavior 100.0% (n=1); symbol_rename 100.0% (n=7)

**user_arm**: knows 100.0% (n=8)

**gold_examples**: both 100.0% (n=8)

**gold_examples_x_change_type**: both / behavior 100.0% (n=1); both / symbol_rename 100.0% (n=7)

### always_ask

**library**: numpy 100.0% (n=8)

**target**: new 100.0% (n=4); old 100.0% (n=4)

**condition**: clue 100.0% (n=2); contradiction 100.0% (n=1); no-clue 100.0% (n=3); stated 100.0% (n=2)

**clue_type**: code 100.0% (n=1); pin 100.0% (n=1); pin-old+code-new 100.0% (n=1)

**exclusivity**: behavior 100.0% (n=1); removal 100.0% (n=7)

**change_type**: behavior 100.0% (n=1); symbol_rename 100.0% (n=7)

**user_arm**: knows 100.0% (n=8)

**gold_examples**: both 100.0% (n=8)

**gold_examples_x_change_type**: both / behavior 100.0% (n=1); both / symbol_rename 100.0% (n=7)

## What size of difference this run can show

8 targeted instances over 2 concepts (4.0 per concept). Estimated intra-concept correlation rho = 0.000; observed discordant rate against va_rag = 0.225. Miller's formula at 80% power, two-sided 5%:

| discordant rate | rho | detectable difference |
| --- | --- | --- |
| 0.20 | 0.25 | 58.6 points |
| 0.20 | 0.50 | 70.0 points |
| 0.30 | 0.50 | 85.8 points |
| 0.23 | 0.00 | 47.0 points (observed) |
