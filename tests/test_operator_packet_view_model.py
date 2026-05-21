"""Tests for the TMR-P31 operator packet view model."""

from __future__ import annotations

import copy
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

from traders_market_read.detectors.output import find_forbidden_fields
from traders_market_read.viewmodels.operator_packet import (
    OperatorPacketViewModelError,
    build_operator_packet_view_model,
)

_EXAMPLES = _REPO_ROOT / "qa" / "examples"
_RUNTIME = _EXAMPLES / "market_snapshot_built_runtime_output.example.json"
_SUMMARY = _EXAMPLES / "market_snapshot_built_summary.example.json"


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


class OperatorPacketViewModelTests(unittest.TestCase):
    def test_view_model_builds_from_built_packet_artifacts(self) -> None:
        vm = build_operator_packet_view_model(
            runtime_output_path=_RUNTIME,
            summary_json_path=_SUMMARY,
        )
        self.assertEqual(vm["schema_version"], 1)

    def test_view_model_contains_required_top_level_fields(self) -> None:
        vm = build_operator_packet_view_model(
            runtime_output_path=_RUNTIME,
            summary_json_path=_SUMMARY,
        )
        required = {
            "schema_version",
            "source_artifacts",
            "counts",
            "boundary",
            "market_read_layers",
            "active_findings",
            "review_queue",
            "blocked_by_feed",
            "context_governance",
            "missing_or_degraded_inputs",
        }
        self.assertTrue(required.issubset(vm))

    def test_counts_match_110_contracts_and_outputs(self) -> None:
        vm = build_operator_packet_view_model(
            runtime_output_path=_RUNTIME,
            summary_json_path=_SUMMARY,
        )
        self.assertEqual(vm["counts"]["total_contracts"], 110)
        self.assertEqual(vm["counts"]["total_outputs"], 110)

    def test_active_findings_include_computable_and_calibrated(self) -> None:
        vm = build_operator_packet_view_model(
            runtime_output_path=_RUNTIME,
            summary_json_path=_SUMMARY,
        )
        classes = {item["determinism_class"] for item in vm["active_findings"]}
        self.assertIn("COMPUTABLE", classes)
        self.assertIn("CALIBRATED", classes)
        self.assertEqual(len(vm["active_findings"]), 36)

    def test_review_queue_contains_judgment_assisted_items(self) -> None:
        vm = build_operator_packet_view_model(
            runtime_output_path=_RUNTIME,
            summary_json_path=_SUMMARY,
        )
        self.assertEqual(len(vm["review_queue"]), 64)
        self.assertTrue(all(item["state"] == "REVIEW_REQUIRED" for item in vm["review_queue"][:5]))

    def test_blocked_by_feed_contains_not_detectable_items(self) -> None:
        vm = build_operator_packet_view_model(
            runtime_output_path=_RUNTIME,
            summary_json_path=_SUMMARY,
        )
        self.assertEqual(len(vm["blocked_by_feed"]), 3)
        self.assertTrue(
            all("feed" in item["refusal_reason"].lower() for item in vm["blocked_by_feed"])
        )

    def test_context_governance_contains_context_only_items(self) -> None:
        vm = build_operator_packet_view_model(
            runtime_output_path=_RUNTIME,
            summary_json_path=_SUMMARY,
        )
        self.assertEqual(len(vm["context_governance"]), 7)
        self.assertTrue(
            all("no execution permission" in item["boundary_note"] for item in vm["context_governance"])
        )

    def test_layer_grouping_is_deterministic_and_covers_all_layers(self) -> None:
        vm = build_operator_packet_view_model(
            runtime_output_path=_RUNTIME,
            summary_json_path=_SUMMARY,
        )
        layer_ids = [layer["layer_id"] for layer in vm["market_read_layers"]]
        self.assertEqual(
            layer_ids,
            [
                "read_discipline",
                "level_interaction",
                "auction_profile",
                "tape_microstructure",
                "momentum_day_type",
                "traps_positioning",
                "session_context",
                "volatility_regime",
                "intermarket_confirmation",
                "catalyst_interpretation",
                "trade_state_management",
                "setup_quality",
            ],
        )
        self.assertEqual(sum(layer["total_outputs"] for layer in vm["market_read_layers"]), 110)

    def test_missing_degraded_input_aggregation_is_deterministic(self) -> None:
        first = build_operator_packet_view_model(
            runtime_output_path=_RUNTIME,
            summary_json_path=_SUMMARY,
        )["missing_or_degraded_inputs"]
        second = build_operator_packet_view_model(
            runtime_output_path=_RUNTIME,
            summary_json_path=_SUMMARY,
        )["missing_or_degraded_inputs"]
        self.assertEqual(first, second)
        self.assertEqual(first, sorted(first, key=lambda item: item["concept_id"]))

    def test_forbidden_execution_fields_are_rejected_recursively(self) -> None:
        runtime = json.loads(_RUNTIME.read_text(encoding="utf-8"))
        runtime[0]["evidence"]["nested"] = {"entry_price": 5000}
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_path = Path(temp_dir) / "runtime.json"
            _write_json(runtime_path, runtime)
            with self.assertRaises(OperatorPacketViewModelError):
                build_operator_packet_view_model(
                    runtime_output_path=runtime_path,
                    summary_json_path=_SUMMARY,
                )

    def test_guardrail_failures_are_rejected(self) -> None:
        runtime = json.loads(_RUNTIME.read_text(encoding="utf-8"))
        runtime[0] = copy.deepcopy(runtime[0])
        runtime[0]["guardrails"]["no_trade_permission"] = False
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime_path = Path(temp_dir) / "runtime.json"
            _write_json(runtime_path, runtime)
            with self.assertRaises(OperatorPacketViewModelError):
                build_operator_packet_view_model(
                    runtime_output_path=runtime_path,
                    summary_json_path=_SUMMARY,
                )

    def test_cli_writes_requested_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "view_model.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_operator_packet_view_model.py",
                    "--runtime-output",
                    str(_RUNTIME),
                    "--summary-json",
                    str(_SUMMARY),
                    "--output",
                    str(output),
                ],
                cwd=_REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(output.exists())

    def test_output_contains_non_execution_boundary_flags(self) -> None:
        vm = build_operator_packet_view_model(
            runtime_output_path=_RUNTIME,
            summary_json_path=_SUMMARY,
        )
        self.assertIs(vm["boundary"]["non_executional"], True)
        self.assertIs(vm["boundary"]["no_trade_permission"], True)
        self.assertIs(vm["boundary"]["no_entries_stops_targets_sizing"], True)
        self.assertIs(vm["boundary"]["no_broker_order_account_fill_pnl"], True)
        self.assertIs(vm["boundary"]["no_autonomous_trading"], True)

    def test_output_contains_no_forbidden_execution_fields(self) -> None:
        vm = build_operator_packet_view_model(
            runtime_output_path=_RUNTIME,
            summary_json_path=_SUMMARY,
        )
        self.assertEqual(find_forbidden_fields(vm), [])


if __name__ == "__main__":
    unittest.main()
