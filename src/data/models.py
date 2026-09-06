"""Normalized OHLCV market data schema with mandatory provenance."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class OHLCVBar:
    timestamp: datetime
    instrument: str
    timeframe: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal | None = None
    currency: str | None = None


@dataclass(frozen=True)
class DataProvenance:
    source: str
    retrieval_timestamp: datetime
    data_start: datetime
    data_end: datetime


@dataclass(frozen=True)
class MarketDataSeries:
    instrument: str
    timeframe: str
    bars: tuple[OHLCVBar, ...]
    provenance: DataProvenance
