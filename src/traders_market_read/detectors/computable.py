"""Real structural behaviour for the COMPUTABLE detector contracts.

Each function consumes explicit fixture fields only. No thresholds are
invented; no motive, trend, reversal, setup quality, or trade opportunity is
inferred. When a required input is absent the detector emits a contract-valid
refusal instead of guessing.

The nine COMPUTABLE contracts in the catalog:

- ch02_structural_reference_levels
- ch03_initial_balance
- ch03_single_prints
- ch03_value_area_vah_val_poc
- ch03_value_migration_and_overlap
- ch03_vwap_relationship
- ch05_one_timeframing
- ch07_rth_open_location
- ch08_inside_outside_and_narrow_wide_range_days
"""

from __future__ import annotations

from typing import Any, Callable

from .catalog import DetectorContract
from .output import computable_output, refusal_output

# Standard Market Profile value-area coverage convention. Recorded as a method
# convention (it comes from the detection spec), not an invented market threshold.
_VALUE_AREA_COVERAGE_FRACTION = 0.70


class _DataError(Exception):
    """Raised when a required input is present but structurally unusable."""


# ---------------------------------------------------------------------------
# Fixture-access helpers
# ---------------------------------------------------------------------------

def _market_context(market_context: Any) -> dict[str, Any]:
    return market_context if isinstance(market_context, dict) else {}


def _present(ctx: dict[str, Any], name: str) -> bool:
    """True when ``name`` is supplied and not empty."""
    if name not in ctx:
        return False
    value = ctx[name]
    if value is None:
        return False
    if isinstance(value, (list, dict, str)) and len(value) == 0:
        return False
    return True


def _missing(ctx: dict[str, Any], names: tuple[str, ...]) -> list[str]:
    return [name for name in names if not _present(ctx, name)]


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _DataError(f"{label} must be a number, got {value!r}")
    return float(value)


def _bars_extremes(bars: Any, label: str) -> tuple[float, float]:
    """Return (max high, min low) over a list of OHLC bars."""
    if not isinstance(bars, list) or not bars:
        raise _DataError(f"{label} must be a non-empty list of bars")
    highs: list[float] = []
    lows: list[float] = []
    for index, bar in enumerate(bars):
        if not isinstance(bar, dict):
            raise _DataError(f"{label}[{index}] must be an object")
        high = _number(bar.get("high"), f"{label}[{index}].high")
        low = _number(bar.get("low"), f"{label}[{index}].low")
        if high < low:
            raise _DataError(f"{label}[{index}] has high < low")
        highs.append(high)
        lows.append(low)
    return max(highs), min(lows)


def _high_low(obj: Any, label: str) -> tuple[float, float]:
    if not isinstance(obj, dict):
        raise _DataError(f"{label} must be an object with high and low")
    high = _number(obj.get("high"), f"{label}.high")
    low = _number(obj.get("low"), f"{label}.low")
    if high < low:
        raise _DataError(f"{label} has high < low")
    return high, low


def _value_area(obj: Any, label: str) -> dict[str, float]:
    if not isinstance(obj, dict):
        raise _DataError(f"{label} must be an object with vah, val, poc")
    vah = _number(obj.get("vah"), f"{label}.vah")
    val = _number(obj.get("val"), f"{label}.val")
    poc = _number(obj.get("poc"), f"{label}.poc")
    if vah < val:
        raise _DataError(f"{label} has vah < val")
    return {"vah": vah, "val": val, "poc": poc}


# ---------------------------------------------------------------------------
# Refusal helpers (computable detectors that cannot compute)
# ---------------------------------------------------------------------------

def _refuse_missing(contract: DetectorContract, missing: list[str]) -> dict[str, Any]:
    return refusal_output(
        contract,
        "REFUSE_TO_CLASSIFY",
        "REFUSE_TO_CLASSIFY",
        route="computable_refusal",
        reason=(
            "COMPUTABLE detector: required structural input(s) are absent, so no "
            "structural classification can be computed."
        ),
        missing_inputs=missing,
        confidence="INPUTS_ABSENT",
    )


