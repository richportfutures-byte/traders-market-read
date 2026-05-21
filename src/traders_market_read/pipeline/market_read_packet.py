"""Build a complete non-executional market-read review packet.

The pipeline only orchestrates existing components:

- detector runtime
- detector output validation
- runtime summary JSON
- review packet Markdown

It does not add detector logic, calibration values, trade permission, order
behavior, sizing, broker/account/fill/P&L behavior, or autonomous execution.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from traders_market_read.detectors.calibration import CalibrationError, load_calibration_profile
from traders_market_read.detectors.catalog import CatalogError, DetectorCatalog, load_catalog
from traders_market_read.detectors.output import find_forbidden_fields, validate_output_payload
from traders_market_read.detectors.runtime import run
from traders_market_read.reporting.runtime_summary import (
    RuntimeSummaryError,
    build_runtime_summary,
    render_review_packet_markdown,
)


class MarketReadPacketError(RuntimeError):
    """Raised when the one-command packet pipeline fails closed."""


@dataclass(frozen=True)
class MarketReadPacketResult:
    runtime_output_path: Path
    summary_json_path: Path
    review_markdown_path: Path
    total_contracts: int
    total_outputs: int
    refusal_count: int
    non_refusal_count: int
    review_queue_count: int
    calibrated_non_refusal_count: int
    computable_non_refusal_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "runtime_output_path": str(self.runtime_output_path),
            "summary_json_path": str(self.summary_json_path),
            "review_markdown_path": str(self.review_markdown_path),
            "total_contracts": self.total_contracts,
            "total_outputs": self.total_outputs,
            "refusal_count": self.refusal_count,
            "non_refusal_count": self.non_refusal_count,
            "review_queue_count": self.review_queue_count,
            "calibrated_non_refusal_count": self.calibrated_non_refusal_count,
            "computable_non_refusal_count": self.computable_non_refusal_count,
        }


def _load_market_context(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise MarketReadPacketError(f"input file not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MarketReadPacketError(f"input file is not valid JSON: {exc}") from exc
    except OSError as exc:
        raise MarketReadPacketError(f"could not read input file {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise MarketReadPacketError("input fixture must be a JSON object")
    if "market_context" in raw:
        market_context = raw["market_context"]
        if not isinstance(market_context, dict):
            raise MarketReadPacketError("input fixture 'market_context' must be a JSON object")
        return market_context
    return raw


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _validate_outputs(outputs: list[dict[str, Any]], catalog: DetectorCatalog) -> None:
    errors: list[str] = []
    for index, output in enumerate(outputs):
        concept_id = output.get("concept_id")
        if not isinstance(concept_id, str) or not concept_id:
            errors.append(f"[{index}] concept_id must be a non-empty string")
            continue
        try:
            contract = catalog.get(concept_id)
        except CatalogError as exc:
            errors.append(f"[{index}] {exc}")
            continue
        for error in validate_output_payload(output, contract):
            errors.append(f"[{index}] {concept_id}: {error}")
    if errors:
        raise MarketReadPacketError(
            "detector output validation failed: " + "; ".join(errors)
        )


def _assert_no_forbidden_json_fields(value: Any, label: str) -> None:
    forbidden = find_forbidden_fields(value)
    if forbidden:
        raise MarketReadPacketError(
            f"forbidden execution field present in {label}: " + ", ".join(forbidden)
        )


def _assert_no_forbidden_markdown_fields(markdown: str) -> None:
    # The boundary section must mention broker/order/account behavior in prose.
    # This check therefore looks for serialized field-style keys, not ordinary
    # boundary language.
    field_markers = (
        "entry_price",
        "stop_price",
        "target_price",
        "order_type",
        "position_size",
        "account_id",
        "fill_price",
        "buy_now",
        "sell_now",
        "place_order",
        "reduce_position",
        "add_position",
    )
    lower = markdown.lower()
    found = [marker for marker in field_markers if marker in lower]
    if found:
        raise MarketReadPacketError(
            "forbidden execution field marker present in review Markdown: "
            + ", ".join(found)
        )


def build_market_read_packet(
    input_json_path: str | Path,
    *,
    runtime_output_path: str | Path,
    summary_json_path: str | Path,
    review_markdown_path: str | Path,
    calibration_profile_path: str | Path | None = None,
) -> MarketReadPacketResult:
    """Run runtime -> validation -> summary JSON -> review Markdown."""
    input_path = Path(input_json_path)
    runtime_path = Path(runtime_output_path)
    summary_path = Path(summary_json_path)
    review_path = Path(review_markdown_path)

    market_context = _load_market_context(input_path)
    _assert_no_forbidden_json_fields(market_context, "input fixture")

    try:
        catalog = load_catalog()
    except CatalogError as exc:
        raise MarketReadPacketError(f"catalog error: {exc}") from exc

    calibration_profile = None
    if calibration_profile_path is not None:
        try:
            calibration_profile = load_calibration_profile(calibration_profile_path)
        except CalibrationError as exc:
            raise MarketReadPacketError(f"calibration profile error: {exc}") from exc

    try:
        runtime_report = run(
            market_context,
            catalog=catalog,
            calibration_profile=calibration_profile,
        )
    except (CatalogError, CalibrationError, RuntimeError, ValueError) as exc:
        raise MarketReadPacketError(f"runtime failure: {exc}") from exc

    if not runtime_report.ok:
        raise MarketReadPacketError(
            "runtime output validation failed: "
            + "; ".join(runtime_report.validation_errors)
        )

    _assert_no_forbidden_json_fields(runtime_report.outputs, "runtime output")
    _validate_outputs(runtime_report.outputs, catalog)
    _write_json(runtime_path, runtime_report.outputs)

    try:
        summary = build_runtime_summary(runtime_path)
        review_markdown = render_review_packet_markdown(runtime_path, summary)
    except RuntimeSummaryError as exc:
        raise MarketReadPacketError(f"summary generation failed: {exc}") from exc

    _assert_no_forbidden_json_fields(summary, "summary JSON")
    _assert_no_forbidden_markdown_fields(review_markdown)
    _write_json(summary_path, summary)
    _write_text(review_path, review_markdown)

    return MarketReadPacketResult(
        runtime_output_path=runtime_path,
        summary_json_path=summary_path,
        review_markdown_path=review_path,
        total_contracts=int(summary["total_contracts"]),
        total_outputs=int(summary["total_outputs"]),
        refusal_count=int(summary["refusal_count"]),
        non_refusal_count=int(summary["non_refusal_count"]),
        review_queue_count=int(summary["judgment_assisted_review_count"]),
        calibrated_non_refusal_count=int(summary["calibrated_non_refusal_count"]),
        computable_non_refusal_count=int(summary["computable_non_refusal_count"]),
    )
