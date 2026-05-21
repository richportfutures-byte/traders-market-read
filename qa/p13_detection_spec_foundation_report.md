# P13 Detection Specification Foundation Report

## Executive Result

- **Overall result: P13_PASS.**
- **Files created:** `spec/detection_spec_schema.yaml`, `spec/concept_registry.yaml`, `qa/p13_detection_spec_foundation_report.md`.
- **Registry concept count:** 110.
- **Expected concept count from P12:** 110.
- **All P12 concepts represented:** Yes.
- **Schema ready for P14 first detection specs:** Yes.
- **Blockers remaining:** None for P14 foundation work. Individual spec logic, parameter values, calibration profiles, validation tests, and implementation code remain deferred.

## Method

Read first: `PROJECT_PROTOCOL.md`, `qa/p12_determinism_triage_report.md`, `qa/concept_determinism_matrix.csv`, `qa/p11_semantic_consistency_report.md`, and `qa/semantic_quality_checklist.md`. The registry was generated directly from `qa/concept_determinism_matrix.csv`; each row became one registry entry with a stable `chNN_` lowercase snake_case `concept_id`, exact concept name preservation, glossary path, P12 determinism class, input summaries, missing-feed behavior, calibration/judgment flags, spec-candidate flag, phase recommendation, and registry status.

The schema preserves semantic/spec separation by requiring every future spec to cite its glossary source, inherit the P12 determinism class, declare required and optional inputs, state missing-feed behavior, and carry an explicit non-executional boundary. False determinism was avoided by encoding different allowed rule shapes for COMPUTABLE, CALIBRATED, JUDGMENT_ASSISTED, CONTEXT_ONLY, and NOT_DETECTABLE_WITH_CURRENT_FEEDS concepts. Calibration was deferred by allowing parameter names and calibration scopes while prohibiting universal parameter values in foundation specs. Executional outputs were prohibited through both universal schema rules and the required `prohibited_outputs` field.

## Schema Summary

`spec/detection_spec_schema.yaml` defines required future-spec fields: `spec_id`, `concept_id`, `concept_name`, `chapter`, `determinism_class`, `semantic_source`, `purpose`, `non_executional_boundary`, `required_inputs`, `optional_inputs`, `unavailable_input_behavior`, `detection_scope`, `evidence_model`, `rule_structure`, `calibration_parameters`, `confidence_behavior`, `refusal_conditions`, `output_labels`, `false_positive_risks`, `false_negative_risks`, `failure_modes`, `validation_requirements`, `prohibited_outputs`, `review_status`, and `notes`.

For each field the schema states expected type, required status, bounded allowed values where applicable, field purpose, and the guard against false determinism, missing-feed hallucination, or executional output. It also defines class-specific rules for computable formulas, calibrated structures without universal values, judgment-assisted evidence/review specs, context-only governance specs, and feed-blocked refusal specs.

## Registry Summary

| Determinism Class | Count |
|---|---:|
| COMPUTABLE | 9 |
| CALIBRATED | 27 |
| JUDGMENT_ASSISTED | 64 |
| CONTEXT_ONLY | 7 |
| NOT_DETECTABLE_WITH_CURRENT_FEEDS | 3 |

| Spec Candidate | Count |
|---|---:|
| true | 100 |
| false | 10 |

| Recommended Spec Phase | Count |
|---|---:|
| P14_FIRST_SPEC_CANDIDATE | 10 |
| P15_SPEC_BACKLOG | 90 |
| CONTEXT_GOVERNANCE_ONLY | 7 |
| BLOCKED_BY_FEEDS | 3 |

## P14 First Spec Candidate Recommendation

| Concept ID | Concept Name | Class | Why First-Wave Candidate | Main Feed Dependencies | False-Determinism Risk |
|---|---|---|---|---|---|
| ch02_structural_reference_levels | Structural Reference Levels | COMPUTABLE | Foundational reference lattice; mostly direct session and prior-session calculations. | Session clock, session and prior-session bars | Low; profile-derived references must be omitted when profile data is unavailable. |
| ch02_acceptance_vs_rejection | Acceptance vs. Rejection | CALIBRATED | Core structural read that many later specs depend on; calibrated without inventing universal dwell values. | Structural level, trade/price sequence | Medium; dwell, buffer, and activity parameters must remain calibrated by product/session. |
| ch03_auction_acceptance_vs_rejection | Auction Acceptance vs. Rejection | CALIBRATED | Profile-level acceptance/rejection is central and can refuse cleanly when profile data is absent. | Price sequence, Market Profile / TPO / volume-at-price | Medium; must not infer auction acceptance from bars when profile evidence is required. |
| ch03_value_area_vah_val_poc | Value Area: VAH / VAL / POC | COMPUTABLE | Direct profile computation with explicit feed dependency and low interpretation load. | Market Profile / TPO / volume-at-price, session boundaries | Low; risk is feed substitution or inconsistent value-area method. |
| ch03_initial_balance | Initial Balance | COMPUTABLE | Session-clock and bar-based computation with clean refusal behavior when session data is missing. | Session clock, RTH bars | Low; risk is incorrect session definition. |
| ch03_vwap_relationship | VWAP Relationship | COMPUTABLE | Direct price-volume computation with clear prohibition on simple-average substitutes. | Intraday trade price, volume | Low; risk is replacing volume-weighted data with an unweighted proxy. |
| ch05_one_timeframing | One-Timeframing | COMPUTABLE | Low-risk bar-sequence state useful across momentum and session context specs. | Clean period bars, defined session/timeframe | Low; risk is dirty bars or inconsistent period boundaries. |
| ch07_rth_open_location | RTH Open Location | COMPUTABLE | Session-location classifier grounded in observable open, overnight, range, and value references. | Session clock, RTH open price, overnight high/low, prior value/range references | Low to medium; value-based labels must degrade when value data is missing. |
| ch08_compression_vs_expansion | Compression vs. Expansion | CALIBRATED | Foundational volatility-regime classifier with calibratable parameters and broad downstream use. | Price bars, range statistics, session range, realized volatility, value behavior | Medium; range/volatility baselines require calibration and should avoid universal thresholds. |
| ch08_inside_outside_and_narrow_wide_range_days | Inside/Outside & Narrow/Wide Range Days | COMPUTABLE | Clean session-range classification with simple feed requirements and bounded output labels. | Session high/low data, clean session definitions | Low; narrow/wide labels need calibrated historical context if used beyond raw inside/outside state. |

## Deferred Work

- Individual detection specs are deferred; no files under `spec/detection_specs/` were created.
- Detection logic details beyond the foundation schema are deferred to P14 and later per-concept spec missions.
- Parameter values are deferred; P13 names calibration requirements but does not set thresholds.
- Calibration profiles are deferred to the calibration layer.
- Validation tests are deferred.
- Implementation code and detectors are deferred.

## Final Recommendation

Proceed to P14 first detection specs.

Next step: create the first P14 detection specs from the P14 first-wave candidate set, starting with low-risk foundational COMPUTABLE concepts before calibrated acceptance or volatility reads.
