from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.data.models import OHLCVBar
from src.data.quality import DataQualityError
from src.domain.results import ExternalDataRequired
from src.risk.calculators import minimum_position_risk
from src.risk.contract_specs import ContractSpec
from src.risk.fx import FXRate, convert
from src.screening.atr import compute_atr_series


def _flat_bars(n: int) -> list[OHLCVBar]:
    """Deterministic synthetic test fixture: constant true range of 2."""
    return [
        OHLCVBar(
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=4 * i),
            instrument="TEST",
            timeframe="H4",
            open=Decimal("10"),
            high=Decimal("11"),
            low=Decimal("9"),
            close=Decimal("10"),
        )
        for i in range(n)
    ]


def test_atr_is_deterministic_on_flat_fixture() -> None:
    bars = _flat_bars(16)
    points = compute_atr_series(bars, period=14)
    assert len(points) == 16
    assert all(point.value is None for point in points[:13])
    assert all(point.value == Decimal("2") for point in points[13:])


def test_atr_exact_period_length_yields_single_valid_point() -> None:
    bars = _flat_bars(14)
    points = compute_atr_series(bars, period=14)
    assert all(point.value is None for point in points[:13])
    assert points[13].value == Decimal("2")


def test_atr_insufficient_warmup_raises_data_quality_error() -> None:
    bars = _flat_bars(10)
    with pytest.raises(DataQualityError) as exc:
        compute_atr_series(bars, period=14)
    assert exc.value.reason == "insufficient_atr_warmup"


def _full_contract() -> ContractSpec:
    return ContractSpec(
        instrument_id="EURUSD",
        account_currency="EUR",
        minimum_lot=Decimal("5"),
        price_tick_size=Decimal("0.0001"),
        tick_value=Decimal("1"),
        quote_currency="EUR",
    )


def test_minimum_position_risk_matches_manual_calculation() -> None:
    contract = _full_contract()
    stop_distance = Decimal("0.0010")
    risk = minimum_position_risk(stop_distance, contract)
    # (0.0010 / 0.0001) ticks * 1 tick_value * 5 minimum_lot = 50
    assert risk == Decimal("50")


def test_minimum_position_risk_missing_contract_fields_returns_external_data_required() -> None:
    contract = ContractSpec(instrument_id="EURUSD", account_currency="EUR")
    result = minimum_position_risk(Decimal("0.0010"), contract)
    assert isinstance(result, ExternalDataRequired)
    assert set(result.missing) == {"minimum_lot", "price_tick_size", "tick_value", "quote_currency"}


def test_minimum_position_risk_requires_fx_when_currencies_differ() -> None:
    contract = ContractSpec(
        instrument_id="USDJPY",
        account_currency="EUR",
        minimum_lot=Decimal("5"),
        price_tick_size=Decimal("0.01"),
        tick_value=Decimal("1"),
        quote_currency="USD",
    )
    result = minimum_position_risk(Decimal("0.10"), contract, fx_rate=None)
    assert isinstance(result, ExternalDataRequired)
    assert result.missing == ("fx_rate:USD/EUR",)


def test_minimum_position_risk_converts_with_supplied_fx_rate() -> None:
    contract = ContractSpec(
        instrument_id="USDJPY",
        account_currency="EUR",
        minimum_lot=Decimal("5"),
        price_tick_size=Decimal("0.01"),
        tick_value=Decimal("1"),
        quote_currency="USD",
    )
    fx_rate = FXRate(pair="USD/EUR", source="test-fixture", timestamp=datetime.now(timezone.utc), rate=Decimal("0.9"))
    risk = minimum_position_risk(Decimal("0.10"), contract, fx_rate=fx_rate)
    # (0.10 / 0.01) * 1 * 5 = 50 USD -> * 0.9 = 45 EUR
    assert risk == Decimal("45.0")


def test_fx_convert_same_currency_is_identity() -> None:
    assert convert(Decimal("10"), "EUR", "EUR", None) == Decimal("10")


def test_fx_convert_wrong_pair_returns_external_data_required() -> None:
    fx_rate = FXRate(pair="GBP/EUR", source="test", timestamp=datetime.now(timezone.utc), rate=Decimal("1.1"))
    result = convert(Decimal("10"), "USD", "EUR", fx_rate)
    assert isinstance(result, ExternalDataRequired)
