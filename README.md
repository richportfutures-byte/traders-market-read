# Trader's Market-Read Glossary

A structured futures-trading market-read doctrine, semantic glossary, and detection/specification architecture.

This project defines how discretionary market observations should be described, classified, validated, and translated into machine-usable specifications without turning trader judgment into false deterministic trade signals.

The repository is organized around three linked layers:

1. **Semantic Layer**  
   Human-readable trader doctrine. This layer explains what each market-read concept means, why it happens, how traders identify it, what it implies, what confirms or invalidates it, and how it relates to other concepts.

2. **Detection and Specification Layer**  
   Machine-usable implementation contracts. This layer defines concept identifiers, required inputs, optional inputs, determinism class, detection logic, refusal behavior, missing-feed behavior, calibration requirements, known false-positive modes, and allowed output labels.

3. **Calibration Layer**  
   Instrument-specific profiles that keep thresholds empirical, contextual, and product-specific rather than universal or invented.

The core discipline of the project is simple:

> A market read is not a trade command.  
> A concept can be useful without being actionable.  
> A concept can be observable without being deterministic.  
> A concept can be trader-realistic without being safe to automate.

---

## Project Status

The repository currently contains the full twelve-chapter semantic glossary structure, 110 per-concept detection specifications, generated detector/catalog artifacts, calibration contract schema, validation scripts, and quality-assurance artifacts.

Current repository layout:

```text
/Users/stu/Projects/traders-market-read/
  README.md
  PROJECT_PROTOCOL.md

  glossary/
    chapter_01_read_discipline_interpretation_method.md
    chapter_02_level_interaction_acceptance.md
    chapter_03_auction_market_profile.md
    chapter_04_tape_reading_microstructure.md
    chapter_05_momentum_follow_through_day_types.md
    chapter_06_traps_positioning.md
    chapter_07_session_context_sequencing.md
    chapter_08_volatility_regime.md
    chapter_09_intermarket_confirmation.md
    chapter_10_catalyst_interpretation.md
    chapter_11_trade_state_management.md
    chapter_12_setup_quality_action_vocabulary.md

  qa/
    glossary_to_spec_traceability.csv
    calibration_parameter_inventory.csv
    detector_contract_catalog_summary.md
    examples/
      detector_output_valid.example.json
      detector_output_invalid_execution.example.json
    p20/p21/p22/p23 reports and prior QA artifacts

  spec/
    concept_registry.yaml
    detection_spec_schema.yaml
    detector_contract_catalog.json
    detector_output_schema.yaml
    detection_specs/
      110 per-concept YAML specs

  calibration/
    calibration_profile_schema.yaml

  scripts/
    validate_detection_specs.py
    extract_calibration_inventory.py
    build_detector_contract_catalog.py
    validate_detector_output.py
```

---

## Non-Execution Boundary

This repository is not a trading bot, signal engine, broker-integration layer, position-sizing engine, or autonomous execution system.

The project may define concepts such as acceptance, rejection, liquidity sweeps, trapped traders, value migration, tape quality, volatility regime, catalyst transmission, and setup quality. It must not produce or imply autonomous trading behavior.

The following are explicitly out of scope:

- Broker/order routing.
- Account access.
- Live order placement.
- Position sizing.
- Exact entries.
- Exact stops.
- Exact targets.
- Automated exits.
- Automated adds.
- P&L-driven behavior.
- Any claim that a market-read label alone authorizes a trade.

The project can support structured interpretation, review, monitoring, and future implementation. It cannot collapse interpretation into execution permission.

---

## Why This Project Exists

Discretionary trader language is often rich but ambiguous. Software systems are often precise but shallow. This project closes that gap by separating trader-realistic meaning from machine-readable detection contracts.

The project is designed to prevent three common failures:

1. **Chart-pattern reduction**  
   Reducing complex market behavior to simple pattern labels such as breakout, rejection, trend, chop, or reversal without explaining the auction logic behind them.

2. **False precision**  
   Inventing hard thresholds, numeric scores, or universal rules for observations that are product-specific, session-specific, regime-specific, or partly discretionary.

3. **Execution leakage**  
   Allowing a valid market observation to become an implied trade instruction without separate confirmation, location quality, risk environment, and operator judgment.

A central doctrine runs through every chapter:

> Do not describe only that price touched a level.  
> Describe what the auction did with that touch.

---

## Repository Architecture

### Root Files

#### `README.md`

The operating overview for the project. It explains the purpose, structure, boundaries, workflow, and maintenance expectations.

#### `PROJECT_PROTOCOL.md`

The governing protocol for the project. It defines the separation between semantic doctrine, detection specifications, calibration profiles, quality controls, and agent workflows.

