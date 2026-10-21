# VA-RAG final sweep: small (20261021T082811Z)

Session `phala@20261021T082811Z`; cost $0.8616; run time 2.1 h. Each section below is one run's full report.

# dev-knows

## VA-RAG run report: 20261021T085318Z-small-b8bb67b6

- Model: `small` = qwen/qwen-2.5-7b-instruct
- Split: dev; user arm: knows; instances: 101; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T09:23:02+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen-2.5-7b-instruct` pinned to provider `phala` (no fallbacks, parameters required); session `phala@20261021T082811Z`; 2306 paid calls, 1907 cache hits, $0.2198; providers reported {'Phala': 3636}
- Provider choice: qwen/qwen2.5-coder-7b-instruct had no live endpoint on 2026-10-19, so the general 7B instruct model stands in

- Repeats: every (instance, method) answered under repeat indices [0, 1, 2] in one session; an instance's score is the mean over its repeats, rates are means of instance scores, and intervals resample concepts.

### Primary metrics

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

### Blending, asking, hedging, cost

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

### Commit direction, clue following, order

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

### Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"asked": 129, "inferred": 162, "no_conflict": 12} | n/a | 34 | 64.7% | 81.5% | 41.2% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"inferred": 162, "no_conflict": 12, "unresolved": 129} | n/a | 21 | 66.7% | 27.5% | 42.9% | 4.8% |
| va_rag_no_guard | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"asked": 129, "inferred": 162, "no_conflict": 12} | n/a | 0 | n/a | 0.0% | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 101} | {"asked": 291, "no_conflict": 12} | n/a | 34 | 64.7% | 81.5% | 41.2% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"asked": 83, "inferred": 162, "no_conflict": 12, "portable": 46} | n/a | 27 | 66.7% | 85.7% | 48.1% | 0.0% |

Portable-first drafts (`va_rag_portable_first`): 129 drafts, 46 returned without a question (35.7%); rejected: {"exclusive or deprecated usage": 83}.

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
| always_ask | intended_pass | +8.9 pts | [-0.0, +20.0] | 6 / 1 | 0.1250 | 0.7500 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +16.3 pts | [+0.6, +32.1] | 24 / 8 | 0.0070 | 0.0490 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| plain_rag | intended_pass | +23.8 pts | [+6.7, +42.2] | 23 / 3 | 0.0001 | 0.0007 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +8.9 pts | [-0.0, +20.0] | 6 / 1 | 0.1250 | 0.7500 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

### Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

#### va_rag

**change_type**: behavior 35.7% (n=14); param_removed 100.0% (n=2); param_rename 46.8% (n=37); param_value 0.0% (n=7); symbol_rename 92.4% (n=35)

**clue_type**: code 60.6% (n=11); error 66.7% (n=6); pin 57.6% (n=11); pin-new+code-old 33.3% (n=6); pin-old+code-new 57.1% (n=7)

**condition**: clue 60.7% (n=28); contradiction 46.2% (n=13); no-clue 63.1% (n=28); stated 61.5% (n=26)

**exclusivity**: behavior 35.7% (n=14); deprecation 63.5% (n=21); one_directional 50.0% (n=4); removal 64.9% (n=56)

**gold_examples**: both 63.6% (n=44); neither 56.2% (n=51)

**gold_examples_x_change_type**: both / behavior 35.7% (n=14); both / param_removed 100.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 46.8% (n=37); neither / symbol_rename 81.0% (n=14)

**library**: numpy 72.9% (n=16); pandas 54.4% (n=30); pydantic 58.5% (n=49)

**target**: new 58.2% (n=51); old 61.4% (n=44)

**user_arm**: knows 59.6% (n=95)

#### plain_rag

**change_type**: behavior 61.9% (n=14); param_removed 0.0% (n=2); param_rename 27.9% (n=37); param_value 0.0% (n=7); symbol_rename 50.5% (n=35)

**clue_type**: code 33.3% (n=11); error 38.9% (n=6); pin 54.5% (n=11); pin-new+code-old 33.3% (n=6); pin-old+code-new 23.8% (n=7)

**condition**: clue 42.9% (n=28); contradiction 28.2% (n=13); no-clue 33.3% (n=28); stated 44.9% (n=26)

**exclusivity**: behavior 61.9% (n=14); deprecation 31.7% (n=21); one_directional 0.0% (n=4); removal 38.1% (n=56)

**gold_examples**: both 42.4% (n=44); neither 35.3% (n=51)

**gold_examples_x_change_type**: both / behavior 61.9% (n=14); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 47.6% (n=21); neither / param_rename 27.9% (n=37); neither / symbol_rename 54.8% (n=14)

**library**: numpy 54.2% (n=16); pandas 43.3% (n=30); pydantic 30.6% (n=49)

**target**: new 30.7% (n=51); old 47.7% (n=44)

**user_arm**: knows 38.6% (n=95)

#### mind_version

**change_type**: behavior 64.3% (n=14); param_removed 50.0% (n=2); param_rename 33.3% (n=37); param_value 0.0% (n=7); symbol_rename 56.2% (n=35)

**clue_type**: code 48.5% (n=11); error 33.3% (n=6); pin 63.6% (n=11); pin-new+code-old 33.3% (n=6); pin-old+code-new 23.8% (n=7)

**condition**: clue 51.2% (n=28); contradiction 28.2% (n=13); no-clue 38.1% (n=28); stated 51.3% (n=26)

**exclusivity**: behavior 64.3% (n=14); deprecation 34.9% (n=21); one_directional 25.0% (n=4); removal 44.0% (n=56)

**gold_examples**: both 47.7% (n=44); neither 41.2% (n=51)

**gold_examples_x_change_type**: both / behavior 64.3% (n=14); both / param_removed 50.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 52.4% (n=21); neither / param_rename 33.3% (n=37); neither / symbol_rename 61.9% (n=14)

**library**: numpy 60.4% (n=16); pandas 45.6% (n=30); pydantic 38.1% (n=49)

**target**: new 39.9% (n=51); old 49.2% (n=44)

**user_arm**: knows 44.2% (n=95)

#### two_branch

**change_type**: behavior 35.7% (n=14); param_removed 33.3% (n=2); param_rename 47.7% (n=37); param_value 0.0% (n=7); symbol_rename 78.1% (n=35)

**clue_type**: code 42.4% (n=11); error 50.0% (n=6); pin 57.6% (n=11); pin-new+code-old 38.9% (n=6); pin-old+code-new 33.3% (n=7)

**condition**: clue 50.0% (n=28); contradiction 35.9% (n=13); no-clue 60.7% (n=28); stated 57.7% (n=26)

**exclusivity**: behavior 35.7% (n=14); deprecation 58.7% (n=21); one_directional 16.7% (n=4); removal 58.3% (n=56)

**gold_examples**: both 50.8% (n=44); neither 55.6% (n=51)

**gold_examples_x_change_type**: both / behavior 35.7% (n=14); both / param_removed 33.3% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 79.4% (n=21); neither / param_rename 47.7% (n=37); neither / symbol_rename 76.2% (n=14)

**library**: numpy 72.9% (n=16); pandas 35.6% (n=30); pydantic 57.8% (n=49)

**target**: new 49.7% (n=51); old 57.6% (n=44)

**user_arm**: knows 53.3% (n=95)

#### always_ask

**change_type**: behavior 35.7% (n=14); param_removed 33.3% (n=2); param_rename 47.7% (n=37); param_value 0.0% (n=7); symbol_rename 78.1% (n=35)

**clue_type**: code 42.4% (n=11); error 50.0% (n=6); pin 57.6% (n=11); pin-new+code-old 38.9% (n=6); pin-old+code-new 33.3% (n=7)

**condition**: clue 50.0% (n=28); contradiction 35.9% (n=13); no-clue 60.7% (n=28); stated 57.7% (n=26)

**exclusivity**: behavior 35.7% (n=14); deprecation 58.7% (n=21); one_directional 16.7% (n=4); removal 58.3% (n=56)

**gold_examples**: both 50.8% (n=44); neither 55.6% (n=51)

**gold_examples_x_change_type**: both / behavior 35.7% (n=14); both / param_removed 33.3% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 79.4% (n=21); neither / param_rename 47.7% (n=37); neither / symbol_rename 76.2% (n=14)

**library**: numpy 72.9% (n=16); pandas 35.6% (n=30); pydantic 57.8% (n=49)

**target**: new 49.7% (n=51); old 57.6% (n=44)

**user_arm**: knows 53.3% (n=95)

### What size of difference this run can show

95 targeted instances over 15 concepts (6.3 per concept), 3 repeats averaged per instance. Measured within-concept correlation rho = 0.450 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.168 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.450 | 16.8 points | measured rho |
| 0.200 | 0.450 | 23.7 points | measured rho |
| 0.300 | 0.450 | 29.0 points | measured rho |
| 0.168 | 0.450 | 21.7 points | observed |
| 0.200 | 0.250 | 19.6 points | handoff assumption |
| 0.200 | 0.500 | 24.6 points | handoff assumption |

### Repeat disagreement (within this session)

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

# dev-unsure

## VA-RAG run report: 20261021T092321Z-small-d053e812

- Model: `small` = qwen/qwen-2.5-7b-instruct
- Split: dev; user arm: unsure; instances: 101; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T09:34:23+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen-2.5-7b-instruct` pinned to provider `phala` (no fallbacks, parameters required); session `phala@20261021T082811Z`; 308 paid calls, 4561 cache hits, $0.0342; providers reported {'Phala': 3636}
- Provider choice: qwen/qwen2.5-coder-7b-instruct had no live endpoint on 2026-10-19, so the general 7B instruct model stands in

