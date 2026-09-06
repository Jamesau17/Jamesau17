# DECISIONS LOG

Immutable-style log. Entries are appended, never edited or deleted. Each entry records a strategic or governance-affecting decision.

Format per entry:

```
## YYYY-MM-DD — <short title>
- Decision:
- Reason:
- Affected components:
- Authority:
```

---

## 2026-09-06 — Bootstrap of governed multi-market trading decision system (V1)

- Decision: Create repository structure, governance documents, configuration skeleton, and testing skeleton for the trading decision-support system. No trading logic, strategy implementation, or calibrated values were introduced.
- Reason: Establish a durable Context Pack and governance mechanism before any strategic content is implemented, per the external authority's bootstrap mission.
- Affected components: Entire repository (initial creation) — `CONSTITUTION.md`, `PROJECT_STATE.md`, `DECISIONS.md`, `ARCHITECTURE.md`, `DATA_REQUIREMENTS.md`, `EXTERNAL_DATA.md`, `config/`, `src/`, `tests/`, `scripts/`.
- Authority: Current task prompt (bootstrap mission), constrained by the authority order defined in `CONSTITUTION.md`. No conflicting higher authority existed at time of this decision (repository was empty).

---

## 2026-09-06 — Core Synchronization Patch 00.1: R4 and economic gate locked

- Decision: Record R4 (circuit breaker: EUR 150 drawdown from High-Water Mark, blocking new entries/scaling and requiring reanalysis of open positions, no automatic liquidation) and the economic gate (minimum EUR 200 net AND 4R; preferred EUR 300 net AND 6R, evaluated against current R_max) as `LOCKED` strategic rules, superseding their prior `NON_OPERATIONAL`/`EXTERNAL_DATA_REQUIRED` classification for their strategic definition. Record the R_max conceptual definition and minimum-size admissibility ordering. Record risk scaling as `LOCKED`: no automatic risk increase with capital growth.
- Reason: The strategic authority supplied these specifications; the repository must reflect them without reinterpretation, optimization, or invention of the remaining undefined dependencies (R_max's contractual/margin/cluster dependencies remain `TO_CALIBRATE`/`EXTERNAL_DATA_REQUIRED`).
- Affected components: `CONSTITUTION.md` (§2, §3, new §3a, §3b, §11), `EXTERNAL_DATA.md`, `PROJECT_STATE.md`, `ARCHITECTURE.md`, `config/risk_rules.yaml`, `config/system_status.yaml`, `tests/test_governance_config.py`.
- Authority: Current task prompt (Core Synchronization Patch 00.1), which the prompt itself states supersedes the prior `EXTERNAL_DATA_REQUIRED`/`NON_OPERATIONAL`/`TO_CALIBRATE`/`UNKNOWN` classification of R4 and the economic gate's strategic definition. Actual broker/account/instrument specifications remain `EXTERNAL_DATA_REQUIRED` and are unaffected by this decision.

---

## 2026-09-06 — C0-SCREEN implemented: capital/instrument feasibility engine

- Decision: Implement C0-SCREEN, a preliminary feasibility screen testing whether candidate instruments are realistically compatible with account capital, R1, and R2-residual scenarios, using a predeclared set of PROVISIONAL ATR-based stop-distance proxies (H4 ATR14×{1.0,1.5,2.0}, D1 ATR14×{0.5,1.0}). No trading signal, entry logic, or PnL/performance metric was implemented. Classification thresholds (CANDIDATE vs CONSTRAINED) remain configuration-driven and default to `null`/`TO_CALIBRATE` — never invented. R_max is intentionally not calculated or compared against at this stage (would be circular per the minimum-size admissibility ordering in `CONSTITUTION.md` §3a).
- Reason: Mission C0-SCREEN requires an empirical feasibility read before the final deterministic market-structure engine (Bloc A) exists, without pre-empting strategy, calibration, or broker-data decisions that remain external.
- Affected components: `src/data/{models,csv_loader,quality}.py`, `src/risk/{contract_specs,fx,calculators}.py`, `src/screening/{atr,c0_screen,report}.py`, `scripts/run_c0_screen.py`, `tests/{test_market_data_quality,test_contract_specs,test_minimum_size_risk,test_c0_screen}.py`, `ARCHITECTURE.md`, `PROJECT_STATE.md`.
- Authority: Current task prompt (C0-SCREEN mission), constrained by `CONSTITUTION.md` (R1/R2/R_max definitions, LOCKED and unaffected) and `DECISIONS.md` (Core Synchronization Patch 00.1). No LOCKED rule was changed. R2-residual scenario values (EUR 100/75/50/25) are analytical reporting scenarios only, not Constitution thresholds.
