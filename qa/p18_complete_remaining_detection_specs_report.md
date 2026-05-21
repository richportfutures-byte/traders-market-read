# P18 Complete Remaining Detection Specs Report
## Executive Result
- Result: P18_PASS
- Registry concept count: 110
- Detection-spec count before: 50
- Detection-spec count after: 110
- Files created: 60 new specs plus this QA report
- Coverage validation result: PASS - 110 registry concept_ids, 110 spec files, 110 unique spec concept_ids, 0 missing, 0 extra
- Schema/YAML validation result: PASS - all 110 spec YAML files parsed; all 60 new specs include required schema fields and `review_status: DRAFT`
- Remaining blockers: None identified during generation

## Files Created

- `spec/detection_specs/ch02_break_quality.yaml`
- `spec/detection_specs/ch02_level_magnetism_and_decay.yaml`
- `spec/detection_specs/ch03_the_auction_framework.yaml`
- `spec/detection_specs/ch08_compression_breakouts_real_vs_false.yaml`
- `spec/detection_specs/ch09_breadth_confirmation_and_divergence.yaml`
- `spec/detection_specs/ch12_execution_environment_quality_and_veto.yaml`
- `spec/detection_specs/ch01_confirmation_and_invalidation_discipline.yaml`
- `spec/detection_specs/ch01_false_precision_and_observation_tracking.yaml`
- `spec/detection_specs/ch01_leading_vs_coincident_signals.yaml`
- `spec/detection_specs/ch01_signal_conflict_taxonomy.yaml`
- `spec/detection_specs/ch01_tape_confirms_narrative_rule.yaml`
- `spec/detection_specs/ch01_the_read_vs_the_touch.yaml`
- `spec/detection_specs/ch02_mechanical_levels_and_obvious_traps.yaml`
- `spec/detection_specs/ch04_tape_vs_narrative.yaml`
- `spec/detection_specs/ch05_exhaustion.yaml`
- `spec/detection_specs/ch07_ny_inheritance_vs_rejection.yaml`
- `spec/detection_specs/ch07_opening_type_taxonomy.yaml`
- `spec/detection_specs/ch07_session_quality_vs_session_completion.yaml`
- `spec/detection_specs/ch08_event_volatility_regime.yaml`
- `spec/detection_specs/ch08_liquidity_driven_and_mechanical_volatility.yaml`
- `spec/detection_specs/ch09_crude_fundamentals_inventories_and_cracks.yaml`
- `spec/detection_specs/ch09_crude_spreads_and_geopolitical_premium.yaml`
- `spec/detection_specs/ch09_euro_event_windows_and_carry.yaml`
- `spec/detection_specs/ch09_euro_dollar_drivers.yaml`
- `spec/detection_specs/ch09_gold_demand_channels.yaml`
- `spec/detection_specs/ch09_gold_drivers_real_yields_dxy_breakevens.yaml`
- `spec/detection_specs/ch09_intermarket_confirmation_general_principle.yaml`
- `spec/detection_specs/ch09_nq_es_relative_strength_and_index_internals.yaml`
- `spec/detection_specs/ch09_the_yield_curve_and_rate_repricing.yaml`
- `spec/detection_specs/ch09_treasury_auctions_and_supply.yaml`
- `spec/detection_specs/ch09_treasury_cash_futures_and_basis.yaml`
- `spec/detection_specs/ch09_vix_credit_and_cross_asset_risk_tone.yaml`
- `spec/detection_specs/ch10_catalyst_effect_on_thesis.yaml`
- `spec/detection_specs/ch10_narrative_consensus_and_disagreement.yaml`
- `spec/detection_specs/ch10_new_information_vs_recycled_context.yaml`
- `spec/detection_specs/ch10_pricing_in.yaml`
- `spec/detection_specs/ch10_source_quality.yaml`
- `spec/detection_specs/ch10_transmission_mechanism_and_order_effects.yaml`
- `spec/detection_specs/ch11_active_trade_state_vs_market_thesis_state.yaml`
- `spec/detection_specs/ch11_maintenance_conditions.yaml`
- `spec/detection_specs/ch11_review_reduce_stand_aside_state.yaml`
- `spec/detection_specs/ch11_thesis_invalidation.yaml`
- `spec/detection_specs/ch11_thesis_replacement_and_bias_flip.yaml`
- `spec/detection_specs/ch11_thesis_staleness_and_expiration.yaml`
- `spec/detection_specs/ch11_thesis_state_lifecycle.yaml`
- `spec/detection_specs/ch11_thesis_weakening_and_degradation.yaml`
- `spec/detection_specs/ch12_alignment_across_dimensions.yaml`
- `spec/detection_specs/ch12_asymmetry_and_practical_r_r.yaml`
- `spec/detection_specs/ch12_invalidation_and_confirmation_clarity.yaml`
- `spec/detection_specs/ch12_location_quality.yaml`
- `spec/detection_specs/ch12_setup_cleanliness_and_timing.yaml`
- `spec/detection_specs/ch12_setup_expression_and_no_clean_expression.yaml`
- `spec/detection_specs/ch12_setup_fragility.yaml`
- `spec/detection_specs/ch01_context_vs_execution_permission.yaml`
- `spec/detection_specs/ch01_product_specific_behavior.yaml`
- `spec/detection_specs/ch06_mechanical_flows_rebalance_month_end_roll.yaml`
- `spec/detection_specs/ch10_catalyst_to_trade_translation.yaml`
- `spec/detection_specs/ch11_thesis_confirmation_vs_execution_permission.yaml`
- `spec/detection_specs/ch12_action_vocabulary.yaml`
- `spec/detection_specs/ch06_dealer_gamma_dynamics.yaml`
- `qa/p18_complete_remaining_detection_specs_report.md`

