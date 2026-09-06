# Trading Decision System (V1 Bootstrap)

Governed multi-market trading decision-support system. This repository is the durable Context Pack, governance mechanism, and bootstrap skeleton for the project. It contains no trading strategy, no trading signals, and no broker execution.

## Authority Order

1. `CONSTITUTION.md`
2. `DECISIONS.md`
3. Validated technical specifications
4. Existing tested implementation
5. Current task prompt

A lower authority never silently overrides a higher one. Conflicts are surfaced, not resolved by implementation work.

## Documents

- `CONSTITUTION.md` — authoritative strategic rules, recorded as supplied. Incomplete areas are marked explicitly, never filled in.
- `DECISIONS.md` — immutable-style decision log.
- `PROJECT_STATE.md` — current implementation state (DONE / IN_PROGRESS / BLOCKED / NON_OPERATIONAL / NEXT).
- `ARCHITECTURE.md` — technical boundaries and component responsibilities.
- `DATA_REQUIREMENTS.md` — data required by future modules and the mandatory provenance model.
- `EXTERNAL_DATA.md` — unresolved external dependencies (broker specification, market data source).

## Pipeline (V1)

```
DATA → FILTER → ANALYSIS → RISK ENGINE → RECOMMENDATION → HUMAN VALIDATION → MANUAL EXECUTION
```

No automatic broker execution is authorized in V1.

## Repository Layout

```
config/
  risk_rules.yaml       # machine-readable risk parameters; unknowns are null with status metadata
  system_status.yaml    # per-component operational status
src/
  domain/                # shared domain types
  risk/                  # risk-rule representation and hard-gate evaluation
  data/                  # data provenance modeling
  structure/              # placeholder — no market-structure definitions yet
  events/                 # placeholder — no event pipeline logic yet
  journal/                # placeholder — future SQLite-backed journal
tests/                    # bootstrap/governance tests
scripts/
```

## Status Vocabulary

`LOCKED`, `TO_CALIBRATE`, `EXTERNAL_DATA_REQUIRED`, `MEASUREMENT_REQUIRED`, `NON_OPERATIONAL`, `PROVISIONAL`, `VALIDATED`. See `CONSTITUTION.md` for definitions. Unknown values remain unknown — never replaced with estimates, conventions, or guesses.

## Requirements

- Python 3.12+
- pytest
