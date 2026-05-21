# P11 Semantic Consistency Report

## Executive Result

- **Overall result: P11_PASS_WITH_NOTES.**
- **Chapters reviewed:** Chapters 1-12.
- **Chapters edited:** Chapters 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, and 11.
- **Concepts materially changed:** Tape-Confirms-Narrative Rule; Product-Specific Behavior; Excess vs. Poor Highs/Lows; Volume Nodes & Air Pockets; Short-Covering vs. Long-Liquidation Auctions; Fresh Flow vs. Weak/Strong Hands; Absorption; Refreshing Liquidity; Tape Quality Spectrum; Spread Behavior; Crude Fundamentals: Inventories & Cracks; Transmission Mechanism & Order Effects.
- **Remaining issues deferred to P12:** Determinism classification for Chapters 2-4, which still use the legacy compact section template and do not yet declare Detection Readiness classes.
- **Corpus ready for P12 determinism triage:** Yes.

## Method

Read governance and QA context first: `PROJECT_PROTOCOL.md`, `qa/chapter_corpus_inventory.md`, `qa/semantic_quality_checklist.md`, `qa/raw_trader_doctrine_enrichment_report_chapters_05_12.md`, `qa/actionable_judgment_normalization_report_chapters_05_12.md`, and the earlier restoration report. Then reviewed the glossary corpus structure, chapter headings, concept headings, required-section coverage, Detection Readiness phrasing, See Also links, stale generation scaffolding, and remaining execution-command patterns.

Edits were targeted to semantic consistency: stale cross-links, stale chapter-end scaffolding, H1 punctuation variance, executional one-line idioms, and readiness-class wording where a class was already declared. The actionable-judgment boundary was enforced by preserving trader-useful meaning while replacing command-like phrases with read-quality, thesis-quality, expression-quality, confirmation, invalidation, or posture-label language. Detection readiness was handled only as wording normalization; no P12 determinism triage, specs, schemas, thresholds, or calibration files were started.

## Edits Applied

