# VA-RAG final sweep: large (20261021T082811Z)

Session `deepinfra/turbo@20261021T082811Z`; cost $1.4824; run time 1.8 h. Each section below is one run's full report.

# dev-knows

## VA-RAG run report: 20261021T085318Z-large-5c2c47a2

- Model: `large` = qwen/qwen3-coder
- Split: dev; user arm: knows; instances: 101; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T09:40:37+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen3-coder` pinned to provider `deepinfra/turbo` (no fallbacks, parameters required), served as fp4; session `deepinfra/turbo@20261021T082811Z`; 2200 paid calls, 1854 cache hits, $0.3951; providers reported {'DeepInfra': 3636}
- Provider choice: served as fp4 by DeepInfra; Google Vertex was rejected because it accepts repetition_penalty and ignores it (probe of 2026-10-19: 1.0 and 2.0 gave the same text)

- Repeats: every (instance, method) answered under repeat indices [0, 1, 2] in one session; an instance's score is the mean over its repeats, rates are means of instance scores, and intervals resample concepts.

### Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 82.5% [68.7%, 94.4%] (Wilson 59.3%, 95.1%) | 82.5% | 78.2% | 82.5% | 1.1% | 16.1% | 16.5% | 0.0% | 0.0% | 0.0% | 4.9% |
| assume_state | 69.1% [59.6%, 78.3%] (Wilson 44.5%, 86.8%) | 69.1% | 66.0% | 71.2% | 19.3% | 18.2% | 11.6% | 0.0% | 0.0% | 0.0% | 4.6% |
| mind_version | 73.0% [60.0%, 84.4%] (Wilson 47.9%, 89.0%) | 73.0% | 67.7% | 75.4% | 14.4% | 23.9% | 12.6% | 0.0% | 0.0% | 0.0% | 7.3% |
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

### Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 27.7% | 100.0% | 100.0% | 0.0% | c=0.0: 82.5%, c=0.1: 72.5%, c=0.3: 52.5% | 1.00 calls, 1.00 answers |
| assume_state | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 69.1%, c=0.1: 69.1%, c=0.3: 69.1% | 1.00 calls, 1.00 answers |
| mind_version | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 0.0% | 3.9% | 0.0% | 0.0% | c=0.0: 73.0%, c=0.1: 72.7%, c=0.3: 72.2% | 1.02 calls, 1.00 answers |
| no_retrieval | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 53.7%, c=0.1: 53.7%, c=0.3: 53.7% | 1.00 calls, 1.00 answers |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 85.6%, c=0.1: 85.6%, c=0.3: 85.6% | 1.00 calls, 1.00 answers |
| plain_rag | 1.4% [0.0%, 4.4%] (Wilson 0.1%, 22.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 69.5%, c=0.1: 69.5%, c=0.3: 69.5% | 1.00 calls, 1.00 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 93.3% | c=0.0: 82.5%, c=0.1: 72.5%, c=0.3: 52.5% | 1.96 calls, 1.96 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 0.0% | c=0.0: 82.8%, c=0.1: 78.5%, c=0.3: 69.9% | 1.03 calls, 1.00 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 70.9%, c=0.1: 70.9%, c=0.3: 70.9% | 1.02 calls, 1.00 answers |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 0.0% | c=0.0: 82.8%, c=0.1: 78.5%, c=0.3: 69.9% | 1.00 calls, 1.00 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 28.9% | 93.3% | 100.0% | 0.0% | c=0.0: 82.8%, c=0.1: 72.8%, c=0.3: 52.8% | 1.03 calls, 1.00 answers |
| va_rag_portable_first | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 72.6% | 70.0% | 0.0% | 66.7% | 0.0% | c=0.0: 77.5%, c=0.1: 74.5%, c=0.3: 68.4% | 1.32 calls, 1.00 answers |

### Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | -0.049 | n/a |
| assume_state | old 11.9%, new 53.6%, both 0.0%, neither 34.5% (n=84) | 41.7% | 0.043 | n/a |
| mind_version | old 11.9%, new 38.1%, both 0.0%, neither 50.0% (n=84) | 36.4% | 0.046 | n/a |
| no_retrieval | old 27.4%, new 28.6%, both 0.0%, neither 44.0% (n=84) | 34.5% | -0.058 | n/a |
| oracle_docs | old 21.4%, new 40.5%, both 0.0%, neither 38.1% (n=84) | 56.0% | -0.090 | n/a |
| plain_rag | old 11.9%, new 42.9%, both 4.8%, neither 40.5% (n=84) | 35.7% | 0.036 | n/a |
| two_branch | old 21.4%, new 36.9%, both 0.0%, neither 41.7% (n=84) | 53.6% | -0.049 | 70.2% |
| va_rag |  (n=0) | 56.0% | -0.055 | n/a |
| va_rag_no_ask | old 15.5%, new 48.8%, both 0.0%, neither 35.7% (n=84) | 56.0% | 0.012 | n/a |
| va_rag_no_guard |  (n=0) | 56.0% | -0.055 | n/a |
| va_rag_no_infer |  (n=0) | n/a | -0.055 | n/a |
| va_rag_portable_first | old 0.0%, new 0.0%, both 0.0%, neither 100.0% (n=23) | 56.0% | -0.091 | n/a |

### Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"asked": 129, "inferred": 162, "no_conflict": 12} | n/a | 9 | 0.0% | n/a | 0.0% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"inferred": 162, "no_conflict": 12, "unresolved": 129} | n/a | 6 | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"asked": 129, "inferred": 162, "no_conflict": 12} | n/a | 0 | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 101} | {"asked": 291, "no_conflict": 12} | n/a | 9 | 0.0% | n/a | 0.0% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"asked": 87, "inferred": 162, "no_conflict": 12, "portable": 42} | n/a | 9 | 0.0% | n/a | 0.0% | 0.0% |

Portable-first drafts (`va_rag_portable_first`): 129 drafts, 42 returned without a question (32.6%); rejected: {"exclusive or deprecated usage": 87}.

Risk-coverage sweep on |margin| for `va_rag` (coverage = answered without a question, risk = wrong-version commits among them):

| threshold | coverage | risk |
| --- | --- | --- |
| 11.50 | 1.9% | 0.0% |
| 3.00 | 27.8% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |

### Primary contrasts: va_rag against each baseline

Paired bootstrap on per-concept differences of instance scores (va_rag minus baseline); exact McNemar on the repeat-0 instance pairs, Holm-adjusted across the contrasts.

| Baseline | Metric | Difference | 95% bootstrap | discordant (va_rag only / baseline only) | McNemar p | Holm p |
| --- | --- | --- | --- | --- | --- | --- |
| always_ask | intended_pass | +0.3 pts | [-1.9, +2.5] | 0 / 1 | 1.0000 | 1.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +11.3 pts | [-1.1, +23.5] | 14 / 9 | 0.4049 | 1.0000 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| plain_rag | intended_pass | +14.4 pts | [+2.5, +26.2] | 15 / 6 | 0.0784 | 0.6268 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +0.3 pts | [-1.9, +2.5] | 0 / 1 | 1.0000 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

### Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

#### va_rag

**change_type**: behavior 71.4% (n=14); param_removed 100.0% (n=2); param_rename 67.6% (n=37); param_value 95.2% (n=7); symbol_rename 100.0% (n=35)

**clue_type**: code 69.7% (n=11); error 72.2% (n=6); pin 90.9% (n=11); pin-new+code-old 61.1% (n=6); pin-old+code-new 95.2% (n=7)

**condition**: clue 78.6% (n=28); contradiction 79.5% (n=13); no-clue 91.7% (n=28); stated 79.5% (n=26)

**exclusivity**: behavior 71.4% (n=14); deprecation 85.7% (n=21); one_directional 100.0% (n=4); removal 83.3% (n=56)

**gold_examples**: both 90.2% (n=44); neither 76.5% (n=51)

**gold_examples_x_change_type**: both / behavior 71.4% (n=14); both / param_removed 100.0% (n=2); both / param_value 95.2% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 67.6% (n=37); neither / symbol_rename 100.0% (n=14)

**library**: numpy 85.4% (n=16); pandas 82.2% (n=30); pydantic 82.3% (n=49)

**target**: new 84.3% (n=51); old 81.1% (n=44)

**user_arm**: knows 82.8% (n=95)

#### plain_rag

**change_type**: behavior 81.0% (n=14); param_removed 50.0% (n=2); param_rename 59.5% (n=37); param_value 85.7% (n=7); symbol_rename 73.3% (n=35)

**clue_type**: code 48.5% (n=11); error 50.0% (n=6); pin 90.9% (n=11); pin-new+code-old 72.2% (n=6); pin-old+code-new 57.1% (n=7)

**condition**: clue 65.5% (n=28); contradiction 64.1% (n=13); no-clue 64.3% (n=28); stated 82.1% (n=26)

**exclusivity**: behavior 81.0% (n=14); deprecation 76.2% (n=21); one_directional 75.0% (n=4); removal 63.7% (n=56)

**gold_examples**: both 75.8% (n=44); neither 64.1% (n=51)

**gold_examples_x_change_type**: both / behavior 81.0% (n=14); both / param_removed 50.0% (n=2); both / param_value 85.7% (n=7); both / symbol_rename 71.4% (n=21); neither / param_rename 59.5% (n=37); neither / symbol_rename 76.2% (n=14)

**library**: numpy 75.0% (n=16); pandas 71.1% (n=30); pydantic 66.7% (n=49)

**target**: new 71.9% (n=51); old 66.7% (n=44)

**user_arm**: knows 69.5% (n=95)

#### mind_version

**change_type**: behavior 92.9% (n=14); param_removed 50.0% (n=2); param_rename 62.2% (n=37); param_value 81.0% (n=7); symbol_rename 76.2% (n=35)

**clue_type**: code 69.7% (n=11); error 61.1% (n=6); pin 84.8% (n=11); pin-new+code-old 83.3% (n=6); pin-old+code-new 61.9% (n=7)

**condition**: clue 73.8% (n=28); contradiction 71.8% (n=13); no-clue 59.5% (n=28); stated 87.2% (n=26)

**exclusivity**: behavior 92.9% (n=14); deprecation 74.6% (n=21); one_directional 75.0% (n=4); removal 67.3% (n=56)

**gold_examples**: both 78.8% (n=44); neither 68.0% (n=51)

**gold_examples_x_change_type**: both / behavior 92.9% (n=14); both / param_removed 50.0% (n=2); both / param_value 81.0% (n=7); both / symbol_rename 71.4% (n=21); neither / param_rename 62.2% (n=37); neither / symbol_rename 83.3% (n=14)

**library**: numpy 75.0% (n=16); pandas 78.9% (n=30); pydantic 68.7% (n=49)

**target**: new 74.5% (n=51); old 71.2% (n=44)

**user_arm**: knows 73.0% (n=95)

#### two_branch

**change_type**: behavior 76.2% (n=14); param_removed 100.0% (n=2); param_rename 64.0% (n=37); param_value 100.0% (n=7); symbol_rename 100.0% (n=35)

**clue_type**: code 69.7% (n=11); error 66.7% (n=6); pin 90.9% (n=11); pin-new+code-old 61.1% (n=6); pin-old+code-new 95.2% (n=7)

**condition**: clue 77.4% (n=28); contradiction 79.5% (n=13); no-clue 91.7% (n=28); stated 79.5% (n=26)

**exclusivity**: behavior 76.2% (n=14); deprecation 85.7% (n=21); one_directional 100.0% (n=4); removal 81.5% (n=56)

**gold_examples**: both 92.4% (n=44); neither 73.9% (n=51)

**gold_examples_x_change_type**: both / behavior 76.2% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 64.0% (n=37); neither / symbol_rename 100.0% (n=14)

**library**: numpy 85.4% (n=16); pandas 83.3% (n=30); pydantic 81.0% (n=49)

**target**: new 84.3% (n=51); old 80.3% (n=44)

**user_arm**: knows 82.5% (n=95)

#### always_ask

**change_type**: behavior 76.2% (n=14); param_removed 100.0% (n=2); param_rename 64.0% (n=37); param_value 100.0% (n=7); symbol_rename 100.0% (n=35)

**clue_type**: code 69.7% (n=11); error 66.7% (n=6); pin 90.9% (n=11); pin-new+code-old 61.1% (n=6); pin-old+code-new 95.2% (n=7)

**condition**: clue 77.4% (n=28); contradiction 79.5% (n=13); no-clue 91.7% (n=28); stated 79.5% (n=26)

**exclusivity**: behavior 76.2% (n=14); deprecation 85.7% (n=21); one_directional 100.0% (n=4); removal 81.5% (n=56)

**gold_examples**: both 92.4% (n=44); neither 73.9% (n=51)

**gold_examples_x_change_type**: both / behavior 76.2% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 64.0% (n=37); neither / symbol_rename 100.0% (n=14)

**library**: numpy 85.4% (n=16); pandas 83.3% (n=30); pydantic 81.0% (n=49)

**target**: new 84.3% (n=51); old 80.3% (n=44)

**user_arm**: knows 82.5% (n=95)

### What size of difference this run can show

95 targeted instances over 15 concepts (6.3 per concept), 3 repeats averaged per instance. Measured within-concept correlation rho = 0.250 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.110 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.250 | 13.9 points | measured rho |
| 0.200 | 0.250 | 19.6 points | measured rho |
| 0.300 | 0.250 | 24.0 points | measured rho |
| 0.110 | 0.250 | 14.6 points | observed |
| 0.200 | 0.250 | 19.6 points | handoff assumption |
| 0.200 | 0.500 | 24.6 points | handoff assumption |

### Repeat disagreement (within this session)

1212 (instance, method) pairs answered under 3 repeats: response text differs on 63.3%, outcome on 13.3%, intended-version pass on 11.1%.

| Method | pairs | text differs | outcome differs |
| --- | --- | --- | --- |
| always_ask | 101 | 58.4% | 7.9% |
| assume_state | 101 | 81.2% | 16.8% |
| mind_version | 101 | 59.4% | 10.9% |
| no_retrieval | 101 | 61.4% | 29.7% |
| oracle_docs | 101 | 64.4% | 11.9% |
| plain_rag | 101 | 61.4% | 13.9% |
| two_branch | 101 | 71.3% | 7.9% |
| va_rag | 101 | 60.4% | 9.9% |
| va_rag_no_ask | 101 | 58.4% | 15.8% |
| va_rag_no_guard | 101 | 60.4% | 9.9% |
| va_rag_no_infer | 101 | 60.4% | 9.9% |
| va_rag_portable_first | 101 | 62.4% | 14.9% |

# dev-unsure

## VA-RAG run report: 20261021T094052Z-large-f22186c7

- Model: `large` = qwen/qwen3-coder
- Split: dev; user arm: unsure; instances: 101; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T09:52:43+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen3-coder` pinned to provider `deepinfra/turbo` (no fallbacks, parameters required), served as fp4; session `deepinfra/turbo@20261021T082811Z`; 236 paid calls, 4475 cache hits, $0.0551; providers reported {'DeepInfra': 3636}
- Provider choice: served as fp4 by DeepInfra; Google Vertex was rejected because it accepts repetition_penalty and ignores it (probe of 2026-10-19: 1.0 and 2.0 gave the same text)