def _refuse_bad_data(contract: DetectorContract, detail: str) -> dict[str, Any]:
    return refusal_output(
        contract,
        "INSUFFICIENT_EVIDENCE",
        "INSUFFICIENT_EVIDENCE",
        route="computable_refusal",
        reason=f"COMPUTABLE detector: required input present but unusable: {detail}",
        confidence="DATA_QUALITY_INSUFFICIENT",
    )


# ---------------------------------------------------------------------------
# ch02_structural_reference_levels
# ---------------------------------------------------------------------------

def compute_structural_reference_levels(
    contract: DetectorContract, market_context: Any
) -> dict[str, Any]:
    ctx = _market_context(market_context)
    missing = _missing(ctx, ("session_clock", "current_session_bars"))
    if missing:
        return _refuse_missing(contract, missing)
    try:
        current = ctx["current_session_bars"]
        if not isinstance(current, list) or not current or not isinstance(current[0], dict):
            raise _DataError("current_session_bars must be a non-empty list of bars")
        rth_open = _number(current[0].get("open"), "current_session_bars[0].open")

        references_observed: dict[str, float] = {"rth_open_price": rth_open}
        references_not_observed: list[str] = []

        if _present(ctx, "prior_session_bars"):
            prior_high, prior_low = _bars_extremes(
                ctx["prior_session_bars"], "prior_session_bars"
            )
            references_observed["prior_day_high"] = prior_high
            references_observed["prior_day_low"] = prior_low
            degraded = False
        else:
            references_not_observed.extend(["prior_day_high", "prior_day_low"])
            degraded = True
    except _DataError as exc:
        return _refuse_bad_data(contract, str(exc))

    measurements = {
        "references_observed": references_observed,
        "references_not_observed": references_not_observed,
        "note": "Reference lattice only; behaviour at any reference is out of scope.",
    }
    if degraded:
        return computable_output(
            contract,
            "DEGRADED_CONFIDENCE",
            measurements=measurements,
            confidence="PRIOR_SESSION_BARS_ABSENT",
            notes="Prior-session references omitted; current-session references published.",
        )
    return computable_output(
        contract,
        "OBSERVED",
        measurements=measurements,
        notes="Structural reference lattice computed from session bars.",
    )


# ---------------------------------------------------------------------------
# ch03_initial_balance
# ---------------------------------------------------------------------------

def compute_initial_balance(
    contract: DetectorContract, market_context: Any
) -> dict[str, Any]:
    ctx = _market_context(market_context)
    missing = _missing(ctx, ("session_clock", "rth_session_bars"))
    if missing:
        return _refuse_missing(contract, missing)
    try:
        session_clock = ctx["session_clock"]
        ib_high, ib_low = _bars_extremes(ctx["rth_session_bars"], "rth_session_bars")
    except _DataError as exc:
        return _refuse_bad_data(contract, str(exc))

    ib_width = ib_high - ib_low
    window_complete = True
    if isinstance(session_clock, dict):
        window_complete = bool(session_clock.get("ib_window_complete", True))

    measurements = {
        "ib_high": ib_high,
        "ib_low": ib_low,
        "ib_width": ib_width,
        "ib_window_complete": window_complete,
    }
    if not window_complete:
        return computable_output(
            contract,
            "PENDING",
            measurements=measurements,
            confidence="IB_WINDOW_INCOMPLETE",
            notes="Initial Balance window not complete; range is provisional.",
        )
    return computable_output(
        contract,
        "OBSERVED",
        measurements=measurements,
        notes="Initial Balance range computed from the RTH IB window.",
    )


# ---------------------------------------------------------------------------
# ch03_single_prints
# ---------------------------------------------------------------------------