---

## Glossary Layer

The `glossary/` directory contains the human-readable market-read doctrine.

Each chapter is written for trader interpretation first. The entries are intended to sound like experienced market-reading notes, not compliance language, not generic chart-pattern descriptions, and not software schema.

Each glossary concept should answer:

- What does this concept mean?
- Why does it happen?
- What does a trader watch?
- What does it imply?
- What is commonly misread?
- What confirms it?
- What invalidates it?
- What related concepts should it link to?
- How ready is the concept for detection or specification?

### Chapter 1: Read Discipline & Interpretation Method

File:

```text
glossary/chapter_01_read_discipline_interpretation_method.md
```

Chapter 1 defines the operating discipline for the entire project. It governs how every later read is formed, weighted, confirmed, invalidated, and kept honest.

Primary themes:

- The read versus the touch.
- Signal conflict taxonomy.
- Leading versus coincident signals.
- Context versus execution permission.
- Confirmation and invalidation discipline.
- Tape-confirms-narrative rule.
- Product-specific behavior.
- False precision and observation tracking.

This chapter is the guardrail against turning the glossary into a signal factory.

### Chapter 2: Level Interaction & Acceptance

File:

```text
glossary/chapter_02_level_interaction_acceptance.md
```

Chapter 2 governs what price does at and through levels.

Primary themes:

- Structural reference levels.
- Acceptance versus rejection.
- Breakout continuation versus breakout failure.
- Liquidity sweep versus real break.
- Break quality.
- Level magnetism and decay.
- Level test sequence.
- Polarity flips.
- Mechanical levels and obvious traps.

This chapter supplies the project’s most basic market-reading discipline: a level touch is not a signal until the post-touch behavior is interpreted.

### Chapter 3: Auction & Market Profile

File:

```text
glossary/chapter_03_auction_market_profile.md
```

Chapter 3 defines the structural skeleton of the auction.

Primary themes:

- Balanced versus imbalanced auction.
- Auction acceptance versus rejection.
- Initiative versus responsive activity.
- Completed, failed, and unfinished auctions.
- Excess versus poor highs/lows.
- VAH, VAL, and POC.
- Value migration and overlap.
- Price outside value.
- Volume nodes and air pockets.
- Single prints.
- Initial Balance.
- VWAP relationship.
- Overnight inventory.
- Short-covering versus long-liquidation auctions.
- Fresh flow versus weak/strong hands.

This chapter defines where price is in the auction and what kind of auction is developing.

### Chapter 4: Tape Reading & Microstructure

File:

```text
glossary/chapter_04_tape_reading_microstructure.md
```

Chapter 4 covers live order-flow behavior and execution-environment quality.

Primary themes:

- Absorption.
- Refreshing liquidity.
- Chasing versus pressing.
- Stall and snap-back.
- Tape quality spectrum.
- Tape versus narrative.
- Spread behavior.
- Liquidity pulls and replenishment.
- Sweeps through liquidity.
- Cumulative delta and delta divergence.

This chapter explains what the live tape is saying independent of structural location. Structure tells the trader where to care; tape tells the trader whether the behavior is confirming, refusing, deteriorating, or unreadable.

### Chapter 5: Momentum, Follow-Through & Day Types

File:

```text
glossary/chapter_05_momentum_follow_through_day_types.md
```

Chapter 5 governs directional pressure and session development.

Primary themes:

- Impulse versus grind.
- Momentum ignition, stall, and exhaustion.
- Follow-through and failure.
- Exhaustion.
- Close quality.
- One-timeframing.
- Day-type taxonomy.

This chapter separates speed from sponsorship. Fast is not automatically strong; slow is not automatically weak. The trader reads whether movement is accepted, sponsored, defended, rejected, or exhausted.

### Chapter 6: Traps & Positioning

File:

```text
glossary/chapter_06_traps_positioning.md
```

Chapter 6 governs the positioning layer of the market read.

Primary themes:

- Trapped traders.
- Strong hands defending.
- Stop-out cascades and liquidation.
- Short-covering rally.
- Crowded trades and pain trades.
- Dealer gamma dynamics.
- Mechanical flows such as rebalance, month-end, roll, and auction-tail positioning.

This chapter asks who is vulnerable, who is defending, where forced flow may appear, and whether a move is fresh initiative or pain relief.

### Chapter 7: Session Context & Sequencing

File:

```text
glossary/chapter_07_session_context_sequencing.md
```

Chapter 7 reads the futures market as a 24-hour auction sequence rather than isolated candles.

Primary themes:

- Asia, London, and NY handoff.
- Asia session character.
- London initiative and traps.
- NY inheritance versus rejection.
- RTH open location.
- Opening type taxonomy.
- Intraday time windows.
- Session quality versus session completion.

This chapter prevents shallow time-zone labeling. A session matters because of what it contributes to the auction, not merely because it occurred during Asia, London, or NY hours.

### Chapter 8: Volatility Regime

File:

```text
glossary/chapter_08_volatility_regime.md
```

Chapter 8 governs the volatility layer of the read.

Primary themes:

- Compression versus expansion.
- Expansion outcomes: trend, chop, exhaustion, or failure.
- Volatility crush and reset.
- Event volatility regime.
- Liquidity-driven volatility.
- Volatility-adjusted level quality.
- Expanded-volatility no-trade conditions.

This chapter explains how movement environment changes the reliability of every other read.

### Chapter 9: Intermarket Confirmation

File:

```text
glossary/chapter_09_intermarket_confirmation.md
```

Chapter 9 governs whether related markets confirm, contradict, lead, lag, ignore, or reprice the story being told by the traded contract.

Primary themes:

- General intermarket confirmation.
- NQ/ES relative strength and index internals.
- Breadth confirmation and divergence.
- VIX, credit, and cross-asset risk tone.
- Rates and dollar transmission.
- Gold intermarket drivers.
- Crude intermarket drivers.
- FX and euro confirmation.
- Treasury/rates influence.

This chapter treats related markets as evidence, not rules. Confirmation improves read quality; it does not create trade permission.

### Chapter 10: Catalyst Interpretation

File:

```text
glossary/chapter_10_catalyst_interpretation.md
```

Chapter 10 governs how traders interpret news, data releases, central-bank language, policy headlines, inventory reports, geopolitical headlines, and other information events.

Primary themes:

- New information versus recycled context.
- Pricing-in.
- Transmission mechanism and order effects.
- Source quality.
- Catalyst effect on thesis.
- Catalyst-to-trade translation.
- Event volatility and first reaction.
- Tape confirms or rejects narrative.
- Delayed, stale, or post-hoc catalyst explanations.

This chapter enforces the rule that market response is senior to the story.

### Chapter 11: Trade-State Management

File:

```text
glossary/chapter_11_trade_state_management.md
```

Chapter 11 governs live thesis state.

Primary themes:

- Thesis state lifecycle.
- Thesis confirmation versus execution permission.
- Thesis weakening and degradation.
- Thesis invalidation.
- Stale thesis.
- Thesis replacement and supersession.
- Trade-working diagnosis.
- Review or stand-aside state.
- Observation tracking.

This chapter prevents a trader or system from protecting a story after the market has changed.

### Chapter 12: Setup Quality & Action Vocabulary

File:

```text
glossary/chapter_12_setup_quality_action_vocabulary.md
```

Chapter 12 governs the final semantic filter between a market read and an operator posture.

Primary themes:

- Setup cleanliness and timing.
- Location quality.
- Asymmetry and practical reward-to-risk.
- Invalidation and confirmation clarity.
- Alignment across dimensions.
- Execution environment quality.
- Setup fragility.
- Action vocabulary.

This chapter defines the language for no-action states, confirmation-required states, review states, poor-location states, insufficient-evidence states, and clean-but-non-executional monitoring states.

---

## Detection Specification Layer

The `spec/` directory contains the machine-readable implementation layer.

The detection layer is not the glossary. It does not explain concepts like a trader. It defines how concepts can or cannot be represented in structured systems.

Detection specs should answer:

- Can this concept be detected deterministically?
- What data feed is required?
- What data feed is optional?
- What parameters are needed?
- Are the parameters fixed, calibrated, or discretionary?
- What states can the detector emit?
- When should the detector refuse to decide?
- What failure modes create false positives?
- What tests prove the rule behaves correctly?

### Core Spec Files

#### `spec/concept_registry.yaml`

Canonical registry of concepts.

Expected responsibilities:

- Stable concept IDs.
- Display names.
- Chapter references.
- Domain grouping.
- Determinism class.
- Glossary anchor reference.
- Specification reference.
- Calibration requirement.
- Output label family.
- Feed dependency class.

This file is the bridge between human-readable glossary entries and machine-readable specifications.

#### `spec/detection_spec_schema.yaml`

Schema for validating detection specification files.

Expected responsibilities:

- Required top-level fields.
- Allowed determinism classes.
- Required input and optional input structure.
- Parameter and calibration structure.
- Missing-feed behavior.
- Refusal behavior.
- Confidence behavior.
- Output labels.
- Known failure modes.
- Test expectations.

#### `spec/detector_contract_catalog.json`

