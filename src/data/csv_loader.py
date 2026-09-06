"""CSV loading into the normalized OHLCV schema.

Designed so future non-CSV adapters (broker/market-data APIs) can be added
alongside this one without changing MarketDataSeries or the quality checks.
No vendor is hard-wired here.
"""

from __future__ import annotations

import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from src.data.models import DataProvenance, MarketDataSeries, OHLCVBar
from src.data.quality import DataQualityError, validate_bars

REQUIRED_COLUMNS = {"timestamp", "instrument", "timeframe", "open", "high", "low", "close"}


def load_ohlcv_csv(path: Path, source: str, retrieval_timestamp: datetime) -> MarketDataSeries:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing_columns:
            raise DataQualityError(
                "missing_columns", f"CSV missing required columns: {sorted(missing_columns)}"
            )

        bars: list[OHLCVBar] = []
        instrument: str | None = None
        timeframe: str | None = None

        for row in reader:
            try:
                timestamp = datetime.fromisoformat(row["timestamp"])
                row_instrument = row["instrument"]
                row_timeframe = row["timeframe"]
                open_price = Decimal(row["open"])
                high = Decimal(row["high"])
                low = Decimal(row["low"])
                close = Decimal(row["close"])
            except (KeyError, InvalidOperation, ValueError) as exc:
                raise DataQualityError("parse_error", str(exc)) from exc

            volume_raw = row.get("volume")
            volume = Decimal(volume_raw) if volume_raw not in (None, "") else None
            currency = row.get("currency") or None

            if instrument is None:
                instrument, timeframe = row_instrument, row_timeframe
            elif row_instrument != instrument or row_timeframe != timeframe:
                raise DataQualityError(
                    "mixed_series",
                    "CSV contains multiple instrument/timeframe combinations; "
                    "load one series per file",
                )

            bars.append(
                OHLCVBar(
                    timestamp=timestamp,
                    instrument=row_instrument,
                    timeframe=row_timeframe,
                    open=open_price,
                    high=high,
                    low=low,
                    close=close,
                    volume=volume,
                    currency=currency,
                )
            )

    validate_bars(bars)
    assert instrument is not None and timeframe is not None

    provenance = DataProvenance(
        source=source,
        retrieval_timestamp=retrieval_timestamp,
        data_start=bars[0].timestamp,
        data_end=bars[-1].timestamp,
    )
    return MarketDataSeries(
        instrument=instrument, timeframe=timeframe, bars=tuple(bars), provenance=provenance
    )