- Repeats: every (instance, method) answered under repeat indices [0, 1, 2] in one session; an instance's score is the mean over its repeats, rates are means of instance scores, and intervals resample concepts.

### Primary metrics

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

### Blending, asking, hedging, cost

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

### Commit direction, clue following, order

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

### Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"both": 129, "inferred": 162, "no_conflict": 12} | n/a | 9 | 0.0% | n/a | 0.0% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"inferred": 162, "no_conflict": 12, "unresolved": 129} | n/a | 6 | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"both": 129, "inferred": 162, "no_conflict": 12} | n/a | 0 | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 101} | {"both": 291, "no_conflict": 12} | n/a | 9 | 0.0% | n/a | 0.0% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"both": 87, "inferred": 162, "no_conflict": 12, "portable": 42} | n/a | 9 | 0.0% | n/a | 0.0% | 0.0% |

Portable-first drafts (`va_rag_portable_first`): 129 drafts, 42 returned without a question (32.6%); rejected: {"exclusive or deprecated usage": 87}.

Risk-coverage sweep on |margin| for `va_rag` (coverage = answered without a question, risk = wrong-version commits among them):

| threshold | coverage | risk |
| --- | --- | --- |
| 11.50 | 1.9% | 0.0% |
| 3.00 | 27.8% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |

### Primary contrasts: va_rag against each baseline

Paired bootstrap on per-concept differences of instance scores (va_rag minus baseline); exact McNemar on the repeat-0 instance pairs, Holm-adjusted across the contrasts.

| Baseline | Metric | Difference | 95% bootstrap | discordant (va_rag only / baseline only) | McNemar p | Holm p |
| --- | --- | --- | --- | --- | --- | --- |
| always_ask | intended_pass | +14.4 pts | [+1.9, +27.3] | 21 / 9 | 0.0428 | 0.3422 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +11.9 pts | [-0.8, +24.1] | 15 / 9 | 0.3075 | 1.0000 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| plain_rag | intended_pass | +14.4 pts | [+2.5, +26.2] | 15 / 6 | 0.0784 | 0.5485 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +0.3 pts | [-1.9, +2.5] | 0 / 1 | 1.0000 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

### Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

#### va_rag

**change_type**: behavior 71.4% (n=14); param_removed 100.0% (n=2); param_rename 67.6% (n=37); param_value 95.2% (n=7); symbol_rename 100.0% (n=35)

**clue_type**: code 69.7% (n=11); error 72.2% (n=6); pin 90.9% (n=11); pin-new+code-old 61.1% (n=6); pin-old+code-new 95.2% (n=7)

**condition**: clue 78.6% (n=28); contradiction 79.5% (n=13); no-clue 91.7% (n=28); stated 79.5% (n=26)

**exclusivity**: behavior 71.4% (n=14); deprecation 85.7% (n=21); one_directional 100.0% (n=4); removal 83.3% (n=56)

**gold_examples**: both 90.2% (n=44); neither 76.5% (n=51)

**gold_examples_x_change_type**: both / behavior 71.4% (n=14); both / param_removed 100.0% (n=2); both / param_value 95.2% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 67.6% (n=37); neither / symbol_rename 100.0% (n=14)

**library**: numpy 85.4% (n=16); pandas 82.2% (n=30); pydantic 82.3% (n=49)

**target**: new 84.3% (n=51); old 81.1% (n=44)

**user_arm**: unsure 82.8% (n=95)

#### plain_rag

**change_type**: behavior 81.0% (n=14); param_removed 50.0% (n=2); param_rename 59.5% (n=37); param_value 85.7% (n=7); symbol_rename 73.3% (n=35)

**clue_type**: code 48.5% (n=11); error 50.0% (n=6); pin 90.9% (n=11); pin-new+code-old 72.2% (n=6); pin-old+code-new 57.1% (n=7)

**condition**: clue 65.5% (n=28); contradiction 64.1% (n=13); no-clue 64.3% (n=28); stated 82.1% (n=26)

**exclusivity**: behavior 81.0% (n=14); deprecation 76.2% (n=21); one_directional 75.0% (n=4); removal 63.7% (n=56)

**gold_examples**: both 75.8% (n=44); neither 64.1% (n=51)

**gold_examples_x_change_type**: both / behavior 81.0% (n=14); both / param_removed 50.0% (n=2); both / param_value 85.7% (n=7); both / symbol_rename 71.4% (n=21); neither / param_rename 59.5% (n=37); neither / symbol_rename 76.2% (n=14)

**library**: numpy 75.0% (n=16); pandas 71.1% (n=30); pydantic 66.7% (n=49)

**target**: new 71.9% (n=51); old 66.7% (n=44)

**user_arm**: unsure 69.5% (n=95)

#### mind_version

**change_type**: behavior 92.9% (n=14); param_removed 50.0% (n=2); param_rename 62.2% (n=37); param_value 81.0% (n=7); symbol_rename 74.3% (n=35)

**clue_type**: code 69.7% (n=11); error 50.0% (n=6); pin 84.8% (n=11); pin-new+code-old 83.3% (n=6); pin-old+code-new 61.9% (n=7)

**condition**: clue 71.4% (n=28); contradiction 71.8% (n=13); no-clue 59.5% (n=28); stated 87.2% (n=26)

**exclusivity**: behavior 92.9% (n=14); deprecation 71.4% (n=21); one_directional 75.0% (n=4); removal 67.3% (n=56)

**gold_examples**: both 78.8% (n=44); neither 66.7% (n=51)

**gold_examples_x_change_type**: both / behavior 92.9% (n=14); both / param_removed 50.0% (n=2); both / param_value 81.0% (n=7); both / symbol_rename 71.4% (n=21); neither / param_rename 62.2% (n=37); neither / symbol_rename 78.6% (n=14)

**library**: numpy 75.0% (n=16); pandas 78.9% (n=30); pydantic 67.3% (n=49)

**target**: new 73.2% (n=51); old 71.2% (n=44)

**user_arm**: unsure 72.3% (n=95)

#### two_branch

**change_type**: behavior 76.2% (n=14); param_removed 100.0% (n=2); param_rename 64.0% (n=37); param_value 100.0% (n=7); symbol_rename 100.0% (n=35)

**clue_type**: code 69.7% (n=11); error 66.7% (n=6); pin 90.9% (n=11); pin-new+code-old 61.1% (n=6); pin-old+code-new 95.2% (n=7)

**condition**: clue 77.4% (n=28); contradiction 79.5% (n=13); no-clue 91.7% (n=28); stated 79.5% (n=26)

**exclusivity**: behavior 76.2% (n=14); deprecation 85.7% (n=21); one_directional 100.0% (n=4); removal 81.5% (n=56)

**gold_examples**: both 92.4% (n=44); neither 73.9% (n=51)

**gold_examples_x_change_type**: both / behavior 76.2% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 64.0% (n=37); neither / symbol_rename 100.0% (n=14)

**library**: numpy 85.4% (n=16); pandas 83.3% (n=30); pydantic 81.0% (n=49)

**target**: new 84.3% (n=51); old 80.3% (n=44)

**user_arm**: unsure 82.5% (n=95)

#### always_ask

**change_type**: behavior 85.7% (n=14); param_removed 50.0% (n=2); param_rename 58.6% (n=37); param_value 76.2% (n=7); symbol_rename 74.3% (n=35)

**clue_type**: code 60.6% (n=11); error 50.0% (n=6); pin 81.8% (n=11); pin-new+code-old 83.3% (n=6); pin-old+code-new 47.6% (n=7)

**condition**: clue 66.7% (n=28); contradiction 64.1% (n=13); no-clue 58.3% (n=28); stated 87.2% (n=26)

**exclusivity**: behavior 85.7% (n=14); deprecation 76.2% (n=21); one_directional 75.0% (n=4); removal 62.5% (n=56)

**gold_examples**: both 75.8% (n=44); neither 64.1% (n=51)

