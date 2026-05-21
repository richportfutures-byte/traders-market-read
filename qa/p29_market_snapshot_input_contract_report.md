# P29 Market Snapshot Input Contract Report

## Result

P29_PASS

## Files Created/Changed

- `spec/market_snapshot_input_schema.yaml`
- `src/traders_market_read/input/__init__.py`
- `src/traders_market_read/input/market_snapshot.py`
- `scripts/validate_market_snapshot_input.py`
- `qa/input_requirements_manifest.csv`
- `qa/examples/market_snapshot_invalid_execution.example.json`
- `qa/examples/market_snapshot_missing_context.example.json`
- `qa/p29_market_snapshot_input_contract_report.md`
- `tests/test_market_snapshot_input_contract.py`
- `scripts/run_detector_runtime.py`
- `scripts/build_market_read_packet.py`
- `src/traders_market_read/pipeline/market_read_packet.py`
- `README.md`

## Input Contract Artifacts

- Input schema path: `spec/market_snapshot_input_schema.yaml`
- Input validator path: `src/traders_market_read/input/market_snapshot.py`
- CLI validator path: `scripts/validate_market_snapshot_input.py`
- Input requirements manifest path: `qa/input_requirements_manifest.csv`

## Fixture Validation Results

- Valid fixture: `qa/examples/detector_runtime_calibrated_input.example.json` PASS
- Invalid execution fixture: `qa/examples/market_snapshot_invalid_execution.example.json` expected failure, rejected forbidden field `entry_price`
- Missing context fixture: `qa/examples/market_snapshot_missing_context.example.json` expected failure, rejected missing `market_context`

## Runtime Integration Result

- `scripts/run_detector_runtime.py` now validates and normalizes market snapshot input before detector runtime execution.
- Invalid execution-field input fails before runtime output is written.

## Packet Pipeline Integration Result

- `src/traders_market_read/pipeline/market_read_packet.py` now validates and normalizes market snapshot input before detector runtime execution.
- `scripts/build_market_read_packet.py` validates input before invoking the packet build.
- Existing calibrated packet pipeline still succeeds and produces 110 validated outputs.

## Validation Results

- `python3 scripts/validate_detection_specs.py`: PASS
- `python3 scripts/build_detector_contract_catalog.py`: PASS
- `python3 scripts/validate_market_snapshot_input.py qa/examples/detector_runtime_calibrated_input.example.json`: PASS
- `python3 scripts/validate_market_snapshot_input.py qa/examples/market_snapshot_invalid_execution.example.json`: expected failure
- `python3 scripts/validate_market_snapshot_input.py qa/examples/market_snapshot_missing_context.example.json`: expected failure
- `python3 scripts/build_market_read_packet.py qa/examples/detector_runtime_calibrated_input.example.json --calibration-profile qa/examples/detector_runtime_calibrated_profile.example.yaml --runtime-output qa/examples/market_read_packet_runtime_output.example.json --summary-json qa/examples/market_read_packet_summary.example.json --review-md qa/examples/market_read_packet_review.example.md`: PASS
- `python3 scripts/validate_detector_output.py qa/examples/market_read_packet_runtime_output.example.json`: PASS
- `python3 -m unittest tests/test_detector_runtime_v1.py tests/test_calibrated_detector_runtime_v1.py tests/test_runtime_summary_review_packet.py tests/test_market_read_packet_pipeline.py tests/test_market_snapshot_input_contract.py`: PASS, 76 tests
- `python3 -m py_compile scripts/validate_market_snapshot_input.py src/traders_market_read/input/market_snapshot.py`: PASS

## Test Results

- Valid calibrated input fixture passes validation.
- Valid P25 input fixture passes validation via legacy normalization.
- Invalid execution-field fixture fails validation.
- Missing market context fixture fails validation.
- Malformed JSON fails validation.
- Unknown detector input key fails validation unless it is an explicitly allowed shared fixture block.
- Runtime CLI rejects invalid execution-field input before producing output.
- Packet pipeline rejects invalid execution-field input before producing output.
- Input validation does not require every detector concept block to exist.
- Existing packet pipeline still succeeds with the valid calibrated fixture.
- Input requirements manifest exists and contains COMPUTABLE and CALIBRATED rows.
- Validation path creates no detector logic, calibration values, or execution behavior.

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
python3 scripts/validate_market_snapshot_input.py qa/examples/detector_runtime_calibrated_input.example.json
```
