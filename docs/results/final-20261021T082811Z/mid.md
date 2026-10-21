# VA-RAG final sweep: mid (20261021T082811Z)

Session `cloudflare@20261021T082811Z`; cost $2.4011; run time 2.3 h. Each section below is one run's full report.

# dev-knows

## VA-RAG run report: 20261021T085318Z-mid-d8ec0624

- Model: `mid` = qwen/qwen-2.5-coder-32b-instruct
- Split: dev; user arm: knows; instances: 101; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T09:25:57+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen-2.5-coder-32b-instruct` pinned to provider `cloudflare` (no fallbacks, parameters required); session `cloudflare@20261021T082811Z`; 887 paid calls, 635 cache hits, $0.5448; providers reported {'Cloudflare': 1212}

### Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 72.6% [55.2%, 87.6%] (Wilson 45.3%, 87.3%) | 72.6% | 69.5% | 72.6% | 11.6% | 15.8% | 15.8% | 0.0% | 0.0% | 0.0% | 4.3% |
| assume_state | 60.0% [46.7%, 71.8%] (Wilson 37.0%, 81.2%) | 60.0% | 54.7% | 64.2% | 17.9% | 17.9% | 22.1% | 0.0% | 0.0% | 0.0% | 8.8% |
| mind_version | 75.8% [58.9%, 90.0%] (Wilson 48.0%, 89.1%) | 75.8% | 72.6% | 76.8% | 5.3% | 20.0% | 18.9% | 0.0% | 0.0% | 0.0% | 4.2% |
| no_retrieval | 50.5% [34.4%, 66.0%] (Wilson 24.1%, 69.1%) | 50.5% | 49.5% | 53.7% | 23.2% | 17.9% | 26.3% | 0.0% | 0.0% | 0.0% | 2.1% |
| oracle_docs | 70.5% [54.1%, 85.0%] (Wilson 43.5%, 86.1%) | 70.5% | 67.4% | 70.5% | 12.6% | 18.9% | 16.8% | 0.0% | 0.0% | 0.0% | 4.5% |
| plain_rag | 64.2% [48.6%, 78.9%] (Wilson 38.3%, 82.2%) | 64.2% | 61.1% | 65.3% | 18.9% | 17.9% | 16.8% | 0.0% | 0.0% | 0.0% | 4.9% |
| two_branch | 72.6% [55.2%, 87.6%] (Wilson 45.3%, 87.3%) | 72.6% | 69.5% | 72.6% | 11.6% | 15.8% | 15.8% | 0.0% | 0.0% | 0.0% | 4.3% |
| va_rag | 80.0% [63.2%, 93.0%] (Wilson 51.9%, 91.4%) | 80.0% | 80.0% | 80.0% | 3.2% | 18.9% | 16.8% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_no_ask | 68.4% [53.3%, 81.1%] (Wilson 41.7%, 84.8%) | 68.4% | 67.4% | 69.5% | 15.8% | 17.9% | 15.8% | 0.0% | 0.0% | 0.0% | 1.5% |
| va_rag_no_guard | 73.7% [56.7%, 88.0%] (Wilson 46.2%, 87.9%) | 73.7% | 70.5% | 73.7% | 9.5% | 14.7% | 16.8% | 0.0% | 0.0% | 0.0% | 4.3% |
| va_rag_no_infer | 80.0% [63.2%, 93.0%] (Wilson 51.9%, 91.4%) | 80.0% | 80.0% | 80.0% | 3.2% | 18.9% | 16.8% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_portable_first | 80.0% [64.2%, 92.4%] (Wilson 54.3%, 92.7%) | 80.0% | 80.0% | 80.0% | 1.1% | 21.1% | 18.9% | 0.0% | 0.0% | 0.0% | 0.0% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

### Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 0.0% | 100.0% | 27.7% | 100.0% | 100.0% | 0.0% | c=0.0: 72.6%, c=0.1: 62.6%, c=0.3: 42.6% | 1.00 calls, 1.00 answers |
| assume_state | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 60.0%, c=0.1: 60.0%, c=0.3: 60.0% | 1.00 calls, 1.00 answers |
| mind_version | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 0.0% | 100.0% | 35.9% | 65.0% | 84.6% | 0.0% | c=0.0: 75.8%, c=0.1: 68.2%, c=0.3: 53.1% | 1.77 calls, 1.00 answers |
| no_retrieval | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 39.3% | 29.5% | 43.3% | 38.5% | 0.0% | c=0.0: 50.5%, c=0.1: 45.9%, c=0.3: 36.6% | 1.44 calls, 1.00 answers |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 10.0% | 11.7% | 15.4% | 0.0% | c=0.0: 70.5%, c=0.1: 69.5%, c=0.3: 67.4% | 1.10 calls, 1.00 answers |
| plain_rag | 2.1% [0.0%, 6.7%] (Wilson 0.1%, 23.3%) | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 0.0% | 25.0% | 41.2% | 13.3% | 15.4% | 0.0% | c=0.0: 64.2%, c=0.1: 62.4%, c=0.3: 58.8% | 1.17 calls, 1.00 answers |
| two_branch | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 93.3% | c=0.0: 72.6%, c=0.1: 62.6%, c=0.3: 42.6% | 1.96 calls, 1.96 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 0.0% | c=0.0: 80.0%, c=0.1: 75.7%, c=0.3: 67.1% | 1.10 calls, 1.00 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 68.4%, c=0.1: 68.4%, c=0.3: 68.4% | 1.06 calls, 1.00 answers |
| va_rag_no_guard | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 0.0% | c=0.0: 73.7%, c=0.1: 69.4%, c=0.3: 60.7% | 1.00 calls, 1.00 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 28.9% | 93.3% | 100.0% | 0.0% | c=0.0: 80.0%, c=0.1: 70.0%, c=0.3: 50.0% | 1.10 calls, 1.00 answers |
| va_rag_portable_first | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 67.9% | 67.9% | 0.0% | 69.2% | 0.0% | c=0.0: 80.0%, c=0.1: 77.1%, c=0.3: 71.2% | 1.38 calls, 1.00 answers |

### Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | -0.076 | n/a |
| assume_state | old 17.9%, new 35.7%, both 0.0%, neither 46.4% (n=28) | 32.1% | -0.069 | n/a |
| mind_version |  (n=0) | 0.0% | -0.046 | n/a |
| no_retrieval | old 46.7%, new 0.0%, both 0.0%, neither 53.3% (n=15) | 23.1% | -0.031 | n/a |
| oracle_docs | old 25.9%, new 33.3%, both 0.0%, neither 40.7% (n=27) | 43.5% | -0.125 | n/a |
| plain_rag | old 33.3%, new 23.8%, both 4.8%, neither 38.1% (n=21) | 27.3% | 0.072 | n/a |
| two_branch | old 21.4%, new 32.1%, both 3.6%, neither 42.9% (n=28) | 50.0% | -0.076 | 54.7% |
| va_rag |  (n=0) | 57.1% | -0.077 | n/a |
| va_rag_no_ask | old 28.6%, new 28.6%, both 0.0%, neither 42.9% (n=28) | 57.1% | 0.041 | n/a |
| va_rag_no_guard |  (n=0) | 57.1% | -0.095 | n/a |
| va_rag_no_infer |  (n=0) | n/a | -0.077 | n/a |
| va_rag_portable_first | old 0.0%, new 0.0%, both 0.0%, neither 100.0% (n=9) | 57.1% | -0.077 | n/a |

### Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision, exclusive-error oracle | guard recall, exclusive-error oracle | guard precision, strict-named oracle | guard recall, strict-named oracle | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"asked": 43, "inferred": 54, "no_conflict": 4} | n/a | 10 | 50.0% | 100.0% | 80.0% | 100.0% | 60.0% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"inferred": 54, "no_conflict": 4, "unresolved": 43} | n/a | 6 | 50.0% | 37.5% | 83.3% | 33.3% | 50.0% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"asked": 43, "inferred": 54, "no_conflict": 4} | n/a | 0 | n/a | 0.0% | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 101} | {"asked": 97, "no_conflict": 4} | n/a | 10 | 50.0% | 100.0% | 80.0% | 100.0% | 60.0% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"asked": 28, "inferred": 54, "no_conflict": 4, "portable": 15} | n/a | 10 | 50.0% | 100.0% | 80.0% | 100.0% | 60.0% | 0.0% |

Guard oracles (`varag.eval.oracle`): exclusive-error (M7) counts a failure whose AttributeError, ImportError or TypeError names an exclusive symbol; strict-named (2026-10-21 correction) counts a strict failure in the committed version whose error, traceback, counted warning or failing line shows the usage, so rejected values and deprecation warnings count too.

Portable-first drafts (`va_rag_portable_first`): 43 drafts, 15 returned without a question (34.9%); rejected: {"exclusive or deprecated usage": 28}.

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
| always_ask | intended_pass | +6.7 pts | [+0.0, +16.2] | 7 / 0 | 0.0156 | 0.1094 |
| always_ask | blend_exec | -1.0 pts | [-2.9, +0.0] | 0 / 1 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +3.8 pts | [-5.7, +14.3] | 8 / 4 | 0.3877 | 1.0000 |
| mind_version | blend_exec | -1.0 pts | [-2.9, +0.0] | 0 / 1 | 1.0000 | 1.0000 |
| plain_rag | intended_pass | +14.3 pts | [+3.8, +25.7] | 18 / 3 | 0.0015 | 0.0119 |
| plain_rag | blend_exec | -1.0 pts | [-2.9, +0.0] | 0 / 1 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +6.7 pts | [+0.0, +16.2] | 7 / 0 | 0.0156 | 0.1094 |
| two_branch | blend_exec | -1.0 pts | [-2.9, +0.0] | 0 / 1 | 1.0000 | 1.0000 |

### Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

#### va_rag

**change_type**: behavior 28.6% (n=14); param_removed 100.0% (n=2); param_rename 81.1% (n=37); param_value 100.0% (n=7); symbol_rename 94.3% (n=35)

**clue_type**: code 81.8% (n=11); error 83.3% (n=6); pin 72.7% (n=11); pin-new+code-old 83.3% (n=6); pin-old+code-new 85.7% (n=7)

**condition**: clue 78.6% (n=28); contradiction 84.6% (n=13); no-clue 75.0% (n=28); stated 84.6% (n=26)

**exclusivity**: behavior 28.6% (n=14); deprecation 85.7% (n=21); one_directional 50.0% (n=4); removal 92.9% (n=56)

**gold_examples**: both 77.3% (n=44); neither 82.4% (n=51)

**gold_examples_x_change_type**: both / behavior 28.6% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 81.1% (n=37); neither / symbol_rename 85.7% (n=14)

**library**: numpy 68.8% (n=16); pandas 76.7% (n=30); pydantic 85.7% (n=49)

**target**: new 78.4% (n=51); old 81.8% (n=44)

**user_arm**: knows 80.0% (n=95)

#### plain_rag

**change_type**: behavior 42.9% (n=14); param_removed 100.0% (n=2); param_rename 64.9% (n=37); param_value 85.7% (n=7); symbol_rename 65.7% (n=35)

**clue_type**: code 45.5% (n=11); error 83.3% (n=6); pin 72.7% (n=11); pin-new+code-old 50.0% (n=6); pin-old+code-new 57.1% (n=7)

**condition**: clue 64.3% (n=28); contradiction 53.8% (n=13); no-clue 60.7% (n=28); stated 73.1% (n=26)

**exclusivity**: behavior 42.9% (n=14); deprecation 76.2% (n=21); one_directional 50.0% (n=4); removal 66.1% (n=56)

**gold_examples**: both 61.4% (n=44); neither 66.7% (n=51)

**gold_examples_x_change_type**: both / behavior 42.9% (n=14); both / param_removed 100.0% (n=2); both / param_value 85.7% (n=7); both / symbol_rename 61.9% (n=21); neither / param_rename 64.9% (n=37); neither / symbol_rename 71.4% (n=14)

**library**: numpy 62.5% (n=16); pandas 60.0% (n=30); pydantic 67.3% (n=49)

**target**: new 60.8% (n=51); old 68.2% (n=44)

**user_arm**: knows 64.2% (n=95)

#### mind_version

**change_type**: behavior 50.0% (n=14); param_removed 100.0% (n=2); param_rename 73.0% (n=37); param_value 100.0% (n=7); symbol_rename 82.9% (n=35)

**clue_type**: code 81.8% (n=11); error 83.3% (n=6); pin 72.7% (n=11); pin-new+code-old 50.0% (n=6); pin-old+code-new 100.0% (n=7)

**condition**: clue 78.6% (n=28); contradiction 76.9% (n=13); no-clue 71.4% (n=28); stated 76.9% (n=26)

**exclusivity**: behavior 50.0% (n=14); deprecation 81.0% (n=21); one_directional 50.0% (n=4); removal 82.1% (n=56)

**gold_examples**: both 72.7% (n=44); neither 78.4% (n=51)

**gold_examples_x_change_type**: both / behavior 50.0% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 76.2% (n=21); neither / param_rename 73.0% (n=37); neither / symbol_rename 92.9% (n=14)

**library**: numpy 81.2% (n=16); pandas 63.3% (n=30); pydantic 81.6% (n=49)

**target**: new 74.5% (n=51); old 77.3% (n=44)

**user_arm**: knows 75.8% (n=95)

#### two_branch

**change_type**: behavior 28.6% (n=14); param_removed 100.0% (n=2); param_rename 73.0% (n=37); param_value 100.0% (n=7); symbol_rename 82.9% (n=35)

**clue_type**: code 72.7% (n=11); error 83.3% (n=6); pin 72.7% (n=11); pin-new+code-old 66.7% (n=6); pin-old+code-new 71.4% (n=7)

**condition**: clue 75.0% (n=28); contradiction 69.2% (n=13); no-clue 67.9% (n=28); stated 76.9% (n=26)

**exclusivity**: behavior 28.6% (n=14); deprecation 85.7% (n=21); one_directional 50.0% (n=4); removal 80.4% (n=56)

**gold_examples**: both 68.2% (n=44); neither 76.5% (n=51)

**gold_examples_x_change_type**: both / behavior 28.6% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 81.0% (n=21); neither / param_rename 73.0% (n=37); neither / symbol_rename 85.7% (n=14)

**library**: numpy 68.8% (n=16); pandas 63.3% (n=30); pydantic 79.6% (n=49)

**target**: new 70.6% (n=51); old 75.0% (n=44)

**user_arm**: knows 72.6% (n=95)

#### always_ask

**change_type**: behavior 28.6% (n=14); param_removed 100.0% (n=2); param_rename 73.0% (n=37); param_value 100.0% (n=7); symbol_rename 82.9% (n=35)

**clue_type**: code 72.7% (n=11); error 83.3% (n=6); pin 72.7% (n=11); pin-new+code-old 66.7% (n=6); pin-old+code-new 71.4% (n=7)

**condition**: clue 75.0% (n=28); contradiction 69.2% (n=13); no-clue 67.9% (n=28); stated 76.9% (n=26)

**exclusivity**: behavior 28.6% (n=14); deprecation 85.7% (n=21); one_directional 50.0% (n=4); removal 80.4% (n=56)

**gold_examples**: both 68.2% (n=44); neither 76.5% (n=51)

**gold_examples_x_change_type**: both / behavior 28.6% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 81.0% (n=21); neither / param_rename 73.0% (n=37); neither / symbol_rename 85.7% (n=14)

**library**: numpy 68.8% (n=16); pandas 63.3% (n=30); pydantic 79.6% (n=49)

**target**: new 70.6% (n=51); old 75.0% (n=44)

**user_arm**: knows 72.6% (n=95)

### What size of difference this run can show

95 targeted instances over 15 concepts (6.3 per concept). Measured within-concept correlation rho = 0.377 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.147 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.377 | 15.8 points | measured rho |
| 0.200 | 0.377 | 22.3 points | measured rho |
| 0.300 | 0.377 | 27.3 points | measured rho |
| 0.147 | 0.377 | 19.1 points | observed |
| 0.200 | 0.250 | 19.6 points | handoff assumption |
| 0.200 | 0.500 | 24.6 points | handoff assumption |

# dev-noise-repeat

## VA-RAG run report: 20261021T092612Z-mid-04020e62

- Model: `mid` = qwen/qwen-2.5-coder-32b-instruct
- Split: dev; user arm: knows; instances: 20; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T09:33:11+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen-2.5-coder-32b-instruct` pinned to provider `cloudflare` (no fallbacks, parameters required); session `cloudflare@20261021T082811Z`; 191 paid calls, 110 cache hits, $0.1078; providers reported {'Cloudflare': 240}

