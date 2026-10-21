# VA-RAG run report: 20261021T093318Z-mid-7a546ea0

- Model: `mid` = qwen/qwen-2.5-coder-32b-instruct
- Split: dev; user arm: unsure; instances: 101; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T09:43:40+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen-2.5-coder-32b-instruct` pinned to provider `cloudflare` (no fallbacks, parameters required); session `cloudflare@20261021T082811Z`; 202 paid calls, 1552 cache hits, $0.1439; providers reported {'Cloudflare': 1212}

## Primary metrics

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

## Blending, asking, hedging, cost

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

## Commit direction, clue following, order

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

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision, exclusive-error oracle | guard recall, exclusive-error oracle | guard precision, strict-named oracle | guard recall, strict-named oracle | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | {"no_conflict": 4, "both": 43, "inferred": 54} | n/a | 10 | 50.0% | 100.0% | 80.0% | 100.0% | 60.0% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | {"no_conflict": 4, "unresolved": 43, "inferred": 54} | n/a | 6 | 50.0% | 37.5% | 83.3% | 33.3% | 50.0% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | {"no_conflict": 4, "both": 43, "inferred": 54} | n/a | 0 | n/a | 0.0% | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 101} | {"no_conflict": 4, "both": 97} | n/a | 10 | 50.0% | 100.0% | 80.0% | 100.0% | 60.0% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | {"no_conflict": 4, "both": 28, "inferred": 54, "portable": 15} | n/a | 10 | 50.0% | 100.0% | 80.0% | 100.0% | 60.0% | 0.0% |

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

## Primary contrasts: va_rag against each baseline

Paired bootstrap on per-concept differences of instance scores (va_rag minus baseline); exact McNemar on the repeat-0 instance pairs, Holm-adjusted across the contrasts.

| Baseline | Metric | Difference | 95% bootstrap | discordant (va_rag only / baseline only) | McNemar p | Holm p |
| --- | --- | --- | --- | --- | --- | --- |
| plain_rag | intended_pass | +18.1 pts | [+4.8, +30.5] | 22 / 3 | 0.0002 | 0.0011 |
| plain_rag | blend_exec | -1.0 pts | [-2.9, +0.0] | 0 / 1 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +22.4 pts | [+8.1, +35.7] | 25 / 4 | 0.0001 | 0.0008 |
| mind_version | blend_exec | -1.0 pts | [-2.9, +0.0] | 0 / 1 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +6.7 pts | [+0.0, +16.2] | 7 / 0 | 0.0156 | 0.0781 |
| two_branch | blend_exec | -1.0 pts | [-2.9, +0.0] | 0 / 1 | 1.0000 | 1.0000 |
| always_ask | intended_pass | +17.1 pts | [+4.8, +28.6] | 21 / 3 | 0.0003 | 0.0017 |
| always_ask | blend_exec | -1.0 pts | [-2.9, +0.0] | 0 / 1 | 1.0000 | 1.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 68.8% (n=16); pandas 76.7% (n=30); pydantic 85.7% (n=49)

**target**: new 78.4% (n=51); old 81.8% (n=44)

**condition**: clue 78.6% (n=28); contradiction 84.6% (n=13); no-clue 75.0% (n=28); stated 84.6% (n=26)

**clue_type**: code 81.8% (n=11); error 83.3% (n=6); pin 72.7% (n=11); pin-new+code-old 83.3% (n=6); pin-old+code-new 85.7% (n=7)

**exclusivity**: behavior 28.6% (n=14); deprecation 85.7% (n=21); one_directional 50.0% (n=4); removal 92.9% (n=56)

**change_type**: behavior 28.6% (n=14); param_removed 100.0% (n=2); param_rename 81.1% (n=37); param_value 100.0% (n=7); symbol_rename 94.3% (n=35)

**user_arm**: unsure 80.0% (n=95)

**gold_examples**: both 77.3% (n=44); neither 82.4% (n=51)

**gold_examples_x_change_type**: both / behavior 28.6% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 81.1% (n=37); neither / symbol_rename 85.7% (n=14)

### plain_rag

**library**: numpy 62.5% (n=16); pandas 60.0% (n=30); pydantic 59.2% (n=49)

**target**: new 54.9% (n=51); old 65.9% (n=44)

**condition**: clue 60.7% (n=28); contradiction 53.8% (n=13); no-clue 50.0% (n=28); stated 73.1% (n=26)

**clue_type**: code 45.5% (n=11); error 66.7% (n=6); pin 72.7% (n=11); pin-new+code-old 50.0% (n=6); pin-old+code-new 57.1% (n=7)

**exclusivity**: behavior 50.0% (n=14); deprecation 66.7% (n=21); one_directional 50.0% (n=4); removal 60.7% (n=56)

**change_type**: behavior 50.0% (n=14); param_removed 100.0% (n=2); param_rename 56.8% (n=37); param_value 85.7% (n=7); symbol_rename 60.0% (n=35)

**user_arm**: unsure 60.0% (n=95)

**gold_examples**: both 61.4% (n=44); neither 58.8% (n=51)

**gold_examples_x_change_type**: both / behavior 50.0% (n=14); both / param_removed 100.0% (n=2); both / param_value 85.7% (n=7); both / symbol_rename 57.1% (n=21); neither / param_rename 56.8% (n=37); neither / symbol_rename 64.3% (n=14)

### mind_version

**library**: numpy 62.5% (n=16); pandas 56.7% (n=30); pydantic 57.1% (n=49)

**target**: new 54.9% (n=51); old 61.4% (n=44)

**condition**: clue 60.7% (n=28); contradiction 53.8% (n=13); no-clue 50.0% (n=28); stated 65.4% (n=26)

**clue_type**: code 45.5% (n=11); error 66.7% (n=6); pin 72.7% (n=11); pin-new+code-old 50.0% (n=6); pin-old+code-new 57.1% (n=7)

**exclusivity**: behavior 50.0% (n=14); deprecation 61.9% (n=21); one_directional 25.0% (n=4); removal 60.7% (n=56)

**change_type**: behavior 50.0% (n=14); param_removed 50.0% (n=2); param_rename 51.4% (n=37); param_value 85.7% (n=7); symbol_rename 62.9% (n=35)

**user_arm**: unsure 57.9% (n=95)

**gold_examples**: both 59.1% (n=44); neither 56.9% (n=51)

**gold_examples_x_change_type**: both / behavior 50.0% (n=14); both / param_removed 50.0% (n=2); both / param_value 85.7% (n=7); both / symbol_rename 57.1% (n=21); neither / param_rename 51.4% (n=37); neither / symbol_rename 71.4% (n=14)

### two_branch

**library**: numpy 68.8% (n=16); pandas 63.3% (n=30); pydantic 79.6% (n=49)

**target**: new 70.6% (n=51); old 75.0% (n=44)

**condition**: clue 75.0% (n=28); contradiction 69.2% (n=13); no-clue 67.9% (n=28); stated 76.9% (n=26)

**clue_type**: code 72.7% (n=11); error 83.3% (n=6); pin 72.7% (n=11); pin-new+code-old 66.7% (n=6); pin-old+code-new 71.4% (n=7)

**exclusivity**: behavior 28.6% (n=14); deprecation 85.7% (n=21); one_directional 50.0% (n=4); removal 80.4% (n=56)

**change_type**: behavior 28.6% (n=14); param_removed 100.0% (n=2); param_rename 73.0% (n=37); param_value 100.0% (n=7); symbol_rename 82.9% (n=35)

**user_arm**: unsure 72.6% (n=95)

**gold_examples**: both 68.2% (n=44); neither 76.5% (n=51)

**gold_examples_x_change_type**: both / behavior 28.6% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 81.0% (n=21); neither / param_rename 73.0% (n=37); neither / symbol_rename 85.7% (n=14)

### always_ask

**library**: numpy 68.8% (n=16); pandas 60.0% (n=30); pydantic 59.2% (n=49)

**target**: new 56.9% (n=51); old 65.9% (n=44)

**condition**: clue 60.7% (n=28); contradiction 53.8% (n=13); no-clue 50.0% (n=28); stated 76.9% (n=26)

**clue_type**: code 45.5% (n=11); error 66.7% (n=6); pin 72.7% (n=11); pin-new+code-old 50.0% (n=6); pin-old+code-new 57.1% (n=7)

**exclusivity**: behavior 50.0% (n=14); deprecation 66.7% (n=21); one_directional 50.0% (n=4); removal 62.5% (n=56)

**change_type**: behavior 50.0% (n=14); param_removed 100.0% (n=2); param_rename 56.8% (n=37); param_value 85.7% (n=7); symbol_rename 62.9% (n=35)

**user_arm**: unsure 61.1% (n=95)

**gold_examples**: both 63.6% (n=44); neither 58.8% (n=51)

**gold_examples_x_change_type**: both / behavior 50.0% (n=14); both / param_removed 100.0% (n=2); both / param_value 85.7% (n=7); both / symbol_rename 61.9% (n=21); neither / param_rename 56.8% (n=37); neither / symbol_rename 64.3% (n=14)

## What size of difference this run can show

95 targeted instances over 15 concepts (6.3 per concept). Measured within-concept correlation rho = 0.347 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.187 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.347 | 15.3 points | measured rho |
| 0.200 | 0.347 | 21.7 points | measured rho |
| 0.300 | 0.347 | 26.6 points | measured rho |
| 0.187 | 0.347 | 21.0 points | observed |
| 0.200 | 0.250 | 19.6 points | handoff assumption |
| 0.200 | 0.500 | 24.6 points | handoff assumption |
