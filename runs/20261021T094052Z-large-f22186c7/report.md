# VA-RAG run report: 20261021T094052Z-large-f22186c7

- Model: `large` = qwen/qwen3-coder
- Split: dev; user arm: unsure; instances: 101; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T09:52:43+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen3-coder` pinned to provider `deepinfra/turbo` (no fallbacks, parameters required), served as fp4; session `deepinfra/turbo@20261021T082811Z`; 236 paid calls, 4475 cache hits, $0.0551; providers reported {'DeepInfra': 3636}
- Provider choice: served as fp4 by DeepInfra; Google Vertex was rejected because it accepts repetition_penalty and ignores it (probe of 2026-10-19: 1.0 and 2.0 gave the same text)

- Repeats: every (instance, method) answered under repeat indices [0, 1, 2] in one session; an instance's score is the mean over its repeats, rates are means of instance scores, and intervals resample concepts.

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 69.5% [59.2%, 79.6%] (Wilson 44.8%, 87.0%) | 69.5% | 64.6% | 71.6% | 21.8% | 20.4% | 8.8% | 0.0% | 0.0% | 0.0% | 7.4% |
| assume_state | 69.1% [59.6%, 78.3%] (Wilson 44.5%, 86.8%) | 69.1% | 66.0% | 71.2% | 19.3% | 18.2% | 11.6% | 0.0% | 0.0% | 0.0% | 4.6% |
| mind_version | 72.3% [59.6%, 83.7%] (Wilson 47.3%, 88.6%) | 72.3% | 67.0% | 75.4% | 15.1% | 23.9% | 12.6% | 0.0% | 0.0% | 0.0% | 7.4% |
| no_retrieval | 53.7% [46.0%, 61.1%] (Wilson 30.1%, 75.2%) | 53.7% | 50.2% | 56.5% | 26.0% | 11.2% | 20.4% | 0.0% | 0.0% | 0.0% | 7.0% |
| oracle_docs | 85.6% [75.0%, 95.2%] (Wilson 62.5%, 96.4%) | 85.6% | 82.5% | 85.6% | 0.0% | 15.1% | 14.4% | 0.0% | 0.0% | 0.0% | 3.4% |
| plain_rag | 69.5% [58.4%, 80.0%] (Wilson 44.8%, 87.0%) | 69.5% | 64.9% | 71.6% | 17.9% | 22.8% | 12.6% | 0.0% | 0.0% | 0.0% | 6.1% |
| two_branch | 82.5% [68.7%, 94.4%] (Wilson 59.3%, 95.1%) | 82.5% | 78.2% | 82.5% | 1.1% | 16.1% | 16.5% | 0.0% | 0.0% | 0.0% | 4.9% |
| va_rag | 82.8% [69.8%, 94.2%] (Wilson 59.6%, 95.2%) | 82.8% | 81.8% | 82.8% | 0.0% | 15.4% | 17.2% | 0.0% | 0.0% | 0.0% | 1.2% |
| va_rag_no_ask | 70.9% [60.0%, 81.0%] (Wilson 46.0%, 87.8%) | 70.9% | 69.5% | 71.9% | 16.1% | 15.4% | 13.0% | 0.0% | 0.0% | 0.0% | 2.3% |
| va_rag_no_guard | 82.8% [69.8%, 94.2%] (Wilson 59.6%, 95.2%) | 82.8% | 78.6% | 82.8% | 0.0% | 15.4% | 17.2% | 0.0% | 0.0% | 0.0% | 4.9% |
| va_rag_no_infer | 82.8% [69.8%, 94.2%] (Wilson 59.6%, 95.2%) | 82.8% | 81.8% | 82.8% | 0.0% | 15.4% | 17.2% | 0.0% | 0.0% | 0.0% | 1.2% |
| va_rag_portable_first | 77.5% [64.4%, 89.7%] (Wilson 54.5%, 92.8%) | 77.5% | 77.5% | 77.5% | 1.4% | 14.4% | 21.1% | 0.0% | 0.0% | 0.0% | 0.0% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 27.7% | 100.0% | 100.0% | 0.0% | c=0.0: 69.5%, c=0.1: 59.5%, c=0.3: 39.5% | 1.00 calls, 1.00 answers |
| assume_state | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 69.1%, c=0.1: 69.1%, c=0.3: 69.1% | 1.00 calls, 1.00 answers |
| mind_version | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 0.0% | 3.9% | 0.0% | 0.0% | c=0.0: 72.3%, c=0.1: 72.0%, c=0.3: 71.5% | 1.02 calls, 1.00 answers |
| no_retrieval | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 53.7%, c=0.1: 53.7%, c=0.3: 53.7% | 1.00 calls, 1.00 answers |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 85.6%, c=0.1: 85.6%, c=0.3: 85.6% | 1.00 calls, 1.00 answers |
| plain_rag | 1.4% [0.0%, 4.4%] (Wilson 0.1%, 22.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 69.5%, c=0.1: 69.5%, c=0.3: 69.5% | 1.00 calls, 1.00 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 93.3% | c=0.0: 82.5%, c=0.1: 72.5%, c=0.3: 52.5% | 1.96 calls, 1.96 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 3.3% | c=0.0: 82.8%, c=0.1: 78.5%, c=0.3: 69.9% | 1.47 calls, 1.43 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 70.9%, c=0.1: 70.9%, c=0.3: 70.9% | 1.02 calls, 1.00 answers |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 3.3% | c=0.0: 82.8%, c=0.1: 78.5%, c=0.3: 69.9% | 1.43 calls, 1.43 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 28.9% | 93.3% | 100.0% | 93.3% | c=0.0: 82.8%, c=0.1: 72.8%, c=0.3: 52.8% | 2.03 calls, 1.96 answers |
| va_rag_portable_first | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 72.6% | 70.0% | 0.0% | 66.7% | 0.0% | c=0.0: 77.5%, c=0.1: 74.5%, c=0.3: 68.4% | 1.62 calls, 1.29 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | 0.022 | n/a |
| assume_state | old 11.9%, new 53.6%, both 0.0%, neither 34.5% (n=84) | 41.7% | 0.043 | n/a |
| mind_version | old 11.9%, new 38.1%, both 0.0%, neither 50.0% (n=84) | 36.4% | 0.059 | n/a |
| no_retrieval | old 27.4%, new 28.6%, both 0.0%, neither 44.0% (n=84) | 34.5% | -0.058 | n/a |
| oracle_docs | old 21.4%, new 40.5%, both 0.0%, neither 38.1% (n=84) | 56.0% | -0.090 | n/a |
| plain_rag | old 11.9%, new 42.9%, both 4.8%, neither 40.5% (n=84) | 35.7% | 0.036 | n/a |
| two_branch | old 21.4%, new 36.9%, both 0.0%, neither 41.7% (n=84) | 53.6% | -0.049 | 70.2% |
| va_rag |  (n=0) | 56.0% | -0.055 | 79.7% |
| va_rag_no_ask | old 15.5%, new 48.8%, both 0.0%, neither 35.7% (n=84) | 56.0% | 0.012 | n/a |
| va_rag_no_guard |  (n=0) | 56.0% | -0.055 | 79.7% |
| va_rag_no_infer |  (n=0) | n/a | -0.055 | 72.6% |
| va_rag_portable_first | old 0.0%, new 0.0%, both 0.0%, neither 100.0% (n=23) | 56.0% | -0.091 | 80.0% |

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | {"no_conflict": 12, "both": 129, "inferred": 162} | n/a | 9 | 0.0% | n/a | 0.0% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | {"no_conflict": 12, "unresolved": 129, "inferred": 162} | n/a | 6 | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | {"no_conflict": 12, "both": 129, "inferred": 162} | n/a | 0 | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 101} | {"no_conflict": 12, "both": 291} | n/a | 9 | 0.0% | n/a | 0.0% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | {"no_conflict": 12, "both": 87, "inferred": 162, "portable": 42} | n/a | 9 | 0.0% | n/a | 0.0% | 0.0% |

Portable-first drafts (`va_rag_portable_first`): 129 drafts, 42 returned without a question (32.6%); rejected: {"exclusive or deprecated usage": 87}.

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
| plain_rag | intended_pass | +14.4 pts | [+2.5, +26.2] | 15 / 6 | 0.0784 | 0.5485 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +11.9 pts | [-0.8, +24.1] | 15 / 9 | 0.3075 | 1.0000 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +0.3 pts | [-1.9, +2.5] | 0 / 1 | 1.0000 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | intended_pass | +14.4 pts | [+1.9, +27.3] | 21 / 9 | 0.0428 | 0.3422 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 85.4% (n=16); pandas 82.2% (n=30); pydantic 82.3% (n=49)

**target**: new 84.3% (n=51); old 81.1% (n=44)

**condition**: clue 78.6% (n=28); contradiction 79.5% (n=13); no-clue 91.7% (n=28); stated 79.5% (n=26)

**clue_type**: code 69.7% (n=11); error 72.2% (n=6); pin 90.9% (n=11); pin-new+code-old 61.1% (n=6); pin-old+code-new 95.2% (n=7)

**exclusivity**: behavior 71.4% (n=14); deprecation 85.7% (n=21); one_directional 100.0% (n=4); removal 83.3% (n=56)

**change_type**: behavior 71.4% (n=14); param_removed 100.0% (n=2); param_rename 67.6% (n=37); param_value 95.2% (n=7); symbol_rename 100.0% (n=35)

**user_arm**: unsure 82.8% (n=95)

**gold_examples**: both 90.2% (n=44); neither 76.5% (n=51)

**gold_examples_x_change_type**: both / behavior 71.4% (n=14); both / param_removed 100.0% (n=2); both / param_value 95.2% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 67.6% (n=37); neither / symbol_rename 100.0% (n=14)

### plain_rag

**library**: numpy 75.0% (n=16); pandas 71.1% (n=30); pydantic 66.7% (n=49)

**target**: new 71.9% (n=51); old 66.7% (n=44)

**condition**: clue 65.5% (n=28); contradiction 64.1% (n=13); no-clue 64.3% (n=28); stated 82.1% (n=26)

**clue_type**: code 48.5% (n=11); error 50.0% (n=6); pin 90.9% (n=11); pin-new+code-old 72.2% (n=6); pin-old+code-new 57.1% (n=7)

**exclusivity**: behavior 81.0% (n=14); deprecation 76.2% (n=21); one_directional 75.0% (n=4); removal 63.7% (n=56)

**change_type**: behavior 81.0% (n=14); param_removed 50.0% (n=2); param_rename 59.5% (n=37); param_value 85.7% (n=7); symbol_rename 73.3% (n=35)

**user_arm**: unsure 69.5% (n=95)

**gold_examples**: both 75.8% (n=44); neither 64.1% (n=51)

**gold_examples_x_change_type**: both / behavior 81.0% (n=14); both / param_removed 50.0% (n=2); both / param_value 85.7% (n=7); both / symbol_rename 71.4% (n=21); neither / param_rename 59.5% (n=37); neither / symbol_rename 76.2% (n=14)

### mind_version

**library**: numpy 75.0% (n=16); pandas 78.9% (n=30); pydantic 67.3% (n=49)

**target**: new 73.2% (n=51); old 71.2% (n=44)

**condition**: clue 71.4% (n=28); contradiction 71.8% (n=13); no-clue 59.5% (n=28); stated 87.2% (n=26)

**clue_type**: code 69.7% (n=11); error 50.0% (n=6); pin 84.8% (n=11); pin-new+code-old 83.3% (n=6); pin-old+code-new 61.9% (n=7)

**exclusivity**: behavior 92.9% (n=14); deprecation 71.4% (n=21); one_directional 75.0% (n=4); removal 67.3% (n=56)

**change_type**: behavior 92.9% (n=14); param_removed 50.0% (n=2); param_rename 62.2% (n=37); param_value 81.0% (n=7); symbol_rename 74.3% (n=35)

**user_arm**: unsure 72.3% (n=95)

**gold_examples**: both 78.8% (n=44); neither 66.7% (n=51)

**gold_examples_x_change_type**: both / behavior 92.9% (n=14); both / param_removed 50.0% (n=2); both / param_value 81.0% (n=7); both / symbol_rename 71.4% (n=21); neither / param_rename 62.2% (n=37); neither / symbol_rename 78.6% (n=14)

### two_branch

**library**: numpy 85.4% (n=16); pandas 83.3% (n=30); pydantic 81.0% (n=49)

**target**: new 84.3% (n=51); old 80.3% (n=44)

**condition**: clue 77.4% (n=28); contradiction 79.5% (n=13); no-clue 91.7% (n=28); stated 79.5% (n=26)

**clue_type**: code 69.7% (n=11); error 66.7% (n=6); pin 90.9% (n=11); pin-new+code-old 61.1% (n=6); pin-old+code-new 95.2% (n=7)

**exclusivity**: behavior 76.2% (n=14); deprecation 85.7% (n=21); one_directional 100.0% (n=4); removal 81.5% (n=56)

**change_type**: behavior 76.2% (n=14); param_removed 100.0% (n=2); param_rename 64.0% (n=37); param_value 100.0% (n=7); symbol_rename 100.0% (n=35)

**user_arm**: unsure 82.5% (n=95)

**gold_examples**: both 92.4% (n=44); neither 73.9% (n=51)

**gold_examples_x_change_type**: both / behavior 76.2% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 64.0% (n=37); neither / symbol_rename 100.0% (n=14)

### always_ask

**library**: numpy 75.0% (n=16); pandas 71.1% (n=30); pydantic 66.7% (n=49)

**target**: new 73.9% (n=51); old 64.4% (n=44)

**condition**: clue 66.7% (n=28); contradiction 64.1% (n=13); no-clue 58.3% (n=28); stated 87.2% (n=26)

**clue_type**: code 60.6% (n=11); error 50.0% (n=6); pin 81.8% (n=11); pin-new+code-old 83.3% (n=6); pin-old+code-new 47.6% (n=7)

**exclusivity**: behavior 85.7% (n=14); deprecation 76.2% (n=21); one_directional 75.0% (n=4); removal 62.5% (n=56)

**change_type**: behavior 85.7% (n=14); param_removed 50.0% (n=2); param_rename 58.6% (n=37); param_value 76.2% (n=7); symbol_rename 74.3% (n=35)

**user_arm**: unsure 69.5% (n=95)

**gold_examples**: both 75.8% (n=44); neither 64.1% (n=51)

**gold_examples_x_change_type**: both / behavior 85.7% (n=14); both / param_removed 50.0% (n=2); both / param_value 76.2% (n=7); both / symbol_rename 71.4% (n=21); neither / param_rename 58.6% (n=37); neither / symbol_rename 78.6% (n=14)

## What size of difference this run can show

95 targeted instances over 15 concepts (6.3 per concept), 3 repeats averaged per instance. Measured within-concept correlation rho = 0.222 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.132 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.222 | 13.4 points | measured rho |
| 0.200 | 0.222 | 19.0 points | measured rho |
| 0.300 | 0.222 | 23.3 points | measured rho |
| 0.132 | 0.222 | 15.4 points | observed |
| 0.200 | 0.250 | 19.6 points | handoff assumption |
| 0.200 | 0.500 | 24.6 points | handoff assumption |

## Repeat disagreement (within this session)

1212 (instance, method) pairs answered under 3 repeats: response text differs on 64.6%, outcome on 14.2%, intended-version pass on 11.6%.

| Method | pairs | text differs | outcome differs |
| --- | --- | --- | --- |
| always_ask | 101 | 54.5% | 19.8% |
| assume_state | 101 | 81.2% | 16.8% |
| mind_version | 101 | 59.4% | 9.9% |
| no_retrieval | 101 | 61.4% | 29.7% |
| oracle_docs | 101 | 64.4% | 11.9% |
| plain_rag | 101 | 61.4% | 13.9% |
| two_branch | 101 | 71.3% | 7.9% |
| va_rag | 101 | 63.4% | 9.9% |
| va_rag_no_ask | 101 | 58.4% | 15.8% |
| va_rag_no_guard | 101 | 63.4% | 9.9% |
| va_rag_no_infer | 101 | 71.3% | 9.9% |
| va_rag_portable_first | 101 | 65.3% | 14.9% |
