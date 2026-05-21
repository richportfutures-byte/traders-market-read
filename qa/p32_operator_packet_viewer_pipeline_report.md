# P32 Operator Packet Viewer and End-to-End Render Pipeline Report

## Result

P32_PASS

## Files Created/Changed

- `src/traders_market_read/viewers/__init__.py`
- `src/traders_market_read/viewers/operator_packet_html.py`
- `src/traders_market_read/pipeline/source_data_html.py`
- `scripts/render_operator_packet_viewer.py`
- `scripts/build_source_data_operator_viewer.py`
- `qa/examples/operator_packet_viewer.example.html`
- `qa/examples/source_data_operator_snapshot.example.json`
- `qa/examples/source_data_operator_runtime_output.example.json`
- `qa/examples/source_data_operator_summary.example.json`
- `qa/examples/source_data_operator_view_model.example.json`
- `qa/examples/source_data_operator_viewer.example.html`
- `qa/p32_operator_packet_viewer_pipeline_report.md`
- `tests/test_operator_packet_static_viewer.py`
- `tests/test_source_data_operator_viewer_pipeline.py`
- `README.md`

## Static Viewer

- Static viewer input path: `qa/examples/operator_packet_view_model.example.json`
- Static viewer HTML output path: `qa/examples/operator_packet_viewer.example.html`

## End-to-End Source-Data Command Used

```bash
python3 scripts/build_source_data_operator_viewer.py --market-context qa/examples/source_data/market_context.example.json --structural-levels qa/examples/source_data/structural_levels.example.json --session-bars qa/examples/source_data/session_bars.example.csv --value-areas qa/examples/source_data/value_areas.example.json --profile-rows qa/examples/source_data/profile_rows.example.csv --tape-metrics qa/examples/source_data/tape_metrics.example.json --intermarket-metrics qa/examples/source_data/intermarket_metrics.example.json --calibration-profile qa/examples/detector_runtime_calibrated_profile.example.yaml --market-snapshot-output qa/examples/source_data_operator_snapshot.example.json --runtime-output qa/examples/source_data_operator_runtime_output.example.json --summary-json qa/examples/source_data_operator_summary.example.json --view-model-output qa/examples/source_data_operator_view_model.example.json --output-html qa/examples/source_data_operator_viewer.example.html
```

## Generated Artifacts

- Generated market snapshot path: `qa/examples/source_data_operator_snapshot.example.json`
- Generated runtime output path: `qa/examples/source_data_operator_runtime_output.example.json`
- Generated summary path: `qa/examples/source_data_operator_summary.example.json`
- Generated operator view-model path: `qa/examples/source_data_operator_view_model.example.json`
- Generated HTML viewer path: `qa/examples/source_data_operator_viewer.example.html`

## Counts

- Total contracts: 110
- Total outputs: 110
- Active findings count: 36
- Review queue count: 64
- Blocked-by-feed count: 3
- Context governance count: 7

## Validation Results

