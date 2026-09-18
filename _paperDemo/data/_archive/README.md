# `data/_archive/` — raw data outside the paper's scope

**Since CLAIMS v9 (2026-09-17) the paper studies the Fe host only: `femgo` (Fe/MgO) and `febmgo`
(Fe-B/MgO).** The Fe-Co and Fe-Co-B structure-search databases were moved here:

| directory | was | size |
|---|---|---|
| `fecomgo/` | Fe-Co/MgO, 4 completed searches | 96 MB |
| `fecobmgo/` | Fe-Co-B/MgO, 3 completed searches | 92 MB |

Nothing was deleted and nothing was recomputed. The models were archived because the host is not a
clean counterfactual against the Fe pair (different strain convention, 4 vs 3 searches cannot reach
p < 0.029, and `fecomgo/main.py` uses an extra `PermutationGenerator`) — **not** because their
results were refuted. Full record, evidence and revival instructions: `_archive/cofe/README.md`;
frozen claim values and the required re-run conditions: `CLAIMS.md` → "ARCHIVED — out of scope".

`data/` is not tracked by git (it is far too large for the paper's commits), so this move is a
plain filesystem move, not a `git mv`.

## Scripts still read these directories

`scripts/scope.py` resolves the data root per system (`data_root()` → `data/_archive/` for an
archived system), so the archived analysis still runs:

```bash
python scripts/ensemble_analysis.py --all-systems     # all four systems, archived ones included
python scripts/ensemble_analysis.py                    # the paper's scope (femgo + febmgo)
```

Do not add a new analysis script that hard-codes `data/<system>/…`; import `scope.db_glob` instead.
