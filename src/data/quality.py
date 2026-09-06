"""Market-data quality validation.

Critical errors are never silently repaired — they raise DataQualityError
so a bad dataset cannot flow into the screening engine unnoticed.
"""

from __future__ import annotations

from typing import Sequence

from src.data.models import OHLCVBar


class DataQualityError(Exception):
    def __init__(self, reason: str, detail: str) -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(f"{reason}: {detail}")


def validate_bars(bars: Sequence[OHLCVBar]) -> None:
    if not bars:
        raise DataQualityError("missing_data", "no bars supplied")

    seen_timestamps: set = set()
    prev_timestamp = None
    for bar in bars:
        if bar.timestamp in seen_timestamps:
            raise DataQualityError(
                "duplicate_timestamp",
                f"{bar.timestamp} appears more than once for {bar.instrument}/{bar.timeframe}",
            )
        seen_timestamps.add(bar.timestamp)

        if prev_timestamp is not None and bar.timestamp <= prev_timestamp:
            raise DataQualityError(
                "non_monotonic_timestamp",
                f"{bar.timestamp} does not come after {prev_timestamp}",
            )
        prev_timestamp = bar.timestamp

        for field_name, value in (
            ("open", bar.open),
            ("high", bar.high),
            ("low", bar.low),
            ("close", bar.close),
        ):
            if value is None:
                raise DataQualityError("missing_ohlc", f"{field_name} missing at {bar.timestamp}")
            if value <= 0:
                raise DataQualityError(
                    "non_positive_price", f"{field_name}={value} at {bar.timestamp}"
                )

        if bar.high < bar.low:
            raise DataQualityError(
                "high_less_than_low", f"high {bar.high} < low {bar.low} at {bar.timestamp}"
            )
        if bar.open > bar.high or bar.open < bar.low:
            raise DataQualityError(
                "ohlc_inconsistency",
                f"open {bar.open} outside [{bar.low}, {bar.high}] at {bar.timestamp}",
            )
        if bar.close > bar.high or bar.close < bar.low:
            raise DataQualityError(
                "ohlc_inconsistency",
                f"close {bar.close} outside [{bar.low}, {bar.high}] at {bar.timestamp}",
            )
