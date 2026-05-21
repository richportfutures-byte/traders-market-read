"""Render an operator packet view model as standalone static HTML."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any

from traders_market_read.detectors.output import find_forbidden_fields


class OperatorPacketHtmlError(RuntimeError):
    """Raised when a view model cannot be rendered safely."""


REQUIRED_TOP_LEVEL = (
    "schema_version",
    "counts",
    "boundary",
    "market_read_layers",
    "active_findings",
    "review_queue",
    "blocked_by_feed",
    "context_governance",
    "missing_or_degraded_inputs",
)

REQUIRED_BOUNDARY_FLAGS = (
    "non_executional",
    "no_trade_permission",
    "no_entries_stops_targets_sizing",
    "no_broker_order_account_fill_pnl",
    "no_autonomous_trading",
)


def _read_json(path: Path) -> Any:
    if not path.exists():
        raise OperatorPacketHtmlError(f"view model not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise OperatorPacketHtmlError(f"view model is not valid JSON: {exc}") from exc
    except OSError as exc:
        raise OperatorPacketHtmlError(f"could not read view model {path}: {exc}") from exc


def _reject_forbidden(value: Any) -> None:
    found = find_forbidden_fields(value)
    if found:
        raise OperatorPacketHtmlError(
            "forbidden execution field present in view model: " + ", ".join(found)
        )


def _validate_view_model(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise OperatorPacketHtmlError("view model must be a JSON object")
    _reject_forbidden(value)
    missing = [field for field in REQUIRED_TOP_LEVEL if field not in value]
    if missing:
        raise OperatorPacketHtmlError("view model missing section(s): " + ", ".join(missing))
    boundary = value.get("boundary")
    if not isinstance(boundary, dict):
        raise OperatorPacketHtmlError("view model boundary must be an object")
    for flag in REQUIRED_BOUNDARY_FLAGS:
        if boundary.get(flag) is not True:
            raise OperatorPacketHtmlError(f"boundary.{flag} must be true")
    for list_key in (
        "market_read_layers",
        "active_findings",
        "review_queue",
        "blocked_by_feed",
        "context_governance",
        "missing_or_degraded_inputs",
    ):
        if not isinstance(value.get(list_key), list):
            raise OperatorPacketHtmlError(f"view model {list_key} must be a list")
    if not isinstance(value.get("counts"), dict):
        raise OperatorPacketHtmlError("view model counts must be an object")
    return value


def load_operator_view_model(path: str | Path) -> dict[str, Any]:
    """Load and validate an operator packet view model JSON file."""
    return _validate_view_model(_read_json(Path(path)))


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value)
    return str(value)


def _e(value: Any) -> str:
    return escape(_text(value), quote=True)


def _count(counts: dict[str, Any], key: str) -> int:
    value = counts.get(key, 0)
    return int(value) if isinstance(value, int) else 0


def _table(headers: list[str], rows: list[list[Any]], empty: str) -> str:
    if not rows:
        return f"<p class=\"empty\">{_e(empty)}</p>"
    head = "".join(f"<th>{_e(header)}</th>" for header in headers)
    body = []
    for row in rows:
        body.append("<tr>" + "".join(f"<td>{_e(cell)}</td>" for cell in row) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def _finding_rows(items: list[dict[str, Any]]) -> list[list[Any]]:
    return [
        [
            item.get("concept_id"),
            item.get("display_name"),
            item.get("determinism_class"),
            item.get("route"),
            item.get("state"),
            item.get("action_label"),
            item.get("confidence"),
            item.get("evidence_summary"),
        ]
        for item in items
    ]


def _review_rows(items: list[dict[str, Any]]) -> list[list[Any]]:
    return [
        [
            item.get("concept_id"),
            item.get("display_name"),
            item.get("state"),
            item.get("action_label"),
            item.get("refusal_reason"),
            item.get("needed_evidence"),
        ]
        for item in items
    ]


def _blocked_rows(items: list[dict[str, Any]]) -> list[list[Any]]:
    return [
        [
            item.get("concept_id"),
            item.get("display_name"),
            item.get("state"),
            item.get("refusal_reason"),
            item.get("needed_feed_or_evidence"),
        ]
        for item in items
    ]


def _context_rows(items: list[dict[str, Any]]) -> list[list[Any]]:
    return [
        [
            item.get("concept_id"),
            item.get("display_name"),
            item.get("state"),
            item.get("action_label"),
            item.get("boundary_note"),
        ]
        for item in items
    ]


def _missing_rows(items: list[dict[str, Any]]) -> list[list[Any]]:
    return [
        [
            item.get("concept_id"),
            item.get("display_name"),
            item.get("route"),
            item.get("state"),
            item.get("missing_inputs"),
            item.get("degraded_inputs"),
        ]
        for item in items
    ]


def render_operator_packet_html(view_model: dict[str, Any]) -> str:
    """Render validated view-model data to deterministic standalone HTML."""
    vm = _validate_view_model(view_model)
    counts = vm["counts"]
    source = vm.get("source_artifacts", {})
    active_count = len(vm["active_findings"])
    review_count = len(vm["review_queue"])
    blocked_count = len(vm["blocked_by_feed"])
    context_count = len(vm["context_governance"])

    layer_sections: list[str] = []
    for layer in vm["market_read_layers"]:
        if not isinstance(layer, dict):
            raise OperatorPacketHtmlError("market_read_layers entries must be objects")
        layer_sections.append(
            f"""
            <section class="layer" id="{_e(layer.get('layer_id'))}">
              <h3>{_e(layer.get('display_name'))}</h3>
              <p class="meta">{_e(layer.get('chapter'))}</p>
              <div class="chips">
                <span>Total {_e(layer.get('total_outputs', 0))}</span>
                <span>Active {_e(layer.get('non_refusal_count', 0))}</span>
                <span>Refusals {_e(layer.get('refusal_count', 0))}</span>
                <span>Review {_e(layer.get('review_queue_count', 0))}</span>
                <span>Blocked {_e(layer.get('blocked_count', 0))}</span>
              </div>
              <h4>Active Findings</h4>
              {_table(['Concept', 'Display', 'Class', 'Route', 'State', 'Action', 'Confidence', 'Evidence'], _finding_rows(layer.get('findings', [])), 'No active findings in this layer.')}
              <h4>Review Items</h4>
              {_table(['Concept', 'Display', 'State', 'Action', 'Reason', 'Needed evidence'], _review_rows(layer.get('review_items', [])), 'No review items in this layer.')}
              <h4>Blocked Items</h4>
              {_table(['Concept', 'Display', 'State', 'Reason', 'Needed feed/evidence'], _blocked_rows(layer.get('blocked_items', [])), 'No blocked items in this layer.')}
            </section>
            """
        )

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Trader's Market-Read Operator Packet</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; color: #1f2933; background: #f6f7f9; }}
    header {{ background: #17202a; color: #fff; padding: 24px 32px; }}
    main {{ padding: 24px 32px 40px; max-width: 1440px; margin: 0 auto; }}
    h1, h2, h3, h4 {{ margin: 0 0 12px; }}
    h2 {{ margin-top: 28px; border-bottom: 2px solid #d6dae0; padding-bottom: 8px; }}
    h3 {{ color: #17202a; }}
    section {{ margin-bottom: 24px; }}
    .boundary {{ background: #e9f7ef; border: 1px solid #8fd19e; padding: 14px 16px; margin: 18px 0; }}
    .summary, .chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .summary span, .chips span {{ background: #fff; border: 1px solid #d6dae0; padding: 6px 10px; border-radius: 4px; }}
    .layer {{ background: #fff; border: 1px solid #d6dae0; padding: 16px; border-radius: 6px; }}
    .meta {{ color: #617080; margin: 0 0 10px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff; margin: 8px 0 18px; }}
    th, td {{ border: 1px solid #d6dae0; padding: 8px; vertical-align: top; text-align: left; font-size: 13px; }}
    th {{ background: #eef1f5; }}
    .empty {{ color: #617080; font-style: italic; }}
    code {{ background: #eef1f5; padding: 2px 4px; border-radius: 3px; }}
    footer {{ margin-top: 36px; color: #617080; font-size: 13px; }}
  </style>
</head>
<body>
  <header>
    <h1>Trader's Market-Read Operator Packet</h1>
    <p>Static local view generated from the operator packet view model.</p>
  </header>
  <main>
    <section>
      <h2>Source Artifacts</h2>
      <p>Runtime output: <code>{_e(source.get('runtime_output', ''))}</code></p>
      <p>Summary JSON: <code>{_e(source.get('summary_json', ''))}</code></p>
    </section>
    <section class="boundary">
      <h2>Boundary</h2>
      <p><strong>Non-executional.</strong> No trade permission. No entries/stops/targets/sizing. No broker/order/account/fill/P&amp;L behavior. No autonomous trading.</p>
    </section>
    <section>
      <h2>Summary Counts</h2>
      <div class="summary">
        <span>Total contracts {_count(counts, 'total_contracts')}</span>
        <span>Total outputs {_count(counts, 'total_outputs')}</span>
        <span>Active findings {active_count}</span>
        <span>Review queue {review_count}</span>
        <span>Blocked-by-feed {blocked_count}</span>
        <span>Context governance {context_count}</span>
      </div>
    </section>
    <section>
      <h2>Market-Read Layers</h2>
      {''.join(layer_sections)}
    </section>
    <section>
      <h2>Active Findings</h2>
      {_table(['Concept', 'Display', 'Class', 'Route', 'State', 'Action', 'Confidence', 'Evidence'], _finding_rows(vm['active_findings']), 'No active findings.')}
    </section>
    <section>
      <h2>Review Queue</h2>
      {_table(['Concept', 'Display', 'State', 'Action', 'Reason', 'Needed evidence'], _review_rows(vm['review_queue']), 'No review queue items.')}
    </section>
    <section>
      <h2>Blocked-by-Feed</h2>
      {_table(['Concept', 'Display', 'State', 'Reason', 'Needed feed/evidence'], _blocked_rows(vm['blocked_by_feed']), 'No blocked-by-feed items.')}
    </section>
    <section>
      <h2>Context Governance</h2>
      {_table(['Concept', 'Display', 'State', 'Action', 'Boundary note'], _context_rows(vm['context_governance']), 'No context governance items.')}
    </section>
    <section>
      <h2>Missing/Degraded Inputs</h2>
      {_table(['Concept', 'Display', 'Route', 'State', 'Missing inputs', 'Degraded inputs'], _missing_rows(vm['missing_or_degraded_inputs']), 'No missing or degraded inputs.')}
    </section>
    <footer>
      <p>Operator usage: <code>python3 scripts/render_operator_packet_viewer.py --view-model qa/examples/operator_packet_view_model.example.json --output-html qa/examples/operator_packet_viewer.example.html</code></p>
    </footer>
  </main>
</body>
</html>
"""
    return html


def write_operator_packet_html(path: str | Path, html: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