def compute_single_prints(
    contract: DetectorContract, market_context: Any
) -> dict[str, Any]:
    ctx = _market_context(market_context)
    missing = _missing(
        ctx, ("tpo_profile", "tpo_period_definition", "session_clock")
    )
    if missing:
        return _refuse_missing(contract, missing)
    try:
        tpo_profile = ctx["tpo_profile"]
        if isinstance(tpo_profile, dict):
            levels = tpo_profile.get("levels")
        else:
            levels = tpo_profile
        if not isinstance(levels, list) or not levels:
            raise _DataError("tpo_profile must provide a non-empty list of price levels")
        single_print_prices: list[float] = []
        for index, level in enumerate(levels):
            if not isinstance(level, dict):
                raise _DataError(f"tpo_profile level[{index}] must be an object")
            price = _number(level.get("price"), f"tpo_profile level[{index}].price")
            count = _number(
                level.get("tpo_count"), f"tpo_profile level[{index}].tpo_count"
            )
            if count == 1:
                single_print_prices.append(price)
    except _DataError as exc:
        return _refuse_bad_data(contract, str(exc))

    measurements = {
        "single_print_prices": single_print_prices,
        "single_print_count": len(single_print_prices),
        "total_levels": len(levels),
        "note": "Single prints are TPO levels touched by exactly one period bracket.",
    }
    if single_print_prices:
        return computable_output(
            contract,
            "SINGLE_PRINTS_PRESENT",
            measurements=measurements,
            notes="One or more single-print levels identified in the TPO profile.",
        )
    return computable_output(
        contract,
        "SINGLE_PRINTS_ABSENT",
        measurements=measurements,
        notes="No single-print levels found in the TPO profile.",
    )


# ---------------------------------------------------------------------------
# ch03_value_area_vah_val_poc
# ---------------------------------------------------------------------------

def _value_area_from_distribution(
    distribution: Any,
) -> tuple[dict[str, float], str]:
    """Compute POC / VAH / VAL from a price distribution.

    Method: locate the POC (max-weight price level), then expand outward one
    adjacent level at a time toward whichever side carries more weight until
    the standard value-area coverage fraction is reached.
    """
    if not isinstance(distribution, list) or len(distribution) < 2:
        raise _DataError("profile_distribution must list at least two price levels")

    levels: list[tuple[float, float]] = []
    weight_kind = "volume"
    for index, item in enumerate(distribution):
        if not isinstance(item, dict):
            raise _DataError(f"profile_distribution[{index}] must be an object")
        price = _number(item.get("price"), f"profile_distribution[{index}].price")
        if "volume" in item:
            weight = _number(item.get("volume"), f"profile_distribution[{index}].volume")
        elif "tpo" in item:
            weight_kind = "tpo"
            weight = _number(item.get("tpo"), f"profile_distribution[{index}].tpo")
        else:
            raise _DataError(
                f"profile_distribution[{index}] must carry a volume or tpo weight"
            )
        if weight < 0:
            raise _DataError(f"profile_distribution[{index}] weight must not be negative")
        levels.append((price, weight))

    levels.sort(key=lambda pair: pair[0])
    prices = [pair[0] for pair in levels]
    weights = [pair[1] for pair in levels]
    total = sum(weights)
    if total <= 0:
        raise _DataError("profile_distribution carries no traded weight")

    poc_index = max(range(len(weights)), key=lambda i: weights[i])
    target = total * _VALUE_AREA_COVERAGE_FRACTION
    low_index = high_index = poc_index
    cumulative = weights[poc_index]
    while cumulative < target and (low_index > 0 or high_index < len(weights) - 1):
        above = weights[high_index + 1] if high_index < len(weights) - 1 else -1.0
        below = weights[low_index - 1] if low_index > 0 else -1.0
        if above >= below and high_index < len(weights) - 1:
            high_index += 1
            cumulative += weights[high_index]
        else:
            low_index -= 1
            cumulative += weights[low_index]

    value_area = {
        "poc": prices[poc_index],
        "vah": prices[high_index],
        "val": prices[low_index],
        "value_area_width": prices[high_index] - prices[low_index],
    }
    return value_area, weight_kind


