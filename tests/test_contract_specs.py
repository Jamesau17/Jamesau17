from __future__ import annotations

from decimal import Decimal

from src.domain.status import Status
from src.risk.contract_specs import ContractSpec


def test_missing_fields_reported_when_nothing_supplied() -> None:
    spec = ContractSpec(instrument_id="EURUSD", account_currency="EUR")
    missing = spec.missing_fields_for_minimum_size_risk()
    assert set(missing) == {"minimum_lot", "price_tick_size", "tick_value", "quote_currency"}


def test_no_missing_fields_when_all_required_fields_supplied() -> None:
    spec = ContractSpec(
        instrument_id="EURUSD",
        account_currency="EUR",
        minimum_lot=Decimal("1000"),
        price_tick_size=Decimal("0.0001"),
        tick_value=Decimal("0.1"),
        quote_currency="EUR",
    )
    assert spec.missing_fields_for_minimum_size_risk() == []


def test_validation_status_defaults_to_external_data_required() -> None:
    spec = ContractSpec(instrument_id="EURUSD", account_currency="EUR")
    assert spec.validation_status == Status.EXTERNAL_DATA_REQUIRED
    assert spec.margin_rule_status == Status.EXTERNAL_DATA_REQUIRED
