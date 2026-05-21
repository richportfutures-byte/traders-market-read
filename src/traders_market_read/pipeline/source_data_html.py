"""End-to-end source-data to static operator HTML pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from traders_market_read.input.market_snapshot import MarketSnapshotInputError, load_market_snapshot
from traders_market_read.input.snapshot_builder import (
    MarketSnapshotBuilderError,
    build_market_snapshot_from_sources,
    write_market_snapshot,
)
from traders_market_read.pipeline.market_read_packet import (
    MarketReadPacketError,
    build_market_read_packet,
)
from traders_market_read.viewmodels.operator_packet import (
    OperatorPacketViewModelError,
    build_operator_packet_view_model,
    write_operator_packet_view_model,
)
from traders_market_read.viewers.operator_packet_html import (
    OperatorPacketHtmlError,
    render_operator_packet_html,
    write_operator_packet_html,
)


class SourceDataHtmlPipelineError(RuntimeError):
    """Raised when the source-data to HTML pipeline fails closed."""


@dataclass(frozen=True)
class SourceDataHtmlPipelineResult:
    market_snapshot_path: Path
    runtime_output_path: Path
    summary_json_path: Path
    operator_view_model_path: Path
    html_viewer_path: Path
    total_contracts: int
    total_outputs: int
    active_findings_count: int
    refusal_count: int
    non_refusal_count: int
    review_queue_count: int
    blocked_by_feed_count: int
    context_governance_count: int


def build_source_data_operator_viewer(
    *,
    market_context_path: str | Path,
    structural_levels_path: str | Path,
    session_bars_path: str | Path,
    value_areas_path: str | Path,
    profile_rows_path: str | Path,
    tape_metrics_path: str | Path,
    intermarket_metrics_path: str | Path,
    market_snapshot_output_path: str | Path,
    runtime_output_path: str | Path,
    summary_json_path: str | Path,
    operator_view_model_output_path: str | Path,
    html_output_path: str | Path,
    calibration_profile_path: str | Path | None = None,
) -> SourceDataHtmlPipelineResult:
    """Build snapshot, packet, operator view model, and static HTML."""
    snapshot_path = Path(market_snapshot_output_path)
    runtime_path = Path(runtime_output_path)
    summary_path = Path(summary_json_path)
    view_model_path = Path(operator_view_model_output_path)
    html_path = Path(html_output_path)

    try:
        snapshot_result = build_market_snapshot_from_sources(
            market_context_path=market_context_path,
            structural_levels_path=structural_levels_path,
            session_bars_path=session_bars_path,
            value_areas_path=value_areas_path,
            profile_rows_path=profile_rows_path,
            tape_metrics_path=tape_metrics_path,
            intermarket_metrics_path=intermarket_metrics_path,
        )
        write_market_snapshot(snapshot_path, snapshot_result.snapshot)
        load_market_snapshot(snapshot_path)

        with TemporaryDirectory() as temp_dir:
            packet_result = build_market_read_packet(
                snapshot_path,
                calibration_profile_path=calibration_profile_path,
                runtime_output_path=runtime_path,
                summary_json_path=summary_path,
                review_markdown_path=Path(temp_dir) / "review_packet.md",
            )
        view_model = build_operator_packet_view_model(
            runtime_output_path=runtime_path,
            summary_json_path=summary_path,
        )
        write_operator_packet_view_model(view_model_path, view_model)
        html = render_operator_packet_html(view_model)
        write_operator_packet_html(html_path, html)
    except (
        MarketSnapshotBuilderError,
        MarketSnapshotInputError,
        MarketReadPacketError,
        OperatorPacketViewModelError,
        OperatorPacketHtmlError,
    ) as exc:
        raise SourceDataHtmlPipelineError(str(exc)) from exc

    return SourceDataHtmlPipelineResult(
        market_snapshot_path=snapshot_path,
        runtime_output_path=runtime_path,
        summary_json_path=summary_path,
        operator_view_model_path=view_model_path,
        html_viewer_path=html_path,
        total_contracts=packet_result.total_contracts,
        total_outputs=packet_result.total_outputs,
        active_findings_count=len(view_model["active_findings"]),
        refusal_count=packet_result.refusal_count,
        non_refusal_count=packet_result.non_refusal_count,
        review_queue_count=len(view_model["review_queue"]),
        blocked_by_feed_count=len(view_model["blocked_by_feed"]),
        context_governance_count=len(view_model["context_governance"]),
    )
