"""Traders Market-Read detector runtime package.

This package implements the TMR-P25 Safe Detector Runtime. It loads the
detector contract catalog, runs every contract in one pass, computes real
structural behaviour for COMPUTABLE detectors, and emits safe non-executional
refusal/context outputs for every other determinism class.

It is not a trading engine. It never produces trade permission, entries,
stops, targets, sizing, order behaviour, broker/account/fill/P&L behaviour,
calibration values, or autonomous trading instructions.
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
