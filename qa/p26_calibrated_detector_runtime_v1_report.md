# P26 Calibrated Detector Runtime v1 Report

## Result

**P26_PASS**

---

## Files Created or Changed

### Created

| File | Description |
|------|-------------|
| `src/traders_market_read/detectors/calibration.py` | Calibration profile loader with fail-closed validation |
| `src/traders_market_read/detectors/calibrated.py` | 27 CALIBRATED detector implementations with real structural logic |
| `qa/examples/detector_runtime_calibrated_profile.example.yaml` | Example calibration profile with fake parameter values for all 27 detectors |
| `qa/examples/detector_runtime_calibrated_input.example.json` | Calibrated input fixture with data blocks for all 27 detectors |
| `qa/examples/detector_runtime_calibrated_output.example.json` | Generated output with 27 calibrated classifications |
| `qa/examples/detector_runtime_missing_calibration_output.example.json` | Generated output proving 27 safe refusals when profile absent |
| `tests/test_calibrated_detector_runtime_v1.py` | 30 tests covering all 15 required P26 test cases |
| `qa/p26_calibrated_detector_runtime_v1_report.md` | This report |

### Modified

| File | Description |
|------|-------------|
| `src/traders_market_read/detectors/runtime.py` | Added calibration profile dispatch for CALIBRATED contracts |
| `scripts/run_detector_runtime.py` | Added `--calibration-profile` CLI argument |
| `src/traders_market_read/detectors/__init__.py` | Exported calibration classes |
| `README.md` | Added calibrated runtime command reference |

---

## CALIBRATED Contracts Discovered

27 CALIBRATED contracts from `spec/detector_contract_catalog.json`:

| # | concept_id | Chapter |
|---|-----------|---------|
| 1 | `ch02_acceptance_vs_rejection` | 2 |
| 2 | `ch02_break_quality` | 2 |
| 3 | `ch02_breakout_continuation_vs_breakout_failure` | 2 |
| 4 | `ch02_level_magnetism_and_decay` | 2 |
| 5 | `ch02_level_test_sequence` | 2 |
| 6 | `ch02_liquidity_sweep_vs_real_break` | 2 |
| 7 | `ch02_polarity_flip` | 2 |
| 8 | `ch03_auction_acceptance_vs_rejection` | 3 |
| 9 | `ch03_completed_failed_and_unfinished_auctions` | 3 |
| 10 | `ch03_excess_vs_poor_highs_lows` | 3 |
| 11 | `ch03_price_outside_value_acceptance_test` | 3 |
| 12 | `ch03_the_auction_framework` | 3 |
| 13 | `ch03_volume_nodes_and_air_pockets` | 3 |
| 14 | `ch04_spread_behavior` | 4 |
| 15 | `ch04_stall_and_snap_back` | 4 |
| 16 | `ch04_sweeps_through_liquidity` | 4 |
| 17 | `ch04_tape_quality_spectrum` | 4 |
| 18 | `ch05_follow_through_and_failure` | 5 |
| 19 | `ch05_impulse_vs_grind` | 5 |
| 20 | `ch06_stop_out_cascades_and_liquidation` | 6 |
| 21 | `ch07_asia_session_character` | 7 |
| 22 | `ch08_compression_breakouts_real_vs_false` | 8 |
| 23 | `ch08_compression_vs_expansion` | 8 |
| 24 | `ch08_expanded_volatility_no_trade_condition` | 8 |
| 25 | `ch08_volatility_crush_and_reset` | 8 |
| 26 | `ch09_breadth_confirmation_and_divergence` | 9 |
| 27 | `ch12_execution_environment_quality_and_veto` | 12 |

---

## CALIBRATED Detectors Implemented

**27 of 27** — all CALIBRATED contracts implemented with real structural logic.

### Implementation Categories

**Family A — Level Interaction (7 detectors)**
- `ch02_acceptance_vs_rejection`: dwell-time acceptance/rejection/failed-acceptance
- `ch02_break_quality`: displacement/crossing/velocity break texture
- `ch02_breakout_continuation_vs_breakout_failure`: extension/failure/retest classification
- `ch02_level_magnetism_and_decay`: drift-toward-level magnetism/overshoot/front-run
- `ch02_level_test_sequence`: test count, reaction decay, exhaustion
- `ch02_liquidity_sweep_vs_real_break`: sweep probe/reclaim/hold classification
- `ch02_polarity_flip`: retest/flip/fail/reclaim classification

**Family B — Auction / Profile (6 detectors)**
- `ch03_auction_acceptance_vs_rejection`: extension/development/return classification
- `ch03_completed_failed_and_unfinished_auctions`: tail/extreme/reclaim classification
- `ch03_excess_vs_poor_highs_lows`: single-print tail vs. flat extreme
- `ch03_price_outside_value_acceptance_test`: outside-value development/return
- `ch03_the_auction_framework`: overlap/directional balance/imbalance
- `ch03_volume_nodes_and_air_pockets`: HVN/LVN prominence and travel

