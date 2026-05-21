Locked.

## A-06 — Semantic Glossary and Detection/Specification Boundary

**Status:** Locked
**Wording:** The semantic glossary and detection/specification layer is the workstation’s market-read rule and concept foundation. It defines trader-realistic market concepts, canonical concept IDs, detection contracts, data dependencies, determinism classes, calibration requirements, allowed output labels, refusal behavior, missing-feed behavior, confidence behavior, known false-positive modes, and test expectations.

This layer must cover, at minimum, read discipline, level interaction, auction/profile behavior, tape/microstructure, momentum and day types, traps and positioning, session context, volatility regime, intermarket confirmation, catalyst interpretation, thesis/trade-state management, and setup quality/action vocabulary.

The layer may produce thesis inputs, trigger states, blocker states, invalidation states, evidence states, confidence changes, context-only labels, insufficient-evidence labels, and not-detectable-with-current-feeds labels.

It must not produce trade commands, broker actions, exact entries, exact stops, exact targets, position sizing, order approvals, autonomous execution labels, or final trader judgment.

The market-read authority layer consumes and governs this layer’s outputs when producing the authoritative market-read state. The two are not identical: the glossary/spec layer defines concepts and detection contracts; the market-read authority layer performs final synthesis and decision-support classification.

All concepts must preserve non-execution boundaries, missing-feed honesty, refusal behavior, and calibration discipline. If required feeds are missing, the correct behavior is refusal, downgrade, insufficient evidence, not-detectable-with-current-feeds, or context-only output, not invented classification. 

**Confirmation status:** Authoritative lock

Current locked assumptions:

```text
A-01 — Source Authority Model
A-02 — Trade-Lifecycle Supervision Boundary
A-03 — Market-Read Authority Boundary
A-04 — Fail-Closed Data Authority Boundary
A-05 — First-Build Feature Boundary
A-06 — Semantic Glossary and Detection/Specification Boundary
```
