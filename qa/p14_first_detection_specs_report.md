# P14 First Detection Specs Report

Mission ID: TMR-P14-FIRST-DETECTION-SPECS
Date: 2026-05-21
Scope: Create the first bounded wave of individual detection spec YAML files under `spec/detection_specs/`.

## Executive Result

- **Overall result: P14_PASS_WITH_NOTES.**
- **Number of specs created:** 5.
- **Spec files created:**
  - `spec/detection_specs/ch02_structural_reference_levels.yaml`
  - `spec/detection_specs/ch03_initial_balance.yaml`
  - `spec/detection_specs/ch03_vwap_relationship.yaml`
  - `spec/detection_specs/ch03_value_area_vah_val_poc.yaml`
  - `spec/detection_specs/ch02_acceptance_vs_rejection.yaml`
- **Concepts skipped:** None. All five default-preference candidates were specifiable from approved doctrine.
- **Schema compliance:** Yes — every spec carries all 25 required schema fields, a registry-matching `concept_id`, and an approved `determinism_class`.
- **Calibration deferred:** Yes. The one calibrated spec (Acceptance vs. Rejection) names every parameter with `value: null` and `status: calibration_required`; no parameter values were invented.
- **Doctrine gaps blocking a candidate:** None.
- **Note (single):** The contract's `spec_content_requirements` specified `review_status: DRAFT_P14_FIRST_SPEC`, but `spec/detection_spec_schema.yaml` defines `review_status` as an enum whose only allowed values are `DRAFT`, `REVIEW_REQUIRED`, `APPROVED_FOR_SPEC_REVIEW`, `BLOCKED_BY_FEEDS`, and `DEPRECATED`. Because the contract's primary requirement is that every spec comply with the schema, each spec uses the schema-valid value `review_status: DRAFT`, and the P14 first-wave provenance is recorded in every spec's `notes` field. This is the only reason the result is `P14_PASS_WITH_NOTES` rather than `P14_PASS`; it is a token-value reconciliation, not a substantive defect.

## Method

**Files read.** `PROJECT_PROTOCOL.md`; `spec/detection_spec_schema.yaml`; `spec/concept_registry.yaml` (registry entries for the five selected concepts); `qa/p13_detection_spec_foundation_report.md`; `qa/p12_determinism_triage_report.md`; `qa/concept_determinism_matrix.csv`. The glossary source sections for the five selected concepts (`glossary/chapter_02_level_interaction_acceptance.md` and `glossary/chapter_03_auction_market_profile.md`) were read in full, including the Detection Readiness sections authored in P12.

**How the five concepts were selected.** P13's report contains a usable "P14 First Spec Candidate Recommendation" table of ten `P14_FIRST_SPEC_CANDIDATE` concepts. The contract's default preference order — Structural Reference Levels, Value Area: VAH/VAL/POC, Initial Balance, VWAP Relationship, Acceptance vs. Rejection — is fully contained in that table, and all five registry entries carry `registry_status: READY_FOR_P14`. The set was adopted unchanged: four foundational COMPUTABLE concepts plus one CALIBRATED concept, matching P13's guidance to specify low-risk computable concepts before calibrated acceptance reads. No candidate had to be skipped.

**How semantic doctrine was translated into spec structure.** For each concept the glossary Core Concept, How Traders Identify It, and P12 Detection Readiness sections were converted into: a `semantic_source` doctrine summary; an `evidence_model` of observable categories and accepted/unsupported states; a `rule_structure` (direct computation for the COMPUTABLE specs, a calibrated state machine for Acceptance vs. Rejection); `required_inputs` / `optional_inputs` with explicit absence behavior; and `false_positive_risks` / `false_negative_risks` drawn from the glossary's stated misreads. No market logic was introduced that is not present in the source chapter.

**How false determinism was avoided.** The four COMPUTABLE specs use exact formulas and session-clock windows with no market thresholds; their only parameters are data-hygiene tolerances and method conventions, explicitly marked as such. The CALIBRATED spec exposes a fixed rule shape but every numeric threshold is a named parameter left null; it emits `INSUFFICIENT_EVIDENCE` when calibration is absent rather than substituting universal defaults. Hard data dependencies (profile data for the value area, traded volume for VWAP, TPO data adjacencies) are stated as refusal conditions, not approximated from OHLC bars.

**How calibration was deferred.** Every `calibration_parameters` entry that represents an empirical market value has `value: null` and `status: calibration_required` with a named calibration scope. Method conventions (the Initial Balance window, the 0.70 value-area coverage fraction) are recorded as conventional defaults and explicitly labelled as method definitions rather than calibrated thresholds. No calibration files were created.

**How executional outputs were prohibited.** Every spec carries the universal `non_executional_boundary` statement, an `output_labels` list limited to evidence/context/confidence/refusal labels, and the full `prohibited_outputs` list from the schema. `detection_scope.not_allowed_to_classify` explicitly excludes trade decisions, setup quality, and location quality in each spec.

## Specs Created

