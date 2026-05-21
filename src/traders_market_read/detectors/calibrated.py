"""Real calibrated structural behaviour for the CALIBRATED detector contracts.

Every CALIBRATED contract in the catalog has a fixed rule structure whose
thresholds are named parameters supplied by a calibration profile. This module
implements that fixed rule structure for each contract: it reads explicit
fixture inputs, reads the contract's calibrated thresholds from the profile,
applies a deterministic structural comparison, and emits a catalog-allowed
state.

It invents no thresholds (every threshold comes from the profile), infers no
motive/trend/reversal/setup-quality/opportunity, and emits no executional
output. When a required fixture field or calibration value is absent, the
detector refuses safely.
"""

from __future__ import annotations

import statistics
from typing import Any, Callable, NamedTuple

from .calibration import CalibrationError, CalibrationProfile
from .catalog import DetectorContract
from .output import make_output
from .refusal import select_safe_action, select_safe_state


class _DataError(Exception):
    """Raised when a required fixture field is present but structurally unusable."""


# ---------------------------------------------------------------------------
# Fixture-access helpers
# ---------------------------------------------------------------------------

def _present(block: dict[str, Any], name: str) -> bool:
    if name not in block:
        return False
    value = block[name]
    if value is None:
        return False
    if isinstance(value, (list, dict, str)) and len(value) == 0:
        return False
    return True