def compute_value_area(
    contract: DetectorContract, market_context: Any
) -> dict[str, Any]:
    ctx = _market_context(market_context)
    missing = _missing(ctx, ("session_clock", "profile_distribution"))
    if missing:
        return _refuse_missing(contract, missing)
    try:
        value_area, weight_kind = _value_area_from_distribution(
            ctx["profile_distribution"]
        )
    except _DataError as exc:
        return _refuse_bad_data(contract, str(exc))

    measurements = {
        **value_area,
        "value_area_method": f"{weight_kind}_single_level_expansion",
        "value_area_coverage_fraction": _VALUE_AREA_COVERAGE_FRACTION,
    }
    return computable_output(
        contract,
        "OBSERVED",
        measurements=measurements,
        notes="Value area (VAH/VAL/POC) computed from the supplied price distribution.",
    )


# ---------------------------------------------------------------------------
# ch03_value_migration_and_overlap
# ---------------------------------------------------------------------------

def compute_value_migration(
    contract: DetectorContract, market_context: Any
) -> dict[str, Any]:
    ctx = _market_context(market_context)
    missing = _missing(
        ctx, ("current_value_area", "prior_value_area", "session_clock")
    )
    if missing:
        return _refuse_missing(contract, missing)
    try:
        current = _value_area(ctx["current_value_area"], "current_value_area")
        prior = _value_area(ctx["prior_value_area"], "prior_value_area")
    except _DataError as exc:
        return _refuse_bad_data(contract, str(exc))

    overlaps = current["val"] <= prior["vah"] and current["vah"] >= prior["val"]
    if (
        current["poc"] > prior["poc"]
        and current["val"] >= prior["val"]
        and current["vah"] >= prior["vah"]
    ):
        state = "VALUE_MIGRATING_HIGHER"
    elif (
        current["poc"] < prior["poc"]
        and current["val"] <= prior["val"]
        and current["vah"] <= prior["vah"]
    ):
        state = "VALUE_MIGRATING_LOWER"
    elif overlaps:
        state = "VALUE_OVERLAPPING"
    else:
        state = "VALUE_NON_MIGRATION"

    measurements = {
        "current_value_area": current,
        "prior_value_area": prior,
        "value_areas_overlap": overlaps,
        "note": "Structural value movement only; directional meaning is out of scope.",
    }
    return computable_output(
        contract,
        state,
        measurements=measurements,
        notes="Value migration/overlap computed by direct value-area comparison.",
    )


# ---------------------------------------------------------------------------
# ch03_vwap_relationship
# ---------------------------------------------------------------------------

def compute_vwap_relationship(
    contract: DetectorContract, market_context: Any
) -> dict[str, Any]:
    ctx = _market_context(market_context)
    missing = _missing(
        ctx, ("session_clock", "intraday_trade_price", "intraday_traded_volume")
    )
    if missing:
        return _refuse_missing(contract, missing)
    try:
        prices = ctx["intraday_trade_price"]
        volumes = ctx["intraday_traded_volume"]
        if not isinstance(prices, list) or not isinstance(volumes, list):
            raise _DataError("intraday trade price and volume must be lists")
        if len(prices) != len(volumes) or not prices:
            raise _DataError("intraday trade price and volume must be equal-length non-empty lists")
        weighted_sum = 0.0
        volume_sum = 0.0
        for index in range(len(prices)):
            price = _number(prices[index], f"intraday_trade_price[{index}]")
            volume = _number(volumes[index], f"intraday_traded_volume[{index}]")
            if volume < 0:
                raise _DataError(f"intraday_traded_volume[{index}] must not be negative")
            weighted_sum += price * volume
            volume_sum += volume
        if volume_sum <= 0:
            raise _DataError("intraday_traded_volume sums to zero; VWAP is undefined")
        last_price = _number(prices[-1], "intraday_trade_price[-1]")
    except _DataError as exc:
        return _refuse_bad_data(contract, str(exc))

    vwap = weighted_sum / volume_sum
    if last_price > vwap:
        location = "above_vwap"
    elif last_price < vwap:
        location = "below_vwap"
    else:
        location = "at_vwap"

    measurements = {
        "session_vwap": vwap,
        "last_trade_price": last_price,
        "price_vs_vwap": location,
        "note": "VWAP geometry only; magnet vs support/resistance behaviour is out of scope.",
    }
    return computable_output(
        contract,
        "OBSERVED",
        measurements=measurements,
        notes="Session VWAP and price-vs-VWAP location computed from trade and volume.",
    )


