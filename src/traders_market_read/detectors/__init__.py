"""Safe detector runtime (TMR-P25).

Public entry points:

- ``load_catalog`` / ``DetectorCatalog`` / ``DetectorContract`` — catalog access.
- ``run`` / ``RuntimeReport`` — orchestrate all detector contracts in one pass.

The runtime is non-executional. Every output stays inside the detector output
contract: bounded states, bounded non-executional action labels, guardrails,
and no execution fields.
"""

from __future__ import annotations

from .catalog import CatalogError, DetectorCatalog, DetectorContract, load_catalog
from .output import OutputError
from .runtime import RuntimeReport, run

__all__ = [
    "CatalogError",
    "DetectorCatalog",
    "DetectorContract",
    "load_catalog",
    "OutputError",
    "RuntimeReport",
    "run",
]