Generated machine-readable catalog compiled from all detection specs. It normalizes each concept's declared inputs, parameters, emitted states, allowed non-executional action labels, refusal behavior, failure modes, and boundary flags.

#### `spec/detector_output_schema.yaml`

Minimal output contract for future detector implementations. It defines the allowed non-executional output shape and forbids execution fields such as entries, stops, targets, sizing, broker/order/account/fill/P&L behavior, and autonomous trading instructions.

### Per-Concept Detection Specs

The `spec/detection_specs/` directory contains 110 per-concept YAML detection contracts.

```text
spec/detection_specs/
  ch01_*.yaml
  ch02_*.yaml
  ...
  ch12_*.yaml
```

Each file maps one glossary concept to a bounded detector contract.

Detection specs should never invent data. If a concept requires DOM, footprint, cumulative delta, breadth, primary-source news, event-calendar data, profile data, or intermarket inputs, the spec must say so explicitly.

If a required feed is missing, the correct output is not a guessed label. It is a refusal, downgrade, context-only label, or insufficient-evidence state.

---

## Determinism Classes

Every concept should be classified before writing detection rules.

### `COMPUTABLE`

The concept can be calculated directly from available data and mathematical definitions.

Examples:

- Prior high and low.
- Session open.
- VWAP.
- Initial Balance high and low.
- Inside day.
- Outside day.
- Price relative to a known reference.

Computable does not mean actionable. It only means the observation itself is mechanically definable.

### `CALIBRATED`

The rule structure can be deterministic, but parameters must be calibrated by instrument, timeframe, session, and volatility regime.

Examples:

- Acceptance versus rejection.
- Break quality.
- Level decay.
- Compression versus expansion.
- Tape speed.
- Range expansion.
- Breadth divergence.
- Volatility-adjusted location quality.

Calibrated concepts must not use universal thresholds unless the threshold is a mathematical definition. Values should come from empirical calibration profiles.

### `JUDGMENT_ASSISTED`

The concept requires human or LLM-assisted interpretation because it depends on sequence, context, hierarchy, narrative, product behavior, or participant inference.

Examples:

- Trapped traders.
- Strong hands defending.
- Tape disagrees with narrative.
- Catalyst transmission.
- Thesis weakening.
- Setup cleanliness.
- Intermarket confirmation quality.

Judgment-assisted concepts can be supported by computable and calibrated sub-signals, but the final interpretation should not pretend to be fully deterministic.

### `CONTEXT_ONLY`

The concept is useful for market interpretation but must not produce an actionable trigger.

Examples:

- Thesis confirmation versus execution permission.
- Broad macro backdrop.
- Catalyst context without accepted repricing.
- Session color.
- Market story without expression quality.

Context-only labels are valid outputs. They protect the system from action bias.

### `NOT_DETECTABLE_WITH_CURRENT_FEEDS`

The concept requires data that is not available in the current system.

Examples:

- DOM-based absorption without level-2/order-book data.
- Iceberg behavior without order-book events.
- Breadth confirmation without breadth feeds.
- Primary-source catalyst novelty without news/event data.
- Footprint-based delta divergence without footprint or bid/ask classified trade data.

The correct behavior is to state that the concept cannot be detected with current feeds.

---

## Calibration Layer

The `calibration/` directory prevents false precision.

### Core File

```text
calibration/calibration_profile_schema.yaml
```

This schema defines how future calibration profiles should express instrument-specific parameters.

Calibration should account for:

- Instrument.
- Session.
- Timeframe.
- Volatility regime.
- Data sample.
- Historical period.
- Parameter value.
- Confidence.
- Expiration or invalidation condition.
- Feed assumptions.
- Regime constraints.

No real instrument calibration profiles exist yet.

The project explicitly rejects the idea that a threshold calibrated for one product automatically applies to another. ES, NQ, CL, 6E, and MGC behave differently. MGC is Micro Gold and should not be casually treated as equivalent to GC.

A valid calibration profile should make clear whether a value applies to:

- A specific instrument.
- A specific session.
- A specific timeframe.
- A specific volatility regime.
- A specific data feed quality.
- A specific historical sample.

---

## QA and Traceability Layer

The `qa/` directory exists to keep the semantic layer, detection layer, and calibration layer aligned.

### `qa/chapter_corpus_inventory.md`

Tracks the current chapter corpus.

Expected responsibilities:

- List all glossary chapters.
- Track chapter status.
- Identify missing or weak sections.
- Note structural inconsistencies.
- Track chapter-level completion.

### `qa/semantic_quality_checklist.md`

Checklist for human-readable glossary quality.

Semantic entries should be checked for:

- Trader-realistic language.
- Clear distinction from common misreads.
- No fake precision.
- No execution leakage.
- Clear confirmation and invalidation.
- Cross-link integrity.
- Proper detection-readiness classification.
- Separation of structure, tape, catalyst, volatility, intermarket, session, thesis, and setup-quality layers.

### `qa/detection_spec_quality_checklist.md`

Checklist for machine-readable spec quality.

Detection specs should be checked for:

- Stable concept IDs.
- Explicit required inputs.
- Explicit optional inputs.
- Missing-feed behavior.
- Determinism class.
- Calibration requirements.
- Refusal behavior.
- Output labels.
- Failure modes.
- Test expectations.
- No invented thresholds.
- No implied trade authorization.

### `qa/concept_coverage_matrix.csv`

Tracks concept coverage across the full project.

Expected responsibilities:

- Concept name.
- Concept ID.
- Chapter.
- Glossary status.
- Spec status.
- Calibration requirement.
- Determinism class.
- Feed dependency.
- Traceability status.
- Review status.

### `qa/glossary_to_spec_traceability.csv`

Maps glossary entries to detection specs.

Expected responsibilities:

- Glossary chapter.
- Glossary heading.
- Concept ID.
- Detection spec file.
- Detection spec anchor or key.
- Determinism class.
- Calibration profile requirement.
- Missing-feed behavior.
- Output label family.

This file is critical because it prevents orphaned glossary concepts and orphaned detection specs.

### `qa/calibration_parameter_inventory.csv`

Generated inventory of named calibration/configuration parameters declared by the detection specs. It records parameter names and metadata only; it does not assign values.

### `qa/detector_contract_catalog_summary.md`

Lightweight summary of the generated detector contract catalog.

### `qa/examples/`

Contains minimal detector-output validation examples:

- `detector_output_valid.example.json`
- `detector_output_invalid_execution.example.json`

### P20-P23 Reports and Prior QA Artifacts

The `qa/` directory also contains phase reports and earlier quality artifacts used to track validation, traceability, calibration-contract, catalog, and detector-output work.

---

## Recommended Workflow

### Phase 0: Inventory and Protocol Alignment

Goal:

Confirm the repository structure, protocol, current chapters, QA artifacts, and spec files.

Deliverables:

- Updated `chapter_corpus_inventory.md`.
- Confirmed chapter list.
- Confirmed spec file list.
- Confirmed calibration schema and calibration-profile status.
- Confirmed protocol alignment.

Do not silently promote old drafts, uploaded files, or unrelated project protocols into source of truth.

### Phase 1: Semantic Layer Review

Goal:

Ensure every glossary chapter is conceptually strong, trader-realistic, internally consistent, and properly bounded.

Review each entry for:

- Clear core concept.
- Why it happens.
- Practical implications.
- How traders identify it.
- Common misreads.
- Confirmation and invalidation.
- Detection readiness.
- One-line summary.
- See also links.

Reject entries that sound like:

- Generic chart-pattern summaries.
- Compliance reports.
- Software schema.
- Overconfident trading rules.
- Post-hoc narrative explanations.
- Exact execution recommendations.

### Phase 2: Determinism Triage

Goal:

Assign or verify determinism class for every concept.

Every concept must be one of:

- `COMPUTABLE`
- `CALIBRATED`
- `JUDGMENT_ASSISTED`
- `CONTEXT_ONLY`
- `NOT_DETECTABLE_WITH_CURRENT_FEEDS`

The determinism class should be justified by data requirements and interpretation requirements.

### Phase 3: Detection Specification Authoring

Goal:

Build or reconcile machine-readable detection specs.

Each detection spec should include:

- `concept_id`
- `display_name`
- `glossary_ref`
- `chapter`
- `determinism_class`
- `description`
- `required_inputs`
- `optional_inputs`
- `parameters`
- `calibration`
- `detection_logic`
- `allowed_outputs`
- `confidence_behavior`
- `missing_feed_behavior`
- `refusal_behavior`
- `known_failure_modes`
- `test_expectations`

Detection specs should be implementation contracts, not prose essays.

### Phase 4: Calibration Profile Development

Goal:

Create instrument-specific and regime-specific calibration profiles.

Profiles should be empirical and explicit.

Do not write:

```text
acceptance_dwell_minutes: 30
```

as if it is universally true.

Write calibration values as contextual parameters tied to instrument, session, timeframe, volatility regime, sample, and feed quality.

### Phase 5: QA and Traceability

Goal:

Ensure every glossary concept has a traceable spec status and every spec maps back to a glossary concept.

QA should verify:

- No orphan glossary concepts.
- No orphan detection specs.
- No concept with missing determinism class.
- No spec with hidden feed assumptions.
- No invented thresholds.
- No unsupported execution labels.
- No cross-link drift.
- No mismatch between glossary meaning and detection output.

