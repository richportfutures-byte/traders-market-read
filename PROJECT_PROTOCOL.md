# Trader's Market-Read Glossary and Detection Specification Protocol

Version: 1.0  
Status: Project starter protocol  
Project type: Trading doctrine, semantic glossary, detection specification, calibration architecture  
Primary objective: Finish the semantic market-read glossary and build a separate machine-usable detection/specification layer without turning discretionary trader judgment into fake deterministic signals.

## 1. Prime Directive

This project builds two separate but linked artifacts:

1. **Semantic Layer**  
   The human-readable trader doctrine. It explains what each concept means, why it happens, how traders identify it, how it affects decision-making, what it is commonly confused with, and what confirms or invalidates the read.

2. **Detection and Specification Layer**  
   The machine-usable implementation contract. It defines data dependencies, determinism class, required inputs, optional inputs, detection logic, confidence behavior, refusal behavior, calibration requirements, failure modes, and allowed output labels.

The semantic layer must sound like an experienced trader's working market read.

The detection layer must sound like a precise implementation contract.

Do not mix them.

## 2. Attached Documents Policy

Uploaded or attached documents are not automatically constraints, project doctrine, or source of truth.

They may be used only as evidence or examples when explicitly useful. A document becomes binding only when the user explicitly promotes it into project doctrine.

Current priority order:

1. Current explicit user instruction.
2. This protocol.
3. User-approved project doctrine.
4. Existing glossary chapters as evidence and draft material.
5. Existing outlines or gap reports as planning aids.
6. Coding-agent repo instructions such as `AGENTS.md` or `CLAUDE.md`, where applicable.
7. Older protocols or orchestration documents from unrelated projects.
8. Generated output from prior runs.

Existing chapters are evidence, not law. They may be revised when trader realism, conceptual accuracy, or detection traceability requires it.

## 3. Core Doctrine

The glossary is not an execution system.

The glossary and detection specification may help organize market reads, structure trader observations, and support later software implementation. They must not produce autonomous trade instructions, broker actions, position sizing, exact entries, exact stops, exact targets, or account-level behavior.

The project may describe concepts such as:

- acceptance
- rejection
- liquidity sweep
- stop run
- reclaim
- trapped longs
- trapped shorts
- weak hands
- strong hands
- initiative activity
- responsive activity
- absorption
- delta divergence
- tape quality
- session handoff
- inventory correction
- stale thesis
- poor location

The project must distinguish:

- structural read
- tape read
- catalyst read
- intermarket read
- volatility regime
- execution environment
- trade-state management
- setup quality

A concept may be actionable in judgment without being executional in instruction. Some concepts are context-only; others materially affect read quality, confirmation requirements, invalidation clarity, setup posture, location quality, or thesis state. None may authorize autonomous execution.

A concept may be observable without being deterministic.

A concept may be real trader language without being safe to automate.

### 3.1 Actionable-Judgment Preservation Standard

The semantic glossary must preserve trader-useful guidance. Non-executional does not mean passive, sterile, academic, or compliance-like.

The governing standard is:

**Actionable in judgment, non-executional in instruction.**

A glossary entry may explain what a trader should watch, downgrade, confirm, invalidate, classify, monitor, or label. It may explain how a condition affects read quality, setup quality, location quality, thesis state, confirmation requirements, invalidation clarity, expression quality, or operator posture.

A glossary entry may use trader-native language when accurate, including pressure, fuel, sponsorship, exhaustion, trapped positioning, forced flow, stale thesis, poor location, no clean expression, confirmation required, review required, context-only, stand aside, and insufficient evidence.

A glossary entry must not become an execution instruction. It must not prescribe exact entries, exits, stops, targets, position sizing, adds, reductions, broker actions, account behavior, fills, or P&L behavior.

Market-participant behavior is not operator instruction. Phrases such as "shorts cover," "longs liquidate," "buyers stop chasing," "sellers press," "defenders lose control," "forced buying appears," and "the market repairs value" are valid market-read language unless the text tells the operator to take a trade action.

