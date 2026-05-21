#!/usr/bin/env python3
"""Extract a value-free calibration parameter inventory from detection specs."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised only on missing dependency.
    print("P21 calibration inventory extraction FAILED")
    print("PyYAML is required but is not available in this environment.")
    raise SystemExit(2) from exc


SPEC_DIR = Path("spec/detection_specs")
OUTPUT_PATH = Path("qa/calibration_parameter_inventory.csv")

FIELDNAMES = (
    "chapter",
    "concept_id",
    "display_name",
    "determinism_class",
    "spec_file",
    "parameter_name",
    "parameter_description",
    "parameter_type_if_available",
    "calibration_scope",
    "required_for_detection",
    "missing_feed_behavior",
    "notes",
)

INCLUDED_CLASSES = {"CALIBRATED", "JUDGMENT_ASSISTED", "COMPUTABLE"}
EXCLUDED_STATUSES = {"not_applicable"}


def load_spec(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML parse failed for {path}: {exc}") from exc
    except OSError as exc:
        raise ValueError(f"Could not read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} must parse to a mapping")
    return data


def stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return " ".join(value.split())
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return "; ".join(stringify(item) for item in value if stringify(item))
    if isinstance(value, dict):
        parts = []
        for key in sorted(value):
            rendered = stringify(value[key])
            if rendered:
                parts.append(f"{key}: {rendered}")
        return "; ".join(parts)
    return str(value)


def chapter_label(spec: dict[str, Any]) -> str:
    chapter = spec.get("chapter")
    if not isinstance(chapter, dict):
        return ""
    number = stringify(chapter.get("chapter_number"))
    title = stringify(chapter.get("chapter_title"))
    if number and title:
        return f"{number}: {title}"
    return number or title


def missing_feed_behavior(spec: dict[str, Any]) -> str:
    behavior = spec.get("unavailable_input_behavior")
    if isinstance(behavior, dict):
        preferred_keys = (
            "missing_calibration_parameters",
            "missing_required_input",
            "missing_required_inputs",
            "missing_optional_input",
            "missing_optional_inputs",
        )
        parts = []
        for key in preferred_keys:
            if key in behavior:
                rendered = stringify(behavior[key])
                if rendered:
                    parts.append(f"{key}: {rendered}")
        if parts:
            return "; ".join(parts)
    return stringify(behavior)


def required_for_detection(parameter: dict[str, Any]) -> str:
    status = stringify(parameter.get("status"))
    if status == "review_required":
        return "REVIEW_REQUIRED"
    if status in {
        "calibration_required",
        "configuration_required",
        "convention_default",
        "convention_inherited",
        "external_definition_required",
    }:
        return "YES"
    if status:
        return status
    return ""


def parameter_type(parameter: dict[str, Any]) -> str:
    return (
        stringify(parameter.get("parameter_type"))
        or stringify(parameter.get("type"))
        or stringify(parameter.get("unit"))
    )


def notes_for(parameter: dict[str, Any]) -> str:
    notes = []
    status = stringify(parameter.get("status"))
    unit = stringify(parameter.get("unit"))
    if status:
        notes.append(f"status={status}")
    if unit:
        notes.append(f"unit={unit}")
    if parameter.get("value") is not None:
        notes.append("source_spec_declares_value; inventory_omits_values")
    return "; ".join(notes)


def include_parameter(spec: dict[str, Any], parameter: dict[str, Any]) -> bool:
    determinism_class = stringify(spec.get("determinism_class"))
    status = stringify(parameter.get("status"))
    if determinism_class not in INCLUDED_CLASSES:
        return False
    if status in EXCLUDED_STATUSES:
        return False
    if not stringify(parameter.get("name")):
        return False
    return True


def build_rows(spec_files: list[Path]) -> tuple[list[dict[str, str]], Counter[str], int]:
    rows: list[dict[str, str]] = []
    seen_concepts: dict[str, Path] = {}
    specs_with_parameters = 0
    breakdown: Counter[str] = Counter()

    for path in spec_files:
        spec = load_spec(path)
        concept_id = stringify(spec.get("concept_id"))
        if not concept_id:
            raise ValueError(f"{path} missing concept_id")
        if concept_id in seen_concepts:
            raise ValueError(f"Duplicate concept_id {concept_id}: {seen_concepts[concept_id]} and {path}")
        seen_concepts[concept_id] = path

        parameters = spec.get("calibration_parameters")
        if parameters is None:
            parameters = []
        if not isinstance(parameters, list):
            raise ValueError(f"{path} calibration_parameters must be a list")

        included_for_spec = 0
        for index, parameter in enumerate(parameters, start=1):
            if not isinstance(parameter, dict):
                raise ValueError(f"{path} calibration_parameters[{index}] must be a mapping")
            if not include_parameter(spec, parameter):
                continue

            determinism_class = stringify(spec.get("determinism_class"))
            rows.append(
                {
                    "chapter": chapter_label(spec),
                    "concept_id": concept_id,
                    "display_name": stringify(spec.get("display_name") or spec.get("concept_name")),
                    "determinism_class": determinism_class,
                    "spec_file": str(path),
                    "parameter_name": stringify(parameter.get("name")),
                    "parameter_description": stringify(parameter.get("description")),
                    "parameter_type_if_available": parameter_type(parameter),
                    "calibration_scope": stringify(parameter.get("calibration_scope")),
                    "required_for_detection": required_for_detection(parameter),
                    "missing_feed_behavior": missing_feed_behavior(spec),
                    "notes": notes_for(parameter),
                }
            )
            included_for_spec += 1
            breakdown[determinism_class] += 1
        if included_for_spec:
            specs_with_parameters += 1

    rows.sort(
        key=lambda row: (
            chapter_sort_key(row["chapter"]),
            row["concept_id"],
            row["parameter_name"],
        )
    )
    return rows, breakdown, specs_with_parameters


def chapter_sort_key(chapter: str) -> tuple[int, str]:
    prefix = chapter.split(":", 1)[0].strip()
    try:
        return int(prefix), chapter
    except ValueError:
        return 0, chapter


def write_inventory(rows: list[dict[str, str]]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    if not SPEC_DIR.exists() or not SPEC_DIR.is_dir():
        print("P21 calibration inventory extraction FAILED")
        print(f"Missing detection spec directory: {SPEC_DIR}")
        return 1

    spec_files = sorted(SPEC_DIR.glob("*.yaml"))
    try:
        rows, breakdown, specs_with_parameters = build_rows(spec_files)
        write_inventory(rows)
    except ValueError as exc:
        print("P21 calibration inventory extraction FAILED")
        print(str(exc))
        return 1

    print("P21 calibration inventory extraction PASS")
    print(f"specs scanned: {len(spec_files)}")
    print(f"specs with parameters: {specs_with_parameters}")
    print(f"parameter rows written: {len(rows)}")
    print("determinism_class breakdown:")
    for determinism_class in sorted(breakdown):
        print(f"- {determinism_class}: {breakdown[determinism_class]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
