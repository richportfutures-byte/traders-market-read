"""Behavioural tests for the TMR-P25 safe detector runtime.

Run with:  python3 -m unittest tests/test_detector_runtime_v1.py
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
for _path in (_REPO_ROOT / "src", _REPO_ROOT / "scripts"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from traders_market_read.detectors.catalog import CatalogError, load_catalog
from traders_market_read.detectors.computable import COMPUTABLE_DETECTORS
from traders_market_read.detectors.output import (
    FORBIDDEN_FIELDS,
    GUARDRAILS,
    find_forbidden_fields,
)
from traders_market_read.detectors.runtime import run

# The external validator, reused to prove parity with the runtime's own checks.
import validate_detector_output as external_validator

_EXAMPLES = _REPO_ROOT / "qa" / "examples"
_INPUT_FIXTURE = _EXAMPLES / "detector_runtime_input.example.json"
_MISSING_FIXTURE = _EXAMPLES / "detector_runtime_missing_inputs.example.json"

_REFUSAL_STATES = {"REFUSE_TO_CLASSIFY", "INSUFFICIENT_EVIDENCE"}
_NON_COMPUTABLE_ROUTES = {
    "calibrated_refusal",
    "judgment_assisted_review",
    "context_only",
    "not_detectable_blocked",
}


def _load_market_context(path: Path) -> dict:
    document = json.loads(path.read_text(encoding="utf-8"))
    return document["market_context"]


class CatalogLoadTests(unittest.TestCase):
    """Test 1: the catalog loads."""

    def test_catalog_loads(self) -> None:
        catalog = load_catalog()
        self.assertEqual(len(catalog), 110)
        self.assertEqual(len(catalog.concept_ids), len(set(catalog.concept_ids)))

    def test_catalog_is_fail_closed(self) -> None:
        with self.assertRaises(CatalogError):
            load_catalog(_REPO_ROOT / "spec" / "does_not_exist.json")


class RunAllTests(unittest.TestCase):
    """Tests 2-4, 8-9 against the complete-input fixture."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog()
        cls.market_context = _load_market_context(_INPUT_FIXTURE)
        cls.report = run(cls.market_context, catalog=cls.catalog)
        cls.outputs = cls.report.outputs
        cls.external_catalog = external_validator.load_catalog()

    def test_one_output_per_contract(self) -> None:
        """Test 2: run-all mode emits exactly one output per contract."""
        emitted = [output["concept_id"] for output in self.outputs]
        self.assertEqual(emitted, self.catalog.concept_ids)
        self.assertEqual(len(emitted), len(set(emitted)))

    def test_output_count_equals_catalog_count(self) -> None:
        """Test 3: output count equals catalog count."""
        self.assertEqual(len(self.outputs), len(self.catalog))
        self.assertEqual(self.report.summary["outputs_generated"], 110)
        self.assertEqual(self.report.summary["total_contracts"], 110)

    def test_every_output_validates(self) -> None:
        """Test 4: every output validates (runtime self-check and external script)."""
        self.assertTrue(self.report.ok, msg=str(self.report.validation_errors))
        self.assertEqual(self.report.validation_errors, [])
        for output in self.outputs:
            errors = external_validator.validate_output(output, self.external_catalog)
            self.assertEqual(errors, [], msg=f"{output['concept_id']}: {errors}")

    def test_no_forbidden_execution_fields(self) -> None:
        """Test 8: no output carries a forbidden execution field, recursively."""
        for output in self.outputs:
            found = find_forbidden_fields(output)
            self.assertEqual(found, [], msg=f"{output['concept_id']}: {found}")
        # The forbidden set must cover the mission's required fields.
        for required in (
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
        ):
            self.assertIn(required, FORBIDDEN_FIELDS)

    def test_guardrail_booleans_always_true(self) -> None:
        """Test 9: guardrail booleans are always present and true."""
        required_guardrails = {
            "non_executional",
            "no_trade_permission",
            "no_order_instructions",
            "no_position_sizing",
            "no_broker_or_account_fields",
        }
        for output in self.outputs:
            guardrails = output["guardrails"]
            self.assertIsInstance(guardrails, dict)
            self.assertTrue(required_guardrails.issubset(guardrails))
            for name, value in guardrails.items():
                self.assertIs(value, True, msg=f"{output['concept_id']}.{name}")
            for name, expected in GUARDRAILS.items():
                self.assertIs(guardrails.get(name), expected)