**Family C — Series Statistics (7 detectors)**
- `ch04_spread_behavior`: widening/normalizing/stability
- `ch04_stall_and_snap_back`: stall-duration/progress/snap-back
- `ch04_sweeps_through_liquidity`: multi-level take/velocity/continuation
- `ch04_tape_quality_spectrum`: spread/range/instability classification
- `ch05_follow_through_and_failure`: extension/hold/failure
- `ch05_impulse_vs_grind`: displacement/overlap texture
- `ch06_stop_out_cascades_and_liquidation`: velocity/volume/breach cascade

**Family D — Session / Breadth / Environment (7 detectors)**
- `ch07_asia_session_character`: range/volume/fakeout classification
- `ch08_compression_breakouts_real_vs_false`: hold/reclaim breakout quality
- `ch08_compression_vs_expansion`: contraction/expansion/transition
- `ch08_expanded_volatility_no_trade_condition`: rv/spread/depth instability
- `ch08_volatility_crush_and_reset`: contraction/normalization/event
- `ch09_breadth_confirmation_and_divergence`: advance-ratio/direction confirmation
- `ch12_execution_environment_quality_and_veto`: spread/depth/rv/event veto

---

## CALIBRATED Detectors Still Refused/Unimplemented

**None.** All 27 CALIBRATED contracts are implemented.

---

## Calibration Profile Behavior Summary

- Profile loads from YAML with fail-closed validation.
- Envelope fields validated against `calibration/calibration_profile_schema.yaml`.
- Forbidden execution fields rejected recursively.
- Duplicate `(concept_id, parameter_name)` entries rejected.
- Missing required parameters rejected per detector at runtime.
- All values in the example profile are labeled `INSUFFICIENT_SAMPLE` and `example_value_for_runtime_wiring_only`.

---

## Fixture Paths

| Artifact | Path |
|----------|------|
| Calibration profile | `qa/examples/detector_runtime_calibrated_profile.example.yaml` |
| Input fixture | `qa/examples/detector_runtime_calibrated_input.example.json` |
| Calibrated output | `qa/examples/detector_runtime_calibrated_output.example.json` |
| Missing-calibration output | `qa/examples/detector_runtime_missing_calibration_output.example.json` |

---

## Validation Results

| Command | Result |
|---------|--------|
| `python3 scripts/validate_detection_specs.py` | PASS (110 specs) |
| `python3 scripts/build_detector_contract_catalog.py` | PASS (110 contracts, 27 CALIBRATED) |
| `python3 scripts/run_detector_runtime.py ... --calibration-profile ... --output ...` | PASS (110 outputs, 27 calibrated implemented) |
| `python3 scripts/validate_detector_output.py ...calibrated_output...` | PASS (110 documents) |
| `python3 scripts/run_detector_runtime.py ... --output ...missing_calibration...` | PASS (110 outputs, 27 calibrated refused) |
| `python3 scripts/validate_detector_output.py ...missing_calibration_output...` | PASS (110 documents) |
| `python3 scripts/run_detector_runtime.py ... --concept-id ch02_acceptance_vs_rejection` | PASS (1 output, calibrated implemented) |
| `python3 -m unittest tests/test_detector_runtime_v1.py tests/test_calibrated_detector_runtime_v1.py` | PASS (42 tests, 0 failures) |
| `python3 -m py_compile` (all source files) | PASS |

---

## Test Results

42 tests total (12 P25 + 30 P26), all passing:

| Test # | Description | Result |
|--------|-------------|--------|
| 1 | Calibration profile loads | PASS |
| 2 | Malformed profile fails closed | PASS (3 sub-tests) |
| 3 | Duplicate concept/parameter entries fail closed | PASS |
| 4 | Forbidden execution fields in profile fail closed | PASS (2 sub-tests) |
| 5 | Runtime without calibration profile refuses CALIBRATED | PASS (2 sub-tests) |
| 6 | Runtime with example profile runs all CALIBRATED detectors | PASS (2 sub-tests) |
| 7 | Implemented calibrated outputs validate | PASS (2 sub-tests: internal + external) |
| 8 | Missing calibrated fixture fields produce refusal | PASS (2 sub-tests) |
| 9 | Infeasible/unimplemented CALIBRATED contracts remain safe | PASS (all 27 implemented) |
| 10 | COMPUTABLE behavior still works with calibration | PASS (2 sub-tests) |
| 11 | JUDGMENT_ASSISTED, CONTEXT_ONLY, NOT_DETECTABLE remain safe | PASS (4 sub-tests) |
| 12 | No forbidden execution fields recursively | PASS |
| 13 | Guardrail booleans always true | PASS |
| 14 | Run-all mode still emits one output per contract | PASS (2 sub-tests) |
| 15 | `--concept-id` works for CALIBRATED detector | PASS (2 sub-tests) |

