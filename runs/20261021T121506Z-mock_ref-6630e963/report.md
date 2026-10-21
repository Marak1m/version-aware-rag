# VA-RAG run report: 20261021T121506Z-mock_ref-6630e963

- Model: `mock_ref` = mock
- Split: dev; user arm: unsure; instances: 101; concepts: 21
- Scoring of deprecation concepts: primary strict (both reported)
- Commit ccf69f806818, config 34f9629df5fa, created 2026-10-21T12:15:40+00:00

> 21 concepts: below the 60-concept benchmark, so method comparisons here are smoke-test readings, not results.

## Primary metrics

| Method | Intended-version pass (bootstrap, Wilson) | pass among answers defining the entry point | strict | lenient | wrong_version | portable | broken | no_entry_point | no_code | second question | soft-fail |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 100.0% [100.0%, 100.0%] (Wilson 79.6%, 100.0%) | 100.0% | 100.0% | 100.0% | 0.0% | 4.2% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| two_branch | 100.0% [100.0%, 100.0%] (Wilson 79.6%, 100.0%) | 100.0% | 100.0% | 100.0% | 0.0% | 4.2% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| va_rag | 100.0% [100.0%, 100.0%] (Wilson 79.6%, 100.0%) | 100.0% | 100.0% | 100.0% | 0.0% | 4.2% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |

## Blending, asking, hedging, cost

| Method | blend_static | blend_exec | guarded_portable | ask recall | ask precision | over-ask | ask on contradiction | over-hedge | utility | cost / instance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| always_ask | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 27.7% | 100.0% | 100.0% | 0.0% | c=0.0: 100.0%, c=0.1: 90.0%, c=0.3: 70.0% | 1.00 calls, 1.00 answers |
| two_branch | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 0.0% | n/a | 0.0% | 0.0% | 93.3% | c=0.0: 100.0%, c=0.1: 90.0%, c=0.3: 70.0% | 1.96 calls, 1.96 answers |
| va_rag | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% [0.0%, 0.0%] (Wilson 0.0%, 20.4%) | 0.0% | 100.0% | 65.1% | 3.3% | 100.0% | 3.3% | c=0.0: 100.0%, c=0.1: 95.7%, c=0.3: 87.1% | 1.43 calls, 1.43 answers |

## Commit direction, clue following, order

| Method | silent commits on no-clue instances | clue following | order sensitivity (first - last) | both_correct |
| --- | --- | --- | --- | --- |
| always_ask |  (n=0) | n/a | 0.000 | n/a |
| two_branch | old 25.0%, new 46.4%, both 0.0%, neither 28.6% (n=28) | 71.4% | 0.000 | 100.0% |
| va_rag |  (n=0) | 71.4% | 0.000 | 100.0% |

## Inference and guard (VA-RAG family)

| Method | inference precision | coverage on clue instances | decisions | answered by (answers) | AUROC |margin| | guard flags (answers) | guard precision | guard recall | fix rate | harm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| va_rag | 100.0% | 100.0% | {"UNCERTAIN": 34, "INFER": 54, "CONTEXT_CONFLICT": 13} | {"no_conflict": 4, "both": 43, "inferred": 54} | n/a | 0 | n/a | n/a | n/a | n/a |

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
| two_branch | intended_pass | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| two_branch | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | intended_pass | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |
| always_ask | blend_exec | +0.0 pts | [+0.0, +0.0] | 0 / 0 | 1.0000 | 1.0000 |

## Slices

Intended-version pass by slice, for va_rag and the primary baselines. gold_examples and change_type overlap (every keyword-level concept is `neither`), so they are read together in the cross-table.

### va_rag

**library**: numpy 100.0% (n=16); pandas 100.0% (n=30); pydantic 100.0% (n=49)

**target**: new 100.0% (n=51); old 100.0% (n=44)

**condition**: clue 100.0% (n=28); contradiction 100.0% (n=13); no-clue 100.0% (n=28); stated 100.0% (n=26)

