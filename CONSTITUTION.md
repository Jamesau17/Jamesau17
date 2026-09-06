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
- **R4 — Circuit Breaker.** `LOCKED` (Core Synchronization Patch 00.1, 2026-09-06).
  - Threshold: EUR 150 drawdown from High-Water Mark (HWM).
  - HWM: the historical maximum observed account EQUITY (realized PnL + unrealized PnL).
  - `CURRENT_DD = HWM_EQUITY - CURRENT_EQUITY`.
  - Trigger: if `CURRENT_DD >= EUR 150`: (1) block all new entries; (2) block all scaling-in/additional entries; (3) immediately require reanalysis of every currently open position.
  - R4 does NOT automatically liquidate an existing position solely because the threshold was reached. Each open position must instead be re-evaluated against its actual thesis and invalidation criteria (structural invalidation, fundamental invalidation, new material information, event risk, gap risk, changed market conditions, as applicable).
  - No second liquidation threshold exists or is authorized.

## 3. Economic Objective

`LOCKED` (Core Synchronization Patch 00.1, 2026-09-06). The economic gate is evaluated against **current R_max** (see §3a).

- Minimum admissible opportunity: `NET POTENTIAL >= EUR 200` AND `NET R MULTIPLE >= 4R` (both mandatory).
- Preferred opportunity: `NET POTENTIAL >= EUR 300` AND `NET R MULTIPLE >= 6R` (preference criteria, not permission to violate a hard gate).
- Precedence: Hard Gates > Score > Preference.
- Mathematical note (explanatory only, not a threshold): when `R_max = EUR 50`, `4R = EUR 200`, so the EUR 200 and 4R conditions coincide. When `R_max < EUR 50`, the EUR 200 absolute-potential requirement may become the stricter condition (e.g. `R_max = EUR 25` → `EUR 200 / EUR 25 = 8R`, so a 4R setup alone would not satisfy the EUR 200 condition). EUR 25 is not itself a threshold and must not be treated as one.

## 3a. R_max — Conceptual Definition

`LOCKED` (conceptual definition) / dependencies `TO_CALIBRATE` or `EXTERNAL_DATA_REQUIRED` as noted (Core Synchronization Patch 00.1, 2026-09-06).

R_max is the maximum currently executable planned monetary risk for the trade after applying all relevant hard constraints. It may depend on: R1, remaining R2 capacity, cluster/correlation constraints, contractual instrument constraints, minimum trade size, margin constraints, execution constraints. Some of these dependencies remain `TO_CALIBRATE` or `EXTERNAL_DATA_REQUIRED` — their missing parameters MUST NOT be invented.

R_max must be recalculated immediately before execution, and the economic gate must be re-evaluated using that current R_max. If R_max is not definable because no legal position size can satisfy the hard constraints: `NO_TRADE`.

**Minimum-size admissibility ordering (conceptual order only, no thresholds invented):**

1. Determine structural invalidation.
2. Determine stop distance.
3. Retrieve actual instrument contractual specifications.
4. Calculate risk at the smallest legally tradable position size.
5. Compare minimum-size risk against R1, remaining R2 capacity, and applicable cluster constraints.
6. If minimum trade size violates a hard limit: `MINIMUM_SIZE_INCOMPATIBLE` → `NO_TRADE`.
7. Only if the instrument/setup is admissible can R_max be calculated.
8. Recalculate current R_max immediately before execution.
9. Apply the economic gate against current R_max.

Minimum-size risk MUST NOT be compared against R_max when determining minimum-size admissibility (circular — R_max does not yet exist at that stage).

## 3b. Risk Scaling

`LOCKED` (Core Synchronization Patch 00.1, 2026-09-06). Growth in account capital does NOT automatically increase permitted risk. No formula of the form "larger balance → automatically larger R1" is authorized. Any future increase of risk limits requires a separate documented `RISK_SCALE_REVIEW`. The protocol and empirical requirements of that review are not defined here and MUST NOT be invented.

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

Broker execution compatibility must eventually be evaluated against the user's actual Vantage account specifications (contract size, minimum lot, lot increment, tick/point value, leverage, margin, spreads, commissions, swaps, execution restrictions, etc.). No Vantage specification is recorded here because none has been supplied. See `EXTERNAL_DATA.md`. `EXTERNAL_DATA_REQUIRED`. This classification applies only to the actual broker/account/instrument specifications — it does not apply to the R4 or economic-gate strategic definitions, which are `LOCKED` per §2 and §3.

## 12. Amendment Rule

Any change to this file requires a corresponding entry in `DECISIONS.md` stating date, decision, reason, affected components, and authority. Implementation work has no authority to amend this file.
