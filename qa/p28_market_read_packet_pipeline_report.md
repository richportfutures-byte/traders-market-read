# P28 Market-Read Packet Pipeline Report

## Result

P28_PASS

## Files Created/Changed

- `src/traders_market_read/pipeline/__init__.py`
- `src/traders_market_read/pipeline/market_read_packet.py`
- `scripts/build_market_read_packet.py`
- `qa/examples/market_read_packet_runtime_output.example.json`
- `qa/examples/market_read_packet_summary.example.json`
- `qa/examples/market_read_packet_review.example.md`
- `qa/p28_market_read_packet_pipeline_report.md`
- `tests/test_market_read_packet_pipeline.py`
- `README.md`

## Pipeline Command Used

```bash
python3 scripts/build_market_read_packet.py qa/examples/detector_runtime_calibrated_input.example.json --calibration-profile qa/examples/detector_runtime_calibrated_profile.example.yaml --runtime-output qa/examples/market_read_packet_runtime_output.example.json --summary-json qa/examples/market_read_packet_summary.example.json --review-md qa/examples/market_read_packet_review.example.md
```

## Pipeline Artifacts

- Runtime output path: `qa/examples/market_read_packet_runtime_output.example.json`
- Summary JSON path: `qa/examples/market_read_packet_summary.example.json`
- Review Markdown path: `qa/examples/market_read_packet_review.example.md`

## Pipeline Counts

- Total contracts: 110
- Total outputs: 110
- Refusal count: 64
- Non-refusal count: 46
- Review queue count: 64
- Calibrated non-refusal count: 27
- Computable non-refusal count: 9

## Validation Results

- `python3 scripts/validate_detection_specs.py`: PASS
- `python3 scripts/build_detector_contract_catalog.py`: PASS
- `python3 scripts/build_market_read_packet.py qa/examples/detector_runtime_calibrated_input.example.json --calibration-profile qa/examples/detector_runtime_calibrated_profile.example.yaml --runtime-output qa/examples/market_read_packet_runtime_output.example.json --summary-json qa/examples/market_read_packet_summary.example.json --review-md qa/examples/market_read_packet_review.example.md`: PASS
- `python3 scripts/validate_detector_output.py qa/examples/market_read_packet_runtime_output.example.json`: PASS
- `python3 scripts/summarize_detector_runtime.py qa/examples/market_read_packet_runtime_output.example.json --summary-json qa/examples/market_read_packet_summary.example.json --review-md qa/examples/market_read_packet_review.example.md`: PASS
- `python3 -m unittest tests/test_detector_runtime_v1.py tests/test_calibrated_detector_runtime_v1.py tests/test_runtime_summary_review_packet.py tests/test_market_read_packet_pipeline.py`: PASS, 64 tests
- `python3 -m py_compile scripts/build_market_read_packet.py src/traders_market_read/pipeline/market_read_packet.py`: PASS

## Test Results

- Pipeline generates runtime output, summary JSON, and review Markdown.
- Runtime output contains 110 detector outputs.
- Summary JSON reports 110 contracts and 110 outputs.
- Review Markdown contains the non-execution boundary section.
- Pipeline works with calibration profile and reports 27 calibrated non-refusal outputs.
- Pipeline works without calibration profile and safely refuses 27 calibrated contracts.
- Pipeline fails on malformed input JSON.
- Pipeline fails when runtime output validation would fail.
- Generated artifacts contain no forbidden execution field keys.
- CLI writes all requested outputs.

## Boundary Confirmation

- No new detector logic was created.
- No new calibration values were created.
- No trade permission was created.
- No entries/stops/targets/sizing were created.
- No broker/order/account/fill/P&L behavior was created.

## Remaining Blockers

None.

## Operator Usage

```bash
python3 scripts/build_market_read_packet.py qa/examples/detector_runtime_calibrated_input.example.json --calibration-profile qa/examples/detector_runtime_calibrated_profile.example.yaml --runtime-output qa/examples/market_read_packet_runtime_output.example.json --summary-json qa/examples/market_read_packet_summary.example.json --review-md qa/examples/market_read_packet_review.example.md
```