def _num(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _DataError(f"{label} must be a number, got {value!r}")
    return float(value)


def _num_list(value: Any, label: str) -> list[float]:
    if not isinstance(value, list) or not value:
        raise _DataError(f"{label} must be a non-empty list of numbers")
    return [_num(item, f"{label}[{i}]") for i, item in enumerate(value)]


def _bars(value: Any, label: str) -> list[dict[str, float]]:
    if not isinstance(value, list) or not value:
        raise _DataError(f"{label} must be a non-empty list of bars")
    bars: list[dict[str, float]] = []
    for i, bar in enumerate(value):
        if not isinstance(bar, dict):
            raise _DataError(f"{label}[{i}] must be an object")
        high = _num(bar.get("high"), f"{label}[{i}].high")
        low = _num(bar.get("low"), f"{label}[{i}].low")
        if high < low:
            raise _DataError(f"{label}[{i}] has high < low")
        entry = {"high": high, "low": low}
        if "close" in bar:
            entry["close"] = _num(bar.get("close"), f"{label}[{i}].close")
        bars.append(entry)
    return bars


def _param_num(params: dict[str, Any], name: str) -> float:
    value = params.get(name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _DataError(f"calibration parameter {name} must be numeric, got {value!r}")
    return float(value)


def _param_obj(params: dict[str, Any], name: str) -> dict[str, Any]:
    value = params.get(name)
    if not isinstance(value, dict) or not value:
        raise _DataError(f"calibration parameter {name} must be a non-empty object")
    return value


def _obj_num(obj: dict[str, Any], key: str, param_name: str) -> float:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _DataError(f"calibration parameter {param_name}.{key} must be numeric")
    return float(value)


# ---------------------------------------------------------------------------
# Shared structural feature extractors
# ---------------------------------------------------------------------------

class _LevelInteraction(NamedTuple):
    side: str
    max_run: int
    peak_excursion: float
    peak_above: float
    peak_below: float
    ever_beyond: bool
    first_beyond: int
    reclaimed: bool
    reclaim_index: int
    crossings: int
    final: float


def _level_interaction(seq: list[float], level: float, buffer: float) -> _LevelInteraction:
    """Summarize how a price sequence interacts with a structural level.

    A sample is "beyond" when it clears ``level`` by at least ``buffer`` on a
    side. The dominant side is the side with the larger peak excursion.
    """
    peak_above = max(p - level for p in seq)
    peak_below = max(level - p for p in seq)
    side = "above" if peak_above >= peak_below else "below"
    target = 1 if side == "above" else -1

    flags = [
        1 if p > level + buffer else (-1 if p < level - buffer else 0)
        for p in seq
    ]
    best = current = 0
    first_beyond = -1
    for index, flag in enumerate(flags):
        if flag == target:
            current += 1
            best = max(best, current)
            if first_beyond < 0:
                first_beyond = index
        else:
            current = 0

    reclaimed = False
    reclaim_index = -1
    if first_beyond >= 0:
        for index in range(first_beyond, len(seq)):
            if (side == "above" and seq[index] < level) or (
                side == "below" and seq[index] > level
            ):
                reclaimed = True
                reclaim_index = index
                break

    crossings = 0
    for index in range(1, len(seq)):
        if (seq[index - 1] - level) * (seq[index] - level) < 0:
            crossings += 1

    return _LevelInteraction(
        side=side,
        max_run=best,
        peak_excursion=max(peak_above, peak_below),
        peak_above=peak_above,
        peak_below=peak_below,
        ever_beyond=first_beyond >= 0,
        first_beyond=first_beyond,
        reclaimed=reclaimed,
        reclaim_index=reclaim_index,
        crossings=crossings,
        final=seq[-1],
    )


def _window_ratio(series: list[float]) -> tuple[float, float]:
    """Return (recent-window mean, early-window mean) of a numeric series."""
    n = len(series)
    span = max(1, n // 3)
    early = statistics.fmean(series[:span])
    recent = statistics.fmean(series[-span:])
    return recent, early


def _spreads(quotes: Any, label: str) -> list[float]:
    """Extract a spread series from bid/ask quote objects or a raw number list."""
    if not isinstance(quotes, list) or not quotes:
        raise _DataError(f"{label} must be a non-empty list")
    spreads: list[float] = []
    for i, quote in enumerate(quotes):
        if isinstance(quote, dict):
            bid = _num(quote.get("bid"), f"{label}[{i}].bid")
            ask = _num(quote.get("ask"), f"{label}[{i}].ask")
            if ask < bid:
                raise _DataError(f"{label}[{i}] has ask < bid")
            spreads.append(ask - bid)
        else:
            spreads.append(_num(quote, f"{label}[{i}]"))
    return spreads


def _overlap_fraction(bars: list[dict[str, float]]) -> float:
    """Average bar-to-bar overlap as a fraction of bar range."""
    if len(bars) < 2:
        return 1.0
    fractions: list[float] = []
    for i in range(1, len(bars)):
        prev, cur = bars[i - 1], bars[i]
        overlap = min(prev["high"], cur["high"]) - max(prev["low"], cur["low"])
        span = cur["high"] - cur["low"]
        fractions.append(max(0.0, overlap) / span if span > 0 else 1.0)
    return statistics.fmean(fractions)


def _profile_levels(value: Any, label: str) -> list[dict[str, float]]:
    """Normalize a profile distribution into sorted [{price, volume, tpo}]."""
    raw = value.get("levels") if isinstance(value, dict) else value
    if not isinstance(raw, list) or not raw:
        raise _DataError(f"{label} must provide a non-empty list of price levels")
    levels: list[dict[str, float]] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise _DataError(f"{label}[{i}] must be an object")
        price = _num(item.get("price"), f"{label}[{i}].price")
        entry = {"price": price}
        if "volume" in item:
            entry["volume"] = _num(item.get("volume"), f"{label}[{i}].volume")
        if "tpo" in item:
            entry["tpo"] = _num(item.get("tpo"), f"{label}[{i}].tpo")
        levels.append(entry)
    levels.sort(key=lambda lv: lv["price"])
    return levels


# ---------------------------------------------------------------------------
# Family A — level interaction detectors
# ---------------------------------------------------------------------------

def _classify_acceptance_vs_rejection(block, params):
    level = _num(block["structural_level"], "structural_level")
    seq = _num_list(block["trade_price_sequence"], "trade_price_sequence")
    dwell = _param_num(params, "acceptance_dwell_time")
    buffer = _param_num(params, "level_buffer")
    fail_window = _param_num(params, "failed_acceptance_window")
    li = _level_interaction(seq, level, buffer)
    measurements = {
        "level": level, "dominant_side": li.side, "max_dwell_beyond": li.max_run,
        "peak_excursion": li.peak_excursion, "reclaimed": li.reclaimed,
    }
    if not li.ever_beyond:
        return "REJECTED", measurements
    if li.max_run >= dwell:
        if li.reclaimed and (li.reclaim_index - li.first_beyond) <= fail_window:
            return "FAILED_ACCEPTANCE", measurements
        return ("ACCEPTED_ABOVE" if li.side == "above" else "ACCEPTED_BELOW"), measurements
    if li.reclaimed:
        return "REJECTED", measurements
    return "PENDING", measurements


def _classify_break_quality(block, params):
    seq = _num_list(block["price_sequence"], "price_sequence")
    reference = _num(block["structural_reference"], "structural_reference")
    req = _param_obj(params, "break_quality_classification_requirement")
    clean_min = _obj_num(req, "clean_displacement_min", "break_quality_classification_requirement")
    dirty_max = _obj_num(req, "dirty_crossing_max", "break_quality_classification_requirement")
    impulse_min = _obj_num(req, "impulse_velocity_min", "break_quality_classification_requirement")
    li = _level_interaction(seq, reference, 0.0)
    velocity = li.peak_excursion / (li.first_beyond + 1) if li.first_beyond >= 0 else 0.0
    measurements = {
        "displacement": li.peak_excursion, "crossings": li.crossings, "velocity": velocity,
    }
    if li.crossings >= dirty_max:
        return "DIRTY_BREAK_TEXTURE", measurements
    if li.peak_excursion >= clean_min:
        if velocity >= impulse_min:
            return "IMPULSIVE_BREAK_TEXTURE", measurements
        return "CLEAN_BREAK_TEXTURE", measurements
    return "GRINDING_BREAK_TEXTURE", measurements


def _classify_breakout_continuation(block, params):
    level = _num(block["structural_level"], "structural_level")
    seq = _num_list(block["price_sequence"], "price_sequence")
    clear = _param_num(params, "break_clear_buffer")
    extension = _param_num(params, "extension_requirement")
    fail_window = _param_num(params, "failure_return_window")
    li = _level_interaction(seq, level, clear)
    measurements = {
        "level": level, "peak_excursion": li.peak_excursion, "max_run": li.max_run,
        "reclaimed": li.reclaimed,
    }
    if not li.ever_beyond:
        return "BREAKOUT_PENDING", measurements
    if li.reclaimed and (li.reclaim_index - li.first_beyond) <= fail_window:
        return "BREAKOUT_FAILURE", measurements
    if li.peak_excursion >= extension:
        return "BREAKOUT_CONTINUATION", measurements
    if li.max_run >= 2 and not li.reclaimed:
        return "BREAKOUT_RETEST_HELD", measurements
    return "STRUCTURAL_FOLLOW_THROUGH_ONLY", measurements


def _classify_level_magnetism(block, params):
    level = _num(block["structural_level"], "structural_level")
    seq = _num_list(block["price_sequence"], "price_sequence")
    req = _param_obj(params, "level_magnetism_and_decay_classification_requirement")
    drift_min = _obj_num(req, "magnetism_drift_min", "level_magnetism_and_decay_classification_requirement")
    overshoot_max = _obj_num(req, "overshoot_excursion_max", "level_magnetism_and_decay_classification_requirement")
    li = _level_interaction(seq, level, 0.0)
    drift = abs(seq[0] - level) - abs(seq[-1] - level)
    crossed = li.crossings > 0
    measurements = {
        "level": level, "drift_toward_level": drift, "crossed_level": crossed,
        "peak_excursion": li.peak_excursion,
    }
    if crossed and li.peak_excursion <= overshoot_max:
        return "LEVEL_OVERSHOOT_CONTEXT", measurements
    if not crossed and drift >= drift_min:
        return "LEVEL_MAGNETISM_CONTEXT", measurements
    if not crossed and drift < 0:
        return "LEVEL_FRONT_RUN_CONTEXT", measurements
    return "TEST_HISTORY_REQUIRED", measurements


def _classify_level_test_sequence(block, params):
    level = _num(block["structural_level"], "structural_level")
    seq = _num_list(block["price_sequence"], "price_sequence")
    separation = _param_num(params, "test_separation_requirement")
    reaction_req = _param_num(params, "reaction_quality_requirement")
    decay_count = _param_num(params, "decay_review_count_policy")
    buffer = _param_num(params, "level_buffer")
    reactions: list[float] = []
    last_test = -(10 ** 9)
    for index, price in enumerate(seq):
        if abs(price - level) <= buffer and (index - last_test) >= separation:
            window = seq[index : index + 5]
            reactions.append(max(abs(x - level) for x in window))
            last_test = index
    measurements = {"test_count": len(reactions), "reactions": reactions}
    if not reactions:
        return "INSUFFICIENT_EVIDENCE", measurements
    if len(reactions) == 1:
        return "FIRST_TEST_CONTEXT", measurements
    if len(reactions) >= decay_count:
        return "LEVEL_EXHAUSTION_REVIEW", measurements
    weakening = all(reactions[i] < reactions[i - 1] for i in range(1, len(reactions)))
    if weakening:
        return "REPEATED_TEST_DECAY", measurements
    if reactions[-1] >= reaction_req:
        return "REACTION_SUPPORTED", measurements
    return "TEST_COUNT_OBSERVED", measurements


def _classify_liquidity_sweep(block, params):
    level = _num(block["structural_level"], "structural_level")
    seq = _num_list(block["price_sequence"], "price_sequence")
    probe = _param_num(params, "sweep_probe_distance")
    reclaim_window = _param_num(params, "reclaim_window")
    hold_window = _param_num(params, "hold_beyond_level_window")
    li = _level_interaction(seq, level, 0.0)
    measurements = {
        "level": level, "peak_excursion": li.peak_excursion, "max_run": li.max_run,
        "reclaimed": li.reclaimed,
    }
    if not li.ever_beyond:
        return "SWEEP_RESOLUTION_PENDING", measurements
    if li.peak_excursion < probe:
        return "STRUCTURAL_SWEEP_ONLY", measurements
    if li.reclaimed and (li.reclaim_index - li.first_beyond) <= reclaim_window:
        return "SWEEP_RECLAIMED_FALSE_BREAK", measurements
    if li.max_run >= hold_window:
        return "SWEEP_HELD_REAL_BREAK_CONTEXT", measurements
    return "SWEEP_RESOLUTION_PENDING", measurements


def _classify_polarity_flip(block, params):
    level = _num(block["broken_structural_level"], "broken_structural_level")
    seq = _num_list(block["post_break_price_sequence"], "post_break_price_sequence")
    retest_window = _param_num(params, "retest_window")
    hold_req = _param_num(params, "hold_or_reject_requirement")
    buffer = _param_num(params, "level_buffer")
    broken_side = "above" if seq[0] > level else "below"
    retest_index = -1
    for index, price in enumerate(seq):
        if abs(price - level) <= buffer:
            retest_index = index
            break
    measurements = {
        "level": level, "broken_side": broken_side, "retest_index": retest_index,
    }
    if retest_index < 0 or retest_index > retest_window:
        return "RETEST_PENDING", measurements
    after = seq[retest_index:]
    if broken_side == "above":
        held = sum(1 for p in after if p >= level - buffer)
        crossed = any(p < level - buffer for p in after)
    else:
        held = sum(1 for p in after if p <= level + buffer)
        crossed = any(p > level + buffer for p in after)
    measurements["held_samples"] = held
    if held >= hold_req and not crossed:
        return "POLARITY_FLIP_CONFIRMED", measurements
    if crossed:
        on_broken_side_at_end = (
            seq[-1] > level if broken_side == "above" else seq[-1] < level
        )
        if on_broken_side_at_end:
            return "RECLAIM_CONFIRMED", measurements
        return "POLARITY_FLIP_FAILED", measurements
    return "STRUCTURAL_RETEST_ONLY", measurements


def _classify_stall_and_snap_back(block, params):
    seq = _num_list(block["price_sequence"], "price_sequence")
    reference = _num(block["structural_reference"], "structural_reference")
    duration = int(_param_num(params, "stall_duration_requirement"))
    progress_fail = _param_num(params, "progress_failure_requirement")
    snap_window = _param_num(params, "snapback_return_window")
    buffer = _param_num(params, "reference_buffer")
    duration = max(2, duration)
    stall_progress = None
    stall_end = -1
    for start in range(0, len(seq) - duration + 1):
        window = seq[start : start + duration]
        if min(abs(p - reference) for p in window) > buffer * 3:
            continue
        progress = max(window) - min(window)
        if stall_progress is None or progress < stall_progress:
            stall_progress = progress
            stall_end = start + duration - 1
    measurements = {"reference": reference, "min_window_progress": stall_progress}
    if stall_progress is None:
        return "STRUCTURAL_STALL_ONLY", measurements
    if stall_progress > progress_fail:
        return "STALL_PENDING", measurements
    after = seq[stall_end : stall_end + int(snap_window) + 1]
    if after and abs(after[-1] - reference) > buffer:
        return "SNAP_BACK_CONFIRMED", measurements
    return "STALL_OBSERVED", measurements


def _classify_follow_through(block, params):
    bars = _bars(block["price_bars"], "price_bars")
    reference = _num(block["structural_reference"], "structural_reference")
    extension = _param_num(params, "post_move_extension_requirement")
    hold_req = _param_num(params, "hold_beyond_reference_requirement")
    fail_window = _param_num(params, "failure_reclaim_window")
    closes = [bar.get("close", (bar["high"] + bar["low"]) / 2) for bar in bars]
    li = _level_interaction(closes, reference, 0.0)
    measurements = {
        "reference": reference, "peak_excursion": li.peak_excursion,
        "max_run": li.max_run, "reclaimed": li.reclaimed,
    }
    if not li.ever_beyond:
        return "FOLLOW_THROUGH_PENDING", measurements
    if li.reclaimed and (li.reclaim_index - li.first_beyond) <= fail_window:
        return "FOLLOW_THROUGH_FAILED", measurements
    if li.peak_excursion >= extension and li.max_run >= hold_req:
        return "FOLLOW_THROUGH_CONFIRMED", measurements
    if li.max_run >= hold_req:
        return "RETEST_HOLD_CONFIRMED", measurements
    return "STRUCTURAL_FOLLOW_THROUGH_ONLY", measurements


# ---------------------------------------------------------------------------
# Family B — auction / profile detectors
# ---------------------------------------------------------------------------

def _classify_auction_acceptance(block, params):
    seq = _num_list(block["price_sequence"], "price_sequence")
    levels = _profile_levels(block["profile_distribution"], "profile_distribution")
    area = block["auction_reference_area"]
    if not isinstance(area, dict):
        raise _DataError("auction_reference_area must be an object with high and low")
    area_high = _num(area.get("high"), "auction_reference_area.high")
    area_low = _num(area.get("low"), "auction_reference_area.low")
    buffer = _param_num(params, "auction_extension_buffer")
    dev_req = _param_num(params, "accepted_volume_development_requirement")
    return_window = _param_num(params, "rejection_return_window")
    extended_above = max(seq) > area_high + buffer
    extended_below = min(seq) < area_low - buffer
    total = sum(lv.get("volume", lv.get("tpo", 0.0)) for lv in levels) or 1.0
    outside = sum(
        lv.get("volume", lv.get("tpo", 0.0))
        for lv in levels
        if lv["price"] > area_high or lv["price"] < area_low
    )
    development = outside / total
    measurements = {
        "extended": extended_above or extended_below,
        "outside_development_fraction": development,
    }
    if not (extended_above or extended_below):
        return "AUCTION_PENDING", measurements
    if development >= dev_req:
        return "AUCTION_ACCEPTED", measurements
    returned = any(area_low <= p <= area_high for p in seq[-int(return_window) - 1 :])
    if returned:
        return "AUCTION_REJECTED", measurements
    return "CONFIRMATION_REQUIRED", measurements


def _classify_completed_auctions(block, params):
    levels = _profile_levels(block["market_profile_or_tpo"], "market_profile_or_tpo")
    seq = _num_list(block["price_sequence"], "price_sequence")
    excess_req = _param_num(params, "excess_tail_requirement")
    poor_req = _param_num(params, "poor_extreme_requirement")
    reclaim_window = _param_num(params, "failed_auction_reclaim_window")
    high_tail = 0
    for level in reversed(levels):
        if level.get("tpo", 9.0) <= 1.0:
            high_tail += 1
        else:
            break
    extreme_width = sum(1 for level in levels[-3:] if level.get("tpo", 0.0) >= poor_req)
    measurements = {"high_single_print_tail": high_tail, "flat_extreme_levels": extreme_width}
    li = _level_interaction(seq, levels[0]["price"], 0.0)
    if li.ever_beyond and li.reclaimed and (li.reclaim_index - li.first_beyond) <= reclaim_window:
        return "FAILED_AUCTION_CONTEXT", measurements
    if high_tail >= excess_req:
        return "COMPLETED_AUCTION", measurements
    if extreme_width >= 2:
        return "POOR_EXTREME_CONTEXT", measurements
    return "UNFINISHED_AUCTION", measurements


def _classify_excess_vs_poor(block, params):
    levels = _profile_levels(block["tpo_or_market_profile"], "tpo_or_market_profile")
    seq = _num_list(block["price_sequence"], "price_sequence")
    tail_req = _param_num(params, "single_print_tail_requirement")
    repeat_req = _param_num(params, "poor_extreme_repetition_requirement")
    speed_req = _param_num(params, "rejection_speed_requirement")
    high_tail = 0
    for level in reversed(levels):
        if level.get("tpo", 9.0) <= 1.0:
            high_tail += 1
        else:
            break
    low_tail = 0
    for level in levels:
        if level.get("tpo", 9.0) <= 1.0:
            low_tail += 1
        else:
            break
    rejection_speed = max(seq) - seq[-1]
    measurements = {
        "high_tail": high_tail, "low_tail": low_tail, "rejection_speed": rejection_speed,
    }
    if high_tail >= tail_req and rejection_speed >= speed_req:
        return "EXCESS_HIGH", measurements
    if low_tail >= tail_req and (seq[-1] - min(seq)) >= speed_req:
        return "EXCESS_LOW", measurements
    flat_high = sum(1 for level in levels[-3:] if level.get("tpo", 0.0) >= repeat_req)
    if flat_high >= 2:
        return "POOR_HIGH", measurements
    flat_low = sum(1 for level in levels[:3] if level.get("tpo", 0.0) >= repeat_req)
    if flat_low >= 2:
        return "POOR_LOW", measurements
    return "PROFILE_EXTREME_PENDING", measurements


def _classify_price_outside_value(block, params):
    refs = block["value_area_references"]
    if not isinstance(refs, dict):
        raise _DataError("value_area_references must be an object with vah and val")
    vah = _num(refs.get("vah"), "value_area_references.vah")
    val = _num(refs.get("val"), "value_area_references.val")
    seq = _num_list(block["price_sequence"], "price_sequence")
    levels = _profile_levels(block["volume_at_price_or_tpo"], "volume_at_price_or_tpo")
    buffer = _param_num(params, "outside_value_buffer")
    dev_req = _param_num(params, "acceptance_development_requirement")
    return_window = _param_num(params, "return_inside_window")
    outside_above = max(seq) > vah + buffer
    outside_below = min(seq) < val - buffer
    total = sum(lv.get("volume", lv.get("tpo", 0.0)) for lv in levels) or 1.0
    outside_vol = sum(
        lv.get("volume", lv.get("tpo", 0.0))
        for lv in levels
        if lv["price"] > vah or lv["price"] < val
    )
    development = outside_vol / total
    measurements = {
        "outside_value": outside_above or outside_below,
        "outside_development_fraction": development,
    }
    if not (outside_above or outside_below):
        return "OUTSIDE_VALUE_PENDING", measurements
    if development >= dev_req:
        return "OUTSIDE_VALUE_ACCEPTED", measurements
    returned = any(val <= p <= vah for p in seq[-int(return_window) - 1 :])
    if returned:
        return "RETURNED_INSIDE_VALUE", measurements
    return "OUTSIDE_VALUE_REJECTED", measurements


def _classify_auction_framework(block, params):
    bars = _bars(block["price_bar_structure"], "price_bar_structure")
    req = _param_obj(params, "the_auction_framework_classification_requirement")
    balance_min = _obj_num(req, "balance_overlap_min", "the_auction_framework_classification_requirement")
    imbalance_min = _obj_num(req, "imbalance_directional_min", "the_auction_framework_classification_requirement")
    overlap = _overlap_fraction(bars)
    mids = [(bar["high"] + bar["low"]) / 2 for bar in bars]
    total_span = max(bar["high"] for bar in bars) - min(bar["low"] for bar in bars)
    directional = abs(mids[-1] - mids[0]) / total_span if total_span > 0 else 0.0
    measurements = {"overlap_fraction": overlap, "directional_travel": directional}
    if overlap >= balance_min and directional < imbalance_min:
        return "BALANCED_AUCTION_CONTEXT", measurements
    if directional >= imbalance_min and overlap < balance_min:
        return "IMBALANCED_AUCTION_CONTEXT", measurements
    if directional >= imbalance_min:
        return "BALANCE_TO_IMBALANCE_TRANSITION", measurements
    return "IMBALANCE_TO_BALANCE_REPAIR", measurements


def _classify_volume_nodes(block, params):
    levels = _profile_levels(block["volume_at_price_distribution"], "volume_at_price_distribution")
    path = _num_list(block["price_path"], "price_path")
    hvn_req = _param_num(params, "high_volume_node_prominence_requirement")
    lvn_req = _param_num(params, "low_volume_node_thinness_requirement")
    travel_req = _param_num(params, "air_pocket_travel_requirement")
    volumes = [lv.get("volume", 0.0) for lv in levels]
    mean_volume = statistics.fmean(volumes) or 1.0
    hvn_prominence = max(volumes) / mean_volume
    lvn_thinness = mean_volume / min(volumes) if min(volumes) > 0 else 9.0
    travel = max(path) - min(path)
    measurements = {
        "hvn_prominence": hvn_prominence, "lvn_thinness": lvn_thinness, "price_travel": travel,
    }
    if hvn_prominence >= hvn_req:
        return "HIGH_VOLUME_NODE_IDENTIFIED", measurements
    if lvn_thinness >= lvn_req:
        return "LOW_VOLUME_NODE_IDENTIFIED", measurements
    if travel >= travel_req:
        return "AIR_POCKET_CONTEXT", measurements
    return "NODE_ACCEPTANCE_TEST", measurements


# ---------------------------------------------------------------------------
# Family C — series-statistics detectors
# ---------------------------------------------------------------------------

def _classify_spread_behavior(block, params):
    spreads = _spreads(block["bid_ask_quotes"], "bid_ask_quotes")
    baseline = _param_num(params, "spread_width_baseline")
    widening_req = _param_num(params, "spread_widening_requirement")
    normalization_req = _param_num(params, "spread_normalization_requirement")
    recent, early = _window_ratio(spreads)
    instability = statistics.pstdev(spreads) / statistics.fmean(spreads) if len(spreads) > 1 else 0.0
    measurements = {
        "recent_spread": recent, "early_spread": early, "baseline": baseline,
        "instability": instability,
    }
    if recent >= baseline * widening_req:
        return "SPREAD_WIDENING", measurements
    if early > recent and recent <= baseline * normalization_req:
        return "SPREAD_NORMALIZING", measurements
    if instability >= 0.5:
        return "SPREAD_UNSTABLE", measurements
    if recent >= baseline * widening_req * 2:
        return "SPREAD_BLOCKED", measurements
    return "SPREAD_STABLE", measurements


def _classify_sweeps_through_liquidity(block, params):
    seq = _num_list(block["price_sequence"], "price_sequence")
    levels = _num_list(block["structural_levels"], "structural_levels")
    take_req = _param_num(params, "multi_level_take_requirement")
    velocity_req = _param_num(params, "sweep_velocity_requirement")
    hold_window = int(_param_num(params, "post_sweep_hold_window"))
    low, high = min(seq), max(seq)
    span = high - low
    levels_taken = sum(1 for level in levels if low <= level <= high)
    velocity = span / len(seq)
    up = (high - seq[0]) >= (seq[0] - low)
    extreme = high if up else low
    extreme_index = seq.index(extreme)
    post = seq[extreme_index + 1 : extreme_index + 1 + max(1, hold_window)]
    reclaim_fraction = 0.0
    if post and span > 0:
        reclaim = (extreme - post[-1]) if up else (post[-1] - extreme)
        reclaim_fraction = reclaim / span
    measurements = {
        "levels_taken": levels_taken, "velocity": velocity,
        "post_sweep_reclaim_fraction": reclaim_fraction,
    }
    if levels_taken >= take_req and velocity >= velocity_req:
        if not post:
            return "SWEEP_DETECTED", measurements
        if reclaim_fraction <= 0.34:
            return "POST_SWEEP_CONTINUATION", measurements
        if reclaim_fraction >= 0.66:
            return "POST_SWEEP_ABSORPTION", measurements
        return "SWEEP_DETECTED", measurements
    if levels_taken >= take_req:
        return "SWEEP_RESOLUTION_PENDING", measurements
    return "COARSE_PRICE_SPIKE_CONTEXT", measurements


def _classify_tape_quality(block, params):
    bars = _bars(block["tick_or_bar_sequence"], "tick_or_bar_sequence")
    spreads = _spreads(block["spread_history"], "spread_history")
    spread_baseline = _param_num(params, "spread_baseline_requirement")
    stability_req = _param_num(params, "tape_stability_requirement")
    range_req = _param_num(params, "bar_range_context_requirement")
    mean_spread = statistics.fmean(spreads)
    ranges = [bar["high"] - bar["low"] for bar in bars]
    mean_range = statistics.fmean(ranges)
    instability = statistics.pstdev(ranges) / mean_range if mean_range > 0 and len(ranges) > 1 else 0.0
    measurements = {
        "mean_spread": mean_spread, "mean_range": mean_range, "range_instability": instability,
    }
    if mean_spread > spread_baseline * 2:
        return "TAPE_WIDE", measurements
    if instability > stability_req:
        return "TAPE_NOISY", measurements
    if mean_range >= range_req:
        return "TAPE_FAST", measurements
    if mean_spread <= spread_baseline and instability <= stability_req:
        return "TAPE_CLEAN", measurements
    return "TAPE_SLOW", measurements


def _classify_impulse_vs_grind(block, params):
    bars = _bars(block["price_bars"], "price_bars")
    impulse_req = _param_num(params, "impulse_displacement_requirement")
    grind_req = _param_num(params, "grind_persistence_requirement")
    overlap_req = _param_num(params, "overlap_requirement")
    closes = [bar.get("close", (bar["high"] + bar["low"]) / 2) for bar in bars]
    displacement = abs(closes[-1] - closes[0])
    overlap = _overlap_fraction(bars)
    measurements = {"displacement": displacement, "overlap_fraction": overlap}
    if displacement >= impulse_req * 2 and overlap <= overlap_req:
        return "VERTICAL_OR_PARABOLIC_MOVE", measurements
    if displacement >= impulse_req and overlap <= overlap_req:
        return "IMPULSE_MOVE", measurements
    if displacement >= grind_req and overlap >= overlap_req:
        return "GRIND_MOVE", measurements
    if displacement < grind_req:
        return "DRIFT_NOT_GRIND", measurements
    return "TEXTURE_PENDING", measurements


def _classify_stop_out_cascades(block, params):
    seq = _num_list(block["price_sequence"], "price_sequence")
    levels = _num_list(block["structural_levels"], "structural_levels")
    series = block["velocity_and_volume_series"]
    if not isinstance(series, dict):
        raise _DataError("velocity_and_volume_series must be an object with velocity and volume")
    velocity = _num_list(series.get("velocity"), "velocity_and_volume_series.velocity")
    volume = _num_list(series.get("volume"), "velocity_and_volume_series.volume")
    velocity_req = _param_num(params, "cascade_velocity_requirement")
    volume_req = _param_num(params, "volume_expansion_requirement")
    breach_req = _param_num(params, "structural_breach_requirement")
    peak_velocity = max(velocity)
    vol_recent, vol_early = _window_ratio(volume)
    vol_expansion = vol_recent / vol_early if vol_early > 0 else 0.0
    low, high = min(seq), max(seq)
    breaches = sum(1 for level in levels if low <= level <= high)
    measurements = {
        "peak_velocity": peak_velocity, "volume_expansion": vol_expansion, "breaches": breaches,
    }
    if peak_velocity >= velocity_req and vol_expansion >= volume_req and breaches >= breach_req:
        return "CASCADE_LIKE_BEHAVIOR", measurements
    if breaches >= breach_req and peak_velocity >= velocity_req:
        return "STOP_OUT_CASCADE_EVIDENCE", measurements
    if peak_velocity >= velocity_req:
        return "FORCED_FLOW_ONLY", measurements
    return "STRUCTURAL_ACCELERATION_ONLY", measurements


def _classify_compression_breakouts(block, params):
    bars = _bars(block["price_bars"], "price_bars")
    rng = block["structural_range"]
    if not isinstance(rng, dict):
        raise _DataError("structural_range must be an object with high and low")
    range_high = _num(rng.get("high"), "structural_range.high")
    range_low = _num(rng.get("low"), "structural_range.low")
    req = _param_obj(params, "compression_breakouts_real_vs_false_classification_requirement")
    hold_min = _obj_num(req, "hold_bars_min", "compression_breakouts_real_vs_false_classification_requirement")
    reclaim_max = _obj_num(req, "reclaim_max_bars", "compression_breakouts_real_vs_false_classification_requirement")
    closes = [bar.get("close", (bar["high"] + bar["low"]) / 2) for bar in bars]
    first_break = -1
    for index, close in enumerate(closes):
        if close > range_high or close < range_low:
            first_break = index
            break
    measurements = {"range_high": range_high, "range_low": range_low, "first_break": first_break}
    if first_break < 0:
        return "BREAKOUT_ANTICIPATION_CONTEXT", measurements
    side_up = closes[first_break] > range_high
    after = closes[first_break:]
    held = sum(
        1 for c in after if (c > range_high if side_up else c < range_low)
    )
    reclaimed_at = -1
    for offset, close in enumerate(after):
        if (close <= range_high) if side_up else (close >= range_low):
            reclaimed_at = offset
            break
    measurements["held_bars"] = held
    if reclaimed_at >= 0 and reclaimed_at <= reclaim_max:
        return "FALSE_COMPRESSION_BREAK", measurements
    if held >= hold_min:
        return "ACCEPTED_COMPRESSION_BREAK", measurements
    return "COMPRESSION_BREAK_PENDING", measurements


def _classify_compression_vs_expansion(block, params):
    stats = block["range_statistics"]
    if not isinstance(stats, dict):
        raise _DataError("range_statistics must be an object with recent_range and baseline_range")
    recent_range = _num(stats.get("recent_range"), "range_statistics.recent_range")
    baseline_range = _num(stats.get("baseline_range"), "range_statistics.baseline_range")
    rv = _num_list(block["realized_volatility_series"], "realized_volatility_series")
    contraction_req = _param_num(params, "compression_range_contraction_requirement")
    expansion_req = _param_num(params, "expansion_range_requirement")
    rv_expansion_req = _param_num(params, "realized_volatility_expansion_requirement")
    return_window = _param_num(params, "failed_expansion_return_window")
    contraction_ratio = recent_range / baseline_range if baseline_range > 0 else 1.0
    rv_recent, rv_early = _window_ratio(rv)
    rv_ratio = rv_recent / rv_early if rv_early > 0 else 1.0
    measurements = {"range_ratio": contraction_ratio, "rv_ratio": rv_ratio}
    if contraction_ratio <= contraction_req:
        return "COMPRESSION_STATE", measurements
    if contraction_ratio >= expansion_req or rv_ratio >= rv_expansion_req:
        recent_window = rv[-int(return_window) - 1 :]
        if len(recent_window) > 1 and recent_window[-1] <= rv_early:
            return "FAILED_EXPANSION_STATE", measurements
        return "EXPANSION_STATE", measurements
    if contraction_ratio > contraction_req and rv_ratio > 1.0:
        return "TRANSITION_FROM_COMPRESSION", measurements
    return "STRUCTURAL_VOLATILITY_CONTEXT", measurements


def _classify_expanded_volatility(block, params):
    spread = _num_list(block["spread_series"], "spread_series")
    depth = _num_list(block["depth_series"], "depth_series")
    rv = _num_list(block["realized_volatility_series"], "realized_volatility_series")
    rv_expansion_req = _param_num(params, "realized_volatility_expansion_requirement")
    spread_req = _param_num(params, "spread_instability_requirement")
    depth_req = _param_num(params, "depth_instability_requirement")
    rv_recent, rv_early = _window_ratio(rv)
    rv_ratio = rv_recent / rv_early if rv_early > 0 else 1.0
    spread_instability = statistics.pstdev(spread) / statistics.fmean(spread) if len(spread) > 1 else 0.0
    depth_instability = statistics.pstdev(depth) / statistics.fmean(depth) if len(depth) > 1 else 0.0
    measurements = {
        "rv_ratio": rv_ratio, "spread_instability": spread_instability,
        "depth_instability": depth_instability,
    }
    rv_expanded = rv_ratio >= rv_expansion_req
    spread_unstable = spread_instability >= spread_req
    depth_unstable = depth_instability >= depth_req
    if rv_expanded and (spread_unstable or depth_unstable):
        return "EXPANDED_VOLATILITY_ENVIRONMENT_BLOCK", measurements
    if spread_unstable or depth_unstable:
        return "SPREAD_OR_DEPTH_QUALITY_BLOCK", measurements
    if rv_expanded:
        return "STRUCTURAL_VOLATILITY_CAUTION", measurements
    return "NO_CLEAN_EXPRESSION_CONTEXT", measurements


def _classify_volatility_crush(block, params):
    rv = _num_list(block["realized_volatility_series"], "realized_volatility_series")
    ranges = _num_list(block["range_series"], "range_series")
    spreads = _num_list(block["spread_series"], "spread_series")
    event = block["event_timing_context"]
    if not isinstance(event, dict):
        raise _DataError("event_timing_context must be an object")
    contraction_req = _param_num(params, "volatility_contraction_requirement")
    range_norm_req = _param_num(params, "range_normalization_requirement")
    post_event_window = _param_num(params, "post_event_window")
    rv_recent, rv_early = _window_ratio(rv)
    rv_ratio = rv_recent / rv_early if rv_early > 0 else 1.0
    range_recent, range_early = _window_ratio(ranges)
    range_ratio = range_recent / range_early if range_early > 0 else 1.0
    spread_recent, spread_early = _window_ratio(spreads)
    samples_since_event = _num(event.get("samples_since_event", -1.0), "event_timing_context.samples_since_event")
    measurements = {
        "rv_ratio": rv_ratio, "range_ratio": range_ratio,
        "samples_since_event": samples_since_event,
    }
    crushed = rv_ratio <= contraction_req
    if 0 <= samples_since_event <= post_event_window and crushed:
        return "POST_EVENT_NORMALIZATION", measurements
    if crushed and range_ratio <= range_norm_req and spread_recent <= spread_early:
        return "VOLATILITY_RESET_CONTEXT", measurements
    if crushed:
        return "REALIZED_VOLATILITY_CRUSH_CONTEXT", measurements
    return "RESET_NOT_CONFIRMED", measurements


# ---------------------------------------------------------------------------
# Family D — session / breadth / environment detectors
# ---------------------------------------------------------------------------

def _classify_asia_session(block, params):
    bars = _bars(block["asia_session_bars"], "asia_session_bars")
    volume = _num_list(block["asia_volume_series"], "asia_volume_series")
    range_req = _param_num(params, "asia_range_meaningfulness_requirement")
    participation_req = _param_num(params, "asia_volume_participation_requirement")
    fakeout_window = _param_num(params, "asia_fakeout_reclaim_window")
    asia_range = max(bar["high"] for bar in bars) - min(bar["low"] for bar in bars)
    mean_volume = statistics.fmean(volume)
    highs = [bar["high"] for bar in bars]
    peak_index = highs.index(max(highs))
    reclaimed = any(
        bar["high"] < max(highs) for bar in bars[peak_index + 1 : peak_index + 1 + int(fakeout_window) + 1]
    )
    measurements = {
        "asia_range": asia_range, "mean_volume": mean_volume, "extension_reclaimed": reclaimed,
    }
    if asia_range >= range_req and mean_volume >= participation_req:
        if asia_range >= range_req * 1.5:
            return "ASIA_REPRICING_CONTEXT", measurements
        return "ASIA_MEANINGFUL_STRUCTURE", measurements
    if asia_range < range_req and reclaimed:
        return "ASIA_FAKEOUT_PRONE_CONTEXT", measurements
    if asia_range < range_req:
        return "ASIA_PLACEHOLDER_RANGE", measurements
    return "STRUCTURAL_ASIA_CONTEXT_ONLY", measurements


def _classify_breadth(block, params):
    cash_index = block["cash_index"]
    advance_decline = block["constituent_advance_decline"]
    equal_weight = block["equal_weight_data"]
    for name, value in (
        ("cash_index", cash_index),
        ("constituent_advance_decline", advance_decline),
        ("equal_weight_data", equal_weight),
    ):
        if not isinstance(value, dict):
            raise _DataError(f"{name} must be an object")
    req = _param_obj(params, "breadth_confirmation_and_divergence_classification_requirement")
    confirm_ratio = _obj_num(req, "confirm_advance_ratio_min", "breadth_confirmation_and_divergence_classification_requirement")
    divergence_gap = _obj_num(req, "divergence_gap", "breadth_confirmation_and_divergence_classification_requirement")
    index_change = _num(cash_index.get("change"), "cash_index.change")
    advancers = _num(advance_decline.get("advancers"), "constituent_advance_decline.advancers")
    decliners = _num(advance_decline.get("decliners"), "constituent_advance_decline.decliners")
    equal_weight_change = _num(equal_weight.get("change"), "equal_weight_data.change")
    total = advancers + decliners
    advance_ratio = advancers / total if total > 0 else 0.0
    measurements = {
        "index_change": index_change, "advance_ratio": advance_ratio,
        "equal_weight_change": equal_weight_change,
    }
    index_up = index_change > 0
    direction_match = (equal_weight_change > 0) == index_up
    if index_up and advance_ratio >= confirm_ratio and direction_match:
        return "BREADTH_CONFIRMS_PRICE", measurements
    if abs(index_change) > 0 and abs(advance_ratio - 0.5) * 2 < (abs(index_change) - divergence_gap):
        return "BREADTH_DIVERGES_FROM_PRICE", measurements
    if index_up and not direction_match:
        return "NARROW_LEADERSHIP_WARNING", measurements
    if not index_up and advance_ratio >= confirm_ratio:
        return "BROADENING_PARTICIPATION", measurements
    return "BREADTH_DIVERGES_FROM_PRICE", measurements


def _classify_execution_environment(block, params):
    spread = _num(block["spread"], "spread")
    depth = _num(block["depth"], "depth")
    realized_volatility = _num(block["realized_volatility"], "realized_volatility")
    event = block["event_calendar"]
    if not isinstance(event, dict):
        raise _DataError("event_calendar must be an object")
    minutes_to_event = _num(event.get("minutes_to_event"), "event_calendar.minutes_to_event")
    req = _param_obj(params, "execution_environment_quality_and_veto_classification_requirement")
    spread_max = _obj_num(req, "spread_max", "execution_environment_quality_and_veto_classification_requirement")
    depth_min = _obj_num(req, "depth_min", "execution_environment_quality_and_veto_classification_requirement")
    rv_max = _obj_num(req, "realized_volatility_max", "execution_environment_quality_and_veto_classification_requirement")
    event_min = _obj_num(req, "event_min_minutes", "execution_environment_quality_and_veto_classification_requirement")
    measurements = {
        "spread": spread, "depth": depth, "realized_volatility": realized_volatility,
        "minutes_to_event": minutes_to_event,
    }
    if spread > spread_max:
        return "SPREAD_QUALITY_BLOCKED", measurements
    if depth < depth_min:
        return "LIQUIDITY_DEPTH_BLOCKED", measurements
    if realized_volatility > rv_max:
        return "VOLATILITY_ENVIRONMENT_BLOCKED", measurements
    if 0 <= minutes_to_event < event_min:
        return "EVENT_RISK_BLOCKED", measurements
    return "ENVIRONMENT_QUALITY_ACCEPTABLE_CONTEXT", measurements


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class _CalibratedSpec(NamedTuple):
    fixture_fields: tuple[str, ...]
    parameter_names: tuple[str, ...]
    classify: Callable[[dict[str, Any], dict[str, Any]], tuple[str, dict[str, Any]]]


CALIBRATED_DETECTORS: dict[str, _CalibratedSpec] = {
    "ch02_acceptance_vs_rejection": _CalibratedSpec(
        ("structural_level", "trade_price_sequence", "session_clock"),
        ("acceptance_dwell_time", "level_buffer", "failed_acceptance_window"),
        _classify_acceptance_vs_rejection,
    ),
    "ch02_break_quality": _CalibratedSpec(
        ("price_sequence", "structural_reference"),
        ("break_quality_classification_requirement",),
        _classify_break_quality,
    ),
    "ch02_breakout_continuation_vs_breakout_failure": _CalibratedSpec(
        ("structural_level", "price_sequence"),
        ("break_clear_buffer", "extension_requirement", "failure_return_window"),
        _classify_breakout_continuation,
    ),
    "ch02_level_magnetism_and_decay": _CalibratedSpec(
        ("structural_level", "price_sequence"),
        ("level_magnetism_and_decay_classification_requirement",),
        _classify_level_magnetism,
    ),
    "ch02_level_test_sequence": _CalibratedSpec(
        ("structural_level", "price_sequence"),
        (
            "test_separation_requirement",
            "reaction_quality_requirement",
            "decay_review_count_policy",
            "level_buffer",
        ),
        _classify_level_test_sequence,
    ),
    "ch02_liquidity_sweep_vs_real_break": _CalibratedSpec(
        ("structural_level", "price_sequence"),
        ("sweep_probe_distance", "reclaim_window", "hold_beyond_level_window"),
        _classify_liquidity_sweep,
    ),
    "ch02_polarity_flip": _CalibratedSpec(
        ("broken_structural_level", "post_break_price_sequence"),
        ("retest_window", "hold_or_reject_requirement", "level_buffer"),
        _classify_polarity_flip,
    ),
    "ch03_auction_acceptance_vs_rejection": _CalibratedSpec(
        ("price_sequence", "profile_distribution", "auction_reference_area"),
        (
            "auction_extension_buffer",
            "accepted_volume_development_requirement",
            "rejection_return_window",
        ),
        _classify_auction_acceptance,
    ),
    "ch03_completed_failed_and_unfinished_auctions": _CalibratedSpec(
        ("market_profile_or_tpo", "price_sequence"),
        ("excess_tail_requirement", "poor_extreme_requirement", "failed_auction_reclaim_window"),
        _classify_completed_auctions,
    ),
    "ch03_excess_vs_poor_highs_lows": _CalibratedSpec(
        ("tpo_or_market_profile", "price_sequence"),
        (
            "single_print_tail_requirement",
            "poor_extreme_repetition_requirement",
            "rejection_speed_requirement",
        ),
        _classify_excess_vs_poor,
    ),
    "ch03_price_outside_value_acceptance_test": _CalibratedSpec(
        ("value_area_references", "price_sequence", "volume_at_price_or_tpo"),
        ("outside_value_buffer", "acceptance_development_requirement", "return_inside_window"),
        _classify_price_outside_value,
    ),
    "ch03_the_auction_framework": _CalibratedSpec(
        ("price_bar_structure",),
        ("the_auction_framework_classification_requirement",),
        _classify_auction_framework,
    ),
    "ch03_volume_nodes_and_air_pockets": _CalibratedSpec(
        ("volume_at_price_distribution", "price_path"),
        (
            "high_volume_node_prominence_requirement",
            "low_volume_node_thinness_requirement",
            "air_pocket_travel_requirement",
        ),
        _classify_volume_nodes,
    ),
    "ch04_spread_behavior": _CalibratedSpec(
        ("bid_ask_quotes",),
        ("spread_width_baseline", "spread_widening_requirement", "spread_normalization_requirement"),
        _classify_spread_behavior,
    ),
    "ch04_stall_and_snap_back": _CalibratedSpec(
        ("price_sequence", "structural_reference"),
        (
            "stall_duration_requirement",
            "progress_failure_requirement",
            "snapback_return_window",
            "reference_buffer",
        ),
        _classify_stall_and_snap_back,
    ),
    "ch04_sweeps_through_liquidity": _CalibratedSpec(
        ("price_sequence", "structural_levels"),
        ("multi_level_take_requirement", "sweep_velocity_requirement", "post_sweep_hold_window"),
        _classify_sweeps_through_liquidity,
    ),
    "ch04_tape_quality_spectrum": _CalibratedSpec(
        ("tick_or_bar_sequence", "spread_history"),
        ("spread_baseline_requirement", "tape_stability_requirement", "bar_range_context_requirement"),
        _classify_tape_quality,
    ),
    "ch05_follow_through_and_failure": _CalibratedSpec(
        ("price_bars", "structural_reference"),
        (
            "post_move_extension_requirement",
            "hold_beyond_reference_requirement",
            "failure_reclaim_window",
        ),
        _classify_follow_through,
    ),
    "ch05_impulse_vs_grind": _CalibratedSpec(
        ("price_bars",),
        ("impulse_displacement_requirement", "grind_persistence_requirement", "overlap_requirement"),
        _classify_impulse_vs_grind,
    ),
    "ch06_stop_out_cascades_and_liquidation": _CalibratedSpec(
        ("price_sequence", "structural_levels", "velocity_and_volume_series"),
        ("cascade_velocity_requirement", "volume_expansion_requirement", "structural_breach_requirement"),
        _classify_stop_out_cascades,
    ),
    "ch07_asia_session_character": _CalibratedSpec(
        ("asia_session_bars", "asia_volume_series"),
        (
            "asia_range_meaningfulness_requirement",
            "asia_volume_participation_requirement",
            "asia_fakeout_reclaim_window",
        ),
        _classify_asia_session,
    ),
    "ch08_compression_breakouts_real_vs_false": _CalibratedSpec(
        ("price_bars", "structural_range"),
        ("compression_breakouts_real_vs_false_classification_requirement",),
        _classify_compression_breakouts,
    ),
    "ch08_compression_vs_expansion": _CalibratedSpec(
        ("range_statistics", "realized_volatility_series"),
        (
            "compression_range_contraction_requirement",
            "expansion_range_requirement",
            "realized_volatility_expansion_requirement",
            "failed_expansion_return_window",
        ),
        _classify_compression_vs_expansion,
    ),
    "ch08_expanded_volatility_no_trade_condition": _CalibratedSpec(
        ("spread_series", "depth_series", "realized_volatility_series"),
        (
            "realized_volatility_expansion_requirement",
            "spread_instability_requirement",
            "depth_instability_requirement",
        ),
        _classify_expanded_volatility,
    ),
    "ch08_volatility_crush_and_reset": _CalibratedSpec(
        ("realized_volatility_series", "range_series", "spread_series", "event_timing_context"),
        ("volatility_contraction_requirement", "range_normalization_requirement", "post_event_window"),
        _classify_volatility_crush,
    ),
    "ch09_breadth_confirmation_and_divergence": _CalibratedSpec(
        ("cash_index", "constituent_advance_decline", "equal_weight_data"),
        ("breadth_confirmation_and_divergence_classification_requirement",),
        _classify_breadth,
    ),
    "ch12_execution_environment_quality_and_veto": _CalibratedSpec(
        ("spread", "depth", "realized_volatility", "event_calendar"),
        ("execution_environment_quality_and_veto_classification_requirement",),
        _classify_execution_environment,
    ),
}


# ---------------------------------------------------------------------------
# Output builders and runner
# ---------------------------------------------------------------------------

_ACTION_FALLBACKS = (
    "OBSERVE",
    "MONITOR_FOR_CONFIRMATION",
    "REVIEW_REQUIRED",
    "CONTEXT_ONLY",
    "INSUFFICIENT_EVIDENCE",
    "REFUSE_TO_CLASSIFY",
    "DOWNGRADE_CONFIDENCE",
)


def _action_for(contract: DetectorContract, state: str) -> str:
    """Pick a contract-valid action label for a classified state."""
    actions = contract.allowed_action_labels
    if not actions:
        return state  # state-only contract
    if state in actions:
        return state
    if "REFUSE" in state:
        preferred = "REFUSE_TO_CLASSIFY"
    elif "INSUFFICIENT" in state:
        preferred = "INSUFFICIENT_EVIDENCE"
    elif "REVIEW" in state:
        preferred = "REVIEW_REQUIRED"
    elif "DEGRADED" in state:
        preferred = "DOWNGRADE_CONFIDENCE"
    elif "CONTEXT" in state:
        preferred = "CONTEXT_ONLY"
    elif "PENDING" in state or "REQUIRED" in state:
        preferred = "MONITOR_FOR_CONFIRMATION"
    else:
        preferred = "OBSERVE"
    if preferred in actions:
        return preferred
    for fallback in _ACTION_FALLBACKS:
        if fallback in actions:
            return fallback
    return actions[0]


def _refuse(
    contract: DetectorContract,
    reason: str,
    *,
    missing_fixture: list[str] | None = None,
    missing_calibration: bool = False,
) -> dict[str, Any]:
    """Build a safe calibrated-refusal output drawn from the contract's labels."""
    state = select_safe_state(contract).label
    action = select_safe_action(contract, state)
    evidence: dict[str, Any] = {
        "route": "calibrated_refusal",
        "detector_class": "CALIBRATED",
        "refusal": True,
        "reason": reason,
    }
    if missing_fixture:
        evidence["missing_fixture_fields"] = list(missing_fixture)
    if missing_calibration:
        evidence["missing_calibration"] = True
    return make_output(
        contract,
        state,
        action,
        evidence=evidence,
        confidence="CALIBRATED_REFUSAL",
        notes=reason,
    )


def _classified(
    contract: DetectorContract,
    state: str,
    measurements: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    """Build a real calibrated-classification output."""
    action = _action_for(contract, state)
    evidence: dict[str, Any] = {
        "route": "calibrated",
        "detector_class": "CALIBRATED",
        "measurements": measurements,
        "calibration_parameters_used": dict(params),
    }
    note = f"Calibrated classification: {state}."
    if contract.allowed_action_labels and state not in contract.allowed_action_labels:
        mapping = f"state {state!r} has no matching action label; mapped to action {action!r}"
        evidence["action_label_mapping_note"] = mapping
    return make_output(
        contract,
        state,
        action,
        evidence=evidence,
        confidence="CALIBRATED_CLASSIFICATION",
        notes=note,
    )


def run_calibrated(
    contract: DetectorContract,
    market_context: Any,
    profile: CalibrationProfile,
) -> dict[str, Any]:
    """Run one CALIBRATED contract against a fixture and a calibration profile.

    Returns a real calibrated classification, or a safe calibrated refusal if
    the fixture block, a required fixture field, or a required calibration
    value is absent or unusable.
    """
    spec = CALIBRATED_DETECTORS.get(contract.concept_id)
    if spec is None:
        return _refuse(
            contract,
            f"CALIBRATED detector {contract.concept_id} is not implemented in this runtime.",
        )

    block = market_context.get(contract.concept_id) if isinstance(market_context, dict) else None
    if not isinstance(block, dict) or not block:
        return _refuse(
            contract,
            f"no calibrated fixture block supplied for {contract.concept_id}.",
            missing_fixture=[contract.concept_id],
        )

    missing_fields = [name for name in spec.fixture_fields if not _present(block, name)]
    if missing_fields:
        return _refuse(
            contract,
            f"missing required fixture field(s): {', '.join(missing_fields)}.",
            missing_fixture=missing_fields,
        )

    try:
        params = profile.require(contract.concept_id, spec.parameter_names)
    except CalibrationError as exc:
        return _refuse(contract, str(exc), missing_calibration=True)

    try:
        state, measurements = spec.classify(block, params)
    except _DataError as exc:
        return _refuse(contract, f"fixture data unusable: {exc}")

    if state not in contract.states_emitted:  # pragma: no cover - guard only.
        return _refuse(
            contract,
            f"internal error: classified state {state!r} is not contract-valid.",
        )
    return _classified(contract, state, measurements, params)