**gold_examples_x_change_type**: both / behavior 85.7% (n=14); both / param_removed 50.0% (n=2); both / param_value 76.2% (n=7); both / symbol_rename 71.4% (n=21); neither / param_rename 58.6% (n=37); neither / symbol_rename 78.6% (n=14)

**library**: numpy 75.0% (n=16); pandas 71.1% (n=30); pydantic 66.7% (n=49)

**target**: new 73.9% (n=51); old 64.4% (n=44)

**user_arm**: unsure 69.5% (n=95)

### What size of difference this run can show

95 targeted instances over 15 concepts (6.3 per concept), 3 repeats averaged per instance. Measured within-concept correlation rho = 0.222 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.132 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.222 | 13.4 points | measured rho |
| 0.200 | 0.222 | 19.0 points | measured rho |
| 0.300 | 0.222 | 23.3 points | measured rho |
| 0.132 | 0.222 | 15.4 points | observed |
| 0.200 | 0.250 | 19.6 points | handoff assumption |
| 0.200 | 0.500 | 24.6 points | handoff assumption |

### Repeat disagreement (within this session)

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

# test-knows

## VA-RAG run report: 20261021T122011Z-large-82f188d0

- Model: `large` = qwen/qwen3-coder
- Split: test; user arm: knows; instances: 237; concepts: 57
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T12:57:19+00:00

