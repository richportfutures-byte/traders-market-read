# P21 Calibration Contract Report

## Result

P21_PASS_WITH_NOTES

## Files Created or Changed

- `calibration/calibration_profile_schema.yaml`
- `qa/calibration_parameter_inventory.csv`
- `scripts/extract_calibration_inventory.py`
- `qa/p21_calibration_contract_report.md`
- `README.md`

## Detection Spec Validation Result

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

## Traceability Regeneration Result

Command:

```bash
python3 scripts/validate_detection_specs.py --traceability-csv qa/glossary_to_spec_traceability.csv
```

Result: PASS

- Registry concept count: 110
- Spec file count: 110
- Unique spec concept_id count: 110
- Missing count: 0
- Duplicate count: 0
- Extra count: 0
- Traceability CSV rows written: 110

## Calibration Inventory Extraction Result

Command:

```bash
python3 scripts/extract_calibration_inventory.py
```

Result: PASS

- Specs scanned: 110
- Specs with parameters: 100
- Parameter rows written: 291
- Determinism-class breakdown:
  - CALIBRATED: 114
  - COMPUTABLE: 29
  - JUDGMENT_ASSISTED: 148

## Coverage Notes

The inventory is generated from named `calibration_parameters` entries in detection specs. It includes:

- CALIBRATED spec parameters.
- JUDGMENT_ASSISTED named calibration or review-rule parameters.
- COMPUTABLE named configuration, convention, external-definition, or calibration parameters.

The inventory excludes explicit `not_applicable` placeholder rows and feed-blocked `NOT_DETECTABLE_WITH_CURRENT_FEEDS` requirements, because those do not represent usable calibration parameters under the current feed boundary.

## Calibration Boundary Confirmations

- No calibration values were created in P21.
- No numeric thresholds were assigned in P21.
- No default instrument, session, timeframe, or regime parameter values were created in P21.
- No instrument calibration profiles were created in P21.
- No ES, NQ, CL, 6E, or MGC parameter values were created in P21.
- No trade permission, entries, stops, targets, sizing, broker/order/account/fill/P&L fields, or autonomous trading behavior were created.

## Remaining Blockers

None.

## Operator Usage

```bash
python3 scripts/extract_calibration_inventory.py
python3 scripts/validate_detection_specs.py
python3 scripts/validate_detection_specs.py --traceability-csv qa/glossary_to_spec_traceability.csv
```