## Concepts Covered

| Concept | concept_id | Determinism Class | Emitted-State Summary |
|---|---|---|---|
| Break Quality | `ch02_break_quality` | CALIBRATED | BREAK_QUALITY_CONTEXT, BREAK_QUALITY_CONFIRMED, BREAK_QUALITY_NOT_CONFIRMED, BREAK_QUALITY_REVIEW_REQUIRED |
| Level Magnetism & Decay | `ch02_level_magnetism_and_decay` | CALIBRATED | LEVEL_MAGNETISM_AND_DECAY_CONTEXT, LEVEL_MAGNETISM_AND_DECAY_CONFIRMED, LEVEL_MAGNETISM_AND_DECAY_NOT_CONFIRMED, LEVEL_MAGNETISM_AND_DECAY_REVIEW_REQUIRED |
| The Auction Framework | `ch03_the_auction_framework` | CALIBRATED | THE_AUCTION_FRAMEWORK_CONTEXT, THE_AUCTION_FRAMEWORK_CONFIRMED, THE_AUCTION_FRAMEWORK_NOT_CONFIRMED, THE_AUCTION_FRAMEWORK_REVIEW_REQUIRED |
| Compression Breakouts (Real vs. False) | `ch08_compression_breakouts_real_vs_false` | CALIBRATED | COMPRESSION_BREAKOUTS_REAL_VS_FALSE_CONTEXT, COMPRESSION_BREAKOUTS_REAL_VS_FALSE_CONFIRMED, COMPRESSION_BREAKOUTS_REAL_VS_FALSE_NOT_CONFIRMED, COMPRESSION_BREAKOUTS_REAL_VS_FALSE_REVIEW_REQUIRED |
| Breadth Confirmation & Divergence | `ch09_breadth_confirmation_and_divergence` | CALIBRATED | BREADTH_CONFIRMATION_AND_DIVERGENCE_CONTEXT, BREADTH_CONFIRMATION_AND_DIVERGENCE_CONFIRMED, BREADTH_CONFIRMATION_AND_DIVERGENCE_NOT_CONFIRMED, BREADTH_CONFIRMATION_AND_DIVERGENCE_REVIEW_REQUIRED |
| Execution Environment Quality & Veto | `ch12_execution_environment_quality_and_veto` | CALIBRATED | EXECUTION_ENVIRONMENT_QUALITY_AND_VETO_CONTEXT, EXECUTION_ENVIRONMENT_QUALITY_AND_VETO_CONFIRMED, EXECUTION_ENVIRONMENT_QUALITY_AND_VETO_NOT_CONFIRMED, EXECUTION_ENVIRONMENT_QUALITY_AND_VETO_REVIEW_REQUIRED |
| Confirmation & Invalidation Discipline | `ch01_confirmation_and_invalidation_discipline` | JUDGMENT_ASSISTED | CONFIRMATION_AND_INVALIDATION_DISCIPLINE_EVIDENCE_PRESENT, CONFIRMATION_AND_INVALIDATION_DISCIPLINE_WEAKENED, CONFIRMATION_AND_INVALIDATION_DISCIPLINE_CONFLICTED, CONFIRMATION_AND_INVALIDATION_DISCIPLINE_PROVISIONAL_CONTEXT |
| False Precision & Observation Tracking | `ch01_false_precision_and_observation_tracking` | JUDGMENT_ASSISTED | FALSE_PRECISION_AND_OBSERVATION_TRACKING_EVIDENCE_PRESENT, FALSE_PRECISION_AND_OBSERVATION_TRACKING_WEAKENED, FALSE_PRECISION_AND_OBSERVATION_TRACKING_CONFLICTED, FALSE_PRECISION_AND_OBSERVATION_TRACKING_PROVISIONAL_CONTEXT |
| Leading vs. Coincident Signals | `ch01_leading_vs_coincident_signals` | JUDGMENT_ASSISTED | LEADING_VS_COINCIDENT_SIGNALS_EVIDENCE_PRESENT, LEADING_VS_COINCIDENT_SIGNALS_WEAKENED, LEADING_VS_COINCIDENT_SIGNALS_CONFLICTED, LEADING_VS_COINCIDENT_SIGNALS_PROVISIONAL_CONTEXT |
| Signal Conflict Taxonomy | `ch01_signal_conflict_taxonomy` | JUDGMENT_ASSISTED | SIGNAL_CONFLICT_TAXONOMY_EVIDENCE_PRESENT, SIGNAL_CONFLICT_TAXONOMY_WEAKENED, SIGNAL_CONFLICT_TAXONOMY_CONFLICTED, SIGNAL_CONFLICT_TAXONOMY_PROVISIONAL_CONTEXT |
| Tape-Confirms-Narrative Rule | `ch01_tape_confirms_narrative_rule` | JUDGMENT_ASSISTED | TAPE_CONFIRMS_NARRATIVE_RULE_EVIDENCE_PRESENT, TAPE_CONFIRMS_NARRATIVE_RULE_WEAKENED, TAPE_CONFIRMS_NARRATIVE_RULE_CONFLICTED, TAPE_CONFIRMS_NARRATIVE_RULE_PROVISIONAL_CONTEXT |
| The Read vs. The Touch | `ch01_the_read_vs_the_touch` | JUDGMENT_ASSISTED | THE_READ_VS_THE_TOUCH_EVIDENCE_PRESENT, THE_READ_VS_THE_TOUCH_WEAKENED, THE_READ_VS_THE_TOUCH_CONFLICTED, THE_READ_VS_THE_TOUCH_PROVISIONAL_CONTEXT |
| Mechanical Levels & Obvious Traps | `ch02_mechanical_levels_and_obvious_traps` | JUDGMENT_ASSISTED | MECHANICAL_LEVELS_AND_OBVIOUS_TRAPS_EVIDENCE_PRESENT, MECHANICAL_LEVELS_AND_OBVIOUS_TRAPS_WEAKENED, MECHANICAL_LEVELS_AND_OBVIOUS_TRAPS_CONFLICTED, MECHANICAL_LEVELS_AND_OBVIOUS_TRAPS_PROVISIONAL_CONTEXT |
| Tape vs. Narrative | `ch04_tape_vs_narrative` | JUDGMENT_ASSISTED | TAPE_VS_NARRATIVE_EVIDENCE_PRESENT, TAPE_VS_NARRATIVE_WEAKENED, TAPE_VS_NARRATIVE_CONFLICTED, TAPE_VS_NARRATIVE_PROVISIONAL_CONTEXT |
| Exhaustion | `ch05_exhaustion` | JUDGMENT_ASSISTED | EXHAUSTION_EVIDENCE_PRESENT, EXHAUSTION_WEAKENED, EXHAUSTION_CONFLICTED, EXHAUSTION_PROVISIONAL_CONTEXT |
| NY Inheritance vs. Rejection | `ch07_ny_inheritance_vs_rejection` | JUDGMENT_ASSISTED | NY_INHERITANCE_VS_REJECTION_EVIDENCE_PRESENT, NY_INHERITANCE_VS_REJECTION_WEAKENED, NY_INHERITANCE_VS_REJECTION_CONFLICTED, NY_INHERITANCE_VS_REJECTION_PROVISIONAL_CONTEXT |
| Opening Type Taxonomy | `ch07_opening_type_taxonomy` | JUDGMENT_ASSISTED | OPENING_TYPE_TAXONOMY_EVIDENCE_PRESENT, OPENING_TYPE_TAXONOMY_WEAKENED, OPENING_TYPE_TAXONOMY_CONFLICTED, OPENING_TYPE_TAXONOMY_PROVISIONAL_CONTEXT |
| Session Quality vs. Session Completion | `ch07_session_quality_vs_session_completion` | JUDGMENT_ASSISTED | SESSION_QUALITY_VS_SESSION_COMPLETION_EVIDENCE_PRESENT, SESSION_QUALITY_VS_SESSION_COMPLETION_WEAKENED, SESSION_QUALITY_VS_SESSION_COMPLETION_CONFLICTED, SESSION_QUALITY_VS_SESSION_COMPLETION_PROVISIONAL_CONTEXT |
| Event Volatility Regime | `ch08_event_volatility_regime` | JUDGMENT_ASSISTED | EVENT_VOLATILITY_REGIME_EVIDENCE_PRESENT, EVENT_VOLATILITY_REGIME_WEAKENED, EVENT_VOLATILITY_REGIME_CONFLICTED, EVENT_VOLATILITY_REGIME_PROVISIONAL_CONTEXT |
| Liquidity-Driven & Mechanical Volatility | `ch08_liquidity_driven_and_mechanical_volatility` | JUDGMENT_ASSISTED | LIQUIDITY_DRIVEN_AND_MECHANICAL_VOLATILITY_EVIDENCE_PRESENT, LIQUIDITY_DRIVEN_AND_MECHANICAL_VOLATILITY_WEAKENED, LIQUIDITY_DRIVEN_AND_MECHANICAL_VOLATILITY_CONFLICTED, LIQUIDITY_DRIVEN_AND_MECHANICAL_VOLATILITY_PROVISIONAL_CONTEXT |
| Crude Fundamentals: Inventories & Cracks | `ch09_crude_fundamentals_inventories_and_cracks` | JUDGMENT_ASSISTED | CRUDE_FUNDAMENTALS_INVENTORIES_AND_CRACKS_EVIDENCE_PRESENT, CRUDE_FUNDAMENTALS_INVENTORIES_AND_CRACKS_WEAKENED, CRUDE_FUNDAMENTALS_INVENTORIES_AND_CRACKS_CONFLICTED, CRUDE_FUNDAMENTALS_INVENTORIES_AND_CRACKS_PROVISIONAL_CONTEXT |
| Crude Spreads & Geopolitical Premium | `ch09_crude_spreads_and_geopolitical_premium` | JUDGMENT_ASSISTED | CRUDE_SPREADS_AND_GEOPOLITICAL_PREMIUM_EVIDENCE_PRESENT, CRUDE_SPREADS_AND_GEOPOLITICAL_PREMIUM_WEAKENED, CRUDE_SPREADS_AND_GEOPOLITICAL_PREMIUM_CONFLICTED, CRUDE_SPREADS_AND_GEOPOLITICAL_PREMIUM_PROVISIONAL_CONTEXT |
| Euro Event Windows & Carry | `ch09_euro_event_windows_and_carry` | JUDGMENT_ASSISTED | EURO_EVENT_WINDOWS_AND_CARRY_EVIDENCE_PRESENT, EURO_EVENT_WINDOWS_AND_CARRY_WEAKENED, EURO_EVENT_WINDOWS_AND_CARRY_CONFLICTED, EURO_EVENT_WINDOWS_AND_CARRY_PROVISIONAL_CONTEXT |
| Euro/Dollar Drivers | `ch09_euro_dollar_drivers` | JUDGMENT_ASSISTED | EURO_DOLLAR_DRIVERS_EVIDENCE_PRESENT, EURO_DOLLAR_DRIVERS_WEAKENED, EURO_DOLLAR_DRIVERS_CONFLICTED, EURO_DOLLAR_DRIVERS_PROVISIONAL_CONTEXT |
| Gold Demand Channels | `ch09_gold_demand_channels` | JUDGMENT_ASSISTED | GOLD_DEMAND_CHANNELS_EVIDENCE_PRESENT, GOLD_DEMAND_CHANNELS_WEAKENED, GOLD_DEMAND_CHANNELS_CONFLICTED, GOLD_DEMAND_CHANNELS_PROVISIONAL_CONTEXT |
| Gold Drivers: Real Yields, DXY, Breakevens | `ch09_gold_drivers_real_yields_dxy_breakevens` | JUDGMENT_ASSISTED | GOLD_DRIVERS_REAL_YIELDS_DXY_BREAKEVENS_EVIDENCE_PRESENT, GOLD_DRIVERS_REAL_YIELDS_DXY_BREAKEVENS_WEAKENED, GOLD_DRIVERS_REAL_YIELDS_DXY_BREAKEVENS_CONFLICTED, GOLD_DRIVERS_REAL_YIELDS_DXY_BREAKEVENS_PROVISIONAL_CONTEXT |
| Intermarket Confirmation (General Principle) | `ch09_intermarket_confirmation_general_principle` | JUDGMENT_ASSISTED | INTERMARKET_CONFIRMATION_GENERAL_PRINCIPLE_EVIDENCE_PRESENT, INTERMARKET_CONFIRMATION_GENERAL_PRINCIPLE_WEAKENED, INTERMARKET_CONFIRMATION_GENERAL_PRINCIPLE_CONFLICTED, INTERMARKET_CONFIRMATION_GENERAL_PRINCIPLE_PROVISIONAL_CONTEXT |
| NQ/ES Relative Strength & Index Internals | `ch09_nq_es_relative_strength_and_index_internals` | JUDGMENT_ASSISTED | NQ_ES_RELATIVE_STRENGTH_AND_INDEX_INTERNALS_EVIDENCE_PRESENT, NQ_ES_RELATIVE_STRENGTH_AND_INDEX_INTERNALS_WEAKENED, NQ_ES_RELATIVE_STRENGTH_AND_INDEX_INTERNALS_CONFLICTED, NQ_ES_RELATIVE_STRENGTH_AND_INDEX_INTERNALS_PROVISIONAL_CONTEXT |
| The Yield Curve & Rate Repricing | `ch09_the_yield_curve_and_rate_repricing` | JUDGMENT_ASSISTED | THE_YIELD_CURVE_AND_RATE_REPRICING_EVIDENCE_PRESENT, THE_YIELD_CURVE_AND_RATE_REPRICING_WEAKENED, THE_YIELD_CURVE_AND_RATE_REPRICING_CONFLICTED, THE_YIELD_CURVE_AND_RATE_REPRICING_PROVISIONAL_CONTEXT |
| Treasury Auctions & Supply | `ch09_treasury_auctions_and_supply` | JUDGMENT_ASSISTED | TREASURY_AUCTIONS_AND_SUPPLY_EVIDENCE_PRESENT, TREASURY_AUCTIONS_AND_SUPPLY_WEAKENED, TREASURY_AUCTIONS_AND_SUPPLY_CONFLICTED, TREASURY_AUCTIONS_AND_SUPPLY_PROVISIONAL_CONTEXT |
| Treasury Cash/Futures & Basis | `ch09_treasury_cash_futures_and_basis` | JUDGMENT_ASSISTED | TREASURY_CASH_FUTURES_AND_BASIS_EVIDENCE_PRESENT, TREASURY_CASH_FUTURES_AND_BASIS_WEAKENED, TREASURY_CASH_FUTURES_AND_BASIS_CONFLICTED, TREASURY_CASH_FUTURES_AND_BASIS_PROVISIONAL_CONTEXT |
| VIX, Credit & Cross-Asset Risk Tone | `ch09_vix_credit_and_cross_asset_risk_tone` | JUDGMENT_ASSISTED | VIX_CREDIT_AND_CROSS_ASSET_RISK_TONE_EVIDENCE_PRESENT, VIX_CREDIT_AND_CROSS_ASSET_RISK_TONE_WEAKENED, VIX_CREDIT_AND_CROSS_ASSET_RISK_TONE_CONFLICTED, VIX_CREDIT_AND_CROSS_ASSET_RISK_TONE_PROVISIONAL_CONTEXT |
| Catalyst Effect on Thesis | `ch10_catalyst_effect_on_thesis` | JUDGMENT_ASSISTED | CATALYST_EFFECT_ON_THESIS_EVIDENCE_PRESENT, CATALYST_EFFECT_ON_THESIS_WEAKENED, CATALYST_EFFECT_ON_THESIS_CONFLICTED, CATALYST_EFFECT_ON_THESIS_PROVISIONAL_CONTEXT |
| Narrative Consensus & Disagreement | `ch10_narrative_consensus_and_disagreement` | JUDGMENT_ASSISTED | NARRATIVE_CONSENSUS_AND_DISAGREEMENT_EVIDENCE_PRESENT, NARRATIVE_CONSENSUS_AND_DISAGREEMENT_WEAKENED, NARRATIVE_CONSENSUS_AND_DISAGREEMENT_CONFLICTED, NARRATIVE_CONSENSUS_AND_DISAGREEMENT_PROVISIONAL_CONTEXT |
| New Information vs. Recycled Context | `ch10_new_information_vs_recycled_context` | JUDGMENT_ASSISTED | NEW_INFORMATION_VS_RECYCLED_CONTEXT_EVIDENCE_PRESENT, NEW_INFORMATION_VS_RECYCLED_CONTEXT_WEAKENED, NEW_INFORMATION_VS_RECYCLED_CONTEXT_CONFLICTED, NEW_INFORMATION_VS_RECYCLED_CONTEXT_PROVISIONAL_CONTEXT |
| Pricing-In | `ch10_pricing_in` | JUDGMENT_ASSISTED | PRICING_IN_EVIDENCE_PRESENT, PRICING_IN_WEAKENED, PRICING_IN_CONFLICTED, PRICING_IN_PROVISIONAL_CONTEXT |
| Source Quality | `ch10_source_quality` | JUDGMENT_ASSISTED | SOURCE_QUALITY_EVIDENCE_PRESENT, SOURCE_QUALITY_WEAKENED, SOURCE_QUALITY_CONFLICTED, SOURCE_QUALITY_PROVISIONAL_CONTEXT |
| Transmission Mechanism & Order Effects | `ch10_transmission_mechanism_and_order_effects` | JUDGMENT_ASSISTED | TRANSMISSION_MECHANISM_AND_ORDER_EFFECTS_EVIDENCE_PRESENT, TRANSMISSION_MECHANISM_AND_ORDER_EFFECTS_WEAKENED, TRANSMISSION_MECHANISM_AND_ORDER_EFFECTS_CONFLICTED, TRANSMISSION_MECHANISM_AND_ORDER_EFFECTS_PROVISIONAL_CONTEXT |
| Active Trade State vs. Market Thesis State | `ch11_active_trade_state_vs_market_thesis_state` | JUDGMENT_ASSISTED | ACTIVE_TRADE_STATE_VS_MARKET_THESIS_STATE_EVIDENCE_PRESENT, ACTIVE_TRADE_STATE_VS_MARKET_THESIS_STATE_WEAKENED, ACTIVE_TRADE_STATE_VS_MARKET_THESIS_STATE_CONFLICTED, ACTIVE_TRADE_STATE_VS_MARKET_THESIS_STATE_PROVISIONAL_CONTEXT |
| Maintenance Conditions | `ch11_maintenance_conditions` | JUDGMENT_ASSISTED | MAINTENANCE_CONDITIONS_EVIDENCE_PRESENT, MAINTENANCE_CONDITIONS_WEAKENED, MAINTENANCE_CONDITIONS_CONFLICTED, MAINTENANCE_CONDITIONS_PROVISIONAL_CONTEXT |
| Review / Reduce / Stand-Aside State | `ch11_review_reduce_stand_aside_state` | JUDGMENT_ASSISTED | REVIEW_REDUCE_STAND_ASIDE_STATE_EVIDENCE_PRESENT, REVIEW_REDUCE_STAND_ASIDE_STATE_WEAKENED, REVIEW_REDUCE_STAND_ASIDE_STATE_CONFLICTED, REVIEW_REDUCE_STAND_ASIDE_STATE_PROVISIONAL_CONTEXT |
| Thesis Invalidation | `ch11_thesis_invalidation` | JUDGMENT_ASSISTED | THESIS_INVALIDATION_EVIDENCE_PRESENT, THESIS_INVALIDATION_WEAKENED, THESIS_INVALIDATION_CONFLICTED, THESIS_INVALIDATION_PROVISIONAL_CONTEXT |
| Thesis Replacement & Bias Flip | `ch11_thesis_replacement_and_bias_flip` | JUDGMENT_ASSISTED | THESIS_REPLACEMENT_AND_BIAS_FLIP_EVIDENCE_PRESENT, THESIS_REPLACEMENT_AND_BIAS_FLIP_WEAKENED, THESIS_REPLACEMENT_AND_BIAS_FLIP_CONFLICTED, THESIS_REPLACEMENT_AND_BIAS_FLIP_PROVISIONAL_CONTEXT |
| Thesis Staleness & Expiration | `ch11_thesis_staleness_and_expiration` | JUDGMENT_ASSISTED | THESIS_STALENESS_AND_EXPIRATION_EVIDENCE_PRESENT, THESIS_STALENESS_AND_EXPIRATION_WEAKENED, THESIS_STALENESS_AND_EXPIRATION_CONFLICTED, THESIS_STALENESS_AND_EXPIRATION_PROVISIONAL_CONTEXT |
| Thesis State Lifecycle | `ch11_thesis_state_lifecycle` | JUDGMENT_ASSISTED | THESIS_STATE_LIFECYCLE_EVIDENCE_PRESENT, THESIS_STATE_LIFECYCLE_WEAKENED, THESIS_STATE_LIFECYCLE_CONFLICTED, THESIS_STATE_LIFECYCLE_PROVISIONAL_CONTEXT |
| Thesis Weakening & Degradation | `ch11_thesis_weakening_and_degradation` | JUDGMENT_ASSISTED | THESIS_WEAKENING_AND_DEGRADATION_EVIDENCE_PRESENT, THESIS_WEAKENING_AND_DEGRADATION_WEAKENED, THESIS_WEAKENING_AND_DEGRADATION_CONFLICTED, THESIS_WEAKENING_AND_DEGRADATION_PROVISIONAL_CONTEXT |
| Alignment Across Dimensions | `ch12_alignment_across_dimensions` | JUDGMENT_ASSISTED | ALIGNMENT_ACROSS_DIMENSIONS_EVIDENCE_PRESENT, ALIGNMENT_ACROSS_DIMENSIONS_WEAKENED, ALIGNMENT_ACROSS_DIMENSIONS_CONFLICTED, ALIGNMENT_ACROSS_DIMENSIONS_PROVISIONAL_CONTEXT |
| Asymmetry & Practical R:R | `ch12_asymmetry_and_practical_r_r` | JUDGMENT_ASSISTED | ASYMMETRY_AND_PRACTICAL_R_R_EVIDENCE_PRESENT, ASYMMETRY_AND_PRACTICAL_R_R_WEAKENED, ASYMMETRY_AND_PRACTICAL_R_R_CONFLICTED, ASYMMETRY_AND_PRACTICAL_R_R_PROVISIONAL_CONTEXT |
| Invalidation & Confirmation Clarity | `ch12_invalidation_and_confirmation_clarity` | JUDGMENT_ASSISTED | INVALIDATION_AND_CONFIRMATION_CLARITY_EVIDENCE_PRESENT, INVALIDATION_AND_CONFIRMATION_CLARITY_WEAKENED, INVALIDATION_AND_CONFIRMATION_CLARITY_CONFLICTED, INVALIDATION_AND_CONFIRMATION_CLARITY_PROVISIONAL_CONTEXT |
| Location Quality | `ch12_location_quality` | JUDGMENT_ASSISTED | LOCATION_QUALITY_EVIDENCE_PRESENT, LOCATION_QUALITY_WEAKENED, LOCATION_QUALITY_CONFLICTED, LOCATION_QUALITY_PROVISIONAL_CONTEXT |
| Setup Cleanliness & Timing | `ch12_setup_cleanliness_and_timing` | JUDGMENT_ASSISTED | SETUP_CLEANLINESS_AND_TIMING_EVIDENCE_PRESENT, SETUP_CLEANLINESS_AND_TIMING_WEAKENED, SETUP_CLEANLINESS_AND_TIMING_CONFLICTED, SETUP_CLEANLINESS_AND_TIMING_PROVISIONAL_CONTEXT |
| Setup Expression & No Clean Expression | `ch12_setup_expression_and_no_clean_expression` | JUDGMENT_ASSISTED | SETUP_EXPRESSION_AND_NO_CLEAN_EXPRESSION_EVIDENCE_PRESENT, SETUP_EXPRESSION_AND_NO_CLEAN_EXPRESSION_WEAKENED, SETUP_EXPRESSION_AND_NO_CLEAN_EXPRESSION_CONFLICTED, SETUP_EXPRESSION_AND_NO_CLEAN_EXPRESSION_PROVISIONAL_CONTEXT |
| Setup Fragility | `ch12_setup_fragility` | JUDGMENT_ASSISTED | SETUP_FRAGILITY_EVIDENCE_PRESENT, SETUP_FRAGILITY_WEAKENED, SETUP_FRAGILITY_CONFLICTED, SETUP_FRAGILITY_PROVISIONAL_CONTEXT |
| Context vs. Execution Permission | `ch01_context_vs_execution_permission` | CONTEXT_ONLY | CONTEXT_VS_EXECUTION_PERMISSION_CONTEXT, CONTEXT_VS_EXECUTION_PERMISSION_BOUNDARY_ACTIVE, CONTEXT_VS_EXECUTION_PERMISSION_REVIEW_REQUIRED, CONTEXT_ONLY |
| Product-Specific Behavior | `ch01_product_specific_behavior` | CONTEXT_ONLY | PRODUCT_SPECIFIC_BEHAVIOR_CONTEXT, PRODUCT_SPECIFIC_BEHAVIOR_BOUNDARY_ACTIVE, PRODUCT_SPECIFIC_BEHAVIOR_REVIEW_REQUIRED, CONTEXT_ONLY |
| Mechanical Flows (Rebalance / Month-End / Roll) | `ch06_mechanical_flows_rebalance_month_end_roll` | CONTEXT_ONLY | MECHANICAL_FLOWS_REBALANCE_MONTH_END_ROLL_CONTEXT, MECHANICAL_FLOWS_REBALANCE_MONTH_END_ROLL_BOUNDARY_ACTIVE, MECHANICAL_FLOWS_REBALANCE_MONTH_END_ROLL_REVIEW_REQUIRED, CONTEXT_ONLY |
| Catalyst-to-Trade Translation | `ch10_catalyst_to_trade_translation` | CONTEXT_ONLY | CATALYST_TO_TRADE_TRANSLATION_CONTEXT, CATALYST_TO_TRADE_TRANSLATION_BOUNDARY_ACTIVE, CATALYST_TO_TRADE_TRANSLATION_REVIEW_REQUIRED, CONTEXT_ONLY |
| Thesis Confirmation vs. Execution Permission | `ch11_thesis_confirmation_vs_execution_permission` | CONTEXT_ONLY | THESIS_CONFIRMATION_VS_EXECUTION_PERMISSION_CONTEXT, THESIS_CONFIRMATION_VS_EXECUTION_PERMISSION_BOUNDARY_ACTIVE, THESIS_CONFIRMATION_VS_EXECUTION_PERMISSION_REVIEW_REQUIRED, CONTEXT_ONLY |
| Action Vocabulary | `ch12_action_vocabulary` | CONTEXT_ONLY | ACTION_VOCABULARY_CONTEXT, ACTION_VOCABULARY_BOUNDARY_ACTIVE, ACTION_VOCABULARY_REVIEW_REQUIRED, CONTEXT_ONLY |
| Dealer Gamma Dynamics | `ch06_dealer_gamma_dynamics` | NOT_DETECTABLE_WITH_CURRENT_FEEDS | DEALER_GAMMA_DYNAMICS_BLOCKED_BY_FEEDS, DEALER_GAMMA_DYNAMICS_EXTERNAL_EVIDENCE_REQUIRED, NOT_DETECTABLE_WITH_CURRENT_FEEDS, INSUFFICIENT_EVIDENCE |

