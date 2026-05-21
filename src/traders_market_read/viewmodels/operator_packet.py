"""Build compact operator packet view models from validated packet artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from traders_market_read.detectors.catalog import CatalogError, DetectorCatalog, DetectorContract, load_catalog
from traders_market_read.detectors.output import GUARDRAILS, find_forbidden_fields


class OperatorPacketViewModelError(RuntimeError):
    """Raised when packet artifacts cannot be transformed safely."""


LAYER_BY_CHAPTER: dict[int, tuple[str, str]] = {
    1: ("read_discipline", "Read Discipline"),
    2: ("level_interaction", "Level Interaction"),
    3: ("auction_profile", "Auction & Profile"),
    4: ("tape_microstructure", "Tape & Microstructure"),
    5: ("momentum_day_type", "Momentum & Day Type"),
    6: ("traps_positioning", "Traps & Positioning"),
    7: ("session_context", "Session Context"),
    8: ("volatility_regime", "Volatility Regime"),
    9: ("intermarket_confirmation", "Intermarket Confirmation"),
    10: ("catalyst_interpretation", "Catalyst Interpretation"),
    11: ("trade_state_management", "Trade-State Management"),
    12: ("setup_quality", "Setup Quality"),
}


def _read_json(path: Path, label: str) -> Any:
    if not path.exists():
        raise OperatorPacketViewModelError(f"{label} not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise OperatorPacketViewModelError(f"{label} is not valid JSON: {exc}") from exc
    except OSError as exc:
        raise OperatorPacketViewModelError(f"could not read {label} {path}: {exc}") from exc


def _reject_forbidden(value: Any, label: str) -> None:
    found = find_forbidden_fields(value)
    if found:
        raise OperatorPacketViewModelError(
            f"forbidden execution field present in {label}: " + ", ".join(found)
        )


def _load_catalog() -> DetectorCatalog:
    try:
        return load_catalog()
    except CatalogError as exc:
        raise OperatorPacketViewModelError(f"detector catalog error: {exc}") from exc


def _runtime_outputs(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        outputs = raw
    elif isinstance(raw, dict) and isinstance(raw.get("outputs"), list):
        outputs = raw["outputs"]
    else:
        raise OperatorPacketViewModelError(
            "runtime output must be an array or an object with an outputs array"
        )
    normalized: list[dict[str, Any]] = []
    for index, output in enumerate(outputs):
        if not isinstance(output, dict):
            raise OperatorPacketViewModelError(f"runtime outputs[{index}] must be an object")
        normalized.append(output)
    return normalized


def _validate_outputs(
    outputs: list[dict[str, Any]], catalog: DetectorCatalog
) -> dict[str, dict[str, Any]]:
    by_concept: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    for index, output in enumerate(outputs):
        concept_id = output.get("concept_id")
        if not isinstance(concept_id, str) or not concept_id:
            raise OperatorPacketViewModelError(f"runtime outputs[{index}] missing concept_id")
        if concept_id not in catalog:
            raise OperatorPacketViewModelError(
                f"runtime output concept_id not found in catalog: {concept_id}"
            )
        if concept_id in by_concept:
            duplicates.append(concept_id)
        by_concept[concept_id] = output
        guardrails = output.get("guardrails")
        if not isinstance(guardrails, dict):
            raise OperatorPacketViewModelError(f"{concept_id}: guardrails must be an object")
        for name in sorted(GUARDRAILS):
            if guardrails.get(name) is not True:
                raise OperatorPacketViewModelError(f"{concept_id}: guardrails.{name} must be true")
    if duplicates:
        raise OperatorPacketViewModelError(
            "duplicate runtime output concept_id: " + ", ".join(sorted(set(duplicates)))
        )
    missing = [concept_id for concept_id in catalog.concept_ids if concept_id not in by_concept]
    if missing:
        raise OperatorPacketViewModelError(
            "runtime output missing catalog concept(s): " + ", ".join(missing)
        )
    return by_concept


def _validate_summary(summary: Any, outputs: list[dict[str, Any]], catalog: DetectorCatalog) -> dict[str, Any]:
    if not isinstance(summary, dict):
        raise OperatorPacketViewModelError("summary JSON must be an object")
    if summary.get("total_outputs") != len(outputs):
        raise OperatorPacketViewModelError(
            f"summary total_outputs mismatch: {summary.get('total_outputs')} != {len(outputs)}"
        )
    if summary.get("total_contracts") != len(catalog):
        raise OperatorPacketViewModelError(
            f"summary total_contracts mismatch: {summary.get('total_contracts')} != {len(catalog)}"
        )
    summary_concepts = set(summary.get("missing_inputs_by_concept", {})) | set(
        summary.get("degraded_inputs_by_concept", {})
    )
    unknown_summary = sorted(concept_id for concept_id in summary_concepts if concept_id not in catalog)
    if unknown_summary:
        raise OperatorPacketViewModelError(
            "summary references unknown concept_id(s): " + ", ".join(unknown_summary)
        )
    return summary


def _chapter_number(chapter: str) -> int:
    prefix = str(chapter).split(":", 1)[0]
    try:
        return int(prefix)
    except ValueError as exc:
        raise OperatorPacketViewModelError(f"could not parse chapter number from {chapter!r}") from exc


def _layer_for(contract: DetectorContract) -> tuple[str, str]:
    chapter_number = _chapter_number(contract.chapter)
    try:
        return LAYER_BY_CHAPTER[chapter_number]
    except KeyError as exc:
        raise OperatorPacketViewModelError(f"no layer mapping for chapter {chapter_number}") from exc


def _route(output: dict[str, Any]) -> str:
    evidence = output.get("evidence")
    if isinstance(evidence, dict) and isinstance(evidence.get("route"), str):
        return evidence["route"]
    return "UNKNOWN"


def _refusal(output: dict[str, Any]) -> bool:
    evidence = output.get("evidence")
    return isinstance(evidence, dict) and evidence.get("refusal") is True


def _reason(output: dict[str, Any]) -> str:
    evidence = output.get("evidence")
    if isinstance(evidence, dict) and isinstance(evidence.get("reason"), str):
        return evidence["reason"]
    notes = output.get("notes")
    return notes if isinstance(notes, str) and notes else ""


def _evidence_summary(output: dict[str, Any]) -> str:
    evidence = output.get("evidence")
    if not isinstance(evidence, dict):
        return "No structured evidence object was provided."
    measurements = evidence.get("measurements")
    if isinstance(measurements, dict) and measurements:
        parts = [f"{key}={measurements[key]!r}" for key in sorted(measurements)[:4]]
        if len(measurements) > 4:
            parts.append("...")
        return "Measurements: " + ", ".join(parts)
    reason = evidence.get("reason")
    if isinstance(reason, str) and reason:
        return reason
    route = evidence.get("route")
    return f"Route: {route}" if isinstance(route, str) and route else "Structured evidence present."


def _base(contract: DetectorContract, output: dict[str, Any]) -> dict[str, Any]:
    layer_id, _ = _layer_for(contract)
    return {
        "concept_id": contract.concept_id,
        "display_name": contract.display_name,
        "chapter": contract.chapter,
        "layer_id": layer_id,
        "state": output.get("state"),
    }


def _missing(summary: dict[str, Any], concept_id: str) -> list[str]:
    value = summary.get("missing_inputs_by_concept", {}).get(concept_id, [])
    return list(value) if isinstance(value, list) else []


def _degraded(summary: dict[str, Any], concept_id: str) -> list[str]:
    value = summary.get("degraded_inputs_by_concept", {}).get(concept_id, [])
    return list(value) if isinstance(value, list) else []


def _needed_evidence(contract: DetectorContract, missing_inputs: list[str]) -> list[str]:
    if missing_inputs:
        return missing_inputs
    required: list[str] = []
    for item in contract.required_inputs:
        if isinstance(item, dict) and isinstance(item.get("name"), str):
            required.append(item["name"])
    return required or [
        "Requires operator/human review evidence defined by the concept contract; runtime did not infer this judgment."
    ]


def _new_layer(contract: DetectorContract) -> dict[str, Any]:
    layer_id, display_name = _layer_for(contract)
    return {
        "layer_id": layer_id,
        "display_name": display_name,
        "chapter": contract.chapter,
        "total_outputs": 0,
        "non_refusal_count": 0,
        "refusal_count": 0,
        "review_queue_count": 0,
        "blocked_count": 0,
        "findings": [],
        "review_items": [],
        "blocked_items": [],
    }


def build_operator_packet_view_model(
    *,
    runtime_output_path: str | Path,
    summary_json_path: str | Path,
) -> dict[str, Any]:
    """Build a deterministic UI-ready operator view model."""
    runtime_path = Path(runtime_output_path)
    summary_path = Path(summary_json_path)
    runtime_raw = _read_json(runtime_path, "runtime output")
    summary_raw = _read_json(summary_path, "summary JSON")
    _reject_forbidden(runtime_raw, "runtime output")
    _reject_forbidden(summary_raw, "summary JSON")
    catalog = _load_catalog()
    outputs = _runtime_outputs(runtime_raw)
    by_concept = _validate_outputs(outputs, catalog)
    summary = _validate_summary(summary_raw, outputs, catalog)

    layers: dict[str, dict[str, Any]] = {}
    active_findings: list[dict[str, Any]] = []
    review_queue: list[dict[str, Any]] = []
    blocked_by_feed: list[dict[str, Any]] = []
    context_governance: list[dict[str, Any]] = []
    missing_or_degraded: list[dict[str, Any]] = []

    for contract in catalog:
        output = by_concept[contract.concept_id]
        layer_id, _ = _layer_for(contract)
        layer = layers.setdefault(layer_id, _new_layer(contract))
        route = _route(output)
        is_refusal = _refusal(output)
        missing_inputs = _missing(summary, contract.concept_id)
        degraded_inputs = _degraded(summary, contract.concept_id)
        layer["total_outputs"] += 1
        if is_refusal:
            layer["refusal_count"] += 1
        else:
            layer["non_refusal_count"] += 1
        if missing_inputs or degraded_inputs:
            missing_or_degraded.append(
                {
                    **_base(contract, output),
                    "missing_inputs": missing_inputs,
                    "degraded_inputs": degraded_inputs,
                    "route": route,
                }
            )

        if contract.determinism_class in {"COMPUTABLE", "CALIBRATED"} and not is_refusal:
            finding = {
                **_base(contract, output),
                "determinism_class": contract.determinism_class,
                "route": route,
                "action_label": output.get("action_label"),
                "confidence": output.get("confidence"),
                "evidence_summary": _evidence_summary(output),
                "missing_inputs": missing_inputs,
                "degraded_inputs": degraded_inputs,
            }
            active_findings.append(finding)
            layer["findings"].append(finding)
        elif contract.determinism_class == "JUDGMENT_ASSISTED" and (
            is_refusal or route == "judgment_assisted_review"
        ):
            item = {
                **_base(contract, output),
                "action_label": output.get("action_label"),
                "refusal_reason": _reason(output),
                "missing_inputs": missing_inputs,
                "degraded_inputs": degraded_inputs,
                "needed_evidence": _needed_evidence(contract, missing_inputs),
            }
            review_queue.append(item)
            layer["review_items"].append(item)
            layer["review_queue_count"] += 1
        elif (
            contract.determinism_class == "NOT_DETECTABLE_WITH_CURRENT_FEEDS"
            or route == "not_detectable_blocked"
            or "feed" in _reason(output).lower()
        ):
            item = {
                **_base(contract, output),
                "refusal_reason": _reason(output),
                "missing_inputs": missing_inputs,
                "needed_feed_or_evidence": _needed_evidence(contract, missing_inputs),
            }
            blocked_by_feed.append(item)
            layer["blocked_items"].append(item)
            layer["blocked_count"] += 1
        elif contract.determinism_class == "CONTEXT_ONLY" or route == "context_only":
            context_governance.append(
                {
                    **_base(contract, output),
                    "action_label": output.get("action_label"),
                    "boundary_note": "Context/governance only; no execution permission.",
                }
            )

    ordered_layers = [layers[layer_id] for layer_id, _ in LAYER_BY_CHAPTER.values()]
    for collection in (
        active_findings,
        review_queue,
        blocked_by_feed,
        context_governance,
        missing_or_degraded,
    ):
        collection.sort(key=lambda item: item["concept_id"])
    for layer in ordered_layers:
        layer["findings"].sort(key=lambda item: item["concept_id"])
        layer["review_items"].sort(key=lambda item: item["concept_id"])
        layer["blocked_items"].sort(key=lambda item: item["concept_id"])

    view_model = {
        "schema_version": 1,
        "source_artifacts": {
            "runtime_output": str(runtime_path),
            "summary_json": str(summary_path),
        },
        "counts": {
            "total_contracts": summary["total_contracts"],
            "total_outputs": summary["total_outputs"],
            "non_refusal_count": summary["non_refusal_count"],
            "refusal_count": summary["refusal_count"],
            "review_queue_count": summary["judgment_assisted_review_count"],
            "calibrated_non_refusal_count": summary["calibrated_non_refusal_count"],
            "computable_non_refusal_count": summary["computable_non_refusal_count"],
            "context_only_count": summary["context_only_count"],
            "not_detectable_blocked_count": summary["not_detectable_blocked_count"],
        },
        "boundary": {
            "non_executional": True,
            "no_trade_permission": True,
            "no_entries_stops_targets_sizing": True,
            "no_broker_order_account_fill_pnl": True,
            "no_autonomous_trading": True,
        },
        "market_read_layers": ordered_layers,
        "active_findings": active_findings,
        "review_queue": review_queue,
        "blocked_by_feed": blocked_by_feed,
        "context_governance": context_governance,
        "missing_or_degraded_inputs": missing_or_degraded,
    }
    _reject_forbidden(view_model, "operator view model")
    return view_model


def write_operator_packet_view_model(path: str | Path, view_model: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(view_model, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
