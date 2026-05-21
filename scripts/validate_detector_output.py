#!/usr/bin/env python3
"""Validate one detector output JSON document against the contract catalog."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


CATALOG_PATH = Path("spec/detector_contract_catalog.json")

FORBIDDEN_FIELDS = {
    "entry_price",
    "stop_price",
    "target_price",
    "order_type",
    "quantity",
    "position_size",
    "account_id",
    "broker",
    "fill_price",
    "pnl",
    "buy_now",
    "sell_now",
    "execute",
    "place_order",
    "reduce_position",
    "add_position",
}

REQUIRED_TOP_LEVEL_FIELDS = (
    "schema_version",
    "concept_id",
    "state",
    "action_label",
    "guardrails",
)

REQUIRED_TRUE_GUARDRAILS = (
    "no_trade_permission",
    "no_execution_fields",
    "no_broker_order_account_fields",
    "catalog_state_action_checked",
)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON parse failed for {path}: {exc}") from exc
    except OSError as exc:
        raise ValueError(f"Could not read {path}: {exc}") from exc


def load_catalog() -> dict[str, dict[str, Any]]:
    data = load_json(CATALOG_PATH)
    if not isinstance(data, dict):
        raise ValueError(f"{CATALOG_PATH} must parse to a JSON object")
    detectors = data.get("detectors")
    if not isinstance(detectors, list):
        raise ValueError(f"{CATALOG_PATH} missing detectors array")

    catalog: dict[str, dict[str, Any]] = {}
    for index, detector in enumerate(detectors, start=1):
        if not isinstance(detector, dict):
            raise ValueError(f"{CATALOG_PATH} detectors[{index}] must be an object")
        concept_id = detector.get("concept_id")
        if not isinstance(concept_id, str) or not concept_id:
            raise ValueError(f"{CATALOG_PATH} detectors[{index}] missing concept_id")
        if concept_id in catalog:
            raise ValueError(f"{CATALOG_PATH} duplicate concept_id: {concept_id}")
        catalog[concept_id] = detector
    return catalog


def find_forbidden_fields(value: Any, path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_path = f"{path}.{key}"
            if str(key).lower() in FORBIDDEN_FIELDS:
                found.append(key_path)
            found.extend(find_forbidden_fields(child, key_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(find_forbidden_fields(child, f"{path}[{index}]"))
    return found


def validate_output(output: Any, catalog: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if not isinstance(output, dict):
        return ["detector output must be a JSON object"]

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in output:
            errors.append(f"missing required field: {field}")

    if output.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    concept_id = output.get("concept_id")
    detector = None
    if not isinstance(concept_id, str) or not concept_id:
        errors.append("concept_id must be a non-empty string")
    else:
        detector = catalog.get(concept_id)
        if detector is None:
            errors.append(f"concept_id not found in catalog: {concept_id}")

    if detector is not None:
        state = output.get("state")
        allowed_states = detector.get("states_emitted") or []
        if state not in allowed_states:
            errors.append(f"state {state!r} is not allowed for concept_id {concept_id}")

        action_label = output.get("action_label")
        allowed_actions = detector.get("allowed_action_labels") or []
        if action_label not in allowed_actions:
            errors.append(f"action_label {action_label!r} is not allowed for concept_id {concept_id}")

    guardrails = output.get("guardrails")
    if not isinstance(guardrails, dict):
        errors.append("guardrails must be an object")
    else:
        for field in REQUIRED_TRUE_GUARDRAILS:
            if guardrails.get(field) is not True:
                errors.append(f"guardrails.{field} must be true")

    forbidden_paths = find_forbidden_fields(output)
    for forbidden_path in forbidden_paths:
        errors.append(f"forbidden execution field present: {forbidden_path}")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a detector output JSON file against the detector contract catalog."
    )
    parser.add_argument("output_json", type=Path, help="Path to detector output JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        catalog = load_catalog()
        output = load_json(args.output_json)
    except ValueError as exc:
        print("detector output validation FAILED")
        print(str(exc))
        return 1

    errors = validate_output(output, catalog)
    if errors:
        print("detector output validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("detector output validation PASS")
    print(f"file: {args.output_json}")
    print(f"concept_id: {output['concept_id']}")
    print(f"state: {output['state']}")
    print(f"action_label: {output['action_label']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
