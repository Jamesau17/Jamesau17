# ARCHITECTURE

Defines technical boundaries and component responsibilities. Does not define trading logic.

## Pipeline (V1)

```
DATA → FILTER → ANALYSIS → RISK ENGINE → RECOMMENDATION → HUMAN VALIDATION → MANUAL EXECUTION
```

No automatic broker execution is authorized in V1. The pipeline terminates at a human-reviewed recommendation; execution is manual.

## Division of Responsibility

**Python / deterministic code owns:**
- Calculations
- Hard gates
- Risk constraints
- Sizing
- State transitions that can be deterministically evaluated

**LLMs may later own (not implemented in V1):**
- Interpretation
- Thesis / counter-thesis
- Contradiction analysis
- Event interpretation
- Red-team reasoning

**Binding constraint:** an LLM must never override a deterministic hard-gate rejection.

## Module Responsibilities (`src/`)

- `domain/` — core domain types shared across modules (instrument identity, monetary values, status enums). No trading logic.
- `risk/` — risk-rule representations and hard-gate evaluation (R1–R4, economic gate, R_max). Values sourced from `config/risk_rules.yaml`; nothing hardcoded or invented. R4 and the economic gate strategic definitions are `LOCKED` (`CONSTITUTION.md` §2–§3a); no evaluation logic is implemented in this repository state.
- `data/` — data ingestion and provenance modeling (see `DATA_REQUIREMENTS.md`). No live data sources connected in this bootstrap.
- `structure/` — placeholder for future market-structure concepts (swing structure, MSS, BOS, FVG, etc.). Contains no definitions in this bootstrap — `NON_OPERATIONAL`.
- `events/` — placeholder for future event/materiality pipeline (`TRUTH → MATERIALITY → ... → POSITION`). No transition logic in this bootstrap — `NON_OPERATIONAL`.
- `journal/` — placeholder for future position/decision journaling. Intended persistence layer is SQLite; not implemented in this bootstrap.

## Persistence

SQLite is the intended initial persistence layer. Not implemented in this bootstrap — no database schema or connection code exists yet, per the minimal-bootstrap scope.

## Multi-Market Scope

The system must eventually be architecturally capable of evaluating: US equities, European equities, Asian equities, ETFs, indices/CFDs, Forex, commodities, eligible crypto/CFDs. No market-specific logic is implemented in this bootstrap.

## Explicit Non-Goals for This Repository State

- No backtesting.
- No calibration.
- No trading signal generation.
- No entry/stop/lot-size determination.
- No broker connection (Vantage or otherwise).
- No invented broker/instrument data.
- No autonomous agents.
- No implementation of Strategy B, MSS, BOS, or FVG algorithms.
- No investment selection or profitability optimization.
- No modification of strategic principles defined in `CONSTITUTION.md`.