| Chapter | Concept/Section | Issue | Edit Type | Resolution | Why It Improves Consistency |
|---|---|---|---|---|---|
| 1 | Detection Readiness sections | Chapter 1 used `Initial class:` while later chapters mostly use direct class labels | Detection Readiness wording | Removed `Initial class:` while preserving each existing class | Aligns readiness phrasing without changing determinism meaning |
| 1 | Tape-Confirms-Narrative Rule | One-line and practical implication used trade-command wording | Executional boundary | Rephrased to upgrading the read/thesis only when tape confirms | Preserves trader lesson without telling the operator to trade |
| 1 | Product-Specific Behavior | One-line summary said not to trade products like chart skins | Executional boundary | Rephrased to not read products like chart skins | Keeps product-specific doctrine non-executional |
| 1 | Chapter end and See Also | Stale recommended-next text and non-glossary cross-links | Stale scaffolding / cross-link | Removed next-step scaffolding and linked to real glossary concepts | Makes Chapter 1 final-corpus neutral |
| 2 | Breakout Continuation vs. Breakout Failure | See Also referenced stale `Failed-Followthrough Risk` | Cross-link | Replaced with `Follow-Through and Failure` | Points to the real Chapter 5 concept |
| 2 | Chapter end | Stale generation prompt and remaining-chapters note | Stale scaffolding | Replaced with stable chapter-end summary | Removes authoring artifact from final corpus |
| 3 | Excess vs. Poor Highs/Lows | Target/short wording and universal "always" language | Executional boundary / false precision | Recast poor highs/lows as auction magnets and unfinished business that often resolves | Preserves trader edge while removing target instruction and overclaim |
| 3 | Volume Nodes & Air Pockets | One-line summary used target language | Executional boundary | Reframed as path-quality read | Keeps the HVN/LVN lesson without order-objective wording |
| 3 | Short-Covering vs. Long-Liquidation Auctions | Buying-command wording in core/summary | Executional boundary | Reframed as endpoint-strength misread and fresh-sponsorship requirement | Preserves forced-flow lesson without operator instruction |
| 3 | Fresh Flow vs. Weak/Strong Hands | One-line used "trading alongside" | Boundary clarity | Reframed as participant-quality reliance | Keeps the participant-quality read cleaner and semantic |
| 3 | Chapter end | Stale recommended-next text | Stale scaffolding | Replaced with stable chapter-end summary | Removes authoring artifact |
| 4 | Absorption | One-line told the reader to quit paying up | Executional boundary | Reframed as effort-without-result read | Preserves tape lesson without action command |
| 4 | Refreshing Liquidity | Core/summary used fade/hit language as operator idiom | Executional boundary | Reframed as misread risk and condition identification | Keeps trader voice while avoiding command wording |
| 4 | Tape Quality Spectrum | One-lines used loss/P&L and "dive in" language | Executional boundary | Reframed as poor expression/no-clean-expression language | Aligns tape quality with Chapter 12 setup doctrine |
| 4 | Spread Behavior | One-line told reader not to pay full price | Executional boundary | Reframed as execution-environment evidence | Keeps spread warning non-executional |
| 4 | Chasing/Stall/Tape/Spread See Also | Several stale or shortened concept names | Cross-link | Replaced with exact concept names | Improves link quality across Chapters 4, 5, and 12 |
| 5 | H1 and See Also | H1 punctuation variance and stale `Weak Hands Defending` link | Heading / cross-link | Normalized H1 and linked to `Fresh Flow vs. Weak/Strong Hands` | Improves chapter consistency without changing doctrine |
| 6 | Detection Readiness sections | Chapter 6 used `Initial class:` phrasing | Detection Readiness wording | Removed `Initial class:` while preserving declared classes | Aligns readiness phrasing without P12 triage |
| 6 | See Also links | Stale labels such as `Failed Auctions`, `Trade-Working Diagnosis`, `Value Non-Migration`, and `Settlement Flow` | Cross-link | Replaced with real concept names | Improves navigation and concept-boundary integrity |
| 7 | Intraday Time Windows See Also | Shortened `Execution Environment Quality` label | Cross-link | Replaced with `Execution Environment Quality & Veto` | Links to actual Chapter 12 concept |
| 8 | H1 and See Also | H1 punctuation variance and generic `Setup Quality` link | Heading / cross-link | Normalized H1 and linked to `Setup Cleanliness & Timing` | Improves final-corpus naming consistency |
| 9 | Crude Fundamentals: Inventories & Cracks | Practical implication said not to trade the headline | Executional boundary | Reframed as not letting the headline stand alone | Keeps "read the full barrel" lesson without operator wording |
| 9 | See Also links | Generic chapter labels and shortened concept names | Cross-link | Replaced with exact concept names where clear | Improves cross-link quality without adding concepts |
| 10 | H1, Transmission Mechanism & Order Effects | H1 punctuation variance and "trade the headline/channel" wording | Heading / executional boundary | Normalized H1 and reframed headline/channel as context/read relationship | Preserves catalyst-transmission doctrine without command wording |
| 10 | See Also links | Stale labels such as `Crude Inventory and Product Confirmation`, `Catalyst Alignment`, and `Policy Event Windows` | Cross-link | Replaced with real glossary concepts | Improves traceability to Chapters 9 and 12 |
| 11 | See Also links | Generic or stale labels including `Setup Quality`, `Confirmation Clarity`, `Invalidation Clarity`, and `Trigger Freshness` | Cross-link | Replaced with exact Chapter 12 or Chapter 11 concepts | Clarifies thesis-state boundaries and setup-quality links |

## Cross-Link and Terminology Notes

See Also links were tightened toward actual concept headings rather than chapter shorthand or planning labels. Important replacements included `Setup Quality` to `Setup Cleanliness & Timing`, `Execution Environment Quality` to `Execution Environment Quality & Veto`, `Gold Drivers` to `Gold Drivers: Real Yields, DXY, Breakevens`, and `Yield Curve and Rate Repricing` to `The Yield Curve & Rate Repricing`.

Stale authoring scaffolding was removed from Chapters 1-3. H1 punctuation was normalized in Chapters 5, 8, and 10. The term `Initial class:` was removed where classes were already declared, leaving the existing Detection Readiness class unchanged.

