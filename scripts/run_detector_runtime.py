#!/usr/bin/env python3
"""Run the TMR-P25 safe detector runtime against an input fixture.

Loads the 110 detector contracts, runs every contract in one pass (or a single
contract with --concept-id), self-validates every emitted output, optionally
writes the outputs as a JSON array, and prints a concise summary.

The runtime is non-executional: it never emits trade permission, entries,
stops, targets, sizing, or broker/order/account/fill/P&L behaviour.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from traders_market_read.detectors.calibration import (
    CalibrationError,
    load_calibration_profile,
)
from traders_market_read.detectors.catalog import CatalogError, load_catalog
from traders_market_read.detectors.runtime import run
from traders_market_read.input.market_snapshot import (
    MarketSnapshotInputError,
    runtime_market_context_from_file,
)


def _fail(message: str, code: int = 2) -> int:
    print("detector runtime FAILED")
    print(message)
    return code


def load_input(path: Path) -> dict[str, Any]:
    """Read the input fixture and return its market-context dictionary.

    Accepts either a document with a ``market_context`` object or a bare
    market-context object. Raises ValueError on malformed input.
    """
    try:
        return runtime_market_context_from_file(path)
    except MarketSnapshotInputError as exc:
        raise ValueError(str(exc)) from exc


def write_outputs(path: Path, outputs: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(outputs, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def print_summary(summary: dict[str, int]) -> None:
    print(f"catalog contracts:           {summary['total_contracts']}")
    print(f"outputs generated:           {summary['outputs_generated']}")
    print(f"computable implemented:      {summary['computable_implemented']}")
    print(f"computable refused/blocked:  {summary['computable_refused_or_blocked']}")
    print(f"calibrated implemented:      {summary['calibrated_implemented']}")
    print(f"calibrated refused:          {summary['calibrated_refused']}")
    print(f"judgment-assisted routed:    {summary['judgment_assisted_routed']}")
    print(f"context-only routed:         {summary['context_only_routed']}")
    print(f"not-detectable blocked:      {summary['not_detectable_blocked']}")
    print(f"total refusals:              {summary['total_refusals']}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the safe detector runtime against an input fixture."
    )
    parser.add_argument("input_json", type=Path, help="Path to the input fixture JSON.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the detector outputs as a JSON array.",
    )
    parser.add_argument(
        "--concept-id",
        default=None,
        help="Optional single concept_id to run instead of all contracts.",
    )
    parser.add_argument(
        "--calibration-profile",
        type=Path,
        default=None,
        help="Optional calibration profile YAML; enables CALIBRATED detectors.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        catalog = load_catalog()
    except CatalogError as exc:
        return _fail(f"catalog error: {exc}")

    try:
        market_context = load_input(args.input_json)
    except ValueError as exc:
        return _fail(f"malformed input: {exc}")

    calibration_profile = None
    if args.calibration_profile is not None:
        try:
            calibration_profile = load_calibration_profile(args.calibration_profile)
        except CalibrationError as exc:
            return _fail(f"calibration profile error: {exc}")

    try:
        report = run(
            market_context,
            catalog=catalog,
            concept_id=args.concept_id,
            calibration_profile=calibration_profile,
        )
    except CatalogError as exc:
        return _fail(f"catalog error: {exc}")

    if args.output is not None:
        write_outputs(args.output, report.outputs)

    if not report.ok:
        print("detector runtime FAILED")
        print(f"{len(report.validation_errors)} output(s) failed validation:")
        for error in report.validation_errors[:50]:
            print(f"- {error}")
        return 1

    print("detector runtime PASS")
    print(f"input fixture:               {args.input_json}")
    if calibration_profile is not None:
        print(f"calibration profile:         {args.calibration_profile}")
    if args.concept_id is not None:
        print(f"concept filter:              {args.concept_id}")
    if args.output is not None:
        print(f"outputs written:             {args.output}")
    print_summary(report.summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
