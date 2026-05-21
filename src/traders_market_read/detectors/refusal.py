"""Class-level safe routing for non-computable detector contracts.

A non-computable concept must never be turned into a fake deterministic
decision. This module maps each determinism class to a safe, contract-valid
output drawn from that contract's own declared labels:

- ``CALIBRATED``                        -> refusal: calibration profile absent.
- ``JUDGMENT_ASSISTED``                 -> review-required / insufficient-evidence.
- ``CONTEXT_ONLY``                      -> context/governance output only.
- ``NOT_DETECTABLE_WITH_CURRENT_FEEDS`` -> blocked-by-feeds output.

Label selection walks an ordered list of matchers per class. Each matcher is
either an exact label or a substring. The first label a contract actually
declares wins, so every output uses the contract's own vocabulary. If a
contract declares no recognizable safe label, the first declared label is used
as a last resort and the substitution is recorded in the output evidence.
"""

from __future__ import annotations

from typing import Any

from .catalog import DetectorContract
from .output import (
    blocked_by_feeds_output,
    context_only_output,
    refusal_output,
)

# A matcher is (mode, pattern); mode is "exact" or "sub" (substring).
_Matcher = tuple[str, str]

# Ordered state matchers per determinism class, most preferred first.
#
# For CALIBRATED / JUDGMENT_ASSISTED / NOT_DETECTABLE the substring matchers
# are restricted to refusal/confidence/review tokens. The "CONTEXT" substring
# is deliberately not used for those classes because several contracts name
# substantive market-read states with a "_CONTEXT" suffix (for example
# LIQUIDATION_CONTEXT); a refusal must never land on one of those.
_STATE_MATCHERS: dict[str, tuple[_Matcher, ...]] = {
    "CALIBRATED": (
        ("exact", "INSUFFICIENT_EVIDENCE"),
        ("exact", "REFUSE_TO_CLASSIFY"),
        ("exact", "CONTEXT_ONLY"),
        ("exact", "REVIEW_REQUIRED"),
        ("exact", "CONFIRMATION_REQUIRED"),
        ("sub", "REVIEW"),
        ("exact", "DEGRADED_CONFIDENCE"),
        ("exact", "PENDING"),
        ("sub", "INSUFFICIENT"),
        ("sub", "REFUSE"),
        ("sub", "DEGRADED"),
        ("sub", "CALIBRATION"),
        ("sub", "PROVISIONAL"),
    ),
    "JUDGMENT_ASSISTED": (
        ("exact", "REVIEW_REQUIRED"),
        ("exact", "INSUFFICIENT_EVIDENCE"),
        ("exact", "REFUSE_TO_CLASSIFY"),
        ("exact", "CONFIRMATION_REQUIRED"),
        ("exact", "CONTEXT_ONLY"),
        ("sub", "REVIEW"),
        ("sub", "PROVISIONAL"),
        ("sub", "INSUFFICIENT"),
        ("sub", "REFUSE"),
        ("exact", "DEGRADED_CONFIDENCE"),
        ("exact", "PENDING"),
        ("sub", "DEGRADED"),
    ),
    "CONTEXT_ONLY": (
        ("exact", "CONTEXT_ONLY"),
        ("sub", "CONTEXT_ONLY"),
        ("sub", "CONTEXT"),
        ("exact", "REVIEW_REQUIRED"),
        ("sub", "REVIEW"),
        ("sub", "BOUNDARY"),
        ("exact", "INSUFFICIENT_EVIDENCE"),
        ("exact", "REFUSE_TO_CLASSIFY"),
        ("exact", "DEGRADED_CONFIDENCE"),
    ),
    "NOT_DETECTABLE_WITH_CURRENT_FEEDS": (
        ("exact", "BLOCKED_BY_FEEDS"),
        ("sub", "BLOCKED_BY_FEEDS"),
        ("sub", "FEEDS_UNAVAILABLE"),
        ("sub", "FEED"),
        ("sub", "BLOCK"),
        ("sub", "UNAVAILABLE"),
        ("sub", "NOT_DETECT"),
        ("exact", "INSUFFICIENT_EVIDENCE"),
        ("exact", "REFUSE_TO_CLASSIFY"),
        ("exact", "REVIEW_REQUIRED"),
        ("sub", "REVIEW"),
    ),
}

# Ordered action-label matchers per determinism class.
_ACTION_MATCHERS: dict[str, tuple[_Matcher, ...]] = {
    "CALIBRATED": (
        ("exact", "INSUFFICIENT_EVIDENCE"),
        ("exact", "REFUSE_TO_CLASSIFY"),
        ("exact", "REVIEW_REQUIRED"),
        ("exact", "CONTEXT_ONLY"),
        ("exact", "CONFIRMATION_REQUIRED"),
        ("exact", "DOWNGRADE_CONFIDENCE"),
        ("sub", "INSUFFICIENT"),
        ("sub", "REFUSE"),
        ("sub", "REVIEW"),
    ),
    "JUDGMENT_ASSISTED": (
        ("exact", "REVIEW_REQUIRED"),
        ("exact", "INSUFFICIENT_EVIDENCE"),
        ("exact", "REFUSE_TO_CLASSIFY"),
        ("exact", "CONFIRMATION_REQUIRED"),
        ("exact", "CONTEXT_ONLY"),
        ("sub", "REVIEW"),
        ("sub", "INSUFFICIENT"),
        ("sub", "REFUSE"),
    ),
    "CONTEXT_ONLY": (
        ("exact", "CONTEXT_ONLY"),
        ("sub", "CONTEXT"),
        ("exact", "REVIEW_REQUIRED"),
        ("exact", "OBSERVE"),
        ("sub", "REVIEW"),
        ("exact", "INSUFFICIENT_EVIDENCE"),
        ("exact", "REFUSE_TO_CLASSIFY"),
    ),
    "NOT_DETECTABLE_WITH_CURRENT_FEEDS": (
        ("exact", "BLOCKED_BY_FEEDS"),
        ("sub", "BLOCKED"),
        ("sub", "FEED"),
        ("exact", "INSUFFICIENT_EVIDENCE"),
        ("exact", "REFUSE_TO_CLASSIFY"),
        ("exact", "REVIEW_REQUIRED"),
        ("sub", "INSUFFICIENT"),
        ("sub", "REFUSE"),
    ),
}


