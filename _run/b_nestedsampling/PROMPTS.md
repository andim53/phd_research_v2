# PROMPTS — Project b_nestedsampling prompt log + grammar concept system

This file logs every prompt the owner adds for future work, each marked with a
**flag code** (`YYYYMMDD_HHMM`, local time) and cleaned into a consistent grammar.
Newer prompts sit **above** older ones. See `AGENTS.md` §3b for the full rules.

> Scaffold created on project setup (2026-08-26). Prompts are logged below; new
> entries get a `# FLAG: <YYYYMMDD_HHMM>` heading with the two grammar blocks and
> any fixes folded into the shared `## Grammar notes`.

# FLAG: 20260827_0041

## Original (before grammar fix)

```
Add an additional Analysist. I want to check the accuracy+uncertainty across different delta Fe_z (distance between the highest Fe z axist height minus the lowest Fe z axist height, i.e., the Fe island height). 
```

## Fixed grammar (after)

```
Add an additional analysis. I want to check the accuracy + uncertainty across
different delta Fe_z (the Fe island height: the distance between the highest Fe
z-axis height and the lowest Fe z-axis height).
```

## Grammar notes

Generalized concepts for grammar fixes across prompts. When a prompt is added, its
fixes are folded into these existing concepts (adding a new one only if the mistake
is genuinely new).

1. **Formatting that breaks machine-readable content** — paths/identifiers split
   mid-token by line wraps. Paths and filenames must stay on one line and be kept
   intact (e.g. `/home/thin k/...` and `It' s` from the 20260826_2333 prompt).
2. **Incomplete clauses** — an instruction missing its verb, object, or noun (e.g.
   "the accuracy ... of the GPR model under different energy range" → add the
   missing plural object "energy ranges").
3. **Non-idiomatic phrasing** — unnatural preposition/filler around common actions
   (e.g. "the accuracy (use MAE...)" → "the accuracy (using MAE...)"; "add an
   additional Analysist" → "add an additional analysis" from the 20260827_0041
   prompt).
4. **Redundant / misplaced comma** — a comma splitting a verb from its object or
   breaking the flow (e.g. "analysis, showing the uncertainty" → "analysis showing
   the uncertainty" from the 20260826_2354 prompt).
5. **Misspelling / dangling punctuation** — a misspelled word ("ratteling" →
   "rattling") and a trailing comma/dangling clause with no following verb (the
   trailing `,` on the 20260827_0024 prompt).
6. **Terminology / clarity** — a term used loosely that should be pinned to its
   precise definition (e.g. "Fe z axist" → "Fe z-axis"; reordering the delta Fe_z
   definition so "Fe island height" leads, from the 20260827_0041 prompt).

# FLAG: 20260827_0024

## Original (before grammar fix)

```
Include an analysis of different ratteling distances (take the structure from the database, then rattled them, then predict its energy) vs the GPR performance (accuracy and uncertainty), 
```

## Fixed grammar (after)

```
Include an analysis of different rattling distances versus GPR performance
(accuracy and uncertainty): take structures from the database, rattle them, then
predict their energy.
```

## Grammar notes

Generalized concepts for grammar fixes across prompts. When a prompt is added, its
fixes are folded into these existing concepts (adding a new one only if the mistake
is genuinely new).

1. **Formatting that breaks machine-readable content** — paths/identifiers split
   mid-token by line wraps. Paths and filenames must stay on one line and be kept
   intact (e.g. `/home/thin k/...` and `It' s` from the 20260826_2333 prompt).
2. **Incomplete clauses** — an instruction missing its verb, object, or noun (e.g.
   "the accuracy ... of the GPR model under different energy range" → add the
   missing plural object "energy ranges").
3. **Non-idiomatic phrasing** — unnatural preposition/filler around common actions
   (e.g. "the accuracy (use MAE...)" → "the accuracy (using MAE...)").
4. **Redundant / misplaced comma** — a comma splitting a verb from its object or
   breaking the flow (e.g. "analysis, showing the uncertainty" → "analysis showing
   the uncertainty" from the 20260826_2354 prompt).
5. **Misspelling / dangling punctuation** — a misspelled word ("ratteling" →
   "rattling") and a trailing comma/dangling clause with no following verb (the
   trailing `,` on the 20260827_0024 prompt).

# FLAG: 20260826_2354

## Original (before grammar fix)

```
Include an uncertainty analysis, showing the uncertainty across the energy level.
```

## Fixed grammar (after)

```
Include an uncertainty analysis showing the uncertainty across the energy levels.
```

## Grammar notes

Generalized concepts for grammar fixes across prompts. When a prompt is added, its
fixes are folded into these existing concepts (adding a new one only if the mistake
is genuinely new).

1. **Formatting that breaks machine-readable content** — paths/identifiers split
   mid-token by line wraps. Paths and filenames must stay on one line and be kept
   intact (e.g. `/home/thin k/...` and `It' s` from the 20260826_2333 prompt).
2. **Incomplete clauses** — an instruction missing its verb, object, or noun (e.g.
   "the accuracy ... of the GPR model under different energy range" → add the
   missing plural object "energy ranges").
3. **Non-idiomatic phrasing** — unnatural preposition/filler around common actions
   (e.g. "the accuracy (use MAE...)" → "the accuracy (using MAE...)").
4. **Redundant / misplaced comma** — a comma splitting a verb from its object or
   breaking the flow (e.g. "analysis, showing the uncertainty" → "analysis showing
   the uncertainty" from the 20260826_2354 prompt).

# FLAG: 20260826_2333

## Original (before grammar fix)

```
Make a new code for this project: /home/thin
k/Desktop/research/_run/b_nestedsampling/. It'
s the kernel GPR accuracy analysis code. It wi
ll extract the performance of the GPR model, under different energy range. Specifically, I want to see the accuracy (use MAE, RMSE, R^2) of the GPR model on predicting the energy of the structures, as a function of the energy range.
```

## Fixed grammar (after)

```
Make a new code for this project:
/home/think/Desktop/research/_run/b_nestedsampling/. It's the kernel GPR accuracy
analysis code. It will extract the performance of the GPR model under different
energy ranges. Specifically, I want to see the accuracy (using MAE, RMSE, R^2) of
the GPR model in predicting the energy of the structures, as a function of the
energy range.
```

## Grammar notes

Generalized concepts for grammar fixes across prompts. When a prompt is added, its
fixes are folded into these existing concepts (adding a new one only if the mistake
is genuinely new).

1. **Formatting that breaks machine-readable content** — paths/identifiers split
   mid-token by line wraps. Paths and filenames must stay on one line and be kept
   intact (e.g. `/home/thin k/...` and `It' s` from the 20260826_2333 prompt).
2. **Incomplete clauses** — an instruction missing its verb, object, or noun (e.g.
   "the accuracy ... of the GPR model under different energy range" → add the
   missing plural object "energy ranges").
3. **Non-idiomatic phrasing** — unnatural preposition/filler around common actions
   (e.g. "the accuracy (use MAE...)" → "the accuracy (using MAE...)").
