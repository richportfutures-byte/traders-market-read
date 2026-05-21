#!/usr/bin/env python3
"""Summarize non-executional detector runtime output."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from traders_market_read.reporting.runtime_summary import (
    RuntimeSummaryError,
    build_runtime_summary,
    render_review_packet_markdown,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a detector runtime summary and review packet."
    )
    parser.add_argument("runtime_output_json", type=Path)
    parser.add_argument("--summary-json", type=Path, default=None)
    parser.add_argument("--review-md", type=Path, default=None)
    return parser.parse_args(argv)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = build_runtime_summary(args.runtime_output_json)
        review_md = None
        if args.review_md is not None:
            review_md = render_review_packet_markdown(args.runtime_output_json, summary)
    except RuntimeSummaryError as exc:
        print("detector runtime summary FAILED")
        print(str(exc))
        return 1

    if args.summary_json is not None:
        _write_json(args.summary_json, summary)
    if args.review_md is not None and review_md is not None:
        _write_text(args.review_md, review_md)

    print("detector runtime summary PASS")
    print(f"input file:                 {args.runtime_output_json}")
    print(f"total contracts:            {summary['total_contracts']}")
    print(f"total outputs:              {summary['total_outputs']}")
    print(f"refusal count:              {summary['refusal_count']}")
    print(f"non-refusal count:          {summary['non_refusal_count']}")
    print(f"computable non-refusal:     {summary['computable_non_refusal_count']}")
    print(f"calibrated non-refusal:     {summary['calibrated_non_refusal_count']}")
    print(f"judgment review queue:      {summary['judgment_assisted_review_count']}")
    print(f"context-only count:         {summary['context_only_count']}")
    print(f"blocked-by-feed count:      {summary['not_detectable_blocked_count']}")
    if args.summary_json is not None:
        print(f"summary JSON written:       {args.summary_json}")
    if args.review_md is not None:
        print(f"review Markdown written:    {args.review_md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