### Primary metrics

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

### Blending, asking, hedging, cost

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

### Commit direction, clue following, order

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

### Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision, exclusive-error oracle | guard recall, exclusive-error oracle | guard precision, strict-named oracle | guard recall, strict-named oracle | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"INFER": 12, "UNCERTAIN": 8} | {"asked": 7, "inferred": 12, "no_conflict": 1} | n/a | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| va_rag_no_ask | 100.0% | 100.0% | {"INFER": 12, "UNCERTAIN": 8} | {"inferred": 12, "no_conflict": 1, "unresolved": 7} | n/a | 0 | n/a | 0.0% | n/a | 0.0% | n/a | n/a |
| va_rag_no_guard | 100.0% | 100.0% | {"INFER": 12, "UNCERTAIN": 8} | {"asked": 7, "inferred": 12, "no_conflict": 1} | n/a | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 20} | {"asked": 19, "no_conflict": 1} | n/a | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| va_rag_portable_first | 100.0% | 100.0% | {"INFER": 12, "UNCERTAIN": 8} | {"asked": 5, "inferred": 12, "no_conflict": 1, "portable": 2} | n/a | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

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

### Primary contrasts: va_rag against each baseline

Paired bootstrap on per-concept differences of instance scores (va_rag minus baseline); exact McNemar on the repeat-0 instance pairs, Holm-adjusted across the contrasts.

| Baseline | Metric | Difference | 95% bootstrap | discordant (va_rag only / baseline only) | McNemar p | Holm p |
| --- | --- | --- | --- | --- | --- | --- |
| always_ask | intended_pass | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +3.0 pts | [+0.0, +9.1] | 1 / 0 | 1.0000 | 1.0000 |
| mind_version | blend_exec | -4.5 pts | [-13.6, +0.0] | 0 / 1 | 1.0000 | 1.0000 |
| plain_rag | intended_pass | +19.7 pts | [+0.0, +42.4] | 4 / 0 | 0.1250 | 1.0000 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

### Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

#### va_rag

**change_type**: behavior 100.0% (n=3); param_rename 71.4% (n=7); param_value 100.0% (n=1); symbol_rename 87.5% (n=8)

**clue_type**: code 100.0% (n=4); pin 100.0% (n=3)

**condition**: clue 100.0% (n=7); no-clue 71.4% (n=7); stated 80.0% (n=5)

**exclusivity**: behavior 100.0% (n=3); deprecation 75.0% (n=4); one_directional 0.0% (n=1); removal 90.9% (n=11)

