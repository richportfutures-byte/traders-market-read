# P31 Operator Packet View Model Report

## Result

P31_PASS

## Files Created/Changed

- `src/traders_market_read/viewmodels/__init__.py`
- `src/traders_market_read/viewmodels/operator_packet.py`
- `scripts/build_operator_packet_view_model.py`
- `qa/examples/operator_packet_view_model.example.json`
- `qa/p31_operator_packet_view_model_report.md`
- `tests/test_operator_packet_view_model.py`
- `README.md`

## Artifacts

- Runtime output input path: `qa/examples/market_snapshot_built_runtime_output.example.json`
- Summary JSON input path: `qa/examples/market_snapshot_built_summary.example.json`
- Operator view model path: `qa/examples/operator_packet_view_model.example.json`

## View Model Counts

- Total contracts: 110
- Total outputs: 110
- Active findings count: 36
- Review queue count: 64
- Blocked-by-feed count: 3
- Context governance count: 7
- Layer count: 12

## Validation Results

- `python3 scripts/validate_detection_specs.py`: PASS
- `python3 scripts/build_detector_contract_catalog.py`: PASS
- `python3 scripts/build_market_snapshot_input.py --market-context qa/examples/source_data/market_context.example.json --structural-levels qa/examples/source_data/structural_levels.example.json --session-bars qa/examples/source_data/session_bars.example.csv --value-areas qa/examples/source_data/value_areas.example.json --profile-rows qa/examples/source_data/profile_rows.example.csv --tape-metrics qa/examples/source_data/tape_metrics.example.json --intermarket-metrics qa/examples/source_data/intermarket_metrics.example.json --output qa/examples/market_snapshot_built.example.json`: PASS
- `python3 scripts/build_market_read_packet.py qa/examples/market_snapshot_built.example.json --calibration-profile qa/examples/detector_runtime_calibrated_profile.example.yaml --runtime-output qa/examples/market_snapshot_built_runtime_output.example.json --summary-json qa/examples/market_snapshot_built_summary.example.json --review-md qa/examples/market_snapshot_built_review.example.md`: PASS
- `python3 scripts/build_operator_packet_view_model.py --runtime-output qa/examples/market_snapshot_built_runtime_output.example.json --summary-json qa/examples/market_snapshot_built_summary.example.json --output qa/examples/operator_packet_view_model.example.json`: PASS
- `python3 -m unittest tests/test_detector_runtime_v1.py tests/test_calibrated_detector_runtime_v1.py tests/test_runtime_summary_review_packet.py tests/test_market_read_packet_pipeline.py tests/test_market_snapshot_input_contract.py tests/test_market_snapshot_builder.py tests/test_operator_packet_view_model.py`: PASS, 102 tests
- `python3 -m py_compile scripts/build_operator_packet_view_model.py src/traders_market_read/viewmodels/operator_packet.py`: PASS

## Test Results

- View model builds from the built runtime output and summary artifacts.
- Required top-level fields are present.
- Counts match 110 contracts and 110 outputs.
- Active findings include COMPUTABLE and CALIBRATED non-refusal outputs.
- Review queue contains JUDGMENT_ASSISTED review/refusal items.
- Blocked-by-feed contains NOT_DETECTABLE_WITH_CURRENT_FEEDS items.
- Context governance contains CONTEXT_ONLY items.
- Layer grouping is deterministic and covers all 12 chapters/layers.
- Missing/degraded input aggregation is deterministic.
- Forbidden execution fields are rejected recursively.
- Guardrail failures are rejected.
- CLI writes the requested output file.
- Output boundary flags are present.
- Output contains no forbidden execution fields.

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
python3 scripts/build_operator_packet_view_model.py --runtime-output qa/examples/market_snapshot_built_runtime_output.example.json --summary-json qa/examples/market_snapshot_built_summary.example.json --output qa/examples/operator_packet_view_model.example.json
```
