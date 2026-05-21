#!/usr/bin/env python3
"""Render an operator packet view model as standalone static HTML."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from traders_market_read.viewers.operator_packet_html import (
    OperatorPacketHtmlError,
    load_operator_view_model,
    render_operator_packet_html,
    write_operator_packet_html,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render static operator packet HTML.")
    parser.add_argument("--view-model", type=Path, required=True)
    parser.add_argument("--output-html", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        view_model = load_operator_view_model(args.view_model)
        html = render_operator_packet_html(view_model)
        write_operator_packet_html(args.output_html, html)
    except OperatorPacketHtmlError as exc:
        print("operator packet viewer FAILED")
        print(str(exc))
        return 1

    print("operator packet viewer PASS")
    print(f"output path:                 {args.output_html}")
    print(f"active findings:             {len(view_model['active_findings'])}")
    print(f"review queue count:          {len(view_model['review_queue'])}")
    print(f"blocked-by-feed count:       {len(view_model['blocked_by_feed'])}")
    print(f"context governance count:    {len(view_model['context_governance'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
