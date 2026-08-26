# FLAG: 20260826_1437

## Original (before grammar fix)

```
Make a new _runs using the same system and setup as the `/home/think/Desktop/research/_run/a_lcbnovel/_runs/a5_mgofe_Seed3_Iter500_k4`, but with a different `NOVELTY_WEIGHT`, starting from 2.0, 3.0, and 4.0. Clarify for every step.
```

## Fixed grammar (after)

```
Create a new `_runs` directory using the same system and setup as
`/home/think/Desktop/research/_run/a_lcbnovel/_runs/a5_mgofe_Seed3_Iter500_k4`,
but with a different `NOVELTY_WEIGHT` value: 2.0, 3.0, and 4.0. Clarify each step.
```

# FLAG: 20260826_14

## Original (before grammar fix)

```
Make a new _runs dir. Same system as /home/think/Desktop/r
esearch/_run/a_lcbnovel/_runs/a1_mgofe_Seed3_Iter500/ but with different kappa number. Make for kappa 3, 4, and 5. Clarify for every step.
```

## Fixed grammar (after)

```
Create a new `_runs` directory using the same setup as
`/home/think/Desktop/research/_run/a_lcbnovel/_runs/a1_mgofe_Seed3_Iter500/`,
but with a different kappa value. Make runs for kappa 3, 4, and 5. Clarify each step.
```

## Grammar notes

The same kinds of mistakes recur across prompts. Below is a set of **concepts** that
generalize them, with the concrete instances from each flagged prompt shown under each.

### Concept 1 — Incomplete clauses: a verb, its object, and its noun are left out

An instruction must name (a) what to create, (b) what it is, and (c) what to do with
it. Dropping any of these makes the reader (or agent) guess.

- **20260826_14:** "Make a new _runs dir. Same system as ..." — the second half is a
  noun phrase with **no verb**, so it is unclear *what* to do with that system. "Make
  for kappa 3, 4, and 5" — **no object**: make *what*? The intended object (runs) is
  omitted.
- **20260826_1437:** "Make a new _runs ..." — missing the **noun** `directory`
  (a `_runs` is a directory, so the type must be named). Same verb-object gap as
  above.

**Fix pattern:** state the object explicitly — "Create a new `_runs` **directory**",
"**Make runs** for kappa 3, 4, and 5".

### Concept 2 — Redundant or near-duplicate words

Two words that carry the same meaning are stacked, adding noise instead of precision.

- **20260826_14:** "different **kappa number**" — *kappa* already denotes a
  number/parameter; the extra word "number" is redundant.
- **20260826_1437:** "same **system and setup**" — *system* and *setup* here are
  near-synonyms for the same thing (the template run being copied); keeping both
  blurs which parameter set is inherited.

**Fix pattern:** pick the single precise word ("kappa value", "same setup") or, if both
really are distinct, define them explicitly.

### Concept 3 — Vague or ambiguous way of listing parameters/values

Lists of values are stated in a way that leaves the reader guessing whether they are a
*range*, a *start point*, or a *fixed set*.

- **20260826_14:** "Make for kappa 3, 4, and 5" — with the object missing, this reads
  as if "3, 4, and 5" is the thing being made.
- **20260826_1437:** "a different `NOVELTY_WEIGHT`, **starting from** 2.0, 3.0, and
  4.0" — "starting from" implies a progression away from 2.0, not a flat set of three
  values; and the parameter name floats without a connector to its values.

**Fix pattern:** connect the parameter to its explicit set of values —
"`NOVELTY_WEIGHT` **values**: 2.0, 3.0, and 4.0" — and say how many runs that implies.

### Concept 4 — Non-idiomatic phrasing around common actions ("for every step")

A preposition or filler word is used in a way a native speaker would not, producing a
grammatically odd but understandable sentence. This one **recurs in both prompts**.

- **20260826_14** and **20260826_1437:** "**Clarify for every step**" — the "for" is
  unnecessary and unidiomatic.

**Fix pattern:** the natural command form is "**Clarify each step**" (or "Clarify every
step", without "for").

### Concept 5 — Formatting that breaks the machine-readable content (paths)

Paths and code identifiers must survive copy-paste; breaking them mid-token destroys
them.

- **20260826_14:** the path was split **inside a word** (`.../Desktop/r` + newline +
  `esearch/...`), so the literal text no longer resolves to the real directory.

**Fix pattern:** keep a path on one line (or wrap it in backticks) so it is copied
verbatim.

---

**Suggested improvements (beyond the grammar fix, shared by both prompts)**

- **Write the instruction as a short list** instead of one long sentence, so each
  action is explicit:
  - "Create a new `_runs` directory based on `<template>`."
  - "Use a different value for the parameter: 3, 4, and 5 (three runs)."
  - "Clarify each step before proceeding."
- **State which parameters are inherited vs changed.** "Same setup as .../Iter500_k4"
  implies seed and iteration budget are inherited; say so explicitly so only the
  intended parameter (kappa, or `NOVELTY_WEIGHT`) is understood to change.
- **Name the output shape** (how many run directories, what they should be called) so
  there is no guesswork about the deliverable.
- **Wrap paths and code identifiers in backticks** and keep each on its own line so
  they scan cleanly and copy verbatim.
