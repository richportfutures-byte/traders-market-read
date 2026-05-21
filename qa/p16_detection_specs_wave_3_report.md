# P16 Detection Specs Wave 3 Report

## Executive Result

- **Result: P16_PASS.**
- **Detection-spec count before and after:** 10 before; 30 after.
- **New specs in this pass:** 20.
- **Replacements made:** None. All 20 primary targets resolved cleanly, were unimplemented, and could be specified without invented doctrine.
- **Schema/YAML validation result:** Passed. PyYAML parsed all 30 detection specs successfully.
- **Registry alignment result:** Passed. All 20 new concept IDs, chapters, glossary paths, and determinism classes match `spec/concept_registry.yaml` and `qa/concept_determinism_matrix.csv`.
- **Duplicate concept_id check result:** Passed. All 30 specs have unique `concept_id` values.
- **Forbidden-output check result:** Passed. Targeted forbidden execution-language scan returned no hits, and every new spec includes `prohibited_outputs` and `forbidden_outputs`.
- **Concepts requiring GPT-5.5 doctrine review:** None identified.
- **Remaining blockers:** None.

## Files Created

- `spec/detection_specs/ch02_breakout_continuation_vs_breakout_failure.yaml`
- `spec/detection_specs/ch02_liquidity_sweep_vs_real_break.yaml`
- `spec/detection_specs/ch02_level_test_sequence.yaml`
- `spec/detection_specs/ch02_polarity_flip.yaml`
- `spec/detection_specs/ch03_excess_vs_poor_highs_lows.yaml`
- `spec/detection_specs/ch03_price_outside_value_acceptance_test.yaml`
- `spec/detection_specs/ch03_value_migration_and_overlap.yaml`
- `spec/detection_specs/ch03_single_prints.yaml`
- `spec/detection_specs/ch05_close_quality.yaml`
- `spec/detection_specs/ch05_day_type_taxonomy.yaml`
- `spec/detection_specs/ch04_absorption.yaml`
- `spec/detection_specs/ch04_refreshing_liquidity.yaml`
- `spec/detection_specs/ch04_chasing_vs_pressing.yaml`
- `spec/detection_specs/ch04_stall_and_snap_back.yaml`
- `spec/detection_specs/ch04_tape_quality_spectrum.yaml`
- `spec/detection_specs/ch04_spread_behavior.yaml`
- `spec/detection_specs/ch04_liquidity_pulls_and_replenishment.yaml`
- `spec/detection_specs/ch04_sweeps_through_liquidity.yaml`
- `spec/detection_specs/ch04_cumulative_delta_and_delta_divergence.yaml`
- `spec/detection_specs/ch05_impulse_vs_grind.yaml`

## Concepts Covered

