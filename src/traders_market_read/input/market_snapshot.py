"""Validate and normalize detector runtime market snapshot inputs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from traders_market_read.detectors.calibrated import CALIBRATED_DETECTORS
from traders_market_read.detectors.catalog import CatalogError, load_catalog
from traders_market_read.detectors.computable import COMPUTABLE_DETECTORS
from traders_market_read.detectors.output import FORBIDDEN_FIELDS, find_forbidden_fields


class MarketSnapshotInputError(ValueError):
    """Raised when a market snapshot input is missing, malformed, or unsafe."""


@dataclass(frozen=True)
class MarketSnapshot:
    """Normalized market snapshot.

    ``runtime_market_context`` is the flat mapping expected by the existing
    detector runtime. ``market_context`` is normalized snapshot metadata.
    """

    schema_version: int
    market_context: dict[str, Any]
    detector_inputs: dict[str, Any]
    runtime_market_context: dict[str, Any]
    source_shape: str


REQUIRED_MARKET_CONTEXT_FIELDS = ("instrument", "session", "timeframe", "data_window")
OPTIONAL_MARKET_CONTEXT_FIELDS = ("as_of", "source", "notes")

SHARED_FIXTURE_BLOCKS = frozenset(
    {
        "session_clock",
        "current_session_bars",
        "prior_session_bars",
        "rth_session_bars",
        "tpo_profile",
        "tpo_period_definition",
        "profile_distribution",
        "current_value_area",
        "prior_value_area",
        "developing_value_area",
        "price_sequence",
        "intraday_trade_price",
        "intraday_traded_volume",
        "period_bars",
        "period_definition",
        "rth_open_price",
        "overnight_high_low",
        "prior_rth_high_low",
        "prior_value_references",
        "current_session_high_low",
        "prior_session_high_low",
    }
)


def _known_concept_ids() -> set[str]:
    try:
        return set(load_catalog().concept_ids)
    except CatalogError as exc:
        raise MarketSnapshotInputError(f"detector catalog error: {exc}") from exc


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (str, list, dict)) and len(value) == 0:
        return False
    return True


def _read_json(path: Path) -> Any:
    if not path.exists():
        raise MarketSnapshotInputError(f"input file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MarketSnapshotInputError(f"input file is not valid JSON: {exc}") from exc
    except OSError as exc:
        raise MarketSnapshotInputError(f"could not read input file {path}: {exc}") from exc


def _reject_forbidden(payload: Any) -> None:
    forbidden = find_forbidden_fields(payload)
    if forbidden:
        raise MarketSnapshotInputError(
            "forbidden execution field present in input: " + ", ".join(forbidden)
        )


def _validate_new_market_context(market_context: Any) -> dict[str, Any]:
    if not isinstance(market_context, dict):
        raise MarketSnapshotInputError("market_context must be a JSON object")
    missing = [
        field
        for field in REQUIRED_MARKET_CONTEXT_FIELDS
        if field not in market_context or not _is_present(market_context[field])
    ]
    if missing:
        raise MarketSnapshotInputError(
            "market_context missing required field(s): " + ", ".join(missing)
        )
    allowed = set(REQUIRED_MARKET_CONTEXT_FIELDS) | set(OPTIONAL_MARKET_CONTEXT_FIELDS)
    unknown = sorted(key for key in market_context if key not in allowed)
    if unknown:
        raise MarketSnapshotInputError(
            "market_context contains unknown field(s): " + ", ".join(unknown)
        )
    return dict(market_context)


def _legacy_market_context(payload: dict[str, Any], detector_inputs: dict[str, Any]) -> dict[str, Any]:
    session_clock = detector_inputs.get("session_clock")
    session = "unspecified_session"
    if isinstance(session_clock, dict) and isinstance(session_clock.get("session_label"), str):
        session = session_clock["session_label"]
    return {
        "instrument": payload.get("instrument_label") or "unspecified_instrument",
        "session": session,
        "timeframe": payload.get("timeframe") or "fixture_timeframe",
        "data_window": payload.get("fixture_id") or "fixture_data_window",
        "source": "legacy_fixture",
        "notes": payload.get("description") or "Normalized from legacy runtime fixture.",
    }


def _validate_detector_inputs(detector_inputs: Any) -> dict[str, Any]:
    if not isinstance(detector_inputs, dict):
        raise MarketSnapshotInputError("detector_inputs must be a JSON object")

    known_concepts = _known_concept_ids()
    allowed_keys = known_concepts | set(SHARED_FIXTURE_BLOCKS)
    unknown = sorted(key for key in detector_inputs if key not in allowed_keys)
    if unknown:
        raise MarketSnapshotInputError(
            "detector_inputs contains unknown key(s): " + ", ".join(unknown)
        )

    for key, value in detector_inputs.items():
        if key in known_concepts and not isinstance(value, dict):
            raise MarketSnapshotInputError(f"detector input block {key} must be an object")
        if key in known_concepts and not value:
            raise MarketSnapshotInputError(f"detector input block {key} must not be empty")
        if key in SHARED_FIXTURE_BLOCKS and value is None:
            raise MarketSnapshotInputError(f"shared input block {key} must not be null")
    return dict(detector_inputs)


def _validate_new_shape(payload: dict[str, Any]) -> MarketSnapshot:
    for field in ("schema_version", "market_context", "detector_inputs"):
        if field not in payload:
            raise MarketSnapshotInputError(f"missing required top-level field: {field}")
    if payload.get("schema_version") != 1:
        raise MarketSnapshotInputError("schema_version must be 1")
    market_context = _validate_new_market_context(payload["market_context"])
    detector_inputs = _validate_detector_inputs(payload["detector_inputs"])
    return MarketSnapshot(
        schema_version=1,
        market_context=market_context,
        detector_inputs=detector_inputs,
        runtime_market_context=dict(detector_inputs),
        source_shape="market_snapshot_v1",
    )


def _validate_legacy_shape(payload: dict[str, Any]) -> MarketSnapshot:
    if "market_context" not in payload:
        raise MarketSnapshotInputError("missing required top-level field: market_context")
    legacy_context = payload["market_context"]
    if not isinstance(legacy_context, dict):
        raise MarketSnapshotInputError("market_context must be a JSON object")
    detector_inputs = _validate_detector_inputs(legacy_context)
    return MarketSnapshot(
        schema_version=1,
        market_context=_legacy_market_context(payload, detector_inputs),
        detector_inputs=detector_inputs,
        runtime_market_context=dict(detector_inputs),
        source_shape="legacy_runtime_fixture",
    )


def validate_market_snapshot_payload(payload: Any) -> MarketSnapshot:
    """Validate and normalize a market snapshot payload.

    Accepts the new ``schema_version``/``market_context``/``detector_inputs``
    envelope and the existing legacy runtime fixture envelope.
    """
    if not isinstance(payload, dict):
        raise MarketSnapshotInputError("market snapshot input must be a JSON object")
    _reject_forbidden(payload)
    if "detector_inputs" in payload or "schema_version" in payload:
        return _validate_new_shape(payload)
    return _validate_legacy_shape(payload)


def load_market_snapshot(path: str | Path) -> MarketSnapshot:
    """Load, validate, and normalize one market snapshot JSON file."""
    return validate_market_snapshot_payload(_read_json(Path(path)))


def runtime_market_context_from_file(path: str | Path) -> dict[str, Any]:
    """Convenience function for existing runtime and pipeline entry points."""
    return load_market_snapshot(path).runtime_market_context


def implemented_runtime_input_expectations() -> list[dict[str, str]]:
    """Return deterministic rows for the current runtime input manifest."""
    rows: list[dict[str, str]] = []
    computable_fields: dict[str, tuple[str, ...]] = {
        "ch02_structural_reference_levels": ("session_clock", "current_session_bars"),
        "ch03_initial_balance": ("session_clock", "rth_session_bars"),
        "ch03_single_prints": ("tpo_profile", "tpo_period_definition", "session_clock"),
        "ch03_value_area_vah_val_poc": ("session_clock", "profile_distribution"),
        "ch03_value_migration_and_overlap": (
            "current_value_area",
            "prior_value_area",
            "session_clock",
        ),
        "ch03_vwap_relationship": (
            "session_clock",
            "intraday_trade_price",
            "intraday_traded_volume",
        ),
        "ch05_one_timeframing": ("period_bars", "period_definition", "session_clock"),
        "ch07_rth_open_location": (
            "session_clock",
            "rth_open_price",
            "overnight_high_low",
            "prior_rth_high_low",
        ),
        "ch08_inside_outside_and_narrow_wide_range_days": (
            "session_clock",
            "current_session_high_low",
            "prior_session_high_low",
        ),
    }
    optional_fields: dict[str, tuple[str, ...]] = {
        "ch02_structural_reference_levels": ("prior_session_bars",),
        "ch07_rth_open_location": ("prior_value_references",),
    }
    for concept_id in sorted(COMPUTABLE_DETECTORS):
        rows.append(
            {
                "concept_id": concept_id,
                "determinism_class": "COMPUTABLE",
                "route": "computable",
                "input_block_required_for_non_refusal": "shared structural blocks",
                "required_fixture_fields": "|".join(computable_fields[concept_id]),
                "optional_fixture_fields": "|".join(optional_fields.get(concept_id, ())),
                "missing_input_behavior": "computable_refusal",
                "notes": "Fields are current runtime fixture keys consumed by the computable detector.",
            }
        )
    for concept_id, spec in sorted(CALIBRATED_DETECTORS.items()):
        rows.append(
            {
                "concept_id": concept_id,
                "determinism_class": "CALIBRATED",
                "route": "calibrated",
                "input_block_required_for_non_refusal": concept_id,
                "required_fixture_fields": "|".join(spec.fixture_fields),
                "optional_fixture_fields": "",
                "missing_input_behavior": "calibrated_refusal",
                "notes": "Requires a concept-id detector input block plus a supplied calibration profile.",
            }
        )
    return rows