> 57 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen3-coder` pinned to provider `deepinfra/turbo` (no fallbacks, parameters required), served as fp4; session `deepinfra/turbo@20261021T082811Z`; 1863 paid calls, 7653 cache hits, $0.3675; providers reported {'DeepInfra': 8532}
- Provider choice: served as fp4 by DeepInfra; Google Vertex was rejected because it accepts repetition_penalty and ignores it (probe of 2026-10-19: 1.0 and 2.0 gave the same text)

- Repeats: every (instance, method) answered under repeat indices [0, 1, 2] in one session; an instance's score is the mean over its repeats, rates are means of instance scores, and intervals resample concepts.

### Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 79.7% [69.6%, 88.6%] (Wilson 67.4%, 89.4%) | 79.7% | 78.9% | 79.8% | 4.8% | 16.8% | 15.5% | 0.0% | 0.0% | 0.0% | 0.9% |
| assume_state | 59.5% [51.8%, 66.4%] (Wilson 46.8%, 73.4%) | 59.5% | 58.3% | 62.1% | 27.3% | 17.0% | 13.2% | 0.0% | 0.0% | 0.0% | 2.2% |
| mind_version | 59.6% [51.2%, 67.4%] (Wilson 47.7%, 74.2%) | 59.6% | 58.6% | 64.3% | 27.3% | 18.7% | 13.0% | 0.0% | 0.0% | 0.0% | 1.5% |
| no_retrieval | 59.5% [50.8%, 67.7%] (Wilson 47.0%, 73.6%) | 59.5% | 58.2% | 63.5% | 19.0% | 22.1% | 21.3% | 0.0% | 0.0% | 0.0% | 2.4% |
| oracle_docs | 81.7% [71.5%, 90.6%] (Wilson 70.4%, 91.3%) | 81.7% | 80.8% | 81.7% | 4.7% | 18.4% | 13.6% | 0.0% | 0.0% | 0.0% | 1.0% |
| plain_rag | 60.1% [51.8%, 67.9%] (Wilson 48.2%, 74.6%) | 60.1% | 58.6% | 64.6% | 29.2% | 20.6% | 10.7% | 0.0% | 0.0% | 0.0% | 2.2% |
| two_branch | 79.7% [69.6%, 88.6%] (Wilson 67.4%, 89.4%) | 79.7% | 78.9% | 79.8% | 4.8% | 16.8% | 15.5% | 0.0% | 0.0% | 0.0% | 0.9% |
| va_rag | 81.1% [71.2%, 89.6%] (Wilson 69.7%, 90.9%) | 81.1% | 80.8% | 81.9% | 2.6% | 18.0% | 16.2% | 0.0% | 0.0% | 0.0% | 0.3% |
| va_rag_no_ask | 63.6% [55.5%, 71.0%] (Wilson 51.2%, 77.2%) | 63.6% | 62.7% | 67.3% | 22.2% | 18.6% | 14.2% | 0.0% | 0.0% | 0.0% | 1.7% |
| va_rag_no_guard | 79.2% [69.2%, 88.1%] (Wilson 67.4%, 89.4%) | 79.2% | 78.9% | 80.0% | 4.7% | 17.4% | 16.1% | 0.0% | 0.0% | 0.0% | 0.3% |
| va_rag_no_infer | 81.1% [71.2%, 89.6%] (Wilson 69.7%, 90.9%) | 81.1% | 80.8% | 81.9% | 2.6% | 18.0% | 16.2% | 0.0% | 0.0% | 0.0% | 0.3% |
| va_rag_portable_first | 78.9% [69.5%, 87.3%] (Wilson 66.6%, 88.9%) | 78.9% | 78.4% | 79.4% | 2.9% | 21.3% | 18.1% | 0.0% | 0.0% | 0.0% | 0.7% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

### Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 34.6% | 100.0% | 100.0% | 0.0% | c=0.0: 79.7%, c=0.1: 69.7%, c=0.3: 49.7% | 1.00 calls, 1.00 answers |
| assume_state | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 59.5%, c=0.1: 59.5%, c=0.3: 59.5% | 1.00 calls, 1.00 answers |
| mind_version | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 2.8% | 42.9% | 1.9% | 0.0% | 0.0% | c=0.0: 59.6%, c=0.1: 59.4%, c=0.3: 59.0% | 1.02 calls, 1.00 answers |
| no_retrieval | 1.0% [0.0%, 2.4%] (Wilson 0.1%, 8.8%) | 0.1% [0.0%, 0.5%] (Wilson 0.0%, 7.6%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 59.5%, c=0.1: 59.5%, c=0.3: 59.5% | 1.00 calls, 1.00 answers |
| oracle_docs | 0.1% [0.0%, 0.5%] (Wilson 0.0%, 7.6%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 81.7%, c=0.1: 81.7%, c=0.3: 81.7% | 1.00 calls, 1.00 answers |
| plain_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 60.1%, c=0.1: 60.1%, c=0.3: 60.1% | 1.00 calls, 1.00 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 95.0% | c=0.0: 79.7%, c=0.1: 69.7%, c=0.3: 49.7% | 1.97 calls, 1.97 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 68.9% | 2.5% | 100.0% | 0.0% | c=0.0: 81.1%, c=0.1: 76.1%, c=0.3: 65.9% | 1.03 calls, 1.00 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 63.6%, c=0.1: 63.6%, c=0.3: 63.6% | 1.01 calls, 1.00 answers |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 68.9% | 2.5% | 100.0% | 0.0% | c=0.0: 79.2%, c=0.1: 74.2%, c=0.3: 64.0% | 1.00 calls, 1.00 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 35.5% | 95.0% | 100.0% | 0.0% | c=0.0: 81.1%, c=0.1: 71.1%, c=0.3: 51.1% | 1.03 calls, 1.00 answers |
| va_rag_portable_first | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 56.5% | 69.0% | 0.0% | 57.8% | 0.0% | c=0.0: 78.9%, c=0.1: 76.1%, c=0.3: 70.3% | 1.31 calls, 1.00 answers |

### Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | -0.011 | n/a |
| assume_state | old 15.4%, new 46.7%, both 0.0%, neither 37.8% (n=246) | 38.2% | 0.101 | n/a |
| mind_version | old 18.4%, new 25.5%, both 0.0%, neither 56.1% (n=239) | 39.3% | 0.212 | n/a |
| no_retrieval | old 13.8%, new 23.6%, both 0.0%, neither 62.6% (n=246) | 33.7% | 0.023 | n/a |
| oracle_docs | old 18.3%, new 29.7%, both 0.0%, neither 52.0% (n=246) | 45.9% | -0.011 | n/a |
| plain_rag | old 15.4%, new 30.5%, both 0.0%, neither 54.1% (n=246) | 35.0% | 0.162 | n/a |
| two_branch | old 16.7%, new 28.9%, both 0.0%, neither 54.5% (n=246) | 45.9% | -0.011 | 69.4% |
| va_rag |  (n=0) | 47.2% | 0.017 | n/a |
| va_rag_no_ask | old 17.5%, new 30.1%, both 0.0%, neither 52.4% (n=246) | 47.2% | 0.155 | n/a |
| va_rag_no_guard |  (n=0) | 45.9% | -0.004 | n/a |
| va_rag_no_infer |  (n=0) | n/a | 0.017 | n/a |
| va_rag_portable_first | old 0.0%, new 0.0%, both 0.0%, neither 100.0% (n=107) | 47.2% | 0.014 | n/a |

### Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"asked": 357, "inferred": 336, "no_conflict": 18} | n/a | 24 | 0.0% | n/a | 54.2% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"inferred": 336, "no_conflict": 18, "unresolved": 357} | n/a | 8 | 0.0% | 0.0% | 37.5% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"asked": 357, "inferred": 336, "no_conflict": 18} | n/a | 0 | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 237} | {"asked": 693, "no_conflict": 18} | n/a | 24 | 0.0% | n/a | 54.2% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"asked": 198, "inferred": 336, "no_conflict": 18, "portable": 159} | n/a | 23 | 0.0% | n/a | 52.2% | 0.0% |

Portable-first drafts (`va_rag_portable_first`): 357 drafts, 159 returned without a question (44.5%); rejected: {"exclusive or deprecated usage": 198}.

Risk-coverage sweep on |margin| for `va_rag` (coverage = answered without a question, risk = wrong-version commits among them):

| threshold | coverage | risk |
| --- | --- | --- |
| 14.00 | 0.9% | 0.0% |
| 4.00 | 40.2% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |

### Primary contrasts: va_rag against each baseline

Paired bootstrap on per-concept differences of instance scores (va_rag minus baseline); exact McNemar on the repeat-0 instance pairs, Holm-adjusted across the contrasts.

| Baseline | Metric | Difference | 95% bootstrap | discordant (va_rag only / baseline only) | McNemar p | Holm p |
| --- | --- | --- | --- | --- | --- | --- |
| always_ask | intended_pass | +2.0 pts | [-1.0, +5.6] | 6 / 3 | 0.5078 | 1.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +20.9 pts | [+12.9, +29.1] | 63 / 9 | 0.0000 | 0.0000 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| plain_rag | intended_pass | +20.4 pts | [+13.0, +28.0] | 59 / 12 | 0.0000 | 0.0000 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +2.0 pts | [-1.0, +5.6] | 6 / 3 | 0.5078 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

### Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

#### va_rag

**change_type**: behavior 49.1% (n=36); moved_import 100.0% (n=5); param_removed 83.3% (n=2); param_rename 88.7% (n=62); param_value 56.7% (n=30); symbol_removed 90.5% (n=14); symbol_rename 96.2% (n=79)

**clue_type**: code 74.7% (n=29); error 81.2% (n=23); pin 85.6% (n=30); pin-new+code-old 71.2% (n=22); pin-old+code-new 88.9% (n=12)

**condition**: clue 80.5% (n=82); contradiction 77.5% (n=34); no-clue 85.0% (n=82); stated 76.7% (n=30)

**exclusivity**: behavior 49.1% (n=36); deprecation 97.1% (n=68); one_directional 86.9% (n=28); removal 80.2% (n=96)

**gold_examples**: both 72.5% (n=51); neither 83.6% (n=177)

**gold_examples_x_change_type**: both / behavior 41.3% (n=21); both / symbol_removed 100.0% (n=6); both / symbol_rename 93.1% (n=24); neither / behavior 60.0% (n=15); neither / moved_import 100.0% (n=5); neither / param_removed 83.3% (n=2); neither / param_rename 88.7% (n=62); neither / param_value 56.7% (n=30); neither / symbol_removed 83.3% (n=8); neither / symbol_rename 97.6% (n=55)

**library**: numpy 71.4% (n=35); pandas 59.7% (n=62); pydantic 93.9% (n=131)

**target**: new 79.3% (n=124); old 83.3% (n=104)

**user_arm**: knows 81.1% (n=228)

#### plain_rag

**change_type**: behavior 51.9% (n=36); moved_import 46.7% (n=5); param_removed 0.0% (n=2); param_rename 65.6% (n=62); param_value 35.6% (n=30); symbol_removed 83.3% (n=14); symbol_rename 67.1% (n=79)

**clue_type**: code 56.3% (n=29); error 63.8% (n=23); pin 84.4% (n=30); pin-new+code-old 45.5% (n=22); pin-old+code-new 50.0% (n=12)

**condition**: clue 68.7% (n=82); contradiction 47.1% (n=34); no-clue 51.2% (n=82); stated 75.6% (n=30)

**exclusivity**: behavior 51.9% (n=36); deprecation 63.7% (n=68); one_directional 73.8% (n=28); removal 56.6% (n=96)

**gold_examples**: both 58.8% (n=51); neither 60.5% (n=177)

**gold_examples_x_change_type**: both / behavior 47.6% (n=21); both / symbol_removed 66.7% (n=6); both / symbol_rename 66.7% (n=24); neither / behavior 57.8% (n=15); neither / moved_import 46.7% (n=5); neither / param_removed 0.0% (n=2); neither / param_rename 65.6% (n=62); neither / param_value 35.6% (n=30); neither / symbol_removed 95.8% (n=8); neither / symbol_rename 67.3% (n=55)

**library**: numpy 70.5% (n=35); pandas 48.9% (n=62); pydantic 62.6% (n=131)

**target**: new 65.3% (n=124); old 53.8% (n=104)

**user_arm**: knows 60.1% (n=228)

#### mind_version

**change_type**: behavior 52.8% (n=36); moved_import 40.0% (n=5); param_removed 0.0% (n=2); param_rename 62.4% (n=62); param_value 36.7% (n=30); symbol_removed 85.7% (n=14); symbol_rename 67.5% (n=79)

**clue_type**: code 59.8% (n=29); error 69.6% (n=23); pin 86.7% (n=30); pin-new+code-old 45.5% (n=22); pin-old+code-new 50.0% (n=12)

**condition**: clue 72.4% (n=82); contradiction 47.1% (n=34); no-clue 47.2% (n=82); stated 73.3% (n=30)

**exclusivity**: behavior 52.8% (n=36); deprecation 63.7% (n=68); one_directional 71.4% (n=28); removal 55.9% (n=96)

**gold_examples**: both 60.1% (n=51); neither 59.5% (n=177)

**gold_examples_x_change_type**: both / behavior 47.6% (n=21); both / symbol_removed 66.7% (n=6); both / symbol_rename 69.4% (n=24); neither / behavior 60.0% (n=15); neither / moved_import 40.0% (n=5); neither / param_removed 0.0% (n=2); neither / param_rename 62.4% (n=62); neither / param_value 36.7% (n=30); neither / symbol_removed 100.0% (n=8); neither / symbol_rename 66.7% (n=55)

**library**: numpy 68.6% (n=35); pandas 48.9% (n=62); pydantic 62.3% (n=131)

**target**: new 61.8% (n=124); old 57.1% (n=104)

**user_arm**: knows 59.6% (n=228)

#### two_branch

**change_type**: behavior 48.1% (n=36); moved_import 100.0% (n=5); param_removed 66.7% (n=2); param_rename 89.8% (n=62); param_value 43.3% (n=30); symbol_removed 88.1% (n=14); symbol_rename 97.5% (n=79)

**clue_type**: code 71.3% (n=29); error 78.3% (n=23); pin 85.6% (n=30); pin-new+code-old 78.8% (n=22); pin-old+code-new 77.8% (n=12)

**condition**: clue 78.5% (n=82); contradiction 78.4% (n=34); no-clue 82.5% (n=82); stated 76.7% (n=30)

**exclusivity**: behavior 48.1% (n=36); deprecation 99.0% (n=68); one_directional 81.0% (n=28); removal 77.4% (n=96)

**gold_examples**: both 71.9% (n=51); neither 81.9% (n=177)

**gold_examples_x_change_type**: both / behavior 41.3% (n=21); both / symbol_removed 88.9% (n=6); both / symbol_rename 94.4% (n=24); neither / behavior 57.8% (n=15); neither / moved_import 100.0% (n=5); neither / param_removed 66.7% (n=2); neither / param_rename 89.8% (n=62); neither / param_value 43.3% (n=30); neither / symbol_removed 87.5% (n=8); neither / symbol_rename 98.8% (n=55)

**library**: numpy 68.6% (n=35); pandas 53.2% (n=62); pydantic 95.2% (n=131)

**target**: new 77.4% (n=124); old 82.4% (n=104)

**user_arm**: knows 79.7% (n=228)

#### always_ask

**change_type**: behavior 48.1% (n=36); moved_import 100.0% (n=5); param_removed 66.7% (n=2); param_rename 89.8% (n=62); param_value 43.3% (n=30); symbol_removed 88.1% (n=14); symbol_rename 97.5% (n=79)

**clue_type**: code 71.3% (n=29); error 78.3% (n=23); pin 85.6% (n=30); pin-new+code-old 78.8% (n=22); pin-old+code-new 77.8% (n=12)

**condition**: clue 78.5% (n=82); contradiction 78.4% (n=34); no-clue 82.5% (n=82); stated 76.7% (n=30)

**exclusivity**: behavior 48.1% (n=36); deprecation 99.0% (n=68); one_directional 81.0% (n=28); removal 77.4% (n=96)

**gold_examples**: both 71.9% (n=51); neither 81.9% (n=177)

**gold_examples_x_change_type**: both / behavior 41.3% (n=21); both / symbol_removed 88.9% (n=6); both / symbol_rename 94.4% (n=24); neither / behavior 57.8% (n=15); neither / moved_import 100.0% (n=5); neither / param_removed 66.7% (n=2); neither / param_rename 89.8% (n=62); neither / param_value 43.3% (n=30); neither / symbol_removed 87.5% (n=8); neither / symbol_rename 98.8% (n=55)

**library**: numpy 68.6% (n=35); pandas 53.2% (n=62); pydantic 95.2% (n=131)

**target**: new 77.4% (n=124); old 82.4% (n=104)

**user_arm**: knows 79.7% (n=228)

### What size of difference this run can show

228 targeted instances over 48 concepts (4.8 per concept), 3 repeats averaged per instance. Measured within-concept correlation rho = 0.385 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.129 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.385 | 9.2 points | measured rho |
| 0.200 | 0.385 | 13.0 points | measured rho |
| 0.300 | 0.385 | 15.9 points | measured rho |
| 0.129 | 0.385 | 10.4 points | observed |
| 0.200 | 0.250 | 11.5 points | handoff assumption |
| 0.200 | 0.500 | 14.1 points | handoff assumption |

### Repeat disagreement (within this session)

2844 (instance, method) pairs answered under 3 repeats: response text differs on 63.6%, outcome on 15.6%, intended-version pass on 11.4%.

| Method | pairs | text differs | outcome differs |
| --- | --- | --- | --- |
| always_ask | 237 | 55.7% | 13.5% |
| assume_state | 237 | 92.8% | 20.7% |
| mind_version | 237 | 66.2% | 21.5% |
| no_retrieval | 237 | 55.3% | 21.5% |
| oracle_docs | 237 | 62.0% | 11.8% |
| plain_rag | 237 | 65.8% | 18.1% |
| two_branch | 237 | 73.0% | 13.5% |
| va_rag | 237 | 57.4% | 11.4% |
| va_rag_no_ask | 237 | 60.3% | 14.3% |
| va_rag_no_guard | 237 | 57.4% | 11.8% |
| va_rag_no_infer | 237 | 57.4% | 11.4% |
| va_rag_portable_first | 237 | 59.5% | 18.1% |

# test-unsure

## VA-RAG run report: 20261021T125742Z-large-85cfcf61

- Model: `large` = qwen/qwen3-coder
- Split: test; user arm: unsure; instances: 237; concepts: 57
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T13:20:26+00:00

> 57 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen3-coder` pinned to provider `deepinfra/turbo` (no fallbacks, parameters required), served as fp4; session `deepinfra/turbo@20261021T082811Z`; 526 paid calls, 10632 cache hits, $0.1182; providers reported {'DeepInfra': 8532}
- Provider choice: served as fp4 by DeepInfra; Google Vertex was rejected because it accepts repetition_penalty and ignores it (probe of 2026-10-19: 1.0 and 2.0 gave the same text)