class ComputableTests(unittest.TestCase):
    """Tests 5-6: COMPUTABLE detector behaviour."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog()
        cls.computable_ids = set(COMPUTABLE_DETECTORS)
        cls.complete = {
            output["concept_id"]: output
            for output in run(
                _load_market_context(_INPUT_FIXTURE), catalog=cls.catalog
            ).outputs
        }
        cls.missing = {
            output["concept_id"]: output
            for output in run(
                _load_market_context(_MISSING_FIXTURE), catalog=cls.catalog
            ).outputs
        }

    def test_all_catalog_computables_are_implemented(self) -> None:
        catalog_computables = {
            contract.concept_id
            for contract in self.catalog
            if contract.determinism_class == "COMPUTABLE"
        }
        self.assertEqual(catalog_computables, self.computable_ids)

    def test_complete_inputs_produce_non_refusal_outputs(self) -> None:
        """Test 5: COMPUTABLE detectors produce non-refusal outputs when data is complete."""
        for concept_id in self.computable_ids:
            output = self.complete[concept_id]
            self.assertNotIn(
                output["state"],
                _REFUSAL_STATES,
                msg=f"{concept_id} refused on complete fixture: {output['state']}",
            )
            self.assertEqual(output["evidence"]["route"], "computable")
            self.assertIn("measurements", output["evidence"])

    def test_missing_inputs_produce_refusal_outputs(self) -> None:
        """Test 6: missing COMPUTABLE inputs produce refusal outputs."""
        for concept_id in self.computable_ids:
            output = self.missing[concept_id]
            self.assertIn(
                output["state"],
                _REFUSAL_STATES,
                msg=f"{concept_id} did not refuse on missing-input fixture: {output['state']}",
            )
            self.assertEqual(output["evidence"]["route"], "computable_refusal")
            self.assertTrue(output["evidence"].get("refusal"))


class NonComputableTests(unittest.TestCase):
    """Test 7: non-computable concepts do not emit detector claims."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog()
        cls.outputs = {
            output["concept_id"]: output
            for output in run(
                _load_market_context(_INPUT_FIXTURE), catalog=cls.catalog
            ).outputs
        }

    def test_non_computable_outputs_are_refusal_or_context_only(self) -> None:
        for contract in self.catalog:
            if contract.determinism_class == "COMPUTABLE":
                continue
            output = self.outputs[contract.concept_id]
            route = output["evidence"]["route"]
            self.assertIn(
                route,
                _NON_COMPUTABLE_ROUTES,
                msg=f"{contract.concept_id} used route {route}",
            )
            # A non-computable output never carries a computed structural claim.
            self.assertNotIn("measurements", output["evidence"])
            self.assertIn(output["state"], contract.states_emitted)
            self.assertIn(output["action_label"], contract.effective_action_labels)

    def test_class_routing_counts(self) -> None:
        report = run(_load_market_context(_INPUT_FIXTURE), catalog=self.catalog)
        summary = report.summary
        self.assertEqual(summary["calibrated_refused"], 27)
        self.assertEqual(summary["judgment_assisted_routed"], 64)
        self.assertEqual(summary["context_only_routed"], 7)
        self.assertEqual(summary["not_detectable_blocked"], 3)
        self.assertEqual(summary["computable_implemented"], 9)


if __name__ == "__main__":
    unittest.main()