---

## Run-All Output Counts

| Metric | With Profile | Without Profile |
|--------|:----------:|:--------------:|
| Catalog contracts | 110 | 110 |
| Outputs generated | 110 | 110 |
| Computable implemented | 9 | 9 |
| Calibrated implemented | 27 | 0 |
| Calibrated refused | 0 | 27 |
| Judgment-assisted routed | 64 | 64 |
| Context-only routed | 7 | 7 |
| Not-detectable blocked | 3 | 3 |
| Total refusals | 74 | 101 |

---

## Safe State/Action-Label Fallback Mappings Used

For calibrated classifications, several detectors emit states that do not directly appear in the contract's action label vocabulary. The `_action_for()` function in `calibrated.py` maps states to the nearest safe action label using keyword matching against the contract's allowed action labels. Mappings used in the example output:

| Concept | Emitted State | Mapped Action |
|---------|--------------|---------------|
| `ch02_break_quality` | `IMPULSIVE_BREAK_TEXTURE` | `OBSERVE` |
| `ch03_auction_acceptance_vs_rejection` | `CONFIRMATION_REQUIRED` | `CONFIRMATION_REQUIRED` |
| `ch03_completed_failed_and_unfinished_auctions` | `COMPLETED_AUCTION` | `OBSERVE` |
| `ch03_the_auction_framework` | `BALANCED_AUCTION_CONTEXT` | `CONTEXT_ONLY` |
| `ch03_volume_nodes_and_air_pockets` | `LOW_VOLUME_NODE_IDENTIFIED` | `OBSERVE` |
| `ch05_follow_through_and_failure` | `FOLLOW_THROUGH_CONFIRMED` | `OBSERVE` |
| `ch06_stop_out_cascades_and_liquidation` | `CASCADE_LIKE_BEHAVIOR` | `OBSERVE` |
| `ch07_asia_session_character` | `ASIA_REPRICING_CONTEXT` | `CONTEXT_ONLY` |
| `ch08_compression_breakouts_real_vs_false` | `ACCEPTED_COMPRESSION_BREAK` | `OBSERVE` |
| `ch08_expanded_volatility_no_trade_condition` | `EXPANDED_VOLATILITY_ENVIRONMENT_BLOCK` | `OBSERVE` |
| `ch08_volatility_crush_and_reset` | `POST_EVENT_NORMALIZATION` | `OBSERVE` |
| `ch09_breadth_confirmation_and_divergence` | `BREADTH_CONFIRMS_PRICE` | `OBSERVE` |
| `ch12_execution_environment_quality_and_veto` | `ENVIRONMENT_QUALITY_ACCEPTABLE_CONTEXT` | `CONTEXT_ONLY` |

---

## Boundary Confirmation

| Boundary | Status |
|----------|--------|
| No trade permission | ✅ Confirmed |
| No entries/stops/targets/sizing | ✅ Confirmed |
| No broker/order/account/fill/P&L behavior | ✅ Confirmed |
| No production calibration values | ✅ Confirmed — all values labeled `example_value_for_runtime_wiring_only` |
| No real instrument profiles | ✅ Confirmed — instrument is `SYNTH-FUT (fabricated non-tradable example contract)` |
| No JUDGMENT_ASSISTED decision logic | ✅ Confirmed — JUDGMENT_ASSISTED remains review-routed |
| No forbidden execution fields in any output | ✅ Confirmed — recursive check passes on all 110 outputs |
| Guardrail booleans always true | ✅ Confirmed |

---

## Remaining Blockers

**None.**

---

## Operator Usage

### Run calibrated detector runtime

```bash
python3 scripts/run_detector_runtime.py qa/examples/detector_runtime_calibrated_input.example.json --calibration-profile qa/examples/detector_runtime_calibrated_profile.example.yaml --output qa/examples/detector_runtime_calibrated_output.example.json
```

### Validate calibrated output

```bash
python3 scripts/validate_detector_output.py qa/examples/detector_runtime_calibrated_output.example.json
```

### Run without profile (proves safe refusal)

```bash
python3 scripts/run_detector_runtime.py qa/examples/detector_runtime_calibrated_input.example.json --output qa/examples/detector_runtime_missing_calibration_output.example.json
```

### Run single calibrated concept

```bash
python3 scripts/run_detector_runtime.py qa/examples/detector_runtime_calibrated_input.example.json --calibration-profile qa/examples/detector_runtime_calibrated_profile.example.yaml --concept-id ch02_acceptance_vs_rejection
```

### Run all tests

```bash
python3 -m unittest tests/test_detector_runtime_v1.py tests/test_calibrated_detector_runtime_v1.py
```
