# VA-RAG run report: 20261021T085318Z-small-b8bb67b6

- Model: `small` = qwen/qwen-2.5-7b-instruct
- Split: dev; user arm: knows; instances: 101; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T09:23:02+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen-2.5-7b-instruct` pinned to provider `phala` (no fallbacks, parameters required); session `phala@20261021T082811Z`; 2306 paid calls, 1907 cache hits, $0.2198; providers reported {'Phala': 3636}
- Provider choice: qwen/qwen2.5-coder-7b-instruct had no live endpoint on 2026-10-19, so the general 7B instruct model stands in

- Repeats: every (instance, method) answered under repeat indices [0, 1, 2] in one session; an instance's score is the mean over its repeats, rates are means of instance scores, and intervals resample concepts.

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 53.3% [35.1%, 70.0%] (Wilson 27.3%, 72.5%) | 55.8% | 47.7% | 53.3% | 9.5% | 12.3% | 32.3% | 4.9% | 0.0% | 0.0% | 13.1% |
| assume_state | 37.2% [24.3%, 50.0%] (Wilson 15.4%, 58.6%) | 37.4% | 32.3% | 37.2% | 22.8% | 8.1% | 36.8% | 3.2% | 0.0% | 0.0% | 14.3% |
| mind_version | 44.2% [28.1%, 59.7%] (Wilson 21.6%, 66.3%) | 48.9% | 35.1% | 46.0% | 20.0% | 16.5% | 25.6% | 10.2% | 0.0% | 0.0% | 20.8% |
| no_retrieval | 37.5% [22.6%, 52.6%] (Wilson 17.2%, 61.0%) | 39.6% | 35.4% | 43.9% | 23.5% | 17.5% | 31.6% | 7.4% | 0.0% | 0.0% | 5.0% |
| oracle_docs | 55.4% [36.8%, 72.3%] (Wilson 27.5%, 72.7%) | 60.5% | 45.6% | 55.4% | 10.2% | 11.2% | 24.6% | 9.8% | 0.0% | 0.0% | 17.3% |
| plain_rag | 38.6% [22.2%, 55.0%] (Wilson 16.3%, 59.7%) | 40.7% | 31.9% | 38.9% | 24.6% | 16.1% | 28.4% | 8.4% | 0.0% | 0.0% | 17.5% |
| two_branch | 53.3% [35.1%, 70.0%] (Wilson 27.3%, 72.5%) | 55.8% | 47.7% | 53.3% | 9.5% | 12.3% | 32.3% | 4.9% | 0.0% | 0.0% | 13.1% |
| va_rag | 59.6% [38.5%, 79.3%] (Wilson 34.6%, 79.3%) | 63.4% | 55.4% | 59.6% | 3.5% | 12.6% | 30.5% | 6.3% | 0.0% | 0.0% | 8.7% |
| va_rag_no_ask | 49.5% [33.3%, 64.4%] (Wilson 25.2%, 70.3%) | 50.7% | 44.6% | 49.5% | 14.7% | 12.3% | 31.9% | 3.9% | 0.0% | 0.0% | 13.5% |
| va_rag_no_guard | 54.7% [34.7%, 73.7%] (Wilson 28.3%, 73.5%) | 58.2% | 49.8% | 54.7% | 8.4% | 11.2% | 30.5% | 6.3% | 0.0% | 0.0% | 11.1% |
| va_rag_no_infer | 59.6% [38.5%, 79.3%] (Wilson 34.6%, 79.3%) | 63.4% | 55.4% | 59.6% | 3.5% | 12.6% | 30.5% | 6.3% | 0.0% | 0.0% | 8.7% |
| va_rag_portable_first | 60.4% [40.4%, 78.9%] (Wilson 33.8%, 78.6%) | 64.1% | 56.1% | 60.4% | 2.5% | 12.3% | 30.9% | 6.3% | 0.0% | 0.0% | 8.6% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.4% [0.0%, 1.1%] (Wilson 0.0%, 20.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 27.7% | 100.0% | 100.0% | 0.0% | c=0.0: 53.3%, c=0.1: 43.3%, c=0.3: 23.3% | 1.00 calls, 1.00 answers |
| assume_state | 0.7% [0.0%, 1.8%] (Wilson 0.0%, 21.4%) | 0.4% [0.0%, 1.1%] (Wilson 0.0%, 20.9%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 37.2%, c=0.1: 37.2%, c=0.3: 37.2% | 1.00 calls, 0.99 answers |
| mind_version | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 28.6% | 30.8% | 25.0% | 23.1% | 0.0% | c=0.0: 44.2%, c=0.1: 41.8%, c=0.3: 36.9% | 1.26 calls, 1.00 answers |
| no_retrieval | 0.7% [0.0%, 2.2%] (Wilson 0.0%, 21.4%) | 0.7% [0.0%, 2.2%] (Wilson 0.0%, 21.4%) | 0.0% | 0.0% | 0.0% | 1.7% | 15.4% | 0.0% | c=0.0: 37.5%, c=0.1: 37.2%, c=0.3: 36.6% | 1.03 calls, 1.00 answers |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 55.4%, c=0.1: 55.4%, c=0.3: 55.4% | 1.00 calls, 1.00 answers |
| plain_rag | 0.7% [0.0%, 2.2%] (Wilson 0.0%, 21.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 38.6%, c=0.1: 38.6%, c=0.3: 38.6% | 1.00 calls, 1.00 answers |
| two_branch | 0.4% [0.0%, 1.1%] (Wilson 0.0%, 20.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 93.3% | c=0.0: 53.3%, c=0.1: 43.3%, c=0.3: 23.3% | 1.96 calls, 1.96 answers |
| va_rag | 0.4% [0.0%, 1.1%] (Wilson 0.0%, 20.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 0.0% | c=0.0: 59.6%, c=0.1: 55.3%, c=0.3: 46.7% | 1.11 calls, 1.00 answers |
| va_rag_no_ask | 0.4% [0.0%, 1.1%] (Wilson 0.0%, 20.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 49.5%, c=0.1: 49.5%, c=0.3: 49.5% | 1.07 calls, 1.00 answers |
| va_rag_no_guard | 0.4% [0.0%, 1.1%] (Wilson 0.0%, 20.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 0.0% | c=0.0: 54.7%, c=0.1: 50.4%, c=0.3: 41.8% | 1.00 calls, 1.00 answers |
| va_rag_no_infer | 0.4% [0.0%, 1.1%] (Wilson 0.0%, 20.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 28.9% | 93.3% | 100.0% | 0.0% | c=0.0: 59.6%, c=0.1: 49.6%, c=0.3: 29.6% | 1.11 calls, 1.00 answers |
| va_rag_portable_first | 0.4% [0.0%, 1.1%] (Wilson 0.0%, 20.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 65.5% | 65.5% | 0.0% | 71.8% | 0.0% | c=0.0: 60.4%, c=0.1: 57.4%, c=0.3: 51.6% | 1.36 calls, 1.00 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | -0.037 | n/a |
| assume_state | old 34.5%, new 26.2%, both 0.0%, neither 39.3% (n=84) | 33.3% | 0.161 | n/a |
| mind_version | old 11.7%, new 36.7%, both 0.0%, neither 51.7% (n=60) | 35.0% | -0.020 | n/a |
| no_retrieval | old 34.5%, new 2.4%, both 0.0%, neither 63.1% (n=84) | 27.2% | 0.012 | n/a |
| oracle_docs | old 31.0%, new 31.0%, both 0.0%, neither 38.1% (n=84) | 50.0% | -0.031 | n/a |
| plain_rag | old 28.6%, new 38.1%, both 0.0%, neither 33.3% (n=84) | 33.3% | -0.021 | n/a |
| two_branch | old 22.6%, new 38.1%, both 0.0%, neither 39.3% (n=84) | 48.8% | -0.037 | 44.9% |
| va_rag |  (n=0) | 57.1% | -0.020 | n/a |
| va_rag_no_ask | old 29.8%, new 41.7%, both 0.0%, neither 28.6% (n=84) | 57.1% | -0.084 | n/a |
| va_rag_no_guard |  (n=0) | 52.4% | -0.033 | n/a |
| va_rag_no_infer |  (n=0) | n/a | -0.020 | n/a |
| va_rag_portable_first | old 0.0%, new 0.0%, both 0.0%, neither 100.0% (n=29) | 57.1% | -0.032 | n/a |

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision, exclusive-error oracle | guard recall, exclusive-error oracle | guard precision, strict-named oracle | guard recall, strict-named oracle | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | {"no_conflict": 12, "asked": 129, "inferred": 162} | n/a | 34 | 64.7% | 81.5% | 82.4% | 90.3% | 41.2% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | {"no_conflict": 12, "unresolved": 129, "inferred": 162} | n/a | 21 | 66.7% | 27.5% | 100.0% | 29.6% | 42.9% | 4.8% |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | {"no_conflict": 12, "asked": 129, "inferred": 162} | n/a | 0 | n/a | 0.0% | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 101} | {"no_conflict": 12, "asked": 291} | n/a | 34 | 64.7% | 81.5% | 82.4% | 90.3% | 41.2% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | {"no_conflict": 12, "asked": 83, "inferred": 162, "portable": 46} | n/a | 27 | 66.7% | 85.7% | 88.9% | 88.9% | 48.1% | 0.0% |

Guard oracles (`varag.eval.oracle`): exclusive-error (M7) counts a failure whose AttributeError, ImportError or TypeError names an exclusive symbol; strict-named (2026-10-21 correction) counts a strict failure in the committed version whose error, traceback, counted warning or failing line shows the usage, so rejected values and deprecation warnings count too.

Portable-first drafts (`va_rag_portable_first`): 129 drafts, 46 returned without a question (35.7%); rejected: {"exclusive or deprecated usage": 83}.

Risk-coverage sweep on |margin| for `va_rag` (coverage = answered without a question, risk = wrong-version commits among them):

| threshold | coverage | risk |
| --- | --- | --- |
| 11.50 | 1.9% | 0.0% |
| 3.00 | 27.8% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |

## Primary contrasts: va_rag against each baseline

Paired bootstrap on per-concept differences of instance scores (va_rag minus baseline); exact McNemar on the repeat-0 instance pairs, Holm-adjusted across the contrasts.

| Baseline | Metric | Difference | 95% bootstrap | discordant (va_rag only / baseline only) | McNemar p | Holm p |
| --- | --- | --- | --- | --- | --- | --- |
| plain_rag | intended_pass | +23.8 pts | [+6.7, +42.2] | 23 / 3 | 0.0001 | 0.0007 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +16.3 pts | [+0.6, +32.1] | 24 / 8 | 0.0070 | 0.0490 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +8.9 pts | [-0.0, +20.0] | 6 / 1 | 0.1250 | 0.7500 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | intended_pass | +8.9 pts | [-0.0, +20.0] | 6 / 1 | 0.1250 | 0.7500 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 72.9% (n=16); pandas 54.4% (n=30); pydantic 58.5% (n=49)

**target**: new 58.2% (n=51); old 61.4% (n=44)

**condition**: clue 60.7% (n=28); contradiction 46.2% (n=13); no-clue 63.1% (n=28); stated 61.5% (n=26)

**clue_type**: code 60.6% (n=11); error 66.7% (n=6); pin 57.6% (n=11); pin-new+code-old 33.3% (n=6); pin-old+code-new 57.1% (n=7)

**exclusivity**: behavior 35.7% (n=14); deprecation 63.5% (n=21); one_directional 50.0% (n=4); removal 64.9% (n=56)

**change_type**: behavior 35.7% (n=14); param_removed 100.0% (n=2); param_rename 46.8% (n=37); param_value 0.0% (n=7); symbol_rename 92.4% (n=35)

**user_arm**: knows 59.6% (n=95)

**gold_examples**: both 63.6% (n=44); neither 56.2% (n=51)

**gold_examples_x_change_type**: both / behavior 35.7% (n=14); both / param_removed 100.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 46.8% (n=37); neither / symbol_rename 81.0% (n=14)

### plain_rag

**library**: numpy 54.2% (n=16); pandas 43.3% (n=30); pydantic 30.6% (n=49)

**target**: new 30.7% (n=51); old 47.7% (n=44)

**condition**: clue 42.9% (n=28); contradiction 28.2% (n=13); no-clue 33.3% (n=28); stated 44.9% (n=26)

**clue_type**: code 33.3% (n=11); error 38.9% (n=6); pin 54.5% (n=11); pin-new+code-old 33.3% (n=6); pin-old+code-new 23.8% (n=7)

**exclusivity**: behavior 61.9% (n=14); deprecation 31.7% (n=21); one_directional 0.0% (n=4); removal 38.1% (n=56)

**change_type**: behavior 61.9% (n=14); param_removed 0.0% (n=2); param_rename 27.9% (n=37); param_value 0.0% (n=7); symbol_rename 50.5% (n=35)

**user_arm**: knows 38.6% (n=95)

**gold_examples**: both 42.4% (n=44); neither 35.3% (n=51)

**gold_examples_x_change_type**: both / behavior 61.9% (n=14); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 47.6% (n=21); neither / param_rename 27.9% (n=37); neither / symbol_rename 54.8% (n=14)

### mind_version

**library**: numpy 60.4% (n=16); pandas 45.6% (n=30); pydantic 38.1% (n=49)

**target**: new 39.9% (n=51); old 49.2% (n=44)

**condition**: clue 51.2% (n=28); contradiction 28.2% (n=13); no-clue 38.1% (n=28); stated 51.3% (n=26)

**clue_type**: code 48.5% (n=11); error 33.3% (n=6); pin 63.6% (n=11); pin-new+code-old 33.3% (n=6); pin-old+code-new 23.8% (n=7)

**exclusivity**: behavior 64.3% (n=14); deprecation 34.9% (n=21); one_directional 25.0% (n=4); removal 44.0% (n=56)

**change_type**: behavior 64.3% (n=14); param_removed 50.0% (n=2); param_rename 33.3% (n=37); param_value 0.0% (n=7); symbol_rename 56.2% (n=35)

**user_arm**: knows 44.2% (n=95)

**gold_examples**: both 47.7% (n=44); neither 41.2% (n=51)

**gold_examples_x_change_type**: both / behavior 64.3% (n=14); both / param_removed 50.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 52.4% (n=21); neither / param_rename 33.3% (n=37); neither / symbol_rename 61.9% (n=14)

### two_branch

**library**: numpy 72.9% (n=16); pandas 35.6% (n=30); pydantic 57.8% (n=49)

**target**: new 49.7% (n=51); old 57.6% (n=44)

**condition**: clue 50.0% (n=28); contradiction 35.9% (n=13); no-clue 60.7% (n=28); stated 57.7% (n=26)

**clue_type**: code 42.4% (n=11); error 50.0% (n=6); pin 57.6% (n=11); pin-new+code-old 38.9% (n=6); pin-old+code-new 33.3% (n=7)

**exclusivity**: behavior 35.7% (n=14); deprecation 58.7% (n=21); one_directional 16.7% (n=4); removal 58.3% (n=56)

**change_type**: behavior 35.7% (n=14); param_removed 33.3% (n=2); param_rename 47.7% (n=37); param_value 0.0% (n=7); symbol_rename 78.1% (n=35)

**user_arm**: knows 53.3% (n=95)

**gold_examples**: both 50.8% (n=44); neither 55.6% (n=51)

**gold_examples_x_change_type**: both / behavior 35.7% (n=14); both / param_removed 33.3% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 79.4% (n=21); neither / param_rename 47.7% (n=37); neither / symbol_rename 76.2% (n=14)

### always_ask

**library**: numpy 72.9% (n=16); pandas 35.6% (n=30); pydantic 57.8% (n=49)

**target**: new 49.7% (n=51); old 57.6% (n=44)

**condition**: clue 50.0% (n=28); contradiction 35.9% (n=13); no-clue 60.7% (n=28); stated 57.7% (n=26)

**clue_type**: code 42.4% (n=11); error 50.0% (n=6); pin 57.6% (n=11); pin-new+code-old 38.9% (n=6); pin-old+code-new 33.3% (n=7)

**exclusivity**: behavior 35.7% (n=14); deprecation 58.7% (n=21); one_directional 16.7% (n=4); removal 58.3% (n=56)

**change_type**: behavior 35.7% (n=14); param_removed 33.3% (n=2); param_rename 47.7% (n=37); param_value 0.0% (n=7); symbol_rename 78.1% (n=35)

**user_arm**: knows 53.3% (n=95)

**gold_examples**: both 50.8% (n=44); neither 55.6% (n=51)

**gold_examples_x_change_type**: both / behavior 35.7% (n=14); both / param_removed 33.3% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 79.4% (n=21); neither / param_rename 47.7% (n=37); neither / symbol_rename 76.2% (n=14)

## What size of difference this run can show

95 targeted instances over 15 concepts (6.3 per concept), 3 repeats averaged per instance. Measured within-concept correlation rho = 0.450 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.168 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.450 | 16.8 points | measured rho |
| 0.200 | 0.450 | 23.7 points | measured rho |
| 0.300 | 0.450 | 29.0 points | measured rho |
| 0.168 | 0.450 | 21.7 points | observed |
| 0.200 | 0.250 | 19.6 points | handoff assumption |
| 0.200 | 0.500 | 24.6 points | handoff assumption |

## Repeat disagreement (within this session)

1212 (instance, method) pairs answered under 3 repeats: response text differs on 51.0%, outcome on 18.5%, intended-version pass on 11.1%.

| Method | pairs | text differs | outcome differs |
| --- | --- | --- | --- |
| always_ask | 101 | 47.5% | 18.8% |
| assume_state | 101 | 81.2% | 26.7% |
| mind_version | 101 | 53.5% | 21.8% |
| no_retrieval | 101 | 33.7% | 14.9% |
| oracle_docs | 101 | 40.6% | 12.9% |
| plain_rag | 101 | 50.5% | 24.8% |
| two_branch | 101 | 67.3% | 18.8% |
| va_rag | 101 | 48.5% | 15.8% |
| va_rag_no_ask | 101 | 46.5% | 18.8% |
| va_rag_no_guard | 101 | 48.5% | 17.8% |
| va_rag_no_infer | 101 | 48.5% | 15.8% |
| va_rag_portable_first | 101 | 45.5% | 14.9% |
