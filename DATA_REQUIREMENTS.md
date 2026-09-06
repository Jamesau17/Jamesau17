# DATA REQUIREMENTS

Records data required by future modules and the provenance model every material datum must support. Does not implement data ingestion.

## Provenance Model (mandatory shape for future data model)

Every material datum must be able to preserve:

- `source`
- `source_type`
- `timestamp`
- `retrieval_timestamp`
- `instrument`
- `value`
- `unit`
- `classification`

## Classification (minimum vocabulary)

- `FACT`
- `INTERPRETATION`
- `HYPOTHESIS`

Binding rule: interpretation must never overwrite the underlying fact. A `FACT` record is immutable once stored; an `INTERPRETATION` or `HYPOTHESIS` is a separate, linked record.

## Future Module Data Needs (recorded, not implemented)

- **`structure/`** — price series across W1 / D1 / H4 / H1 timeframes per instrument. `EXTERNAL_DATA_REQUIRED` (market data source not yet selected).
- **`events/`** — event calendar and release data (central-bank decisions, inflation/employment releases, corporate earnings, guidance, inventory reports, regulatory/FDA-type decisions). `EXTERNAL_DATA_REQUIRED`.
- **`risk/`** — realized/open position data for R1–R3 evaluation. Sourced from `journal/` once implemented. `NON_OPERATIONAL` until `journal/` exists.
- **`journal/`** — persistent record of decisions, recommendations, and manual executions. Intended store: SQLite. Not implemented in this bootstrap.

## Status

All data sources above are `EXTERNAL_DATA_REQUIRED` or `NON_OPERATIONAL`. No data source is connected, mocked, or fabricated in this bootstrap.
