"""Build validated market snapshot inputs from local normalized source files.

This is a static source-data mapper for examples and tests. It does not fetch
live data, implement detector decisions, add calibration values, or create any
execution behavior.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from traders_market_read.detectors.calibrated import CALIBRATED_DETECTORS
from traders_market_read.detectors.computable import COMPUTABLE_DETECTORS
from traders_market_read.detectors.output import find_forbidden_fields
from traders_market_read.input.market_snapshot import (
    MarketSnapshotInputError,
    validate_market_snapshot_payload,
)


class MarketSnapshotBuilderError(RuntimeError):
    """Raised when source data cannot safely produce a market snapshot."""


@dataclass(frozen=True)
class MarketSnapshotBuildResult:
    snapshot: dict[str, Any]
    detector_input_blocks_written: int
    computable_blocks_written: int
    calibrated_blocks_written: int


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise MarketSnapshotBuilderError(f"missing required source file: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MarketSnapshotBuilderError(f"{label} is not valid JSON: {exc}") from exc
    except OSError as exc:
        raise MarketSnapshotBuilderError(f"could not read {label} {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise MarketSnapshotBuilderError(f"{label} must be a JSON object")
    _reject_forbidden(data, label)
    return data


def _reject_forbidden(value: Any, label: str) -> None:
    forbidden = find_forbidden_fields(value)
    if forbidden:
        raise MarketSnapshotBuilderError(
            f"forbidden execution field present in {label}: " + ", ".join(forbidden)
        )


def _num(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MarketSnapshotBuilderError(f"{label} must be numeric")
    return float(value)


def _require(data: dict[str, Any], key: str, label: str) -> Any:
    if key not in data or data[key] in (None, ""):
        raise MarketSnapshotBuilderError(f"{label} missing required field: {key}")
    return data[key]


def _load_csv(path: Path, label: str, required_columns: tuple[str, ...]) -> list[dict[str, Any]]:
    if not path.exists():
        raise MarketSnapshotBuilderError(f"missing required source file: {path}")
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise MarketSnapshotBuilderError(f"{label} must include a header row")
            missing = [column for column in required_columns if column not in reader.fieldnames]
            if missing:
                raise MarketSnapshotBuilderError(
                    f"{label} missing required column(s): " + ", ".join(missing)
                )
            rows = [dict(row) for row in reader]
    except csv.Error as exc:
        raise MarketSnapshotBuilderError(f"{label} is malformed CSV: {exc}") from exc
    except OSError as exc:
        raise MarketSnapshotBuilderError(f"could not read {label} {path}: {exc}") from exc
    if not rows:
        raise MarketSnapshotBuilderError(f"{label} must contain at least one data row")
    _reject_forbidden(rows, label)
    return rows


def _float_cell(row: dict[str, Any], column: str, label: str) -> float:
    value = row.get(column)
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise MarketSnapshotBuilderError(
            f"{label} column {column} must be numeric, got {value!r}"
        ) from exc


def _bars(rows: list[dict[str, Any]], session: str) -> list[dict[str, float]]:
    bars: list[dict[str, float]] = []
    for index, row in enumerate(rows):
        if row.get("session") != session:
            continue
        label = f"session_bars[{index}]"
        high = _float_cell(row, "high", label)
        low = _float_cell(row, "low", label)
        if high < low:
            raise MarketSnapshotBuilderError(f"{label} has high < low")
        bars.append(
            {
                "open": _float_cell(row, "open", label),
                "high": high,
                "low": low,
                "close": _float_cell(row, "close", label),
                "volume": _float_cell(row, "volume", label),
            }
        )
    if not bars:
        raise MarketSnapshotBuilderError(f"session_bars has no rows for session={session}")
    return bars


def _period_bars(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{**bar, "complete": True} for bar in _bars(rows, "period")]


def _profile_levels(rows: list[dict[str, Any]]) -> list[dict[str, float]]:
    levels: list[dict[str, float]] = []
    for index, row in enumerate(rows):
        label = f"profile_rows[{index}]"
        levels.append(
            {
                "price": _float_cell(row, "price", label),
                "volume": _float_cell(row, "volume", label),
                "tpo": _float_cell(row, "tpo", label),
            }
        )
    levels.sort(key=lambda level: level["price"])
    return levels


def _value_area(data: dict[str, Any], prefix: str) -> dict[str, float]:
    return {
        "vah": _num(_require(data, f"{prefix}_vah", "value_areas"), f"{prefix}_vah"),
        "val": _num(_require(data, f"{prefix}_val", "value_areas"), f"{prefix}_val"),
        "poc": _num(_require(data, f"{prefix}_poc", "value_areas"), f"{prefix}_poc"),
    }


def _high_low(high: Any, low: Any) -> dict[str, float]:
    high_num = _num(high, "high")
    low_num = _num(low, "low")
    if high_num < low_num:
        raise MarketSnapshotBuilderError("high/low pair has high < low")
    return {"high": high_num, "low": low_num}


def _plain_bars(bars: list[dict[str, float]]) -> list[dict[str, float]]:
    return [{"high": b["high"], "low": b["low"], "close": b["close"]} for b in bars]


def _bid_ask_quotes(tape: dict[str, Any]) -> list[dict[str, float]]:
    quotes = _require(tape, "bid_ask_quotes", "tape_metrics")
    if not isinstance(quotes, list) or not quotes:
        raise MarketSnapshotBuilderError("tape_metrics.bid_ask_quotes must be a non-empty list")
    normalized: list[dict[str, float]] = []
    for index, quote in enumerate(quotes):
        if not isinstance(quote, dict):
            raise MarketSnapshotBuilderError(f"bid_ask_quotes[{index}] must be an object")
        normalized.append(
            {
                "bid": _num(quote.get("bid"), f"bid_ask_quotes[{index}].bid"),
                "ask": _num(quote.get("ask"), f"bid_ask_quotes[{index}].ask"),
            }
        )
    return normalized


def _num_list(data: dict[str, Any], key: str, label: str) -> list[float]:
    value = _require(data, key, label)
    if not isinstance(value, list) or not value:
        raise MarketSnapshotBuilderError(f"{label}.{key} must be a non-empty list")
    return [_num(item, f"{label}.{key}[{index}]") for index, item in enumerate(value)]


def _market_context(data: dict[str, Any]) -> dict[str, Any]:
    required = ("instrument", "session", "timeframe", "data_window")
    missing = [field for field in required if not data.get(field)]
    if missing:
        raise MarketSnapshotBuilderError(
            "market_context missing required field(s): " + ", ".join(missing)
        )
    allowed = {"instrument", "session", "timeframe", "data_window", "as_of", "source", "notes"}
    return {key: data[key] for key in sorted(data) if key in allowed}


def _build_detector_inputs(
    context: dict[str, Any],
    levels: dict[str, Any],
    session_rows: list[dict[str, Any]],
    value_areas: dict[str, Any],
    profile_rows: list[dict[str, Any]],
    tape: dict[str, Any],
    intermarket: dict[str, Any],
) -> dict[str, Any]:
    current_bars = _bars(session_rows, "current")
    prior_bars = _bars(session_rows, "prior")
    rth_bars = _bars(session_rows, "rth")
    asia_bars = _plain_bars(_bars(session_rows, "asia"))
    period_bars = _period_bars(session_rows)
    levels_rows = _profile_levels(profile_rows)
    volume_levels = [{"price": r["price"], "volume": r["volume"]} for r in levels_rows]
    tpo_levels = [
        {"price": r["price"], "tpo": r["tpo"], "tpo_count": r["tpo"]}
        for r in levels_rows
    ]

    session_clock = {
        "session_label": context["session"],
        "rth_open_index": 0,
        "ib_window_complete": True,
        "note": "Example static session boundaries only.",
    }
    detector_inputs: dict[str, Any] = {
        "session_clock": session_clock,
        "current_session_bars": current_bars,
        "prior_session_bars": prior_bars,
        "rth_session_bars": rth_bars,
        "tpo_profile": {"levels": tpo_levels},
        "tpo_period_definition": {"period_unit": context["timeframe"]},
        "profile_distribution": volume_levels,
        "current_value_area": _value_area(value_areas, "current"),
        "prior_value_area": _value_area(value_areas, "prior"),
        "developing_value_area": _value_area(value_areas, "developing"),
        "price_sequence": [bar["close"] for bar in current_bars],
        "intraday_trade_price": [bar["close"] for bar in current_bars],
        "intraday_traded_volume": [bar["volume"] for bar in current_bars],
        "period_bars": period_bars,
        "period_definition": {"period_unit": context["timeframe"]},
        "rth_open_price": _num(_require(levels, "rth_open", "structural_levels"), "rth_open"),
        "overnight_high_low": _high_low(levels["overnight_high"], levels["overnight_low"]),
        "prior_rth_high_low": _high_low(levels["prior_high"], levels["prior_low"]),
        "prior_value_references": _value_area(value_areas, "prior"),
        "current_session_high_low": _high_low(levels["session_high"], levels["session_low"]),
        "prior_session_high_low": _high_low(levels["prior_high"], levels["prior_low"]),
    }

    ref = _num(levels["reference_level"], "reference_level")
    breakout = _num(levels["breakout_level"], "breakout_level")
    ladder = _num_list(levels, "structural_level_ladder", "structural_levels")
    detector_inputs.update(
        {
            "ch02_acceptance_vs_rejection": {
                "structural_level": ref,
                "trade_price_sequence": _num_list(levels, "acceptance_sequence", "structural_levels"),
                "session_clock": session_clock,
            },
            "ch02_break_quality": {
                "price_sequence": _num_list(levels, "break_quality_sequence", "structural_levels"),
                "structural_reference": ref,
            },
            "ch02_breakout_continuation_vs_breakout_failure": {
                "structural_level": breakout,
                "price_sequence": _num_list(levels, "breakout_sequence", "structural_levels"),
            },
            "ch02_level_magnetism_and_decay": {
                "structural_level": ref,
                "price_sequence": _num_list(levels, "magnetism_sequence", "structural_levels"),
            },
            "ch02_level_test_sequence": {
                "structural_level": ref,
                "price_sequence": _num_list(levels, "level_test_sequence", "structural_levels"),
            },
            "ch02_liquidity_sweep_vs_real_break": {
                "structural_level": ref,
                "price_sequence": _num_list(levels, "liquidity_sweep_sequence", "structural_levels"),
            },
            "ch02_polarity_flip": {
                "broken_structural_level": breakout,
                "post_break_price_sequence": _num_list(levels, "polarity_flip_sequence", "structural_levels"),
            },
            "ch03_auction_acceptance_vs_rejection": {
                "price_sequence": _num_list(levels, "auction_price_sequence", "structural_levels"),
                "profile_distribution": {"levels": volume_levels},
                "auction_reference_area": {
                    "high": _num(value_areas["auction_reference_high"], "auction_reference_high"),
                    "low": _num(value_areas["auction_reference_low"], "auction_reference_low"),
                },
            },
            "ch03_completed_failed_and_unfinished_auctions": {
                "market_profile_or_tpo": {"levels": tpo_levels},
                "price_sequence": _num_list(levels, "completed_auction_sequence", "structural_levels"),
            },
            "ch03_excess_vs_poor_highs_lows": {
                "tpo_or_market_profile": {"levels": tpo_levels},
                "price_sequence": _num_list(levels, "excess_sequence", "structural_levels"),
            },
            "ch03_price_outside_value_acceptance_test": {
                "value_area_references": {
                    "vah": _num(value_areas["prior_vah"], "prior_vah"),
                    "val": _num(value_areas["prior_val"], "prior_val"),
                },
                "price_sequence": _num_list(levels, "outside_value_sequence", "structural_levels"),
                "volume_at_price_or_tpo": {"levels": volume_levels},
            },
            "ch03_the_auction_framework": {"price_bar_structure": _plain_bars(current_bars)},
            "ch03_volume_nodes_and_air_pockets": {
                "volume_at_price_distribution": {"levels": volume_levels},
                "price_path": _num_list(levels, "volume_node_path", "structural_levels"),
            },
            "ch04_spread_behavior": {"bid_ask_quotes": _bid_ask_quotes(tape)},
            "ch04_stall_and_snap_back": {
                "price_sequence": _num_list(levels, "stall_sequence", "structural_levels"),
                "structural_reference": _num(levels["prior_resistance"], "prior_resistance"),
            },
            "ch04_sweeps_through_liquidity": {
                "price_sequence": _num_list(levels, "sweep_through_sequence", "structural_levels"),
                "structural_levels": ladder[:5],
            },
            "ch04_tape_quality_spectrum": {
                "tick_or_bar_sequence": _plain_bars(current_bars),
                "spread_history": _num_list(tape, "spread_history", "tape_metrics"),
            },
            "ch05_follow_through_and_failure": {
                "price_bars": _plain_bars(current_bars),
                "structural_reference": ref,
            },
            "ch05_impulse_vs_grind": {"price_bars": _plain_bars(current_bars)},
            "ch06_stop_out_cascades_and_liquidation": {
                "price_sequence": _num_list(levels, "cascade_sequence", "structural_levels"),
                "structural_levels": ladder,
                "velocity_and_volume_series": {
                    "velocity": _num_list(tape, "velocity_series", "tape_metrics"),
                    "volume": _num_list(tape, "volume_series", "tape_metrics"),
                },
            },
            "ch07_asia_session_character": {
                "asia_session_bars": asia_bars,
                "asia_volume_series": [bar["volume"] for bar in _bars(session_rows, "asia")],
            },
            "ch08_compression_breakouts_real_vs_false": {
                "price_bars": _plain_bars(current_bars),
                "structural_range": {"high": 5006.0, "low": 4999.0},
            },
            "ch08_compression_vs_expansion": {
                "range_statistics": {
                    "recent_range": _num(tape["compressed_range_recent"], "compressed_range_recent"),
                    "baseline_range": _num(tape["compressed_range_baseline"], "compressed_range_baseline"),
                },
                "realized_volatility_series": _num_list(tape, "compressed_volatility_series", "tape_metrics"),
            },
            "ch08_expanded_volatility_no_trade_condition": {
                "spread_series": _num_list(tape, "spread_series", "tape_metrics"),
                "depth_series": _num_list(tape, "depth_series", "tape_metrics"),
                "realized_volatility_series": _num_list(tape, "realized_volatility_series", "tape_metrics"),
            },
            "ch08_volatility_crush_and_reset": {
                "realized_volatility_series": _num_list(tape, "volatility_crush_series", "tape_metrics"),
                "range_series": _num_list(tape, "range_series", "tape_metrics"),
                "spread_series": _num_list(tape, "spread_history", "tape_metrics"),
                "event_timing_context": {
                    "event_label": str(tape.get("event_label", "example_static_event")),
                    "samples_since_event": _num(tape["samples_since_event"], "samples_since_event"),
                },
            },
            "ch09_breadth_confirmation_and_divergence": {
                "cash_index": intermarket["cash_index"],
                "constituent_advance_decline": intermarket["constituent_advance_decline"],
                "equal_weight_data": intermarket["equal_weight_data"],
            },
            "ch12_execution_environment_quality_and_veto": {
                "spread": _num(levels["current_spread"], "current_spread"),
                "depth": _num(levels["depth"], "depth"),
                "realized_volatility": _num(tape["realized_volatility_series"][-1], "realized_volatility"),
                "event_calendar": {
                    "event_label": "none",
                    "minutes_to_event": _num(tape["minutes_to_event"], "minutes_to_event"),
                },
            },
        }
    )
    return detector_inputs


def build_market_snapshot_from_sources(
    *,
    market_context_path: str | Path,
    structural_levels_path: str | Path,
    session_bars_path: str | Path,
    value_areas_path: str | Path,
    profile_rows_path: str | Path,
    tape_metrics_path: str | Path,
    intermarket_metrics_path: str | Path,
) -> MarketSnapshotBuildResult:
    """Build and validate a market snapshot from local normalized source files."""
    market_context = _market_context(
        _load_json(Path(market_context_path), "market_context")
    )
    structural_levels = _load_json(Path(structural_levels_path), "structural_levels")
    value_areas = _load_json(Path(value_areas_path), "value_areas")
    tape_metrics = _load_json(Path(tape_metrics_path), "tape_metrics")
    intermarket_metrics = _load_json(Path(intermarket_metrics_path), "intermarket_metrics")
    session_rows = _load_csv(
        Path(session_bars_path),
        "session_bars",
        ("period", "session", "open", "high", "low", "close", "volume"),
    )
    profile_rows = _load_csv(
        Path(profile_rows_path),
        "profile_rows",
        ("price", "volume", "tpo"),
    )

    detector_inputs = _build_detector_inputs(
        market_context,
        structural_levels,
        session_rows,
        value_areas,
        profile_rows,
        tape_metrics,
        intermarket_metrics,
    )
    if not detector_inputs:
        raise MarketSnapshotBuilderError("unable to build any implemented detector inputs")

    calibrated_ids = set(CALIBRATED_DETECTORS)
    snapshot = {
        "schema_version": 1,
        "market_context": market_context,
        "detector_inputs": detector_inputs,
    }
    try:
        validate_market_snapshot_payload(snapshot)
    except MarketSnapshotInputError as exc:
        raise MarketSnapshotBuilderError(f"generated snapshot failed validation: {exc}") from exc
    _reject_forbidden(snapshot, "generated snapshot")

    return MarketSnapshotBuildResult(
        snapshot=snapshot,
        detector_input_blocks_written=len(detector_inputs),
        computable_blocks_written=len(COMPUTABLE_DETECTORS),
        calibrated_blocks_written=sum(1 for key in calibrated_ids if key in detector_inputs),
    )


def write_market_snapshot(path: str | Path, snapshot: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
