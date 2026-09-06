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

## R4 Circuit-Breaker Specification

`CONSTITUTION.md` records that a circuit-breaker principle (R4) exists but its implementation is governed by a specification not yet supplied. `EXTERNAL_DATA_REQUIRED` / pending validated technical specification.

## Economic-Gate Specification

The exact computation and enforcement of the opportunity-potential economic gate (EUR 200 minimum / EUR 300 preferred, net) is governed by a specification not yet supplied. `EXTERNAL_DATA_REQUIRED` / pending validated technical specification.