When older chapter language contains execution-command wording, preserve the trader lesson by reclassifying it into one of these semantic categories:

- read-quality implication
- setup-quality implication
- location-quality implication
- confirmation requirement
- invalidation condition
- thesis-state change
- posture label
- watch-next instruction
- evidence downgrade
- no-clean-expression condition

Examples:

- Replace "trade the first test" with "the first test usually carries cleaner information because defensive liquidity is freshest."
- Replace "fade the rejection" with "a clean rejection strengthens a value-repair or rejection thesis if price fails to accept beyond the reference."
- Replace "size down" with "downgrade setup quality or conviction when the evidence is late, thin, conflicted, or poorly located."
- Replace "move the stop" with "the semantic invalidation condition is acceptance beyond the defended reference."
- Replace "take partials" with "the continuation read weakens when effort stops producing displacement."


## 4. Non-Negotiable Separation

### 4.1 Semantic Layer Answers

For each concept, the semantic layer answers:

- What does this mean?
- Why does it happen?
- What does a trader watch?
- What does it imply?
- What is commonly misread?
- What confirms it?
- What invalidates it?
- What related concepts should it link to?

### 4.2 Detection Layer Answers

For each concept, the detection layer answers:

- Can this be detected deterministically?
- What data feed is required?
- What data feed is optional?
- What parameters are needed?
- Are the parameters fixed, calibrated, or discretionary?
- What states can the detector emit?
- When should the detector refuse to decide?
- What failure modes create false positives?
- What tests prove the rule behaves correctly?

### 4.3 Calibration Layer Answers

For each instrument, session, timeframe, and regime, the calibration layer answers:

- What parameter values are empirically appropriate?
- What historical sample produced them?
- What regime does the calibration apply to?
- What regime invalidates the calibration?
- What confidence should the system attach?

No authored glossary entry may invent thresholds as if they are universal.

## 5. Recommended Project Structure

```text
traders-market-read/
  README.md
  PROJECT_PROTOCOL.md
  glossary/
    chapter_01_read_discipline.md
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
  spec/
    concept_registry.yaml
    detection_spec_schema.yaml
    detection_specs/
      level_interaction.yaml
      auction_market_profile.yaml
      tape_microstructure.yaml
      momentum_day_types.yaml
      traps_positioning.yaml
      session_context.yaml
      volatility_regime.yaml
      intermarket_confirmation.yaml
      catalyst_interpretation.yaml
      trade_state_management.yaml
      setup_quality.yaml
  calibration/
    calibration_profile_schema.yaml
    example_profiles/
      ES_intraday.example.yaml
      NQ_intraday.example.yaml
      CL_intraday.example.yaml
      6E_intraday.example.yaml
      MGC_intraday.example.yaml
  qa/
    semantic_quality_checklist.md
    detection_spec_quality_checklist.md
    concept_coverage_matrix.csv
    glossary_to_spec_traceability.csv
  agent/
    AGENTS.md
    CLAUDE.md
    mission_templates.md
```

## 6. Roles

### 6.1 GPT-5.5 Thinking

GPT-5.5 is the lead doctrine architect and semantic editor.

Responsibilities:

- Finish missing glossary chapters.
- Rewrite weak or generic explanations.
- Preserve trader realism.
- Detect overclaiming, false precision, and shallow chart-pattern language.
- Decide whether a concept is semantic-only, computable, calibrated, judgment-assisted, context-only, or not detectable with current feeds.
- Build the detection specification schema and concept registry.
- Review coding-agent output for conceptual correctness.

GPT-5.5 is the final editorial authority unless the user overrides it.

### 6.2 Codex GPT-5.5

Codex is the structured implementation agent.

Use Codex for:

- creating project files
- applying approved markdown structure
- converting approved schema into YAML or JSON
- validating schema consistency
- generating coverage matrices
- checking cross-links
- writing tests for schema validity
- building tooling that compares glossary entries to detection specs

Do not use Codex as an unchecked doctrine author. Codex may implement approved structure, but GPT-5.5 must review doctrine quality.

