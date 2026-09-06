"""Deterministic contract-specification structure.

Unknown fields remain `None` — nothing here infers, estimates, or
remembers a plausible broker value. `validation_status` and
`margin_rule_status` default to EXTERNAL_DATA_REQUIRED so a spec is never
silently treated as validated just because a caller forgot to set it.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.domain.status import Status

REQUIRED_FIELDS_FOR_MINIMUM_SIZE_RISK = (
    "minimum_lot",
    "price_tick_size",
    "tick_value",
    "quote_currency",
)


@dataclass(frozen=True)
class ContractSpec:
    instrument_id: str
    account_currency: str
    asset_class: str | None = None
    contract_size: Decimal | None = None
    minimum_lot: Decimal | None = None
    lot_increment: Decimal | None = None
    price_tick_size: Decimal | None = None
    tick_value: Decimal | None = None
    quote_currency: str | None = None
    margin_currency: str | None = None
    leverage: Decimal | None = None
    margin_rule_status: Status = Status.EXTERNAL_DATA_REQUIRED
    spread: Decimal | None = None
    commission: Decimal | None = None
    swap: Decimal | None = None
    trading_hours: str | None = None
    source: str | None = None
    source_timestamp: datetime | None = None
    validation_status: Status = Status.EXTERNAL_DATA_REQUIRED

    def missing_fields_for_minimum_size_risk(self) -> list[str]:
        return [
            name
            for name in REQUIRED_FIELDS_FOR_MINIMUM_SIZE_RISK
            if getattr(self, name) is None
        ]
