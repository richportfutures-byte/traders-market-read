"""Static viewers for operator-facing market-read artifacts."""

from .operator_packet_html import (
    OperatorPacketHtmlError,
    load_operator_view_model,
    render_operator_packet_html,
    write_operator_packet_html,
)

__all__ = [
    "OperatorPacketHtmlError",
    "load_operator_view_model",
    "render_operator_packet_html",
    "write_operator_packet_html",
]
