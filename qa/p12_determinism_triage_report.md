# P12 Determinism Triage Report

Mission ID: TMR-P12-DETERMINISM-TRIAGE-FULL-CORPUS
Review date: 2026-05-21
Scope: Determinism triage over every concept in the Chapters 1-12 semantic glossary corpus.

## Executive Result

- **Overall result: P12_PASS.**
- **Chapters reviewed:** Chapters 1-12 (all 12).
- **Concepts triaged:** 110.
- **Chapters edited:** 3 (Chapter 2, Chapter 3, Chapter 4).
- **Detection Readiness sections added:** 34 (Chapter 2: 9; Chapter 3: 15; Chapter 4: 10).
- **Detection Readiness sections revised:** 0.
- **Concepts left unchanged:** 76 (Chapter 1: 8; Chapters 5-12: 68).
- **Corpus ready for P13 detection spec schema:** Yes. Every concept in Chapters 1-12 now carries a Detection Readiness section, every section declares exactly one of the five approved determinism classes, and every concept is recorded in `qa/concept_determinism_matrix.csv`.

Chapters 2-4 used the legacy compact concept template and carried no Detection Readiness sections; all 34 of their concepts received one in this pass. Chapter 1 and Chapters 5-12 already carried valid Detection Readiness sections with approved class names (P11 had already removed the legacy `Initial class:` wording from Chapters 1 and 6), so those 76 sections were verified and left unchanged. No determinism class was forced toward false computability, no thresholds were invented, and no detection-spec or calibration files were created.

## Method

**Files read.** Governance and QA context first: `PROJECT_PROTOCOL.md`, `qa/chapter_corpus_inventory.md`, `qa/p11_semantic_consistency_report.md`, `qa/actionable_judgment_normalization_report_chapters_05_12.md`, `qa/raw_trader_doctrine_enrichment_report_chapters_05_12.md`, and `qa/semantic_quality_checklist.md`. Then the full glossary corpus, Chapters 1-12, every concept entry read in full.

**How determinism classes were assigned.** Each concept was classified against the five-class rubric using the protocol's definitions. COMPUTABLE was reserved for concepts fully determined by available data and mathematical definition once clean inputs exist (for example, the value area calculation, single prints, Initial Balance, VWAP, one-timeframing, inside/outside day labels, the structural reference lattice). CALIBRATED was used where the rule structure is deterministic but thresholds, windows, or tolerances must be calibrated by instrument, session, timeframe, and regime (acceptance/rejection, break quality, compression/expansion, tape quality, and similar). JUDGMENT_ASSISTED was used where observable evidence supports the read but the final classification depends on context, hierarchy, or interpretation across layers. CONTEXT_ONLY was used for governance, posture, and decision-hygiene concepts that organize judgment rather than detect a market pattern. NOT_DETECTABLE_WITH_CURRENT_FEEDS was used only where the missing data dependency is fundamental rather than merely helpful.

**How missing Detection Readiness sections were handled.** For the 34 Chapter 2-4 concepts, a Detection Readiness section was inserted between `How Traders Identify It` and `One-Line Summary` — the slot the full concept template uses. Each new section declares the class, names required evidence and optional feeds, states missing-feed degradation or refusal behavior, says why the concept should or should not become a detector, and defers calibration and spec wiring to P13. No other section of any Chapter 2-4 concept was modified; `Common Misreads` and `Confirmation and Invalidation` were deliberately not added, as expanding the compact template beyond Detection Readiness is out of P12 scope.

**How false determinism was avoided.** Concepts that depend on inference, participant identity, or unavailable order-book data were not promoted into COMPUTABLE or CALIBRATED to make them look tidier. See False Determinism Controls below.

**How missing-feed behavior was treated.** Every new and existing Detection Readiness section states what happens when a required feed is absent: refuse, downgrade to a narrower structural read, or emit insufficient evidence / NOT_DETECTABLE for the affected feed condition. No concept is permitted to fall back silently to a guessed value.