### 6.3 Claude Code Opus 4.7

Claude Code may be used for local repo work, multi-file edits, and careful implementation.

Use Claude Code for:

- large chapter refactors
- multi-file consistency edits
- glossary-to-spec synchronization
- repo restructuring after the protocol is stable
- validation tooling when careful local exploration matters

Do not use Claude Code as an unchecked doctrine authority. It can draft, organize, and implement, but GPT-5.5 must review the conceptual output.

## 7. Workflow Phases

### Phase 0: Project Initialization

Goal: establish the working folder or repo, protocol, file layout, and source inventory.

Deliverables:

- `PROJECT_PROTOCOL.md`
- `README.md`
- `concept_coverage_matrix.csv`
- list of current chapters
- list of missing chapters
- list of available source materials, marked as evidence rather than binding truth

Done when:

- the project has a clear folder structure
- current chapter status is known
- no document has been silently promoted to source of truth
- the next semantic chapter target is identified

### Phase 1: Semantic Layer Completion

Goal: complete the glossary chapters first, before writing detailed detection rules.

Required entry format:

```text
## Concept Name

### Core Concept
Plain-language trader definition with sharp distinction from common misreads.

### Why It Happens
Driver and mechanism table.

### Practical Implications
Concrete actionable-judgment implications without autonomous trade instruction. Explain what the trader should watch, downgrade, confirm, invalidate, classify, or label. Preserve useful trader education while avoiding entries, exits, stops, sizing, targets, broker/order behavior, account behavior, fills, or P&L instructions.

### How Traders Identify It
Observable tells, separated from confirmation requirements.

### Common Misreads
What traders, LLMs, or coders often confuse it with.

### Confirmation and Invalidation
What strengthens, weakens, confirms, or invalidates the read.

### Detection Readiness
Computable, Calibrated, Judgment-Assisted, Context-Only, or Not Detectable With Current Feeds.

### One-Line Summary
Trader-style compression.

### See Also
Cross-links.
```

Semantic writing rules:

- Do not sound like a compliance report.
- Do not reduce concepts to chart patterns.
- Do not use invented precision.
- Do not say "always" when the condition is regime-dependent.
- Do not authorize trades from context-only observations.
- Do not collapse structural read, tape read, catalyst read, execution quality, and trade-state management.
- Do include trader-native language where accurate.
- Do preserve actionable market-read guidance as judgment language, not execution instruction.
- Do reclassify restricted execution wording into read quality, setup quality, location quality, confirmation, invalidation, thesis-state, posture-label, watch-next, evidence-downgrade, or no-clean-expression language.
- Do not strip practical trader lessons merely because they affect decision quality.

Done when:

- all 12 chapters exist
- every concept has a consistent entry structure
- forward links resolve
- obvious redundancy is removed
- missing lived-trader concepts are added where needed

### Phase 2: Determinism Triage

Goal: classify every concept before writing detection rules.

Every concept receives one determinism class:

```text
COMPUTABLE
Fully determined by available data and mathematical definition.
Examples: VWAP, prior high and low, IB high and low, inside day, outside day.

CALIBRATED
Rule structure can be deterministic, but thresholds must be calibrated by product, timeframe, session, and regime.
Examples: acceptance and rejection, break quality, level decay, momentum exhaustion, tape quality.

JUDGMENT_ASSISTED
Requires structured human or LLM judgment because it depends on narrative, context, or interpretation.
Examples: tape disagrees with narrative, catalyst translation, conflict severity.

CONTEXT_ONLY
Useful for market read, but must not produce an actionable trigger.
Examples: broad macro backdrop, session color, possible positioning narrative without observable confirmation.

NOT_DETECTABLE_WITH_CURRENT_FEEDS
Concept requires data not currently available.
Examples: DOM-based absorption without level-2 data, iceberg behavior without order book events.
```

Done when:

- every glossary concept has a determinism class
- every class assignment has a short rationale
- every non-computable concept is prevented from pretending to be deterministic

### Phase 3: Detection Specification Layer

Goal: build machine-readable specs keyed to the glossary.