| Concept | Concept ID | Determinism Class | Spec File | Emitted-State Summary |
|---|---|---|---|---|
| Breakout Continuation vs. Breakout Failure | `ch02_breakout_continuation_vs_breakout_failure` | CALIBRATED | `spec/detection_specs/ch02_breakout_continuation_vs_breakout_failure.yaml` | BREAKOUT_PENDING, BREAKOUT_CONTINUATION, BREAKOUT_RETEST_HELD, BREAKOUT_FAILURE, STRUCTURAL_FOLLOW_THROUGH_ONLY |
| Liquidity Sweep vs. Real Break | `ch02_liquidity_sweep_vs_real_break` | CALIBRATED | `spec/detection_specs/ch02_liquidity_sweep_vs_real_break.yaml` | SWEEP_RESOLUTION_PENDING, SWEEP_RECLAIMED_FALSE_BREAK, SWEEP_HELD_REAL_BREAK_CONTEXT, STRUCTURAL_SWEEP_ONLY, MOTIVE_NOT_DETECTABLE |
| Level Test Sequence | `ch02_level_test_sequence` | CALIBRATED | `spec/detection_specs/ch02_level_test_sequence.yaml` | TEST_COUNT_OBSERVED, FIRST_TEST_CONTEXT, REPEATED_TEST_DECAY, LEVEL_EXHAUSTION_REVIEW, REACTION_SUPPORTED |
| Polarity Flip | `ch02_polarity_flip` | CALIBRATED | `spec/detection_specs/ch02_polarity_flip.yaml` | RETEST_PENDING, POLARITY_FLIP_CONFIRMED, POLARITY_FLIP_FAILED, RECLAIM_CONFIRMED, LOSS_CONFIRMED |
| Excess vs. Poor Highs/Lows | `ch03_excess_vs_poor_highs_lows` | CALIBRATED | `spec/detection_specs/ch03_excess_vs_poor_highs_lows.yaml` | EXCESS_HIGH, EXCESS_LOW, POOR_HIGH, POOR_LOW, PROFILE_EXTREME_PENDING |
| Price Outside Value / Acceptance Test | `ch03_price_outside_value_acceptance_test` | CALIBRATED | `spec/detection_specs/ch03_price_outside_value_acceptance_test.yaml` | OUTSIDE_VALUE_PENDING, OUTSIDE_VALUE_ACCEPTED, OUTSIDE_VALUE_REJECTED, RETURNED_INSIDE_VALUE, VALUE_ACCEPTANCE_TEST_ONLY |
| Value Migration & Overlap | `ch03_value_migration_and_overlap` | COMPUTABLE | `spec/detection_specs/ch03_value_migration_and_overlap.yaml` | VALUE_MIGRATING_HIGHER, VALUE_MIGRATING_LOWER, VALUE_OVERLAPPING, VALUE_NON_MIGRATION, VALUE_REFERENCE_MISSING |
| Single Prints | `ch03_single_prints` | COMPUTABLE | `spec/detection_specs/ch03_single_prints.yaml` | SINGLE_PRINTS_PRESENT, SINGLE_PRINTS_ABSENT, SINGLE_PRINTS_HOLDING, SINGLE_PRINTS_FILLED, PROFILE_POSITION_CONTEXT_REQUIRED |
| Close Quality | `ch05_close_quality` | JUDGMENT_ASSISTED | `spec/detection_specs/ch05_close_quality.yaml` | STRONG_CLOSE_CONTEXT, WEAK_CLOSE_CONTEXT, ACCEPTED_CLOSE, FAILED_CLOSE, LATE_REPAIR_CLOSE |
| Day-Type Taxonomy | `ch05_day_type_taxonomy` | JUDGMENT_ASSISTED | `spec/detection_specs/ch05_day_type_taxonomy.yaml` | DAY_TYPE_CANDIDATE_TREND, DAY_TYPE_CANDIDATE_ROTATIONAL, DAY_TYPE_CANDIDATE_NEUTRAL, DAY_TYPE_CANDIDATE_DOUBLE_DISTRIBUTION, DAY_TYPE_CANDIDATE_NORMAL |
| Absorption | `ch04_absorption` | JUDGMENT_ASSISTED | `spec/detection_specs/ch04_absorption.yaml` | EFFORT_WITHOUT_RESULT_OBSERVED, ABSORPTION_EVIDENCE_PRESENT, ABSORPTION_REVIEW_REQUIRED, LOW_CONFIDENCE_STRUCTURAL_STALL, NOT_DETECTABLE_WITH_CURRENT_FEEDS |
| Refreshing Liquidity | `ch04_refreshing_liquidity` | NOT_DETECTABLE_WITH_CURRENT_FEEDS | `spec/detection_specs/ch04_refreshing_liquidity.yaml` | BLOCKED_BY_FEEDS, DEPTH_RELOAD_EVIDENCE_REQUIRED, RELATED_ABSORPTION_CONTEXT_ONLY, INSUFFICIENT_EVIDENCE, REFUSE_TO_CLASSIFY |
| Chasing vs. Pressing | `ch04_chasing_vs_pressing` | JUDGMENT_ASSISTED | `spec/detection_specs/ch04_chasing_vs_pressing.yaml` | CHASE_EVIDENCE_PRESENT, PRESSING_EVIDENCE_PRESENT, VACUUM_OR_THIN_TRAVEL_RISK, PARTICIPATION_QUALITY_REVIEW, STRUCTURAL_CONTEXT_ONLY |
| Stall & Snap-Back | `ch04_stall_and_snap_back` | CALIBRATED | `spec/detection_specs/ch04_stall_and_snap_back.yaml` | STALL_OBSERVED, SNAP_BACK_CONFIRMED, STALL_PENDING, STALL_WITH_ABSORPTION_CONTEXT, STRUCTURAL_STALL_ONLY |
| Tape Quality Spectrum | `ch04_tape_quality_spectrum` | CALIBRATED | `spec/detection_specs/ch04_tape_quality_spectrum.yaml` | TAPE_CLEAN, TAPE_NOISY, TAPE_THIN, TAPE_WIDE, TAPE_FAST |
| Spread Behavior | `ch04_spread_behavior` | CALIBRATED | `spec/detection_specs/ch04_spread_behavior.yaml` | SPREAD_STABLE, SPREAD_WIDENING, SPREAD_NORMALIZING, SPREAD_UNSTABLE, SPREAD_BLOCKED |
| Liquidity Pulls & Replenishment | `ch04_liquidity_pulls_and_replenishment` | NOT_DETECTABLE_WITH_CURRENT_FEEDS | `spec/detection_specs/ch04_liquidity_pulls_and_replenishment.yaml` | BLOCKED_BY_FEEDS, DEPTH_PULL_EVIDENCE_REQUIRED, DEPTH_REPLENISHMENT_EVIDENCE_REQUIRED, AIR_POCKET_CONTEXT_ONLY, INSUFFICIENT_EVIDENCE |
| Sweeps Through Liquidity | `ch04_sweeps_through_liquidity` | CALIBRATED | `spec/detection_specs/ch04_sweeps_through_liquidity.yaml` | SWEEP_DETECTED, POST_SWEEP_ABSORPTION, POST_SWEEP_CONTINUATION, SWEEP_RESOLUTION_PENDING, COARSE_PRICE_SPIKE_CONTEXT |
| Cumulative Delta & Delta Divergence | `ch04_cumulative_delta_and_delta_divergence` | JUDGMENT_ASSISTED | `spec/detection_specs/ch04_cumulative_delta_and_delta_divergence.yaml` | DELTA_CONFIRMATION, DELTA_DIVERGENCE, DELTA_FAILURE_EFFORT_WITHOUT_RESULT, LOCATION_REQUIRED, TRADE_CLASSIFICATION_REQUIRED |
| Impulse vs. Grind | `ch05_impulse_vs_grind` | CALIBRATED | `spec/detection_specs/ch05_impulse_vs_grind.yaml` | IMPULSE_MOVE, GRIND_MOVE, VERTICAL_OR_PARABOLIC_MOVE, DRIFT_NOT_GRIND, TEXTURE_PENDING |

