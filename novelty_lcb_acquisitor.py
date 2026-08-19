"""
Novelty-LCB Acquisitor — organized package
============================================

Import shorthand that matches the old monolithic module at the project root
(``novelty_lcb_acquisitor.py``) so that existing scripts continue to work
unchanged::

    from novelty_lcb_acquisitor import NoveltyLCBAcquisitor, is_distinct
    from novelty_lcb_acquisitor import fingerprint_distance

This file lives at the project root.  The canonical implementation has been
moved into ``novelty_lcb/``:

    novelty_lcb/
    ├── __init__.py              # re-exports the three canonical names
    ├── acquisitor.py            # NoveltyLCBAcquisitor class
    ├── utils.py                 # is_distinct(), fingerprint_distance()
    ├── benchmark_helpers.py     # build_agox() factory + defaults
    ├── benchmarks/
    │   ├── __init__.py
    │   ├── benchmark_v1.py      # broad energy window
    │   └── benchmark_v2.py      # tight energy window
    ├── visualization/
    │   ├── __init__.py
    │   └── concept.py           # 3-panel acquisition concept figure
    └── tests/
        ├── __init__.py
        ├── run_tests.py         # runner (mirrors test_novelty_lcb.py)
        └── mock_objects.py      # MockDescriptor, MockModel, MockDatabase
"""

from novelty_lcb import NoveltyLCBAcquisitor, is_distinct, fingerprint_distance  # noqa: F401
