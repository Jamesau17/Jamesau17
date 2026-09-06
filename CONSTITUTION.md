# CONSTITUTION

Authority rank: 1 (highest). Governed by `DECISIONS.md` for amendments only — no other document may override this file.

This document records strategic rules supplied externally. It records; it does not derive, complete, or interpret. Any area left incomplete below is incomplete because no external authority has yet supplied it — it MUST NOT be filled in during implementation work.

## Status Vocabulary (binding on all documents)

- `LOCKED` — cannot be changed by implementation work.
- `TO_CALIBRATE` — requires empirical calibration; never invent a value.
- `EXTERNAL_DATA_REQUIRED` — requires external factual/contractual data.
- `MEASUREMENT_REQUIRED` — requires actual measurement before a numerical claim can be made.
- `NON_OPERATIONAL` — exists conceptually but cannot authorize dependent functionality.
- `PROVISIONAL` — temporary result explicitly unsuitable for final/live authorization.
- `VALIDATED` — passed the defined validation process.

## 1. Account Reference

| Item | Value | Status |
|---|---|---|
| Reference capital | EUR 1,000 | LOCKED |
| Account currency | EUR | LOCKED |
| Maximum simultaneous positions | 2 | LOCKED |

## 2. Risk Rules

- **R1** — maximum EUR 50 per position. `LOCKED`
- **R2** — maximum aggregate open risk EUR 100. `LOCKED`
- **R3** — maximum realized loss events EUR 100 over a rolling 14-day window. Loss events are recorded at realization/closure. Gains do not net against losses for R3. `LOCKED`
- **R4** — Circuit-breaker principle exists. Its final implementation is **not defined in this document** and MUST NOT be invented or reconstructed by implementation work. `NON_OPERATIONAL` pending specification.

## 3. Economic Objective

- Minimum opportunity potential: EUR 200 net.
- Preferred opportunity potential: EUR 300 net.
- The exact economic-gate implementation (how potential is computed, validated, and enforced) is governed by a specification not yet supplied. `NON_OPERATIONAL` pending specification. This summary MUST NOT be reverse-engineered into an implementation.

## 4. Strategy B — Holding Horizon

- Approximate holding horizon: 15–35 days. `LOCKED` (as a recorded parameter; not an operational rule set)

## 5. Technical Hierarchy

- **Strategy B**: W1 → D1 → H4, with H1 used only for execution refinement when legitimate.
- **Event/Position Intelligence**: W1 context, then D1 → H4 → H1.
- Principle: lower timeframes cannot repair higher-timeframe invalidation. `LOCKED` (as principle)

## 6. Technical Concepts (named only, not specified)

The following concepts are named for future empirical specification. None of them are operational definitions. Implementation work MUST NOT define, algorithmize, or approximate them:

- swing structure
- MSS (Market Structure Shift)
- BOS (Break of Structure)
- displacement
- liquidity sweep
- FVG (Fair Value Gap)
- Fibonacci retracement/confluence
- ATR
- volume confirmation
- structural invalidation

Fibonacci is confluence/localization only — it is explicitly NOT an autonomous entry signal.

All concepts above: `NON_OPERATIONAL`, `TO_CALIBRATE` where numeric thresholds would eventually apply.

## 7. Decision Pipeline (conceptual only)

```
TRUTH → MATERIALITY → SURPRISE → MARKET REACTION → CONFIRMATION → ASYMMETRY → RISK → POSITION
```

A true event is not automatically a tradable event. Only materially exploitable information belongs in the pipeline. Categories of potentially material events (not an exhaustive or operational list): central-bank decisions, inflation/employment releases, corporate earnings, guidance, inventory reports (e.g. energy inventories), regulatory decisions, FDA-type decisions, other verified market-moving events.

Status: `NON_OPERATIONAL` — no transition logic exists yet.

## 8. Opportunity States

`WATCH`, `ARMED`, `POSITION_READY`, `NO_TRADE`. No transition logic between these states is defined. `NON_OPERATIONAL`.

## 9. Architectural Principle (binding)

- Python/deterministic code owns: calculations, hard gates, risk constraints, sizing, deterministically evaluable state transitions.
- LLMs may later own: interpretation, thesis, counter-thesis, contradiction analysis, event interpretation, red-team reasoning.
- An LLM MUST NEVER override a deterministic hard-gate rejection.
- No automatic broker execution is authorized in V1.

Pipeline: `DATA → FILTER → ANALYSIS → RISK ENGINE → RECOMMENDATION → HUMAN VALIDATION → MANUAL EXECUTION`.

## 10. Target Market Scope (architectural capability only, not implemented)

US equities, European equities, Asian equities, ETFs, indices/CFDs, Forex, commodities, eligible crypto/CFDs. Market logic is NOT implemented in V1.

## 11. Broker (Vantage) Compatibility

Broker execution compatibility must eventually be evaluated against the user's actual Vantage account specifications. No Vantage specification is recorded here because none has been supplied. See `EXTERNAL_DATA.md`. `EXTERNAL_DATA_REQUIRED`.

## 12. Amendment Rule

Any change to this file requires a corresponding entry in `DECISIONS.md` stating date, decision, reason, affected components, and authority. Implementation work has no authority to amend this file.