Chapters 2-4 remain compact-template chapters: they contain Core Concept, Why It Happens, Practical Implications, How Traders Identify It, One-Line Summary, and See Also, but do not yet expose separate Common Misreads, Confirmation and Invalidation, or Detection Readiness sections. This was reviewed and documented. Expanding all 34 compact-template concepts, especially assigning Detection Readiness classes, would be broader authoring and would overlap P12 determinism triage.

## Executional Boundary Review

Remaining operator-command language found and fixed:

| Phrase | Source | Replacement | Why the replacement preserves trader education |
|---|---|---|---|
| `Trade the witness, not the speech` | Chapter 1, Tape-Confirms-Narrative Rule | `Upgrade the read only when the witness confirms the speech` | Keeps tape seniority without instructing execution |
| `Do not add conviction to a trade` | Chapter 1, Tape-Confirms-Narrative Rule | `Do not add conviction to a thesis` | Preserves conviction discipline at thesis level |
| `Do not trade products like chart skins` | Chapter 1, Product-Specific Behavior | `Do not read products like chart skins` | Keeps product-specific warning as interpretation doctrine |
| `treat them as targets` | Chapter 3, Excess vs. Poor Highs/Lows | `auction magnets, not clean resistance or support by default` | Preserves poor-high/low magnet logic without target instruction |
| `match your target to the terrain` | Chapter 3, Volume Nodes & Air Pockets | `match the path-quality read to the terrain` | Keeps HVN/LVN path lesson semantic |
| `don't be the one buying it` | Chapter 3, Short-Covering vs. Long-Liquidation Auctions | `continuation needs fresh sponsorship or the read weakens` | Preserves forced-flow exhaustion warning |
| `quit paying up` | Chapter 4, Absorption | `the read is effort without result` | Keeps absorption lesson without operator command |
| `know which one you're hitting before you hit it` | Chapter 4, Refreshing Liquidity | `Know which condition the read is dealing with` | Keeps refresh-vs-spoof distinction semantic |
| `check the water before you dive in` and P&L/loss phrasing | Chapter 4, Tape Quality Spectrum | `bad tape can still have poor expression` and `no clean expression` | Aligns tape quality with setup-expression doctrine |
| `Don't pay full price` | Chapter 4, Spread Behavior | `treat it as execution-environment evidence before upgrading the read` | Preserves spread warning as read-quality evidence |
| `Do not trade the crude inventory headline` | Chapter 9, Crude Fundamentals | `Do not let the crude inventory headline stand alone` | Preserves full-barrel reading discipline |
| `Do not trade the headline; trade only the channel` | Chapter 10, Transmission Mechanism & Order Effects | `The headline is context; the accepted transmission channel is the market read` | Preserves catalyst-channel doctrine without command wording |

The final boundary scan still finds expected governance disclaimers and market-participant language, such as broker/order/account/P&L prohibitions, "buyers chase," "sellers press," "participants trade the data," and "the market may trade the rumor." These are not operator execution instructions.

## Detection Readiness Notes

Corrected readiness-class wording where a class was already declared:

- Chapter 1: removed `Initial class:` from eight Detection Readiness sections.
- Chapter 6: removed `Initial class:` from seven Detection Readiness sections.

No readiness class was changed. No new classes were assigned. Chapters 2-4 still lack explicit Detection Readiness sections because assigning those classes across 34 concepts belongs to P12 determinism triage or a separate approved structure-expansion pass.

## Deferred Issues for P12

- Assign determinism/readiness classes for Chapter 2-4 concepts.
- Decide whether the compact Chapter 2-4 template should be expanded into full Common Misreads, Confirmation and Invalidation, and Detection Readiness sections after P12 class decisions exist.
- Build no detection specs until P12 completes determinism triage.
- Preserve calibration questions for the calibration layer; no thresholds should be invented in P11.

## Final Recommendation

Corpus ready for P12 determinism triage.

Next step: run P12 determinism triage over the complete Chapters 1-12 semantic corpus, starting with the Chapter 2-4 concepts that do not yet declare Detection Readiness classes.
