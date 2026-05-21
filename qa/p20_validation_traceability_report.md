# P20 Validation and Traceability Report

## Result

P20_PASS_WITH_NOTES

The validation layer passed against the completed detection spec corpus: registry coverage is complete, every spec concept maps to the registry, determinism classes match registry and matrix data where available, review statuses are schema-allowed, `forbidden_outputs` is present in every spec, and no forbidden execution strings were found.

Note: this local shell has `python3` available but no `python` shim. The validator was executed with `python3` locally; the operator-facing command remains the requested `python ...` form for environments where `python` resolves to Python 3 with PyYAML.

## Files Created or Changed

- Created `scripts/validate_detection_specs.py`
- Created `qa/glossary_to_spec_traceability.csv`
- Created `qa/p20_validation_traceability_report.md`
- Updated `README.md` with a short validation command reference

No glossary chapters, protocol files, registry files, schema files, matrix files, detection specs, calibration profiles, or git history were modified.

## Validation Command Used

```bash
python3 scripts/validate_detection_specs.py --traceability-csv qa/glossary_to_spec_traceability.csv
```

Output summary:

```text
P20 validation PASS
registry concept count: 110
spec file count: 110
unique spec concept_id count: 110
missing count: 0
duplicate count: 0
extra count: 0
traceability csv: wrote 110 rows to qa/glossary_to_spec_traceability.csv
```

## Counts

| Measure | Count |
|---|---:|
| Registry concept count | 110 |
| Detection spec count | 110 |
| Unique spec concept_id count | 110 |
| Missing count | 0 |
| Duplicate count | 0 |
| Extra count | 0 |
| Traceability CSV row count | 110 |

## Repaired Defects

None. Validation did not identify a blocking spec defect, so no detection specs were changed.

## Remaining Blockers

None for P20 validation and traceability.

## Operator Usage

Validate the detection specs:

```bash
python3 scripts/validate_detection_specs.py
```

Regenerate the traceability CSV:

```bash
python3 scripts/validate_detection_specs.py --traceability-csv qa/glossary_to_spec_traceability.csv
```

The script uses only the Python standard library plus PyYAML. It does not require, read, generate, or modify calibration profiles.
