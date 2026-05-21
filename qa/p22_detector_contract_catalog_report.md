# P22 Detector Contract Catalog Report

## Result

P22_PASS_WITH_NOTES

## Files Created or Changed

- `scripts/build_detector_contract_catalog.py`
- `spec/detector_contract_catalog.json`
- `qa/detector_contract_catalog_summary.md`
- `qa/p22_detector_contract_catalog_report.md`
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

## Catalog Generation Result

Command:

```bash
python3 scripts/build_detector_contract_catalog.py
```

Result: PASS

- Total detector contracts: 110
- Specs with parameters: 102
- Specs with required inputs: 110
- Specs with refusal behavior: 110

## Counts by Determinism Class

- CALIBRATED: 27
- COMPUTABLE: 9
- CONTEXT_ONLY: 7
- JUDGMENT_ASSISTED: 64
- NOT_DETECTABLE_WITH_CURRENT_FEEDS: 3

## Counts by Chapter

- 1: Read Discipline & Interpretation Method: 8
- 2: Level Interaction & Acceptance: 9
- 3: Auction & Market Profile: 15
- 4: Tape Reading & Microstructure: 10
- 5: Momentum, Follow-Through & Day Types: 7
- 6: Traps & Positioning: 7
- 7: Session Context & Sequencing: 8
- 8: Volatility Regime: 8
- 9: Intermarket Confirmation: 13
- 10: Catalyst Interpretation: 7
- 11: Trade-State Management: 9
- 12: Setup Quality & Action Vocabulary: 9

## Boundary Confirmations

- No detector logic was implemented.
- No calibration values were created.
- No instrument calibration profiles were created.
- No trade permission, entries, stops, targets, sizing, broker/order/account/fill/P&L behavior, or autonomous trading instructions were created.
- Parameter `value` fields from source specs are not carried into the normalized catalog `parameters` objects.

## Notes

Five existing specs declare emitted labels through `output_labels` without a separate `states_emitted` field. The catalog preserves those spec-declared labels in `states_emitted` without changing the specs.

## Remaining Blockers

None.

## Operator Usage

```bash
python3 scripts/validate_detection_specs.py
python3 scripts/extract_calibration_inventory.py
python3 scripts/build_detector_contract_catalog.py
```
