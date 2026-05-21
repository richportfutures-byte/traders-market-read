"""Tests for the TMR-P32 source-data to static operator viewer pipeline."""

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
from traders_market_read.input.market_snapshot import load_market_snapshot
from traders_market_read.pipeline.source_data_html import (
    SourceDataHtmlPipelineError,
    build_source_data_operator_viewer,
)

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


def _output_kwargs(root: Path) -> dict[str, Path]:
    return {
        "market_snapshot_output_path": root / "snapshot.json",
        "runtime_output_path": root / "runtime.json",
        "summary_json_path": root / "summary.json",
        "operator_view_model_output_path": root / "view_model.json",
        "html_output_path": root / "viewer.html",
    }


class SourceDataOperatorViewerPipelineTests(unittest.TestCase):
    def test_pipeline_writes_all_five_requested_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = _output_kwargs(Path(temp_dir))
            build_source_data_operator_viewer(
                **_source_kwargs(),
                calibration_profile_path=_CALIBRATION_PROFILE,
                **outputs,
            )
            for path in outputs.values():
                self.assertTrue(path.exists(), msg=str(path))

    def test_generated_market_snapshot_passes_p29_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = _output_kwargs(Path(temp_dir))
            build_source_data_operator_viewer(
                **_source_kwargs(),
                calibration_profile_path=_CALIBRATION_PROFILE,
                **outputs,
            )
            self.assertEqual(
                load_market_snapshot(outputs["market_snapshot_output_path"]).source_shape,
                "market_snapshot_v1",
            )

    def test_generated_runtime_output_passes_detector_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = _output_kwargs(Path(temp_dir))
            build_source_data_operator_viewer(
                **_source_kwargs(),
                calibration_profile_path=_CALIBRATION_PROFILE,
                **outputs,
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/validate_detector_output.py",
                    str(outputs["runtime_output_path"]),
                ],
                cwd=_REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_generated_summary_reports_110_contracts_and_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = _output_kwargs(Path(temp_dir))
            build_source_data_operator_viewer(
                **_source_kwargs(),
                calibration_profile_path=_CALIBRATION_PROFILE,
                **outputs,
            )
            summary = json.loads(outputs["summary_json_path"].read_text(encoding="utf-8"))
            self.assertEqual(summary["total_contracts"], 110)
            self.assertEqual(summary["total_outputs"], 110)

    def test_generated_view_model_reports_110_contracts_and_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = _output_kwargs(Path(temp_dir))
            build_source_data_operator_viewer(
                **_source_kwargs(),
                calibration_profile_path=_CALIBRATION_PROFILE,
                **outputs,
            )
            view_model = json.loads(outputs["operator_view_model_output_path"].read_text(encoding="utf-8"))
            self.assertEqual(view_model["counts"]["total_contracts"], 110)
            self.assertEqual(view_model["counts"]["total_outputs"], 110)

    def test_generated_html_contains_non_execution_boundary_banner(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = _output_kwargs(Path(temp_dir))
            build_source_data_operator_viewer(
                **_source_kwargs(),
                calibration_profile_path=_CALIBRATION_PROFILE,
                **outputs,
            )
            html = outputs["html_output_path"].read_text(encoding="utf-8")
            self.assertIn("Non-executional", html)
            self.assertIn("No trade permission", html)

    def test_pipeline_with_calibration_reports_calibrated_non_refusals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = _output_kwargs(Path(temp_dir))
            result = build_source_data_operator_viewer(
                **_source_kwargs(),
                calibration_profile_path=_CALIBRATION_PROFILE,
                **outputs,
            )
            view_model = json.loads(outputs["operator_view_model_output_path"].read_text(encoding="utf-8"))
            self.assertEqual(result.total_outputs, 110)
            self.assertEqual(view_model["counts"]["calibrated_non_refusal_count"], 27)

    def test_pipeline_without_calibration_safely_refuses_calibrated_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = _output_kwargs(Path(temp_dir))
            build_source_data_operator_viewer(**_source_kwargs(), **outputs)
            view_model = json.loads(outputs["operator_view_model_output_path"].read_text(encoding="utf-8"))
            self.assertEqual(view_model["counts"]["calibrated_non_refusal_count"], 0)

    def test_pipeline_fails_on_forbidden_execution_source_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bad = Path(temp_dir) / "levels.json"
            data = json.loads((_SOURCE / "structural_levels.example.json").read_text(encoding="utf-8"))
            data["entry_price"] = 5000
            bad.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(SourceDataHtmlPipelineError):
                build_source_data_operator_viewer(
                    **_source_kwargs(structural_levels_path=bad),
                    **_output_kwargs(Path(temp_dir)),
                )

    def test_pipeline_fails_on_missing_source_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(SourceDataHtmlPipelineError):
                build_source_data_operator_viewer(
                    **_source_kwargs(session_bars_path=Path(temp_dir) / "missing.csv"),
                    **_output_kwargs(Path(temp_dir)),
                )

    def test_generated_artifacts_contain_no_forbidden_execution_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = _output_kwargs(Path(temp_dir))
            build_source_data_operator_viewer(
                **_source_kwargs(),
                calibration_profile_path=_CALIBRATION_PROFILE,
                **outputs,
            )
            for key in (
                "market_snapshot_output_path",
                "runtime_output_path",
                "summary_json_path",
                "operator_view_model_output_path",
            ):
                value = json.loads(outputs[key].read_text(encoding="utf-8"))
                self.assertEqual(find_forbidden_fields(value), [])

    def test_cli_writes_all_requested_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            snapshot = root / "snapshot.json"
            runtime = root / "runtime.json"
            summary = root / "summary.json"
            view_model = root / "view_model.json"
            html = root / "viewer.html"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/build_source_data_operator_viewer.py",
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
                    "--calibration-profile",
                    str(_CALIBRATION_PROFILE),
                    "--market-snapshot-output",
                    str(snapshot),
                    "--runtime-output",
                    str(runtime),
                    "--summary-json",
                    str(summary),
                    "--view-model-output",
                    str(view_model),
                    "--output-html",
                    str(html),
                ],
                cwd=_REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            for path in (snapshot, runtime, summary, view_model, html):
                self.assertTrue(path.exists(), msg=str(path))


if __name__ == "__main__":
    unittest.main()
