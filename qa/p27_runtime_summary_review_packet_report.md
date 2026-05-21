# P27 Runtime Summary and Review Packet Report

## Result

P27_PASS

## Files Created/Changed

- `src/traders_market_read/reporting/__init__.py`
- `src/traders_market_read/reporting/runtime_summary.py`
- `scripts/summarize_detector_runtime.py`
- `qa/examples/detector_runtime_summary.example.json`
- `qa/examples/detector_runtime_review_packet.example.md`
- `qa/p27_runtime_summary_review_packet_report.md`
- `tests/test_runtime_summary_review_packet.py`
- `README.md`

## Runtime Artifacts

- Input runtime output used: `qa/examples/detector_runtime_calibrated_output.example.json`
- Summary JSON path: `qa/examples/detector_runtime_summary.example.json`
- Review packet path: `qa/examples/detector_runtime_review_packet.example.md`

## Summary Counts

- Total contracts: 110
- Total outputs: 110
- Counts by determinism class:
  - CALIBRATED: 27
  - COMPUTABLE: 9
  - CONTEXT_ONLY: 7
  - JUDGMENT_ASSISTED: 64
  - NOT_DETECTABLE_WITH_CURRENT_FEEDS: 3
- Counts by route:
  - calibrated: 27
  - computable: 9
  - context_only: 7
  - judgment_assisted_review: 64
  - not_detectable_blocked: 3
- Refusal count: 64
- Non-refusal count: 46
- JUDGMENT_ASSISTED review queue count: 64
- Blocked-by-feed count: 3

## Validation Results

- `python3 scripts/validate_detection_specs.py`: PASS
- `python3 scripts/build_detector_contract_catalog.py`: PASS
- `python3 scripts/run_detector_runtime.py qa/examples/detector_runtime_calibrated_input.example.json --calibration-profile qa/examples/detector_runtime_calibrated_profile.example.yaml --output qa/examples/detector_runtime_calibrated_output.example.json`: PASS
- `python3 scripts/validate_detector_output.py qa/examples/detector_runtime_calibrated_output.example.json`: PASS
- `python3 scripts/summarize_detector_runtime.py qa/examples/detector_runtime_calibrated_output.example.json --summary-json qa/examples/detector_runtime_summary.example.json --review-md qa/examples/detector_runtime_review_packet.example.md`: PASS
- `python3 -m unittest tests/test_detector_runtime_v1.py tests/test_calibrated_detector_runtime_v1.py tests/test_runtime_summary_review_packet.py`: PASS, 54 tests
- `python3 -m py_compile scripts/summarize_detector_runtime.py src/traders_market_read/reporting/runtime_summary.py`: PASS

## Test Results

- Summary loads calibrated runtime output.
- Summary includes all 110 contracts.
- Duplicate output `concept_id` fails closed.
- Missing output `concept_id` fails closed.
- Forbidden execution fields fail closed recursively.
- Missing or false guardrail booleans fail closed.
- COMPUTABLE and CALIBRATED non-refusal counts are verified.
- JUDGMENT_ASSISTED review/refusal count is verified.
- Review packet Markdown generation is verified.
- Review packet boundary language is verified.
- Review packet does not include forbidden execution field keys.
- CLI writes both summary JSON and review Markdown.

## Boundary Confirmation

- No trade permission was created.
- No entries/stops/targets/sizing were created.
- No broker/order/account/fill/P&L behavior was created.
- No new detector logic was created.
- No new calibration values were created.

## Remaining Blockers

None.

## Operator Usage

```bash
python3 scripts/summarize_detector_runtime.py qa/examples/detector_runtime_calibrated_output.example.json --summary-json qa/examples/detector_runtime_summary.example.json --review-md qa/examples/detector_runtime_review_packet.example.md
```