**gold_examples**: both 100.0% (n=8); neither 72.7% (n=11)

**gold_examples_x_change_type**: both / behavior 100.0% (n=3); both / param_value 100.0% (n=1); both / symbol_rename 100.0% (n=4); neither / param_rename 71.4% (n=7); neither / symbol_rename 75.0% (n=4)

**library**: numpy 85.7% (n=7); pandas 100.0% (n=3); pydantic 77.8% (n=9)

**target**: new 75.0% (n=8); old 90.9% (n=11)

**user_arm**: knows 84.2% (n=19)

#### plain_rag

**change_type**: behavior 100.0% (n=3); param_rename 42.9% (n=7); param_value 100.0% (n=1); symbol_rename 62.5% (n=8)

**clue_type**: code 75.0% (n=4); pin 66.7% (n=3)

**condition**: clue 71.4% (n=7); no-clue 57.1% (n=7); stated 60.0% (n=5)

**exclusivity**: behavior 100.0% (n=3); deprecation 75.0% (n=4); one_directional 0.0% (n=1); removal 54.5% (n=11)

**gold_examples**: both 75.0% (n=8); neither 54.5% (n=11)

**gold_examples_x_change_type**: both / behavior 100.0% (n=3); both / param_value 100.0% (n=1); both / symbol_rename 50.0% (n=4); neither / param_rename 42.9% (n=7); neither / symbol_rename 75.0% (n=4)

**library**: numpy 57.1% (n=7); pandas 100.0% (n=3); pydantic 55.6% (n=9)

**target**: new 50.0% (n=8); old 72.7% (n=11)

**user_arm**: knows 63.2% (n=19)

#### mind_version

**change_type**: behavior 100.0% (n=3); param_rename 71.4% (n=7); param_value 100.0% (n=1); symbol_rename 75.0% (n=8)

**clue_type**: code 100.0% (n=4); pin 100.0% (n=3)

**condition**: clue 100.0% (n=7); no-clue 71.4% (n=7); stated 60.0% (n=5)

**exclusivity**: behavior 100.0% (n=3); deprecation 75.0% (n=4); one_directional 0.0% (n=1); removal 81.8% (n=11)

**gold_examples**: both 87.5% (n=8); neither 72.7% (n=11)

**gold_examples_x_change_type**: both / behavior 100.0% (n=3); both / param_value 100.0% (n=1); both / symbol_rename 75.0% (n=4); neither / param_rename 71.4% (n=7); neither / symbol_rename 75.0% (n=4)

**library**: numpy 71.4% (n=7); pandas 100.0% (n=3); pydantic 77.8% (n=9)

**target**: new 62.5% (n=8); old 90.9% (n=11)

**user_arm**: knows 78.9% (n=19)

#### two_branch

**change_type**: behavior 100.0% (n=3); param_rename 71.4% (n=7); param_value 100.0% (n=1); symbol_rename 87.5% (n=8)

**clue_type**: code 100.0% (n=4); pin 100.0% (n=3)

**condition**: clue 100.0% (n=7); no-clue 71.4% (n=7); stated 80.0% (n=5)

**exclusivity**: behavior 100.0% (n=3); deprecation 75.0% (n=4); one_directional 0.0% (n=1); removal 90.9% (n=11)

**gold_examples**: both 100.0% (n=8); neither 72.7% (n=11)

**gold_examples_x_change_type**: both / behavior 100.0% (n=3); both / param_value 100.0% (n=1); both / symbol_rename 100.0% (n=4); neither / param_rename 71.4% (n=7); neither / symbol_rename 75.0% (n=4)

**library**: numpy 85.7% (n=7); pandas 100.0% (n=3); pydantic 77.8% (n=9)

**target**: new 75.0% (n=8); old 90.9% (n=11)

**user_arm**: knows 84.2% (n=19)

#### always_ask

**change_type**: behavior 100.0% (n=3); param_rename 71.4% (n=7); param_value 100.0% (n=1); symbol_rename 87.5% (n=8)

**clue_type**: code 100.0% (n=4); pin 100.0% (n=3)

**condition**: clue 100.0% (n=7); no-clue 71.4% (n=7); stated 80.0% (n=5)

**exclusivity**: behavior 100.0% (n=3); deprecation 75.0% (n=4); one_directional 0.0% (n=1); removal 90.9% (n=11)

**gold_examples**: both 100.0% (n=8); neither 72.7% (n=11)

**gold_examples_x_change_type**: both / behavior 100.0% (n=3); both / param_value 100.0% (n=1); both / symbol_rename 100.0% (n=4); neither / param_rename 71.4% (n=7); neither / symbol_rename 75.0% (n=4)

**library**: numpy 85.7% (n=7); pandas 100.0% (n=3); pydantic 77.8% (n=9)

**target**: new 75.0% (n=8); old 90.9% (n=11)

**user_arm**: knows 84.2% (n=19)

### What size of difference this run can show

19 targeted instances over 11 concepts (1.7 per concept). Measured within-concept correlation rho = 0.083 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.096 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.083 | 20.9 points | measured rho |
| 0.200 | 0.083 | 29.6 points | measured rho |
| 0.300 | 0.083 | 36.3 points | measured rho |
| 0.096 | 0.083 | 20.5 points | observed |
| 0.200 | 0.250 | 31.2 points | handoff assumption |
| 0.200 | 0.500 | 33.6 points | handoff assumption |

# dev-unsure

## VA-RAG run report: 20261021T093318Z-mid-7a546ea0