class _Selection:
    """A chosen label plus whether a last-resort fallback was needed."""

    __slots__ = ("label", "used_fallback")

    def __init__(self, label: str, used_fallback: bool) -> None:
        self.label = label
        self.used_fallback = used_fallback


def _select(candidates: tuple[str, ...], matchers: tuple[_Matcher, ...]) -> _Selection:
    """Pick the first declared label matching the ordered matcher list."""
    for mode, pattern in matchers:
        for candidate in candidates:
            if mode == "exact" and candidate == pattern:
                return _Selection(candidate, used_fallback=False)
            if mode == "sub" and pattern in candidate:
                return _Selection(candidate, used_fallback=False)
    # Last resort: a contract always declares at least one state/action.
    return _Selection(candidates[0], used_fallback=True)


def select_safe_state(contract: DetectorContract) -> _Selection:
    return _select(
        contract.states_emitted,
        _STATE_MATCHERS.get(contract.determinism_class, ()),
    )


def select_safe_action(contract: DetectorContract, state: str) -> str:
    """Pick a safe action label, or mirror the state for a state-only contract."""
    if not contract.allowed_action_labels:
        return state
    return _select(
        contract.allowed_action_labels,
        _ACTION_MATCHERS.get(contract.determinism_class, ()),
    ).label


def _mapping_note(contract: DetectorContract, state_selection: _Selection) -> str | None:
    notes: list[str] = []
    if state_selection.used_fallback:
        notes.append(
            f"contract declares no recognized safe label; first declared label "
            f"{state_selection.label!r} used as a last resort"
        )
    if contract.is_state_only:
        notes.append("state-only contract: action_label mirrors the emitted state")
    return "; ".join(notes) if notes else None


def calibrated_refusal(contract: DetectorContract) -> dict[str, Any]:
    """CALIBRATED concept: refuse because a calibration profile is absent."""
    state_selection = select_safe_state(contract)
    state = state_selection.label
    action = select_safe_action(contract, state)
    return refusal_output(
        contract,
        state,
        action,
        route="calibrated_refusal",
        reason=(
            "CALIBRATED detector: no calibration profile or empirically derived "
            "parameter values are available. The rule structure exists but its "
            "thresholds are uncalibrated, so no calibrated classification is emitted."
        ),
        mapping_note=_mapping_note(contract, state_selection),
        confidence="CALIBRATION_ABSENT",
    )


def judgment_assisted_routing(contract: DetectorContract) -> dict[str, Any]:
    """JUDGMENT_ASSISTED concept: route to review-required, not a fake decision."""
    state_selection = select_safe_state(contract)
    state = state_selection.label
    action = select_safe_action(contract, state)
    return refusal_output(
        contract,
        state,
        action,
        route="judgment_assisted_review",
        reason=(
            "JUDGMENT_ASSISTED detector: the concept depends on structured human "
            "or LLM interpretation of context, narrative, or sequence. The runtime "
            "routes it for review and emits no autonomous classification."
        ),
        mapping_note=_mapping_note(contract, state_selection),
        confidence="REVIEW_REQUIRED",
    )


def context_only_routing(contract: DetectorContract) -> dict[str, Any]:
    """CONTEXT_ONLY concept: emit a context/governance output only."""
    state_selection = select_safe_state(contract)
    state = state_selection.label
    action = select_safe_action(contract, state)
    return context_only_output(
        contract,
        state,
        action,
        reason=(
            "CONTEXT_ONLY detector: the concept informs the market read but must "
            "not produce an actionable trigger. A context/governance label is "
            "emitted with no execution permission."
        ),
        mapping_note=_mapping_note(contract, state_selection),
    )


def not_detectable_routing(contract: DetectorContract) -> dict[str, Any]:
    """NOT_DETECTABLE_WITH_CURRENT_FEEDS concept: emit a blocked-by-feeds output."""
    state_selection = select_safe_state(contract)
    state = state_selection.label
    action = select_safe_action(contract, state)
    return blocked_by_feeds_output(
        contract,
        state,
        action,
        reason=(
            "NOT_DETECTABLE_WITH_CURRENT_FEEDS detector: the concept requires data "
            "feeds that are not available. The runtime emits a blocked-by-feeds "
            "output instead of inferring a result."
        ),
        mapping_note=_mapping_note(contract, state_selection),
    )


_CLASS_ROUTERS = {
    "CALIBRATED": calibrated_refusal,
    "JUDGMENT_ASSISTED": judgment_assisted_routing,
    "CONTEXT_ONLY": context_only_routing,
    "NOT_DETECTABLE_WITH_CURRENT_FEEDS": not_detectable_routing,
}


def route_non_computable(contract: DetectorContract) -> dict[str, Any]:
    """Route any non-computable contract to its safe class handler."""
    router = _CLASS_ROUTERS.get(contract.determinism_class)
    if router is None:
        raise ValueError(
            f"{contract.concept_id}: refusal routing called for unexpected "
            f"determinism_class {contract.determinism_class!r}"
        )
    return router(contract)