**How P12 stopped short of detection specs and calibration.** No YAML, schema, concept-registry, detection-spec, or calibration files were created or modified. No numeric thresholds were authored. `spec/` and `calibration/` do not exist and were not created.

## Determinism Class Summary

| Class | Count |
|---|---:|
| COMPUTABLE | 9 |
| CALIBRATED | 27 |
| JUDGMENT_ASSISTED | 64 |
| CONTEXT_ONLY | 7 |
| NOT_DETECTABLE_WITH_CURRENT_FEEDS | 3 |
| **Total** | **110** |

COMPUTABLE concepts: Structural Reference Levels (Ch2); Value Area: VAH/VAL/POC, Value Migration & Overlap, Single Prints, Initial Balance, VWAP Relationship (Ch3); One-Timeframing (Ch5); RTH Open Location (Ch7); Inside/Outside & Narrow/Wide Range Days (Ch8).

NOT_DETECTABLE_WITH_CURRENT_FEEDS concepts: Refreshing Liquidity, Liquidity Pulls & Replenishment (Ch4); Dealer Gamma Dynamics (Ch6).

CONTEXT_ONLY concepts: Context vs. Execution Permission, Product-Specific Behavior (Ch1); Crowded Trades & Pain Trades, Mechanical Flows (Ch6); Catalyst-to-Trade Translation (Ch10); Thesis Confirmation vs. Execution Permission (Ch11); Action Vocabulary (Ch12).

## Detection Readiness Edits Applied

