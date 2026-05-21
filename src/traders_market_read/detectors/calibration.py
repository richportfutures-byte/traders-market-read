"""Calibration profile loading, validation, and lookup.

A calibration profile supplies the empirically-scoped parameter values a
CALIBRATED detector needs to turn its fixed rule structure into a real
classification. This module loads a profile fail-closed and exposes a simple
lookup by ``concept_id`` plus ``parameter_name``.

It never supplies values itself. A profile passed here is example/fixture data;
no production instrument calibration is created or implied.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised only on missing dependency.
    raise RuntimeError("PyYAML is required to load calibration profiles") from exc

from .output import find_forbidden_fields

_REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCHEMA_PATH = _REPO_ROOT / "calibration" / "calibration_profile_schema.yaml"

# Fallbacks used only if the schema file cannot supply these lists.
_FALLBACK_REQUIRED_TOP_LEVEL = (
    "schema_version",
    "profile_id",
    "instrument",
    "session_scope",
    "timeframe_scope",
    "regime_scope",
    "data_sample",
    "parameter_values",
    "validation_rules",
    "forbidden_behavior",
)
_FALLBACK_ITEM_FIELDS = (
    "concept_id",
    "parameter_name",
    "value",
    "unit",
    "derivation_method",
    "confidence",
    "last_calibrated",
    "notes",
)


class CalibrationError(RuntimeError):
    """Raised when a calibration profile cannot be trusted."""


class CalibrationProfile:
    """A validated calibration profile with (concept_id, parameter_name) lookup."""

    def __init__(
        self,
        profile_id: str,
        values: dict[tuple[str, str], Any],
        raw: dict[str, Any],
        source_path: Path,
    ) -> None:
        self.profile_id = profile_id
        self._values = values
        self.raw = raw
        self.source_path = source_path

    def has_concept(self, concept_id: str) -> bool:
        return any(cid == concept_id for cid, _ in self._values)

    def get(self, concept_id: str, parameter_name: str) -> Any:
        """Return one parameter value, fail-closed when it is absent."""
        try:
            return self._values[(concept_id, parameter_name)]
        except KeyError:
            raise CalibrationError(
                f"calibration profile has no value for {concept_id}/{parameter_name}"
            ) from None

    def require(self, concept_id: str, parameter_names: tuple[str, ...]) -> dict[str, Any]:
        """Return all requested parameter values, fail-closed if any is absent."""
        missing = [
            name
            for name in parameter_names
            if (concept_id, name) not in self._values
        ]
        if missing:
            raise CalibrationError(
                f"calibration profile is missing required value(s) for "
                f"{concept_id}: {', '.join(missing)}"
            )
        return {name: self._values[(concept_id, name)] for name in parameter_names}

    def concept_ids(self) -> set[str]:
        return {cid for cid, _ in self._values}


def _load_yaml(path: Path, what: str) -> Any:
    if not path.exists():
        raise CalibrationError(f"{what} not found: {path}")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CalibrationError(f"{what} is not valid YAML: {exc}") from exc
    except OSError as exc:
        raise CalibrationError(f"could not read {what} {path}: {exc}") from exc


def _schema_field_lists(schema_path: Path) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Read required top-level and parameter-item field lists from the schema."""
    schema = _load_yaml(schema_path, "calibration profile schema")
    if not isinstance(schema, dict):
        raise CalibrationError("calibration profile schema must be a mapping")
    top_level = schema.get("required_top_level_fields")
    if not isinstance(top_level, list) or not top_level:
        top_level = list(_FALLBACK_REQUIRED_TOP_LEVEL)
    item_fields = (
        schema.get("field_definitions", {})
        .get("parameter_values", {})
        .get("item_required_fields")
    )
    if not isinstance(item_fields, list) or not item_fields:
        item_fields = list(_FALLBACK_ITEM_FIELDS)
    return tuple(str(f) for f in top_level), tuple(str(f) for f in item_fields)


def load_calibration_profile(
    path: str | Path,
    *,
    schema_path: str | Path | None = None,
) -> CalibrationProfile:
    """Load and fail-closed validate a calibration profile YAML file.

    Fails closed (raises ``CalibrationError``) on: a missing file, malformed
    YAML, a non-mapping document, a missing or non-list ``parameter_values``,
    a malformed parameter entry, a duplicate ``concept_id``+``parameter_name``,
    a missing required envelope field, or a forbidden execution field anywhere
    inside the profile.
    """
    profile_path = Path(path)
    resolved_schema = Path(schema_path) if schema_path is not None else DEFAULT_SCHEMA_PATH
    required_top_level, item_fields = _schema_field_lists(resolved_schema)

    data = _load_yaml(profile_path, "calibration profile")
    if not isinstance(data, dict):
        raise CalibrationError(f"{profile_path} must parse to a mapping")

    # Forbidden execution fields are rejected anywhere in the profile.
    forbidden = find_forbidden_fields(data)
    if forbidden:
        raise CalibrationError(
            f"{profile_path} contains forbidden execution field(s): {', '.join(forbidden)}"
        )

    missing_envelope = [field for field in required_top_level if field not in data]
    if missing_envelope:
        raise CalibrationError(
            f"{profile_path} is missing required envelope field(s): "
            f"{', '.join(missing_envelope)}"
        )

    profile_id = data.get("profile_id")
    if not isinstance(profile_id, str) or not profile_id:
        raise CalibrationError(f"{profile_path} profile_id must be a non-empty string")

    parameter_values = data.get("parameter_values")
    if not isinstance(parameter_values, list) or not parameter_values:
        raise CalibrationError(f"{profile_path} parameter_values must be a non-empty list")

    values: dict[tuple[str, str], Any] = {}
    for index, entry in enumerate(parameter_values):
        if not isinstance(entry, dict):
            raise CalibrationError(
                f"{profile_path} parameter_values[{index}] must be a mapping"
            )
        missing_item = [field for field in item_fields if field not in entry]
        if missing_item:
            raise CalibrationError(
                f"{profile_path} parameter_values[{index}] is missing field(s): "
                f"{', '.join(missing_item)}"
            )
        concept_id = entry.get("concept_id")
        parameter_name = entry.get("parameter_name")
        if not isinstance(concept_id, str) or not concept_id:
            raise CalibrationError(
                f"{profile_path} parameter_values[{index}] concept_id must be a non-empty string"
            )
        if not isinstance(parameter_name, str) or not parameter_name:
            raise CalibrationError(
                f"{profile_path} parameter_values[{index}] parameter_name must be a non-empty string"
            )
        key = (concept_id, parameter_name)
        if key in values:
            raise CalibrationError(
                f"{profile_path} has a duplicate parameter entry: {concept_id}/{parameter_name}"
            )
        if entry.get("value") is None:
            raise CalibrationError(
                f"{profile_path} parameter_values[{index}] ({concept_id}/{parameter_name}) "
                f"has no value"
            )
        values[key] = entry["value"]

    return CalibrationProfile(profile_id, values, data, profile_path)