## Counts By Determinism Class

- COMPUTABLE: 0
- CALIBRATED: 6
- JUDGMENT_ASSISTED: 47
- CONTEXT_ONLY: 6
- NOT_DETECTABLE_WITH_CURRENT_FEEDS: 1

## Coverage Validation Result

All registry concepts that lacked specs at the start of P18 were generated as one YAML file per `concept_id`. Final command validation confirmed 110 registry IDs, 110 spec files, 110 unique spec IDs, zero missing IDs, and zero extra IDs.

## Schema/YAML Validation Result

Generated specs include schema-required fields, standard project fields, `review_status: DRAFT`, bounded `states_emitted`, explicit `required_inputs`, `optional_inputs`, `unavailable_input_behavior`, `decision_logic`, `confidence_rules`, `refusal_behavior`, `failure_modes`, `test_cases`, `prohibited_outputs`, and `forbidden_outputs`.

## Registry Alignment Result

Each generated spec copies `concept_id`, concept name, chapter metadata, glossary path, and determinism class from `spec/concept_registry.yaml`. Registry and matrix classes were checked before generation and no conflicts were found.

## Duplicate concept_id Check Result

Generation refused to overwrite existing specs and pre-checked for duplicate implemented `concept_id` values. Final validation confirmed no duplicates across all specs.

## Forbidden-Output Check Result

Every generated spec prohibits trade permission, entries, exits, stops, targets, sizing, add/reduce, broker/order/account/fill/P&L behavior, and autonomous trade calls. Specs emit read-quality, context, confidence, review, insufficient-evidence, and refusal labels only.

## Calibration-Boundary Notes

Calibrated concepts define named parameters with `value: null`; judgment-assisted concepts define evidence weighting and downgrade review hooks; context-only concepts emit governance/context labels only; feed-blocked concepts refuse classification unless the missing external feed class is available in a future governed pass. No calibration profiles or numeric thresholds were created.

## Missing-Feed/Refusal Behavior Summary

Every generated spec includes missing-required-feed behavior, optional-feed downgrade behavior, stale/malformed-data refusal, missing-calibration handling, and executional-output refusal. Missing feeds produce `INSUFFICIENT_EVIDENCE`, `DEGRADED_CONFIDENCE`, `CONTEXT_ONLY`, or `REFUSE_TO_CLASSIFY` according to schema-valid behavior.

## Concepts Requiring GPT-5.5 Doctrine Review

None.

## Remaining Blockers

None.
