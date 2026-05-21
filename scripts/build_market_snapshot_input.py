#!/usr/bin/env python3
"""Build a validated market snapshot input from local normalized source data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from traders_market_read.input.snapshot_builder import (
    MarketSnapshotBuilderError,
    build_market_snapshot_from_sources,
    write_market_snapshot,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a validated detector-runtime market snapshot input."
    )
    parser.add_argument("--market-context", type=Path, required=True)
    parser.add_argument("--structural-levels", type=Path, required=True)
    parser.add_argument("--session-bars", type=Path, required=True)
    parser.add_argument("--value-areas", type=Path, required=True)
    parser.add_argument("--profile-rows", type=Path, required=True)
    parser.add_argument("--tape-metrics", type=Path, required=True)
    parser.add_argument("--intermarket-metrics", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = build_market_snapshot_from_sources(
            market_context_path=args.market_context,
            structural_levels_path=args.structural_levels,
            session_bars_path=args.session_bars,
            value_areas_path=args.value_areas,
            profile_rows_path=args.profile_rows,
            tape_metrics_path=args.tape_metrics,
            intermarket_metrics_path=args.intermarket_metrics,
        )
        write_market_snapshot(args.output, result.snapshot)
    except MarketSnapshotBuilderError as exc:
        print("market snapshot builder FAILED")
        print(str(exc))
        return 1

    print("market snapshot builder PASS")
    print(f"output path:                 {args.output}")
    print(f"detector input blocks:       {result.detector_input_blocks_written}")
    print(f"computable blocks:           {result.computable_blocks_written}")
    print(f"calibrated blocks:           {result.calibrated_blocks_written}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