**clue_type**: code 100.0% (n=11); error 100.0% (n=6); pin 100.0% (n=11); pin-new+code-old 100.0% (n=6); pin-old+code-new 100.0% (n=7)

**exclusivity**: behavior 100.0% (n=14); deprecation 100.0% (n=21); one_directional 100.0% (n=4); removal 100.0% (n=56)

**change_type**: behavior 100.0% (n=14); param_removed 100.0% (n=2); param_rename 100.0% (n=37); param_value 100.0% (n=7); symbol_rename 100.0% (n=35)

**user_arm**: unsure 100.0% (n=95)

**gold_examples**: both 100.0% (n=44); neither 100.0% (n=51)

**gold_examples_x_change_type**: both / behavior 100.0% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 100.0% (n=37); neither / symbol_rename 100.0% (n=14)

### two_branch

**library**: numpy 100.0% (n=16); pandas 100.0% (n=30); pydantic 100.0% (n=49)

**target**: new 100.0% (n=51); old 100.0% (n=44)

**condition**: clue 100.0% (n=28); contradiction 100.0% (n=13); no-clue 100.0% (n=28); stated 100.0% (n=26)

**clue_type**: code 100.0% (n=11); error 100.0% (n=6); pin 100.0% (n=11); pin-new+code-old 100.0% (n=6); pin-old+code-new 100.0% (n=7)

**exclusivity**: behavior 100.0% (n=14); deprecation 100.0% (n=21); one_directional 100.0% (n=4); removal 100.0% (n=56)

**change_type**: behavior 100.0% (n=14); param_removed 100.0% (n=2); param_rename 100.0% (n=37); param_value 100.0% (n=7); symbol_rename 100.0% (n=35)

**user_arm**: unsure 100.0% (n=95)

**gold_examples**: both 100.0% (n=44); neither 100.0% (n=51)

**gold_examples_x_change_type**: both / behavior 100.0% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 100.0% (n=37); neither / symbol_rename 100.0% (n=14)

### always_ask

**library**: numpy 100.0% (n=16); pandas 100.0% (n=30); pydantic 100.0% (n=49)

**target**: new 100.0% (n=51); old 100.0% (n=44)

**condition**: clue 100.0% (n=28); contradiction 100.0% (n=13); no-clue 100.0% (n=28); stated 100.0% (n=26)

**clue_type**: code 100.0% (n=11); error 100.0% (n=6); pin 100.0% (n=11); pin-new+code-old 100.0% (n=6); pin-old+code-new 100.0% (n=7)

**exclusivity**: behavior 100.0% (n=14); deprecation 100.0% (n=21); one_directional 100.0% (n=4); removal 100.0% (n=56)

**change_type**: behavior 100.0% (n=14); param_removed 100.0% (n=2); param_rename 100.0% (n=37); param_value 100.0% (n=7); symbol_rename 100.0% (n=35)

**user_arm**: unsure 100.0% (n=95)

**gold_examples**: both 100.0% (n=44); neither 100.0% (n=51)

**gold_examples_x_change_type**: both / behavior 100.0% (n=14); both / param_removed 100.0% (n=2); both / param_value 100.0% (n=7); both / symbol_rename 100.0% (n=21); neither / param_rename 100.0% (n=37); neither / symbol_rename 100.0% (n=14)

## What size of difference this run can show

95 targeted instances over 15 concepts (6.3 per concept). Measured within-concept correlation rho = 0.000 (ICC of instance scores, mean over methods); observed discordance against va_rag = 0.000 (mean squared difference of paired instance scores). Miller's formula at 80% power, two-sided 5%:

| discordance | rho | detectable difference | basis |
| --- | --- | --- | --- |
| 0.100 | 0.000 | 9.1 points | measured rho |
| 0.200 | 0.000 | 12.9 points | measured rho |
| 0.300 | 0.000 | 15.7 points | measured rho |
| 0.200 | 0.250 | 19.6 points | handoff assumption |
| 0.200 | 0.500 | 24.6 points | handoff assumption |
