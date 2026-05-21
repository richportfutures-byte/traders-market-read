# P15 Detection Specs Wave 2 Report

## Executive Result

- **Result: P15_PASS.**
- **Files created:**
  - `spec/detection_specs/ch03_auction_acceptance_vs_rejection.yaml`
  - `spec/detection_specs/ch05_one_timeframing.yaml`
  - `spec/detection_specs/ch07_rth_open_location.yaml`
  - `spec/detection_specs/ch08_compression_vs_expansion.yaml`
  - `spec/detection_specs/ch08_inside_outside_and_narrow_wide_range_days.yaml`
  - `qa/p15_detection_specs_wave_2_report.md`
- **Concepts covered:** Auction Acceptance vs. Rejection; One-Timeframing; RTH Open Location; Compression vs. Expansion; Inside/Outside & Narrow/Wide Range Days.
- **Detection-spec count before and after:** 5 before; 10 after.
- **Schema/YAML validation result:** Passed. PyYAML parsed all 10 detection specs successfully.
- **Registry alignment result:** Passed. All five concept IDs, names, chapters, glossary paths, and determinism classes match `spec/concept_registry.yaml` and `qa/concept_determinism_matrix.csv`.
- **Forbidden-output check result:** Passed. Targeted forbidden execution-token scan returned no hits, and every spec carries schema-prohibited outputs and non-executional boundaries.
- **Concepts requiring GPT-5.5 doctrine review:** None identified.
- **Remaining blockers:** None.

## Concepts Covered

| Concept | Concept ID | Determinism Class | Spec File | Emitted-State Summary |
|---|---|---|---|---|
| Auction Acceptance vs. Rejection | `ch03_auction_acceptance_vs_rejection` | CALIBRATED | `spec/detection_specs/ch03_auction_acceptance_vs_rejection.yaml` | `AUCTION_PENDING`, `AUCTION_ACCEPTED`, `AUCTION_REJECTED`, confirmation/review/degraded/refusal states |
| One-Timeframing | `ch05_one_timeframing` | COMPUTABLE | `spec/detection_specs/ch05_one_timeframing.yaml` | One-timeframing higher/lower, loss of one-timeframing, no one-timeframing, pending/refusal states |
| RTH Open Location | `ch07_rth_open_location` | COMPUTABLE | `spec/detection_specs/ch07_rth_open_location.yaml` | Open relative to overnight range, prior RTH range, prior value, near-reference, structural context/refusal states |
| Compression vs. Expansion | `ch08_compression_vs_expansion` | CALIBRATED | `spec/detection_specs/ch08_compression_vs_expansion.yaml` | Compression, expansion, transition, failed expansion, structural volatility context, degraded/refusal states |
| Inside/Outside & Narrow/Wide Range Days | `ch08_inside_outside_and_narrow_wide_range_days` | COMPUTABLE | `spec/detection_specs/ch08_inside_outside_and_narrow_wide_range_days.yaml` | Inside day, outside day, one-sided extension, overlapping range, narrow/typical/wide range, developing/refusal states |

## File Naming Note

The expected filename list shortened the final file to `ch08_inside_outside_narrow_wide_range_days.yaml`. The created file is `ch08_inside_outside_and_narrow_wide_range_days.yaml` because the registry concept ID is `ch08_inside_outside_and_narrow_wide_range_days`, and the existing P14 convention names each detection spec file exactly after `concept_id`.

## Calibration Boundary Notes

- `ch03_auction_acceptance_vs_rejection` defines the calibrated auction-state rule structure but leaves dwell, TPO/volume-development, extension-buffer, and rejection-window parameters as `value: null` with `status: calibration_required`.
- `ch08_compression_vs_expansion` defines range, overlap, realized-volatility, and failed-expansion parameter names without assigning universal values.
- `ch08_inside_outside_and_narrow_wide_range_days` keeps inside/outside labels computable but requires calibrated historical range context before emitting narrow/wide labels.
- `ch05_one_timeframing` and `ch07_rth_open_location` use method configuration where needed and keep interpretation separate from computable structural labels.
- No calibration profile or threshold file was created.

## Missing-Feed And Downgrade Behavior Summary

| Concept ID | Missing Required Feed Behavior | Optional Feed Downgrade Behavior |
|---|---|---|
| `ch03_auction_acceptance_vs_rejection` | Refuses without profile distribution, price sequence, auction reference, session clock, or calibration | Missing value, single-print, or delta evidence produces degraded confidence rather than acceptance claims |
| `ch05_one_timeframing` | Refuses without period bars, period definition, or session clock; incomplete current period stays pending | Missing profile/value/tape/day-type context leaves structural state only |
| `ch07_rth_open_location` | Refuses without session clock, RTH open, overnight range, or prior RTH range | Missing value data omits value-relative labels; missing late-overnight structure omits that context |
| `ch08_compression_vs_expansion` | Refuses without price/session inputs; emits insufficient evidence without statistics or calibration | Missing profile, value, tape, or event context downgrades to structural volatility context |
| `ch08_inside_outside_and_narrow_wide_range_days` | Refuses without session definitions or current/prior high-low data | Missing range history withholds narrow/wide labels; missing value/tape context withholds auction-meaning claims |

## Boundary Review

- No spec emits trade permission, entries, exits, stops, targets, position sizing, broker/order/account/fill/P&L behavior, or autonomous trade calls.
- Computable specs emit structural context only and keep interpretation separate.
- Calibrated specs define rule structure and named parameters only; no parameter values were invented.
- Judgment-heavy interpretation such as sponsorship, trend quality, reversal, setup quality, and location quality remains outside these specs.

## Verification Results

- Confirmed all five new YAML files exist.
- Confirmed `spec/detection_specs/*.yaml` count is 10.
- Confirmed PyYAML parses all 10 detection specs.
- Confirmed each new `concept_id` exists in `spec/concept_registry.yaml`.
- Confirmed each new `determinism_class` matches the registry and `qa/concept_determinism_matrix.csv`.
- Confirmed each `review_status` is schema-valid (`DRAFT`).
- Confirmed forbidden execution tokens are absent from the five new specs.
- Confirmed calibration-required parameters in the five new specs have `value: null`.
- Confirmed no calibration files were created.

## Deferred Work

- Individual P15 backlog specs beyond this wave.
- Calibration values and calibration profiles.
- Detector implementation code.
- Validation test files and fixtures.
- Doctrine review beyond the five approved P14-candidate concepts.

## Final Recommendation

Proceed with the next detection-spec wave.

Next step: choose the next bounded set of registry-backed spec candidates, continuing to prioritize low false-determinism risk and clean feed availability.