- Repeats: every (instance, method) answered under repeat indices [0, 1, 2] in one session; an instance's score is the mean over its repeats, rates are means of instance scores, and intervals resample concepts.

### Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 59.8% [51.5%, 67.5%] (Wilson 48.1%, 74.5%) | 59.8% | 58.3% | 64.2% | 27.8% | 20.2% | 12.4% | 0.0% | 0.0% | 0.0% | 2.7% |
| assume_state | 59.5% [51.8%, 66.4%] (Wilson 46.8%, 73.4%) | 59.5% | 58.3% | 62.1% | 27.3% | 17.0% | 13.2% | 0.0% | 0.0% | 0.0% | 2.2% |
| mind_version | 58.9% [50.4%, 66.7%] (Wilson 47.0%, 73.6%) | 58.9% | 57.9% | 64.3% | 28.1% | 19.2% | 13.0% | 0.0% | 0.0% | 0.0% | 1.6% |
| no_retrieval | 59.5% [50.8%, 67.7%] (Wilson 47.0%, 73.6%) | 59.5% | 58.2% | 63.5% | 19.0% | 22.1% | 21.3% | 0.0% | 0.0% | 0.0% | 2.4% |
| oracle_docs | 81.7% [71.5%, 90.6%] (Wilson 70.4%, 91.3%) | 81.7% | 80.8% | 81.7% | 4.7% | 18.4% | 13.6% | 0.0% | 0.0% | 0.0% | 1.0% |
| plain_rag | 60.1% [51.8%, 67.9%] (Wilson 48.2%, 74.6%) | 60.1% | 58.6% | 64.6% | 29.2% | 20.6% | 10.7% | 0.0% | 0.0% | 0.0% | 2.2% |
| two_branch | 79.7% [69.6%, 88.6%] (Wilson 67.4%, 89.4%) | 79.7% | 78.9% | 79.8% | 4.8% | 16.8% | 15.5% | 0.0% | 0.0% | 0.0% | 0.9% |
| va_rag | 81.1% [71.2%, 89.6%] (Wilson 69.7%, 90.9%) | 81.1% | 80.8% | 81.9% | 2.6% | 18.0% | 16.2% | 0.0% | 0.0% | 0.0% | 0.3% |
| va_rag_no_ask | 63.6% [55.5%, 71.0%] (Wilson 51.2%, 77.2%) | 63.6% | 62.7% | 67.3% | 22.2% | 18.6% | 14.2% | 0.0% | 0.0% | 0.0% | 1.7% |
| va_rag_no_guard | 79.2% [69.2%, 88.1%] (Wilson 67.4%, 89.4%) | 79.2% | 78.9% | 80.0% | 4.7% | 17.4% | 16.1% | 0.0% | 0.0% | 0.0% | 0.3% |
| va_rag_no_infer | 81.1% [71.2%, 89.6%] (Wilson 69.7%, 90.9%) | 81.1% | 80.8% | 81.9% | 2.6% | 18.0% | 16.2% | 0.0% | 0.0% | 0.0% | 0.3% |
| va_rag_portable_first | 78.9% [69.5%, 87.3%] (Wilson 66.6%, 88.9%) | 78.9% | 78.4% | 79.4% | 2.9% | 21.3% | 18.1% | 0.0% | 0.0% | 0.0% | 0.7% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

### Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 34.6% | 100.0% | 100.0% | 0.0% | c=0.0: 59.8%, c=0.1: 49.8%, c=0.3: 29.8% | 1.00 calls, 1.00 answers |
| assume_state | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 59.5%, c=0.1: 59.5%, c=0.3: 59.5% | 1.00 calls, 1.00 answers |
| mind_version | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 2.8% | 42.9% | 1.9% | 0.0% | 0.0% | c=0.0: 58.9%, c=0.1: 58.7%, c=0.3: 58.3% | 1.02 calls, 1.00 answers |
| no_retrieval | 1.0% [0.0%, 2.4%] (Wilson 0.1%, 8.8%) | 0.1% [0.0%, 0.5%] (Wilson 0.0%, 7.6%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 59.5%, c=0.1: 59.5%, c=0.3: 59.5% | 1.00 calls, 1.00 answers |
| oracle_docs | 0.1% [0.0%, 0.5%] (Wilson 0.0%, 7.6%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 81.7%, c=0.1: 81.7%, c=0.3: 81.7% | 1.00 calls, 1.00 answers |
| plain_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 60.1%, c=0.1: 60.1%, c=0.3: 60.1% | 1.00 calls, 1.00 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 95.0% | c=0.0: 79.7%, c=0.1: 69.7%, c=0.3: 49.7% | 1.97 calls, 1.97 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 68.9% | 2.5% | 100.0% | 2.5% | c=0.0: 81.1%, c=0.1: 76.1%, c=0.3: 65.9% | 1.55 calls, 1.50 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 63.6%, c=0.1: 63.6%, c=0.3: 63.6% | 1.01 calls, 1.00 answers |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 68.9% | 2.5% | 100.0% | 2.5% | c=0.0: 79.2%, c=0.1: 74.2%, c=0.3: 64.0% | 1.50 calls, 1.50 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 35.5% | 95.0% | 100.0% | 95.0% | c=0.0: 81.1%, c=0.1: 71.1%, c=0.3: 51.1% | 2.04 calls, 1.97 answers |
| va_rag_portable_first | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 56.5% | 69.0% | 0.0% | 57.8% | 0.0% | c=0.0: 78.9%, c=0.1: 76.1%, c=0.3: 70.3% | 1.60 calls, 1.28 answers |

### Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | 0.185 | n/a |
| assume_state | old 15.4%, new 46.7%, both 0.0%, neither 37.8% (n=246) | 38.2% | 0.101 | n/a |
| mind_version | old 18.4%, new 25.5%, both 0.0%, neither 56.1% (n=239) | 39.3% | 0.225 | n/a |
| no_retrieval | old 13.8%, new 23.6%, both 0.0%, neither 62.6% (n=246) | 33.7% | 0.023 | n/a |
| oracle_docs | old 18.3%, new 29.7%, both 0.0%, neither 52.0% (n=246) | 45.9% | -0.011 | n/a |
| plain_rag | old 15.4%, new 30.5%, both 0.0%, neither 54.1% (n=246) | 35.0% | 0.162 | n/a |
| two_branch | old 16.7%, new 28.9%, both 0.0%, neither 54.5% (n=246) | 45.9% | -0.011 | 69.4% |
| va_rag |  (n=0) | 47.2% | 0.017 | 75.0% |
| va_rag_no_ask | old 17.5%, new 30.1%, both 0.0%, neither 52.4% (n=246) | 47.2% | 0.155 | n/a |
| va_rag_no_guard |  (n=0) | 45.9% | -0.004 | 71.6% |
| va_rag_no_infer |  (n=0) | n/a | 0.017 | 73.7% |
| va_rag_portable_first | old 0.0%, new 0.0%, both 0.0%, neither 100.0% (n=107) | 47.2% | 0.014 | 84.0% |

### Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"both": 357, "inferred": 336, "no_conflict": 18} | n/a | 24 | 0.0% | n/a | 54.2% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"inferred": 336, "no_conflict": 18, "unresolved": 357} | n/a | 8 | 0.0% | 0.0% | 37.5% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"both": 357, "inferred": 336, "no_conflict": 18} | n/a | 0 | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 237} | {"both": 693, "no_conflict": 18} | n/a | 24 | 0.0% | n/a | 54.2% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"both": 198, "inferred": 336, "no_conflict": 18, "portable": 159} | n/a | 23 | 0.0% | n/a | 52.2% | 0.0% |

Portable-first drafts (`va_rag_portable_first`): 357 drafts, 159 returned without a question (44.5%); rejected: {"exclusive or deprecated usage": 198}.

Risk-coverage sweep on |margin| for `va_rag` (coverage = answered without a question, risk = wrong-version commits among them):

| threshold | coverage | risk |
| --- | --- | --- |
| 14.00 | 0.9% | 0.0% |
| 4.00 | 40.2% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |

### Primary contrasts: va_rag against each baseline

Paired bootstrap on per-concept differences of instance scores (va_rag minus baseline); exact McNemar on the repeat-0 instance pairs, Holm-adjusted across the contrasts.

| Baseline | Metric | Difference | 95% bootstrap | discordant (va_rag only / baseline only) | McNemar p | Holm p |
| --- | --- | --- | --- | --- | --- | --- |
| always_ask | intended_pass | +20.5 pts | [+12.7, +28.4] | 58 / 8 | 0.0000 | 0.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +21.6 pts | [+13.5, +29.8] | 65 / 9 | 0.0000 | 0.0000 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| plain_rag | intended_pass | +20.4 pts | [+13.0, +28.0] | 59 / 12 | 0.0000 | 0.0000 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +2.0 pts | [-1.0, +5.6] | 6 / 3 | 0.5078 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

### Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

#### va_rag

**change_type**: behavior 49.1% (n=36); moved_import 100.0% (n=5); param_removed 83.3% (n=2); param_rename 88.7% (n=62); param_value 56.7% (n=30); symbol_removed 90.5% (n=14); symbol_rename 96.2% (n=79)

**clue_type**: code 74.7% (n=29); error 81.2% (n=23); pin 85.6% (n=30); pin-new+code-old 71.2% (n=22); pin-old+code-new 88.9% (n=12)

**condition**: clue 80.5% (n=82); contradiction 77.5% (n=34); no-clue 85.0% (n=82); stated 76.7% (n=30)

**exclusivity**: behavior 49.1% (n=36); deprecation 97.1% (n=68); one_directional 86.9% (n=28); removal 80.2% (n=96)

**gold_examples**: both 72.5% (n=51); neither 83.6% (n=177)

**gold_examples_x_change_type**: both / behavior 41.3% (n=21); both / symbol_removed 100.0% (n=6); both / symbol_rename 93.1% (n=24); neither / behavior 60.0% (n=15); neither / moved_import 100.0% (n=5); neither / param_removed 83.3% (n=2); neither / param_rename 88.7% (n=62); neither / param_value 56.7% (n=30); neither / symbol_removed 83.3% (n=8); neither / symbol_rename 97.6% (n=55)

**library**: numpy 71.4% (n=35); pandas 59.7% (n=62); pydantic 93.9% (n=131)

**target**: new 79.3% (n=124); old 83.3% (n=104)

**user_arm**: unsure 81.1% (n=228)

#### plain_rag

**change_type**: behavior 51.9% (n=36); moved_import 46.7% (n=5); param_removed 0.0% (n=2); param_rename 65.6% (n=62); param_value 35.6% (n=30); symbol_removed 83.3% (n=14); symbol_rename 67.1% (n=79)

**clue_type**: code 56.3% (n=29); error 63.8% (n=23); pin 84.4% (n=30); pin-new+code-old 45.5% (n=22); pin-old+code-new 50.0% (n=12)

**condition**: clue 68.7% (n=82); contradiction 47.1% (n=34); no-clue 51.2% (n=82); stated 75.6% (n=30)

**exclusivity**: behavior 51.9% (n=36); deprecation 63.7% (n=68); one_directional 73.8% (n=28); removal 56.6% (n=96)

**gold_examples**: both 58.8% (n=51); neither 60.5% (n=177)

**gold_examples_x_change_type**: both / behavior 47.6% (n=21); both / symbol_removed 66.7% (n=6); both / symbol_rename 66.7% (n=24); neither / behavior 57.8% (n=15); neither / moved_import 46.7% (n=5); neither / param_removed 0.0% (n=2); neither / param_rename 65.6% (n=62); neither / param_value 35.6% (n=30); neither / symbol_removed 95.8% (n=8); neither / symbol_rename 67.3% (n=55)

**library**: numpy 70.5% (n=35); pandas 48.9% (n=62); pydantic 62.6% (n=131)

**target**: new 65.3% (n=124); old 53.8% (n=104)

**user_arm**: unsure 60.1% (n=228)

#### mind_version

**change_type**: behavior 52.8% (n=36); moved_import 40.0% (n=5); param_removed 0.0% (n=2); param_rename 62.4% (n=62); param_value 36.7% (n=30); symbol_removed 85.7% (n=14); symbol_rename 65.4% (n=79)

**clue_type**: code 59.8% (n=29); error 69.6% (n=23); pin 86.7% (n=30); pin-new+code-old 45.5% (n=22); pin-old+code-new 50.0% (n=12)

**condition**: clue 72.4% (n=82); contradiction 47.1% (n=34); no-clue 45.1% (n=82); stated 73.3% (n=30)

**exclusivity**: behavior 52.8% (n=36); deprecation 61.3% (n=68); one_directional 71.4% (n=28); removal 55.9% (n=96)

**gold_examples**: both 60.1% (n=51); neither 58.6% (n=177)

**gold_examples_x_change_type**: both / behavior 47.6% (n=21); both / symbol_removed 66.7% (n=6); both / symbol_rename 69.4% (n=24); neither / behavior 60.0% (n=15); neither / moved_import 40.0% (n=5); neither / param_removed 0.0% (n=2); neither / param_rename 62.4% (n=62); neither / param_value 36.7% (n=30); neither / symbol_removed 100.0% (n=8); neither / symbol_rename 63.6% (n=55)

**library**: numpy 68.6% (n=35); pandas 48.9% (n=62); pydantic 61.1% (n=131)

**target**: new 60.5% (n=124); old 57.1% (n=104)

**user_arm**: unsure 58.9% (n=228)

#### two_branch

**change_type**: behavior 48.1% (n=36); moved_import 100.0% (n=5); param_removed 66.7% (n=2); param_rename 89.8% (n=62); param_value 43.3% (n=30); symbol_removed 88.1% (n=14); symbol_rename 97.5% (n=79)

**clue_type**: code 71.3% (n=29); error 78.3% (n=23); pin 85.6% (n=30); pin-new+code-old 78.8% (n=22); pin-old+code-new 77.8% (n=12)

**condition**: clue 78.5% (n=82); contradiction 78.4% (n=34); no-clue 82.5% (n=82); stated 76.7% (n=30)

**exclusivity**: behavior 48.1% (n=36); deprecation 99.0% (n=68); one_directional 81.0% (n=28); removal 77.4% (n=96)

**gold_examples**: both 71.9% (n=51); neither 81.9% (n=177)

**gold_examples_x_change_type**: both / behavior 41.3% (n=21); both / symbol_removed 88.9% (n=6); both / symbol_rename 94.4% (n=24); neither / behavior 57.8% (n=15); neither / moved_import 100.0% (n=5); neither / param_removed 66.7% (n=2); neither / param_rename 89.8% (n=62); neither / param_value 43.3% (n=30); neither / symbol_removed 87.5% (n=8); neither / symbol_rename 98.8% (n=55)

**library**: numpy 68.6% (n=35); pandas 53.2% (n=62); pydantic 95.2% (n=131)

**target**: new 77.4% (n=124); old 82.4% (n=104)

**user_arm**: unsure 79.7% (n=228)

#### always_ask

**change_type**: behavior 52.8% (n=36); moved_import 53.3% (n=5); param_removed 0.0% (n=2); param_rename 64.5% (n=62); param_value 40.0% (n=30); symbol_removed 85.7% (n=14); symbol_rename 64.1% (n=79)

**clue_type**: code 57.5% (n=29); error 63.8% (n=23); pin 88.9% (n=30); pin-new+code-old 45.5% (n=22); pin-old+code-new 47.2% (n=12)

**condition**: clue 70.7% (n=82); contradiction 46.1% (n=34); no-clue 49.2% (n=82); stated 74.4% (n=30)

**exclusivity**: behavior 52.8% (n=36); deprecation 63.2% (n=68); one_directional 72.6% (n=28); removal 56.2% (n=96)

**gold_examples**: both 56.2% (n=51); neither 60.8% (n=177)

**gold_examples_x_change_type**: both / behavior 41.3% (n=21); both / symbol_removed 66.7% (n=6); both / symbol_rename 66.7% (n=24); neither / behavior 68.9% (n=15); neither / moved_import 53.3% (n=5); neither / param_removed 0.0% (n=2); neither / param_rename 64.5% (n=62); neither / param_value 40.0% (n=30); neither / symbol_removed 100.0% (n=8); neither / symbol_rename 63.0% (n=55)

**library**: numpy 69.5% (n=35); pandas 51.1% (n=62); pydantic 61.3% (n=131)

**target**: new 61.6% (n=124); old 57.7% (n=104)

**user_arm**: unsure 59.8% (n=228)

### What size of difference this run can show

228 targeted instances over 48 concepts (4.8 per concept), 3 repeats averaged per instance. Measured within-concept correlation rho = 0.351 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.151 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.351 | 8.9 points | measured rho |
| 0.200 | 0.351 | 12.6 points | measured rho |
| 0.300 | 0.351 | 15.5 points | measured rho |
| 0.151 | 0.351 | 11.0 points | observed |
| 0.200 | 0.250 | 11.5 points | handoff assumption |
| 0.200 | 0.500 | 14.1 points | handoff assumption |

### Repeat disagreement (within this session)

2844 (instance, method) pairs answered under 3 repeats: response text differs on 66.7%, outcome on 15.8%, intended-version pass on 11.4%.

| Method | pairs | text differs | outcome differs |
| --- | --- | --- | --- |
| always_ask | 237 | 64.1% | 16.9% |
| assume_state | 237 | 92.8% | 20.7% |
| mind_version | 237 | 65.4% | 20.3% |
| no_retrieval | 237 | 55.3% | 21.5% |
| oracle_docs | 237 | 62.0% | 11.8% |
| plain_rag | 237 | 65.8% | 18.1% |
| two_branch | 237 | 73.0% | 13.5% |
| va_rag | 237 | 62.9% | 11.4% |
| va_rag_no_ask | 237 | 60.3% | 14.3% |
| va_rag_no_guard | 237 | 62.9% | 11.8% |
| va_rag_no_infer | 237 | 72.2% | 11.4% |
| va_rag_portable_first | 237 | 63.7% | 18.1% |
