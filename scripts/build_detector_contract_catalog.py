#!/usr/bin/env python3
"""Build a normalized detector contract catalog from detection specs."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised only on missing dependency.
    print("P22 detector contract catalog generation FAILED")
    print("PyYAML is required but is not available in this environment.")
    raise SystemExit(2) from exc


SPEC_DIR = Path("spec/detection_specs")
TRACEABILITY_CSV = Path("qa/glossary_to_spec_traceability.csv")
CALIBRATION_INVENTORY_CSV = Path("qa/calibration_parameter_inventory.csv")
OUTPUT_PATH = Path("spec/detector_contract_catalog.json")

REQUIRED_SPEC_FIELDS = (
    "concept_id",
    "concept_name",
    "chapter",
    "determinism_class",
    "review_status",
    "required_inputs",
    "optional_inputs",
    "calibration_parameters",
    "output_labels",
    "forbidden_outputs",
    "unavailable_input_behavior",
    "refusal_conditions",
    "failure_modes",
)

PARAMETER_VALUE_FIELDS = {"value"}


def load_yaml(path: Path) -> dict[str, Any]:
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


def load_traceability(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        raise ValueError(f"Missing traceability CSV: {path}")
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            required = {"concept_id", "display_name", "glossary_ref", "spec_file"}
            missing = required.difference(reader.fieldnames or ())
            if missing:
                raise ValueError(f"{path} missing columns: {', '.join(sorted(missing))}")
            rows = {}
            for row in reader:
                concept_id = stringify(row.get("concept_id"))
                if concept_id:
                    rows[concept_id] = row
            return rows
    except csv.Error as exc:
        raise ValueError(f"CSV parse failed for {path}: {exc}") from exc
    except OSError as exc:
        raise ValueError(f"Could not read {path}: {exc}") from exc


def load_calibration_inventory_counts(path: Path) -> Counter[str]:
    if not path.exists():
        raise ValueError(f"Missing calibration inventory CSV: {path}")
    counts: Counter[str] = Counter()
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if "concept_id" not in (reader.fieldnames or ()):
                raise ValueError(f"{path} missing concept_id column")
            for row in reader:
                concept_id = stringify(row.get("concept_id"))
                if concept_id:
                    counts[concept_id] += 1
    except csv.Error as exc:
        raise ValueError(f"CSV parse failed for {path}: {exc}") from exc
    except OSError as exc:
        raise ValueError(f"Could not read {path}: {exc}") from exc
    return counts


def stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def as_list(value: Any, field: str, path: Path) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{path} {field} must be a list")
    return value


def chapter_label(spec: dict[str, Any], path: Path) -> str:
    chapter = spec.get("chapter")
    if not isinstance(chapter, dict):
        raise ValueError(f"{path} chapter must be a mapping")
    number = stringify(chapter.get("chapter_number"))
    title = stringify(chapter.get("chapter_title"))
    if not number or not title:
        raise ValueError(f"{path} chapter must include chapter_number and chapter_title")
    return f"{number}: {title}"


def chapter_sort_key(chapter: str) -> tuple[int, str]:
    prefix = chapter.split(":", 1)[0].strip()
    try:
        return int(prefix), chapter
    except ValueError:
        return 0, chapter


def glossary_ref(spec: dict[str, Any], trace_row: dict[str, str] | None) -> str:
    if trace_row and stringify(trace_row.get("glossary_ref")):
        return stringify(trace_row.get("glossary_ref"))
    semantic_source = spec.get("semantic_source")
    if isinstance(semantic_source, dict):
        return stringify(semantic_source.get("glossary_path"))
    chapter = spec.get("chapter")
    if isinstance(chapter, dict):
        return stringify(chapter.get("glossary_path"))
    return ""


def normalize_parameters(parameters: list[Any], path: Path) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for index, parameter in enumerate(parameters, start=1):
        if not isinstance(parameter, dict):
            raise ValueError(f"{path} calibration_parameters[{index}] must be a mapping")
        name = stringify(parameter.get("name"))
        if not name:
            raise ValueError(f"{path} calibration_parameters[{index}] missing name")
        normalized.append(
            {
                key: value
                for key, value in parameter.items()
                if key not in PARAMETER_VALUE_FIELDS
            }
        )
    return normalized


def validate_required_fields(spec: dict[str, Any], path: Path) -> None:
    missing = [field for field in REQUIRED_SPEC_FIELDS if field not in spec]
    if missing:
        raise ValueError(f"{path} missing required catalog source fields: {', '.join(missing)}")


def detector_from_spec(
    path: Path,
    spec: dict[str, Any],
    trace_row: dict[str, str] | None,
    inventory_counts: Counter[str],
) -> dict[str, Any]:
    validate_required_fields(spec, path)

    concept_id = stringify(spec.get("concept_id"))
    if not concept_id:
        raise ValueError(f"{path} missing concept_id")
    determinism_class = stringify(spec.get("determinism_class"))
    chapter = chapter_label(spec, path)
    states_emitted = spec.get("states_emitted")
    if states_emitted is None:
        states_emitted = spec.get("output_labels")

    detector = {
        "concept_id": concept_id,
        "display_name": stringify(
            (trace_row or {}).get("display_name") or spec.get("display_name") or spec.get("concept_name")
        ),
        "chapter": chapter,
        "glossary_ref": glossary_ref(spec, trace_row),
        "spec_file": str(path),
        "determinism_class": determinism_class,
        "review_status": stringify(spec.get("review_status")),
        "required_inputs": as_list(spec.get("required_inputs"), "required_inputs", path),
        "optional_inputs": as_list(spec.get("optional_inputs"), "optional_inputs", path),
        "parameters": normalize_parameters(
            as_list(spec.get("calibration_parameters"), "calibration_parameters", path),
            path,
        ),
        "states_emitted": as_list(states_emitted, "states_emitted/output_labels", path),
        "allowed_action_labels": as_list(spec.get("allowed_action_labels", []), "allowed_action_labels", path),
        "forbidden_outputs": as_list(spec.get("forbidden_outputs"), "forbidden_outputs", path),
        "refusal_behavior": {
            "unavailable_input_behavior": spec.get("unavailable_input_behavior"),
            "refusal_conditions": as_list(spec.get("refusal_conditions"), "refusal_conditions", path),
        },
        "failure_modes": as_list(spec.get("failure_modes"), "failure_modes", path),
        "calibration_required": bool(inventory_counts.get(concept_id))
        or determinism_class in {"CALIBRATED", "JUDGMENT_ASSISTED"},
        "context_only": determinism_class == "CONTEXT_ONLY",
        "not_detectable_with_current_feeds": determinism_class == "NOT_DETECTABLE_WITH_CURRENT_FEEDS",
    }

    empty_required = [
        field
        for field in (
            "display_name",
            "chapter",
            "glossary_ref",
            "determinism_class",
            "review_status",
            "spec_file",
        )
        if not detector[field]
    ]
    if empty_required:
        raise ValueError(f"{path} missing required catalog values: {', '.join(empty_required)}")
    return detector


def build_catalog() -> dict[str, Any]:
    if not SPEC_DIR.exists() or not SPEC_DIR.is_dir():
        raise ValueError(f"Missing detection spec directory: {SPEC_DIR}")

    traceability = load_traceability(TRACEABILITY_CSV)
    inventory_counts = load_calibration_inventory_counts(CALIBRATION_INVENTORY_CSV)
    spec_files = sorted(SPEC_DIR.glob("*.yaml"))
    detectors: list[dict[str, Any]] = []
    seen: dict[str, Path] = {}

    for path in spec_files:
        spec = load_yaml(path)
        concept_id = stringify(spec.get("concept_id"))
        if not concept_id:
            raise ValueError(f"{path} missing concept_id")
        if concept_id in seen:
            raise ValueError(f"Duplicate concept_id {concept_id}: {seen[concept_id]} and {path}")
        seen[concept_id] = path
        detectors.append(detector_from_spec(path, spec, traceability.get(concept_id), inventory_counts))

    detectors.sort(key=lambda item: (chapter_sort_key(item["chapter"]), item["concept_id"]))

    by_determinism_class = Counter(detector["determinism_class"] for detector in detectors)
    by_chapter = Counter(detector["chapter"] for detector in detectors)
    counts = {
        "total_specs": len(detectors),
        "by_determinism_class": dict(sorted(by_determinism_class.items())),
        "by_chapter": dict(sorted(by_chapter.items(), key=lambda item: chapter_sort_key(item[0]))),
        "specs_with_parameters": sum(1 for detector in detectors if detector["parameters"]),
        "specs_with_required_inputs": sum(1 for detector in detectors if detector["required_inputs"]),
        "specs_with_refusal_behavior": sum(
            1
            for detector in detectors
            if detector["refusal_behavior"]["unavailable_input_behavior"]
            or detector["refusal_behavior"]["refusal_conditions"]
        ),
    }

    return {
        "schema_version": 1,
        "generated_from": {
            "detection_specs_dir": str(SPEC_DIR),
            "traceability_csv": str(TRACEABILITY_CSV),
            "calibration_inventory_csv": str(CALIBRATION_INVENTORY_CSV),
        },
        "counts": counts,
        "detectors": detectors,
    }


def write_catalog(catalog: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(catalog, handle, indent=2, sort_keys=False, ensure_ascii=False, default=str)
        handle.write("\n")


def main() -> int:
    try:
        catalog = build_catalog()
        write_catalog(catalog)
    except ValueError as exc:
        print("P22 detector contract catalog generation FAILED")
        print(str(exc))
        return 1

    counts = catalog["counts"]
    print("P22 detector contract catalog generation PASS")
    print(f"total specs: {counts['total_specs']}")
    print(f"specs with parameters: {counts['specs_with_parameters']}")
    print(f"specs with required inputs: {counts['specs_with_required_inputs']}")
    print(f"specs with refusal behavior: {counts['specs_with_refusal_behavior']}")
    print("determinism_class breakdown:")
    for determinism_class, count in counts["by_determinism_class"].items():
        print(f"- {determinism_class}: {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