Required detection spec shape:

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

  - name: trade_prints
    type: time_and_sales
    granularity: tick_or_1m
    required: true

  - name: session_clock
    type: calendar_session_state
    required: true

optional_inputs:
  - name: volume_at_price
    type: profile_volume
    degradation_if_missing: lower_confidence

  - name: cumulative_delta
    type: aggressive_flow_proxy
    degradation_if_missing: no_delta_confirmation

parameters:
  - name: acceptance_dwell_time
    type: duration
    calibration_required: true
    scope: instrument_timeframe_regime

  - name: acceptance_volume_threshold
    type: relative_volume
    calibration_required: true
    scope: instrument_timeframe_regime

  - name: level_buffer
    type: price_distance
    calibration_required: true
    suggested_basis: atr_fraction_or_ticks

states_emitted:
  - ACCEPTED_ABOVE
  - ACCEPTED_BELOW
  - REJECTED
  - FAILED_ACCEPTANCE
  - PENDING
  - INSUFFICIENT_EVIDENCE

decision_logic: >
  Emit acceptance only when price holds beyond the level for the calibrated dwell
  time and, where available, activity builds beyond the level. Emit rejection when
  price tests the level and returns without acceptance. Emit failed acceptance
  when apparent acceptance reverses back through the level inside the calibrated
  failure window.

confidence_rules:
  - Missing required input emits INSUFFICIENT_EVIDENCE.
  - Missing optional volume data lowers confidence.
  - Thin session state lowers confidence or blocks signal.
  - Conflicting tape evidence emits CONFIRMATION_REQUIRED.

failure_modes:
  - stop run mistaken for real break
  - oscillation around level causing state flip
  - low-liquidity session creating false acceptance
  - gapped move skipping valid level interaction

allowed_action_labels:
  - WATCH_ONLY
  - WAIT_FOR_ACCEPTANCE
  - WAIT_FOR_REJECTION
  - CONFIRMATION_REQUIRED
  - INSUFFICIENT_EVIDENCE
  - CONTEXT_ONLY

forbidden_outputs:
  - exact_entry
  - exact_stop
  - exact_position_size
  - broker_order
  - autonomous_trade_decision

test_cases:
  - accepts_above_after_dwell_and_volume
  - rejects_after_touch_without_follow_through
  - fails_acceptance_after_reclaim
  - emits_insufficient_evidence_without_trade_prints
  - lowers_confidence_without_volume_at_price
```

Done when:

- every spec has required inputs
- every parameter is named and typed
- no threshold is invented without calibration status
- every detector can refuse to decide
- every spec has failure modes
- every spec emits labels, not trade orders

### Phase 4: Calibration Profile Layer

Goal: separate rule structure from empirical parameter values.

Calibration profile shape:

```yaml
profile_id: ES_RTH_intraday_v1
instrument: ES
session: RTH
timeframe: intraday
sample_window:
  start: YYYY-MM-DD
  end: YYYY-MM-DD

parameter_values:
  acceptance_rejection_level:
    acceptance_dwell_time:
      value: null
      status: requires_empirical_calibration
    acceptance_volume_threshold:
      value: null
      status: requires_empirical_calibration
    level_buffer:
      value: null
      status: requires_empirical_calibration

valid_regimes:
  - normal_liquidity
  - standard_rth

invalid_regimes:
  - major_event_window
  - holiday_liquidity
  - roll_distortion
  - extreme_volatility_expansion

notes: >
  This profile is a placeholder until calibrated from historical instrument data.