| Chapter | Concept | Prior State | Final Class | Edit Type | Rationale |
|---|---|---|---|---|---|
| 2 | Structural Reference Levels | No Detection Readiness section | COMPUTABLE | ADDED_MISSING_SECTION | Canonical reference set is mechanically derivable from session data; value references need profile data |
| 2 | Acceptance vs. Rejection | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Deterministic rule structure; dwell/activity/buffer thresholds need calibration |
| 2 | Level Test Sequence | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Test count computable; decay read needs calibrated window and reaction threshold |
| 2 | Level Magnetism & Decay | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Magnet/overshoot/decay structural; parameters need calibration; stop clusters inferred |
| 2 | Breakout Continuation vs. Breakout Failure | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Continuation/retest/failure structure observable; windows need calibration |
| 2 | Liquidity Sweep vs. Real Break | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Reclaim/hold reaction calibrable; engineered intent is not detectable |
| 2 | Break Quality | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Texture and location gradeable with calibrated measures |
| 2 | Polarity Flip | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Flip-confirmed/failed observable; retest window needs calibration |
| 2 | Mechanical Levels & Obvious Traps | No Detection Readiness section | JUDGMENT_ASSISTED | ADDED_MISSING_SECTION | Trap-risk read depends on crowding and consensus inference, not observable feeds |
| 3 | The Auction Framework | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Balance/imbalance regime; rotation and shape thresholds need calibration |
| 3 | Auction Acceptance vs. Rejection | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Auction-level acceptance read; needs profile data and calibrated dwell |
| 3 | Initiative vs. Responsive Activity | No Detection Readiness section | JUDGMENT_ASSISTED | ADDED_MISSING_SECTION | Location split is mechanical but the conviction-vs-defense read is interpretive |
| 3 | Completed, Failed & Unfinished Auctions | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Excess/poor/failed structure deterministic; TPO and failed-break thresholds need calibration |
| 3 | Excess vs. Poor Highs/Lows | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Tail vs flat extreme near-structural with TPO data; quality threshold needs calibration |
| 3 | Value Area: VAH / VAL / POC | No Detection Readiness section | COMPUTABLE | ADDED_MISSING_SECTION | Mechanically computed from the volume/TPO distribution where profile data exists |
| 3 | Value Migration & Overlap | No Detection Readiness section | COMPUTABLE | ADDED_MISSING_SECTION | Day-over-day value comparison is a mechanical operation given value areas |
| 3 | Price Outside Value / Acceptance Test | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Position vs value computable; the acceptance test needs calibrated dwell/volume thresholds |
| 3 | Volume Nodes & Air Pockets | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | HVN/LVN identification needs volume-at-price data and calibrated node/gap thresholds |
| 3 | Single Prints | No Detection Readiness section | COMPUTABLE | ADDED_MISSING_SECTION | Mechanically identified from TPO data once the TPO period is defined |
| 3 | Initial Balance | No Detection Readiness section | COMPUTABLE | ADDED_MISSING_SECTION | IB high/low computed directly from the first two 30-minute periods |
| 3 | VWAP Relationship | No Detection Readiness section | COMPUTABLE | ADDED_MISSING_SECTION | VWAP, bands, and price location computed directly from price and volume |
| 3 | Overnight Inventory & Inventory Correction | No Detection Readiness section | JUDGMENT_ASSISTED | ADDED_MISSING_SECTION | Range computable; lopsidedness and the correction call are inference |
| 3 | Short-Covering vs. Long-Liquidation Auctions | No Detection Readiness section | JUDGMENT_ASSISTED | ADDED_MISSING_SECTION | Forced exit flow vs fresh initiative requires judgment and positioning data |
| 3 | Fresh Flow vs. Weak/Strong Hands | No Detection Readiness section | JUDGMENT_ASSISTED | ADDED_MISSING_SECTION | Participant quality cannot be observed directly; it is inferred |
| 4 | Absorption | No Detection Readiness section | JUDGMENT_ASSISTED | ADDED_MISSING_SECTION | Effort-without-result read; needs footprint/DOM/delta and judgment |
| 4 | Refreshing Liquidity | No Detection Readiness section | NOT_DETECTABLE_WITH_CURRENT_FEEDS | ADDED_MISSING_SECTION | Order-book phenomenon; cannot be read from bars or trade prints |
| 4 | Chasing vs. Pressing | No Detection Readiness section | JUDGMENT_ASSISTED | ADDED_MISSING_SECTION | Needs trade classification; vacuum-vs-demand read is interpretive |
| 4 | Stall & Snap-Back | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Velocity and snap-back structure deterministic; thresholds need calibration |
| 4 | Tape Quality Spectrum | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Tape-quality axes measurable against calibrated baselines |
| 4 | Tape vs. Narrative | No Detection Readiness section | JUDGMENT_ASSISTED | ADDED_MISSING_SECTION | Requires a transmission-mechanism judgment; cannot be a deterministic rule |
| 4 | Spread Behavior | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Spread measurable from quote data; needs calibrated baselines |
| 4 | Liquidity Pulls & Replenishment | No Detection Readiness section | NOT_DETECTABLE_WITH_CURRENT_FEEDS | ADDED_MISSING_SECTION | Requires live DOM depth data; bars cannot show the book emptying |
| 4 | Sweeps Through Liquidity | No Detection Readiness section | CALIBRATED | ADDED_MISSING_SECTION | Sweep and post-sweep resolution calibrable; order-flow data improves it |
| 4 | Cumulative Delta & Delta Divergence | No Detection Readiness section | JUDGMENT_ASSISTED | ADDED_MISSING_SECTION | Delta computable with classified trade data; divergence read needs judgment |
| 1 | All 8 concepts | Detection Readiness present, valid class, P11-normalized | (unchanged) | LEFT_UNCHANGED | Sections already declare an approved class with feed and spec notes; no revision needed |
| 5-12 | All 68 concepts | Detection Readiness present, valid class | (unchanged) | LEFT_UNCHANGED | Every section already declares one of the five approved classes consistent with the concept; `Initial class:` wording already removed by P11 |

## Chapter 2-4 Special Review

**Missing sections found.** All 34 concepts in Chapters 2-4 lacked a Detection Readiness section. Chapters 2-4 use the legacy compact concept template (Core Concept, Why It Happens, Practical Implications, How Traders Identify It, One-Line Summary, See Also) and never carried Detection Readiness, Common Misreads, or Confirmation and Invalidation headings. This was flagged by the P10.5 corpus inventory and explicitly deferred to P12 by the P11 semantic consistency report.

