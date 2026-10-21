# VA-RAG run report: 20261021T105119Z-small-6168007f

- Model: `small` = qwen/qwen-2.5-7b-instruct
- Split: test; user arm: unsure; instances: 237; concepts: 57
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T11:15:13+00:00

> 57 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen-2.5-7b-instruct` pinned to provider `phala` (no fallbacks, parameters required); session `phala@20261021T082811Z`; 735 paid calls, 10955 cache hits, $0.0823; providers reported {'Phala': 8532}
- Provider choice: qwen/qwen2.5-coder-7b-instruct had no live endpoint on 2026-10-19, so the general 7B instruct model stands in

- Repeats: every (instance, method) answered under repeat indices [0, 1, 2] in one session; an instance's score is the mean over its repeats, rates are means of instance scores, and intervals resample concepts.

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 30.7% [21.3%, 40.9%] (Wilson 22.7%, 48.7%) | 31.3% | 28.7% | 34.1% | 17.5% | 13.9% | 49.7% | 2.0% | 0.0% | 0.0% | 7.6% |
| assume_state | 31.1% [21.8%, 41.2%] (Wilson 23.0%, 49.0%) | 31.8% | 28.9% | 33.2% | 15.2% | 14.5% | 50.0% | 3.7% | 0.0% | 0.0% | 6.1% |
| mind_version | 27.8% [19.1%, 37.7%] (Wilson 20.4%, 45.8%) | 28.7% | 26.9% | 31.1% | 17.4% | 14.6% | 52.0% | 2.8% | 0.0% | 0.0% | 3.8% |
| no_retrieval | 27.0% [18.4%, 36.5%] (Wilson 20.6%, 46.1%) | 28.2% | 25.7% | 29.5% | 12.0% | 15.9% | 55.3% | 5.4% | 0.3% | 0.0% | 4.3% |
| oracle_docs | 39.8% [28.7%, 51.6%] (Wilson 31.4%, 58.5%) | 41.6% | 39.2% | 40.6% | 7.3% | 15.2% | 48.5% | 4.4% | 0.0% | 0.0% | 2.0% |
| plain_rag | 30.6% [21.0%, 41.0%] (Wilson 22.4%, 48.4%) | 31.8% | 28.9% | 33.8% | 16.4% | 14.9% | 48.7% | 4.4% | 0.0% | 0.0% | 5.1% |
| two_branch | 37.3% [27.6%, 47.8%] (Wilson 27.6%, 54.3%) | 38.3% | 36.5% | 38.2% | 7.0% | 12.1% | 51.9% | 3.8% | 0.0% | 0.0% | 2.1% |
| va_rag | 42.1% [31.7%, 53.1%] (Wilson 31.6%, 58.7%) | 43.2% | 41.7% | 43.0% | 3.9% | 13.6% | 51.2% | 2.8% | 0.0% | 0.0% | 0.9% |
| va_rag_no_ask | 37.3% [27.4%, 47.5%] (Wilson 27.2%, 53.9%) | 37.9% | 36.7% | 39.3% | 11.3% | 14.3% | 49.4% | 2.0% | 0.0% | 0.0% | 2.1% |
| va_rag_no_guard | 36.7% [26.8%, 47.1%] (Wilson 26.2%, 52.8%) | 37.9% | 35.8% | 37.6% | 7.9% | 11.4% | 51.6% | 3.8% | 0.0% | 0.0% | 2.1% |
| va_rag_no_infer | 42.1% [31.7%, 53.1%] (Wilson 31.6%, 58.7%) | 43.2% | 41.7% | 43.0% | 3.9% | 13.6% | 51.2% | 2.8% | 0.0% | 0.0% | 0.9% |
| va_rag_portable_first | 42.1% [32.2%, 52.4%] (Wilson 32.5%, 59.7%) | 43.2% | 41.7% | 43.0% | 3.5% | 15.8% | 52.0% | 2.3% | 0.0% | 0.0% | 0.9% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 1.8% [0.4%, 3.5%] (Wilson 0.2%, 9.7%) | 0.4% [0.0%, 1.4%] (Wilson 0.0%, 8.0%) | 0.0% | 100.0% | 34.6% | 100.0% | 100.0% | 0.0% | c=0.0: 30.7%, c=0.1: 20.7%, c=0.3: 0.7% | 1.00 calls, 1.00 answers |
| assume_state | 1.5% [0.3%, 2.9%] (Wilson 0.1%, 9.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 31.1%, c=0.1: 31.1%, c=0.3: 31.1% | 1.00 calls, 0.99 answers |
| mind_version | 3.5% [1.0%, 6.5%] (Wilson 0.6%, 12.0%) | 0.9% [0.0%, 2.8%] (Wilson 0.0%, 8.5%) | 0.0% | 32.9% | 38.0% | 27.5% | 29.4% | 0.0% | c=0.0: 27.8%, c=0.1: 24.8%, c=0.3: 18.9% | 1.30 calls, 1.00 answers |
| no_retrieval | 0.9% [0.0%, 2.6%] (Wilson 0.1%, 8.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | 0.0% | 3.3% | 8.8% | 0.0% | c=0.0: 27.0%, c=0.1: 26.7%, c=0.3: 26.1% | 1.03 calls, 0.99 answers |
| oracle_docs | 1.9% [0.3%, 4.2%] (Wilson 0.2%, 10.1%) | 0.9% [0.0%, 2.8%] (Wilson 0.0%, 8.5%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 39.8%, c=0.1: 39.8%, c=0.3: 39.8% | 1.00 calls, 1.00 answers |
| plain_rag | 1.0% [0.1%, 2.2%] (Wilson 0.1%, 8.8%) | 0.6% [0.0%, 1.7%] (Wilson 0.0%, 8.2%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 30.6%, c=0.1: 30.6%, c=0.3: 30.6% | 1.00 calls, 1.00 answers |
| two_branch | 2.5% [0.4%, 5.1%] (Wilson 0.4%, 11.0%) | 0.9% [0.0%, 2.8%] (Wilson 0.0%, 8.5%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 95.0% | c=0.0: 37.3%, c=0.1: 27.3%, c=0.3: 7.3% | 1.97 calls, 1.97 answers |
| va_rag | 0.3% [0.0%, 0.7%] (Wilson 0.0%, 7.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 68.9% | 2.5% | 100.0% | 2.5% | c=0.0: 42.1%, c=0.1: 37.0%, c=0.3: 26.8% | 1.66 calls, 1.50 answers |
| va_rag_no_ask | 0.4% [0.0%, 1.0%] (Wilson 0.0%, 8.2%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 37.3%, c=0.1: 37.3%, c=0.3: 37.3% | 1.08 calls, 1.00 answers |
| va_rag_no_guard | 1.9% [0.0%, 4.4%] (Wilson 0.2%, 10.1%) | 0.9% [0.0%, 2.8%] (Wilson 0.0%, 8.5%) | 0.0% | 100.0% | 68.9% | 2.5% | 100.0% | 2.5% | c=0.0: 36.7%, c=0.1: 31.6%, c=0.3: 21.4% | 1.50 calls, 1.50 answers |
| va_rag_no_infer | 0.3% [0.0%, 0.7%] (Wilson 0.0%, 7.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 35.5% | 95.0% | 100.0% | 95.0% | c=0.0: 42.1%, c=0.1: 32.1%, c=0.3: 12.1% | 2.18 calls, 1.97 answers |
| va_rag_portable_first | 0.3% [0.0%, 0.7%] (Wilson 0.0%, 7.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 59.3% | 68.5% | 0.0% | 62.7% | 0.0% | c=0.0: 42.1%, c=0.1: 39.0%, c=0.3: 32.9% | 1.73 calls, 1.30 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | -0.014 | n/a |
| assume_state | old 17.1%, new 40.7%, both 0.4%, neither 41.9% (n=246) | 23.6% | -0.040 | n/a |
| mind_version | old 20.0%, new 50.9%, both 4.2%, neither 24.8% (n=165) | 30.0% | 0.013 | n/a |
| no_retrieval | old 28.3%, new 7.4%, both 0.8%, neither 63.5% (n=244) | 16.2% | 0.068 | n/a |
| oracle_docs | old 13.8%, new 26.8%, both 3.3%, neither 56.1% (n=246) | 40.7% | 0.014 | n/a |
| plain_rag | old 13.0%, new 39.0%, both 0.8%, neither 47.2% (n=246) | 26.8% | 0.012 | n/a |
| two_branch | old 18.3%, new 28.0%, both 2.4%, neither 51.2% (n=246) | 39.8% | -0.039 | 20.3% |
| va_rag |  (n=0) | 44.3% | 0.015 | 22.1% |
| va_rag_no_ask | old 14.2%, new 43.1%, both 0.0%, neither 42.7% (n=246) | 44.3% | 0.051 | n/a |
| va_rag_no_guard |  (n=0) | 39.8% | -0.029 | 16.1% |
| va_rag_no_infer |  (n=0) | n/a | 0.015 | 25.9% |
| va_rag_portable_first | old 0.0%, new 0.0%, both 0.0%, neither 100.0% (n=100) | 44.3% | 0.063 | 21.5% |

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision, exclusive-error oracle | guard recall, exclusive-error oracle | guard precision, strict-named oracle | guard recall, strict-named oracle | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 91, "INFER": 112, "CONTEXT_CONFLICT": 34} | {"no_conflict": 18, "both": 357, "inferred": 336} | n/a | 77 | 31.2% | 55.8% | 83.1% | 95.5% | 48.1% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"UNCERTAIN": 91, "INFER": 112, "CONTEXT_CONFLICT": 34} | {"no_conflict": 18, "unresolved": 357, "inferred": 336} | n/a | 54 | 33.3% | 24.0% | 79.6% | 28.7% | 48.1% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 91, "INFER": 112, "CONTEXT_CONFLICT": 34} | {"no_conflict": 18, "both": 357, "inferred": 336} | n/a | 0 | n/a | 0.0% | n/a | n/a | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 237} | {"no_conflict": 18, "both": 693} | n/a | 77 | 31.2% | 55.8% | 83.1% | 95.5% | 48.1% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"UNCERTAIN": 91, "INFER": 112, "CONTEXT_CONFLICT": 34} | {"no_conflict": 18, "portable": 147, "inferred": 336, "both": 210} | n/a | 73 | 31.5% | 54.8% | 83.6% | 92.4% | 50.7% | 0.0% |

Guard oracles (`varag.eval.oracle`): exclusive-error (M7) counts a failure whose AttributeError, ImportError or TypeError names an exclusive symbol; strict-named (2026-10-21 correction) counts a strict failure in the committed version whose error, traceback, counted warning or failing line shows the usage, so rejected values and deprecation warnings count too.

Portable-first drafts (`va_rag_portable_first`): 357 drafts, 147 returned without a question (41.2%); rejected: {"exclusive or deprecated usage": 203, "no code": 7}.

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
| plain_rag | intended_pass | +10.5 pts | [+3.4, +17.9] | 39 / 15 | 0.0015 | 0.0105 |
| plain_rag | blend_exec | -0.4 pts | [-1.2, +0.0] | 0 / 2 | 0.5000 | 1.0000 |
| mind_version | intended_pass | +13.0 pts | [+4.3, +22.0] | 47 / 20 | 0.0013 | 0.0105 |
| mind_version | blend_exec | -0.6 pts | [-1.8, +0.0] | 0 / 2 | 0.5000 | 1.0000 |
| two_branch | intended_pass | +4.5 pts | [+0.1, +9.0] | 13 / 3 | 0.0213 | 0.1064 |
| two_branch | blend_exec | -0.6 pts | [-1.8, +0.0] | 0 / 2 | 0.5000 | 1.0000 |
| always_ask | intended_pass | +10.2 pts | [+2.1, +17.9] | 40 / 17 | 0.0032 | 0.0192 |
| always_ask | blend_exec | -0.3 pts | [-0.9, +0.0] | 0 / 1 | 1.0000 | 1.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 58.1% (n=35); pandas 43.5% (n=62); pydantic 37.2% (n=131)

**target**: new 45.7% (n=124); old 37.8% (n=104)

**condition**: clue 44.3% (n=82); contradiction 36.3% (n=34); no-clue 40.7% (n=82); stated 46.7% (n=30)

**clue_type**: code 50.6% (n=29); error 33.3% (n=23); pin 46.7% (n=30); pin-new+code-old 31.8% (n=22); pin-old+code-new 44.4% (n=12)

**exclusivity**: behavior 38.0% (n=36); deprecation 41.2% (n=68); one_directional 58.3% (n=28); removal 39.6% (n=96)

**change_type**: behavior 38.0% (n=36); moved_import 0.0% (n=5); param_removed 16.7% (n=2); param_rename 41.4% (n=62); param_value 44.4% (n=30); symbol_removed 50.0% (n=14); symbol_rename 45.6% (n=79)

**user_arm**: unsure 42.1% (n=228)

**gold_examples**: both 45.8% (n=51); neither 41.1% (n=177)

**gold_examples_x_change_type**: both / behavior 33.3% (n=21); both / symbol_removed 50.0% (n=6); both / symbol_rename 55.6% (n=24); neither / behavior 44.4% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 16.7% (n=2); neither / param_rename 41.4% (n=62); neither / param_value 44.4% (n=30); neither / symbol_removed 50.0% (n=8); neither / symbol_rename 41.2% (n=55)

### plain_rag

**library**: numpy 50.5% (n=35); pandas 37.6% (n=62); pydantic 21.9% (n=131)

**target**: new 32.8% (n=124); old 27.9% (n=104)

**condition**: clue 32.1% (n=82); contradiction 30.4% (n=34); no-clue 28.0% (n=82); stated 33.3% (n=30)

**clue_type**: code 28.7% (n=29); error 30.4% (n=23); pin 36.7% (n=30); pin-new+code-old 33.3% (n=22); pin-old+code-new 25.0% (n=12)

**exclusivity**: behavior 41.7% (n=36); deprecation 26.0% (n=68); one_directional 52.4% (n=28); removal 23.3% (n=96)

**change_type**: behavior 41.7% (n=36); moved_import 0.0% (n=5); param_removed 50.0% (n=2); param_rename 26.9% (n=62); param_value 25.6% (n=30); symbol_removed 47.6% (n=14); symbol_rename 28.7% (n=79)

**user_arm**: unsure 30.6% (n=228)

**gold_examples**: both 27.5% (n=51); neither 31.5% (n=177)

**gold_examples_x_change_type**: both / behavior 33.3% (n=21); both / symbol_removed 33.3% (n=6); both / symbol_rename 20.8% (n=24); neither / behavior 53.3% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 50.0% (n=2); neither / param_rename 26.9% (n=62); neither / param_value 25.6% (n=30); neither / symbol_removed 58.3% (n=8); neither / symbol_rename 32.1% (n=55)

### mind_version

**library**: numpy 45.7% (n=35); pandas 35.5% (n=62); pydantic 19.3% (n=131)

**target**: new 29.3% (n=124); old 26.0% (n=104)

**condition**: clue 27.2% (n=82); contradiction 21.6% (n=34); no-clue 28.9% (n=82); stated 33.3% (n=30)

**clue_type**: code 21.8% (n=29); error 20.3% (n=23); pin 37.8% (n=30); pin-new+code-old 18.2% (n=22); pin-old+code-new 27.8% (n=12)

**exclusivity**: behavior 36.1% (n=36); deprecation 22.5% (n=68); one_directional 52.4% (n=28); removal 21.2% (n=96)

**change_type**: behavior 36.1% (n=36); moved_import 0.0% (n=5); param_removed 50.0% (n=2); param_rename 26.3% (n=62); param_value 23.3% (n=30); symbol_removed 40.5% (n=14); symbol_rename 25.7% (n=79)

**user_arm**: unsure 27.8% (n=228)

**gold_examples**: both 28.1% (n=51); neither 27.7% (n=177)

**gold_examples_x_change_type**: both / behavior 41.3% (n=21); both / symbol_removed 33.3% (n=6); both / symbol_rename 15.3% (n=24); neither / behavior 28.9% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 50.0% (n=2); neither / param_rename 26.3% (n=62); neither / param_value 23.3% (n=30); neither / symbol_removed 45.8% (n=8); neither / symbol_rename 30.3% (n=55)

### two_branch

**library**: numpy 51.4% (n=35); pandas 38.2% (n=62); pydantic 33.1% (n=131)

**target**: new 39.2% (n=124); old 34.9% (n=104)

**condition**: clue 39.8% (n=82); contradiction 38.2% (n=34); no-clue 36.2% (n=82); stated 32.2% (n=30)

**clue_type**: code 44.8% (n=29); error 27.5% (n=23); pin 44.4% (n=30); pin-new+code-old 36.4% (n=22); pin-old+code-new 41.7% (n=12)

**exclusivity**: behavior 38.9% (n=36); deprecation 40.7% (n=68); one_directional 53.6% (n=28); removal 29.5% (n=96)

**change_type**: behavior 38.9% (n=36); moved_import 0.0% (n=5); param_removed 33.3% (n=2); param_rename 33.3% (n=62); param_value 30.0% (n=30); symbol_removed 50.0% (n=14); symbol_rename 42.6% (n=79)

**user_arm**: unsure 37.3% (n=228)

**gold_examples**: both 43.8% (n=51); neither 35.4% (n=177)

**gold_examples_x_change_type**: both / behavior 33.3% (n=21); both / symbol_removed 33.3% (n=6); both / symbol_rename 55.6% (n=24); neither / behavior 46.7% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 33.3% (n=2); neither / param_rename 33.3% (n=62); neither / param_value 30.0% (n=30); neither / symbol_removed 62.5% (n=8); neither / symbol_rename 37.0% (n=55)

### always_ask

**library**: numpy 51.4% (n=35); pandas 34.9% (n=62); pydantic 23.2% (n=131)

**target**: new 34.9% (n=124); old 25.6% (n=104)

**condition**: clue 30.5% (n=82); contradiction 27.5% (n=34); no-clue 30.9% (n=82); stated 34.4% (n=30)

**clue_type**: code 26.4% (n=29); error 27.5% (n=23); pin 36.7% (n=30); pin-new+code-old 28.8% (n=22); pin-old+code-new 25.0% (n=12)

**exclusivity**: behavior 39.8% (n=36); deprecation 25.0% (n=68); one_directional 53.6% (n=28); removal 24.7% (n=96)

**change_type**: behavior 39.8% (n=36); moved_import 0.0% (n=5); param_removed 50.0% (n=2); param_rename 31.2% (n=62); param_value 21.1% (n=30); symbol_removed 50.0% (n=14); symbol_rename 27.8% (n=79)

**user_arm**: unsure 30.7% (n=228)

**gold_examples**: both 24.2% (n=51); neither 32.6% (n=177)

**gold_examples_x_change_type**: both / behavior 33.3% (n=21); both / symbol_removed 16.7% (n=6); both / symbol_rename 18.1% (n=24); neither / behavior 48.9% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 50.0% (n=2); neither / param_rename 31.2% (n=62); neither / param_value 21.1% (n=30); neither / symbol_removed 75.0% (n=8); neither / symbol_rename 32.1% (n=55)

## What size of difference this run can show

228 targeted instances over 48 concepts (4.8 per concept), 3 repeats averaged per instance. Measured within-concept correlation rho = 0.452 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.133 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.452 | 9.6 points | measured rho |
| 0.200 | 0.452 | 13.6 points | measured rho |
| 0.300 | 0.452 | 16.7 points | measured rho |
| 0.133 | 0.452 | 11.1 points | observed |
| 0.200 | 0.250 | 11.5 points | handoff assumption |
| 0.200 | 0.500 | 14.1 points | handoff assumption |

## Repeat disagreement (within this session)

2844 (instance, method) pairs answered under 3 repeats: response text differs on 59.0%, outcome on 15.1%, intended-version pass on 10.0%.

| Method | pairs | text differs | outcome differs |
| --- | --- | --- | --- |
| always_ask | 237 | 52.7% | 11.4% |
| assume_state | 237 | 70.5% | 19.4% |
| mind_version | 237 | 54.9% | 19.8% |
| no_retrieval | 237 | 48.9% | 12.2% |
| oracle_docs | 237 | 49.4% | 12.2% |
| plain_rag | 237 | 50.6% | 16.0% |
| two_branch | 237 | 72.6% | 15.6% |
| va_rag | 237 | 62.0% | 14.8% |
| va_rag_no_ask | 237 | 51.9% | 13.5% |
| va_rag_no_guard | 237 | 62.0% | 15.2% |
| va_rag_no_infer | 237 | 72.6% | 14.8% |
| va_rag_portable_first | 237 | 60.3% | 16.0% |
