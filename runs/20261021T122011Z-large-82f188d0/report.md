# VA-RAG run report: 20261021T122011Z-large-82f188d0

- Model: `large` = qwen/qwen3-coder
- Split: test; user arm: knows; instances: 237; concepts: 57
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T12:57:19+00:00

> 57 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen3-coder` pinned to provider `deepinfra/turbo` (no fallbacks, parameters required), served as fp4; session `deepinfra/turbo@20261021T082811Z`; 1863 paid calls, 7653 cache hits, $0.3675; providers reported {'DeepInfra': 8532}
- Provider choice: served as fp4 by DeepInfra; Google Vertex was rejected because it accepts repetition_penalty and ignores it (probe of 2026-10-19: 1.0 and 2.0 gave the same text)

- Repeats: every (instance, method) answered under repeat indices [0, 1, 2] in one session; an instance's score is the mean over its repeats, rates are means of instance scores, and intervals resample concepts.

## Primary metrics

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

## Blending, asking, hedging, cost

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

## Commit direction, clue following, order

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

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 91, "INFER": 112, "CONTEXT_CONFLICT": 34} | {"no_conflict": 18, "asked": 357, "inferred": 336} | n/a | 24 | 0.0% | n/a | 54.2% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"UNCERTAIN": 91, "INFER": 112, "CONTEXT_CONFLICT": 34} | {"no_conflict": 18, "unresolved": 357, "inferred": 336} | n/a | 8 | 0.0% | 0.0% | 37.5% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 91, "INFER": 112, "CONTEXT_CONFLICT": 34} | {"no_conflict": 18, "asked": 357, "inferred": 336} | n/a | 0 | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 237} | {"no_conflict": 18, "asked": 693} | n/a | 24 | 0.0% | n/a | 54.2% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"UNCERTAIN": 91, "INFER": 112, "CONTEXT_CONFLICT": 34} | {"no_conflict": 18, "portable": 159, "inferred": 336, "asked": 198} | n/a | 23 | 0.0% | n/a | 52.2% | 0.0% |

Portable-first drafts (`va_rag_portable_first`): 357 drafts, 159 returned without a question (44.5%); rejected: {"exclusive or deprecated usage": 198}.

Risk-coverage sweep on |margin| for `va_rag` (coverage = answered without a question, risk = wrong-version commits among them):

| threshold | coverage | risk |
| --- | --- | --- |
| 14.00 | 0.9% | 0.0% |
| 4.00 | 40.2% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |
| 0.00 | 100.0% | 0.0% |

## Primary contrasts: va_rag against each baseline

Paired bootstrap on per-concept differences of instance scores (va_rag minus baseline); exact McNemar on the repeat-0 instance pairs, Holm-adjusted across the contrasts.

| Baseline | Metric | Difference | 95% bootstrap | discordant (va_rag only / baseline only) | McNemar p | Holm p |
| --- | --- | --- | --- | --- | --- | --- |
| plain_rag | intended_pass | +20.4 pts | [+13.0, +28.0] | 59 / 12 | 0.0000 | 0.0000 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +20.9 pts | [+12.9, +29.1] | 63 / 9 | 0.0000 | 0.0000 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +2.0 pts | [-1.0, +5.6] | 6 / 3 | 0.5078 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | intended_pass | +2.0 pts | [-1.0, +5.6] | 6 / 3 | 0.5078 | 1.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 71.4% (n=35); pandas 59.7% (n=62); pydantic 93.9% (n=131)

**target**: new 79.3% (n=124); old 83.3% (n=104)

**condition**: clue 80.5% (n=82); contradiction 77.5% (n=34); no-clue 85.0% (n=82); stated 76.7% (n=30)

**clue_type**: code 74.7% (n=29); error 81.2% (n=23); pin 85.6% (n=30); pin-new+code-old 71.2% (n=22); pin-old+code-new 88.9% (n=12)

**exclusivity**: behavior 49.1% (n=36); deprecation 97.1% (n=68); one_directional 86.9% (n=28); removal 80.2% (n=96)

**change_type**: behavior 49.1% (n=36); moved_import 100.0% (n=5); param_removed 83.3% (n=2); param_rename 88.7% (n=62); param_value 56.7% (n=30); symbol_removed 90.5% (n=14); symbol_rename 96.2% (n=79)

**user_arm**: knows 81.1% (n=228)

**gold_examples**: both 72.5% (n=51); neither 83.6% (n=177)

**gold_examples_x_change_type**: both / behavior 41.3% (n=21); both / symbol_removed 100.0% (n=6); both / symbol_rename 93.1% (n=24); neither / behavior 60.0% (n=15); neither / moved_import 100.0% (n=5); neither / param_removed 83.3% (n=2); neither / param_rename 88.7% (n=62); neither / param_value 56.7% (n=30); neither / symbol_removed 83.3% (n=8); neither / symbol_rename 97.6% (n=55)

### plain_rag

**library**: numpy 70.5% (n=35); pandas 48.9% (n=62); pydantic 62.6% (n=131)

**target**: new 65.3% (n=124); old 53.8% (n=104)

**condition**: clue 68.7% (n=82); contradiction 47.1% (n=34); no-clue 51.2% (n=82); stated 75.6% (n=30)

**clue_type**: code 56.3% (n=29); error 63.8% (n=23); pin 84.4% (n=30); pin-new+code-old 45.5% (n=22); pin-old+code-new 50.0% (n=12)

**exclusivity**: behavior 51.9% (n=36); deprecation 63.7% (n=68); one_directional 73.8% (n=28); removal 56.6% (n=96)

**change_type**: behavior 51.9% (n=36); moved_import 46.7% (n=5); param_removed 0.0% (n=2); param_rename 65.6% (n=62); param_value 35.6% (n=30); symbol_removed 83.3% (n=14); symbol_rename 67.1% (n=79)

**user_arm**: knows 60.1% (n=228)

**gold_examples**: both 58.8% (n=51); neither 60.5% (n=177)

**gold_examples_x_change_type**: both / behavior 47.6% (n=21); both / symbol_removed 66.7% (n=6); both / symbol_rename 66.7% (n=24); neither / behavior 57.8% (n=15); neither / moved_import 46.7% (n=5); neither / param_removed 0.0% (n=2); neither / param_rename 65.6% (n=62); neither / param_value 35.6% (n=30); neither / symbol_removed 95.8% (n=8); neither / symbol_rename 67.3% (n=55)

### mind_version

**library**: numpy 68.6% (n=35); pandas 48.9% (n=62); pydantic 62.3% (n=131)

**target**: new 61.8% (n=124); old 57.1% (n=104)

**condition**: clue 72.4% (n=82); contradiction 47.1% (n=34); no-clue 47.2% (n=82); stated 73.3% (n=30)

**clue_type**: code 59.8% (n=29); error 69.6% (n=23); pin 86.7% (n=30); pin-new+code-old 45.5% (n=22); pin-old+code-new 50.0% (n=12)

**exclusivity**: behavior 52.8% (n=36); deprecation 63.7% (n=68); one_directional 71.4% (n=28); removal 55.9% (n=96)

**change_type**: behavior 52.8% (n=36); moved_import 40.0% (n=5); param_removed 0.0% (n=2); param_rename 62.4% (n=62); param_value 36.7% (n=30); symbol_removed 85.7% (n=14); symbol_rename 67.5% (n=79)

**user_arm**: knows 59.6% (n=228)

**gold_examples**: both 60.1% (n=51); neither 59.5% (n=177)

**gold_examples_x_change_type**: both / behavior 47.6% (n=21); both / symbol_removed 66.7% (n=6); both / symbol_rename 69.4% (n=24); neither / behavior 60.0% (n=15); neither / moved_import 40.0% (n=5); neither / param_removed 0.0% (n=2); neither / param_rename 62.4% (n=62); neither / param_value 36.7% (n=30); neither / symbol_removed 100.0% (n=8); neither / symbol_rename 66.7% (n=55)

### two_branch

**library**: numpy 68.6% (n=35); pandas 53.2% (n=62); pydantic 95.2% (n=131)

**target**: new 77.4% (n=124); old 82.4% (n=104)

**condition**: clue 78.5% (n=82); contradiction 78.4% (n=34); no-clue 82.5% (n=82); stated 76.7% (n=30)

**clue_type**: code 71.3% (n=29); error 78.3% (n=23); pin 85.6% (n=30); pin-new+code-old 78.8% (n=22); pin-old+code-new 77.8% (n=12)

**exclusivity**: behavior 48.1% (n=36); deprecation 99.0% (n=68); one_directional 81.0% (n=28); removal 77.4% (n=96)

**change_type**: behavior 48.1% (n=36); moved_import 100.0% (n=5); param_removed 66.7% (n=2); param_rename 89.8% (n=62); param_value 43.3% (n=30); symbol_removed 88.1% (n=14); symbol_rename 97.5% (n=79)

**user_arm**: knows 79.7% (n=228)

**gold_examples**: both 71.9% (n=51); neither 81.9% (n=177)

**gold_examples_x_change_type**: both / behavior 41.3% (n=21); both / symbol_removed 88.9% (n=6); both / symbol_rename 94.4% (n=24); neither / behavior 57.8% (n=15); neither / moved_import 100.0% (n=5); neither / param_removed 66.7% (n=2); neither / param_rename 89.8% (n=62); neither / param_value 43.3% (n=30); neither / symbol_removed 87.5% (n=8); neither / symbol_rename 98.8% (n=55)

### always_ask

**library**: numpy 68.6% (n=35); pandas 53.2% (n=62); pydantic 95.2% (n=131)

**target**: new 77.4% (n=124); old 82.4% (n=104)

**condition**: clue 78.5% (n=82); contradiction 78.4% (n=34); no-clue 82.5% (n=82); stated 76.7% (n=30)

**clue_type**: code 71.3% (n=29); error 78.3% (n=23); pin 85.6% (n=30); pin-new+code-old 78.8% (n=22); pin-old+code-new 77.8% (n=12)

**exclusivity**: behavior 48.1% (n=36); deprecation 99.0% (n=68); one_directional 81.0% (n=28); removal 77.4% (n=96)

**change_type**: behavior 48.1% (n=36); moved_import 100.0% (n=5); param_removed 66.7% (n=2); param_rename 89.8% (n=62); param_value 43.3% (n=30); symbol_removed 88.1% (n=14); symbol_rename 97.5% (n=79)

**user_arm**: knows 79.7% (n=228)

**gold_examples**: both 71.9% (n=51); neither 81.9% (n=177)

**gold_examples_x_change_type**: both / behavior 41.3% (n=21); both / symbol_removed 88.9% (n=6); both / symbol_rename 94.4% (n=24); neither / behavior 57.8% (n=15); neither / moved_import 100.0% (n=5); neither / param_removed 66.7% (n=2); neither / param_rename 89.8% (n=62); neither / param_value 43.3% (n=30); neither / symbol_removed 87.5% (n=8); neither / symbol_rename 98.8% (n=55)

## What size of difference this run can show

228 targeted instances over 48 concepts (4.8 per concept), 3 repeats averaged per instance. Measured within-concept correlation rho = 0.385 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.129 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.385 | 9.2 points | measured rho |
| 0.200 | 0.385 | 13.0 points | measured rho |
| 0.300 | 0.385 | 15.9 points | measured rho |
| 0.129 | 0.385 | 10.4 points | observed |
| 0.200 | 0.250 | 11.5 points | handoff assumption |
| 0.200 | 0.500 | 14.1 points | handoff assumption |

## Repeat disagreement (within this session)

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