# ---------------------------------------------------------------------------
# ch05_one_timeframing
# ---------------------------------------------------------------------------

def compute_one_timeframing(
    contract: DetectorContract, market_context: Any
) -> dict[str, Any]:
    ctx = _market_context(market_context)
    missing = _missing(
        ctx, ("period_bars", "period_definition", "session_clock")
    )
    if missing:
        return _refuse_missing(contract, missing)
    try:
        period_bars = ctx["period_bars"]
        if not isinstance(period_bars, list) or not period_bars:
            raise _DataError("period_bars must be a non-empty list")
        completed: list[tuple[float, float]] = []
        has_incomplete = False
        for index, bar in enumerate(period_bars):
            if not isinstance(bar, dict):
                raise _DataError(f"period_bars[{index}] must be an object")
            if not bool(bar.get("complete", True)):
                has_incomplete = True
                continue
            high = _number(bar.get("high"), f"period_bars[{index}].high")
            low = _number(bar.get("low"), f"period_bars[{index}].low")
            if high < low:
                raise _DataError(f"period_bars[{index}] has high < low")
            completed.append((high, low))
    except _DataError as exc:
        return _refuse_bad_data(contract, str(exc))

    if len(completed) < 2:
        state = "PENDING" if has_incomplete else "INSUFFICIENT_EVIDENCE"
        return computable_output(
            contract,
            state,
            measurements={
                "completed_periods": len(completed),
                "note": "At least two completed periods are required for a structural state.",
            },
            confidence="AWAITING_PERIODS",
            notes="One-timeframing state pending more completed periods.",
        )

    highs = [pair[0] for pair in completed]
    lows = [pair[1] for pair in completed]
    all_higher = all(lows[i] >= lows[i - 1] for i in range(1, len(lows)))
    all_lower = all(highs[i] <= highs[i - 1] for i in range(1, len(highs)))

    if all_higher and not all_lower:
        state = "ONE_TIMEFRAMING_HIGHER"
    elif all_lower and not all_higher:
        state = "ONE_TIMEFRAMING_LOWER"
    elif all_higher and all_lower:
        state = "NO_ONE_TIMEFRAMING"
    else:
        started_higher = lows[1] >= lows[0]
        started_lower = highs[1] <= highs[0]
        if started_higher and not started_lower:
            state = "LOSS_OF_ONE_TIMEFRAMING_HIGHER"
        elif started_lower and not started_higher:
            state = "LOSS_OF_ONE_TIMEFRAMING_LOWER"
        else:
            state = "NO_ONE_TIMEFRAMING"

    measurements = {
        "completed_periods": len(completed),
        "period_highs": highs,
        "period_lows": lows,
        "note": "Structural period-control state only; not a reversal or continuation claim.",
    }
    return computable_output(
        contract,
        state,
        measurements=measurements,
        notes="One-timeframing state computed by direct period high/low comparison.",
    )


# ---------------------------------------------------------------------------
# ch07_rth_open_location
# ---------------------------------------------------------------------------

