#!/usr/bin/env python3
"""Build a compact operator packet view model JSON."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from traders_market_read.viewmodels.operator_packet import (
    OperatorPacketViewModelError,
    build_operator_packet_view_model,
    write_operator_packet_view_model,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an operator packet view model.")
    parser.add_argument("--runtime-output", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        view_model = build_operator_packet_view_model(
            runtime_output_path=args.runtime_output,
            summary_json_path=args.summary_json,
        )
        write_operator_packet_view_model(args.output, view_model)
    except OperatorPacketViewModelError as exc:
        print("operator packet view model FAILED")
        print(str(exc))
        return 1

    print("operator packet view model PASS")
    print(f"output path:                 {args.output}")
    print(f"total outputs:               {view_model['counts']['total_outputs']}")
    print(f"active findings:             {len(view_model['active_findings'])}")
    print(f"review queue count:          {len(view_model['review_queue'])}")
    print(f"blocked count:               {len(view_model['blocked_by_feed'])}")
    print(f"context governance count:    {len(view_model['context_governance'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
