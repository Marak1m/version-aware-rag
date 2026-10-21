# VA-RAG run report: 20261021T092612Z-mid-04020e62

- Model: `mid` = qwen/qwen-2.5-coder-32b-instruct
- Split: dev; user arm: knows; instances: 20; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T09:33:11+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen-2.5-coder-32b-instruct` pinned to provider `cloudflare` (no fallbacks, parameters required); session `cloudflare@20261021T082811Z`; 191 paid calls, 110 cache hits, $0.1078; providers reported {'Cloudflare': 240}

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 84.2% [64.7%, 100.0%] (Wilson 52.3%, 94.9%) | 84.2% | 84.2% | 84.2% | 0.0% | 21.1% | 15.8% | 0.0% | 0.0% | 0.0% | 0.0% |
| assume_state | 63.2% [35.3%, 85.0%] (Wilson 29.2%, 79.8%) | 63.2% | 63.2% | 63.2% | 10.5% | 15.8% | 26.3% | 0.0% | 0.0% | 0.0% | 0.0% |
| mind_version | 78.9% [61.9%, 94.4%] (Wilson 49.2%, 93.4%) | 78.9% | 78.9% | 78.9% | 5.3% | 21.1% | 15.8% | 0.0% | 0.0% | 0.0% | 0.0% |
| no_retrieval | 47.4% [25.0%, 69.6%] (Wilson 20.2%, 70.8%) | 47.4% | 47.4% | 52.6% | 26.3% | 21.1% | 26.3% | 0.0% | 0.0% | 0.0% | 0.0% |
| oracle_docs | 73.7% [53.3%, 90.0%] (Wilson 40.7%, 88.5%) | 73.7% | 73.7% | 73.7% | 10.5% | 21.1% | 15.8% | 0.0% | 0.0% | 0.0% | 0.0% |
| plain_rag | 63.2% [42.9%, 83.3%] (Wilson 34.1%, 83.9%) | 63.2% | 63.2% | 63.2% | 21.1% | 21.1% | 15.8% | 0.0% | 0.0% | 0.0% | 0.0% |
| two_branch | 84.2% [64.7%, 100.0%] (Wilson 52.3%, 94.9%) | 84.2% | 84.2% | 84.2% | 0.0% | 21.1% | 15.8% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag | 84.2% [64.7%, 100.0%] (Wilson 52.3%, 94.9%) | 84.2% | 84.2% | 84.2% | 0.0% | 21.1% | 15.8% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_no_ask | 78.9% [61.9%, 94.4%] (Wilson 49.2%, 93.4%) | 78.9% | 78.9% | 78.9% | 5.3% | 21.1% | 15.8% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_no_guard | 84.2% [64.7%, 100.0%] (Wilson 52.3%, 94.9%) | 84.2% | 84.2% | 84.2% | 0.0% | 21.1% | 15.8% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_no_infer | 84.2% [64.7%, 100.0%] (Wilson 52.3%, 94.9%) | 84.2% | 84.2% | 84.2% | 0.0% | 21.1% | 15.8% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_portable_first | 89.5% [75.0%, 100.0%] (Wilson 62.3%, 98.4%) | 89.5% | 89.5% | 89.5% | 0.0% | 26.3% | 10.5% | 0.0% | 0.0% | 0.0% | 0.0% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% | 100.0% | 35.0% | 100.0% | n/a | 0.0% | c=0.0: 84.2%, c=0.1: 74.2%, c=0.3: 54.2% | 1.00 calls, 1.00 answers |
| assume_state | 5.3% [0.0%, 16.7%] (Wilson 0.5%, 32.1%) | 5.3% [0.0%, 16.7%] (Wilson 0.5%, 32.1%) | 0.0% | 0.0% | n/a | 0.0% | n/a | 0.0% | c=0.0: 63.2%, c=0.1: 63.2%, c=0.3: 63.2% | 1.00 calls, 1.00 answers |
| mind_version | 5.3% [0.0%, 16.7%] (Wilson 0.5%, 32.1%) | 5.3% [0.0%, 16.7%] (Wilson 0.5%, 32.1%) | 0.0% | 100.0% | 43.8% | 69.2% | n/a | 0.0% | c=0.0: 78.9%, c=0.1: 71.1%, c=0.3: 55.3% | 1.80 calls, 1.00 answers |
| no_retrieval | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% | 42.9% | 33.3% | 61.5% | n/a | 0.0% | c=0.0: 47.4%, c=0.1: 41.1%, c=0.3: 28.4% | 1.60 calls, 1.00 answers |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% | 0.0% | 25.0% | 23.1% | n/a | 0.0% | c=0.0: 73.7%, c=0.1: 71.6%, c=0.3: 67.4% | 1.20 calls, 1.00 answers |
| plain_rag | 5.3% [0.0%, 16.7%] (Wilson 0.5%, 32.1%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% | 28.6% | 40.0% | 23.1% | n/a | 0.0% | c=0.0: 63.2%, c=0.1: 60.5%, c=0.3: 55.3% | 1.25 calls, 1.00 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% | 0.0% | n/a | 0.0% | n/a | 92.3% | c=0.0: 84.2%, c=0.1: 74.2%, c=0.3: 54.2% | 1.95 calls, 1.95 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% | 100.0% | 100.0% | 0.0% | n/a | 0.0% | c=0.0: 84.2%, c=0.1: 80.5%, c=0.3: 73.2% | 1.00 calls, 1.00 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% | 0.0% | n/a | 0.0% | n/a | 0.0% | c=0.0: 78.9%, c=0.1: 78.9%, c=0.3: 78.9% | 1.00 calls, 1.00 answers |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% | 100.0% | 100.0% | 0.0% | n/a | 0.0% | c=0.0: 84.2%, c=0.1: 80.5%, c=0.3: 73.2% | 1.00 calls, 1.00 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% | 100.0% | 36.8% | 92.3% | n/a | 0.0% | c=0.0: 84.2%, c=0.1: 74.2%, c=0.3: 54.2% | 1.00 calls, 1.00 answers |
| va_rag_portable_first | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 25.9%) | 0.0% | 71.4% | 100.0% | 0.0% | n/a | 0.0% | c=0.0: 89.5%, c=0.1: 86.8%, c=0.3: 81.6% | 1.25 calls, 1.00 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | -0.013 | n/a |
| assume_state | old 42.9%, new 14.3%, both 0.0%, neither 42.9% (n=7) | 42.9% | 0.051 | n/a |
| mind_version |  (n=0) | n/a | -0.179 | n/a |
| no_retrieval | old 66.7%, new 0.0%, both 0.0%, neither 33.3% (n=3) | 0.0% | -0.449 | n/a |
| oracle_docs | old 33.3%, new 33.3%, both 0.0%, neither 33.3% (n=6) | 60.0% | -0.103 | n/a |
| plain_rag | old 60.0%, new 20.0%, both 0.0%, neither 20.0% (n=5) | 20.0% | 0.051 | n/a |
| two_branch | old 28.6%, new 28.6%, both 0.0%, neither 42.9% (n=7) | 57.1% | -0.013 | 57.9% |
| va_rag |  (n=0) | 57.1% | -0.013 | n/a |
| va_rag_no_ask | old 57.1%, new 14.3%, both 0.0%, neither 28.6% (n=7) | 57.1% | 0.064 | n/a |
| va_rag_no_guard |  (n=0) | 57.1% | -0.013 | n/a |
| va_rag_no_infer |  (n=0) | n/a | -0.013 | n/a |
| va_rag_portable_first | old 0.0%, new 0.0%, both 0.0%, neither 100.0% (n=2) | 57.1% | -0.090 | n/a |

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision, exclusive-error oracle | guard recall, exclusive-error oracle | guard precision, strict-named oracle | guard recall, strict-named oracle | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 8, "INFER": 12} | {"no_conflict": 1, "inferred": 12, "asked": 7} | n/a | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| va_rag_no_ask | 100.0% | 100.0% | {"UNCERTAIN": 8, "INFER": 12} | {"no_conflict": 1, "inferred": 12, "unresolved": 7} | n/a | 0 | n/a | 0.0% | n/a | 0.0% | n/a | n/a |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 8, "INFER": 12} | {"no_conflict": 1, "inferred": 12, "asked": 7} | n/a | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 20} | {"no_conflict": 1, "asked": 19} | n/a | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| va_rag_portable_first | 100.0% | 100.0% | {"UNCERTAIN": 8, "INFER": 12} | {"no_conflict": 1, "inferred": 12, "asked": 5, "portable": 2} | n/a | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

Guard oracles (`varag.eval.oracle`): exclusive-error (M7) counts a failure whose AttributeError, ImportError or TypeError names an exclusive symbol; strict-named (2026-10-21 correction) counts a strict failure in the committed version whose error, traceback, counted warning or failing line shows the usage, so rejected values and deprecation warnings count too.

Portable-first drafts (`va_rag_portable_first`): 7 drafts, 2 returned without a question (28.6%); rejected: {"exclusive or deprecated usage": 5}.

Risk-coverage sweep on |margin| for `va_rag` (coverage = answered without a question, risk = wrong-version commits among them):

| threshold | coverage | risk |
| --- | --- | --- |
| 11.50 | 8.3% | 0.0% |
| 4.50 | 33.3% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |

## Primary contrasts: va_rag against each baseline

Paired bootstrap on per-concept differences of instance scores (va_rag minus baseline); exact McNemar on the repeat-0 instance pairs, Holm-adjusted across the contrasts.

| Baseline | Metric | Difference | 95% bootstrap | discordant (va_rag only / baseline only) | McNemar p | Holm p |
| --- | --- | --- | --- | --- | --- | --- |
| plain_rag | intended_pass | +19.7 pts | [+0.0, +42.4] | 4 / 0 | 0.1250 | 1.0000 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +3.0 pts | [+0.0, +9.1] | 1 / 0 | 1.0000 | 1.0000 |
| mind_version | blend_exec | -4.5 pts | [-13.6, +0.0] | 0 / 1 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | intended_pass | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 85.7% (n=7); pandas 100.0% (n=3); pydantic 77.8% (n=9)

**target**: new 75.0% (n=8); old 90.9% (n=11)

**condition**: clue 100.0% (n=7); no-clue 71.4% (n=7); stated 80.0% (n=5)

**clue_type**: code 100.0% (n=4); pin 100.0% (n=3)

**exclusivity**: behavior 100.0% (n=3); deprecation 75.0% (n=4); one_directional 0.0% (n=1); removal 90.9% (n=11)

**change_type**: behavior 100.0% (n=3); param_rename 71.4% (n=7); param_value 100.0% (n=1); symbol_rename 87.5% (n=8)

**user_arm**: knows 84.2% (n=19)

**gold_examples**: both 100.0% (n=8); neither 72.7% (n=11)

**gold_examples_x_change_type**: both / behavior 100.0% (n=3); both / param_value 100.0% (n=1); both / symbol_rename 100.0% (n=4); neither / param_rename 71.4% (n=7); neither / symbol_rename 75.0% (n=4)

### plain_rag

**library**: numpy 57.1% (n=7); pandas 100.0% (n=3); pydantic 55.6% (n=9)

**target**: new 50.0% (n=8); old 72.7% (n=11)

**condition**: clue 71.4% (n=7); no-clue 57.1% (n=7); stated 60.0% (n=5)

**clue_type**: code 75.0% (n=4); pin 66.7% (n=3)

**exclusivity**: behavior 100.0% (n=3); deprecation 75.0% (n=4); one_directional 0.0% (n=1); removal 54.5% (n=11)

**change_type**: behavior 100.0% (n=3); param_rename 42.9% (n=7); param_value 100.0% (n=1); symbol_rename 62.5% (n=8)

**user_arm**: knows 63.2% (n=19)

**gold_examples**: both 75.0% (n=8); neither 54.5% (n=11)

**gold_examples_x_change_type**: both / behavior 100.0% (n=3); both / param_value 100.0% (n=1); both / symbol_rename 50.0% (n=4); neither / param_rename 42.9% (n=7); neither / symbol_rename 75.0% (n=4)

### mind_version

**library**: numpy 71.4% (n=7); pandas 100.0% (n=3); pydantic 77.8% (n=9)

**target**: new 62.5% (n=8); old 90.9% (n=11)

**condition**: clue 100.0% (n=7); no-clue 71.4% (n=7); stated 60.0% (n=5)

**clue_type**: code 100.0% (n=4); pin 100.0% (n=3)

**exclusivity**: behavior 100.0% (n=3); deprecation 75.0% (n=4); one_directional 0.0% (n=1); removal 81.8% (n=11)

**change_type**: behavior 100.0% (n=3); param_rename 71.4% (n=7); param_value 100.0% (n=1); symbol_rename 75.0% (n=8)

**user_arm**: knows 78.9% (n=19)

**gold_examples**: both 87.5% (n=8); neither 72.7% (n=11)

**gold_examples_x_change_type**: both / behavior 100.0% (n=3); both / param_value 100.0% (n=1); both / symbol_rename 75.0% (n=4); neither / param_rename 71.4% (n=7); neither / symbol_rename 75.0% (n=4)

### two_branch

**library**: numpy 85.7% (n=7); pandas 100.0% (n=3); pydantic 77.8% (n=9)

**target**: new 75.0% (n=8); old 90.9% (n=11)

**condition**: clue 100.0% (n=7); no-clue 71.4% (n=7); stated 80.0% (n=5)

**clue_type**: code 100.0% (n=4); pin 100.0% (n=3)

**exclusivity**: behavior 100.0% (n=3); deprecation 75.0% (n=4); one_directional 0.0% (n=1); removal 90.9% (n=11)

**change_type**: behavior 100.0% (n=3); param_rename 71.4% (n=7); param_value 100.0% (n=1); symbol_rename 87.5% (n=8)

**user_arm**: knows 84.2% (n=19)

**gold_examples**: both 100.0% (n=8); neither 72.7% (n=11)

**gold_examples_x_change_type**: both / behavior 100.0% (n=3); both / param_value 100.0% (n=1); both / symbol_rename 100.0% (n=4); neither / param_rename 71.4% (n=7); neither / symbol_rename 75.0% (n=4)

### always_ask

**library**: numpy 85.7% (n=7); pandas 100.0% (n=3); pydantic 77.8% (n=9)

**target**: new 75.0% (n=8); old 90.9% (n=11)

**condition**: clue 100.0% (n=7); no-clue 71.4% (n=7); stated 80.0% (n=5)

**clue_type**: code 100.0% (n=4); pin 100.0% (n=3)

**exclusivity**: behavior 100.0% (n=3); deprecation 75.0% (n=4); one_directional 0.0% (n=1); removal 90.9% (n=11)

**change_type**: behavior 100.0% (n=3); param_rename 71.4% (n=7); param_value 100.0% (n=1); symbol_rename 87.5% (n=8)

**user_arm**: knows 84.2% (n=19)

**gold_examples**: both 100.0% (n=8); neither 72.7% (n=11)

**gold_examples_x_change_type**: both / behavior 100.0% (n=3); both / param_value 100.0% (n=1); both / symbol_rename 100.0% (n=4); neither / param_rename 71.4% (n=7); neither / symbol_rename 75.0% (n=4)

## What size of difference this run can show

19 targeted instances over 11 concepts (1.7 per concept). Measured within-concept correlation rho = 0.083 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.096 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.083 | 20.9 points | measured rho |
| 0.200 | 0.083 | 29.6 points | measured rho |
| 0.300 | 0.083 | 36.3 points | measured rho |
| 0.096 | 0.083 | 20.5 points | observed |
| 0.200 | 0.250 | 31.2 points | handoff assumption |
| 0.200 | 0.500 | 33.6 points | handoff assumption |