---

## Concept Entry Standard

A strong glossary entry should use this structure:

```markdown
## Concept Name

### Core Concept

Plain-language trader definition with sharp distinction from common misreads.

### Why It Happens

Driver and mechanism table.

### Practical Implications

Concrete trader implications without autonomous trade instruction.

### How Traders Identify It

Observable tells, separated from confirmation requirements.

### Common Misreads

What traders, LLMs, or coders often confuse it with.

### Confirmation and Invalidation

What strengthens, weakens, confirms, or invalidates the read.

### Detection Readiness

Computable, calibrated, judgment-assisted, context-only, or not detectable with current feeds.

### One-Line Summary

Trader-style compression.

### See Also

Cross-links.
```

Not every legacy chapter entry may perfectly match this structure. The project should converge toward this standard as chapters are reviewed and refined.

---

## Detection Spec Standard

A strong detection spec should use this conceptual shape:

```yaml
concept_id: acceptance_rejection_level
display_name: Acceptance vs. Rejection
glossary_ref: glossary/chapter_02_level_interaction_acceptance.md#acceptance-vs-rejection
chapter: 2
determinism_class: CALIBRATED

description: >
  Level-specific read of whether price accepted beyond, rejected from,
  or briefly accepted and then failed back through a structural reference.

required_inputs:
  - name: structural_level
    type: price
    source: structural_reference_module
    required: true

  - name: trade_prints_or_bars
    type: market_data
    granularity: tick_or_1m
    required: true

optional_inputs:
  - name: volume_at_price
    type: profile_data
    required: false

  - name: cumulative_delta
    type: order_flow
    required: false

parameters:
  - name: acceptance_dwell
    calibration_required: true
    scope:
      - instrument
      - session
      - timeframe
      - volatility_regime

allowed_outputs:
  - ACCEPTED_ABOVE
  - ACCEPTED_BELOW
  - REJECTED_FROM_ABOVE
  - REJECTED_FROM_BELOW
  - FAILED_ACCEPTANCE
  - PENDING
  - INSUFFICIENT_EVIDENCE

missing_feed_behavior:
  volume_at_price: downgrade_confidence
  trade_prints_or_bars: refuse

refusal_behavior:
  - missing_structural_level
  - missing_price_sequence
  - insufficient_observation_window

known_failure_modes:
  - stop_run_misclassified_as_acceptance
  - thin_liquidity_probe_misclassified_as_rejection
  - gap_through_level_without_trade_misclassified_as_clean_acceptance
```

The exact schema is governed by `spec/detection_spec_schema.yaml`.

---

## Output Labels

Action vocabulary should describe evidence state, read quality, setup quality, or operator posture. It should not trigger execution.

Examples of safe labels:

- `CONTEXT_ONLY`
- `CONFIRMATION_REQUIRED`
- `REVIEW_REQUIRED`
- `INSUFFICIENT_EVIDENCE`
- `NOT_DETECTABLE_WITH_CURRENT_FEEDS`
- `THESIS_VALID_BUT_NO_CLEAN_EXPRESSION`
- `TRIGGER_VALID_BUT_LOCATION_POOR`
- `STRUCTURE_VALID_BUT_TAPE_UNCONFIRMED`
- `MARKET_READ_WEAKENED`
- `STAND_ASIDE`
- `NO_CLEAN_EXPRESSION`
- `MEDIUM_REQUIRES_SHADOW_ONLY`

Unsafe labels would be any labels that imply autonomous execution, such as:

- `BUY_NOW`
- `SELL_NOW`
- `ENTER_LONG`
- `ENTER_SHORT`
- `PLACE_STOP`
- `TARGET_HIT`
- `SIZE_UP`
- `AUTO_EXECUTE`
- `ORDER_APPROVED`

Those labels do not belong in this project.

---

## Data Dependency Rules

Detection specifications must be explicit about data requirements.

Examples:

- Absorption may require footprint, DOM, delta, or at least high-quality trade and volume behavior.
- Refreshing liquidity requires order-book behavior and should not be claimed from ordinary bars alone.
- Breadth confirmation requires breadth or constituent/index-internals data.
- Catalyst novelty requires source timestamps, event calendars, consensus expectations, and primary-source or trusted news data.
- Value migration requires Market Profile, volume-at-price, TPO, or a defined value-area method.
- Intermarket confirmation requires related-market feeds.
- Tape quality may require tick data, spread history, trade classification, depth, or lower-confidence bar proxies.

If the feed does not exist, the system must not invent the read.

The correct behavior is one of:

