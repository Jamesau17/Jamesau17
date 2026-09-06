# PROJECT STATE

Tracks current implementation state only. Not a planning document.

## DONE

- Repository structure created (`config/`, `src/`, `tests/`, `scripts/`).
- Governance documents created: `CONSTITUTION.md`, `DECISIONS.md`, `PROJECT_STATE.md`, `ARCHITECTURE.md`, `DATA_REQUIREMENTS.md`, `EXTERNAL_DATA.md`.
- `config/risk_rules.yaml` created with LOCKED values recorded and unresolved parameters marked `null` with status metadata (never guessed).
- Core Synchronization Patch 00.1 applied: R4 and economic gate synchronized as `LOCKED` per `DECISIONS.md` (2026-09-06).
- `config/system_status.yaml` created recording per-component operational status.
- Bootstrap/governance tests created under `tests/`.

## IN_PROGRESS

- None.

## BLOCKED

- R_max computation — strategic definition `LOCKED` (`CONSTITUTION.md` §3a), but blocked on contractual/margin/cluster dependencies that remain `TO_CALIBRATE`/`EXTERNAL_DATA_REQUIRED`. No Risk Engine implementation exists yet.
- Opportunity-state transition logic — blocked on specification (`CONSTITUTION.md` §8). `NON_OPERATIONAL`. Not a blocker for C0-SCREEN.
- Decision-pipeline transition logic — blocked on specification (`CONSTITUTION.md` §7). `NON_OPERATIONAL`.
- RISK_SCALE_REVIEW protocol — blocked on specification (`CONSTITUTION.md` §3b). `NON_OPERATIONAL`.

## LOCKED (Core Synchronization Patch 00.1)

- R4 circuit breaker: EUR 150 drawdown from High-Water Mark; blocks new entries and scaling-in; requires reanalysis of open positions; no automatic liquidation. `CONSTITUTION.md` §2.
- Economic gate: minimum EUR 200 net AND 4R; preferred EUR 300 net AND 6R; evaluated against current R_max. `CONSTITUTION.md` §3.
- R_max conceptual definition and minimum-size admissibility ordering. `CONSTITUTION.md` §3a.
- Risk scaling: no automatic risk increase with capital growth. `CONSTITUTION.md` §3b.

## NON_OPERATIONAL

- Technical concepts (swing structure, MSS, BOS, displacement, liquidity sweep, FVG, Fibonacci confluence, ATR, volume confirmation, structural invalidation) — named only, no definitions exist.
- Multi-market instrument logic (equities, ETFs, indices/CFDs, Forex, commodities, crypto/CFDs) — architectural scope recorded, no logic implemented.
- Vantage broker compatibility — no account/instrument specification available. See `EXTERNAL_DATA.md`.
- SQLite persistence layer — intended, not yet implemented (not required for this bootstrap).
- R_max dependencies not yet calibrated/supplied: cluster/correlation constraints, contractual instrument constraints, minimum trade size, margin constraints, execution constraints.

## NEXT

- C0-SCREEN specification/implementation (see mission recommendation at end of this bootstrap).