- `python3 scripts/validate_detection_specs.py`: PASS
- `python3 scripts/build_detector_contract_catalog.py`: PASS
- `python3 scripts/build_market_snapshot_input.py --market-context qa/examples/source_data/market_context.example.json --structural-levels qa/examples/source_data/structural_levels.example.json --session-bars qa/examples/source_data/session_bars.example.csv --value-areas qa/examples/source_data/value_areas.example.json --profile-rows qa/examples/source_data/profile_rows.example.csv --tape-metrics qa/examples/source_data/tape_metrics.example.json --intermarket-metrics qa/examples/source_data/intermarket_metrics.example.json --output qa/examples/market_snapshot_built.example.json`: PASS
- `python3 scripts/build_market_read_packet.py qa/examples/market_snapshot_built.example.json --calibration-profile qa/examples/detector_runtime_calibrated_profile.example.yaml --runtime-output qa/examples/market_snapshot_built_runtime_output.example.json --summary-json qa/examples/market_snapshot_built_summary.example.json --review-md qa/examples/market_snapshot_built_review.example.md`: PASS
- `python3 scripts/build_operator_packet_view_model.py --runtime-output qa/examples/market_snapshot_built_runtime_output.example.json --summary-json qa/examples/market_snapshot_built_summary.example.json --output qa/examples/operator_packet_view_model.example.json`: PASS
- `python3 scripts/render_operator_packet_viewer.py --view-model qa/examples/operator_packet_view_model.example.json --output-html qa/examples/operator_packet_viewer.example.html`: PASS
- `python3 scripts/build_source_data_operator_viewer.py --market-context qa/examples/source_data/market_context.example.json --structural-levels qa/examples/source_data/structural_levels.example.json --session-bars qa/examples/source_data/session_bars.example.csv --value-areas qa/examples/source_data/value_areas.example.json --profile-rows qa/examples/source_data/profile_rows.example.csv --tape-metrics qa/examples/source_data/tape_metrics.example.json --intermarket-metrics qa/examples/source_data/intermarket_metrics.example.json --calibration-profile qa/examples/detector_runtime_calibrated_profile.example.yaml --market-snapshot-output qa/examples/source_data_operator_snapshot.example.json --runtime-output qa/examples/source_data_operator_runtime_output.example.json --summary-json qa/examples/source_data_operator_summary.example.json --view-model-output qa/examples/source_data_operator_view_model.example.json --output-html qa/examples/source_data_operator_viewer.example.html`: PASS
- `python3 -m unittest tests/test_detector_runtime_v1.py tests/test_calibrated_detector_runtime_v1.py tests/test_runtime_summary_review_packet.py tests/test_market_read_packet_pipeline.py tests/test_market_snapshot_input_contract.py tests/test_market_snapshot_builder.py tests/test_operator_packet_view_model.py tests/test_operator_packet_static_viewer.py tests/test_source_data_operator_viewer_pipeline.py`: PASS, 128 tests
- `python3 -m py_compile scripts/render_operator_packet_viewer.py scripts/build_source_data_operator_viewer.py src/traders_market_read/viewers/operator_packet_html.py src/traders_market_read/pipeline/source_data_html.py`: PASS

## Test Results

- Static viewer renders HTML from the operator packet view model.
- Static viewer CLI writes the requested HTML file.
- HTML includes title, boundary banner, market-read layers, active findings, review queue, blocked-by-feed, context governance, and missing/degraded input sections.
- HTML escapes content values.
- Viewer rejects malformed JSON, missing boundary flags, and forbidden execution fields.
- End-to-end pipeline writes all five requested artifacts.
- Generated market snapshot passes P29 validation.
- Generated runtime output passes detector output validation.
- Generated summary and view model report 110 contracts and 110 outputs.
- Pipeline works with calibration profile and without calibration profile.
- Pipeline rejects forbidden execution source fields and missing source files.
- Generated JSON artifacts contain no forbidden execution fields.
- End-to-end CLI writes all requested outputs.

## Boundary Confirmation

- No new detector logic was created.
- No new calibration values were created.
- No live data adapters were created.
- No trade permission was created.
- No entries/stops/targets/sizing were created.
- No broker/order/account/fill/P&L behavior was created.

## Remaining Blockers

None.

## Operator Usage

```bash
python3 scripts/render_operator_packet_viewer.py --view-model qa/examples/operator_packet_view_model.example.json --output-html qa/examples/operator_packet_viewer.example.html
```

```bash
python3 scripts/build_source_data_operator_viewer.py --market-context qa/examples/source_data/market_context.example.json --structural-levels qa/examples/source_data/structural_levels.example.json --session-bars qa/examples/source_data/session_bars.example.csv --value-areas qa/examples/source_data/value_areas.example.json --profile-rows qa/examples/source_data/profile_rows.example.csv --tape-metrics qa/examples/source_data/tape_metrics.example.json --intermarket-metrics qa/examples/source_data/intermarket_metrics.example.json --calibration-profile qa/examples/detector_runtime_calibrated_profile.example.yaml --market-snapshot-output qa/examples/source_data_operator_snapshot.example.json --runtime-output qa/examples/source_data_operator_runtime_output.example.json --summary-json qa/examples/source_data_operator_summary.example.json --view-model-output qa/examples/source_data_operator_view_model.example.json --output-html qa/examples/source_data_operator_viewer.example.html
```
