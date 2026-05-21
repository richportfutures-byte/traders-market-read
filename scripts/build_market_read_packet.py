#!/usr/bin/env python3
"""Build a complete non-executional market-read packet in one command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from traders_market_read.pipeline.market_read_packet import (
    MarketReadPacketError,
    build_market_read_packet,
)
from traders_market_read.input.market_snapshot import (
    MarketSnapshotInputError,
    load_market_snapshot,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run detector runtime, validation, summary, and review packet generation."
    )
    parser.add_argument("input_json", type=Path)
    parser.add_argument("--calibration-profile", type=Path, default=None)
    parser.add_argument("--runtime-output", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    parser.add_argument("--review-md", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        load_market_snapshot(args.input_json)
        result = build_market_read_packet(
            args.input_json,
            calibration_profile_path=args.calibration_profile,
            runtime_output_path=args.runtime_output,
            summary_json_path=args.summary_json,
            review_markdown_path=args.review_md,
        )
    except (MarketReadPacketError, MarketSnapshotInputError) as exc:
        print("market-read packet pipeline FAILED")
        print(str(exc))
        return 1

    print("market-read packet pipeline PASS")
    print(f"runtime output:             {result.runtime_output_path}")
    print(f"summary JSON:               {result.summary_json_path}")
    print(f"review Markdown:            {result.review_markdown_path}")
    print(f"total contracts:            {result.total_contracts}")
    print(f"total outputs:              {result.total_outputs}")
    print(f"refusal count:              {result.refusal_count}")
    print(f"non-refusal count:          {result.non_refusal_count}")
    print(f"review queue count:         {result.review_queue_count}")
    print(f"calibrated non-refusal:     {result.calibrated_non_refusal_count}")
    print(f"computable non-refusal:     {result.computable_non_refusal_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