```

Rules:

- Do not hardcode ES thresholds into CL, 6E, NQ, or MGC.
- Do not assume RTH thresholds apply to Globex.
- Do not assume normal-liquidity thresholds apply to event windows.
- Do not let a missing calibration profile fall back silently to generic values.
- Missing calibration must emit `INSUFFICIENT_EVIDENCE`, `UNVALIDATED_PARAMETER`, or `SHADOW_ONLY`.

### Phase 5: Quality Review

Semantic review checklist:

```text
- Does the entry sound like a trader wrote it?
- Does it distinguish price touch from price behavior?
- Does it explain why the condition happens?
- Does it name common false reads?
- Does it separate context from action?
- Does it avoid false precision?
- Does it include confirmation and invalidation?
- Does it cross-link correctly?
```

Detection review checklist:

```text
- Are required feeds explicit?
- Are optional feeds explicit?
- Are missing-feed behaviors explicit?
- Is the determinism class correct?
- Are parameters named rather than invented?
- Are calibration requirements explicit?
- Can the detector refuse to decide?
- Are known false positives listed?
- Are action labels bounded?
- Are forbidden outputs blocked?
```

## 8. Output Labels

The detection/spec layer may emit controlled labels only.

Approved labels:

```text
NO_TRADE
WATCH_ONLY
CONTEXT_ONLY
BIAS_ONLY
WAIT_FOR_CONFIRMATION
WAIT_FOR_ACCEPTANCE
WAIT_FOR_REJECTION
WAIT_FOR_RETEST
WAIT_FOR_LIQUIDITY_NORMALIZATION
CONFIRMATION_REQUIRED
INSUFFICIENT_EVIDENCE
MEDIUM_REQUIRES_SHADOW_ONLY
STRUCTURE_VALID_BUT_NO_TRIGGER
TRIGGER_VALID_BUT_LOCATION_POOR
CATALYST_VALID_BUT_TAPE_REJECTS
TAPE_VALID_BUT_CATALYST_WEAK
REGIME_BLOCKED
EVENT_RISK_BLOCKED
LIQUIDITY_BLOCKED
SPREAD_BLOCKED
VOLATILITY_BLOCKED
INVALIDATED
THESIS_STALE
REVIEW_REQUIRED
MANUAL_ONLY
DO_NOT_CHASE
EXIT_REVIEW_REQUIRED
```

Forbidden outputs:

```text
BUY_NOW
SELL_NOW
ENTER_LONG
ENTER_SHORT
PLACE_ORDER
SET_STOP_AT
POSITION_SIZE
AUTOMATED_EXECUTION
GUARANTEED_SIGNAL
HIGH_PROBABILITY_TRADE
```

## 9. Agent Mission Rules

Agent missions must be bounded.

Missions should ask for a concrete artifact, targeted verification, and a final report rather than broad audit work.

### 9.1 Use GPT-5.5 Directly For

- writing new glossary chapters
- rewriting weak semantic entries
- deciding determinism class
- resolving concept overlap
- identifying missing trader concepts
- reviewing whether a concept is over-mechanized

### 9.2 Use Codex For

- creating repo files
- applying approved markdown structure
- generating YAML stubs
- enforcing schema validity
- checking cross-link integrity
- creating coverage tables
- running validation scripts

### 9.3 Use Claude Code For

- multi-file local restructuring
- large consistency passes
- careful repo-level refactors
- validation tooling where Plan Mode is useful

## 10. Coding-Agent Mission Template

Use this for coding-agent work.

```text
1. Codex Mission

Mission ID: TMR-M###
Target Agent: Codex
Target Model: GPT-5.5
Execution Surface: Codex CLI or IDE
Execution Mode: Direct implementation unless a real blocker appears
Reasoning Effort: High
Risk: Medium
Project: Trader's Market-Read Glossary and Detection Specification
Project Step: <Phase and task>

CONTROL PREAMBLE:
This project is building two separate artifacts: a semantic trader glossary and a machine-readable detection/specification layer. Do not collapse them. Do not invent thresholds. Do not convert discretionary trader judgment into fake deterministic signals. Build the requested artifact, wire it into the project structure, validate it, and report what now works.

Goal:
<Specific artifact or behavior to create.>

Context:
- The semantic layer explains trader meaning.
- The detection layer defines implementation contracts.
- Calibration values belong in calibration profiles, not glossary prose or raw specs.
- Missing feeds must emit insufficient evidence, not guesses.

