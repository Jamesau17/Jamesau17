"""Deterministic ATR(period) — a stop-distance proxy input, not a trading signal.

Wilder's smoothing method. The first `period - 1` points of any series are
warm-up and carry `value=None` rather than a fabricated number. A series
shorter than `period` bars cannot produce any ATR value at all and raises
DataQualityError instead of silently returning an all-None result.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Sequence

from src.data.models import OHLCVBar
from src.data.quality import DataQualityError

DEFAULT_PERIOD = 14


@dataclass(frozen=True)
class ATRPoint:
    timestamp: datetime
    value: Decimal | None


def true_range(high: Decimal, low: Decimal, prev_close: Decimal | None) -> Decimal:
    range_high_low = high - low
    if prev_close is None:
        return range_high_low
    return max(range_high_low, abs(high - prev_close), abs(low - prev_close))


def compute_atr_series(
    bars: Sequence[OHLCVBar], period: int = DEFAULT_PERIOD
) -> list[ATRPoint]:
    if len(bars) < period:
        raise DataQualityError(
            "insufficient_atr_warmup",
            f"{len(bars)} bars supplied, need at least {period} for ATR({period})",
        )

    true_ranges = [
        true_range(bar.high, bar.low, bars[i - 1].close if i > 0 else None)
        for i, bar in enumerate(bars)
    ]

    points: list[ATRPoint] = []
    atr_value: Decimal | None = None
    for i, bar in enumerate(bars):
        if i < period - 1:
            points.append(ATRPoint(timestamp=bar.timestamp, value=None))
            continue
        if i == period - 1:
            atr_value = sum(true_ranges[:period], Decimal(0)) / period
        else:
            assert atr_value is not None
            atr_value = (atr_value * (period - 1) + true_ranges[i]) / period
        points.append(ATRPoint(timestamp=bar.timestamp, value=atr_value))

    return points
