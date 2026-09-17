"""Completed-run selection — the single place where "which searches count" is decided.

RULE: only searches that ran the full iteration budget (FULL_ITERATIONS) are used.  A run that
was stopped early has had less search time, so its per-seed best is systematically worse, and
because unfinished runs are *not* distributed evenly across systems and parameter settings,
including them biases every comparison they take part in.

Why this module exists: the previous loaders globbed `seed_*/1_db/db_*.db`, which drops runs
*named* `stop_*` but silently accepts a `seed_*` run that stopped early.  That is how
`fecomgo/seed_4` (iteration 10 only) and `fecobmgo/seed_3` (stopped at 73) came to be included in
the main-text analysis.  Every loader now imports this module rather than testing for itself.

Typical use
-----------
    from run_selection import completed_dbs
    dbs, rejected = completed_dbs(f'data/{system}/seed_*/1_db/db_*.db')

Both the accepted and the rejected lists are returned so a caller can report *what* it dropped
instead of dropping it silently.
"""
import glob
import os
import sqlite3

FULL_ITERATIONS = 100      # the configured AGOX run length; reaching it makes a run "completed"


def db_iteration_range(dbp):
    """(min_iteration, max_iteration, n_structures) for an AGOX .db, or (None, None, 0).

    Read-only; the file is never modified.  Returns (None, None, 0) for an unreadable or empty
    database (e.g. a replica directory whose db was never populated).
    """
    try:
        con = sqlite3.connect(f'file:{os.path.abspath(dbp)}?mode=ro', uri=True)
        try:
            row = con.execute('select min(iteration), max(iteration), count(*) from structures'
                              ).fetchone()
        finally:
            con.close()
    except Exception:
        return (None, None, 0)
    if row is None:
        return (None, None, 0)
    return (row[0], row[1], row[2] or 0)


def is_completed(dbp, full_iterations=FULL_ITERATIONS):
    """True if the run in `dbp` reached `full_iterations`."""
    hi = db_iteration_range(dbp)[1]
    return hi is not None and hi >= full_iterations


def select_completed(dbs, full_iterations=FULL_ITERATIONS):
    """Split db paths into (completed, rejected); rejected entries are (path, max_iteration)."""
    completed, rejected = [], []
    for d in dbs:
        hi = db_iteration_range(d)[1]
        if hi is not None and hi >= full_iterations:
            completed.append(d)
        else:
            rejected.append((d, hi))
    return completed, rejected


def completed_dbs(pattern, full_iterations=FULL_ITERATIONS, verbose=False, indent='    '):
    """Glob `pattern` and keep only completed runs.  Returns (completed, rejected).

    `rejected` is a list of (path, max_iteration) so the caller can print or record exactly which
    runs were excluded — an exclusion that is reported is a caveat, one that is not is a bug.
    """
    matched = sorted(glob.glob(pattern))
    completed, rejected = select_completed(matched, full_iterations)
    if verbose and rejected:
        for path, hi in rejected:
            where = 'no data' if hi is None else f'max iteration {hi}'
            print(f'{indent}excluded unfinished run ({where} < {full_iterations}): {path}')
    return completed, rejected


def replica_name(dbp):
    """The replica (search) directory name for a `.../<replica>/1_db/db_N.db` path."""
    return os.path.basename(os.path.dirname(os.path.dirname(dbp)))
