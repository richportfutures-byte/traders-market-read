"""Detector runtime orchestration.

One pass over the detector contract catalog:

- ``COMPUTABLE`` contracts route to their structural implementation.
- every other determinism class routes to safe class-level refusal handling.

The runtime returns one output payload per contract, self-validates every
payload, and reports a count summary.
"""

from __future__ import annotations

from typing import Any

from .catalog import DetectorCatalog, DetectorContract, load_catalog
from .computable import COMPUTABLE_DETECTORS
from .output import refusal_output, validate_output_payload
from .refusal import route_non_computable

# evidence.route -> summary counter key.
_ROUTE_TO_SUMMARY_KEY = {
    "computable": "computable_implemented",
    "computable_refusal": "computable_refused_or_blocked",
    "calibrated_refusal": "calibrated_refused",
    "judgment_assisted_review": "judgment_assisted_routed",
    "context_only": "context_only_routed",
    "not_detectable_blocked": "not_detectable_blocked",
}


class RuntimeReport:
    """The result of one detector runtime pass."""

    def __init__(
        self,
        outputs: list[dict[str, Any]],
        summary: dict[str, int],
        validation_errors: list[str],
        catalog_size: int,
    ) -> None:
        self.outputs = outputs
        self.summary = summary
        self.validation_errors = validation_errors
        self.catalog_size = catalog_size

    @property
    def ok(self) -> bool:
        """True when every emitted output validated against its contract."""
        return not self.validation_errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": dict(self.summary),
            "validation_errors": list(self.validation_errors),
            "outputs": self.outputs,
        }


def _output_for_contract(
    contract: DetectorContract, market_context: Any
) -> dict[str, Any]:
    """Produce exactly one output payload for one detector contract."""
    if contract.is_computable:
        computable_fn = COMPUTABLE_DETECTORS.get(contract.concept_id)
        if computable_fn is not None:
            return computable_fn(contract, market_context)
        # A COMPUTABLE contract with no structural implementation: refuse
        # rather than fabricate. (No such contract exists in the catalog today.)
        return refusal_output(
            contract,
            "REFUSE_TO_CLASSIFY"
            if "REFUSE_TO_CLASSIFY" in contract.states_emitted
            else contract.states_emitted[0],
            "REFUSE_TO_CLASSIFY"
            if "REFUSE_TO_CLASSIFY" in contract.effective_action_labels
            else contract.effective_action_labels[0],
            route="computable_refusal",
            reason="COMPUTABLE detector has no structural implementation in this runtime.",
        )
    return route_non_computable(contract)


def _empty_summary() -> dict[str, int]:
    return {
        "total_contracts": 0,
        "outputs_generated": 0,
        "computable_implemented": 0,
        "computable_refused_or_blocked": 0,
        "calibrated_refused": 0,
        "judgment_assisted_routed": 0,
        "context_only_routed": 0,
        "not_detectable_blocked": 0,
        "total_refusals": 0,
    }


def run(
    market_context: Any,
    *,
    catalog: DetectorCatalog | None = None,
    concept_id: str | None = None,
) -> RuntimeReport:
    """Run detector contracts against one input fixture.

    By default every contract in the catalog runs in a single pass. When
    ``concept_id`` is supplied, only that contract runs.

    Each output is self-validated against its contract; any validation failure
    is collected into ``RuntimeReport.validation_errors``.
    """
    active_catalog = catalog if catalog is not None else load_catalog()

    if concept_id is not None:
        contracts = [active_catalog.get(concept_id)]
    else:
        contracts = active_catalog.contracts

    outputs: list[dict[str, Any]] = []
    validation_errors: list[str] = []
    summary = _empty_summary()
    summary["total_contracts"] = len(active_catalog)

    for contract in contracts:
        output = _output_for_contract(contract, market_context)
        outputs.append(output)

        errors = validate_output_payload(output, contract)
        for error in errors:
            validation_errors.append(f"{contract.concept_id}: {error}")

        route = output.get("evidence", {}).get("route")
        summary_key = _ROUTE_TO_SUMMARY_KEY.get(route)
        if summary_key is not None:
            summary[summary_key] += 1

    summary["outputs_generated"] = len(outputs)
    summary["total_refusals"] = len(outputs) - summary["computable_implemented"]
    return RuntimeReport(outputs, summary, validation_errors, len(active_catalog))