- Refuse.
- Downgrade confidence.
- Emit `INSUFFICIENT_EVIDENCE`.
- Emit `NOT_DETECTABLE_WITH_CURRENT_FEEDS`.
- Emit a context-only or structural-only version of the read.
- Require review.

---

## False Precision Rules

Do not hardcode universal thresholds for qualitative market reads.

Bad:

```text
Acceptance means price holds above the level for 30 minutes.
```

Better:

```text
Acceptance requires dwell and activity beyond the level. The dwell threshold is a calibrated parameter scoped by instrument, session, timeframe, and volatility regime.
```

Bad:

```text
If delta diverges by 20%, absorption is confirmed.
```

Better:

```text
Delta-price divergence can support an absorption read only when the required trade-classification feed exists, the divergence threshold is calibrated, and price fails to displace despite sufficient aggressive effort.
```

Bad:

```text
Three touches always weakens a level.
```

Better:

```text
Repeated tests can weaken a level when each test consumes defensive liquidity and produces progressively weaker response. The test-count window and reaction-quality threshold require calibration.
```

---

## Review Standards

A chapter, spec, or calibration profile is not complete simply because a file exists.

### A glossary chapter is complete when:

- The concepts are trader-realistic.
- Common misreads are named.
- Confirmation and invalidation are explicit.
- Detection readiness is honest.
- Context is separated from execution permission.
- Cross-links are useful.
- The chapter does not invent precision.
- The chapter does not reduce live-market behavior to generic patterns.

### A detection spec is complete when:

- Concept ID is stable.
- Required feeds are explicit.
- Optional feeds are explicit.
- Missing-feed behavior is explicit.
- Determinism class is assigned.
- Parameters are marked fixed, calibrated, or discretionary.
- Output labels are bounded and non-executional.
- Refusal behavior exists.
- Known false positives are documented.
- Tests can validate behavior.

### A calibration profile is complete when:

- Instrument is named.
- Session/timeframe are named.
- Volatility regime is named.
- Data sample is named.
- Parameter values are empirical.
- Confidence is stated.
- Expiration or invalidation condition is stated.
- Feed assumptions are stated.

---

## Contributor and Agent Rules

Any contributor or coding agent working in this repo must follow these rules:

1. Do not conflate semantic glossary entries with detection specs.
2. Do not turn market reads into trade commands.
3. Do not invent universal thresholds.
4. Do not assume feeds that are not declared.
5. Do not claim DOM, footprint, cumulative delta, breadth, catalyst novelty, or profile behavior unless the relevant feed exists.
6. Do not collapse context into execution permission.
7. Do not use numeric scores to hide unresolved judgment.
8. Do not let a valid thesis bypass setup quality.
9. Do not let a clean setup label imply execution.
10. Keep concept IDs stable unless a deliberate migration is performed.
11. Keep the concept registry, detection specs, calibration profiles, and QA matrices synchronized.
12. Preserve product-specific behavior.
13. Preserve missing-feed and refusal behavior.
14. Prefer explicit uncertainty over confident but unsupported classification.

---

## Validation Commands

The exact commands depend on the local tooling selected for the repository. At minimum, validation should cover:

```bash
python3 scripts/validate_detection_specs.py
python3 scripts/validate_detection_specs.py --traceability-csv qa/glossary_to_spec_traceability.csv
python3 scripts/extract_calibration_inventory.py
python3 scripts/build_detector_contract_catalog.py
python3 scripts/validate_detector_output.py qa/examples/detector_output_valid.example.json
```

The safe detector runtime runs all detector contracts in one pass and writes a
validatable JSON array of non-executional detector outputs:

```bash
python3 scripts/run_detector_runtime.py qa/examples/detector_runtime_input.example.json --output qa/examples/detector_runtime_output.example.json
python3 scripts/validate_detector_output.py qa/examples/detector_runtime_output.example.json
python3 -m unittest tests/test_detector_runtime_v1.py
```

The calibrated detector runtime extends P25 to run CALIBRATED contracts when an
example calibration profile is supplied:

```bash
python3 scripts/run_detector_runtime.py qa/examples/detector_runtime_calibrated_input.example.json --calibration-profile qa/examples/detector_runtime_calibrated_profile.example.yaml --output qa/examples/detector_runtime_calibrated_output.example.json
python3 scripts/validate_detector_output.py qa/examples/detector_runtime_calibrated_output.example.json
python3 scripts/summarize_detector_runtime.py qa/examples/detector_runtime_calibrated_output.example.json --summary-json qa/examples/detector_runtime_summary.example.json --review-md qa/examples/detector_runtime_review_packet.example.md
python3 scripts/build_market_read_packet.py qa/examples/detector_runtime_calibrated_input.example.json --calibration-profile qa/examples/detector_runtime_calibrated_profile.example.yaml --runtime-output qa/examples/market_read_packet_runtime_output.example.json --summary-json qa/examples/market_read_packet_summary.example.json --review-md qa/examples/market_read_packet_review.example.md
python3 -m unittest tests/test_calibrated_detector_runtime_v1.py
```