- Repeats: every (instance, method) answered under repeat indices [0, 1, 2] in one session; an instance's score is the mean over its repeats, rates are means of instance scores, and intervals resample concepts.

### Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 39.6% [25.1%, 54.4%] (Wilson 16.9%, 60.6%) | 39.6% | 32.3% | 40.7% | 25.3% | 14.0% | 33.0% | 2.1% | 0.0% | 0.0% | 21.4% |
| assume_state | 37.2% [24.3%, 50.0%] (Wilson 15.4%, 58.6%) | 37.4% | 32.3% | 37.2% | 22.8% | 8.1% | 36.8% | 3.2% | 0.0% | 0.0% | 14.3% |
| mind_version | 43.2% [26.7%, 59.6%] (Wilson 20.9%, 65.5%) | 47.0% | 34.0% | 44.9% | 19.6% | 17.2% | 27.4% | 9.8% | 0.0% | 0.0% | 21.7% |
| no_retrieval | 37.5% [22.6%, 52.6%] (Wilson 17.2%, 61.0%) | 39.6% | 35.4% | 43.9% | 23.2% | 17.5% | 31.9% | 7.4% | 0.0% | 0.0% | 5.0% |
| oracle_docs | 55.4% [36.8%, 72.3%] (Wilson 27.5%, 72.7%) | 60.5% | 45.6% | 55.4% | 10.2% | 11.2% | 24.6% | 9.8% | 0.0% | 0.0% | 17.3% |
| plain_rag | 38.6% [22.2%, 55.0%] (Wilson 16.3%, 59.7%) | 40.7% | 31.9% | 38.9% | 24.6% | 16.1% | 28.4% | 8.4% | 0.0% | 0.0% | 17.5% |
| two_branch | 53.3% [35.1%, 70.0%] (Wilson 27.3%, 72.5%) | 55.8% | 47.7% | 53.3% | 9.5% | 12.3% | 32.3% | 4.9% | 0.0% | 0.0% | 13.1% |
| va_rag | 59.6% [38.5%, 79.3%] (Wilson 34.6%, 79.3%) | 63.4% | 55.4% | 59.6% | 3.5% | 12.6% | 30.5% | 6.3% | 0.0% | 0.0% | 8.7% |
| va_rag_no_ask | 49.5% [33.3%, 64.4%] (Wilson 25.2%, 70.3%) | 50.7% | 44.6% | 49.5% | 14.7% | 12.3% | 31.9% | 3.9% | 0.0% | 0.0% | 13.5% |
| va_rag_no_guard | 54.7% [34.7%, 73.7%] (Wilson 28.3%, 73.5%) | 58.2% | 49.8% | 54.7% | 8.4% | 11.2% | 30.5% | 6.3% | 0.0% | 0.0% | 11.1% |
| va_rag_no_infer | 59.6% [38.5%, 79.3%] (Wilson 34.6%, 79.3%) | 63.4% | 55.4% | 59.6% | 3.5% | 12.6% | 30.5% | 6.3% | 0.0% | 0.0% | 8.7% |
| va_rag_portable_first | 60.4% [40.4%, 78.9%] (Wilson 33.8%, 78.6%) | 64.1% | 56.1% | 60.4% | 2.5% | 12.3% | 30.9% | 6.3% | 0.0% | 0.0% | 8.6% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

### Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 1.1% [0.0%, 3.3%] (Wilson 0.0%, 21.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 27.7% | 100.0% | 100.0% | 0.0% | c=0.0: 39.6%, c=0.1: 29.6%, c=0.3: 9.6% | 1.00 calls, 1.00 answers |
| assume_state | 0.7% [0.0%, 1.8%] (Wilson 0.0%, 21.4%) | 0.4% [0.0%, 1.1%] (Wilson 0.0%, 20.9%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 37.2%, c=0.1: 37.2%, c=0.3: 37.2% | 1.00 calls, 0.99 answers |
| mind_version | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 28.6% | 30.8% | 25.0% | 23.1% | 0.0% | c=0.0: 43.2%, c=0.1: 40.7%, c=0.3: 35.9% | 1.26 calls, 1.00 answers |
| no_retrieval | 0.7% [0.0%, 2.2%] (Wilson 0.0%, 21.4%) | 0.7% [0.0%, 2.2%] (Wilson 0.0%, 21.4%) | 0.0% | 0.0% | 0.0% | 1.7% | 15.4% | 0.0% | c=0.0: 37.5%, c=0.1: 37.2%, c=0.3: 36.6% | 1.03 calls, 1.00 answers |
| oracle_docs | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 55.4%, c=0.1: 55.4%, c=0.3: 55.4% | 1.00 calls, 1.00 answers |
| plain_rag | 0.7% [0.0%, 2.2%] (Wilson 0.0%, 21.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 38.6%, c=0.1: 38.6%, c=0.3: 38.6% | 1.00 calls, 1.00 answers |
| two_branch | 0.4% [0.0%, 1.1%] (Wilson 0.0%, 20.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 93.3% | c=0.0: 53.3%, c=0.1: 43.3%, c=0.3: 23.3% | 1.96 calls, 1.96 answers |
| va_rag | 0.4% [0.0%, 1.1%] (Wilson 0.0%, 20.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 3.3% | c=0.0: 59.6%, c=0.1: 55.3%, c=0.3: 46.7% | 1.55 calls, 1.43 answers |
| va_rag_no_ask | 0.4% [0.0%, 1.1%] (Wilson 0.0%, 20.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 49.5%, c=0.1: 49.5%, c=0.3: 49.5% | 1.07 calls, 1.00 answers |
| va_rag_no_guard | 0.4% [0.0%, 1.1%] (Wilson 0.0%, 20.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 3.3% | c=0.0: 54.7%, c=0.1: 50.4%, c=0.3: 41.8% | 1.43 calls, 1.43 answers |
| va_rag_no_infer | 0.4% [0.0%, 1.1%] (Wilson 0.0%, 20.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 28.9% | 93.3% | 100.0% | 93.3% | c=0.0: 59.6%, c=0.1: 49.6%, c=0.3: 29.6% | 2.13 calls, 1.96 answers |
| va_rag_portable_first | 0.4% [0.0%, 1.1%] (Wilson 0.0%, 20.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 65.5% | 65.5% | 0.0% | 71.8% | 0.0% | c=0.0: 60.4%, c=0.1: 57.4%, c=0.3: 51.6% | 1.64 calls, 1.27 answers |

### Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | 0.075 | n/a |
| assume_state | old 34.5%, new 26.2%, both 0.0%, neither 39.3% (n=84) | 33.3% | 0.161 | n/a |
| mind_version | old 11.7%, new 36.7%, both 0.0%, neither 51.7% (n=60) | 35.0% | 0.013 | n/a |
| no_retrieval | old 34.5%, new 2.4%, both 0.0%, neither 63.1% (n=84) | 27.2% | 0.012 | n/a |
| oracle_docs | old 31.0%, new 31.0%, both 0.0%, neither 38.1% (n=84) | 50.0% | -0.031 | n/a |
| plain_rag | old 28.6%, new 38.1%, both 0.0%, neither 33.3% (n=84) | 33.3% | -0.021 | n/a |
| two_branch | old 22.6%, new 38.1%, both 0.0%, neither 39.3% (n=84) | 48.8% | -0.037 | 44.9% |
| va_rag |  (n=0) | 57.1% | -0.020 | 52.0% |
| va_rag_no_ask | old 29.8%, new 41.7%, both 0.0%, neither 28.6% (n=84) | 57.1% | -0.084 | n/a |
| va_rag_no_guard |  (n=0) | 52.4% | -0.033 | 47.2% |
| va_rag_no_infer |  (n=0) | n/a | -0.020 | 52.6% |
| va_rag_portable_first | old 0.0%, new 0.0%, both 0.0%, neither 100.0% (n=29) | 57.1% | -0.032 | 71.3% |

### Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"both": 129, "inferred": 162, "no_conflict": 12} | n/a | 34 | 64.7% | 81.5% | 41.2% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"inferred": 162, "no_conflict": 12, "unresolved": 129} | n/a | 21 | 66.7% | 27.5% | 42.9% | 4.8% |
| va_rag_no_guard | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"both": 129, "inferred": 162, "no_conflict": 12} | n/a | 0 | n/a | 0.0% | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 101} | {"both": 291, "no_conflict": 12} | n/a | 34 | 64.7% | 81.5% | 41.2% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 13, "INFER": 54, "UNCERTAIN": 34} | {"both": 83, "inferred": 162, "no_conflict": 12, "portable": 46} | n/a | 27 | 66.7% | 85.7% | 48.1% | 0.0% |

Portable-first drafts (`va_rag_portable_first`): 129 drafts, 46 returned without a question (35.7%); rejected: {"exclusive or deprecated usage": 83}.

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
| always_ask | intended_pass | +22.9 pts | [+6.0, +41.0] | 25 / 9 | 0.0090 | 0.0542 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +17.3 pts | [+0.3, +34.0] | 26 / 9 | 0.0060 | 0.0419 |
| mind_version | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| plain_rag | intended_pass | +23.8 pts | [+6.7, +42.2] | 23 / 3 | 0.0001 | 0.0007 |
| plain_rag | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | intended_pass | +8.9 pts | [-0.0, +20.0] | 6 / 1 | 0.1250 | 0.6250 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

### Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

#### va_rag

**change_type**: behavior 35.7% (n=14); param_removed 100.0% (n=2); param_rename 46.8% (n=37); param_value 0.0% (n=7); symbol_rename 92.4% (n=35)

**clue_type**: code 60.6% (n=11); error 66.7% (n=6); pin 57.6% (n=11); pin-new+code-old 33.3% (n=6); pin-old+code-new 57.1% (n=7)

**condition**: clue 60.7% (n=28); contradiction 46.2% (n=13); no-clue 63.1% (n=28); stated 61.5% (n=26)

**exclusivity**: behavior 35.7% (n=14); deprecation 63.5% (n=21); one_directional 50.0% (n=4); removal 64.9% (n=56)

**gold_examples**: both 63.6% (n=44); neither 56.2% (n=51)

**gold_examples_x_change_type**: both / behavior 35.7% (n=14); both / param_removed 100.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 46.8% (n=37); neither / symbol_rename 81.0% (n=14)

**library**: numpy 72.9% (n=16); pandas 54.4% (n=30); pydantic 58.5% (n=49)

**target**: new 58.2% (n=51); old 61.4% (n=44)

**user_arm**: unsure 59.6% (n=95)

#### plain_rag

**change_type**: behavior 61.9% (n=14); param_removed 0.0% (n=2); param_rename 27.9% (n=37); param_value 0.0% (n=7); symbol_rename 50.5% (n=35)

**clue_type**: code 33.3% (n=11); error 38.9% (n=6); pin 54.5% (n=11); pin-new+code-old 33.3% (n=6); pin-old+code-new 23.8% (n=7)

**condition**: clue 42.9% (n=28); contradiction 28.2% (n=13); no-clue 33.3% (n=28); stated 44.9% (n=26)

**exclusivity**: behavior 61.9% (n=14); deprecation 31.7% (n=21); one_directional 0.0% (n=4); removal 38.1% (n=56)

**gold_examples**: both 42.4% (n=44); neither 35.3% (n=51)

**gold_examples_x_change_type**: both / behavior 61.9% (n=14); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 47.6% (n=21); neither / param_rename 27.9% (n=37); neither / symbol_rename 54.8% (n=14)

**library**: numpy 54.2% (n=16); pandas 43.3% (n=30); pydantic 30.6% (n=49)

**target**: new 30.7% (n=51); old 47.7% (n=44)

**user_arm**: unsure 38.6% (n=95)

#### mind_version

**change_type**: behavior 69.0% (n=14); param_removed 50.0% (n=2); param_rename 30.6% (n=37); param_value 0.0% (n=7); symbol_rename 54.3% (n=35)

**clue_type**: code 48.5% (n=11); error 33.3% (n=6); pin 63.6% (n=11); pin-new+code-old 33.3% (n=6); pin-old+code-new 19.0% (n=7)

**condition**: clue 51.2% (n=28); contradiction 25.6% (n=13); no-clue 40.5% (n=28); stated 46.2% (n=26)

**exclusivity**: behavior 69.0% (n=14); deprecation 34.9% (n=21); one_directional 25.0% (n=4); removal 41.1% (n=56)

**gold_examples**: both 47.7% (n=44); neither 39.2% (n=51)

**gold_examples_x_change_type**: both / behavior 69.0% (n=14); both / param_removed 50.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 49.2% (n=21); neither / param_rename 30.6% (n=37); neither / symbol_rename 61.9% (n=14)

**library**: numpy 60.4% (n=16); pandas 45.6% (n=30); pydantic 36.1% (n=49)

**target**: new 37.9% (n=51); old 49.2% (n=44)

**user_arm**: unsure 43.2% (n=95)

#### two_branch

**change_type**: behavior 35.7% (n=14); param_removed 33.3% (n=2); param_rename 47.7% (n=37); param_value 0.0% (n=7); symbol_rename 78.1% (n=35)

**clue_type**: code 42.4% (n=11); error 50.0% (n=6); pin 57.6% (n=11); pin-new+code-old 38.9% (n=6); pin-old+code-new 33.3% (n=7)

**condition**: clue 50.0% (n=28); contradiction 35.9% (n=13); no-clue 60.7% (n=28); stated 57.7% (n=26)

**exclusivity**: behavior 35.7% (n=14); deprecation 58.7% (n=21); one_directional 16.7% (n=4); removal 58.3% (n=56)

**gold_examples**: both 50.8% (n=44); neither 55.6% (n=51)

**gold_examples_x_change_type**: both / behavior 35.7% (n=14); both / param_removed 33.3% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 79.4% (n=21); neither / param_rename 47.7% (n=37); neither / symbol_rename 76.2% (n=14)

**library**: numpy 72.9% (n=16); pandas 35.6% (n=30); pydantic 57.8% (n=49)

**target**: new 49.7% (n=51); old 57.6% (n=44)

**user_arm**: unsure 53.3% (n=95)

#### always_ask

**change_type**: behavior 61.9% (n=14); param_removed 0.0% (n=2); param_rename 35.1% (n=37); param_value 0.0% (n=7); symbol_rename 45.7% (n=35)

**clue_type**: code 33.3% (n=11); error 33.3% (n=6); pin 60.6% (n=11); pin-new+code-old 33.3% (n=6); pin-old+code-new 19.0% (n=7)

**condition**: clue 44.0% (n=28); contradiction 25.6% (n=13); no-clue 39.3% (n=28); stated 42.3% (n=26)

**exclusivity**: behavior 61.9% (n=14); deprecation 28.6% (n=21); one_directional 0.0% (n=4); removal 41.1% (n=56)

**gold_examples**: both 42.4% (n=44); neither 37.3% (n=51)

**gold_examples_x_change_type**: both / behavior 61.9% (n=14); both / param_removed 0.0% (n=2); both / param_value 0.0% (n=7); both / symbol_rename 47.6% (n=21); neither / param_rename 35.1% (n=37); neither / symbol_rename 42.9% (n=14)

**library**: numpy 58.3% (n=16); pandas 40.0% (n=30); pydantic 33.3% (n=49)

**target**: new 34.6% (n=51); old 45.5% (n=44)

**user_arm**: unsure 39.6% (n=95)

### What size of difference this run can show

95 targeted instances over 15 concepts (6.3 per concept), 3 repeats averaged per instance. Measured within-concept correlation rho = 0.437 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.191 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.437 | 16.6 points | measured rho |
| 0.200 | 0.437 | 23.5 points | measured rho |
| 0.300 | 0.437 | 28.7 points | measured rho |
| 0.191 | 0.437 | 22.9 points | observed |
| 0.200 | 0.250 | 19.6 points | handoff assumption |
| 0.200 | 0.500 | 24.6 points | handoff assumption |

### Repeat disagreement (within this session)

1212 (instance, method) pairs answered under 3 repeats: response text differs on 54.1%, outcome on 18.3%, intended-version pass on 10.6%.

| Method | pairs | text differs | outcome differs |
| --- | --- | --- | --- |
| always_ask | 101 | 48.5% | 18.8% |
| assume_state | 101 | 81.2% | 26.7% |
| mind_version | 101 | 55.4% | 20.8% |
| no_retrieval | 101 | 33.7% | 13.9% |
| oracle_docs | 101 | 40.6% | 12.9% |
| plain_rag | 101 | 50.5% | 24.8% |
| two_branch | 101 | 67.3% | 18.8% |
| va_rag | 101 | 54.5% | 15.8% |
| va_rag_no_ask | 101 | 46.5% | 18.8% |
| va_rag_no_guard | 101 | 56.4% | 17.8% |
| va_rag_no_infer | 101 | 66.3% | 15.8% |
| va_rag_portable_first | 101 | 48.5% | 14.9% |

# test-knows

## VA-RAG run report: 20261021T093451Z-small-0143bf25

- Model: `small` = qwen/qwen-2.5-7b-instruct
- Split: test; user arm: knows; instances: 237; concepts: 57
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T10:50:43+00:00

> 57 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen-2.5-7b-instruct` pinned to provider `phala` (no fallbacks, parameters required); session `phala@20261021T082811Z`; 5484 paid calls, 4464 cache hits, $0.5253; providers reported {'Phala': 8532}
- Provider choice: qwen/qwen2.5-coder-7b-instruct had no live endpoint on 2026-10-19, so the general 7B instruct model stands in

- Repeats: every (instance, method) answered under repeat indices [0, 1, 2] in one session; an instance's score is the mean over its repeats, rates are means of instance scores, and intervals resample concepts.

### Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 37.3% [27.6%, 47.8%] (Wilson 27.6%, 54.3%) | 38.3% | 36.5% | 38.2% | 7.0% | 12.1% | 51.9% | 3.8% | 0.0% | 0.0% | 2.1% |
| assume_state | 31.1% [21.8%, 41.2%] (Wilson 23.0%, 49.0%) | 31.8% | 28.9% | 33.2% | 15.2% | 14.5% | 50.0% | 3.7% | 0.0% | 0.0% | 6.1% |
| mind_version | 28.1% [19.5%, 37.9%] (Wilson 20.3%, 45.7%) | 29.2% | 27.2% | 31.4% | 17.0% | 13.6% | 52.0% | 2.9% | 0.0% | 0.0% | 3.8% |
| no_retrieval | 26.8% [18.0%, 36.3%] (Wilson 20.3%, 45.8%) | 27.9% | 25.4% | 29.2% | 12.0% | 15.8% | 55.3% | 5.4% | 0.3% | 0.0% | 4.3% |
| oracle_docs | 39.8% [28.7%, 51.6%] (Wilson 31.4%, 58.5%) | 41.6% | 39.2% | 40.6% | 7.3% | 15.2% | 48.5% | 4.4% | 0.0% | 0.0% | 2.0% |
| plain_rag | 30.6% [21.0%, 41.0%] (Wilson 22.4%, 48.4%) | 31.8% | 28.9% | 33.8% | 16.4% | 14.9% | 48.7% | 4.4% | 0.0% | 0.0% | 5.1% |
| two_branch | 37.3% [27.6%, 47.8%] (Wilson 27.6%, 54.3%) | 38.3% | 36.5% | 38.2% | 7.0% | 12.1% | 51.9% | 3.8% | 0.0% | 0.0% | 2.1% |
| va_rag | 42.1% [31.7%, 53.1%] (Wilson 31.6%, 58.7%) | 43.2% | 41.7% | 43.0% | 3.9% | 13.6% | 51.0% | 2.8% | 0.0% | 0.0% | 0.9% |
| va_rag_no_ask | 37.3% [27.4%, 47.5%] (Wilson 27.2%, 53.9%) | 37.9% | 36.7% | 39.3% | 11.3% | 14.3% | 49.3% | 2.0% | 0.0% | 0.0% | 2.1% |
| va_rag_no_guard | 36.7% [26.8%, 47.1%] (Wilson 26.2%, 52.8%) | 37.9% | 35.8% | 37.6% | 7.9% | 11.4% | 51.5% | 3.8% | 0.0% | 0.0% | 2.1% |
| va_rag_no_infer | 42.1% [31.7%, 53.1%] (Wilson 31.6%, 58.7%) | 43.2% | 41.7% | 43.0% | 3.9% | 13.6% | 51.0% | 2.8% | 0.0% | 0.0% | 0.9% |
| va_rag_portable_first | 42.1% [32.2%, 52.4%] (Wilson 32.5%, 59.7%) | 43.2% | 41.7% | 43.0% | 3.5% | 15.8% | 51.9% | 2.3% | 0.0% | 0.0% | 0.9% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

### Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 2.5% [0.4%, 5.1%] (Wilson 0.4%, 11.0%) | 0.9% [0.0%, 2.8%] (Wilson 0.0%, 8.5%) | 0.0% | 100.0% | 34.6% | 100.0% | 100.0% | 0.0% | c=0.0: 37.3%, c=0.1: 27.3%, c=0.3: 7.3% | 1.00 calls, 1.00 answers |
| assume_state | 1.5% [0.3%, 2.9%] (Wilson 0.1%, 9.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 31.1%, c=0.1: 31.1%, c=0.3: 31.1% | 1.00 calls, 0.99 answers |
| mind_version | 3.7% [1.0%, 6.9%] (Wilson 0.6%, 12.2%) | 1.2% [0.0%, 3.3%] (Wilson 0.1%, 8.9%) | 0.0% | 32.9% | 38.0% | 27.5% | 29.4% | 0.0% | c=0.0: 28.1%, c=0.1: 25.1%, c=0.3: 19.2% | 1.30 calls, 1.00 answers |
| no_retrieval | 0.9% [0.0%, 2.6%] (Wilson 0.1%, 8.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | 0.0% | 3.3% | 8.8% | 0.0% | c=0.0: 26.8%, c=0.1: 26.4%, c=0.3: 25.8% | 1.03 calls, 0.99 answers |
| oracle_docs | 1.9% [0.3%, 4.2%] (Wilson 0.2%, 10.1%) | 0.9% [0.0%, 2.8%] (Wilson 0.0%, 8.5%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 39.8%, c=0.1: 39.8%, c=0.3: 39.8% | 1.00 calls, 1.00 answers |
| plain_rag | 1.0% [0.1%, 2.2%] (Wilson 0.1%, 8.8%) | 0.6% [0.0%, 1.7%] (Wilson 0.0%, 8.2%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 30.6%, c=0.1: 30.6%, c=0.3: 30.6% | 1.00 calls, 1.00 answers |
| two_branch | 2.5% [0.4%, 5.1%] (Wilson 0.4%, 11.0%) | 0.9% [0.0%, 2.8%] (Wilson 0.0%, 8.5%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 95.0% | c=0.0: 37.3%, c=0.1: 27.3%, c=0.3: 7.3% | 1.97 calls, 1.97 answers |
| va_rag | 0.3% [0.0%, 0.7%] (Wilson 0.0%, 7.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 68.9% | 2.5% | 100.0% | 0.0% | c=0.0: 42.1%, c=0.1: 37.0%, c=0.3: 26.8% | 1.11 calls, 1.00 answers |
| va_rag_no_ask | 0.4% [0.0%, 1.0%] (Wilson 0.0%, 8.2%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 0.0% | c=0.0: 37.3%, c=0.1: 37.3%, c=0.3: 37.3% | 1.08 calls, 1.00 answers |
| va_rag_no_guard | 1.9% [0.0%, 4.4%] (Wilson 0.2%, 10.1%) | 0.9% [0.0%, 2.8%] (Wilson 0.0%, 8.5%) | 0.0% | 100.0% | 68.9% | 2.5% | 100.0% | 0.0% | c=0.0: 36.7%, c=0.1: 31.6%, c=0.3: 21.4% | 1.00 calls, 1.00 answers |
| va_rag_no_infer | 0.3% [0.0%, 0.7%] (Wilson 0.0%, 7.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 100.0% | 35.5% | 95.0% | 100.0% | 0.0% | c=0.0: 42.1%, c=0.1: 32.1%, c=0.3: 12.1% | 1.11 calls, 1.00 answers |
| va_rag_portable_first | 0.3% [0.0%, 0.7%] (Wilson 0.0%, 7.9%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 7.4%) | 0.0% | 59.3% | 68.5% | 0.0% | 62.7% | 0.0% | c=0.0: 42.1%, c=0.1: 39.0%, c=0.3: 32.9% | 1.40 calls, 1.00 answers |

### Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | -0.039 | n/a |
| assume_state | old 17.1%, new 40.7%, both 0.4%, neither 41.9% (n=246) | 23.6% | -0.040 | n/a |
| mind_version | old 20.0%, new 50.9%, both 4.2%, neither 24.8% (n=165) | 30.0% | -0.016 | n/a |
| no_retrieval | old 28.3%, new 7.4%, both 0.8%, neither 63.5% (n=244) | 16.2% | 0.061 | n/a |
| oracle_docs | old 13.8%, new 26.8%, both 3.3%, neither 56.1% (n=246) | 40.7% | 0.014 | n/a |
| plain_rag | old 13.0%, new 39.0%, both 0.8%, neither 47.2% (n=246) | 26.8% | 0.012 | n/a |
| two_branch | old 18.3%, new 28.0%, both 2.4%, neither 51.2% (n=246) | 39.8% | -0.039 | 20.3% |
| va_rag |  (n=0) | 44.3% | 0.015 | n/a |
| va_rag_no_ask | old 14.2%, new 43.1%, both 0.0%, neither 42.7% (n=246) | 44.3% | 0.051 | n/a |
| va_rag_no_guard |  (n=0) | 39.8% | -0.029 | n/a |
| va_rag_no_infer |  (n=0) | n/a | 0.015 | n/a |
| va_rag_portable_first | old 0.0%, new 0.0%, both 0.0%, neither 100.0% (n=100) | 44.3% | 0.063 | n/a |

### Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"asked": 357, "inferred": 336, "no_conflict": 18} | n/a | 77 | 31.2% | 55.8% | 48.1% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"inferred": 336, "no_conflict": 18, "unresolved": 357} | n/a | 54 | 33.3% | 24.0% | 48.1% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"asked": 357, "inferred": 336, "no_conflict": 18} | n/a | 0 | n/a | 0.0% | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 237} | {"asked": 693, "no_conflict": 18} | n/a | 77 | 31.2% | 55.8% | 48.1% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"asked": 210, "inferred": 336, "no_conflict": 18, "portable": 147} | n/a | 73 | 31.5% | 54.8% | 50.7% | 0.0% |

Portable-first drafts (`va_rag_portable_first`): 357 drafts, 147 returned without a question (41.2%); rejected: {"exclusive or deprecated usage": 203, "no code": 7}.

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
| always_ask | intended_pass | +4.5 pts | [+0.1, +9.0] | 13 / 3 | 0.0213 | 0.1276 |
| always_ask | blend_exec | -0.6 pts | [-1.8, +0.0] | 0 / 2 | 0.5000 | 1.0000 |
| mind_version | intended_pass | +13.1 pts | [+5.1, +21.4] | 44 / 18 | 0.0013 | 0.0104 |
| mind_version | blend_exec | -0.9 pts | [-2.4, +0.0] | 0 / 2 | 0.5000 | 1.0000 |
| plain_rag | intended_pass | +10.5 pts | [+3.4, +17.9] | 39 / 15 | 0.0015 | 0.0105 |
| plain_rag | blend_exec | -0.4 pts | [-1.2, +0.0] | 0 / 2 | 0.5000 | 1.0000 |
| two_branch | intended_pass | +4.5 pts | [+0.1, +9.0] | 13 / 3 | 0.0213 | 0.1276 |
| two_branch | blend_exec | -0.6 pts | [-1.8, +0.0] | 0 / 2 | 0.5000 | 1.0000 |

### Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

#### va_rag

**change_type**: behavior 38.0% (n=36); moved_import 0.0% (n=5); param_removed 16.7% (n=2); param_rename 41.4% (n=62); param_value 44.4% (n=30); symbol_removed 50.0% (n=14); symbol_rename 45.6% (n=79)

**clue_type**: code 50.6% (n=29); error 33.3% (n=23); pin 46.7% (n=30); pin-new+code-old 31.8% (n=22); pin-old+code-new 44.4% (n=12)

**condition**: clue 44.3% (n=82); contradiction 36.3% (n=34); no-clue 40.7% (n=82); stated 46.7% (n=30)

**exclusivity**: behavior 38.0% (n=36); deprecation 41.2% (n=68); one_directional 58.3% (n=28); removal 39.6% (n=96)

**gold_examples**: both 45.8% (n=51); neither 41.1% (n=177)

**gold_examples_x_change_type**: both / behavior 33.3% (n=21); both / symbol_removed 50.0% (n=6); both / symbol_rename 55.6% (n=24); neither / behavior 44.4% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 16.7% (n=2); neither / param_rename 41.4% (n=62); neither / param_value 44.4% (n=30); neither / symbol_removed 50.0% (n=8); neither / symbol_rename 41.2% (n=55)

**library**: numpy 58.1% (n=35); pandas 43.5% (n=62); pydantic 37.2% (n=131)

**target**: new 45.7% (n=124); old 37.8% (n=104)

**user_arm**: knows 42.1% (n=228)

#### plain_rag

**change_type**: behavior 41.7% (n=36); moved_import 0.0% (n=5); param_removed 50.0% (n=2); param_rename 26.9% (n=62); param_value 25.6% (n=30); symbol_removed 47.6% (n=14); symbol_rename 28.7% (n=79)

**clue_type**: code 28.7% (n=29); error 30.4% (n=23); pin 36.7% (n=30); pin-new+code-old 33.3% (n=22); pin-old+code-new 25.0% (n=12)

**condition**: clue 32.1% (n=82); contradiction 30.4% (n=34); no-clue 28.0% (n=82); stated 33.3% (n=30)

**exclusivity**: behavior 41.7% (n=36); deprecation 26.0% (n=68); one_directional 52.4% (n=28); removal 23.3% (n=96)

**gold_examples**: both 27.5% (n=51); neither 31.5% (n=177)

**gold_examples_x_change_type**: both / behavior 33.3% (n=21); both / symbol_removed 33.3% (n=6); both / symbol_rename 20.8% (n=24); neither / behavior 53.3% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 50.0% (n=2); neither / param_rename 26.9% (n=62); neither / param_value 25.6% (n=30); neither / symbol_removed 58.3% (n=8); neither / symbol_rename 32.1% (n=55)

**library**: numpy 50.5% (n=35); pandas 37.6% (n=62); pydantic 21.9% (n=131)

**target**: new 32.8% (n=124); old 27.9% (n=104)

**user_arm**: knows 30.6% (n=228)

#### mind_version

**change_type**: behavior 37.0% (n=36); moved_import 0.0% (n=5); param_removed 50.0% (n=2); param_rename 25.3% (n=62); param_value 23.3% (n=30); symbol_removed 40.5% (n=14); symbol_rename 27.0% (n=79)

**clue_type**: code 26.4% (n=29); error 20.3% (n=23); pin 35.6% (n=30); pin-new+code-old 24.2% (n=22); pin-old+code-new 30.6% (n=12)

**condition**: clue 28.0% (n=82); contradiction 26.5% (n=34); no-clue 26.8% (n=82); stated 33.3% (n=30)

**exclusivity**: behavior 37.0% (n=36); deprecation 24.0% (n=68); one_directional 48.8% (n=28); removal 21.5% (n=96)

**gold_examples**: both 24.8% (n=51); neither 29.0% (n=177)

**gold_examples_x_change_type**: both / behavior 34.9% (n=21); both / symbol_removed 22.2% (n=6); both / symbol_rename 16.7% (n=24); neither / behavior 40.0% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 50.0% (n=2); neither / param_rename 25.3% (n=62); neither / param_value 23.3% (n=30); neither / symbol_removed 54.2% (n=8); neither / symbol_rename 31.5% (n=55)

**library**: numpy 40.0% (n=35); pandas 36.6% (n=62); pydantic 20.9% (n=131)

**target**: new 29.8% (n=124); old 26.0% (n=104)

**user_arm**: knows 28.1% (n=228)

#### two_branch

**change_type**: behavior 38.9% (n=36); moved_import 0.0% (n=5); param_removed 33.3% (n=2); param_rename 33.3% (n=62); param_value 30.0% (n=30); symbol_removed 50.0% (n=14); symbol_rename 42.6% (n=79)

**clue_type**: code 44.8% (n=29); error 27.5% (n=23); pin 44.4% (n=30); pin-new+code-old 36.4% (n=22); pin-old+code-new 41.7% (n=12)

**condition**: clue 39.8% (n=82); contradiction 38.2% (n=34); no-clue 36.2% (n=82); stated 32.2% (n=30)

**exclusivity**: behavior 38.9% (n=36); deprecation 40.7% (n=68); one_directional 53.6% (n=28); removal 29.5% (n=96)

**gold_examples**: both 43.8% (n=51); neither 35.4% (n=177)

**gold_examples_x_change_type**: both / behavior 33.3% (n=21); both / symbol_removed 33.3% (n=6); both / symbol_rename 55.6% (n=24); neither / behavior 46.7% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 33.3% (n=2); neither / param_rename 33.3% (n=62); neither / param_value 30.0% (n=30); neither / symbol_removed 62.5% (n=8); neither / symbol_rename 37.0% (n=55)

**library**: numpy 51.4% (n=35); pandas 38.2% (n=62); pydantic 33.1% (n=131)

**target**: new 39.2% (n=124); old 34.9% (n=104)

**user_arm**: knows 37.3% (n=228)

#### always_ask

**change_type**: behavior 38.9% (n=36); moved_import 0.0% (n=5); param_removed 33.3% (n=2); param_rename 33.3% (n=62); param_value 30.0% (n=30); symbol_removed 50.0% (n=14); symbol_rename 42.6% (n=79)

**clue_type**: code 44.8% (n=29); error 27.5% (n=23); pin 44.4% (n=30); pin-new+code-old 36.4% (n=22); pin-old+code-new 41.7% (n=12)

**condition**: clue 39.8% (n=82); contradiction 38.2% (n=34); no-clue 36.2% (n=82); stated 32.2% (n=30)

**exclusivity**: behavior 38.9% (n=36); deprecation 40.7% (n=68); one_directional 53.6% (n=28); removal 29.5% (n=96)

**gold_examples**: both 43.8% (n=51); neither 35.4% (n=177)

**gold_examples_x_change_type**: both / behavior 33.3% (n=21); both / symbol_removed 33.3% (n=6); both / symbol_rename 55.6% (n=24); neither / behavior 46.7% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 33.3% (n=2); neither / param_rename 33.3% (n=62); neither / param_value 30.0% (n=30); neither / symbol_removed 62.5% (n=8); neither / symbol_rename 37.0% (n=55)

**library**: numpy 51.4% (n=35); pandas 38.2% (n=62); pydantic 33.1% (n=131)

**target**: new 39.2% (n=124); old 34.9% (n=104)

**user_arm**: knows 37.3% (n=228)

### What size of difference this run can show

228 targeted instances over 48 concepts (4.8 per concept), 3 repeats averaged per instance. Measured within-concept correlation rho = 0.447 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.118 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.447 | 9.6 points | measured rho |
| 0.200 | 0.447 | 13.6 points | measured rho |
| 0.300 | 0.447 | 16.6 points | measured rho |
| 0.118 | 0.447 | 10.4 points | observed |
| 0.200 | 0.250 | 11.5 points | handoff assumption |
| 0.200 | 0.500 | 14.1 points | handoff assumption |

### Repeat disagreement (within this session)

2844 (instance, method) pairs answered under 3 repeats: response text differs on 55.2%, outcome on 15.3%, intended-version pass on 10.1%.

| Method | pairs | text differs | outcome differs |
| --- | --- | --- | --- |
| always_ask | 237 | 52.3% | 14.3% |
| assume_state | 237 | 70.5% | 19.4% |
| mind_version | 237 | 50.6% | 16.9% |
| no_retrieval | 237 | 48.9% | 13.1% |
| oracle_docs | 237 | 49.4% | 12.2% |
| plain_rag | 237 | 50.6% | 16.0% |
| two_branch | 237 | 72.6% | 15.6% |
| va_rag | 237 | 53.2% | 15.2% |
| va_rag_no_ask | 237 | 51.9% | 13.9% |
| va_rag_no_guard | 237 | 53.2% | 15.6% |
| va_rag_no_infer | 237 | 53.2% | 15.2% |
| va_rag_portable_first | 237 | 56.5% | 16.5% |

# test-unsure

## VA-RAG run report: 20261021T105119Z-small-6168007f

- Model: `small` = qwen/qwen-2.5-7b-instruct
- Split: test; user arm: unsure; instances: 237; concepts: 57
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T11:15:13+00:00

> 57 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

- OpenRouter: `qwen/qwen-2.5-7b-instruct` pinned to provider `phala` (no fallbacks, parameters required); session `phala@20261021T082811Z`; 735 paid calls, 10955 cache hits, $0.0823; providers reported {'Phala': 8532}
- Provider choice: qwen/qwen2.5-coder-7b-instruct had no live endpoint on 2026-10-19, so the general 7B instruct model stands in

- Repeats: every (instance, method) answered under repeat indices [0, 1, 2] in one session; an instance's score is the mean over its repeats, rates are means of instance scores, and intervals resample concepts.

### Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 30.7% [21.3%, 40.9%] (Wilson 22.7%, 48.7%) | 31.3% | 28.7% | 34.1% | 17.5% | 13.9% | 49.7% | 2.0% | 0.0% | 0.0% | 7.6% |
| assume_state | 31.1% [21.8%, 41.2%] (Wilson 23.0%, 49.0%) | 31.8% | 28.9% | 33.2% | 15.2% | 14.5% | 50.0% | 3.7% | 0.0% | 0.0% | 6.1% |
| mind_version | 27.8% [19.1%, 37.7%] (Wilson 20.4%, 45.8%) | 28.7% | 26.9% | 31.1% | 17.4% | 14.6% | 51.9% | 2.8% | 0.0% | 0.0% | 3.8% |
| no_retrieval | 27.0% [18.4%, 36.5%] (Wilson 20.6%, 46.1%) | 28.2% | 25.7% | 29.5% | 12.0% | 15.9% | 55.0% | 5.4% | 0.3% | 0.0% | 4.3% |
| oracle_docs | 39.8% [28.7%, 51.6%] (Wilson 31.4%, 58.5%) | 41.6% | 39.2% | 40.6% | 7.3% | 15.2% | 48.5% | 4.4% | 0.0% | 0.0% | 2.0% |
| plain_rag | 30.6% [21.0%, 41.0%] (Wilson 22.4%, 48.4%) | 31.8% | 28.9% | 33.8% | 16.4% | 14.9% | 48.7% | 4.4% | 0.0% | 0.0% | 5.1% |
| two_branch | 37.3% [27.6%, 47.8%] (Wilson 27.6%, 54.3%) | 38.3% | 36.5% | 38.2% | 7.0% | 12.1% | 51.9% | 3.8% | 0.0% | 0.0% | 2.1% |
| va_rag | 42.1% [31.7%, 53.1%] (Wilson 31.6%, 58.7%) | 43.2% | 41.7% | 43.0% | 3.9% | 13.6% | 51.0% | 2.8% | 0.0% | 0.0% | 0.9% |
| va_rag_no_ask | 37.3% [27.4%, 47.5%] (Wilson 27.2%, 53.9%) | 37.9% | 36.7% | 39.3% | 11.3% | 14.3% | 49.3% | 2.0% | 0.0% | 0.0% | 2.1% |
| va_rag_no_guard | 36.7% [26.8%, 47.1%] (Wilson 26.2%, 52.8%) | 37.9% | 35.8% | 37.6% | 7.9% | 11.4% | 51.5% | 3.8% | 0.0% | 0.0% | 2.1% |
| va_rag_no_infer | 42.1% [31.7%, 53.1%] (Wilson 31.6%, 58.7%) | 43.2% | 41.7% | 43.0% | 3.9% | 13.6% | 51.0% | 2.8% | 0.0% | 0.0% | 0.9% |
| va_rag_portable_first | 42.1% [32.2%, 52.4%] (Wilson 32.5%, 59.7%) | 43.2% | 41.7% | 43.0% | 3.5% | 15.8% | 51.9% | 2.3% | 0.0% | 0.0% | 0.9% |

> `oracle_docs` gives target-version documents with no version statement and no guard, so it is not an upper bound for `va_rag`.

### Blending, asking, hedging, cost

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

### Commit direction, clue following, order

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

### Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"both": 357, "inferred": 336, "no_conflict": 18} | n/a | 77 | 31.2% | 55.8% | 48.1% | 0.0% |
| va_rag_no_ask | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"inferred": 336, "no_conflict": 18, "unresolved": 357} | n/a | 54 | 33.3% | 24.0% | 48.1% | 0.0% |
| va_rag_no_guard | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"both": 357, "inferred": 336, "no_conflict": 18} | n/a | 0 | n/a | 0.0% | n/a | n/a |
| va_rag_no_infer | n/a | 0.0% | {"UNCERTAIN": 237} | {"both": 693, "no_conflict": 18} | n/a | 77 | 31.2% | 55.8% | 48.1% | 0.0% |
| va_rag_portable_first | 100.0% | 100.0% | {"CONTEXT_CONFLICT": 34, "INFER": 112, "UNCERTAIN": 91} | {"both": 210, "inferred": 336, "no_conflict": 18, "portable": 147} | n/a | 73 | 31.5% | 54.8% | 50.7% | 0.0% |

Portable-first drafts (`va_rag_portable_first`): 357 drafts, 147 returned without a question (41.2%); rejected: {"exclusive or deprecated usage": 203, "no code": 7}.

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
| always_ask | intended_pass | +10.2 pts | [+2.1, +17.9] | 40 / 17 | 0.0032 | 0.0192 |
| always_ask | blend_exec | -0.3 pts | [-0.9, +0.0] | 0 / 1 | 1.0000 | 1.0000 |
| mind_version | intended_pass | +13.0 pts | [+4.3, +22.0] | 47 / 20 | 0.0013 | 0.0105 |
| mind_version | blend_exec | -0.6 pts | [-1.8, +0.0] | 0 / 2 | 0.5000 | 1.0000 |
| plain_rag | intended_pass | +10.5 pts | [+3.4, +17.9] | 39 / 15 | 0.0015 | 0.0105 |
| plain_rag | blend_exec | -0.4 pts | [-1.2, +0.0] | 0 / 2 | 0.5000 | 1.0000 |
| two_branch | intended_pass | +4.5 pts | [+0.1, +9.0] | 13 / 3 | 0.0213 | 0.1064 |
| two_branch | blend_exec | -0.6 pts | [-1.8, +0.0] | 0 / 2 | 0.5000 | 1.0000 |

### Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

#### va_rag

**change_type**: behavior 38.0% (n=36); moved_import 0.0% (n=5); param_removed 16.7% (n=2); param_rename 41.4% (n=62); param_value 44.4% (n=30); symbol_removed 50.0% (n=14); symbol_rename 45.6% (n=79)

**clue_type**: code 50.6% (n=29); error 33.3% (n=23); pin 46.7% (n=30); pin-new+code-old 31.8% (n=22); pin-old+code-new 44.4% (n=12)

**condition**: clue 44.3% (n=82); contradiction 36.3% (n=34); no-clue 40.7% (n=82); stated 46.7% (n=30)

**exclusivity**: behavior 38.0% (n=36); deprecation 41.2% (n=68); one_directional 58.3% (n=28); removal 39.6% (n=96)

**gold_examples**: both 45.8% (n=51); neither 41.1% (n=177)

**gold_examples_x_change_type**: both / behavior 33.3% (n=21); both / symbol_removed 50.0% (n=6); both / symbol_rename 55.6% (n=24); neither / behavior 44.4% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 16.7% (n=2); neither / param_rename 41.4% (n=62); neither / param_value 44.4% (n=30); neither / symbol_removed 50.0% (n=8); neither / symbol_rename 41.2% (n=55)

**library**: numpy 58.1% (n=35); pandas 43.5% (n=62); pydantic 37.2% (n=131)

**target**: new 45.7% (n=124); old 37.8% (n=104)

**user_arm**: unsure 42.1% (n=228)

#### plain_rag

**change_type**: behavior 41.7% (n=36); moved_import 0.0% (n=5); param_removed 50.0% (n=2); param_rename 26.9% (n=62); param_value 25.6% (n=30); symbol_removed 47.6% (n=14); symbol_rename 28.7% (n=79)

**clue_type**: code 28.7% (n=29); error 30.4% (n=23); pin 36.7% (n=30); pin-new+code-old 33.3% (n=22); pin-old+code-new 25.0% (n=12)

**condition**: clue 32.1% (n=82); contradiction 30.4% (n=34); no-clue 28.0% (n=82); stated 33.3% (n=30)

**exclusivity**: behavior 41.7% (n=36); deprecation 26.0% (n=68); one_directional 52.4% (n=28); removal 23.3% (n=96)

**gold_examples**: both 27.5% (n=51); neither 31.5% (n=177)

**gold_examples_x_change_type**: both / behavior 33.3% (n=21); both / symbol_removed 33.3% (n=6); both / symbol_rename 20.8% (n=24); neither / behavior 53.3% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 50.0% (n=2); neither / param_rename 26.9% (n=62); neither / param_value 25.6% (n=30); neither / symbol_removed 58.3% (n=8); neither / symbol_rename 32.1% (n=55)

**library**: numpy 50.5% (n=35); pandas 37.6% (n=62); pydantic 21.9% (n=131)

**target**: new 32.8% (n=124); old 27.9% (n=104)

**user_arm**: unsure 30.6% (n=228)

#### mind_version

**change_type**: behavior 36.1% (n=36); moved_import 0.0% (n=5); param_removed 50.0% (n=2); param_rename 26.3% (n=62); param_value 23.3% (n=30); symbol_removed 40.5% (n=14); symbol_rename 25.7% (n=79)

**clue_type**: code 21.8% (n=29); error 20.3% (n=23); pin 37.8% (n=30); pin-new+code-old 18.2% (n=22); pin-old+code-new 27.8% (n=12)

**condition**: clue 27.2% (n=82); contradiction 21.6% (n=34); no-clue 28.9% (n=82); stated 33.3% (n=30)

**exclusivity**: behavior 36.1% (n=36); deprecation 22.5% (n=68); one_directional 52.4% (n=28); removal 21.2% (n=96)

**gold_examples**: both 28.1% (n=51); neither 27.7% (n=177)

**gold_examples_x_change_type**: both / behavior 41.3% (n=21); both / symbol_removed 33.3% (n=6); both / symbol_rename 15.3% (n=24); neither / behavior 28.9% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 50.0% (n=2); neither / param_rename 26.3% (n=62); neither / param_value 23.3% (n=30); neither / symbol_removed 45.8% (n=8); neither / symbol_rename 30.3% (n=55)

**library**: numpy 45.7% (n=35); pandas 35.5% (n=62); pydantic 19.3% (n=131)

**target**: new 29.3% (n=124); old 26.0% (n=104)

**user_arm**: unsure 27.8% (n=228)

#### two_branch

**change_type**: behavior 38.9% (n=36); moved_import 0.0% (n=5); param_removed 33.3% (n=2); param_rename 33.3% (n=62); param_value 30.0% (n=30); symbol_removed 50.0% (n=14); symbol_rename 42.6% (n=79)

**clue_type**: code 44.8% (n=29); error 27.5% (n=23); pin 44.4% (n=30); pin-new+code-old 36.4% (n=22); pin-old+code-new 41.7% (n=12)

**condition**: clue 39.8% (n=82); contradiction 38.2% (n=34); no-clue 36.2% (n=82); stated 32.2% (n=30)

**exclusivity**: behavior 38.9% (n=36); deprecation 40.7% (n=68); one_directional 53.6% (n=28); removal 29.5% (n=96)

**gold_examples**: both 43.8% (n=51); neither 35.4% (n=177)

**gold_examples_x_change_type**: both / behavior 33.3% (n=21); both / symbol_removed 33.3% (n=6); both / symbol_rename 55.6% (n=24); neither / behavior 46.7% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 33.3% (n=2); neither / param_rename 33.3% (n=62); neither / param_value 30.0% (n=30); neither / symbol_removed 62.5% (n=8); neither / symbol_rename 37.0% (n=55)

**library**: numpy 51.4% (n=35); pandas 38.2% (n=62); pydantic 33.1% (n=131)

**target**: new 39.2% (n=124); old 34.9% (n=104)

**user_arm**: unsure 37.3% (n=228)

#### always_ask

**change_type**: behavior 39.8% (n=36); moved_import 0.0% (n=5); param_removed 50.0% (n=2); param_rename 31.2% (n=62); param_value 21.1% (n=30); symbol_removed 50.0% (n=14); symbol_rename 27.8% (n=79)

**clue_type**: code 26.4% (n=29); error 27.5% (n=23); pin 36.7% (n=30); pin-new+code-old 28.8% (n=22); pin-old+code-new 25.0% (n=12)

**condition**: clue 30.5% (n=82); contradiction 27.5% (n=34); no-clue 30.9% (n=82); stated 34.4% (n=30)

**exclusivity**: behavior 39.8% (n=36); deprecation 25.0% (n=68); one_directional 53.6% (n=28); removal 24.7% (n=96)

**gold_examples**: both 24.2% (n=51); neither 32.6% (n=177)

**gold_examples_x_change_type**: both / behavior 33.3% (n=21); both / symbol_removed 16.7% (n=6); both / symbol_rename 18.1% (n=24); neither / behavior 48.9% (n=15); neither / moved_import 0.0% (n=5); neither / param_removed 50.0% (n=2); neither / param_rename 31.2% (n=62); neither / param_value 21.1% (n=30); neither / symbol_removed 75.0% (n=8); neither / symbol_rename 32.1% (n=55)

**library**: numpy 51.4% (n=35); pandas 34.9% (n=62); pydantic 23.2% (n=131)

**target**: new 34.9% (n=124); old 25.6% (n=104)

**user_arm**: unsure 30.7% (n=228)

### What size of difference this run can show

228 targeted instances over 48 concepts (4.8 per concept), 3 repeats averaged per instance. Measured within-concept correlation rho = 0.452 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.133 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.452 | 9.6 points | measured rho |
| 0.200 | 0.452 | 13.6 points | measured rho |
| 0.300 | 0.452 | 16.7 points | measured rho |
| 0.133 | 0.452 | 11.1 points | observed |
| 0.200 | 0.250 | 11.5 points | handoff assumption |
| 0.200 | 0.500 | 14.1 points | handoff assumption |

### Repeat disagreement (within this session)

2844 (instance, method) pairs answered under 3 repeats: response text differs on 59.0%, outcome on 15.4%, intended-version pass on 10.0%.

| Method | pairs | text differs | outcome differs |
| --- | --- | --- | --- |
| always_ask | 237 | 52.7% | 11.4% |
| assume_state | 237 | 70.5% | 19.4% |
| mind_version | 237 | 54.9% | 20.3% |
| no_retrieval | 237 | 48.9% | 13.1% |
| oracle_docs | 237 | 49.4% | 12.2% |
| plain_rag | 237 | 50.6% | 16.0% |
| two_branch | 237 | 72.6% | 15.6% |
| va_rag | 237 | 62.0% | 15.2% |
| va_rag_no_ask | 237 | 51.9% | 13.9% |
| va_rag_no_guard | 237 | 62.0% | 15.6% |
| va_rag_no_infer | 237 | 72.6% | 15.2% |
| va_rag_portable_first | 237 | 60.3% | 16.5% |