def compute_rth_open_location(
    contract: DetectorContract, market_context: Any
) -> dict[str, Any]:
    ctx = _market_context(market_context)
    missing = _missing(
        ctx,
        ("session_clock", "rth_open_price", "overnight_high_low", "prior_rth_high_low"),
    )
    if missing:
        return _refuse_missing(contract, missing)
    try:
        rth_open = _number(ctx["rth_open_price"], "rth_open_price")
        overnight_high, overnight_low = _high_low(
            ctx["overnight_high_low"], "overnight_high_low"
        )
        prior_high, prior_low = _high_low(
            ctx["prior_rth_high_low"], "prior_rth_high_low"
        )
        value_tag = None
        if _present(ctx, "prior_value_references"):
            value = _value_area(ctx["prior_value_references"], "prior_value_references")
            if rth_open > value["vah"]:
                value_tag = "OPEN_ABOVE_PRIOR_VALUE"
            elif rth_open < value["val"]:
                value_tag = "OPEN_BELOW_PRIOR_VALUE"
            else:
                value_tag = "OPEN_INSIDE_PRIOR_VALUE"
    except _DataError as exc:
        return _refuse_bad_data(contract, str(exc))

    if rth_open > overnight_high:
        overnight_tag = "OPEN_ABOVE_OVERNIGHT_HIGH"
    elif rth_open < overnight_low:
        overnight_tag = "OPEN_BELOW_OVERNIGHT_LOW"
    else:
        overnight_tag = "OPEN_INSIDE_OVERNIGHT_RANGE"

    if rth_open > prior_high:
        prior_tag = "OPEN_ABOVE_PRIOR_RTH_HIGH"
    elif rth_open < prior_low:
        prior_tag = "OPEN_BELOW_PRIOR_RTH_LOW"
    else:
        prior_tag = "OPEN_INSIDE_PRIOR_RTH_RANGE"

    location_tags = [overnight_tag, prior_tag]
    if value_tag is not None:
        location_tags.append(value_tag)

    measurements = {
        "rth_open_price": rth_open,
        "overnight_location": overnight_tag,
        "prior_rth_location": prior_tag,
        "prior_value_location": value_tag,
        "location_tags": location_tags,
        "note": "Open-location mapping only; acceptance/rejection is out of scope.",
    }
    confidence = "STRUCTURAL_OBSERVED" if value_tag is not None else "PRIOR_VALUE_REFERENCES_ABSENT"
    return computable_output(
        contract,
        overnight_tag,
        measurements=measurements,
        confidence=confidence,
        notes="RTH open location mapped against overnight, prior-RTH, and value references.",
    )


# ---------------------------------------------------------------------------
# ch08_inside_outside_and_narrow_wide_range_days
# ---------------------------------------------------------------------------

def compute_inside_outside_day(
    contract: DetectorContract, market_context: Any
) -> dict[str, Any]:
    ctx = _market_context(market_context)
    missing = _missing(
        ctx, ("session_clock", "current_session_high_low", "prior_session_high_low")
    )
    if missing:
        return _refuse_missing(contract, missing)
    try:
        current_high, current_low = _high_low(
            ctx["current_session_high_low"], "current_session_high_low"
        )
        prior_high, prior_low = _high_low(
            ctx["prior_session_high_low"], "prior_session_high_low"
        )
    except _DataError as exc:
        return _refuse_bad_data(contract, str(exc))

    above = current_high > prior_high
    below = current_low < prior_low
    if above and below:
        state = "OUTSIDE_DAY"
    elif not above and not below:
        state = "INSIDE_DAY"
    elif above:
        state = "ONE_SIDED_EXTENSION_ABOVE"
    else:
        state = "ONE_SIDED_EXTENSION_BELOW"

    measurements = {
        "current_session_high": current_high,
        "current_session_low": current_low,
        "prior_session_high": prior_high,
        "prior_session_low": prior_low,
        "note": "Structural day container only; no breakout/trend inference.",
    }
    return computable_output(
        contract,
        state,
        measurements=measurements,
        notes="Inside/outside day container computed by direct session-range comparison.",
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

ComputableFn = Callable[[DetectorContract, Any], dict[str, Any]]

COMPUTABLE_DETECTORS: dict[str, ComputableFn] = {
    "ch02_structural_reference_levels": compute_structural_reference_levels,
    "ch03_initial_balance": compute_initial_balance,
    "ch03_single_prints": compute_single_prints,
    "ch03_value_area_vah_val_poc": compute_value_area,
    "ch03_value_migration_and_overlap": compute_value_migration,
    "ch03_vwap_relationship": compute_vwap_relationship,
    "ch05_one_timeframing": compute_one_timeframing,
    "ch07_rth_open_location": compute_rth_open_location,
    "ch08_inside_outside_and_narrow_wide_range_days": compute_inside_outside_day,
}
