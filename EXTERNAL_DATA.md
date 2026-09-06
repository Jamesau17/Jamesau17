# EXTERNAL DATA — UNRESOLVED DEPENDENCIES

Lists external dependencies not yet satisfied. No value in this file is a guess, estimate, industry convention, or remembered broker specification.

## Vantage Broker/Account Compatibility

Future Vantage compatibility requires actual account/instrument specifications, including where applicable:

- instrument identifier
- contract size
- minimum lot
- lot increment
- tick/point size
- tick/point value
- quote currency
- effective leverage
- margin requirements
- spread
- commissions
- overnight financing/swap
- trading hours
- relevant execution restrictions

Status: `EXTERNAL_DATA_REQUIRED` for all items above. None may be filled with assumed, typical, or remembered values. Broker execution compatibility will be evaluated only against the user's actual Vantage account specifications when supplied.

## Market Data Source

No market data source (price series, event calendar) has been selected or connected. `EXTERNAL_DATA_REQUIRED`.

## R4 Circuit-Breaker — Strategic Specification LOCKED

R4's strategic definition (EUR 150 drawdown from High-Water Mark; blocks new entries/scaling-in; requires reanalysis of open positions; no automatic liquidation) is `LOCKED` per `CONSTITUTION.md` §2 (Core Synchronization Patch 00.1, 2026-09-06). It is **not** `EXTERNAL_DATA_REQUIRED`.

## Economic Gate — Strategic Specification LOCKED

The economic gate's strategic definition (minimum EUR 200 net AND 4R; preferred EUR 300 net AND 6R; evaluated against current R_max) is `LOCKED` per `CONSTITUTION.md` §3 (Core Synchronization Patch 00.1, 2026-09-06). It is **not** `EXTERNAL_DATA_REQUIRED`.

## R_max Dependencies — Partially External/Uncalibrated

R_max's conceptual definition is `LOCKED` (`CONSTITUTION.md` §3a), but the following dependencies remain unresolved and MUST NOT be guessed:

- contractual instrument constraints (minimum lot, lot increment, tick/point value, margin) — `EXTERNAL_DATA_REQUIRED` (see Vantage section above)
- cluster/correlation constraints — `TO_CALIBRATE`
- minimum trade size per instrument — `EXTERNAL_DATA_REQUIRED`
- execution constraints — `EXTERNAL_DATA_REQUIRED`

## RISK_SCALE_REVIEW Protocol

`CONSTITUTION.md` §3b records that any future increase of risk limits requires a separate documented `RISK_SCALE_REVIEW`. Its protocol and empirical requirements are not yet supplied. `NON_OPERATIONAL` pending specification (not `EXTERNAL_DATA_REQUIRED` — this is a governance protocol, not factual/contractual data).
