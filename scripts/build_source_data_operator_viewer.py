#!/usr/bin/env python3
"""Build source-data snapshot, packet artifacts, view model, and static HTML."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from traders_market_read.pipeline.source_data_html import (
    SourceDataHtmlPipelineError,
    build_source_data_operator_viewer,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a complete static operator viewer from normalized source data."
    )
    parser.add_argument("--market-context", type=Path, required=True)
    parser.add_argument("--structural-levels", type=Path, required=True)
    parser.add_argument("--session-bars", type=Path, required=True)
    parser.add_argument("--value-areas", type=Path, required=True)
    parser.add_argument("--profile-rows", type=Path, required=True)
    parser.add_argument("--tape-metrics", type=Path, required=True)
    parser.add_argument("--intermarket-metrics", type=Path, required=True)
    parser.add_argument("--calibration-profile", type=Path, default=None)
    parser.add_argument("--market-snapshot-output", type=Path, required=True)
    parser.add_argument("--runtime-output", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    parser.add_argument("--view-model-output", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = build_source_data_operator_viewer(
            market_context_path=args.market_context,
            structural_levels_path=args.structural_levels,
            session_bars_path=args.session_bars,
            value_areas_path=args.value_areas,
            profile_rows_path=args.profile_rows,
            tape_metrics_path=args.tape_metrics,
            intermarket_metrics_path=args.intermarket_metrics,
            calibration_profile_path=args.calibration_profile,
            market_snapshot_output_path=args.market_snapshot_output,
            runtime_output_path=args.runtime_output,
            summary_json_path=args.summary_json,
            operator_view_model_output_path=args.view_model_output,
            html_output_path=args.output_html,
        )
    except SourceDataHtmlPipelineError as exc:
        print("source-data operator viewer pipeline FAILED")
        print(str(exc))
        return 1

    print("source-data operator viewer pipeline PASS")
    print(f"market snapshot:             {result.market_snapshot_path}")
    print(f"runtime output:              {result.runtime_output_path}")
    print(f"summary JSON:                {result.summary_json_path}")
    print(f"operator view model:         {result.operator_view_model_path}")
    print(f"HTML viewer:                 {result.html_viewer_path}")
    print(f"total outputs:               {result.total_outputs}")
    print(f"active findings:             {result.active_findings_count}")
    print(f"review queue count:          {result.review_queue_count}")
    print(f"blocked-by-feed count:       {result.blocked_by_feed_count}")
    print(f"context governance count:    {result.context_governance_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
