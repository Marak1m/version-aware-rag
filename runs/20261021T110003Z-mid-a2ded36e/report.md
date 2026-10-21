# VA-RAG run report: 20261021T110003Z-mid-a2ded36e

- Model: `mid` = qwen/qwen-2.5-coder-32b-instruct
- Split: test; user arm: unsure; instances: 237; concepts: 57
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T11:22:30+00:00

> 57 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen-2.5-coder-32b-instruct` pinned to provider `cloudflare` (no fallbacks, parameters required); session `cloudflare@20261021T082811Z`; 441 paid calls, 3709 cache hits, $0.3191; providers reported {'Cloudflare': 2844}

## Primary metrics

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

## Blending, asking, hedging, cost

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

## Commit direction, clue following, order

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

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 91, "INFER": 112, "CONTEXT_CONFLICT": 34} | {"no_conflict": 6, "both": 119, "inferred": 112} | n/a | 13 | 23.1% | 75.0% | 69.2% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"UNCERTAIN": 91, "INFER": 112, "CONTEXT_CONFLICT": 34} | {"no_conflict": 6, "unresolved": 119, "inferred": 112} | n/a | 7 | 28.6% | 11.8% | 57.1% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"UNCERTAIN": 91, "INFER": 112, "CONTEXT_CONFLICT": 34} | {"no_conflict": 6, "both": 119, "inferred": 112} | n/a | 0 | n/a | 0.0% | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 237} | {"no_conflict": 6, "both": 231} | n/a | 13 | 23.1% | 75.0% | 69.2% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"UNCERTAIN": 91, "INFER": 112, "CONTEXT_CONFLICT": 34} | {"no_conflict": 6, "both": 81, "inferred": 112, "portable": 38} | n/a | 13 | 23.1% | 75.0% | 69.2% | 0.0% |

Portable-first drafts (`va_rag_portable_first`): 119 drafts, 38 returned without a question (31.9%); rejected: {"exclusive or deprecated usage": 78, "does not parse": 3}.

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
| plain_rag | intended_pass | +24.1 pts | [+15.6, +32.9] | 57 / 8 | 0.0000 | 0.0000 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +28.2 pts | [+19.0, +37.4] | 65 / 9 | 0.0000 | 0.0000 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +4.9 pts | [+0.4, +10.8] | 11 / 1 | 0.0063 | 0.0317 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | intended_pass | +26.0 pts | [+17.5, +34.6] | 63 / 9 | 0.0000 | 0.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 65.7% (n=35); pandas 66.1% (n=62); pydantic 75.6% (n=131)

**target**: new 71.8% (n=124); old 71.2% (n=104)

**condition**: clue 70.7% (n=82); contradiction 70.6% (n=34); no-clue 73.2% (n=82); stated 70.0% (n=30)

**clue_type**: code 69.0% (n=29); error 78.3% (n=23); pin 66.7% (n=30); pin-new+code-old 59.1% (n=22); pin-old+code-new 91.7% (n=12)

**exclusivity**: behavior 50.0% (n=36); deprecation 86.8% (n=68); one_directional 92.9% (n=28); removal 62.5% (n=96)

**change_type**: behavior 50.0% (n=36); moved_import 20.0% (n=5); param_removed 100.0% (n=2); param_rename 77.4% (n=62); param_value 56.7% (n=30); symbol_removed 85.7% (n=14); symbol_rename 82.3% (n=79)

**user_arm**: unsure 71.5% (n=228)

**gold_examples**: both 70.6% (n=51); neither 71.8% (n=177)

**gold_examples_x_change_type**: both / behavior 52.4% (n=21); both / symbol_removed 100.0% (n=6); both / symbol_rename 79.2% (n=24); neither / behavior 46.7% (n=15); neither / moved_import 20.0% (n=5); neither / param_removed 100.0% (n=2); neither / param_rename 77.4% (n=62); neither / param_value 56.7% (n=30); neither / symbol_removed 75.0% (n=8); neither / symbol_rename 83.6% (n=55)

### plain_rag

**library**: numpy 48.6% (n=35); pandas 50.0% (n=62); pydantic 50.4% (n=131)

**target**: new 51.6% (n=124); old 48.1% (n=104)

**condition**: clue 52.4% (n=82); contradiction 44.1% (n=34); no-clue 42.7% (n=82); stated 70.0% (n=30)

**clue_type**: code 41.4% (n=29); error 43.5% (n=23); pin 70.0% (n=30); pin-new+code-old 45.5% (n=22); pin-old+code-new 41.7% (n=12)

**exclusivity**: behavior 47.2% (n=36); deprecation 64.7% (n=68); one_directional 60.7% (n=28); removal 37.5% (n=96)

**change_type**: behavior 47.2% (n=36); moved_import 0.0% (n=5); param_removed 0.0% (n=2); param_rename 43.5% (n=62); param_value 36.7% (n=30); symbol_removed 57.1% (n=14); symbol_rename 64.6% (n=79)

**user_arm**: unsure 50.0% (n=228)

**gold_examples**: both 60.8% (n=51); neither 46.9% (n=177)

**gold_examples_x_change_type**: both / behavior 52.4% (n=21); both / symbol_removed 66.7% (n=6); both / symbol_rename 66.7% (n=24); neither / behavior 40.0% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 0.0% (n=2); neither / param_rename 43.5% (n=62); neither / param_value 36.7% (n=30); neither / symbol_removed 50.0% (n=8); neither / symbol_rename 63.6% (n=55)

### mind_version

**library**: numpy 48.6% (n=35); pandas 46.8% (n=62); pydantic 46.6% (n=131)

**target**: new 49.2% (n=124); old 44.2% (n=104)

**condition**: clue 50.0% (n=82); contradiction 41.2% (n=34); no-clue 37.8% (n=82); stated 70.0% (n=30)

**clue_type**: code 44.8% (n=29); error 34.8% (n=23); pin 66.7% (n=30); pin-new+code-old 45.5% (n=22); pin-old+code-new 33.3% (n=12)

**exclusivity**: behavior 47.2% (n=36); deprecation 58.8% (n=68); one_directional 53.6% (n=28); removal 36.5% (n=96)

**change_type**: behavior 47.2% (n=36); moved_import 0.0% (n=5); param_removed 0.0% (n=2); param_rename 35.5% (n=62); param_value 43.3% (n=30); symbol_removed 57.1% (n=14); symbol_rename 59.5% (n=79)

**user_arm**: unsure 46.9% (n=228)

**gold_examples**: both 56.9% (n=51); neither 44.1% (n=177)

**gold_examples_x_change_type**: both / behavior 52.4% (n=21); both / symbol_removed 66.7% (n=6); both / symbol_rename 58.3% (n=24); neither / behavior 40.0% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 0.0% (n=2); neither / param_rename 35.5% (n=62); neither / param_value 43.3% (n=30); neither / symbol_removed 50.0% (n=8); neither / symbol_rename 60.0% (n=55)

### two_branch

**library**: numpy 65.7% (n=35); pandas 50.0% (n=62); pydantic 75.6% (n=131)

**target**: new 64.5% (n=124); old 70.2% (n=104)

**condition**: clue 65.9% (n=82); contradiction 64.7% (n=34); no-clue 69.5% (n=82); stated 66.7% (n=30)

**clue_type**: code 62.1% (n=29); error 69.6% (n=23); pin 66.7% (n=30); pin-new+code-old 59.1% (n=22); pin-old+code-new 75.0% (n=12)

**exclusivity**: behavior 47.2% (n=36); deprecation 88.2% (n=68); one_directional 85.7% (n=28); removal 54.2% (n=96)

**change_type**: behavior 47.2% (n=36); moved_import 20.0% (n=5); param_removed 100.0% (n=2); param_rename 75.8% (n=62); param_value 26.7% (n=30); symbol_removed 85.7% (n=14); symbol_rename 83.5% (n=79)

**user_arm**: unsure 67.1% (n=228)

**gold_examples**: both 70.6% (n=51); neither 66.1% (n=177)

**gold_examples_x_change_type**: both / behavior 52.4% (n=21); both / symbol_removed 100.0% (n=6); both / symbol_rename 79.2% (n=24); neither / behavior 40.0% (n=15); neither / moved_import 20.0% (n=5); neither / param_removed 100.0% (n=2); neither / param_rename 75.8% (n=62); neither / param_value 26.7% (n=30); neither / symbol_removed 75.0% (n=8); neither / symbol_rename 85.5% (n=55)

### always_ask

**library**: numpy 48.6% (n=35); pandas 50.0% (n=62); pydantic 46.6% (n=131)

**target**: new 51.6% (n=124); old 43.3% (n=104)

**condition**: clue 48.8% (n=82); contradiction 41.2% (n=34); no-clue 39.0% (n=82); stated 76.7% (n=30)

**clue_type**: code 37.9% (n=29); error 39.1% (n=23); pin 66.7% (n=30); pin-new+code-old 45.5% (n=22); pin-old+code-new 33.3% (n=12)

**exclusivity**: behavior 47.2% (n=36); deprecation 55.9% (n=68); one_directional 60.7% (n=28); removal 38.5% (n=96)

**change_type**: behavior 47.2% (n=36); moved_import 0.0% (n=5); param_removed 0.0% (n=2); param_rename 43.5% (n=62); param_value 40.0% (n=30); symbol_removed 57.1% (n=14); symbol_rename 57.0% (n=79)

**user_arm**: unsure 47.8% (n=228)

**gold_examples**: both 56.9% (n=51); neither 45.2% (n=177)

**gold_examples_x_change_type**: both / behavior 52.4% (n=21); both / symbol_removed 66.7% (n=6); both / symbol_rename 58.3% (n=24); neither / behavior 40.0% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 0.0% (n=2); neither / param_rename 43.5% (n=62); neither / param_value 40.0% (n=30); neither / symbol_removed 50.0% (n=8); neither / symbol_rename 56.4% (n=55)

## What size of difference this run can show

228 targeted instances over 48 concepts (4.8 per concept). Measured within-concept correlation rho = 0.350 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.183 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.350 | 8.9 points | measured rho |
| 0.200 | 0.350 | 12.6 points | measured rho |
| 0.300 | 0.350 | 15.4 points | measured rho |
| 0.183 | 0.350 | 12.1 points | observed |
| 0.200 | 0.250 | 11.5 points | handoff assumption |
| 0.200 | 0.500 | 14.1 points | handoff assumption |
