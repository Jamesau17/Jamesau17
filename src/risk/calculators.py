"""Minimum-lot monetary risk calculation.

Instrument-aware by design: `get_calculator` resolves a calculator by
`asset_class`, defaulting to a generic tick-value formula. This lets a
future asset-class-specific calculator (e.g. a different Forex or futures
convention) be registered without changing the interface or any caller.

No universal formula is assumed to hold for every instrument type.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol

from src.domain.results import ExternalDataRequired
from src.risk.contract_specs import ContractSpec
from src.risk.fx import FXRate, convert


class RiskCalculator(Protocol):
    def minimum_position_risk(
        self,
        stop_distance: Decimal,
        contract: ContractSpec,
        fx_rate: FXRate | None = None,
    ) -> Decimal | ExternalDataRequired: ...


class GenericTickValueRiskCalculator:
    """risk = (stop_distance / tick_size) * tick_value * minimum_lot, converted to account currency."""

    def minimum_position_risk(
        self,
        stop_distance: Decimal,
        contract: ContractSpec,
        fx_rate: FXRate | None = None,
    ) -> Decimal | ExternalDataRequired:
        missing = contract.missing_fields_for_minimum_size_risk()
        if missing:
            return ExternalDataRequired(missing=tuple(missing))

        assert contract.price_tick_size is not None
        assert contract.tick_value is not None
        assert contract.minimum_lot is not None
        assert contract.quote_currency is not None

        ticks = stop_distance / contract.price_tick_size
        risk_in_quote_currency = ticks * contract.tick_value * contract.minimum_lot

        return convert(
            risk_in_quote_currency,
            contract.quote_currency,
            contract.account_currency,
            fx_rate,
        )


_CALCULATORS_BY_ASSET_CLASS: dict[str, RiskCalculator] = {}


def get_calculator(asset_class: str | None) -> RiskCalculator:
    if asset_class is not None and asset_class in _CALCULATORS_BY_ASSET_CLASS:
        return _CALCULATORS_BY_ASSET_CLASS[asset_class]
    return GenericTickValueRiskCalculator()


def minimum_position_risk(
    stop_distance: Decimal,
    contract: ContractSpec,
    fx_rate: FXRate | None = None,
) -> Decimal | ExternalDataRequired:
    return get_calculator(contract.asset_class).minimum_position_risk(
        stop_distance, contract, fx_rate
    )
