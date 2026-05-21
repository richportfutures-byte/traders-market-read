"""Tests for the TMR-P27 runtime summary and review packet."""

from __future__ import annotations

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

from traders_market_read.reporting.runtime_summary import (
    RuntimeSummaryError,
    build_runtime_summary,
    render_review_packet_markdown,
)

_EXAMPLES = _REPO_ROOT / "qa" / "examples"
_CALIBRATED_OUTPUT = _EXAMPLES / "detector_runtime_calibrated_output.example.json"

_FORBIDDEN_BOUNDARY_TERMS = (
    "entry_price",
    "stop_price",
    "target_price",
    "order_type",
    "quantity",
    "position_size",
    "account_id",
    "fill_price",
    "pnl",
    "buy_now",
    "sell_now",
    "place_order",
    "reduce_position",
    "add_position",
)


def _load_outputs() -> list[dict]:
    return json.loads(_CALIBRATED_OUTPUT.read_text(encoding="utf-8"))


def _write_temp(outputs: list[dict]) -> Path:
    handle = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", encoding="utf-8", delete=False
    )
    with handle:
        json.dump(outputs, handle)
    return Path(handle.name)


class RuntimeSummaryTests(unittest.TestCase):
    def test_summary_loads_calibrated_runtime_output(self) -> None:
        summary = build_runtime_summary(_CALIBRATED_OUTPUT)
        self.assertEqual(summary["total_outputs"], 110)
        self.assertEqual(summary["input_path"], str(_CALIBRATED_OUTPUT))

    def test_summary_includes_all_110_contracts(self) -> None:
        summary = build_runtime_summary(_CALIBRATED_OUTPUT)
        self.assertEqual(summary["total_contracts"], 110)
        self.assertEqual(summary["missing_outputs"], [])
        self.assertEqual(summary["duplicate_outputs"], [])

    def test_duplicate_output_concept_id_is_detected(self) -> None:
        outputs = _load_outputs()
        outputs[1] = dict(outputs[0])
        temp = _write_temp(outputs)
        try:
            with self.assertRaises(RuntimeSummaryError) as ctx:
                build_runtime_summary(temp)
            self.assertIn("duplicate output concept_id", str(ctx.exception))
        finally:
            temp.unlink(missing_ok=True)

    def test_missing_output_concept_id_is_detected(self) -> None:
        outputs = _load_outputs()[:-1]
        temp = _write_temp(outputs)
        try:
            with self.assertRaises(RuntimeSummaryError) as ctx:
                build_runtime_summary(temp)
            self.assertIn("missing output", str(ctx.exception))
        finally:
            temp.unlink(missing_ok=True)

    def test_forbidden_execution_fields_are_detected_recursively(self) -> None:
        outputs = _load_outputs()
        outputs[0]["evidence"]["nested"] = {"entry_price": 5000}
        temp = _write_temp(outputs)
        try:
            with self.assertRaises(RuntimeSummaryError) as ctx:
                build_runtime_summary(temp)
            self.assertIn("forbidden execution field", str(ctx.exception))
        finally:
            temp.unlink(missing_ok=True)

    def test_missing_or_false_guardrail_booleans_are_detected(self) -> None:
        outputs = _load_outputs()
        del outputs[0]["guardrails"]["no_trade_permission"]
        outputs[1]["guardrails"]["no_execution_fields"] = False
        temp = _write_temp(outputs)
        try:
            with self.assertRaises(RuntimeSummaryError) as ctx:
                build_runtime_summary(temp)
            message = str(ctx.exception)
            self.assertIn("guardrail validation failed", message)
            self.assertIn("guardrails.no_trade_permission", message)
            self.assertIn("guardrails.no_execution_fields", message)
        finally:
            temp.unlink(missing_ok=True)

    def test_non_refusal_counts_for_computable_and_calibrated_outputs(self) -> None:
        summary = build_runtime_summary(_CALIBRATED_OUTPUT)
        self.assertEqual(summary["computable_non_refusal_count"], 9)
        self.assertEqual(summary["calibrated_non_refusal_count"], 27)

    def test_judgment_assisted_review_refusal_count(self) -> None:
        summary = build_runtime_summary(_CALIBRATED_OUTPUT)
        self.assertEqual(summary["judgment_assisted_review_count"], 64)
        self.assertEqual(len(summary["review_queue"]), 64)

    def test_review_packet_markdown_is_generated(self) -> None:
        summary = build_runtime_summary(_CALIBRATED_OUTPUT)
        markdown = render_review_packet_markdown(_CALIBRATED_OUTPUT, summary)
        self.assertIn("# Detector Runtime Review Packet", markdown)
        self.assertIn("## JUDGMENT_ASSISTED Review Queue", markdown)
        self.assertIn("## Blocked-by-Feed Concepts", markdown)

    def test_review_packet_contains_non_execution_boundary_language(self) -> None:
        markdown = render_review_packet_markdown(_CALIBRATED_OUTPUT)
        self.assertIn("This packet is non-executional", markdown)
        self.assertIn("no trade permission", markdown)
        self.assertIn("no entries/stops/targets/sizing", markdown)
        self.assertIn("no broker/order/account/fill/P&L behavior", markdown)

    def test_review_packet_does_not_contain_forbidden_execution_fields(self) -> None:
        markdown = render_review_packet_markdown(_CALIBRATED_OUTPUT)
        lower = markdown.lower()
        for term in _FORBIDDEN_BOUNDARY_TERMS:
            self.assertNotIn(term, lower)

    def test_cli_writes_summary_json_and_review_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            summary_path = Path(temp_dir) / "summary.json"
            review_path = Path(temp_dir) / "review.md"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/summarize_detector_runtime.py",
                    str(_CALIBRATED_OUTPUT),
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
            self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
            self.assertTrue(summary_path.exists())
            self.assertTrue(review_path.exists())
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["total_contracts"], 110)
            self.assertIn(
                "# Detector Runtime Review Packet",
                review_path.read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
