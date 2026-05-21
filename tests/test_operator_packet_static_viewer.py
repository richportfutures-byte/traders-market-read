"""Tests for the TMR-P32 static operator packet viewer."""

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

from traders_market_read.viewers.operator_packet_html import (
    OperatorPacketHtmlError,
    load_operator_view_model,
    render_operator_packet_html,
)

_VIEW_MODEL = _REPO_ROOT / "qa" / "examples" / "operator_packet_view_model.example.json"


class OperatorPacketStaticViewerTests(unittest.TestCase):
    def test_viewer_renders_html_from_view_model(self) -> None:
        html = render_operator_packet_html(load_operator_view_model(_VIEW_MODEL))
        self.assertIn("<!doctype html>", html)

    def test_cli_creates_output_html(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "viewer.html"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/render_operator_packet_viewer.py",
                    "--view-model",
                    str(_VIEW_MODEL),
                    "--output-html",
                    str(output),
                ],
                cwd=_REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            self.assertTrue(output.exists())

    def test_html_contains_title(self) -> None:
        html = render_operator_packet_html(load_operator_view_model(_VIEW_MODEL))
        self.assertIn("Trader's Market-Read Operator Packet", html)

    def test_html_contains_non_execution_boundary_banner(self) -> None:
        html = render_operator_packet_html(load_operator_view_model(_VIEW_MODEL))
        self.assertIn("Non-executional", html)
        self.assertIn("No trade permission", html)
        self.assertIn("No entries/stops/targets/sizing", html)

    def test_html_contains_market_read_layer_sections(self) -> None:
        html = render_operator_packet_html(load_operator_view_model(_VIEW_MODEL))
        self.assertIn("Market-Read Layers", html)
        self.assertIn("Read Discipline", html)
        self.assertIn("Setup Quality", html)

    def test_html_contains_active_findings(self) -> None:
        html = render_operator_packet_html(load_operator_view_model(_VIEW_MODEL))
        self.assertIn("Active Findings", html)
        self.assertIn("ch02_acceptance_vs_rejection", html)

    def test_html_contains_review_queue(self) -> None:
        html = render_operator_packet_html(load_operator_view_model(_VIEW_MODEL))
        self.assertIn("Review Queue", html)
        self.assertIn("ch01_confirmation_and_invalidation_discipline", html)

    def test_html_contains_blocked_by_feed_section(self) -> None:
        html = render_operator_packet_html(load_operator_view_model(_VIEW_MODEL))
        self.assertIn("Blocked-by-Feed", html)
        self.assertIn("ch04_liquidity_pulls_and_replenishment", html)

    def test_html_contains_context_governance_section(self) -> None:
        html = render_operator_packet_html(load_operator_view_model(_VIEW_MODEL))
        self.assertIn("Context Governance", html)
        self.assertIn("ch01_context_vs_execution_permission", html)

    def test_html_escapes_content_values(self) -> None:
        vm = load_operator_view_model(_VIEW_MODEL)
        vm = copy.deepcopy(vm)
        vm["active_findings"][0]["display_name"] = "<script>alert(1)</script>"
        html = render_operator_packet_html(vm)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertNotIn("<script>alert(1)</script>", html)

    def test_viewer_rejects_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "bad.json"
            bad.write_text("{bad json", encoding="utf-8")
            with self.assertRaises(OperatorPacketHtmlError):
                load_operator_view_model(bad)

    def test_viewer_rejects_missing_boundary_flags(self) -> None:
        vm = load_operator_view_model(_VIEW_MODEL)
        vm = copy.deepcopy(vm)
        del vm["boundary"]["no_trade_permission"]
        with self.assertRaises(OperatorPacketHtmlError):
            render_operator_packet_html(vm)

    def test_viewer_rejects_forbidden_execution_fields_recursively(self) -> None:
        vm = load_operator_view_model(_VIEW_MODEL)
        vm = copy.deepcopy(vm)
        vm["active_findings"][0]["entry_price"] = 5000
        with self.assertRaises(OperatorPacketHtmlError):
            render_operator_packet_html(vm)

    def test_html_output_contains_no_forbidden_execution_field_names(self) -> None:
        html = render_operator_packet_html(load_operator_view_model(_VIEW_MODEL)).lower()
        for field in (
            "entry_price",
            "stop_price",
            "target_price",
            "order_type",
            "quantity",
            "position_size",
            "account_id",
            "fill_price",
            "buy_now",
            "sell_now",
            "place_order",
            "reduce_position",
            "add_position",
        ):
            self.assertNotIn(field, html)


if __name__ == "__main__":
    unittest.main()
