#!/usr/bin/env python3
"""Validate market snapshot input JSON for the detector runtime."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from traders_market_read.input.market_snapshot import (
    MarketSnapshotInputError,
    load_market_snapshot,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate one or more market snapshot input JSON files."
    )
    parser.add_argument("input_json", nargs="+", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    passed = 0
    failed = 0
    for path in args.input_json:
        try:
            snapshot = load_market_snapshot(path)
        except MarketSnapshotInputError as exc:
            failed += 1
            print(f"FAIL {path}: {exc}")
            continue
        passed += 1
        print(
            f"PASS {path}: shape={snapshot.source_shape} detector_inputs={len(snapshot.detector_inputs)}"
        )
    print(f"summary: passed={passed} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
