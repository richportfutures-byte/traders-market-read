# P23 Detector Output Contract Report

## Result

P23_PASS

## Files Created

- `spec/detector_output_schema.yaml`
- `scripts/validate_detector_output.py`
- `qa/examples/detector_output_valid.example.json`
- `qa/examples/detector_output_invalid_execution.example.json`
- `qa/p23_detector_output_contract_report.md`

## Validation Results

Command:

```bash
python3 scripts/validate_detection_specs.py
```

Result: PASS

- Registry concept count: 110
- Spec file count: 110
- Unique spec concept_id count: 110
- Missing count: 0
- Duplicate count: 0
- Extra count: 0

Command:

```bash
python3 scripts/build_detector_contract_catalog.py
```

Result: PASS

- Total specs: 110
- Specs with parameters: 102
- Specs with required inputs: 110
- Specs with refusal behavior: 110
- Determinism-class breakdown:
  - CALIBRATED: 27
  - COMPUTABLE: 9
  - CONTEXT_ONLY: 7
  - JUDGMENT_ASSISTED: 64
  - NOT_DETECTABLE_WITH_CURRENT_FEEDS: 3

Command:

```bash
python3 scripts/validate_detector_output.py qa/examples/detector_output_valid.example.json
```

Result: PASS

Command:

```bash
python3 scripts/validate_detector_output.py qa/examples/detector_output_invalid_execution.example.json
```

Result: FAILED as expected

- Failure reason: forbidden execution field present at `$.evidence.execution_leak.entry_price`

Command:

```bash
python3 -m py_compile scripts/validate_detector_output.py
```

Result: PASS

## Boundary Confirmation

- No detector logic was implemented.
- No calibration values were created.
- No calibration profiles were created.
- No trade permission, entries, stops, targets, sizing, broker/order/account/fill/P&L behavior, or autonomous trading instructions were created.

## Remaining Blockers

None.