## Replacements

None. The primary target list produced exactly 20 viable unimplemented concepts.

## Class Mix

| Determinism Class | Count |
|---|---:|
| COMPUTABLE | 2 |
| CALIBRATED | 11 |
| JUDGMENT_ASSISTED | 5 |
| CONTEXT_ONLY | 0 |
| NOT_DETECTABLE_WITH_CURRENT_FEEDS | 2 |

## Calibration-Boundary Notes

- CALIBRATED specs define rule structure and named parameters only; all empirical calibration values are `null`.
- COMPUTABLE specs emit structural/profile/session states only and keep interpretation separate.
- JUDGMENT_ASSISTED specs emit bounded evidence, review, downgrade, and refusal states rather than deterministic conclusions.
- NOT_DETECTABLE_WITH_CURRENT_FEEDS specs are explicit refusal contracts naming required external feeds; they do not proxy unavailable order-book phenomena from bars.
- No calibration files or detector implementation code were created.

## Missing-Feed Or Downgrade Behavior Summary

| Concept ID | Missing Required Feed Behavior | Optional Feed Downgrade Behavior |
|---|---|---|
| `ch02_breakout_continuation_vs_breakout_failure` | REFUSE_TO_CLASSIFY for missing required feeds; INSUFFICIENT_EVIDENCE when calibration is absent | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch02_liquidity_sweep_vs_real_break` | REFUSE_TO_CLASSIFY for missing required feeds; INSUFFICIENT_EVIDENCE when calibration is absent | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch02_level_test_sequence` | REFUSE_TO_CLASSIFY for missing required feeds; INSUFFICIENT_EVIDENCE when calibration is absent | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch02_polarity_flip` | REFUSE_TO_CLASSIFY for missing required feeds; INSUFFICIENT_EVIDENCE when calibration is absent | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch03_excess_vs_poor_highs_lows` | REFUSE_TO_CLASSIFY for missing required feeds; INSUFFICIENT_EVIDENCE when calibration is absent | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch03_price_outside_value_acceptance_test` | REFUSE_TO_CLASSIFY for missing required feeds; INSUFFICIENT_EVIDENCE when calibration is absent | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch03_value_migration_and_overlap` | REFUSE_TO_CLASSIFY or INSUFFICIENT_EVIDENCE for missing required feeds | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch03_single_prints` | REFUSE_TO_CLASSIFY or INSUFFICIENT_EVIDENCE for missing required feeds | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch05_close_quality` | REFUSE_TO_CLASSIFY or INSUFFICIENT_EVIDENCE for missing required feeds | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch05_day_type_taxonomy` | REFUSE_TO_CLASSIFY or INSUFFICIENT_EVIDENCE for missing required feeds | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch04_absorption` | REFUSE_TO_CLASSIFY or INSUFFICIENT_EVIDENCE for missing required feeds | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch04_refreshing_liquidity` | BLOCKED_BY_FEEDS / REFUSE_TO_CLASSIFY until required external depth/order-book feeds exist | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch04_chasing_vs_pressing` | REFUSE_TO_CLASSIFY or INSUFFICIENT_EVIDENCE for missing required feeds | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch04_stall_and_snap_back` | REFUSE_TO_CLASSIFY for missing required feeds; INSUFFICIENT_EVIDENCE when calibration is absent | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch04_tape_quality_spectrum` | REFUSE_TO_CLASSIFY for missing required feeds; INSUFFICIENT_EVIDENCE when calibration is absent | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch04_spread_behavior` | REFUSE_TO_CLASSIFY for missing required feeds; INSUFFICIENT_EVIDENCE when calibration is absent | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch04_liquidity_pulls_and_replenishment` | BLOCKED_BY_FEEDS / REFUSE_TO_CLASSIFY until required external depth/order-book feeds exist | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch04_sweeps_through_liquidity` | REFUSE_TO_CLASSIFY for missing required feeds; INSUFFICIENT_EVIDENCE when calibration is absent | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch04_cumulative_delta_and_delta_divergence` | REFUSE_TO_CLASSIFY or INSUFFICIENT_EVIDENCE for missing required feeds | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |
| `ch05_impulse_vs_grind` | REFUSE_TO_CLASSIFY for missing required feeds; INSUFFICIENT_EVIDENCE when calibration is absent | Missing optional feeds produce DEGRADED_CONFIDENCE, CONTEXT_ONLY, or REVIEW_REQUIRED rather than proxy classification |

## Verification Results

- Confirmed total detection spec count is 30.
- Confirmed exactly 20 P16 YAML files were created.
- Confirmed all spec YAML files parse successfully.
- Confirmed every new `concept_id` exists in the registry.
- Confirmed all `concept_id` values are unique across `spec/detection_specs/`.
- Confirmed every new `determinism_class` matches registry and matrix.
- Confirmed every new `review_status` is schema-allowed.
- Confirmed every new spec contains `forbidden_outputs` and `prohibited_outputs`.
- Confirmed targeted forbidden execution-language scan returned no hits.
- Confirmed calibration-required parameters in new specs have `value: null`.
- Confirmed no calibration files were created.

## Final Recommendation

Proceed with the next bounded detection-spec wave.

Next step: continue implementing registry-backed specs while preserving calibration boundaries and using feed-blocked refusal contracts where required.
