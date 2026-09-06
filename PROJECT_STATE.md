# PROJECT STATE

Tracks current implementation state only. Not a planning document.

## DONE

- Repository structure created (`config/`, `src/`, `tests/`, `scripts/`).
- Governance documents created: `CONSTITUTION.md`, `DECISIONS.md`, `PROJECT_STATE.md`, `ARCHITECTURE.md`, `DATA_REQUIREMENTS.md`, `EXTERNAL_DATA.md`.
- `config/risk_rules.yaml` created with LOCKED values recorded and unresolved parameters marked `null` with status metadata (never guessed).
- `config/system_status.yaml` created recording per-component operational status.
- Bootstrap/governance tests created under `tests/`.

## IN_PROGRESS

- None.

## BLOCKED

- R4 circuit-breaker implementation — blocked on specification (`CONSTITUTION.md` §2, R4). `NON_OPERATIONAL`.
- Economic-gate implementation — blocked on specification (`CONSTITUTION.md` §3). `NON_OPERATIONAL`.
- Opportunity-state transition logic — blocked on specification (`CONSTITUTION.md` §8). `NON_OPERATIONAL`.
- Decision-pipeline transition logic — blocked on specification (`CONSTITUTION.md` §7). `NON_OPERATIONAL`.

## NON_OPERATIONAL

- Technical concepts (swing structure, MSS, BOS, displacement, liquidity sweep, FVG, Fibonacci confluence, ATR, volume confirmation, structural invalidation) — named only, no definitions exist.
- Multi-market instrument logic (equities, ETFs, indices/CFDs, Forex, commodities, crypto/CFDs) — architectural scope recorded, no logic implemented.
- Vantage broker compatibility — no account/instrument specification available. See `EXTERNAL_DATA.md`.
- SQLite persistence layer — intended, not yet implemented (not required for this bootstrap).

## NEXT

- C0-SCREEN specification/implementation (see mission recommendation at end of this bootstrap).