Boundaries:
- Stay inside this project.
- Do not modify unrelated repos.
- Do not add broker/order/execution/account/fill/P&L behavior.
- Do not create exact entries, exact stops, position sizing, or autonomous trade recommendations.
- Do not invent universal thresholds.
- Do not silently treat discretionary concepts as computable.
- Do not add broad unrelated cleanup.

Implementation Scope:
- Inspect only files relevant to this mission.
- Create or edit only files needed for this artifact.
- Add validation where useful.
- Preserve existing chapter content unless the mission explicitly asks for rewriting.

Verification Floor:
- Validate markdown links where relevant.
- Validate YAML or JSON syntax where relevant.
- Validate schema conformance where relevant.
- Produce a concept coverage summary if the mission touches registry or spec files.
- Report any missing inputs, unresolved references, or concepts that need human review.

Done When:
- The requested artifact exists.
- The artifact follows the semantic/spec separation.
- No fake thresholds were invented.
- No forbidden outputs were introduced.
- Verification results are reported.

Final Report:
1. Artifact created or changed
2. Files changed
3. Verification performed
4. Concepts covered
5. Concepts requiring human or GPT-5.5 review
6. Remaining blockers
```

## 11. Chapter Completion Roadmap

Recommended order:

```text
P0: Project protocol and folder structure
P1: Concept coverage matrix
P2: Finish Chapter 1, Read Discipline and Interpretation Method
P3: Finish Chapter 6, Traps and Positioning
P4: Finish Chapter 5, Momentum, Follow-Through and Day Types
P5: Finish Chapter 7, Session Context and Sequencing
P6: Finish Chapter 8, Volatility Regime
P7: Finish Chapter 11, Trade-State Management
P8: Finish Chapter 12, Setup Quality and Action Vocabulary
P9: Finish Chapter 9, Intermarket Confirmation
P10: Finish Chapter 10, Catalyst Interpretation
P11: Full semantic consistency pass
P12: Determinism triage for all concepts
P13: Detection spec schema
P14: Detection spec stubs for all concepts
P15: Fully specified detection specs for computable concepts
P16: Fully specified detection specs for calibrated concepts
P17: Judgment-assisted spec format
P18: Calibration profile schema
P19: Validation tooling
P20: Final doctrine and spec review
```

Why this order:

- Chapter 1 should be finished early because it defines interpretation discipline.
- Chapter 6 should come next because trapped positioning, weak hands, crowded trades, and pain trades are heavily referenced by level and tape concepts.
- Trade-state and setup-quality chapters should be completed before finalizing output labels.
- Intermarket and catalyst chapters should come after the core price-action structure so they do not dominate the doctrine prematurely.

## 12. Stop Conditions

Stop and escalate to GPT-5.5 review when:

- a concept requires trader judgment and an agent tries to make it deterministic
- a detector needs a feed that is not available
- a threshold is being guessed
- a chapter entry sounds generic or textbook-like
- a concept overlaps another concept and the boundary is unclear
- an output label implies trade execution
- a spec cannot define failure modes
- a calibration value is being authored instead of derived
- the glossary starts reading like software documentation instead of market-read doctrine

## 13. Definition of Done

The project is not done when all chapters exist.

The project is done when:

```text
- All semantic chapters are complete.
- Every concept has a stable concept_id.
- Every concept has a determinism class.
- Every concept maps to either a detection spec, judgment-assisted spec, context-only label, or not-detectable status.
- Required feeds are explicit.
- Missing-feed behavior is explicit.
- Calibration requirements are explicit.
- No invented universal thresholds exist.
- Output labels are bounded and non-executional.
- Cross-links are valid.
- Coverage matrix shows no orphan concepts.
- A human trader can read the glossary.
- A coding agent can implement the spec without inventing doctrine.
```

## 14. Immediate Next Step

For this project, GPT-5.5 should lead the next phase directly.

The immediate next deliverable after this protocol should be:

```text
concept_coverage_matrix.csv
```

Then:

```text
Chapter 1 - Read Discipline and Interpretation Method
```

This prevents the project from drifting into either prose-only glossary generation or premature detector implementation.
