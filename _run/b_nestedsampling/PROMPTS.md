# PROMPTS — Project b_nestedsampling prompt log + grammar concept system

This file logs every prompt the owner adds for future work, each marked with a
**flag code** (`YYYYMMDD_HHMM`, local time) and cleaned into a consistent grammar.
Newer prompts sit **above** older ones. See `AGENTS.md` §3b for the full rules.

> Scaffold created on project setup (2026-08-26). Prompts are logged below; new
> entries get a `# FLAG: <YYYYMMDD_HHMM>` heading with the two grammar blocks and
> any fixes folded into the single shared `## Grammar notes` below.

## Grammar notes

Generalized concepts for grammar fixes across all flagged prompts. When a prompt is
added, its fixes are folded into these existing concepts (adding a new one only if the
mistake is genuinely new). There is exactly ONE Grammar notes section for the whole
file — do not create a per-flag one.

1. **Formatting that breaks machine-readable content** — paths/identifiers split
   mid-token by line wraps. Paths and filenames must stay on one line and be kept
   intact (e.g. `/home/thin k/...` and `It' s` from the 20260826_2333 prompt;
   "nested\n_sampling" and "relat\nive" from the 20260827_1638 prompt).
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
   definition so "Fe island height" leads, from the 20260827_0041 prompt; "gpr" →
   "GPR" from the 20260827_1638 prompt).
7. **Missing noun / dangling pronoun** — a sentence missing a plural noun or whose
   pronoun lacks an antecedent (e.g. "For all the DISCUSSION.md, include ... the
   script that it used" → "For all the DISCUSSION.md files, include the actual
   running script that produced them", from the 20260827_0059 prompt; "limit
   dataset" → "limit the dataset" from the 20260827_1638 prompt).

---

# FLAG: 20260828_1918

## Original (before grammar fix)

```
The DB, at low energy were dominated with almost duplicated structure, so, the initial live point might also include duplicated structure. To counter that, we can use a novelty+force filter here: /home/think/Desktop/research/_run/9_novelFilter, for the dataset before the initial live points selection. Note that this is not a filter for GPR training. GPR still use all the dataset. Only use this filter when we were about to choose initial live points. What do you think? What is the good and the bad?
```

## Fixed grammar (after)

```
The DB is dominated at low energy by almost-duplicated structures, so the initial live points might also include duplicates. To counter that, we can apply the novelty+force filter here
(/home/think/Desktop/research/_run/9_novelFilter) to the dataset before the initial-live-point selection. Note this is NOT a filter for GPR training: the GPR still uses the full dataset. Use this filter only when we are about to choose the initial live points. What do you think? What are the pros and cons?
```

# FLAG: 20260827_1638

## Original (before grammar fix)

```
Much like in the gpr_accuracy.py code, update the nested
_sampling codes to include --e-max-per-atom (that is relat
ive to its lowest energy). It will limit dataset that is u
sed for the nested sampling and the gpr training data and
the initial structure for the nested sampling. 
```

## Fixed grammar (after)

```
Much like in the gpr_accuracy.py code, update the nested-sampling codes to include
--e-max-per-atom (relative to the lowest energy). It will limit the dataset used
for the nested sampling and the GPR training data, and the initial structures for
the nested sampling.
```

---

# FLAG: 20260827_0059

## Original (before grammar fix)

```
For all the DISCUSSION.md, include the actual running script that it used.
```

## Fixed grammar (after)

```
For all the DISCUSSION.md files, include the actual running script that produced
them.
```

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

# FLAG: 20260827_0024

## Original (before grammar fix)

```
Include an analysis of different ratteling distances (take the structure from the database, then rattled them, then predict its energy) vs the GPR performance (accuracy and uncertainty), 
```

## Fixed grammar (after)

```
Include an analysis of different rattling distances versus GPR performance
(accuracy and uncertainty): take structures from the database, rattle them under
different ranges, then predict their energy. I want to check how much rattling
distance the kernel can handle (rattle only Fe by default; provide a way to choose
which atoms to rattle). Clarify each step.
```

# FLAG: 20260826_2354

## Original (before grammar fix)

```
Include an uncertainty analysis, showing the uncertainty across the energy level.
```

## Fixed grammar (after)

```
Include an uncertainty analysis showing the uncertainty across the energy levels.
```

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
