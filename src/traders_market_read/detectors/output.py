"""Safe detector output envelope.

Every payload the runtime emits is built here so the non-executional contract
is enforced in exactly one place:

- ``state`` must be one of the contract's ``states_emitted``.
- ``action_label`` must be one of the contract's action labels (or, for a
  state-only contract that declares no action vocabulary, one of its states).
- ``guardrails`` booleans are always present and always ``True``.
- No forbidden execution field may appear anywhere in the payload, at any
  nesting depth.

The envelope shape matches ``spec/detector_output_schema.yaml``.
"""

from __future__ import annotations

from typing import Any

from .catalog import DetectorContract

SCHEMA_VERSION = 1

# Execution fields that must never appear anywhere in a detector output.
# Mirrors spec/detector_output_schema.yaml -> forbidden_fields_anywhere.
FORBIDDEN_FIELDS = frozenset(
    {
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
)

# Guardrail booleans. The union of the schema's required-true guardrails and
# the booleans required by the TMR-P25 mission. Every one is always True.
GUARDRAILS: dict[str, bool] = {
    # Required by spec/detector_output_schema.yaml + validate_detector_output.py.
    "no_trade_permission": True,
    "no_execution_fields": True,
    "no_broker_order_account_fields": True,
    "catalog_state_action_checked": True,
    # Required by the TMR-P25 detector runtime contract.
    "non_executional": True,
    "no_order_instructions": True,
    "no_position_sizing": True,
    "no_broker_or_account_fields": True,
}

REQUIRED_TOP_LEVEL_FIELDS = (
    "schema_version",
    "concept_id",
    "state",
    "action_label",
    "guardrails",
)


class OutputError(RuntimeError):
    """Raised when a detector output would violate the non-executional contract."""


def find_forbidden_fields(value: Any, path: str = "$") -> list[str]:
    """Recursively locate any forbidden execution field key in ``value``."""
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


def _validate_state(contract: DetectorContract, state: str) -> None:
    if state not in contract.states_emitted:
        raise OutputError(
            f"{contract.concept_id}: state {state!r} is not in states_emitted"
        )


def _validate_action_label(contract: DetectorContract, action_label: str) -> None:
    allowed = contract.effective_action_labels
    if action_label not in allowed:
        raise OutputError(
            f"{contract.concept_id}: action_label {action_label!r} is not an allowed action label"
        )


def make_output(
    contract: DetectorContract,
    state: str,
    action_label: str,
    *,
    evidence: dict[str, Any] | None = None,
    confidence: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    """Build one validated, guardrailed detector output payload.

    Raises ``OutputError`` if the state or action label is outside the
    contract, or if any forbidden execution field is present.
    """
    _validate_state(contract, state)
    _validate_action_label(contract, action_label)

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "concept_id": contract.concept_id,
        "state": state,
        "action_label": action_label,
        "evidence": dict(evidence) if evidence else {},
        "confidence": confidence,
        "notes": notes,
        "guardrails": dict(GUARDRAILS),
    }

    forbidden = find_forbidden_fields(payload)
    if forbidden:
        raise OutputError(
            f"{contract.concept_id}: forbidden execution field(s) present: {', '.join(forbidden)}"
        )
    return payload


def computable_output(
    contract: DetectorContract,
    state: str,
    *,
    measurements: dict[str, Any],
    action_label: str | None = None,
    confidence: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    """A real structural detection from a COMPUTABLE detector."""
    evidence = {
        "route": "computable",
        "detector_class": contract.determinism_class,
        "measurements": measurements,
    }
    return make_output(
        contract,
        state,
        action_label if action_label is not None else state,
        evidence=evidence,
        confidence=confidence or "STRUCTURAL_OBSERVED",
        notes=notes,
    )


def refusal_output(
    contract: DetectorContract,
    state: str,
    action_label: str,
    *,
    route: str,
    reason: str,
    missing_inputs: list[str] | None = None,
    mapping_note: str | None = None,
    confidence: str | None = None,
) -> dict[str, Any]:
    """A safe refusal: the detector declines to produce a substantive claim."""
    evidence: dict[str, Any] = {
        "route": route,
        "detector_class": contract.determinism_class,
        "refusal": True,
        "reason": reason,
    }
    if missing_inputs:
        evidence["missing_required_inputs"] = list(missing_inputs)
    if mapping_note:
        evidence["label_mapping_note"] = mapping_note
    return make_output(
        contract,
        state,
        action_label,
        evidence=evidence,
        confidence=confidence or "REFUSED",
        notes=reason,
    )


def context_only_output(
    contract: DetectorContract,
    state: str,
    action_label: str,
    *,
    reason: str,
    mapping_note: str | None = None,
) -> dict[str, Any]:
    """A context/governance output that carries no actionable trigger."""
    evidence: dict[str, Any] = {
        "route": "context_only",
        "detector_class": contract.determinism_class,
        "context_only": True,
        "reason": reason,
    }
    if mapping_note:
        evidence["label_mapping_note"] = mapping_note
    return make_output(
        contract,
        state,
        action_label,
        evidence=evidence,
        confidence="CONTEXT_ONLY",
        notes=reason,
    )


def blocked_by_feeds_output(
    contract: DetectorContract,
    state: str,
    action_label: str,
    *,
    reason: str,
    mapping_note: str | None = None,
) -> dict[str, Any]:
    """A blocked output: the concept is not detectable with current feeds."""
    evidence: dict[str, Any] = {
        "route": "not_detectable_blocked",
        "detector_class": contract.determinism_class,
        "blocked_by_feeds": True,
        "reason": reason,
    }
    if mapping_note:
        evidence["label_mapping_note"] = mapping_note
    return make_output(
        contract,
        state,
        action_label,
        evidence=evidence,
        confidence="BLOCKED_BY_FEEDS",
        notes=reason,
    )


def validate_output_payload(
    output: Any, contract: DetectorContract
) -> list[str]:
    """Validate a finished payload against a contract.

    Mirrors ``scripts/validate_detector_output.py`` (with the same state-only
    handling), so the runtime can self-check every output it emits.
    """
    errors: list[str] = []
    if not isinstance(output, dict):
        return ["detector output must be a JSON object"]

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in output:
            errors.append(f"missing required field: {field}")

    if output.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version must be 1")

    if output.get("concept_id") != contract.concept_id:
        errors.append(
            f"concept_id {output.get('concept_id')!r} does not match contract {contract.concept_id!r}"
        )

    state = output.get("state")
    if state not in contract.states_emitted:
        errors.append(f"state {state!r} is not allowed for {contract.concept_id}")

    action_label = output.get("action_label")
    if action_label not in contract.effective_action_labels:
        errors.append(
            f"action_label {action_label!r} is not allowed for {contract.concept_id}"
        )

    guardrails = output.get("guardrails")
    if not isinstance(guardrails, dict):
        errors.append("guardrails must be an object")
    else:
        for name, expected in GUARDRAILS.items():
            if guardrails.get(name) is not expected:
                errors.append(f"guardrails.{name} must be true")

    for forbidden_path in find_forbidden_fields(output):
        errors.append(f"forbidden execution field present: {forbidden_path}")

    return errors
