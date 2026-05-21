"""Detector contract catalog loading and lookup.

The catalog (``spec/detector_contract_catalog.json``) is the single source of
truth for which detectors exist and what each one is contractually allowed to
emit. This module loads it fail-closed: any structural problem raises
``CatalogError`` rather than producing a partial catalog.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

# Repo root is four parents up: detectors/ -> traders_market_read/ -> src/ -> root.
_REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CATALOG_PATH = _REPO_ROOT / "spec" / "detector_contract_catalog.json"

DETERMINISM_CLASSES = frozenset(
    {
        "COMPUTABLE",
        "CALIBRATED",
        "JUDGMENT_ASSISTED",
        "CONTEXT_ONLY",
        "NOT_DETECTABLE_WITH_CURRENT_FEEDS",
    }
)

# Fields a detector record must carry for the runtime to route and bound it.
_REQUIRED_DETECTOR_FIELDS = (
    "concept_id",
    "determinism_class",
    "states_emitted",
    "allowed_action_labels",
)


class CatalogError(RuntimeError):
    """Raised when the detector contract catalog cannot be trusted."""


class DetectorContract:
    """One detector contract, normalized from a catalog record."""

    __slots__ = (
        "concept_id",
        "determinism_class",
        "display_name",
        "chapter",
        "states_emitted",
        "allowed_action_labels",
        "required_inputs",
        "optional_inputs",
        "raw",
    )

    def __init__(self, record: dict[str, Any]) -> None:
        self.concept_id: str = record["concept_id"]
        self.determinism_class: str = record["determinism_class"]
        self.display_name: str = str(record.get("display_name") or self.concept_id)
        self.chapter: str = str(record.get("chapter") or "")
        self.states_emitted: tuple[str, ...] = tuple(record["states_emitted"])
        self.allowed_action_labels: tuple[str, ...] = tuple(record["allowed_action_labels"])
        self.required_inputs: tuple[Any, ...] = tuple(record.get("required_inputs") or ())
        self.optional_inputs: tuple[Any, ...] = tuple(record.get("optional_inputs") or ())
        self.raw: dict[str, Any] = record

    @property
    def is_computable(self) -> bool:
        return self.determinism_class == "COMPUTABLE"

    @property
    def is_state_only(self) -> bool:
        """True when the contract declares no separate action vocabulary."""
        return not self.allowed_action_labels

    @property
    def effective_action_labels(self) -> tuple[str, ...]:
        """Action labels usable by an output.

        State-only contracts carry no action vocabulary; their action label
        mirrors a valid emitted state.
        """
        return self.allowed_action_labels or self.states_emitted

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only.
        return f"DetectorContract({self.concept_id!r}, {self.determinism_class!r})"


class DetectorCatalog:
    """An ordered, validated collection of detector contracts."""

    def __init__(self, contracts: list[DetectorContract], source_path: Path) -> None:
        self._contracts = contracts
        self._by_id = {contract.concept_id: contract for contract in contracts}
        self.source_path = source_path

    def __len__(self) -> int:
        return len(self._contracts)

    def __iter__(self) -> Iterator[DetectorContract]:
        return iter(self._contracts)

    def __contains__(self, concept_id: object) -> bool:
        return concept_id in self._by_id

    @property
    def contracts(self) -> list[DetectorContract]:
        return list(self._contracts)

    @property
    def concept_ids(self) -> list[str]:
        return [contract.concept_id for contract in self._contracts]

    def get(self, concept_id: str) -> DetectorContract:
        """Return one contract by concept_id, fail-closed when unknown."""
        try:
            return self._by_id[concept_id]
        except KeyError:
            raise CatalogError(f"unknown concept_id: {concept_id}") from None

    def by_determinism_class(self) -> dict[str, list[DetectorContract]]:
        """Group contracts by determinism class, preserving catalog order."""
        grouped: dict[str, list[DetectorContract]] = {}
        for contract in self._contracts:
            grouped.setdefault(contract.determinism_class, []).append(contract)
        return grouped


def _read_json(path: Path) -> Any:
    if not path.exists():
        raise CatalogError(f"detector contract catalog not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CatalogError(f"detector contract catalog is not valid JSON: {exc}") from exc
    except OSError as exc:
        raise CatalogError(f"could not read detector contract catalog {path}: {exc}") from exc


def _validate_record(record: Any, index: int) -> None:
    if not isinstance(record, dict):
        raise CatalogError(f"detectors[{index}] must be a JSON object")
    for field in _REQUIRED_DETECTOR_FIELDS:
        if field not in record:
            raise CatalogError(f"detectors[{index}] missing required field: {field}")
    concept_id = record["concept_id"]
    if not isinstance(concept_id, str) or not concept_id:
        raise CatalogError(f"detectors[{index}] concept_id must be a non-empty string")
    determinism_class = record["determinism_class"]
    if determinism_class not in DETERMINISM_CLASSES:
        raise CatalogError(
            f"detectors[{index}] ({concept_id}) has unknown determinism_class: {determinism_class!r}"
        )
    states = record["states_emitted"]
    if not isinstance(states, list) or not states:
        raise CatalogError(
            f"detectors[{index}] ({concept_id}) states_emitted must be a non-empty list"
        )
    if not all(isinstance(state, str) and state for state in states):
        raise CatalogError(
            f"detectors[{index}] ({concept_id}) states_emitted must contain non-empty strings"
        )
    actions = record["allowed_action_labels"]
    if not isinstance(actions, list):
        raise CatalogError(
            f"detectors[{index}] ({concept_id}) allowed_action_labels must be a list"
        )
    if not all(isinstance(action, str) and action for action in actions):
        raise CatalogError(
            f"detectors[{index}] ({concept_id}) allowed_action_labels must contain non-empty strings"
        )


def load_catalog(path: str | Path | None = None) -> DetectorCatalog:
    """Load and fail-closed validate the detector contract catalog.

    Raises ``CatalogError`` on a missing file, malformed JSON, a missing
    ``detectors`` array, a malformed detector record, a duplicate concept_id,
    a missing required field, or an unknown determinism class.
    """
    catalog_path = Path(path) if path is not None else DEFAULT_CATALOG_PATH
    data = _read_json(catalog_path)

    if not isinstance(data, dict):
        raise CatalogError(f"{catalog_path} must parse to a JSON object")
    detectors = data.get("detectors")
    if not isinstance(detectors, list):
        raise CatalogError(f"{catalog_path} is missing a 'detectors' array")
    if not detectors:
        raise CatalogError(f"{catalog_path} contains no detectors")

    contracts: list[DetectorContract] = []
    seen: set[str] = set()
    for index, record in enumerate(detectors):
        _validate_record(record, index)
        concept_id = record["concept_id"]
        if concept_id in seen:
            raise CatalogError(f"duplicate concept_id in catalog: {concept_id}")
        seen.add(concept_id)
        contracts.append(DetectorContract(record))

    return DetectorCatalog(contracts, catalog_path)
