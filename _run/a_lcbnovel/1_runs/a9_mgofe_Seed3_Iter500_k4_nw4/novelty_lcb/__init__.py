#!/usr/bin/env python3


__version__ = "1.0.0"

#  (noqa: D104 — the module docstring is in __init__.py)

# Re-export the canonical names so that
#   from novelty_lcb import NoveltyLCBAcquisitor, is_distinct, fingerprint_distance
# works exactly like the old monolithic module.
from .acquisitor import NoveltyLCBAcquisitor
from .utils import is_distinct, fingerprint_distance

__all__ = ["NoveltyLCBAcquisitor", "is_distinct", "fingerprint_distance"]
