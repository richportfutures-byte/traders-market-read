"""Tests for the TMR-P29 market snapshot input contract."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from traders_market_read.input.market_snapshot import (
    MarketSnapshotInputError,
    load_market_snapshot,
    validate_market_snapshot_payload,
)
from traders_market_read.pipeline.market_read_packet import (
    MarketReadPacketError,
    build_market_read_packet,
)

_EXAMPLES = _REPO_ROOT / "qa" / "examples"
_CALIBRATED_INPUT = _EXAMPLES / "detector_runtime_calibrated_input.example.json"
_P25_INPUT = _EXAMPLES / "detector_runtime_input.example.json"
_CALIBRATION_PROFILE = _EXAMPLES / "detector_runtime_calibrated_profile.example.yaml"
_INVALID_EXECUTION = _EXAMPLES / "market_snapshot_invalid_execution.example.json"
_MISSING_CONTEXT = _EXAMPLES / "market_snapshot_missing_context.example.json"
_MANIFEST = _REPO_ROOT / "qa" / "input_requirements_manifest.csv"


class MarketSnapshotInputContractTests(unittest.TestCase):
    def test_valid_calibrated_fixture_passes_validation(self) -> None:
        snapshot = load_market_snapshot(_CALIBRATED_INPUT)
        self.assertEqual(snapshot.source_shape, "legacy_runtime_fixture")
        self.assertIn("ch02_acceptance_vs_rejection", snapshot.detector_inputs)

    def test_valid_p25_fixture_passes_validation(self) -> None:
        snapshot = load_market_snapshot(_P25_INPUT)
        self.assertEqual(snapshot.source_shape, "legacy_runtime_fixture")
        self.assertIn("session_clock", snapshot.runtime_market_context)

    def test_invalid_execution_field_fixture_fails_validation(self) -> None:
        with self.assertRaises(MarketSnapshotInputError) as ctx:
            load_market_snapshot(_INVALID_EXECUTION)
        self.assertIn("forbidden execution field", str(ctx.exception))

    def test_missing_market_context_fixture_fails_validation(self) -> None:
        with self.assertRaises(MarketSnapshotInputError) as ctx:
            load_market_snapshot(_MISSING_CONTEXT)
        self.assertIn("missing required top-level field: market_context", str(ctx.exception))

    def test_malformed_json_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "bad.json"
            bad.write_text("{bad json", encoding="utf-8")
            with self.assertRaises(MarketSnapshotInputError):
                load_market_snapshot(bad)

    def test_unknown_detector_input_key_fails_validation(self) -> None:
        payload = {
            "schema_version": 1,
            "market_context": {
                "instrument": "ES",
                "session": "synthetic_rth",
                "timeframe": "intraday_fixture",
                "data_window": "unit_test",
            },
            "detector_inputs": {"not_a_known_detector_or_shared_block": {}},
        }
        with self.assertRaises(MarketSnapshotInputError) as ctx:
            validate_market_snapshot_payload(payload)
        self.assertIn("unknown key", str(ctx.exception))

    def test_runtime_cli_rejects_invalid_execution_input_before_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "runtime.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_detector_runtime.py",
                    str(_INVALID_EXECUTION),
                    "--output",
                    str(output),
                ],
                cwd=_REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("forbidden execution field", result.stdout)
            self.assertFalse(output.exists())

    def test_packet_pipeline_rejects_invalid_execution_input_before_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime = Path(temp_dir) / "runtime.json"
            summary = Path(temp_dir) / "summary.json"
            review = Path(temp_dir) / "review.md"
            with self.assertRaises(MarketReadPacketError):
                build_market_read_packet(
                    _INVALID_EXECUTION,
                    runtime_output_path=runtime,
                    summary_json_path=summary,
                    review_markdown_path=review,
                )
            self.assertFalse(runtime.exists())
            self.assertFalse(summary.exists())
            self.assertFalse(review.exists())

    def test_validation_does_not_require_every_detector_block(self) -> None:
        payload = {
            "schema_version": 1,
            "market_context": {
                "instrument": "ES",
                "session": "synthetic_rth",
                "timeframe": "intraday_fixture",
                "data_window": "unit_test",
            },
            "detector_inputs": {},
        }
        snapshot = validate_market_snapshot_payload(payload)
        self.assertEqual(snapshot.detector_inputs, {})

    def test_existing_packet_pipeline_still_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime = Path(temp_dir) / "runtime.json"
            summary = Path(temp_dir) / "summary.json"
            review = Path(temp_dir) / "review.md"
            result = build_market_read_packet(
                _CALIBRATED_INPUT,
                calibration_profile_path=_CALIBRATION_PROFILE,
                runtime_output_path=runtime,
                summary_json_path=summary,
                review_markdown_path=review,
            )
            self.assertEqual(result.total_outputs, 110)
            self.assertEqual(result.calibrated_non_refusal_count, 27)

    def test_manifest_exists_and_contains_computable_and_calibrated_rows(self) -> None:
        self.assertTrue(_MANIFEST.exists())
        with _MANIFEST.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        classes = {row["determinism_class"] for row in rows}
        self.assertIn("COMPUTABLE", classes)
        self.assertIn("CALIBRATED", classes)
        self.assertIn("required_fixture_fields", rows[0])

    def test_validation_path_does_not_create_execution_behavior(self) -> None:
        schema = (_REPO_ROOT / "spec" / "market_snapshot_input_schema.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("no_detector_logic_in_schema: true", schema)
        self.assertIn("no_calibration_values_in_schema: true", schema)
        self.assertIn("no_trade_permission", schema)
        self.assertIn("no_broker_order_account_fill_pnl_fields", schema)


if __name__ == "__main__":
    unittest.main()