- Model: `mid` = qwen/qwen-2.5-coder-32b-instruct
- Split: dev; user arm: unsure; instances: 101; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T09:43:40+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen-2.5-coder-32b-instruct` pinned to provider `cloudflare` (no fallbacks, parameters required); session `cloudflare@20261021T082811Z`; 202 paid calls, 1552 cache hits, $0.1439; providers reported {'Cloudflare': 1212}

### Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 61.1% [45.6%, 76.0%] (Wilson 35.7%, 80.2%) | 61.1% | 57.9% | 64.2% | 22.1% | 20.0% | 16.8% | 0.0% | 0.0% | 0.0% | 5.2% |
| assume_state | 60.0% [46.7%, 71.8%] (Wilson 37.0%, 81.2%) | 60.0% | 54.7% | 64.2% | 17.9% | 17.9% | 22.1% | 0.0% | 0.0% | 0.0% | 8.8% |
| mind_version | 57.9% [42.9%, 72.6%] (Wilson 31.3%, 76.3%) | 57.9% | 53.7% | 62.1% | 26.3% | 25.3% | 15.8% | 0.0% | 0.0% | 0.0% | 7.3% |
| no_retrieval | 48.4% [31.6%, 64.2%] (Wilson 22.6%, 67.5%) | 48.4% | 46.3% | 52.6% | 25.3% | 18.9% | 26.3% | 0.0% | 0.0% | 0.0% | 4.3% |
| oracle_docs | 69.5% [53.3%, 83.8%] (Wilson 42.6%, 85.5%) | 69.5% | 66.3% | 69.5% | 14.7% | 18.9% | 15.8% | 0.0% | 0.0% | 0.0% | 4.5% |
| plain_rag | 60.0% [44.2%, 75.6%] (Wilson 34.9%, 79.5%) | 60.0% | 56.8% | 63.2% | 23.2% | 20.0% | 16.8% | 0.0% | 0.0% | 0.0% | 5.3% |
| two_branch | 72.6% [55.2%, 87.6%] (Wilson 45.3%, 87.3%) | 72.6% | 69.5% | 72.6% | 11.6% | 15.8% | 15.8% | 0.0% | 0.0% | 0.0% | 4.3% |
| va_rag | 80.0% [63.2%, 93.0%] (Wilson 51.9%, 91.4%) | 80.0% | 80.0% | 80.0% | 3.2% | 18.9% | 16.8% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_no_ask | 68.4% [53.3%, 81.1%] (Wilson 41.7%, 84.8%) | 68.4% | 67.4% | 69.5% | 15.8% | 17.9% | 15.8% | 0.0% | 0.0% | 0.0% | 1.5% |
| va_rag_no_guard | 73.7% [56.7%, 88.0%] (Wilson 46.2%, 87.9%) | 73.7% | 70.5% | 73.7% | 9.5% | 14.7% | 16.8% | 0.0% | 0.0% | 0.0% | 4.3% |
| va_rag_no_infer | 80.0% [63.2%, 93.0%] (Wilson 51.9%, 91.4%) | 80.0% | 80.0% | 80.0% | 3.2% | 18.9% | 16.8% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag_portable_first | 80.0% [64.2%, 92.4%] (Wilson 54.3%, 92.7%) | 80.0% | 80.0% | 80.0% | 1.1% | 21.1% | 18.9% | 0.0% | 0.0% | 0.0% | 0.0% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

### Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 2.1% [0.0%, 6.7%] (Wilson 0.1%, 23.3%) | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 0.0% | 100.0% | 27.7% | 100.0% | 100.0% | 0.0% | c=0.0: 61.1%, c=0.1: 51.1%, c=0.3: 31.1% | 1.00 calls, 1.00 answers |
| assume_state | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 60.0%, c=0.1: 60.0%, c=0.3: 60.0% | 1.00 calls, 1.00 answers |
| mind_version | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 0.0% | 100.0% | 35.9% | 65.0% | 84.6% | 0.0% | c=0.0: 57.9%, c=0.1: 50.3%, c=0.3: 35.2% | 1.77 calls, 1.00 answers |
| no_retrieval | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 39.3% | 29.5% | 43.3% | 38.5% | 0.0% | c=0.0: 48.4%, c=0.1: 43.8%, c=0.3: 34.5% | 1.44 calls, 1.00 answers |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | 10.0% | 11.7% | 15.4% | 0.0% | c=0.0: 69.5%, c=0.1: 68.4%, c=0.3: 66.3% | 1.10 calls, 1.00 answers |
| plain_rag | 2.1% [0.0%, 6.7%] (Wilson 0.1%, 23.3%) | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 0.0% | 25.0% | 41.2% | 13.3% | 15.4% | 0.0% | c=0.0: 60.0%, c=0.1: 58.2%, c=0.3: 54.6% | 1.17 calls, 1.00 answers |
| two_branch | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 93.3% | c=0.0: 72.6%, c=0.1: 62.6%, c=0.3: 42.6% | 1.96 calls, 1.96 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 3.3% | c=0.0: 80.0%, c=0.1: 75.7%, c=0.3: 67.1% | 1.57 calls, 1.43 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 68.4%, c=0.1: 68.4%, c=0.3: 68.4% | 1.06 calls, 1.00 answers |
| va_rag_no_guard | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 3.3% | c=0.0: 73.7%, c=0.1: 69.4%, c=0.3: 60.7% | 1.43 calls, 1.43 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 28.9% | 93.3% | 100.0% | 93.3% | c=0.0: 80.0%, c=0.1: 70.0%, c=0.3: 50.0% | 2.17 calls, 1.96 answers |
| va_rag_portable_first | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 67.9% | 67.9% | 0.0% | 69.2% | 0.0% | c=0.0: 80.0%, c=0.1: 77.1%, c=0.3: 71.2% | 1.70 calls, 1.28 answers |

### Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | 0.084 | n/a |
| assume_state | old 17.9%, new 35.7%, both 0.0%, neither 46.4% (n=28) | 32.1% | -0.069 | n/a |
| mind_version |  (n=0) | 0.0% | 0.054 | n/a |
| no_retrieval | old 46.7%, new 0.0%, both 0.0%, neither 53.3% (n=15) | 23.1% | 0.006 | n/a |
| oracle_docs | old 25.9%, new 33.3%, both 0.0%, neither 40.7% (n=27) | 43.5% | -0.150 | n/a |
| plain_rag | old 33.3%, new 23.8%, both 4.8%, neither 38.1% (n=21) | 27.3% | 0.060 | n/a |
| two_branch | old 21.4%, new 32.1%, both 3.6%, neither 42.9% (n=28) | 50.0% | -0.076 | 54.7% |
| va_rag |  (n=0) | 57.1% | -0.077 | 65.9% |
| va_rag_no_ask | old 28.6%, new 28.6%, both 0.0%, neither 42.9% (n=28) | 57.1% | 0.041 | n/a |
| va_rag_no_guard |  (n=0) | 57.1% | -0.095 | 53.7% |
| va_rag_no_infer |  (n=0) | n/a | -0.077 | 66.3% |
| va_rag_portable_first | old 0.0%, new 0.0%, both 0.0%, neither 100.0% (n=9) | 57.1% | -0.077 | 82.1% |

### Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision, exclusive-error oracle | guard recall, exclusive-error oracle | guard precision, strict-named oracle | guard recall, strict-named oracle | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"both": 43, "inferred": 54, "no_conflict": 4} | n/a | 10 | 50.0% | 100.0% | 80.0% | 100.0% | 60.0% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"inferred": 54, "no_conflict": 4, "unresolved": 43} | n/a | 6 | 50.0% | 37.5% | 83.3% | 33.3% | 50.0% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"both": 43, "inferred": 54, "no_conflict": 4} | n/a | 0 | n/a | 0.0% | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 101} | {"both": 97, "no_conflict": 4} | n/a | 10 | 50.0% | 100.0% | 80.0% | 100.0% | 60.0% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"both": 28, "inferred": 54, "no_conflict": 4, "portable": 15} | n/a | 10 | 50.0% | 100.0% | 80.0% | 100.0% | 60.0% | 0.0% |

Guard oracles (`varag.eval.oracle`): exclusive-error (M7) counts a failure whose AttributeError, ImportError or TypeError names an exclusive symbol; strict-named (2026-10-21 correction) counts a strict failure in the committed version whose error, traceback, counted warning or failing line shows the usage, so rejected values and deprecation warnings count too.

Portable-first drafts (`va_rag_portable_first`): 43 drafts, 15 returned without a question (34.9%); rejected: {"exclusive or deprecated usage": 28}.

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
| always_ask | intended_pass | +17.1 pts | [+4.8, +28.6] | 21 / 3 | 0.0003 | 0.0017 |
| always_ask | blend_exec | -1.0 pts | [-2.9, +0.0] | 0 / 1 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +22.4 pts | [+8.1, +35.7] | 25 / 4 | 0.0001 | 0.0008 |
| mind_version | blend_exec | -1.0 pts | [-2.9, +0.0] | 0 / 1 | 1.0000 | 1.0000 |
| plain_rag | intended_pass | +18.1 pts | [+4.8, +30.5] | 22 / 3 | 0.0002 | 0.0011 |
| plain_rag | blend_exec | -1.0 pts | [-2.9, +0.0] | 0 / 1 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +6.7 pts | [+0.0, +16.2] | 7 / 0 | 0.0156 | 0.0781 |
| two_branch | blend_exec | -1.0 pts | [-2.9, +0.0] | 0 / 1 | 1.0000 | 1.0000 |

### Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

#### va_rag

**change_type**: behavior 28.6% (n=14); param_removed 100.0% (n=2); param_rename 81.1% (n=37); param_value 100.0% (n=7); symbol_rename 94.3% (n=35)

**clue_type**: code 81.8% (n=11); error 83.3% (n=6); pin 72.7% (n=11); pin-new+code-old 83.3% (n=6); pin-old+code-new 85.7% (n=7)

**condition**: clue 78.6% (n=28); contradiction 84.6% (n=13); no-clue 75.0% (n=28); stated 84.6% (n=26)

**exclusivity**: behavior 28.6% (n=14); deprecation 85.7% (n=21); one_directional 50.0% (n=4); removal 92.9% (n=56)

**gold_examples**: both 77.3% (n=44); neither 82.4% (n=51)

**gold_examples_x_change_type**: both / behavior 28.6% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 81.1% (n=37); neither / symbol_rename 85.7% (n=14)

**library**: numpy 68.8% (n=16); pandas 76.7% (n=30); pydantic 85.7% (n=49)

**target**: new 78.4% (n=51); old 81.8% (n=44)

**user_arm**: unsure 80.0% (n=95)

#### plain_rag

**change_type**: behavior 50.0% (n=14); param_removed 100.0% (n=2); param_rename 56.8% (n=37); param_value 85.7% (n=7); symbol_rename 60.0% (n=35)

**clue_type**: code 45.5% (n=11); error 66.7% (n=6); pin 72.7% (n=11); pin-new+code-old 50.0% (n=6); pin-old+code-new 57.1% (n=7)

**condition**: clue 60.7% (n=28); contradiction 53.8% (n=13); no-clue 50.0% (n=28); stated 73.1% (n=26)

**exclusivity**: behavior 50.0% (n=14); deprecation 66.7% (n=21); one_directional 50.0% (n=4); removal 60.7% (n=56)

**gold_examples**: both 61.4% (n=44); neither 58.8% (n=51)

**gold_examples_x_change_type**: both / behavior 50.0% (n=14); both / param_removed 100.0% (n=2); both / param_value 85.7% (n=7); both / symbol_rename 57.1% (n=21); neither / param_rename 56.8% (n=37); neither / symbol_rename 64.3% (n=14)

**library**: numpy 62.5% (n=16); pandas 60.0% (n=30); pydantic 59.2% (n=49)

**target**: new 54.9% (n=51); old 65.9% (n=44)

**user_arm**: unsure 60.0% (n=95)

#### mind_version

**change_type**: behavior 50.0% (n=14); param_removed 50.0% (n=2); param_rename 51.4% (n=37); param_value 85.7% (n=7); symbol_rename 62.9% (n=35)

**clue_type**: code 45.5% (n=11); error 66.7% (n=6); pin 72.7% (n=11); pin-new+code-old 50.0% (n=6); pin-old+code-new 57.1% (n=7)

**condition**: clue 60.7% (n=28); contradiction 53.8% (n=13); no-clue 50.0% (n=28); stated 65.4% (n=26)

**exclusivity**: behavior 50.0% (n=14); deprecation 61.9% (n=21); one_directional 25.0% (n=4); removal 60.7% (n=56)

**gold_examples**: both 59.1% (n=44); neither 56.9% (n=51)

**gold_examples_x_change_type**: both / behavior 50.0% (n=14); both / param_removed 50.0% (n=2); both / param_value 85.7% (n=7); both / symbol_rename 57.1% (n=21); neither / param_rename 51.4% (n=37); neither / symbol_rename 71.4% (n=14)

**library**: numpy 62.5% (n=16); pandas 56.7% (n=30); pydantic 57.1% (n=49)

**target**: new 54.9% (n=51); old 61.4% (n=44)

**user_arm**: unsure 57.9% (n=95)

#### two_branch

**change_type**: behavior 28.6% (n=14); param_removed 100.0% (n=2); param_rename 73.0% (n=37); param_value 100.0% (n=7); symbol_rename 82.9% (n=35)

**clue_type**: code 72.7% (n=11); error 83.3% (n=6); pin 72.7% (n=11); pin-new+code-old 66.7% (n=6); pin-old+code-new 71.4% (n=7)

**condition**: clue 75.0% (n=28); contradiction 69.2% (n=13); no-clue 67.9% (n=28); stated 76.9% (n=26)

**exclusivity**: behavior 28.6% (n=14); deprecation 85.7% (n=21); one_directional 50.0% (n=4); removal 80.4% (n=56)

**gold_examples**: both 68.2% (n=44); neither 76.5% (n=51)

**gold_examples_x_change_type**: both / behavior 28.6% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 81.0% (n=21); neither / param_rename 73.0% (n=37); neither / symbol_rename 85.7% (n=14)

**library**: numpy 68.8% (n=16); pandas 63.3% (n=30); pydantic 79.6% (n=49)

**target**: new 70.6% (n=51); old 75.0% (n=44)

**user_arm**: unsure 72.6% (n=95)

#### always_ask

**change_type**: behavior 50.0% (n=14); param_removed 100.0% (n=2); param_rename 56.8% (n=37); param_value 85.7% (n=7); symbol_rename 62.9% (n=35)

**clue_type**: code 45.5% (n=11); error 66.7% (n=6); pin 72.7% (n=11); pin-new+code-old 50.0% (n=6); pin-old+code-new 57.1% (n=7)

**condition**: clue 60.7% (n=28); contradiction 53.8% (n=13); no-clue 50.0% (n=28); stated 76.9% (n=26)

**exclusivity**: behavior 50.0% (n=14); deprecation 66.7% (n=21); one_directional 50.0% (n=4); removal 62.5% (n=56)

**gold_examples**: both 63.6% (n=44); neither 58.8% (n=51)

**gold_examples_x_change_type**: both / behavior 50.0% (n=14); both / param_removed 100.0% (n=2); both / param_value 85.7% (n=7); both / symbol_rename 61.9% (n=21); neither / param_rename 56.8% (n=37); neither / symbol_rename 64.3% (n=14)

**library**: numpy 68.8% (n=16); pandas 60.0% (n=30); pydantic 59.2% (n=49)

**target**: new 56.9% (n=51); old 65.9% (n=44)

**user_arm**: unsure 61.1% (n=95)

### What size of difference this run can show

95 targeted instances over 15 concepts (6.3 per concept). Measured within-concept correlation rho = 0.347 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.187 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.347 | 15.3 points | measured rho |
| 0.200 | 0.347 | 21.7 points | measured rho |
| 0.300 | 0.347 | 26.6 points | measured rho |
| 0.187 | 0.347 | 21.0 points | observed |
| 0.200 | 0.250 | 19.6 points | handoff assumption |
| 0.200 | 0.500 | 24.6 points | handoff assumption |

# test-knows

## VA-RAG run report: 20261021T094407Z-mid-922e98c7

- Model: `mid` = qwen/qwen-2.5-coder-32b-instruct
- Split: test; user arm: knows; instances: 237; concepts: 57
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T10:59:30+00:00

> 57 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen-2.5-coder-32b-instruct` pinned to provider `cloudflare` (no fallbacks, parameters required); session `cloudflare@20261021T082811Z`; 2115 paid calls, 1471 cache hits, $1.2856; providers reported {'Cloudflare': 2844}

### Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 67.1% [55.2%, 78.4%] (Wilson 56.4%, 81.4%) | 68.6% | 66.7% | 67.1% | 8.8% | 16.2% | 23.2% | 0.0% | 0.9% | 0.0% | 0.7% |
| assume_state | 46.9% [37.8%, 55.8%] (Wilson 33.9%, 61.1%) | 47.6% | 44.7% | 50.0% | 27.2% | 11.8% | 25.9% | 0.0% | 0.0% | 0.0% | 4.7% |
| mind_version | 63.2% [51.9%, 73.9%] (Wilson 50.0%, 76.2%) | 64.6% | 61.0% | 63.2% | 12.3% | 14.5% | 24.1% | 0.4% | 0.0% | 0.0% | 3.5% |
| no_retrieval | 52.2% [42.2%, 61.8%] (Wilson 38.9%, 66.1%) | 53.4% | 51.3% | 57.0% | 22.4% | 14.0% | 25.0% | 0.4% | 0.0% | 0.0% | 1.7% |
| oracle_docs | 68.4% [57.7%, 78.7%] (Wilson 57.2%, 82.0%) | 69.3% | 68.0% | 68.4% | 8.8% | 16.2% | 22.8% | 0.0% | 0.0% | 0.0% | 0.6% |
| plain_rag | 54.4% [44.6%, 63.8%] (Wilson 41.1%, 68.2%) | 55.1% | 51.3% | 56.1% | 22.4% | 12.7% | 23.2% | 0.0% | 0.0% | 0.0% | 5.6% |
| two_branch | 67.1% [55.2%, 78.4%] (Wilson 56.4%, 81.4%) | 68.6% | 66.7% | 67.1% | 8.8% | 16.2% | 23.2% | 0.0% | 0.9% | 0.0% | 0.7% |
| va_rag | 71.5% [60.9%, 81.4%] (Wilson 61.6%, 85.4%) | 73.1% | 71.1% | 71.9% | 4.8% | 18.4% | 22.8% | 0.0% | 0.9% | 0.0% | 0.6% |
| va_rag_no_ask | 54.8% [46.1%, 63.4%] (Wilson 44.3%, 71.1%) | 56.1% | 53.9% | 58.8% | 20.6% | 15.4% | 24.1% | 0.0% | 0.4% | 0.0% | 1.6% |
| va_rag_no_guard | 67.5% [56.2%, 78.4%] (Wilson 56.8%, 81.8%) | 69.1% | 67.1% | 68.0% | 8.8% | 16.2% | 22.8% | 0.0% | 0.9% | 0.0% | 0.6% |
| va_rag_no_infer | 71.5% [60.9%, 81.4%] (Wilson 61.6%, 85.4%) | 73.1% | 71.1% | 71.9% | 4.8% | 18.4% | 22.8% | 0.0% | 0.9% | 0.0% | 0.6% |
| va_rag_portable_first | 70.2% [59.3%, 80.4%] (Wilson 60.1%, 84.3%) | 71.7% | 69.7% | 70.6% | 5.3% | 19.3% | 23.7% | 0.0% | 0.9% | 0.0% | 0.6% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

### Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 34.6% | 100.0% | 100.0% | 0.0% | c=0.0: 67.1%, c=0.1: 57.1%, c=0.3: 37.1% | 1.00 calls, 0.99 answers |
| assume_state | 0.4% [0.0%, 1.4%] (Wilson 0.0%, 8.0%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 46.9%, c=0.1: 46.9%, c=0.3: 46.9% | 1.00 calls, 1.00 answers |
| mind_version | 0.4% [0.0%, 1.4%] (Wilson 0.0%, 8.2%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 43.4% | 71.9% | 58.8% | 0.0% | c=0.0: 63.2%, c=0.1: 55.3%, c=0.3: 39.5% | 1.80 calls, 1.00 answers |
| no_retrieval | 0.4% [0.0%, 1.4%] (Wilson 0.0%, 8.2%) | 0.4% [0.0%, 1.4%] (Wilson 0.0%, 8.2%) | 0.0% | 41.5% | 37.6% | 52.9% | 41.2% | 0.0% | c=0.0: 52.2%, c=0.1: 46.8%, c=0.3: 36.1% | 1.53 calls, 1.00 answers |
| oracle_docs | 0.9% [0.0%, 2.8%] (Wilson 0.1%, 8.9%) | 0.9% [0.0%, 2.8%] (Wilson 0.1%, 8.9%) | 0.0% | 2.4% | 22.2% | 13.2% | 14.7% | 0.0% | c=0.0: 68.4%, c=0.1: 67.2%, c=0.3: 64.9% | 1.11 calls, 1.00 answers |
| plain_rag | 0.9% [0.0%, 2.2%] (Wilson 0.1%, 8.7%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 29.3% | 55.8% | 12.4% | 11.8% | 0.0% | c=0.0: 54.4%, c=0.1: 52.5%, c=0.3: 48.7% | 1.18 calls, 1.00 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 95.0% | c=0.0: 67.1%, c=0.1: 57.1%, c=0.3: 37.1% | 1.97 calls, 1.97 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 68.9% | 2.5% | 100.0% | 0.0% | c=0.0: 71.5%, c=0.1: 66.4%, c=0.3: 56.2% | 1.05 calls, 0.99 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 54.8%, c=0.1: 54.8%, c=0.3: 54.8% | 1.03 calls, 1.00 answers |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 68.9% | 2.5% | 100.0% | 0.0% | c=0.0: 67.5%, c=0.1: 62.5%, c=0.3: 52.3% | 1.00 calls, 0.99 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 35.5% | 95.0% | 100.0% | 0.0% | c=0.0: 71.5%, c=0.1: 61.5%, c=0.3: 41.5% | 1.05 calls, 0.99 answers |
| va_rag_portable_first | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 68.3% | 69.1% | 0.0% | 73.5% | 0.0% | c=0.0: 70.2%, c=0.1: 66.6%, c=0.3: 59.5% | 1.40 calls, 0.99 answers |

### Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | -0.002 | n/a |
| assume_state | old 17.1%, new 41.5%, both 0.0%, neither 41.5% (n=82) | 35.4% | 0.098 | n/a |
| mind_version |  (n=0) | 27.3% | -0.005 | n/a |
| no_retrieval | old 25.7%, new 0.0%, both 0.0%, neither 74.3% (n=35) | 17.6% | -0.029 | n/a |
| oracle_docs | old 18.4%, new 27.6%, both 1.3%, neither 52.6% (n=76) | 42.9% | -0.007 | n/a |
| plain_rag | old 19.0%, new 34.5%, both 0.0%, neither 46.6% (n=58) | 37.3% | 0.130 | n/a |
| two_branch | old 19.8%, new 29.6%, both 0.0%, neither 50.6% (n=81) | 45.7% | -0.002 | 55.3% |
| va_rag |  (n=0) | 48.1% | 0.012 | n/a |
| va_rag_no_ask | old 14.6%, new 39.0%, both 0.0%, neither 46.3% (n=82) | 48.1% | 0.104 | n/a |
| va_rag_no_guard |  (n=0) | 45.7% | -0.009 | n/a |
| va_rag_no_infer |  (n=0) | n/a | 0.012 | n/a |
| va_rag_portable_first | old 0.0%, new 0.0%, both 0.0%, neither 100.0% (n=26) | 48.1% | 0.017 | n/a |

### Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision, exclusive-error oracle | guard recall, exclusive-error oracle | guard precision, strict-named oracle | guard recall, strict-named oracle | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"asked": 119, "inferred": 112, "no_conflict": 6} | n/a | 13 | 23.1% | 75.0% | 100.0% | 100.0% | 69.2% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"inferred": 112, "no_conflict": 6, "unresolved": 119} | n/a | 7 | 28.6% | 11.8% | 100.0% | 14.3% | 57.1% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"asked": 119, "inferred": 112, "no_conflict": 6} | n/a | 0 | n/a | 0.0% | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 237} | {"asked": 231, "no_conflict": 6} | n/a | 13 | 23.1% | 75.0% | 100.0% | 100.0% | 69.2% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"asked": 81, "inferred": 112, "no_conflict": 6, "portable": 38} | n/a | 13 | 23.1% | 75.0% | 100.0% | 100.0% | 69.2% | 0.0% |

Guard oracles (`varag.eval.oracle`): exclusive-error (M7) counts a failure whose AttributeError, ImportError or TypeError names an exclusive symbol; strict-named (2026-10-21 correction) counts a strict failure in the committed version whose error, traceback, counted warning or failing line shows the usage, so rejected values and deprecation warnings count too.

Portable-first drafts (`va_rag_portable_first`): 119 drafts, 38 returned without a question (31.9%); rejected: {"does not parse": 3, "exclusive or deprecated usage": 78}.

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
| always_ask | intended_pass | +4.9 pts | [+0.4, +10.8] | 11 / 1 | 0.0063 | 0.0381 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +11.2 pts | [+4.2, +19.5] | 28 / 9 | 0.0026 | 0.0179 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| plain_rag | intended_pass | +20.3 pts | [+12.1, +29.2] | 49 / 10 | 0.0000 | 0.0000 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +4.9 pts | [+0.4, +10.8] | 11 / 1 | 0.0063 | 0.0381 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

### Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

#### va_rag

**change_type**: behavior 50.0% (n=36); moved_import 20.0% (n=5); param_removed 100.0% (n=2); param_rename 77.4% (n=62); param_value 56.7% (n=30); symbol_removed 85.7% (n=14); symbol_rename 82.3% (n=79)

**clue_type**: code 69.0% (n=29); error 78.3% (n=23); pin 66.7% (n=30); pin-new+code-old 59.1% (n=22); pin-old+code-new 91.7% (n=12)

**condition**: clue 70.7% (n=82); contradiction 70.6% (n=34); no-clue 73.2% (n=82); stated 70.0% (n=30)

**exclusivity**: behavior 50.0% (n=36); deprecation 86.8% (n=68); one_directional 92.9% (n=28); removal 62.5% (n=96)

**gold_examples**: both 70.6% (n=51); neither 71.8% (n=177)

**gold_examples_x_change_type**: both / behavior 52.4% (n=21); both / symbol_removed 100.0% (n=6); both / symbol_rename 79.2% (n=24); neither / behavior 46.7% (n=15); neither / moved_import 20.0% (n=5); neither / param_removed 100.0% (n=2); neither / param_rename 77.4% (n=62); neither / param_value 56.7% (n=30); neither / symbol_removed 75.0% (n=8); neither / symbol_rename 83.6% (n=55)

**library**: numpy 65.7% (n=35); pandas 66.1% (n=62); pydantic 75.6% (n=131)

**target**: new 71.8% (n=124); old 71.2% (n=104)

**user_arm**: knows 71.5% (n=228)

#### plain_rag

**change_type**: behavior 47.2% (n=36); moved_import 0.0% (n=5); param_removed 0.0% (n=2); param_rename 51.6% (n=62); param_value 36.7% (n=30); symbol_removed 57.1% (n=14); symbol_rename 70.9% (n=79)

**clue_type**: code 41.4% (n=29); error 56.5% (n=23); pin 70.0% (n=30); pin-new+code-old 45.5% (n=22); pin-old+code-new 50.0% (n=12)

**condition**: clue 56.1% (n=82); contradiction 47.1% (n=34); no-clue 50.0% (n=82); stated 70.0% (n=30)

**exclusivity**: behavior 47.2% (n=36); deprecation 72.1% (n=68); one_directional 60.7% (n=28); removal 42.7% (n=96)

**gold_examples**: both 60.8% (n=51); neither 52.5% (n=177)

**gold_examples_x_change_type**: both / behavior 52.4% (n=21); both / symbol_removed 66.7% (n=6); both / symbol_rename 66.7% (n=24); neither / behavior 40.0% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 0.0% (n=2); neither / param_rename 51.6% (n=62); neither / param_value 36.7% (n=30); neither / symbol_removed 50.0% (n=8); neither / symbol_rename 72.7% (n=55)

**library**: numpy 51.4% (n=35); pandas 50.0% (n=62); pydantic 57.3% (n=131)

**target**: new 55.6% (n=124); old 52.9% (n=104)

**user_arm**: knows 54.4% (n=228)

#### mind_version

**change_type**: behavior 47.2% (n=36); moved_import 20.0% (n=5); param_removed 0.0% (n=2); param_rename 66.1% (n=62); param_value 36.7% (n=30); symbol_removed 71.4% (n=14); symbol_rename 81.0% (n=79)

**clue_type**: code 58.6% (n=29); error 56.5% (n=23); pin 70.0% (n=30); pin-new+code-old 45.5% (n=22); pin-old+code-new 66.7% (n=12)

**condition**: clue 62.2% (n=82); contradiction 52.9% (n=34); no-clue 67.1% (n=82); stated 66.7% (n=30)

**exclusivity**: behavior 47.2% (n=36); deprecation 85.3% (n=68); one_directional 71.4% (n=28); removal 51.0% (n=96)

**gold_examples**: both 64.7% (n=51); neither 62.7% (n=177)

**gold_examples_x_change_type**: both / behavior 52.4% (n=21); both / symbol_removed 66.7% (n=6); both / symbol_rename 75.0% (n=24); neither / behavior 40.0% (n=15); neither / moved_import 20.0% (n=5); neither / param_removed 0.0% (n=2); neither / param_rename 66.1% (n=62); neither / param_value 36.7% (n=30); neither / symbol_removed 75.0% (n=8); neither / symbol_rename 83.6% (n=55)

**library**: numpy 60.0% (n=35); pandas 50.0% (n=62); pydantic 70.2% (n=131)

**target**: new 61.3% (n=124); old 65.4% (n=104)

**user_arm**: knows 63.2% (n=228)

#### two_branch

**change_type**: behavior 47.2% (n=36); moved_import 20.0% (n=5); param_removed 100.0% (n=2); param_rename 75.8% (n=62); param_value 26.7% (n=30); symbol_removed 85.7% (n=14); symbol_rename 83.5% (n=79)

**clue_type**: code 62.1% (n=29); error 69.6% (n=23); pin 66.7% (n=30); pin-new+code-old 59.1% (n=22); pin-old+code-new 75.0% (n=12)

**condition**: clue 65.9% (n=82); contradiction 64.7% (n=34); no-clue 69.5% (n=82); stated 66.7% (n=30)

**exclusivity**: behavior 47.2% (n=36); deprecation 88.2% (n=68); one_directional 85.7% (n=28); removal 54.2% (n=96)

**gold_examples**: both 70.6% (n=51); neither 66.1% (n=177)

**gold_examples_x_change_type**: both / behavior 52.4% (n=21); both / symbol_removed 100.0% (n=6); both / symbol_rename 79.2% (n=24); neither / behavior 40.0% (n=15); neither / moved_import 20.0% (n=5); neither / param_removed 100.0% (n=2); neither / param_rename 75.8% (n=62); neither / param_value 26.7% (n=30); neither / symbol_removed 75.0% (n=8); neither / symbol_rename 85.5% (n=55)

**library**: numpy 65.7% (n=35); pandas 50.0% (n=62); pydantic 75.6% (n=131)

**target**: new 64.5% (n=124); old 70.2% (n=104)

**user_arm**: knows 67.1% (n=228)

#### always_ask

**change_type**: behavior 47.2% (n=36); moved_import 20.0% (n=5); param_removed 100.0% (n=2); param_rename 75.8% (n=62); param_value 26.7% (n=30); symbol_removed 85.7% (n=14); symbol_rename 83.5% (n=79)

**clue_type**: code 62.1% (n=29); error 69.6% (n=23); pin 66.7% (n=30); pin-new+code-old 59.1% (n=22); pin-old+code-new 75.0% (n=12)

**condition**: clue 65.9% (n=82); contradiction 64.7% (n=34); no-clue 69.5% (n=82); stated 66.7% (n=30)

**exclusivity**: behavior 47.2% (n=36); deprecation 88.2% (n=68); one_directional 85.7% (n=28); removal 54.2% (n=96)

**gold_examples**: both 70.6% (n=51); neither 66.1% (n=177)

**gold_examples_x_change_type**: both / behavior 52.4% (n=21); both / symbol_removed 100.0% (n=6); both / symbol_rename 79.2% (n=24); neither / behavior 40.0% (n=15); neither / moved_import 20.0% (n=5); neither / param_removed 100.0% (n=2); neither / param_rename 75.8% (n=62); neither / param_value 26.7% (n=30); neither / symbol_removed 75.0% (n=8); neither / symbol_rename 85.5% (n=55)

**library**: numpy 65.7% (n=35); pandas 50.0% (n=62); pydantic 75.6% (n=131)

**target**: new 64.5% (n=124); old 70.2% (n=104)

**user_arm**: knows 67.1% (n=228)

### What size of difference this run can show

228 targeted instances over 48 concepts (4.8 per concept). Measured within-concept correlation rho = 0.411 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.139 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.411 | 9.4 points | measured rho |
| 0.200 | 0.411 | 13.2 points | measured rho |
| 0.300 | 0.411 | 16.2 points | measured rho |
| 0.139 | 0.411 | 11.0 points | observed |
| 0.200 | 0.250 | 11.5 points | handoff assumption |
| 0.200 | 0.500 | 14.1 points | handoff assumption |

# test-unsure

## VA-RAG run report: 20261021T110003Z-mid-a2ded36e

- Model: `mid` = qwen/qwen-2.5-coder-32b-instruct
- Split: test; user arm: unsure; instances: 237; concepts: 57
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T11:22:30+00:00

> 57 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen-2.5-coder-32b-instruct` pinned to provider `cloudflare` (no fallbacks, parameters required); session `cloudflare@20261021T082811Z`; 441 paid calls, 3709 cache hits, $0.3191; providers reported {'Cloudflare': 2844}

### Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 47.8% [39.2%, 56.2%] (Wilson 35.8%, 63.0%) | 48.7% | 45.2% | 52.6% | 29.8% | 13.2% | 22.4% | 0.0% | 0.0% | 0.0% | 5.5% |
| assume_state | 46.9% [37.8%, 55.8%] (Wilson 33.9%, 61.1%) | 47.6% | 44.7% | 50.0% | 27.2% | 11.8% | 25.9% | 0.0% | 0.0% | 0.0% | 4.7% |
| mind_version | 46.9% [37.7%, 56.1%] (Wilson 33.8%, 61.0%) | 48.0% | 44.7% | 51.8% | 28.5% | 16.2% | 23.7% | 0.9% | 0.0% | 0.0% | 4.7% |
| no_retrieval | 47.4% [38.6%, 55.8%] (Wilson 34.5%, 61.7%) | 48.2% | 46.5% | 54.8% | 27.2% | 13.2% | 25.4% | 0.0% | 0.0% | 0.0% | 1.9% |
| oracle_docs | 68.4% [57.7%, 78.6%] (Wilson 57.3%, 82.1%) | 69.3% | 68.0% | 68.9% | 9.2% | 16.2% | 22.4% | 0.0% | 0.0% | 0.0% | 0.6% |
| plain_rag | 50.0% [40.6%, 59.2%] (Wilson 37.5%, 64.7%) | 51.1% | 47.4% | 54.4% | 27.2% | 15.8% | 22.4% | 0.4% | 0.0% | 0.0% | 5.3% |
| two_branch | 67.1% [55.2%, 78.4%] (Wilson 56.4%, 81.4%) | 68.6% | 66.7% | 67.1% | 8.8% | 16.2% | 23.2% | 0.0% | 0.9% | 0.0% | 0.7% |
| va_rag | 71.5% [60.9%, 81.4%] (Wilson 61.6%, 85.4%) | 73.1% | 71.1% | 71.9% | 4.8% | 18.4% | 22.8% | 0.4% | 0.4% | 0.0% | 0.6% |
| va_rag_no_ask | 54.8% [46.1%, 63.4%] (Wilson 44.3%, 71.1%) | 56.1% | 53.9% | 58.8% | 20.6% | 15.4% | 24.1% | 0.0% | 0.4% | 0.0% | 1.6% |
| va_rag_no_guard | 67.5% [56.2%, 78.4%] (Wilson 56.8%, 81.8%) | 69.1% | 67.1% | 68.0% | 8.8% | 16.2% | 22.8% | 0.4% | 0.4% | 0.0% | 0.6% |
| va_rag_no_infer | 71.5% [60.9%, 81.4%] (Wilson 61.6%, 85.4%) | 73.1% | 71.1% | 71.9% | 4.8% | 18.4% | 22.8% | 0.9% | 0.0% | 0.0% | 0.6% |
| va_rag_portable_first | 70.2% [59.3%, 80.4%] (Wilson 60.1%, 84.3%) | 71.7% | 69.7% | 70.6% | 5.3% | 19.3% | 23.7% | 0.4% | 0.4% | 0.0% | 0.6% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

### Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.4% [0.0%, 1.4%] (Wilson 0.0%, 8.0%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 34.6% | 100.0% | 100.0% | 0.0% | c=0.0: 47.8%, c=0.1: 37.8%, c=0.3: 17.8% | 1.00 calls, 1.00 answers |
| assume_state | 0.4% [0.0%, 1.4%] (Wilson 0.0%, 8.0%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 46.9%, c=0.1: 46.9%, c=0.3: 46.9% | 1.00 calls, 1.00 answers |
| mind_version | 0.9% [0.0%, 2.2%] (Wilson 0.0%, 8.5%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 43.4% | 71.9% | 58.8% | 0.0% | c=0.0: 46.9%, c=0.1: 39.0%, c=0.3: 23.2% | 1.80 calls, 1.00 answers |
| no_retrieval | 0.4% [0.0%, 1.4%] (Wilson 0.0%, 8.2%) | 0.4% [0.0%, 1.4%] (Wilson 0.0%, 8.2%) | 0.0% | 41.5% | 37.6% | 52.9% | 41.2% | 0.0% | c=0.0: 47.4%, c=0.1: 42.0%, c=0.3: 31.3% | 1.53 calls, 1.00 answers |
| oracle_docs | 0.9% [0.0%, 2.8%] (Wilson 0.1%, 8.9%) | 0.9% [0.0%, 2.8%] (Wilson 0.1%, 8.9%) | 0.0% | 2.4% | 22.2% | 13.2% | 14.7% | 0.0% | c=0.0: 68.4%, c=0.1: 67.2%, c=0.3: 64.9% | 1.11 calls, 1.00 answers |
| plain_rag | 0.4% [0.0%, 1.4%] (Wilson 0.0%, 8.0%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 29.3% | 55.8% | 12.4% | 11.8% | 0.0% | c=0.0: 50.0%, c=0.1: 48.1%, c=0.3: 44.3% | 1.18 calls, 1.00 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 95.0% | c=0.0: 67.1%, c=0.1: 57.1%, c=0.3: 37.1% | 1.97 calls, 1.97 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 68.9% | 2.5% | 100.0% | 2.5% | c=0.0: 71.5%, c=0.1: 66.4%, c=0.3: 56.2% | 1.57 calls, 1.50 answers |
| va_rag_no_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 54.8%, c=0.1: 54.8%, c=0.3: 54.8% | 1.03 calls, 1.00 answers |
| va_rag_no_guard | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 68.9% | 2.5% | 100.0% | 2.5% | c=0.0: 67.5%, c=0.1: 62.5%, c=0.3: 52.3% | 1.50 calls, 1.50 answers |
| va_rag_no_infer | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 35.5% | 95.0% | 100.0% | 95.0% | c=0.0: 71.5%, c=0.1: 61.5%, c=0.3: 41.5% | 2.06 calls, 1.97 answers |
| va_rag_portable_first | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 68.3% | 69.1% | 0.0% | 73.5% | 0.0% | c=0.0: 70.2%, c=0.1: 66.6%, c=0.3: 59.5% | 1.75 calls, 1.34 answers |

### Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | 0.137 | n/a |
| assume_state | old 17.1%, new 41.5%, both 0.0%, neither 41.5% (n=82) | 35.4% | 0.098 | n/a |
| mind_version |  (n=0) | 27.3% | 0.080 | n/a |
| no_retrieval | old 25.7%, new 0.0%, both 0.0%, neither 74.3% (n=35) | 17.6% | 0.019 | n/a |
| oracle_docs | old 18.4%, new 27.6%, both 1.3%, neither 52.6% (n=76) | 42.9% | -0.007 | n/a |
| plain_rag | old 19.0%, new 34.5%, both 0.0%, neither 46.6% (n=58) | 37.3% | 0.135 | n/a |
| two_branch | old 19.8%, new 29.6%, both 0.0%, neither 50.6% (n=81) | 45.7% | -0.002 | 55.3% |
| va_rag |  (n=0) | 48.1% | 0.012 | 56.9% |
| va_rag_no_ask | old 14.6%, new 39.0%, both 0.0%, neither 46.3% (n=82) | 48.1% | 0.104 | n/a |
| va_rag_no_guard |  (n=0) | 45.7% | -0.009 | 52.6% |
| va_rag_no_infer |  (n=0) | n/a | 0.012 | 58.8% |
| va_rag_portable_first | old 0.0%, new 0.0%, both 0.0%, neither 100.0% (n=26) | 48.1% | 0.017 | 63.0% |

### Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision, exclusive-error oracle | guard recall, exclusive-error oracle | guard precision, strict-named oracle | guard recall, strict-named oracle | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"both": 119, "inferred": 112, "no_conflict": 6} | n/a | 13 | 23.1% | 75.0% | 100.0% | 100.0% | 69.2% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"inferred": 112, "no_conflict": 6, "unresolved": 119} | n/a | 7 | 28.6% | 11.8% | 100.0% | 14.3% | 57.1% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"both": 119, "inferred": 112, "no_conflict": 6} | n/a | 0 | n/a | 0.0% | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 237} | {"both": 231, "no_conflict": 6} | n/a | 13 | 23.1% | 75.0% | 100.0% | 100.0% | 69.2% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"both": 81, "inferred": 112, "no_conflict": 6, "portable": 38} | n/a | 13 | 23.1% | 75.0% | 100.0% | 100.0% | 69.2% | 0.0% |

Guard oracles (`varag.eval.oracle`): exclusive-error (M7) counts a failure whose AttributeError, ImportError or TypeError names an exclusive symbol; strict-named (2026-10-21 correction) counts a strict failure in the committed version whose error, traceback, counted warning or failing line shows the usage, so rejected values and deprecation warnings count too.

Portable-first drafts (`va_rag_portable_first`): 119 drafts, 38 returned without a question (31.9%); rejected: {"does not parse": 3, "exclusive or deprecated usage": 78}.

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
| always_ask | intended_pass | +26.0 pts | [+17.5, +34.6] | 63 / 9 | 0.0000 | 0.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +28.2 pts | [+19.0, +37.4] | 65 / 9 | 0.0000 | 0.0000 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| plain_rag | intended_pass | +24.1 pts | [+15.6, +32.9] | 57 / 8 | 0.0000 | 0.0000 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +4.9 pts | [+0.4, +10.8] | 11 / 1 | 0.0063 | 0.0317 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

### Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

#### va_rag

**change_type**: behavior 50.0% (n=36); moved_import 20.0% (n=5); param_removed 100.0% (n=2); param_rename 77.4% (n=62); param_value 56.7% (n=30); symbol_removed 85.7% (n=14); symbol_rename 82.3% (n=79)

**clue_type**: code 69.0% (n=29); error 78.3% (n=23); pin 66.7% (n=30); pin-new+code-old 59.1% (n=22); pin-old+code-new 91.7% (n=12)

**condition**: clue 70.7% (n=82); contradiction 70.6% (n=34); no-clue 73.2% (n=82); stated 70.0% (n=30)

**exclusivity**: behavior 50.0% (n=36); deprecation 86.8% (n=68); one_directional 92.9% (n=28); removal 62.5% (n=96)

**gold_examples**: both 70.6% (n=51); neither 71.8% (n=177)

**gold_examples_x_change_type**: both / behavior 52.4% (n=21); both / symbol_removed 100.0% (n=6); both / symbol_rename 79.2% (n=24); neither / behavior 46.7% (n=15); neither / moved_import 20.0% (n=5); neither / param_removed 100.0% (n=2); neither / param_rename 77.4% (n=62); neither / param_value 56.7% (n=30); neither / symbol_removed 75.0% (n=8); neither / symbol_rename 83.6% (n=55)

**library**: numpy 65.7% (n=35); pandas 66.1% (n=62); pydantic 75.6% (n=131)

**target**: new 71.8% (n=124); old 71.2% (n=104)

**user_arm**: unsure 71.5% (n=228)

#### plain_rag

**change_type**: behavior 47.2% (n=36); moved_import 0.0% (n=5); param_removed 0.0% (n=2); param_rename 43.5% (n=62); param_value 36.7% (n=30); symbol_removed 57.1% (n=14); symbol_rename 64.6% (n=79)

**clue_type**: code 41.4% (n=29); error 43.5% (n=23); pin 70.0% (n=30); pin-new+code-old 45.5% (n=22); pin-old+code-new 41.7% (n=12)

**condition**: clue 52.4% (n=82); contradiction 44.1% (n=34); no-clue 42.7% (n=82); stated 70.0% (n=30)

**exclusivity**: behavior 47.2% (n=36); deprecation 64.7% (n=68); one_directional 60.7% (n=28); removal 37.5% (n=96)

**gold_examples**: both 60.8% (n=51); neither 46.9% (n=177)

**gold_examples_x_change_type**: both / behavior 52.4% (n=21); both / symbol_removed 66.7% (n=6); both / symbol_rename 66.7% (n=24); neither / behavior 40.0% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 0.0% (n=2); neither / param_rename 43.5% (n=62); neither / param_value 36.7% (n=30); neither / symbol_removed 50.0% (n=8); neither / symbol_rename 63.6% (n=55)

**library**: numpy 48.6% (n=35); pandas 50.0% (n=62); pydantic 50.4% (n=131)

**target**: new 51.6% (n=124); old 48.1% (n=104)

**user_arm**: unsure 50.0% (n=228)

#### mind_version

**change_type**: behavior 47.2% (n=36); moved_import 0.0% (n=5); param_removed 0.0% (n=2); param_rename 35.5% (n=62); param_value 43.3% (n=30); symbol_removed 57.1% (n=14); symbol_rename 59.5% (n=79)

**clue_type**: code 44.8% (n=29); error 34.8% (n=23); pin 66.7% (n=30); pin-new+code-old 45.5% (n=22); pin-old+code-new 33.3% (n=12)

**condition**: clue 50.0% (n=82); contradiction 41.2% (n=34); no-clue 37.8% (n=82); stated 70.0% (n=30)

**exclusivity**: behavior 47.2% (n=36); deprecation 58.8% (n=68); one_directional 53.6% (n=28); removal 36.5% (n=96)

**gold_examples**: both 56.9% (n=51); neither 44.1% (n=177)

**gold_examples_x_change_type**: both / behavior 52.4% (n=21); both / symbol_removed 66.7% (n=6); both / symbol_rename 58.3% (n=24); neither / behavior 40.0% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 0.0% (n=2); neither / param_rename 35.5% (n=62); neither / param_value 43.3% (n=30); neither / symbol_removed 50.0% (n=8); neither / symbol_rename 60.0% (n=55)

**library**: numpy 48.6% (n=35); pandas 46.8% (n=62); pydantic 46.6% (n=131)

**target**: new 49.2% (n=124); old 44.2% (n=104)

**user_arm**: unsure 46.9% (n=228)

#### two_branch

**change_type**: behavior 47.2% (n=36); moved_import 20.0% (n=5); param_removed 100.0% (n=2); param_rename 75.8% (n=62); param_value 26.7% (n=30); symbol_removed 85.7% (n=14); symbol_rename 83.5% (n=79)

**clue_type**: code 62.1% (n=29); error 69.6% (n=23); pin 66.7% (n=30); pin-new+code-old 59.1% (n=22); pin-old+code-new 75.0% (n=12)

**condition**: clue 65.9% (n=82); contradiction 64.7% (n=34); no-clue 69.5% (n=82); stated 66.7% (n=30)

**exclusivity**: behavior 47.2% (n=36); deprecation 88.2% (n=68); one_directional 85.7% (n=28); removal 54.2% (n=96)

**gold_examples**: both 70.6% (n=51); neither 66.1% (n=177)

**gold_examples_x_change_type**: both / behavior 52.4% (n=21); both / symbol_removed 100.0% (n=6); both / symbol_rename 79.2% (n=24); neither / behavior 40.0% (n=15); neither / moved_import 20.0% (n=5); neither / param_removed 100.0% (n=2); neither / param_rename 75.8% (n=62); neither / param_value 26.7% (n=30); neither / symbol_removed 75.0% (n=8); neither / symbol_rename 85.5% (n=55)

**library**: numpy 65.7% (n=35); pandas 50.0% (n=62); pydantic 75.6% (n=131)

**target**: new 64.5% (n=124); old 70.2% (n=104)

**user_arm**: unsure 67.1% (n=228)

#### always_ask

**change_type**: behavior 47.2% (n=36); moved_import 0.0% (n=5); param_removed 0.0% (n=2); param_rename 43.5% (n=62); param_value 40.0% (n=30); symbol_removed 57.1% (n=14); symbol_rename 57.0% (n=79)

**clue_type**: code 37.9% (n=29); error 39.1% (n=23); pin 66.7% (n=30); pin-new+code-old 45.5% (n=22); pin-old+code-new 33.3% (n=12)

**condition**: clue 48.8% (n=82); contradiction 41.2% (n=34); no-clue 39.0% (n=82); stated 76.7% (n=30)

**exclusivity**: behavior 47.2% (n=36); deprecation 55.9% (n=68); one_directional 60.7% (n=28); removal 38.5% (n=96)

**gold_examples**: both 56.9% (n=51); neither 45.2% (n=177)

**gold_examples_x_change_type**: both / behavior 52.4% (n=21); both / symbol_removed 66.7% (n=6); both / symbol_rename 58.3% (n=24); neither / behavior 40.0% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 0.0% (n=2); neither / param_rename 43.5% (n=62); neither / param_value 40.0% (n=30); neither / symbol_removed 50.0% (n=8); neither / symbol_rename 56.4% (n=55)

**library**: numpy 48.6% (n=35); pandas 50.0% (n=62); pydantic 46.6% (n=131)

**target**: new 51.6% (n=124); old 43.3% (n=104)

**user_arm**: unsure 47.8% (n=228)

### What size of difference this run can show

228 targeted instances over 48 concepts (4.8 per concept). Measured within-concept correlation rho = 0.350 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.183 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.350 | 8.9 points | measured rho |
| 0.200 | 0.350 | 12.6 points | measured rho |
| 0.300 | 0.350 | 15.4 points | measured rho |
| 0.183 | 0.350 | 12.1 points | observed |
| 0.200 | 0.250 | 11.5 points | handoff assumption |
| 0.200 | 0.500 | 14.1 points | handoff assumption |
