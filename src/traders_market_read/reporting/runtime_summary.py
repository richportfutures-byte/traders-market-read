"""Summarize safe detector runtime output into an operator review packet.

This module is intentionally non-executional. It reads detector output payloads,
joins them to the detector contract catalog, and reports what the runtime did
or refused to do. It does not add detector logic, calibration values, trade
permission, order behavior, position sizing, or account behavior.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from traders_market_read.detectors.catalog import (
    DEFAULT_CATALOG_PATH,
    CatalogError,
    DetectorCatalog,
    DetectorContract,
    load_catalog,
)
from traders_market_read.detectors.output import GUARDRAILS, find_forbidden_fields


class RuntimeSummaryError(RuntimeError):
    """Raised when runtime output cannot be summarized safely."""


def _read_json(path: Path) -> Any:
    if not path.exists():
        raise RuntimeSummaryError(f"runtime output file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeSummaryError(f"runtime output is not valid JSON: {exc}") from exc
    except OSError as exc:
        raise RuntimeSummaryError(f"could not read runtime output {path}: {exc}") from exc


def load_runtime_outputs(path: str | Path) -> list[dict[str, Any]]:
    """Load a runtime output file.

    Accepts either a JSON array of detector output payloads or a JSON object
    containing an ``outputs`` array.
    """
    raw = _read_json(Path(path))
    forbidden = find_forbidden_fields(raw)
    if forbidden:
        raise RuntimeSummaryError(
            "forbidden execution field present in runtime output: "
            + ", ".join(forbidden)
        )

    if isinstance(raw, list):
        outputs = raw
    elif isinstance(raw, dict) and isinstance(raw.get("outputs"), list):
        outputs = raw["outputs"]
    else:
        raise RuntimeSummaryError(
            "runtime output must be a JSON array or an object with an outputs array"
        )

    normalized: list[dict[str, Any]] = []
    for index, output in enumerate(outputs):
        if not isinstance(output, dict):
            raise RuntimeSummaryError(f"outputs[{index}] must be a JSON object")
        normalized.append(output)
    return normalized


def _catalog(path: str | Path | None) -> DetectorCatalog:
    try:
        return load_catalog(path or DEFAULT_CATALOG_PATH)
    except CatalogError as exc:
        raise RuntimeSummaryError(str(exc)) from exc


def _required_input_names(contract: DetectorContract) -> list[str]:
    names: list[str] = []
    for item in contract.required_inputs:
        if isinstance(item, dict):
            name = item.get("name")
            if isinstance(name, str) and name:
                names.append(name)
    return names


def _optional_input_names(contract: DetectorContract) -> list[str]:
    names: list[str] = []
    for item in contract.optional_inputs:
        if isinstance(item, dict):
            name = item.get("name")
            if isinstance(name, str) and name:
                names.append(name)
    return names


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
    if isinstance(route, str) and route:
        return f"Route: {route}"
    return "Structured evidence was present without measurements."


def _missing_inputs_for(
    output: dict[str, Any], contract: DetectorContract
) -> list[str]:
    evidence = output.get("evidence") if isinstance(output.get("evidence"), dict) else {}
    explicit = evidence.get("missing_required_inputs") if isinstance(evidence, dict) else None
    if isinstance(explicit, list):
        return [str(item) for item in explicit if str(item)]
    route = evidence.get("route") if isinstance(evidence, dict) else None
    refusal = bool(evidence.get("refusal")) if isinstance(evidence, dict) else False
    if refusal or route in {"judgment_assisted_review", "not_detectable_blocked"}:
        return _required_input_names(contract)
    return []


def _guardrail_failures(output: dict[str, Any]) -> list[str]:
    concept_id = output.get("concept_id", "<unknown>")
    guardrails = output.get("guardrails")
    if not isinstance(guardrails, dict):
        return [f"{concept_id}: guardrails must be an object"]
    failures: list[str] = []
    for name in sorted(GUARDRAILS):
        if guardrails.get(name) is not True:
            failures.append(f"{concept_id}: guardrails.{name} must be true")
    return failures


def _validate_outputs(
    outputs: list[dict[str, Any]], catalog: DetectorCatalog, require_all: bool
) -> tuple[dict[str, dict[str, Any]], list[str], list[str], list[str]]:
    by_concept: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    guardrail_failures: list[str] = []

    for index, output in enumerate(outputs):
        concept_id = output.get("concept_id")
        if not isinstance(concept_id, str) or not concept_id:
            raise RuntimeSummaryError(f"outputs[{index}] missing concept_id")
        if concept_id not in catalog:
            raise RuntimeSummaryError(f"output concept_id not found in catalog: {concept_id}")
        if concept_id in by_concept:
            duplicates.append(concept_id)
        by_concept[concept_id] = output
        guardrail_failures.extend(_guardrail_failures(output))

    if duplicates:
        raise RuntimeSummaryError(
            "duplicate output concept_id: " + ", ".join(sorted(set(duplicates)))
        )
    if guardrail_failures:
        raise RuntimeSummaryError(
            "guardrail validation failed: " + "; ".join(guardrail_failures)
        )

    missing = [concept_id for concept_id in catalog.concept_ids if concept_id not in by_concept]
    if require_all and missing:
        raise RuntimeSummaryError(
            "missing output for catalog contract(s): " + ", ".join(missing)
        )
    return by_concept, missing, sorted(set(duplicates)), guardrail_failures


def build_runtime_summary(
    runtime_output_path: str | Path,
    *,
    catalog_path: str | Path | None = None,
    require_all: bool = True,
) -> dict[str, Any]:
    """Build a deterministic summary dictionary for a runtime output file."""
    path = Path(runtime_output_path)
    catalog = _catalog(catalog_path)
    outputs = load_runtime_outputs(path)
    by_concept, missing, duplicates, guardrail_failures = _validate_outputs(
        outputs, catalog, require_all
    )

    counts_by_chapter: Counter[str] = Counter()
    counts_by_class: Counter[str] = Counter()
    counts_by_route: Counter[str] = Counter()
    counts_by_state: Counter[str] = Counter()
    missing_inputs_by_concept: dict[str, list[str]] = {}
    degraded_inputs_by_concept: dict[str, list[str]] = {}
    review_queue: list[dict[str, Any]] = []

    refusal_count = 0
    computable_non_refusal_count = 0
    calibrated_non_refusal_count = 0
    judgment_assisted_review_count = 0
    context_only_count = 0
    not_detectable_blocked_count = 0

    for contract in catalog:
        output = by_concept.get(contract.concept_id)
        if output is None:
            continue
        evidence = output.get("evidence") if isinstance(output.get("evidence"), dict) else {}
        route = evidence.get("route") if isinstance(evidence, dict) else None
        route_label = route if isinstance(route, str) and route else "UNKNOWN"
        is_refusal = bool(evidence.get("refusal")) if isinstance(evidence, dict) else False

        counts_by_chapter[contract.chapter] += 1
        counts_by_class[contract.determinism_class] += 1
        counts_by_route[route_label] += 1
        counts_by_state[str(output.get("state"))] += 1
        if is_refusal:
            refusal_count += 1
        if contract.determinism_class == "COMPUTABLE" and not is_refusal:
            computable_non_refusal_count += 1
        if contract.determinism_class == "CALIBRATED" and not is_refusal:
            calibrated_non_refusal_count += 1
        if contract.determinism_class == "JUDGMENT_ASSISTED" and (
            is_refusal or route_label == "judgment_assisted_review"
        ):
            judgment_assisted_review_count += 1
        if contract.determinism_class == "CONTEXT_ONLY" or route_label == "context_only":
            context_only_count += 1
        if (
            contract.determinism_class == "NOT_DETECTABLE_WITH_CURRENT_FEEDS"
            or route_label == "not_detectable_blocked"
        ):
            not_detectable_blocked_count += 1

        missing_inputs = _missing_inputs_for(output, contract)
        if missing_inputs:
            missing_inputs_by_concept[contract.concept_id] = missing_inputs
        if route_label in {"judgment_assisted_review", "context_only"}:
            optional_inputs = _optional_input_names(contract)
            if optional_inputs:
                degraded_inputs_by_concept[contract.concept_id] = optional_inputs
        if contract.determinism_class == "JUDGMENT_ASSISTED" and (
            is_refusal or route_label == "judgment_assisted_review"
        ):
            review_queue.append(
                {
                    "concept_id": contract.concept_id,
                    "display_name": contract.display_name,
                    "chapter": contract.chapter,
                    "state": output.get("state"),
                    "action_label": output.get("action_label"),
                    "why_runtime_did_not_decide": evidence.get("reason")
                    or output.get("notes")
                    or "Runtime routed this judgment-assisted concept for review.",
                    "evidence_needed": missing_inputs or _required_input_names(contract),
                    "degraded_inputs": degraded_inputs_by_concept.get(
                        contract.concept_id, []
                    ),
                }
            )

    summary: dict[str, Any] = {
        "input_path": str(path),
        "catalog_path": str(catalog.source_path),
        "total_outputs": len(outputs),
        "total_contracts": len(catalog),
        "missing_outputs": missing,
        "duplicate_outputs": duplicates,
        "counts_by_chapter": dict(sorted(counts_by_chapter.items())),
        "counts_by_determinism_class": dict(sorted(counts_by_class.items())),
        "counts_by_route": dict(sorted(counts_by_route.items())),
        "counts_by_state": dict(sorted(counts_by_state.items())),
        "refusal_count": refusal_count,
        "non_refusal_count": len(outputs) - refusal_count,
        "guardrail_failures": guardrail_failures,
        "computable_non_refusal_count": computable_non_refusal_count,
        "calibrated_non_refusal_count": calibrated_non_refusal_count,
        "judgment_assisted_review_count": judgment_assisted_review_count,
        "context_only_count": context_only_count,
        "not_detectable_blocked_count": not_detectable_blocked_count,
        "missing_inputs_by_concept": dict(sorted(missing_inputs_by_concept.items())),
        "degraded_inputs_by_concept": dict(sorted(degraded_inputs_by_concept.items())),
        "review_queue": review_queue,
    }
    return summary


def _ordered_outputs(
    runtime_output_path: str | Path, catalog: DetectorCatalog
) -> list[tuple[DetectorContract, dict[str, Any]]]:
    outputs = load_runtime_outputs(runtime_output_path)
    by_concept, _, _, _ = _validate_outputs(outputs, catalog, True)
    return [
        (contract, by_concept[contract.concept_id])
        for contract in catalog
        if contract.concept_id in by_concept
    ]


def _line_list(items: list[str]) -> str:
    return ", ".join(items) if items else "None listed"


def render_review_packet_markdown(
    runtime_output_path: str | Path,
    summary: dict[str, Any] | None = None,
    *,
    catalog_path: str | Path | None = None,
) -> str:
    """Render a concise non-executional Markdown review packet."""
    path = Path(runtime_output_path)
    catalog = _catalog(catalog_path)
    summary = summary or build_runtime_summary(path, catalog_path=catalog_path)
    ordered = _ordered_outputs(path, catalog)

    lines: list[str] = [
        "# Detector Runtime Review Packet",
        "",
        f"Input file: `{path}`",
        "",
        "## Runtime Summary Counts",
        "",
        f"- Total contracts: {summary['total_contracts']}",
        f"- Total outputs: {summary['total_outputs']}",
        f"- Refusal count: {summary['refusal_count']}",
        f"- Non-refusal count: {summary['non_refusal_count']}",
        f"- JUDGMENT_ASSISTED review queue count: {summary['judgment_assisted_review_count']}",
        f"- Blocked-by-feed count: {summary['not_detectable_blocked_count']}",
        f"- Counts by determinism class: `{json.dumps(summary['counts_by_determinism_class'], sort_keys=True)}`",
        f"- Counts by route: `{json.dumps(summary['counts_by_route'], sort_keys=True)}`",
        "",
        "## Non-Refusal Findings",
        "",
    ]

    current_chapter: str | None = None
    non_refusal_rows = 0
    for contract, output in ordered:
        evidence = output.get("evidence") if isinstance(output.get("evidence"), dict) else {}
        if bool(evidence.get("refusal")):
            continue
        if evidence.get("route") == "not_detectable_blocked":
            continue
        if contract.chapter != current_chapter:
            current_chapter = contract.chapter
            lines.extend([f"### {current_chapter}", ""])
        non_refusal_rows += 1
        lines.extend(
            [
                f"- `{contract.concept_id}` - {contract.display_name}",
                f"  - Class: {contract.determinism_class}",
                f"  - State: `{output.get('state')}`",
                f"  - Action label: `{output.get('action_label')}`",
                f"  - Confidence: `{output.get('confidence')}`",
                f"  - Evidence summary: {_evidence_summary(output)}",
            ]
        )
    if non_refusal_rows == 0:
        lines.append("- None")

    lines.extend(["", "## Refusals and Review-Required Items", ""])
    current_class: str | None = None
    refusal_rows = 0
    for contract, output in ordered:
        evidence = output.get("evidence") if isinstance(output.get("evidence"), dict) else {}
        route = evidence.get("route") if isinstance(evidence, dict) else None
        if not bool(evidence.get("refusal")) and route != "not_detectable_blocked":
            continue
        if contract.determinism_class != current_class:
            current_class = contract.determinism_class
            lines.extend([f"### {current_class}", ""])
        refusal_rows += 1
        lines.extend(
            [
                f"- `{contract.concept_id}`",
                f"  - State: `{output.get('state')}`",
                f"  - Action label: `{output.get('action_label')}`",
                f"  - Refusal reason: {evidence.get('reason') or output.get('notes') or 'None listed'}",
                f"  - Missing inputs: {_line_list(summary['missing_inputs_by_concept'].get(contract.concept_id, []))}",
                f"  - Degraded inputs: {_line_list(summary['degraded_inputs_by_concept'].get(contract.concept_id, []))}",
            ]
        )
    if refusal_rows == 0:
        lines.append("- None")

    lines.extend(["", "## JUDGMENT_ASSISTED Review Queue", ""])
    for item in summary["review_queue"]:
        lines.extend(
            [
                f"- `{item['concept_id']}` - {item['display_name']}",
                f"  - Why runtime did not decide: {item['why_runtime_did_not_decide']}",
                f"  - Evidence needed: {_line_list(item['evidence_needed'])}",
            ]
        )
    if not summary["review_queue"]:
        lines.append("- None")

    lines.extend(["", "## Blocked-by-Feed Concepts", ""])
    blocked_rows = 0
    for contract, output in ordered:
        evidence = output.get("evidence") if isinstance(output.get("evidence"), dict) else {}
        if evidence.get("route") != "not_detectable_blocked":
            continue
        blocked_rows += 1
        lines.extend(
            [
                f"- `{contract.concept_id}`",
                f"  - Missing feed/evidence reason: {evidence.get('reason') or output.get('notes') or 'Not detectable with current feeds.'}",
            ]
        )
    if blocked_rows == 0:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This packet is non-executional. It grants no trade permission, contains no entries/stops/targets/sizing, and defines no broker/order/account/fill/P&L behavior.",
            "",
            "## Operator Usage Command",
            "",
            "```bash",
            "python3 scripts/summarize_detector_runtime.py qa/examples/detector_runtime_calibrated_output.example.json --summary-json qa/examples/detector_runtime_summary.example.json --review-md qa/examples/detector_runtime_review_packet.example.md",
            "```",
            "",
        ]
    )
    return "\n".join(lines)
