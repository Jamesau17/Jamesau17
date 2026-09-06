"""FX conversion — never fetched live, never invented.

A conversion across currencies requires an explicitly supplied FXRate for
the exact pair. Missing or mismatched rates return ExternalDataRequired.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.domain.results import ExternalDataRequired


@dataclass(frozen=True)
class FXRate:
    pair: str  # "FROM/TO", e.g. "USD/EUR" meaning 1 USD = `rate` EUR
    source: str
    timestamp: datetime
    rate: Decimal


def convert(
    amount: Decimal,
    from_currency: str,
    to_currency: str,
    fx_rate: FXRate | None,
) -> Decimal | ExternalDataRequired:
    if from_currency == to_currency:
        return amount

    expected_pair = f"{from_currency}/{to_currency}"
    if fx_rate is None or fx_rate.pair != expected_pair:
        return ExternalDataRequired(missing=(f"fx_rate:{expected_pair}",))

    return amount * fx_rate.rate
