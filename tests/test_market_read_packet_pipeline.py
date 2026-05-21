"""Tests for the TMR-P28 one-command market-read packet pipeline."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from traders_market_read.detectors.output import find_forbidden_fields
from traders_market_read.pipeline.market_read_packet import (
    MarketReadPacketError,
    build_market_read_packet,
)

_EXAMPLES = _REPO_ROOT / "qa" / "examples"
_CALIBRATED_INPUT = _EXAMPLES / "detector_runtime_calibrated_input.example.json"
_CALIBRATION_PROFILE = _EXAMPLES / "detector_runtime_calibrated_profile.example.yaml"

_FORBIDDEN_MARKDOWN_FIELD_MARKERS = (
    "entry_price",
    "stop_price",
    "target_price",
    "order_type",
    "position_size",
    "account_id",
    "fill_price",
    "buy_now",
    "sell_now",
    "place_order",
    "reduce_position",
    "add_position",
)


class _FakeRuntimeReport:
    ok = True
    validation_errors: list[str] = []
    outputs = [
        {
            "schema_version": 1,
            "concept_id": "ch01_confirmation_and_invalidation_discipline",
            "state": "NOT_ALLOWED",
            "action_label": "REVIEW_REQUIRED",
            "evidence": {"route": "judgment_assisted_review", "refusal": True},
            "confidence": "REVIEW_REQUIRED",
            "guardrails": {
                "no_trade_permission": True,
                "no_execution_fields": True,
                "no_broker_order_account_fields": True,
                "catalog_state_action_checked": True,
                "non_executional": True,
                "no_order_instructions": True,
                "no_position_sizing": True,
                "no_broker_or_account_fields": True,
            },
        }
    ]


def _paths(temp_dir: str) -> tuple[Path, Path, Path]:
    root = Path(temp_dir)
    return root / "runtime.json", root / "summary.json", root / "review.md"


class MarketReadPacketPipelineTests(unittest.TestCase):
    def test_pipeline_generates_runtime_summary_and_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_path, summary_path, review_path = _paths(temp_dir)
            result = build_market_read_packet(
                _CALIBRATED_INPUT,
                calibration_profile_path=_CALIBRATION_PROFILE,
                runtime_output_path=runtime_path,
                summary_json_path=summary_path,
                review_markdown_path=review_path,
            )
            self.assertTrue(runtime_path.exists())
            self.assertTrue(summary_path.exists())
            self.assertTrue(review_path.exists())
            self.assertEqual(result.total_outputs, 110)

    def test_runtime_output_contains_110_detector_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_path, summary_path, review_path = _paths(temp_dir)
            build_market_read_packet(
                _CALIBRATED_INPUT,
                calibration_profile_path=_CALIBRATION_PROFILE,
                runtime_output_path=runtime_path,
                summary_json_path=summary_path,
                review_markdown_path=review_path,
            )
            outputs = json.loads(runtime_path.read_text(encoding="utf-8"))
            self.assertEqual(len(outputs), 110)

    def test_summary_reports_110_contracts_and_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_path, summary_path, review_path = _paths(temp_dir)
            build_market_read_packet(
                _CALIBRATED_INPUT,
                calibration_profile_path=_CALIBRATION_PROFILE,
                runtime_output_path=runtime_path,
                summary_json_path=summary_path,
                review_markdown_path=review_path,
            )
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["total_contracts"], 110)
            self.assertEqual(summary["total_outputs"], 110)

    def test_review_markdown_contains_non_execution_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_path, summary_path, review_path = _paths(temp_dir)
            build_market_read_packet(
                _CALIBRATED_INPUT,
                calibration_profile_path=_CALIBRATION_PROFILE,
                runtime_output_path=runtime_path,
                summary_json_path=summary_path,
                review_markdown_path=review_path,
            )
            review = review_path.read_text(encoding="utf-8")
            self.assertIn("## Boundary", review)
            self.assertIn("This packet is non-executional", review)

    def test_pipeline_with_calibration_reports_calibrated_non_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_path, summary_path, review_path = _paths(temp_dir)
            result = build_market_read_packet(
                _CALIBRATED_INPUT,
                calibration_profile_path=_CALIBRATION_PROFILE,
                runtime_output_path=runtime_path,
                summary_json_path=summary_path,
                review_markdown_path=review_path,
            )
            self.assertEqual(result.calibrated_non_refusal_count, 27)
            self.assertEqual(result.computable_non_refusal_count, 9)

    def test_pipeline_without_calibration_safely_refuses_calibrated_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_path, summary_path, review_path = _paths(temp_dir)
            result = build_market_read_packet(
                _CALIBRATED_INPUT,
                runtime_output_path=runtime_path,
                summary_json_path=summary_path,
                review_markdown_path=review_path,
            )
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(result.calibrated_non_refusal_count, 0)
            self.assertEqual(summary["counts_by_route"]["calibrated_refusal"], 27)

    def test_pipeline_fails_on_malformed_input_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad_input = Path(temp_dir) / "bad.json"
            bad_input.write_text("{bad json", encoding="utf-8")
            runtime_path, summary_path, review_path = _paths(temp_dir)
            with self.assertRaises(MarketReadPacketError):
                build_market_read_packet(
                    bad_input,
                    runtime_output_path=runtime_path,
                    summary_json_path=summary_path,
                    review_markdown_path=review_path,
                )

    def test_pipeline_fails_when_runtime_output_validation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_path, summary_path, review_path = _paths(temp_dir)
            with patch(
                "traders_market_read.pipeline.market_read_packet.run",
                return_value=_FakeRuntimeReport(),
            ):
                with self.assertRaises(MarketReadPacketError) as ctx:
                    build_market_read_packet(
                        _CALIBRATED_INPUT,
                        runtime_output_path=runtime_path,
                        summary_json_path=summary_path,
                        review_markdown_path=review_path,
                    )
            self.assertIn("detector output validation failed", str(ctx.exception))

    def test_generated_artifacts_contain_no_forbidden_execution_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_path, summary_path, review_path = _paths(temp_dir)
            build_market_read_packet(
                _CALIBRATED_INPUT,
                calibration_profile_path=_CALIBRATION_PROFILE,
                runtime_output_path=runtime_path,
                summary_json_path=summary_path,
                review_markdown_path=review_path,
            )
            runtime_outputs = json.loads(runtime_path.read_text(encoding="utf-8"))
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(find_forbidden_fields(runtime_outputs), [])
            self.assertEqual(find_forbidden_fields(summary), [])
            review_lower = review_path.read_text(encoding="utf-8").lower()
            for marker in _FORBIDDEN_MARKDOWN_FIELD_MARKERS:
                self.assertNotIn(marker, review_lower)

    def test_cli_writes_all_requested_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_path, summary_path, review_path = _paths(temp_dir)
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_market_read_packet.py",
                    str(_CALIBRATED_INPUT),
                    "--calibration-profile",
                    str(_CALIBRATION_PROFILE),
                    "--runtime-output",
                    str(runtime_path),
                    "--summary-json",
                    str(summary_path),
                    "--review-md",
                    str(review_path),
                ],
                cwd=_REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(runtime_path.exists())
            self.assertTrue(summary_path.exists())
            self.assertTrue(review_path.exists())


if __name__ == "__main__":
    unittest.main()
