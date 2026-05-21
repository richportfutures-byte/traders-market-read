# P17 Detection Specs Wave 4 Report

## Result

P17_PASS

## Files Created

- `spec/detection_specs/ch05_momentum_ignition_stall_and_exhaustion.yaml`
- `spec/detection_specs/ch05_follow_through_and_failure.yaml`
- `spec/detection_specs/ch08_expansion_outcomes_trend_chop_exhaustion.yaml`
- `spec/detection_specs/ch07_session_sequencing.yaml`
- `spec/detection_specs/ch07_asia_session_character.yaml`
- `spec/detection_specs/ch07_london_initiative_and_traps.yaml`
- `spec/detection_specs/ch07_intraday_time_windows.yaml`
- `spec/detection_specs/ch03_overnight_inventory_and_inventory_correction.yaml`
- `spec/detection_specs/ch03_volume_nodes_and_air_pockets.yaml`
- `spec/detection_specs/ch03_completed_failed_and_unfinished_auctions.yaml`
- `spec/detection_specs/ch03_initiative_vs_responsive_activity.yaml`
- `spec/detection_specs/ch03_short_covering_vs_long_liquidation_auctions.yaml`
- `spec/detection_specs/ch03_fresh_flow_vs_weak_strong_hands.yaml`
- `spec/detection_specs/ch06_trapped_traders.yaml`
- `spec/detection_specs/ch06_strong_hands_defending.yaml`
- `spec/detection_specs/ch06_stop_out_cascades_and_liquidation.yaml`
- `spec/detection_specs/ch06_short_covering_rally.yaml`
- `spec/detection_specs/ch06_crowded_trades_and_pain_trades.yaml`
- `spec/detection_specs/ch08_volatility_crush_and_reset.yaml`
- `spec/detection_specs/ch08_expanded_volatility_no_trade_condition.yaml`
- `qa/p17_detection_specs_wave_4_report.md`

## Concepts Covered

| Concept | concept_id | Determinism Class | Emitted-State Summary |
|---|---|---|---|
| Momentum Ignition, Stall & Exhaustion | `ch05_momentum_ignition_stall_and_exhaustion` | JUDGMENT_ASSISTED | IGNITION_EVIDENCE_PRESENT, MOMENTUM_CONTINUATION_ATTEMPT, MOMENTUM_STALL_EVIDENCE, EXHAUSTION_REVIEW_REQUIRED |
| Follow-Through and Failure | `ch05_follow_through_and_failure` | CALIBRATED | FOLLOW_THROUGH_PENDING, FOLLOW_THROUGH_CONFIRMED, FOLLOW_THROUGH_FAILED, RETEST_HOLD_CONFIRMED |
| Expansion Outcomes (Trend / Chop / Exhaustion) | `ch08_expansion_outcomes_trend_chop_exhaustion` | JUDGMENT_ASSISTED | EXPANSION_TREND_CANDIDATE, EXPANSION_CHOP_CANDIDATE, EXPANSION_EXHAUSTION_REVIEW, FAILED_EXPANSION_CONTEXT |
| Session Sequencing | `ch07_session_sequencing` | JUDGMENT_ASSISTED | SESSION_HANDOFF_CONTEXT, SESSION_INHERITANCE_EVIDENCE, SESSION_REJECTION_EVIDENCE, INVENTORY_REPAIR_CONTEXT |
| Asia Session Character | `ch07_asia_session_character` | CALIBRATED | ASIA_MEANINGFUL_STRUCTURE, ASIA_PLACEHOLDER_RANGE, ASIA_FAKEOUT_PRONE_CONTEXT, ASIA_REPRICING_CONTEXT |
| London Initiative & Traps | `ch07_london_initiative_and_traps` | JUDGMENT_ASSISTED | LONDON_INITIATIVE_EVIDENCE, LONDON_TRAP_RISK, LONDON_EXTENSION_CONTEXT, NY_CONFIRMATION_REQUIRED |
| Intraday Time Windows | `ch07_intraday_time_windows` | JUDGMENT_ASSISTED | OPEN_WINDOW_CONTEXT, MIDDAY_DRIFT_RISK, SETTLEMENT_OR_CLOSE_FLOW_CONTEXT, POWER_HOUR_REVIEW_REQUIRED |
| Overnight Inventory & Inventory Correction | `ch03_overnight_inventory_and_inventory_correction` | JUDGMENT_ASSISTED | OVERNIGHT_LONG_INVENTORY_CONTEXT, OVERNIGHT_SHORT_INVENTORY_CONTEXT, BALANCED_OVERNIGHT_INVENTORY, INVENTORY_CORRECTION_EVIDENCE |
| Volume Nodes & Air Pockets | `ch03_volume_nodes_and_air_pockets` | CALIBRATED | HIGH_VOLUME_NODE_IDENTIFIED, LOW_VOLUME_NODE_IDENTIFIED, AIR_POCKET_CONTEXT, NODE_ACCEPTANCE_TEST |
| Completed, Failed & Unfinished Auctions | `ch03_completed_failed_and_unfinished_auctions` | CALIBRATED | COMPLETED_AUCTION, UNFINISHED_AUCTION, POOR_EXTREME_CONTEXT, FAILED_AUCTION_CONTEXT |
| Initiative vs. Responsive Activity | `ch03_initiative_vs_responsive_activity` | JUDGMENT_ASSISTED | INITIATIVE_ACTIVITY_LOCATION, RESPONSIVE_ACTIVITY_LOCATION, MIXED_ACTIVITY_CONTEXT, VALUE_EDGE_CONFIRMATION_REQUIRED |
| Short-Covering vs. Long-Liquidation Auctions | `ch03_short_covering_vs_long_liquidation_auctions` | JUDGMENT_ASSISTED | SHORT_COVERING_AUCTION_EVIDENCE, LONG_LIQUIDATION_AUCTION_EVIDENCE, FORCED_FLOW_CONTEXT, FRESH_FLOW_NOT_CONFIRMED |
| Fresh Flow vs. Weak/Strong Hands | `ch03_fresh_flow_vs_weak_strong_hands` | JUDGMENT_ASSISTED | FRESH_FLOW_EVIDENCE, WEAK_HAND_PARTICIPATION_CONTEXT, STRONG_HAND_DEFENSE_EVIDENCE, PARTICIPANT_QUALITY_PROVISIONAL |
| Trapped Traders | `ch06_trapped_traders` | JUDGMENT_ASSISTED | TRAPPED_LONGS_CONTEXT, TRAPPED_SHORTS_CONTEXT, FAILED_PREMISE_CONTEXT, FORCED_FLOW_REVIEW |
| Strong Hands Defending | `ch06_strong_hands_defending` | JUDGMENT_ASSISTED | STRONG_HAND_DEFENSE_EVIDENCE, DEFENSE_HOLDING, DEFENSE_WEAKENING, DEFENSE_FAILED |
| Stop-Out Cascades & Liquidation | `ch06_stop_out_cascades_and_liquidation` | CALIBRATED | CASCADE_LIKE_BEHAVIOR, STOP_OUT_CASCADE_EVIDENCE, LIQUIDATION_CONTEXT, FORCED_FLOW_ONLY |
| Short-Covering Rally | `ch06_short_covering_rally` | JUDGMENT_ASSISTED | SHORT_COVERING_RALLY_CONTEXT, SQUEEZE_CONTEXT, FRESH_BUYING_NOT_CONFIRMED, COVERING_EXHAUSTION_REVIEW |
| Crowded Trades & Pain Trades | `ch06_crowded_trades_and_pain_trades` | CONTEXT_ONLY | CROWDING_CONTEXT, PAIN_TRADE_RISK_CONTEXT, POSITIONING_EVIDENCE_REQUIRED, OBSERVABLE_VULNERABILITY_ONLY |
| Volatility Crush & Reset | `ch08_volatility_crush_and_reset` | CALIBRATED | REALIZED_VOLATILITY_CRUSH_CONTEXT, VOLATILITY_RESET_CONTEXT, POST_EVENT_NORMALIZATION, REALIZED_VOLATILITY_ONLY |
| Expanded-Volatility No-Trade Condition | `ch08_expanded_volatility_no_trade_condition` | CALIBRATED | EXPANDED_VOLATILITY_ENVIRONMENT_BLOCK, SPREAD_OR_DEPTH_QUALITY_BLOCK, STRUCTURAL_VOLATILITY_CAUTION, ENVIRONMENT_REVIEW_REQUIRED |