| Spec File | Concept ID | Concept Name | Class | Required Inputs | Calibration Needed | Output Labels | Notes |
|---|---|---|---|---|---|---|---|
| ch02_structural_reference_levels.yaml | ch02_structural_reference_levels | Structural Reference Levels | COMPUTABLE | session_clock, current_session_bars, prior_session_bars | No (definitional; one inherited convention) | OBSERVED, NOT_OBSERVED, CONTEXT_ONLY, DEGRADED_CONFIDENCE, INSUFFICIENT_EVIDENCE, REFUSE_TO_CLASSIFY | Publishes the reference lattice only; significance weighting deferred to a later judgment-assisted spec |
| ch03_initial_balance.yaml | ch03_initial_balance | Initial Balance | COMPUTABLE | session_clock, rth_session_bars | Partial — relative narrow/wide width percentiles are calibration_required | OBSERVED, PENDING, CONTEXT_ONLY, DEGRADED_CONFIDENCE, INSUFFICIENT_EVIDENCE, REFUSE_TO_CLASSIFY | IB range and extension computable; relative-width labeling needs calibration |
| ch03_vwap_relationship.yaml | ch03_vwap_relationship | VWAP Relationship | COMPUTABLE | session_clock, intraday_trade_price, intraday_traded_volume | No (data-hygiene tolerances only, left null) | OBSERVED, CONTEXT_ONLY, DEGRADED_CONFIDENCE, INSUFFICIENT_EVIDENCE, REFUSE_TO_CLASSIFY | Refuses if volume absent; no unweighted-average substitute permitted |
| ch03_value_area_vah_val_poc.yaml | ch03_value_area_vah_val_poc | Value Area: VAH / VAL / POC | COMPUTABLE | session_clock, profile_distribution | No (method conventions + one tick tolerance) | OBSERVED, CONTEXT_ONLY, DEGRADED_CONFIDENCE, INSUFFICIENT_EVIDENCE, REFUSE_TO_CLASSIFY | Hard profile-data dependency; refuses rather than approximating from OHLC bars |
| ch02_acceptance_vs_rejection.yaml | ch02_acceptance_vs_rejection | Acceptance vs. Rejection | CALIBRATED | structural_level, trade_price_sequence, session_clock | Yes — five named parameters, all value: null, status: calibration_required | PENDING, ACCEPTED_ABOVE, ACCEPTED_BELOW, REJECTED, FAILED_ACCEPTANCE, REVIEW_REQUIRED, DEGRADED_CONFIDENCE, INSUFFICIENT_EVIDENCE, REFUSE_TO_CLASSIFY | Rule shape fully specified; emits INSUFFICIENT_EVIDENCE when calibration is absent |

## Skipped Candidates

None. All five default-preference candidates were specifiable from approved doctrine without inventing market logic or thresholds.

## Boundary Review

- **No trade-permission outputs:** Confirmed. Every spec's `output_labels` is limited to evidence, context, confidence, and refusal labels; none implies tradability.
- **No entries / exits / stops / targets / sizing:** Confirmed. None appears as an output; all are listed in each spec's `prohibited_outputs`. The word "target" appears only inside `prohibited_outputs` as `target_instruction`.
- **No broker / order / account / fill / P&L behavior:** Confirmed. None appears as an output; all are listed in `prohibited_outputs`.
- **No invented thresholds:** Confirmed. COMPUTABLE specs contain no market thresholds. The CALIBRATED spec's five parameters are all `value: null`, `status: calibration_required`. Method conventions (IB window, 0.70 coverage fraction) are recorded as definitional conventions, not empirical market thresholds.
- **No calibration files:** Confirmed. `calibration/` was not created and contains nothing.
- **No glossary edits:** Confirmed. No file under `glossary/` was modified.
- **No schema or registry edits:** Confirmed. `spec/detection_spec_schema.yaml` and `spec/concept_registry.yaml` were not modified.
- **No detector implementation or test files:** Confirmed. Only the five YAML specs and this report were created.

## Deferred Work

- **Calibration values** for `ch02_acceptance_vs_rejection` (acceptance_dwell_time, level_buffer, acceptance_activity_threshold, failed_acceptance_window, rejection_return_speed) and for `ch03_initial_balance` (ib_width percentiles and lookback) — deferred to the calibration layer.
- **Detector implementation** — no executable code was written; the specs are contracts only.
- **Validation tests** — each spec lists `validation_requirements`, but no test files or fixtures were created.
- **Additional detection specs** — the remaining five `P14_FIRST_SPEC_CANDIDATE` concepts and the 90 `P15_SPEC_BACKLOG` concepts are deferred to P15 and later waves.
- **Schema refinement** — not required for P14; the one observed contract/schema mismatch (`review_status` token) was reconciled in favor of the schema and did not require editing the schema.

## Final Recommendation

**Proceed to P15 next detection-spec wave.**

Next step: specify the remaining P14-candidate concepts (Auction Acceptance vs. Rejection, One-Timeframing, RTH Open Location, Compression vs. Expansion, Inside/Outside & Narrow/Wide Range Days) and then draw from the P15 spec backlog, keeping the same schema-bounded, non-executional, calibration-deferred discipline.
