"""C0-SCREEN report assembly with mandatory provenance.

The report is a preliminary feasibility read-out, never a strategy result.
No PnL, win rate, or performance metric is ever placed on this object.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from src.data.models import DataProvenance
from src.risk.contract_specs import ContractSpec
from src.risk.fx import FXRate
from src.screening.c0_screen import ProxyMetrics, R2_RESIDUAL_SCENARIOS_EUR

DISCLAIMER = (
    "C0-SCREEN is a preliminary capital/instrument feasibility screen using "
    "PROVISIONAL ATR-based stop-distance proxies. It is NOT a strategy "
    "backtest, entry-signal engine, profitability measure, or final "
    "structural validation. Final structural compatibility is measured "
    "later by C0-FINAL once Bloc A exists."
)


@dataclass(frozen=True)
class ContractProvenance:
    source: str | None
    source_timestamp: datetime | None
    validation_status: str


@dataclass(frozen=True)
class FXProvenance:
    pair: str
    source: str
    timestamp: datetime


@dataclass(frozen=True)
class C0Report:
    generated_at: datetime
    instrument: str
    account_currency: str
    r1_eur: Decimal
    r2_residual_scenarios_eur: tuple[Decimal, ...]
    proxy_metrics: tuple[ProxyMetrics, ...]
    market_data_provenance: dict[str, DataProvenance]
    contract_provenance: ContractProvenance
    fx_provenance: FXProvenance | None
    disclaimer: str = DISCLAIMER


def build_report(
    market_data_provenance: dict[str, DataProvenance],
    contract: ContractSpec,
    r1_eur: Decimal,
    proxy_metrics: list[ProxyMetrics],
    fx_rate: FXRate | None = None,
    r2_residual_scenarios_eur: tuple[Decimal, ...] = R2_RESIDUAL_SCENARIOS_EUR,
    generated_at: datetime | None = None,
) -> C0Report:
    return C0Report(
        generated_at=generated_at or datetime.now(timezone.utc),
        instrument=contract.instrument_id,
        account_currency=contract.account_currency,
        r1_eur=r1_eur,
        r2_residual_scenarios_eur=r2_residual_scenarios_eur,
        proxy_metrics=tuple(proxy_metrics),
        market_data_provenance=market_data_provenance,
        contract_provenance=ContractProvenance(
            source=contract.source,
            source_timestamp=contract.source_timestamp,
            validation_status=contract.validation_status.value,
        ),
        fx_provenance=(
            FXProvenance(pair=fx_rate.pair, source=fx_rate.source, timestamp=fx_rate.timestamp)
            if fx_rate is not None
            else None
        ),
    )


def _to_jsonable(value: object) -> object:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {k: _to_jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    return value


def report_to_dict(report: C0Report) -> dict:
    return _to_jsonable(report)  # type: ignore[return-value]