## Detection-Spec Count

- Before P17: 30
- New specs in P17: 20
- After P17: 50

## Replacements Made

- `One-Timeframing` was already implemented in P15 as `ch05_one_timeframing`, so `ch08_volatility_crush_and_reset` was selected from the calibrated replacement backlog.
- `RTH Open Location` was already implemented in P15 as `ch07_rth_open_location`, so `ch08_expanded_volatility_no_trade_condition` was selected from the calibrated replacement backlog.
- `Event Window Behavior` is not an exact registry concept. The registry-backed concept `ch07_intraday_time_windows` was used because it covers time-window/session-window behavior and preserves the requested event/window boundary without inventing a new concept.

## Schema/YAML Validation Result

Targeted validation parsed all detection spec YAML files successfully after creation. Each new spec uses `review_status: DRAFT`, includes schema-required fields, and preserves named calibration parameters without numeric values.

## Registry Alignment Result

All 20 new `concept_id` values exist in `spec/concept_registry.yaml`. Determinism classes were copied from the registry and checked against `qa/concept_determinism_matrix.csv`.

## Duplicate concept_id Check Result

Validation confirmed unique `concept_id` values across all 50 detection specs.

## Forbidden-Output Check Result

The new specs include `forbidden_outputs` and `prohibited_outputs` prohibiting trade permission, entries, exits, stops, targets, sizing, broker/order/account/fill/P&L behavior, and autonomous trade calls. Targeted forbidden-token search found no forbidden execution labels in the new P17 specs.

## Calibration-Boundary Notes

Calibrated specs define parameter names and scope only. Judgment-assisted specs define evidence collection, downgrade logic, confidence behavior, and review hooks. Context-only crowding/pain-trade output remains posture/context labeling and does not become a detector or signal. No universal thresholds or parameter values were introduced.

## Missing-Feed or Downgrade Behavior Summary

Every new spec defines required feed refusal or insufficient-evidence behavior, optional-feed degradation, stale-data refusal, and missing-calibration handling. Missing profile, order-flow, depth, breadth, event, volatility, or positioning feeds downgrade interpretation instead of being proxied by unrelated data.

## Concepts Requiring GPT-5.5 Doctrine Review

None.

## Remaining Blockers

None.

## Operator-Usable Outcome

P17 adds 20 additional schema-aligned detection contracts, expanding the project from 30 to 50 machine-readable specs while preserving the actionable-in-judgment, non-executional boundary.
