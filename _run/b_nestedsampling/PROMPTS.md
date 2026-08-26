# PROMPTS — Project b_nestedsampling prompt log + grammar concept system

This file logs every prompt the owner adds for future work, each marked with a
**flag code** (`YYYYMMDD_HHMM`, local time) and cleaned into a consistent grammar.
Newer prompts sit **above** older ones. See `AGENTS.md` §3b for the full rules.

> Scaffold created on project setup (2026-08-26). Prompts are logged below; new
> entries get a `# FLAG: <YYYYMMDD_HHMM>` heading with the two grammar blocks and
> any fixes folded into the shared `## Grammar notes`.

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
