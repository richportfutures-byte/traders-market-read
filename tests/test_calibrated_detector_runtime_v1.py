"""Behavioural tests for the TMR-P26 calibrated detector runtime.

Run with:  python3 -m unittest tests/test_calibrated_detector_runtime_v1.py
"""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent
for _path in (_REPO_ROOT / "src", _REPO_ROOT / "scripts"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from traders_market_read.detectors.calibrated import CALIBRATED_DETECTORS
from traders_market_read.detectors.calibration import (
    CalibrationError,
    CalibrationProfile,
    load_calibration_profile,
)
from traders_market_read.detectors.catalog import load_catalog
from traders_market_read.detectors.output import (
    FORBIDDEN_FIELDS,
    GUARDRAILS,
    find_forbidden_fields,
)
from traders_market_read.detectors.runtime import run

import validate_detector_output as external_validator

_EXAMPLES = _REPO_ROOT / "qa" / "examples"
_CALIBRATED_INPUT = _EXAMPLES / "detector_runtime_calibrated_input.example.json"
_CALIBRATION_PROFILE = _EXAMPLES / "detector_runtime_calibrated_profile.example.yaml"
_P25_INPUT = _EXAMPLES / "detector_runtime_input.example.json"


def _load_market_context(path: Path) -> dict:
    document = json.loads(path.read_text(encoding="utf-8"))
    if "market_context" in document:
        return document["market_context"]
    return document


# ---- Test 1: Calibration profile loads ----

class CalibrationProfileLoadTests(unittest.TestCase):
    """Test 1: the calibration profile loads successfully."""

    def test_profile_loads(self) -> None:
        profile = load_calibration_profile(_CALIBRATION_PROFILE)
        self.assertIsInstance(profile, CalibrationProfile)
        self.assertTrue(len(profile.concept_ids()) > 0)
        self.assertEqual(
            profile.profile_id,
            "detector_runtime_calibrated_profile_example_v1",
        )

    def test_profile_covers_all_implemented_detectors(self) -> None:
        profile = load_calibration_profile(_CALIBRATION_PROFILE)
        for concept_id, spec in CALIBRATED_DETECTORS.items():
            for param_name in spec.parameter_names:
                try:
                    profile.get(concept_id, param_name)
                except CalibrationError:
                    self.fail(
                        f"profile is missing {concept_id}/{param_name}"
                    )


# ---- Test 2: Malformed profile fails closed ----

class MalformedProfileTests(unittest.TestCase):
    """Test 2: malformed profiles fail closed."""

    def test_missing_file_fails(self) -> None:
        with self.assertRaises(CalibrationError):
            load_calibration_profile("/does/not/exist.yaml")

    def test_non_mapping_yaml_fails(self) -> None:
        tmp = _REPO_ROOT / "tests" / "_tmp_bad_profile.yaml"
        try:
            tmp.write_text("- just a list\n", encoding="utf-8")
            with self.assertRaises(CalibrationError):
                load_calibration_profile(tmp)
        finally:
            tmp.unlink(missing_ok=True)

    def test_malformed_yaml_fails(self) -> None:
        tmp = _REPO_ROOT / "tests" / "_tmp_bad_yaml.yaml"
        try:
            tmp.write_text("key: [unclosed\n", encoding="utf-8")
            with self.assertRaises(CalibrationError):
                load_calibration_profile(tmp)
        finally:
            tmp.unlink(missing_ok=True)

    def test_missing_parameter_values_fails(self) -> None:
        tmp = _REPO_ROOT / "tests" / "_tmp_no_params.yaml"
        try:
            data = yaml.safe_load(_CALIBRATION_PROFILE.read_text(encoding="utf-8"))
            del data["parameter_values"]
            tmp.write_text(yaml.dump(data), encoding="utf-8")
            with self.assertRaises(CalibrationError):
                load_calibration_profile(tmp)
        finally:
            tmp.unlink(missing_ok=True)


# ---- Test 3: Duplicate concept/parameter entries fail closed ----

class DuplicateParameterTests(unittest.TestCase):
    """Test 3: duplicate concept/parameter profile entries fail closed."""

    def test_duplicate_entry_fails(self) -> None:
        tmp = _REPO_ROOT / "tests" / "_tmp_dup.yaml"
        try:
            data = yaml.safe_load(_CALIBRATION_PROFILE.read_text(encoding="utf-8"))
            first = data["parameter_values"][0]
            data["parameter_values"].append(dict(first))
            tmp.write_text(yaml.dump(data), encoding="utf-8")
            with self.assertRaises(CalibrationError) as ctx:
                load_calibration_profile(tmp)
            self.assertIn("duplicate", str(ctx.exception).lower())
        finally:
            tmp.unlink(missing_ok=True)


# ---- Test 4: Forbidden execution fields in profile fail closed ----

class ForbiddenFieldsProfileTests(unittest.TestCase):
    """Test 4: calibration profile containing forbidden execution fields fails."""

    def test_forbidden_field_in_profile_fails(self) -> None:
        tmp = _REPO_ROOT / "tests" / "_tmp_forbidden.yaml"
        try:
            data = yaml.safe_load(_CALIBRATION_PROFILE.read_text(encoding="utf-8"))
            data["entry_price"] = 5000.0
            tmp.write_text(yaml.dump(data), encoding="utf-8")
            with self.assertRaises(CalibrationError) as ctx:
                load_calibration_profile(tmp)
            self.assertIn("forbidden", str(ctx.exception).lower())
        finally:
            tmp.unlink(missing_ok=True)

    def test_forbidden_field_nested_in_profile_fails(self) -> None:
        tmp = _REPO_ROOT / "tests" / "_tmp_forbidden2.yaml"
        try:
            data = yaml.safe_load(_CALIBRATION_PROFILE.read_text(encoding="utf-8"))
            data["parameter_values"][0]["stop_price"] = 4990.0
            tmp.write_text(yaml.dump(data), encoding="utf-8")
            with self.assertRaises(CalibrationError) as ctx:
                load_calibration_profile(tmp)
            self.assertIn("forbidden", str(ctx.exception).lower())
        finally:
            tmp.unlink(missing_ok=True)


# ---- Test 5: Runtime without calibration profile refuses CALIBRATED ----

class NoCalibratedProfileTests(unittest.TestCase):
    """Test 5: runtime without calibration profile refuses CALIBRATED contracts."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog()
        cls.market_context = _load_market_context(_CALIBRATED_INPUT)
        cls.report = run(cls.market_context, catalog=cls.catalog)

    def test_calibrated_all_refused(self) -> None:
        self.assertEqual(self.report.summary["calibrated_implemented"], 0)
        self.assertEqual(self.report.summary["calibrated_refused"], 27)

    def test_calibrated_outputs_are_refusal_route(self) -> None:
        calibrated_concepts = {
            c.concept_id for c in self.catalog if c.determinism_class == "CALIBRATED"
        }
        for output in self.report.outputs:
            if output["concept_id"] in calibrated_concepts:
                self.assertEqual(
                    output["evidence"]["route"],
                    "calibrated_refusal",
                    msg=output["concept_id"],
                )
                self.assertTrue(output["evidence"].get("refusal"))


# ---- Test 6: Runtime with example profile runs all CALIBRATED detectors ----

class CalibratedWithProfileTests(unittest.TestCase):
    """Test 6: runtime with example profile runs all feasible CALIBRATED detectors."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog()
        cls.market_context = _load_market_context(_CALIBRATED_INPUT)
        cls.profile = load_calibration_profile(_CALIBRATION_PROFILE)
        cls.report = run(
            cls.market_context,
            catalog=cls.catalog,
            calibration_profile=cls.profile,
        )
        cls.outputs = cls.report.outputs
        cls.by_concept = {o["concept_id"]: o for o in cls.outputs}
        cls.external_catalog = external_validator.load_catalog()

    def test_all_calibrated_implemented(self) -> None:
        self.assertEqual(self.report.summary["calibrated_implemented"], 27)
        self.assertEqual(self.report.summary["calibrated_refused"], 0)

    def test_calibrated_outputs_have_route_calibrated(self) -> None:
        calibrated_concepts = {
            c.concept_id
            for c in self.catalog
            if c.determinism_class == "CALIBRATED"
        }
        for cid in calibrated_concepts:
            output = self.by_concept[cid]
            self.assertEqual(
                output["evidence"]["route"],
                "calibrated",
                msg=f"{cid}: expected route=calibrated, got {output['evidence']['route']}",
            )
            self.assertIn("measurements", output["evidence"])
            self.assertIn("calibration_parameters_used", output["evidence"])

    # ---- Test 7: Implemented calibrated outputs validate ----

    def test_calibrated_outputs_validate_internal(self) -> None:
        """Test 7a: runtime self-validation passes."""
        self.assertTrue(
            self.report.ok,
            msg=f"validation errors: {self.report.validation_errors}",
        )

    def test_calibrated_outputs_validate_external(self) -> None:
        """Test 7b: external validator passes for all outputs."""
        for output in self.outputs:
            errors = external_validator.validate_output(output, self.external_catalog)
            self.assertEqual(
                errors, [], msg=f"{output['concept_id']}: {errors}"
            )


# ---- Test 8: Missing calibrated fixture fields produce refusal ----

class MissingFixtureFieldTests(unittest.TestCase):
    """Test 8: missing calibrated fixture fields produce refusal."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog()
        cls.profile = load_calibration_profile(_CALIBRATION_PROFILE)
        # Use the P25 input which has no calibrated fixture blocks.
        cls.market_context_no_blocks = _load_market_context(_P25_INPUT)
        cls.report = run(
            cls.market_context_no_blocks,
            catalog=cls.catalog,
            calibration_profile=cls.profile,
        )

    def test_calibrated_all_refused_on_missing_blocks(self) -> None:
        """When fixture blocks are absent, all CALIBRATED contracts refuse safely."""
        self.assertEqual(self.report.summary["calibrated_implemented"], 0)
        self.assertEqual(self.report.summary["calibrated_refused"], 27)

    def test_partial_fixture_produces_refusal(self) -> None:
        """Removing a required field from one block produces calibrated_refusal."""
        market = copy.deepcopy(_load_market_context(_CALIBRATED_INPUT))
        # Remove structural_level from acceptance_vs_rejection.
        del market["ch02_acceptance_vs_rejection"]["structural_level"]
        report = run(
            market, catalog=self.catalog, calibration_profile=self.profile
        )
        target = next(
            o for o in report.outputs
            if o["concept_id"] == "ch02_acceptance_vs_rejection"
        )
        self.assertEqual(target["evidence"]["route"], "calibrated_refusal")
        self.assertTrue(target["evidence"].get("refusal"))


# ---- Test 9: Infeasible/unimplemented remain safe refusals ----

class InfeasibleCalibratedTests(unittest.TestCase):
    """Test 9: any infeasible/unimplemented CALIBRATED contracts remain safe."""

    def test_no_infeasible_remain(self) -> None:
        """All 27 CALIBRATED contracts are implemented in this pass."""
        catalog = load_catalog()
        calibrated_ids = {
            c.concept_id
            for c in catalog
            if c.determinism_class == "CALIBRATED"
        }
        self.assertEqual(len(calibrated_ids), 27)
        self.assertEqual(set(CALIBRATED_DETECTORS.keys()), calibrated_ids)


# ---- Test 10: COMPUTABLE behavior still works with calibration ----

class ComputableWithCalibrationTests(unittest.TestCase):
    """Test 10: COMPUTABLE behaviour still works when calibration profile is present."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog()
        cls.profile = load_calibration_profile(_CALIBRATION_PROFILE)
        cls.market_context = _load_market_context(_CALIBRATED_INPUT)
        cls.report = run(
            cls.market_context,
            catalog=cls.catalog,
            calibration_profile=cls.profile,
        )

    def test_computable_count_unchanged(self) -> None:
        self.assertEqual(self.report.summary["computable_implemented"], 9)

    def test_computable_outputs_are_computable_route(self) -> None:
        computable_concepts = {
            c.concept_id
            for c in self.catalog
            if c.determinism_class == "COMPUTABLE"
        }
        for output in self.report.outputs:
            if output["concept_id"] in computable_concepts:
                route = output["evidence"]["route"]
                self.assertIn(
                    route,
                    ("computable", "computable_refusal"),
                    msg=output["concept_id"],
                )


# ---- Test 11: JUDGMENT_ASSISTED, CONTEXT_ONLY, NOT_DETECTABLE remain safe ----

class OtherClassesTests(unittest.TestCase):
    """Test 11: JUDGMENT_ASSISTED, CONTEXT_ONLY, NOT_DETECTABLE remain safely routed."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog()
        cls.profile = load_calibration_profile(_CALIBRATION_PROFILE)
        cls.report = run(
            _load_market_context(_CALIBRATED_INPUT),
            catalog=cls.catalog,
            calibration_profile=cls.profile,
        )

    def test_judgment_assisted_count(self) -> None:
        self.assertEqual(self.report.summary["judgment_assisted_routed"], 64)

    def test_context_only_count(self) -> None:
        self.assertEqual(self.report.summary["context_only_routed"], 7)

    def test_not_detectable_count(self) -> None:
        self.assertEqual(self.report.summary["not_detectable_blocked"], 3)

    def test_routes_are_correct(self) -> None:
        expected_routes = {
            "JUDGMENT_ASSISTED": "judgment_assisted_review",
            "CONTEXT_ONLY": "context_only",
            "NOT_DETECTABLE_WITH_CURRENT_FEEDS": "not_detectable_blocked",
        }
        for output in self.report.outputs:
            route = output["evidence"]["route"]
            cid = output["concept_id"]
            contract = self.catalog.get(cid)
            dc = contract.determinism_class
            if dc in expected_routes:
                self.assertEqual(
                    route,
                    expected_routes[dc],
                    msg=f"{cid}: expected {expected_routes[dc]}, got {route}",
                )


# ---- Test 12: No forbidden execution fields recursively ----

class ForbiddenFieldsOutputTests(unittest.TestCase):
    """Test 12: no output contains forbidden execution fields recursively."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog()
        cls.profile = load_calibration_profile(_CALIBRATION_PROFILE)
        cls.report = run(
            _load_market_context(_CALIBRATED_INPUT),
            catalog=cls.catalog,
            calibration_profile=cls.profile,
        )

    def test_no_forbidden_fields(self) -> None:
        for output in self.report.outputs:
            found = find_forbidden_fields(output)
            self.assertEqual(found, [], msg=f"{output['concept_id']}: {found}")


# ---- Test 13: Guardrail booleans always true ----

class GuardrailBooleansTests(unittest.TestCase):
    """Test 13: guardrail booleans are always true for all outputs."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog()
        cls.profile = load_calibration_profile(_CALIBRATION_PROFILE)
        cls.report = run(
            _load_market_context(_CALIBRATED_INPUT),
            catalog=cls.catalog,
            calibration_profile=cls.profile,
        )

    def test_guardrails_present_and_true(self) -> None:
        required_guardrails = {
            "non_executional",
            "no_trade_permission",
            "no_order_instructions",
            "no_position_sizing",
            "no_broker_or_account_fields",
        }
        for output in self.report.outputs:
            guardrails = output["guardrails"]
            self.assertIsInstance(guardrails, dict)
            self.assertTrue(required_guardrails.issubset(guardrails))
            for name, value in guardrails.items():
                self.assertIs(
                    value, True,
                    msg=f"{output['concept_id']}.guardrails.{name} is not True",
                )
            for name, expected in GUARDRAILS.items():
                self.assertIs(guardrails.get(name), expected)


# ---- Test 14: Run-all mode still emits one output per catalog contract ----

class RunAllCountTests(unittest.TestCase):
    """Test 14: run-all mode still emits one output per catalog contract."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog()
        cls.profile = load_calibration_profile(_CALIBRATION_PROFILE)
        cls.report = run(
            _load_market_context(_CALIBRATED_INPUT),
            catalog=cls.catalog,
            calibration_profile=cls.profile,
        )

    def test_output_count_equals_110(self) -> None:
        self.assertEqual(len(self.report.outputs), 110)
        self.assertEqual(self.report.summary["outputs_generated"], 110)

    def test_one_per_contract(self) -> None:
        emitted = [o["concept_id"] for o in self.report.outputs]
        self.assertEqual(emitted, self.catalog.concept_ids)
        self.assertEqual(len(emitted), len(set(emitted)))


# ---- Test 15: --concept-id works for at least one CALIBRATED detector ----

class ConceptIdFilterTests(unittest.TestCase):
    """Test 15: --concept-id works for at least one implemented CALIBRATED detector."""

    def test_single_concept_id(self) -> None:
        catalog = load_catalog()
        profile = load_calibration_profile(_CALIBRATION_PROFILE)
        market_context = _load_market_context(_CALIBRATED_INPUT)
        report = run(
            market_context,
            catalog=catalog,
            concept_id="ch02_acceptance_vs_rejection",
            calibration_profile=profile,
        )
        self.assertEqual(len(report.outputs), 1)
        self.assertEqual(report.outputs[0]["concept_id"], "ch02_acceptance_vs_rejection")
        self.assertEqual(report.outputs[0]["evidence"]["route"], "calibrated")
        self.assertIn("measurements", report.outputs[0]["evidence"])
        self.assertEqual(report.summary["calibrated_implemented"], 1)

    def test_single_concept_id_without_profile(self) -> None:
        catalog = load_catalog()
        market_context = _load_market_context(_CALIBRATED_INPUT)
        report = run(
            market_context,
            catalog=catalog,
            concept_id="ch02_acceptance_vs_rejection",
        )
        self.assertEqual(len(report.outputs), 1)
        self.assertEqual(
            report.outputs[0]["evidence"]["route"], "calibrated_refusal"
        )


if __name__ == "__main__":
    unittest.main()
