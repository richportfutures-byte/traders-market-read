#!/usr/bin/env python3
"""Validate detection spec coverage and optionally emit traceability CSV."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised only on missing dependency.
    print("P20 validation FAILED")
    print("PyYAML is required but is not available in this environment.")
    raise SystemExit(2) from exc


ROOT = Path.cwd()
REGISTRY_PATH = Path("spec/concept_registry.yaml")
SCHEMA_PATH = Path("spec/detection_spec_schema.yaml")
MATRIX_PATH = Path("qa/concept_determinism_matrix.csv")
SPEC_DIR = Path("spec/detection_specs")

FORBIDDEN_EXECUTION_STRINGS = (
    "BUY_NOW",
    "SELL_NOW",
    "ENTER_LONG",
    "ENTER_SHORT",
    "PLACE_ORDER",
    "SET_STOP_AT",
    "POSITION_SIZE",
    "AUTOMATED_EXECUTION",
    "GUARANTEED_SIGNAL",
    "HIGH_PROBABILITY_TRADE",
)

TRACEABILITY_FIELDS = (
    "chapter",
    "concept_id",
    "display_name",
    "determinism_class",
    "glossary_ref",
    "spec_file",
    "review_status",
    "required_inputs_count",
    "optional_inputs_count",
    "states_emitted_count",
    "forbidden_outputs_count",
)


def load_yaml(path: Path, errors: list[str]) -> Any:
    if not path.exists():
        errors.append(f"Missing required file: {path}")
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        errors.append(f"YAML parse failed for {path}: {exc}")
    except OSError as exc:
        errors.append(f"Could not read {path}: {exc}")
    return None


def load_matrix(path: Path, errors: list[str]) -> dict[tuple[str, str], dict[str, str]]:
    rows_by_key: dict[tuple[str, str], dict[str, str]] = {}
    if not path.exists():
        errors.append(f"Missing required file: {path}")
        return rows_by_key
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            required_columns = {"chapter_number", "concept_name", "determinism_class"}
            missing_columns = required_columns.difference(reader.fieldnames or ())
            if missing_columns:
                errors.append(
                    f"{path} missing required columns: {', '.join(sorted(missing_columns))}"
                )
                return rows_by_key
            for line_number, row in enumerate(reader, start=2):
                chapter = (row.get("chapter_number") or "").strip()
                concept_name = (row.get("concept_name") or "").strip()
                if not chapter or not concept_name:
                    errors.append(f"{path}:{line_number} missing chapter_number or concept_name")
                    continue
                key = (chapter, concept_name)
                if key in rows_by_key:
                    errors.append(
                        f"{path}:{line_number} duplicate matrix row for chapter {chapter}, {concept_name}"
                    )
                rows_by_key[key] = row
    except csv.Error as exc:
        errors.append(f"CSV parse failed for {path}: {exc}")
    except OSError as exc:
        errors.append(f"Could not read {path}: {exc}")
    return rows_by_key


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def sorted_registry_entries(registry_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        registry_entries,
        key=lambda entry: (int(entry.get("chapter_number") or 0), str(entry.get("concept_id") or "")),
    )


def get_allowed_review_statuses(schema: Any, errors: list[str]) -> set[str]:
    if not isinstance(schema, dict):
        return set()
    values = (
        schema.get("field_definitions", {})
        .get("review_status", {})
        .get("allowed_values", [])
    )
    if not isinstance(values, list) or not values:
        errors.append(f"{SCHEMA_PATH} does not define review_status.allowed_values")
        return set()
    return {str(value) for value in values}


def validate_registry(registry: Any, errors: list[str]) -> list[dict[str, Any]]:
    if not isinstance(registry, dict):
        errors.append(f"{REGISTRY_PATH} must parse to a mapping")
        return []
    entries = registry.get("entries")
    if not isinstance(entries, list):
        errors.append(f"{REGISTRY_PATH} must contain an entries list")
        return []
    valid_entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            errors.append(f"{REGISTRY_PATH} entries[{index}] must be a mapping")
            continue
        concept_id = entry.get("concept_id")
        if not concept_id:
            errors.append(f"{REGISTRY_PATH} entries[{index}] missing concept_id")
            continue
        if concept_id in seen:
            errors.append(f"{REGISTRY_PATH} duplicate concept_id: {concept_id}")
        seen.add(concept_id)
        valid_entries.append(entry)
    declared_count = registry.get("concept_count")
    if declared_count is not None and declared_count != len(valid_entries):
        errors.append(
            f"{REGISTRY_PATH} concept_count is {declared_count}, but entries contain {len(valid_entries)} concepts"
        )
    return valid_entries


def find_forbidden_strings(path: Path, errors: list[str]) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"Could not scan {path} for forbidden execution strings: {exc}")
        return
    for forbidden in FORBIDDEN_EXECUTION_STRINGS:
        if forbidden in text:
            errors.append(f"{path} contains forbidden execution string: {forbidden}")


def validate_specs(
    registry_entries: list[dict[str, Any]],
    matrix_rows: dict[tuple[str, str], dict[str, str]],
    allowed_review_statuses: set[str],
    errors: list[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    if not SPEC_DIR.exists():
        errors.append(f"Missing required directory: {SPEC_DIR}")
        return {}, {
            "registry_concepts": len(registry_entries),
            "spec_files": 0,
            "unique_spec_concepts": 0,
            "missing": len(registry_entries),
            "duplicates": 0,
            "extra": 0,
        }
    if not SPEC_DIR.is_dir():
        errors.append(f"{SPEC_DIR} exists but is not a directory")
        return {}, {
            "registry_concepts": len(registry_entries),
            "spec_files": 0,
            "unique_spec_concepts": 0,
            "missing": len(registry_entries),
            "duplicates": 0,
            "extra": 0,
        }

    registry_by_id = {str(entry["concept_id"]): entry for entry in registry_entries}
    specs_by_concept: dict[str, list[dict[str, Any]]] = defaultdict(list)
    spec_files = sorted(SPEC_DIR.glob("*.yaml"))

    for path in spec_files:
        find_forbidden_strings(path, errors)
        spec = load_yaml(path, errors)
        if not isinstance(spec, dict):
            errors.append(f"{path} must parse to a mapping")
            continue

        concept_id = spec.get("concept_id")
        if not concept_id:
            errors.append(f"{path} missing concept_id")
            continue
        concept_id = str(concept_id)
        spec["_spec_path"] = str(path)
        specs_by_concept[concept_id].append(spec)

        if concept_id not in registry_by_id:
            errors.append(f"{path} concept_id not present in registry: {concept_id}")
            continue

        registry_entry = registry_by_id[concept_id]
        registry_class = registry_entry.get("determinism_class")
        spec_class = spec.get("determinism_class")
        if spec_class != registry_class:
            errors.append(
                f"{path} determinism_class {spec_class!r} does not match registry {registry_class!r}"
            )

        matrix_key = (
            str(registry_entry.get("chapter_number") or ""),
            str(registry_entry.get("concept_name") or ""),
        )
        matrix_row = matrix_rows.get(matrix_key)
        if matrix_row:
            matrix_class = matrix_row.get("determinism_class")
            if spec_class != matrix_class:
                errors.append(
                    f"{path} determinism_class {spec_class!r} does not match matrix {matrix_class!r}"
                )

        review_status = spec.get("review_status")
        if review_status not in allowed_review_statuses:
            errors.append(
                f"{path} review_status {review_status!r} is not schema-allowed "
                f"({', '.join(sorted(allowed_review_statuses))})"
            )

        if "forbidden_outputs" not in spec:
            errors.append(f"{path} missing forbidden_outputs")

    duplicate_count = 0
    single_spec_by_concept: dict[str, dict[str, Any]] = {}
    for concept_id, matching_specs in specs_by_concept.items():
        if len(matching_specs) > 1:
            duplicate_count += len(matching_specs) - 1
            locations = ", ".join(spec["_spec_path"] for spec in matching_specs)
            errors.append(f"Duplicate spec concept_id {concept_id}: {locations}")
        single_spec_by_concept[concept_id] = matching_specs[0]

    registry_ids = set(registry_by_id)
    spec_ids = set(specs_by_concept)
    missing_ids = sorted(registry_ids - spec_ids)
    extra_ids = sorted(spec_ids - registry_ids)
    for concept_id in missing_ids:
        errors.append(f"Registry concept_id has no spec: {concept_id}")
    for concept_id in extra_ids:
        errors.append(f"Spec concept_id has no registry entry: {concept_id}")

    counts = {
        "registry_concepts": len(registry_entries),
        "spec_files": len(spec_files),
        "unique_spec_concepts": len(spec_ids),
        "missing": len(missing_ids),
        "duplicates": duplicate_count,
        "extra": len(extra_ids),
    }
    return single_spec_by_concept, counts


def build_traceability_rows(
    registry_entries: list[dict[str, Any]],
    specs_by_concept: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in sorted_registry_entries(registry_entries):
        concept_id = str(entry.get("concept_id") or "")
        if concept_id in seen:
            continue
        seen.add(concept_id)
        spec = specs_by_concept.get(concept_id, {})
        chapter_number = entry.get("chapter_number") or ""
        chapter_title = entry.get("chapter_title") or ""
        glossary_ref = spec.get("glossary_ref") or entry.get("glossary_path") or ""
        rows.append(
            {
                "chapter": f"{chapter_number}: {chapter_title}",
                "concept_id": concept_id,
                "display_name": spec.get("display_name") or entry.get("concept_name") or "",
                "determinism_class": spec.get("determinism_class") or entry.get("determinism_class") or "",
                "glossary_ref": glossary_ref,
                "spec_file": spec.get("_spec_path") or "",
                "review_status": spec.get("review_status") or "",
                "required_inputs_count": len(as_list(spec.get("required_inputs"))),
                "optional_inputs_count": len(as_list(spec.get("optional_inputs"))),
                "states_emitted_count": len(as_list(spec.get("states_emitted"))),
                "forbidden_outputs_count": len(as_list(spec.get("forbidden_outputs"))),
            }
        )
    return rows


def write_traceability_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRACEABILITY_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def print_summary(
    passed: bool,
    counts: dict[str, int],
    errors: list[str],
    traceability_path: Path | None = None,
    traceability_rows: int | None = None,
) -> None:
    print(f"P20 validation {'PASS' if passed else 'FAILED'}")
    print(f"registry concept count: {counts.get('registry_concepts', 0)}")
    print(f"spec file count: {counts.get('spec_files', 0)}")
    print(f"unique spec concept_id count: {counts.get('unique_spec_concepts', 0)}")
    print(f"missing count: {counts.get('missing', 0)}")
    print(f"duplicate count: {counts.get('duplicates', 0)}")
    print(f"extra count: {counts.get('extra', 0)}")
    if traceability_path is not None and traceability_rows is not None:
        print(f"traceability csv: wrote {traceability_rows} rows to {traceability_path}")
    if errors:
        print("errors:")
        for error in errors[:50]:
            print(f"- {error}")
        if len(errors) > 50:
            print(f"- ... {len(errors) - 50} additional errors omitted")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate detection spec registry coverage and optional traceability output."
    )
    parser.add_argument(
        "--traceability-csv",
        type=Path,
        help="Write deterministic glossary-to-spec traceability CSV after validation passes.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []

    registry = load_yaml(REGISTRY_PATH, errors)
    schema = load_yaml(SCHEMA_PATH, errors)
    matrix_rows = load_matrix(MATRIX_PATH, errors)

    if schema is not None and not isinstance(schema, dict):
        errors.append(f"{SCHEMA_PATH} must parse to a mapping")
    registry_entries = validate_registry(registry, errors)
    allowed_review_statuses = get_allowed_review_statuses(schema, errors)

    specs_by_concept, counts = validate_specs(
        registry_entries,
        matrix_rows,
        allowed_review_statuses,
        errors,
    )

    if errors:
        print_summary(False, counts, errors)
        return 1

    traceability_rows = None
    if args.traceability_csv:
        rows = build_traceability_rows(registry_entries, specs_by_concept)
        write_traceability_csv(args.traceability_csv, rows)
        traceability_rows = len(rows)

    print_summary(True, counts, errors, args.traceability_csv, traceability_rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
