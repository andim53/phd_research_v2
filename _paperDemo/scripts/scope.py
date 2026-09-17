"""Which systems this paper analyses — the single place where the paper's scope is decided.

RULE (v9, 2026-09-17): the paper studies the **Fe host only**:

    femgo  (Fe/MgO)   13 completed searches
    febmgo (Fe-B/MgO)  6 completed searches

The Fe-Co and Fe-Co-B models are **archived out of scope**.  Their raw data lives under
`data/_archive/`, their frozen claim values are in CLAIMS.md ("ARCHIVED — out of scope"), and the
narrative/evidence trail is in `_archive/cofe/README.md`.  No paper figure, table or claim may use
them.

Why the host was dropped (CLAIMS v9): the Co pair sat on a different strain convention
(`a_MgO/sqrt2 = 2.97833 A`, film stretched 4.9 %) than the Fe pair (`a_Fe = 2.87019 A`, substrate
compressed 3.6 %), so boron and the strain convention varied together; 4 vs 3 completed searches
cannot reach p < 0.029; and `data/fecomgo/main.py` adds a third PermutationGenerator.  The host was
therefore not a clean counterfactual.

Keeping the four-system capability
---------------------------------
Every script that reads several systems imports this module instead of carrying its own list, so
the scope is changed in one place.  Pass

    --all-systems                 every system in ALL_SYSTEMS, archived ones included
    --systems fecomgo,fecobmgo    an explicit list

to recompute the archived analysis; without either flag a script uses SYSTEMS_IN_SCOPE.  Archived
systems are read from ARCHIVE_DATA_ROOT, so the archived analysis keeps working after the data
move.  Args may also be read straight from argv via `systems_from_argv()` in scripts that have no
argparse parser.

Typical use
-----------
    from scope import SYSTEMS_IN_SCOPE, LABELS, db_glob, add_scope_arguments, systems_from_args

    SYSTEMS = list(SYSTEMS_IN_SCOPE)
    ...
    add_scope_arguments(ap)
    args = ap.parse_args()
    SYSTEMS = systems_from_args(args)
    for system in SYSTEMS:
        dbs, rejected = completed_dbs(db_glob(system))
"""
import sys

DATA_ROOT = 'data'                  # in-scope raw data
ARCHIVE_DATA_ROOT = 'data/_archive'  # archived raw data

ALL_SYSTEMS = ('femgo', 'febmgo', 'fecomgo', 'fecobmgo')
SYSTEMS_IN_SCOPE = ('femgo', 'febmgo')
SYSTEMS_OUT_OF_SCOPE = ('fecomgo', 'fecobmgo')

LABELS = {'femgo': 'Fe/MgO', 'febmgo': 'Fe-B/MgO',
          'fecomgo': 'Fe-Co/MgO', 'fecobmgo': 'Fe-Co-B/MgO'}


def in_scope(system):
    """True if `system` belongs to the paper's scope."""
    return system in SYSTEMS_IN_SCOPE


def label(system):
    return LABELS.get(system, system)


def data_root(system):
    """Directory holding `system`'s replicas; archived systems live under data/_archive/."""
    return DATA_ROOT if in_scope(system) else ARCHIVE_DATA_ROOT


def db_glob(system, replica='*/1_db/db_*.db'):
    """Glob pattern for `system`'s databases, resolved against the right data root."""
    return f'{data_root(system)}/{system}/{replica}'


def add_scope_arguments(ap):
    """Add --systems/--all-systems to an argparse parser (default: the paper's scope)."""
    ap.add_argument('--systems', default=None,
                    help="comma-separated systems to analyse; default is the paper's scope, "
                         f"{'+'.join(SYSTEMS_IN_SCOPE)}")
    ap.add_argument('--all-systems', action='store_true',
                    help='analyse every system in ALL_SYSTEMS, archived ones included '
                         f"({'+'.join(ALL_SYSTEMS)})")


def systems_from_args(args):
    """Resolve the system list from parsed argparse args (see add_scope_arguments)."""
    if getattr(args, 'all_systems', False):
        return list(ALL_SYSTEMS)
    explicit = getattr(args, 'systems', None)
    return _split(explicit) if explicit else list(SYSTEMS_IN_SCOPE)


def systems_from_argv(argv=None):
    """Resolve the system list from raw argv, for scripts without an argparse parser."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if '--all-systems' in argv:
        return list(ALL_SYSTEMS)
    for i, a in enumerate(argv):
        if a.startswith('--systems='):
            return _split(a.split('=', 1)[1])
        if a == '--systems' and i + 1 < len(argv):
            return _split(argv[i + 1])
    return list(SYSTEMS_IN_SCOPE)


def _split(text):
    out = [s.strip() for s in text.replace(',', ' ').split() if s.strip()]
    unknown = [s for s in out if s not in ALL_SYSTEMS]
    if unknown:
        raise SystemExit(f'unknown system(s) {unknown}; known systems: {list(ALL_SYSTEMS)}')
    return out


if __name__ == '__main__':
    print(f'in scope      : {list(SYSTEMS_IN_SCOPE)}')
    print(f'out of scope  : {list(SYSTEMS_OUT_OF_SCOPE)}')
    for s in ALL_SYSTEMS:
        print(f'  {s:10s} {label(s):12s} data in {data_root(s)}/')