```bash
# Inspect repository structure
find . -maxdepth 3 -type f | sort

# Check Markdown files exist
find glossary qa -name "*.md" -type f | sort

# Check YAML files exist
find spec calibration -name "*.yaml" -type f | sort

# Check CSV QA files exist
find qa -name "*.csv" -type f | sort
```

If schema validation tooling is added, use it to validate:

```text
spec/concept_registry.yaml
spec/detection_spec_schema.yaml
spec/detector_output_schema.yaml
spec/detection_specs/*.yaml
calibration/calibration_profile_schema.yaml
```

If link-checking tooling is added, use it to validate internal glossary references and glossary-to-spec traceability.

---

## Recommended Maintenance Sequence

For future work, use this sequence:

1. Update or review the glossary concept.
2. Assign or confirm determinism class.
3. Update `spec/concept_registry.yaml`.
4. Update the relevant detection spec.
5. Update calibration requirements if needed.
6. Update `qa/concept_coverage_matrix.csv`.
7. Update `qa/glossary_to_spec_traceability.csv`.
8. Run targeted QA checks.
9. Review for execution leakage and false precision.
10. Commit the change with a message naming the layer changed.

Recommended commit message examples:

```text
docs(glossary): refine acceptance versus rejection doctrine
spec(ch02): add calibrated detection contract for failed acceptance
qa(traceability): map chapter 2 concepts to level interaction specs
calibration: update profile schema or parameter inventory
qa(catalog): rebuild detector contract catalog summary
```

---

## Example Use Cases

### Human Trader Review

A trader can use the glossary to sharpen market-read language, distinguish context from execution permission, and avoid common misreads such as treating a touch as a breakout or treating a catalyst headline as market confirmation.

### Software Specification

A developer can use the detection specs to understand what data is required, which concepts can be computed, which require calibration, which require judgment, and when the system should refuse to decide.

### QA and Audit

A reviewer can use the QA files to verify that every concept has traceability, determinism classification, data dependencies, and bounded output behavior.

### Scripted Maintenance

Coding agents and maintainers can use the validation scripts and QA artifacts to perform bounded edits, registry updates, traceability reconciliation, catalog generation, and schema validation without drifting into doctrine invention or execution leakage.

---

## Key Design Principles

### Read Behavior, Not Labels

Do not stop at “breakout,” “rejection,” or “momentum.” Explain what price did, who likely acted, whether the auction accepted it, and what would invalidate that interpretation.

### Separate Context From Permission

A correct observation does not authorize action. Thesis validity, setup quality, location, confirmation clarity, invalidation clarity, volatility regime, tape quality, and operator judgment remain separate.

### Use Missing-Feed Honesty

If the system lacks the feed required to support a claim, it must say so. Absence of data is not permission to infer.

### Calibrate, Do Not Invent

Thresholds must be empirical, product-specific, timeframe-specific, session-aware, and regime-aware.

### Prefer Refusal Over Fabrication

`INSUFFICIENT_EVIDENCE` is a valid and often correct output.

### Preserve Trader Realism

The glossary should sound like a trader’s working read, not a software engineer modeling a trader from generic chart patterns.

---

## Definition of Done

The project reaches a complete operational baseline when:

- All twelve glossary chapters are present and reviewed.
- Every concept has a stable concept ID.
- Every concept has a determinism class.
- Every concept has traceability from glossary to registry to spec.
- Every detection spec declares required and optional feeds.
- Every detection spec defines missing-feed behavior.
- Every calibrated concept points to a calibration requirement.
- No spec uses universal thresholds for product-specific behavior.
- QA matrices are current.
- Agent instructions preserve the project doctrine.
- No file implies autonomous execution, exact entries, stops, targets, sizing, or broker behavior.

---

## License and Use

No license is declared in the provided project tree.

Until a license is explicitly added, treat the repository as private project material.

---

## Summary

Trader's Market-Read Glossary is a doctrine-first, specification-aware market-read project.

It exists to make trader observations clearer, more traceable, more testable, and safer to implement. Its value comes from preserving the difference between:

- what a concept means,
- what data would be required to detect it,
- whether it can be computed or must be judged,
- whether it is context or action-relevant,
- and when the correct answer is no decision.

The project’s highest standard is not confidence. It is disciplined interpretation.
