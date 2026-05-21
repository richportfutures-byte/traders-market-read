"""Tests for the TMR-P30 market snapshot builder."""

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

from traders_market_read.detectors.output import find_forbidden_fields
from traders_market_read.input.market_snapshot import load_market_snapshot, validate_market_snapshot_payload
from traders_market_read.input.snapshot_builder import (
    MarketSnapshotBuilderError,
    build_market_snapshot_from_sources,
    write_market_snapshot,
)
from traders_market_read.pipeline.market_read_packet import build_market_read_packet

_SOURCE = _REPO_ROOT / "qa" / "examples" / "source_data"
_CALIBRATION_PROFILE = (
    _REPO_ROOT / "qa" / "examples" / "detector_runtime_calibrated_profile.example.yaml"
)


def _source_kwargs(**overrides: Path) -> dict[str, Path]:
    paths = {
        "market_context_path": _SOURCE / "market_context.example.json",
        "structural_levels_path": _SOURCE / "structural_levels.example.json",
        "session_bars_path": _SOURCE / "session_bars.example.csv",
        "value_areas_path": _SOURCE / "value_areas.example.json",
        "profile_rows_path": _SOURCE / "profile_rows.example.csv",
        "tape_metrics_path": _SOURCE / "tape_metrics.example.json",
        "intermarket_metrics_path": _SOURCE / "intermarket_metrics.example.json",
    }
    paths.update(overrides)
    return paths


class MarketSnapshotBuilderTests(unittest.TestCase):
    def test_builder_creates_required_top_level_fields(self) -> None:
        result = build_market_snapshot_from_sources(**_source_kwargs())
        self.assertEqual(set(result.snapshot), {"schema_version", "market_context", "detector_inputs"})
        self.assertEqual(result.snapshot["schema_version"], 1)

    def test_builder_writes_detector_input_blocks(self) -> None:
        result = build_market_snapshot_from_sources(**_source_kwargs())
        self.assertEqual(result.detector_input_blocks_written, 48)
        self.assertEqual(result.computable_blocks_written, 9)
        self.assertEqual(result.calibrated_blocks_written, 27)

    def test_builder_output_passes_p29_validation(self) -> None:
        result = build_market_snapshot_from_sources(**_source_kwargs())
        snapshot = validate_market_snapshot_payload(result.snapshot)
        self.assertEqual(snapshot.source_shape, "market_snapshot_v1")

    def test_builder_rejects_forbidden_execution_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "structural.json"
            data = json.loads((_SOURCE / "structural_levels.example.json").read_text(encoding="utf-8"))
            data["entry_price"] = 5000
            bad.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(MarketSnapshotBuilderError):
                build_market_snapshot_from_sources(
                    **_source_kwargs(structural_levels_path=bad)
                )

    def test_builder_rejects_missing_market_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "market_context.json"
            bad.write_text(json.dumps({"instrument": "EXAMPLE"}), encoding="utf-8")
            with self.assertRaises(MarketSnapshotBuilderError):
                build_market_snapshot_from_sources(**_source_kwargs(market_context_path=bad))

    def test_builder_rejects_malformed_csv(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "session_bars.csv"
            bad.write_text("period,session,open,high,low,close,volume\nP1,current,notnum,1,1,1,1\n", encoding="utf-8")
            with self.assertRaises(MarketSnapshotBuilderError):
                build_market_snapshot_from_sources(**_source_kwargs(session_bars_path=bad))

    def test_builder_generated_snapshot_runs_through_packet_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            snapshot_path = root / "snapshot.json"
            runtime_path = root / "runtime.json"
            summary_path = root / "summary.json"
            review_path = root / "review.md"
            result = build_market_snapshot_from_sources(**_source_kwargs())
            write_market_snapshot(snapshot_path, result.snapshot)
            packet = build_market_read_packet(
                snapshot_path,
                calibration_profile_path=_CALIBRATION_PROFILE,
                runtime_output_path=runtime_path,
                summary_json_path=summary_path,
                review_markdown_path=review_path,
            )
            self.assertEqual(packet.total_outputs, 110)
            self.assertEqual(packet.calibrated_non_refusal_count, 27)

    def test_pipeline_output_from_builder_snapshot_validates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            snapshot_path = root / "snapshot.json"
            runtime_path = root / "runtime.json"
            summary_path = root / "summary.json"
            review_path = root / "review.md"
            result = build_market_snapshot_from_sources(**_source_kwargs())
            write_market_snapshot(snapshot_path, result.snapshot)
            build_market_read_packet(
                snapshot_path,
                calibration_profile_path=_CALIBRATION_PROFILE,
                runtime_output_path=runtime_path,
                summary_json_path=summary_path,
                review_markdown_path=review_path,
            )
            validate = subprocess.run(
                [
                    sys.executable,
                    "scripts/validate_detector_output.py",
                    str(runtime_path),
                ],
                cwd=_REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(validate.returncode, 0, msg=validate.stdout + validate.stderr)

    def test_builder_does_not_require_every_detector_concept_block(self) -> None:
        result = build_market_snapshot_from_sources(**_source_kwargs())
        concept_blocks = [key for key in result.snapshot["detector_inputs"] if key.startswith("ch")]
        self.assertEqual(len(concept_blocks), 27)
        self.assertLess(len(concept_blocks), 110)

    def test_builder_snapshot_contains_no_forbidden_execution_fields(self) -> None:
        result = build_market_snapshot_from_sources(**_source_kwargs())
        self.assertEqual(find_forbidden_fields(result.snapshot), [])

    def test_cli_writes_requested_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "snapshot.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_market_snapshot_input.py",
                    "--market-context",
                    str(_SOURCE / "market_context.example.json"),
                    "--structural-levels",
                    str(_SOURCE / "structural_levels.example.json"),
                    "--session-bars",
                    str(_SOURCE / "session_bars.example.csv"),
                    "--value-areas",
                    str(_SOURCE / "value_areas.example.json"),
                    "--profile-rows",
                    str(_SOURCE / "profile_rows.example.csv"),
                    "--tape-metrics",
                    str(_SOURCE / "tape_metrics.example.json"),
                    "--intermarket-metrics",
                    str(_SOURCE / "intermarket_metrics.example.json"),
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

    def test_source_data_fixtures_are_fake_example_and_non_executional(self) -> None:
        context = json.loads((_SOURCE / "market_context.example.json").read_text(encoding="utf-8"))
        self.assertEqual(context["instrument"], "EXAMPLE")
        self.assertEqual(context["source"], "example_static_source_data")
        for path in _SOURCE.iterdir():
            if path.suffix == ".json":
                self.assertEqual(find_forbidden_fields(json.loads(path.read_text(encoding="utf-8"))), [])
if __name__ == "__main__":
    unittest.main()