**Older-format readiness sections found.** None in Chapters 2-4 — there were no readiness sections to be in an older format. The legacy `Initial class:` phrasing previously found in Chapters 1 and 6 had already been removed during P11, so no class-name normalization was required in this pass.

**Classes assigned in Chapters 2-4.** Chapter 2: 1 COMPUTABLE, 7 CALIBRATED, 1 JUDGMENT_ASSISTED. Chapter 3: 5 COMPUTABLE, 6 CALIBRATED, 4 JUDGMENT_ASSISTED. Chapter 4: 4 CALIBRATED, 4 JUDGMENT_ASSISTED, 2 NOT_DETECTABLE_WITH_CURRENT_FEEDS.

**Remaining concerns.** One structural note for a later pass, not a P12 blocker: Chapters 2-4 still lack `Common Misreads` and `Confirmation and Invalidation` headings (their content is partly carried inline within Core Concept and Practical Implications). Expanding the compact template into the full nine-section schema is a separate authoring decision and was deliberately left out of P12 scope, which was limited to determinism triage and Detection Readiness.

## False Determinism Controls

The pass refused to overstate detectability in the following places:

- **Refreshing Liquidity** and **Liquidity Pulls & Replenishment** (Ch4) were classed NOT_DETECTABLE_WITH_CURRENT_FEEDS rather than CALIBRATED. Both are order-book phenomena; a bar-or-tape-only system cannot see displayed size reload or depth collapse. The Detection Readiness sections state the dependency is fundamental and that the most a feedless system can report is the related Absorption read or low-confidence air-pocket price behavior.
- **Dealer Gamma Dynamics** (Ch6) was confirmed NOT_DETECTABLE_WITH_CURRENT_FEEDS; it requires options open interest, an implied-volatility surface, and a dealer-position model.
- **Absorption** and **Cumulative Delta & Delta Divergence** (Ch4) were classed JUDGMENT_ASSISTED, not COMPUTABLE or CALIBRATED, with explicit missing-feed notes that the concept becomes NOT_DETECTABLE_WITH_CURRENT_FEEDS when footprint, DOM, or bid/ask-classified trade data is absent.
- **Initiative vs. Responsive Activity**, **Overnight Inventory & Inventory Correction**, **Short-Covering vs. Long-Liquidation Auctions**, and **Fresh Flow vs. Weak/Strong Hands** (Ch3) were kept JUDGMENT_ASSISTED. Participant identity, lopsided positioning, and forced-versus-fresh flow are inferences; only their structural footprints are observable.
- **Mechanical Levels & Obvious Traps** (Ch2) was kept JUDGMENT_ASSISTED because the trap-risk read depends on crowding and consensus, which ordinary price and volume feeds do not expose.
- **Value Area**, **Value Migration & Overlap**, and **Single Prints** were classed COMPUTABLE but each Detection Readiness section names a hard data dependency (volume-at-price or TPO data) and states the concept becomes NOT_DETECTABLE under the feed condition where that data is absent, rather than approximating it from bars.
- No numeric threshold was authored for any CALIBRATED concept; every CALIBRATED section states that values belong in P13/P14 calibration profiles.

## Deferred To P13

The following belong to P13 and later phases and were not started:

- The detection specification schema (`spec/detection_spec_schema.yaml`).
- The concept registry (`spec/concept_registry.yaml`), including stable concept IDs and glossary anchors.
- Per-concept YAML detection specs for COMPUTABLE, CALIBRATED, and JUDGMENT_ASSISTED concepts.
- Parameter definitions and named threshold parameters for all CALIBRATED concepts.
- Calibration profiles and empirical parameter values (P18 calibration layer).
- Validation tests and traceability matrices.
- The decision on whether the compact Chapter 2-4 template should be expanded into the full nine-section concept schema.

## Final Recommendation

**Corpus ready for P13 detection spec schema.**

Next step: begin P13 by building the detection specification schema and concept registry, keyed to the determinism classes recorded in `qa/concept_determinism_matrix.csv`, starting with the COMPUTABLE and CALIBRATED concepts that are the most direct detection-spec candidates.
