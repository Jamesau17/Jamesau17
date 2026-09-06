from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from src.data.csv_loader import load_ohlcv_csv
from src.data.models import OHLCVBar
from src.data.quality import DataQualityError, validate_bars


def _bar(hour: int, o="10", h="11", l="9", c="10.5") -> OHLCVBar:
    return OHLCVBar(
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=hour),
        instrument="TEST",
        timeframe="H4",
        open=Decimal(o),
        high=Decimal(h),
        low=Decimal(l),
        close=Decimal(c),
    )


def test_valid_bars_pass_validation() -> None:
    bars = [_bar(0), _bar(4), _bar(8)]
    validate_bars(bars)  # must not raise


def test_empty_bars_rejected() -> None:
    with pytest.raises(DataQualityError) as exc:
        validate_bars([])
    assert exc.value.reason == "missing_data"


def test_duplicate_timestamps_rejected() -> None:
    bars = [_bar(0), _bar(0)]
    with pytest.raises(DataQualityError) as exc:
        validate_bars(bars)
    assert exc.value.reason == "duplicate_timestamp"


def test_non_monotonic_timestamps_rejected() -> None:
    bars = [_bar(4), _bar(0)]
    with pytest.raises(DataQualityError) as exc:
        validate_bars(bars)
    assert exc.value.reason == "non_monotonic_timestamp"


def test_high_less_than_low_rejected() -> None:
    bars = [_bar(0, h="8", l="9")]
    with pytest.raises(DataQualityError) as exc:
        validate_bars(bars)
    assert exc.value.reason == "high_less_than_low"


def test_open_outside_range_rejected() -> None:
    bars = [_bar(0, o="20")]
    with pytest.raises(DataQualityError) as exc:
        validate_bars(bars)
    assert exc.value.reason == "ohlc_inconsistency"


def test_non_positive_price_rejected() -> None:
    bars = [_bar(0, o="0")]
    with pytest.raises(DataQualityError) as exc:
        validate_bars(bars)
    assert exc.value.reason == "non_positive_price"


CSV_HEADER = "timestamp,instrument,timeframe,open,high,low,close,volume,currency\n"


def test_csv_loader_parses_valid_series(tmp_path: Path) -> None:
    csv_path = tmp_path / "series.csv"
    csv_path.write_text(
        CSV_HEADER
        + "2026-01-01T00:00:00+00:00,EURUSD,H4,1.10,1.11,1.09,1.105,1000,USD\n"
        + "2026-01-01T04:00:00+00:00,EURUSD,H4,1.105,1.12,1.10,1.115,1200,USD\n",
        encoding="utf-8",
    )
    series = load_ohlcv_csv(csv_path, source="test-fixture", retrieval_timestamp=datetime.now(timezone.utc))
    assert series.instrument == "EURUSD"
    assert series.timeframe == "H4"
    assert len(series.bars) == 2
    assert series.provenance.source == "test-fixture"
    assert series.provenance.data_start == series.bars[0].timestamp
    assert series.provenance.data_end == series.bars[-1].timestamp


def test_csv_loader_rejects_missing_columns(tmp_path: Path) -> None:
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("timestamp,instrument,timeframe,open,high,low\n2026-01-01T00:00:00+00:00,EURUSD,H4,1,1,1\n", encoding="utf-8")
    with pytest.raises(DataQualityError) as exc:
        load_ohlcv_csv(csv_path, source="test-fixture", retrieval_timestamp=datetime.now(timezone.utc))
    assert exc.value.reason == "missing_columns"


def test_csv_loader_rejects_mixed_series(tmp_path: Path) -> None:
    csv_path = tmp_path / "mixed.csv"
    csv_path.write_text(
        CSV_HEADER
        + "2026-01-01T00:00:00+00:00,EURUSD,H4,1.10,1.11,1.09,1.105,,\n"
        + "2026-01-01T04:00:00+00:00,GBPUSD,H4,1.30,1.31,1.29,1.305,,\n",
        encoding="utf-8",
    )
    with pytest.raises(DataQualityError) as exc:
        load_ohlcv_csv(csv_path, source="test-fixture", retrieval_timestamp=datetime.now(timezone.utc))
    assert exc.value.reason == "mixed_series"
