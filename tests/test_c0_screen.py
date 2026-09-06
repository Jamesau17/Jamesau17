from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from src.data.models import DataProvenance, MarketDataSeries, OHLCVBar
from src.risk.contract_specs import ContractSpec
from src.screening.c0_screen import (
    ClassificationThresholds,
    ObservationResult,
    ProxyMetrics,
    aggregate,
    classify,
    load_r1_eur,
    screen_instrument,
)

FORBIDDEN_PERFORMANCE_TERMS = (
    "profit",
    "loss",
    "win_rate",
    "sharpe",
    "expectancy",
    "profit_factor",
    "score",
    "pnl",
)


def _valid_obs(risk: Decimal, idx: int = 0) -> ObservationResult:
    return ObservationResult(
        timestamp=idx, status="VALID", stop_distance=Decimal("1"), minimum_size_risk_eur=risk
    )


def _external_required_obs(idx: int = 0) -> ObservationResult:
    return ObservationResult(
        timestamp=idx,
        status="EXTERNAL_DATA_REQUIRED",
        stop_distance=Decimal("1"),
        minimum_size_risk_eur=None,
        missing=("minimum_lot",),
    )


def _insufficient_obs(idx: int = 0) -> ObservationResult:
    return ObservationResult(timestamp=idx, status="INSUFFICIENT_DATA", stop_distance=None, minimum_size_risk_eur=None)


def test_no_performance_metrics_exist_on_proxy_metrics() -> None:
    field_names = {f.name for f in dataclasses.fields(ProxyMetrics)}
    for term in FORBIDDEN_PERFORMANCE_TERMS:
        assert not any(term in name for name in field_names), f"forbidden metric-like field: {term}"


def test_aggregate_percentiles_and_compatibility() -> None:
    observations = [_valid_obs(Decimal(v), i) for i, v in enumerate((10, 20, 30, 40))]
    metrics = aggregate(
        instrument="TEST",
        timeframe="H4",
        proxy_name="H4_ATR14x1.0",
        observations=observations,
        r1_eur=Decimal("25"),
    )
    assert metrics.observations == 4
    assert metrics.valid_observations == 4
    assert metrics.minimum_size_compatible_count == 2
    assert metrics.minimum_size_incompatible_count == 2
    assert metrics.compatibility_percentage == Decimal("50")
    assert metrics.median_risk_eur == Decimal("25")
    assert metrics.p25_risk_eur == Decimal("17.5")
    assert metrics.p75_risk_eur == Decimal("32.5")
    assert metrics.p90_risk_eur == Decimal("37")
    assert metrics.max_risk_eur == Decimal("40")


def test_boundary_risk_equal_to_r1_is_compatible() -> None:
    metrics = aggregate(
        instrument="TEST",
        timeframe="H4",
        proxy_name="H4_ATR14x1.0",
        observations=[_valid_obs(Decimal("50"))],
        r1_eur=Decimal("50"),
    )
    assert metrics.minimum_size_compatible_count == 1
    assert metrics.minimum_size_incompatible_count == 0


def test_r2_residual_scenarios_apply_stricter_limit_than_r1() -> None:
    observations = [_valid_obs(Decimal("40"), i) for i in range(4)]
    metrics = aggregate(
        instrument="TEST",
        timeframe="H4",
        proxy_name="H4_ATR14x1.0",
        observations=observations,
        r1_eur=Decimal("50"),
        r2_residual_scenarios_eur=(Decimal("100"), Decimal("75"), Decimal("50"), Decimal("25")),
    )
    by_residual = {r.residual_eur: r for r in metrics.r2_scenarios}
    assert by_residual[Decimal("100")].compatible_count == 4
    assert by_residual[Decimal("50")].compatible_count == 4
    # residual 25 is stricter than R1 -> risk 40 no longer fits
    assert by_residual[Decimal("25")].compatible_count == 0
    assert by_residual[Decimal("25")].incompatible_count == 4


def test_classification_non_operational_when_no_valid_size_fits_r1() -> None:
    metrics = aggregate(
        instrument="TEST",
        timeframe="H4",
        proxy_name="H4_ATR14x1.0",
        observations=[_valid_obs(Decimal("100"), i) for i in range(3)],
        r1_eur=Decimal("50"),
    )
    assert metrics.classification == "NON_OPERATIONAL"


def test_classification_non_operational_when_specs_permanently_missing() -> None:
    result = classify(
        total_observations=3,
        valid_count=0,
        external_required_count=3,
        compatible_count=0,
        thresholds=None,
    )
    assert result == "NON_OPERATIONAL"


def test_classification_insufficient_data_when_only_warmup_points_exist() -> None:
    result = classify(
        total_observations=3,
        valid_count=0,
        external_required_count=0,
        compatible_count=0,
        thresholds=None,
    )
    assert result == "INSUFFICIENT_DATA"


def test_classification_defaults_to_to_calibrate_without_thresholds() -> None:
    assert ClassificationThresholds().min_compatibility_percentage is None
    result = classify(
        total_observations=4,
        valid_count=4,
        external_required_count=0,
        compatible_count=2,
        thresholds=None,
    )
    assert result == "TO_CALIBRATE"


def test_classification_uses_supplied_thresholds_when_present() -> None:
    thresholds = ClassificationThresholds(min_compatibility_percentage=Decimal("60"))
    candidate = classify(
        total_observations=4, valid_count=4, external_required_count=0, compatible_count=3, thresholds=thresholds
    )
    constrained = classify(
        total_observations=4, valid_count=4, external_required_count=0, compatible_count=1, thresholds=thresholds
    )
    assert candidate == "CANDIDATE"
    assert constrained == "CONSTRAINED"


def test_load_r1_eur_matches_locked_config() -> None:
    assert load_r1_eur() == Decimal("50")


def _flat_series(instrument: str, timeframe: str, n: int, half_range: str) -> MarketDataSeries:
    bars = tuple(
        OHLCVBar(
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(hours=4 * i),
            instrument=instrument,
            timeframe=timeframe,
            open=Decimal("100"),
            high=Decimal("100") + Decimal(half_range),
            low=Decimal("100") - Decimal(half_range),
            close=Decimal("100"),
        )
        for i in range(n)
    )
    provenance = DataProvenance(
        source="test-fixture",
        retrieval_timestamp=datetime.now(timezone.utc),
        data_start=bars[0].timestamp,
        data_end=bars[-1].timestamp,
    )
    return MarketDataSeries(instrument=instrument, timeframe=timeframe, bars=bars, provenance=provenance)


def test_screen_instrument_end_to_end_with_flat_fixture() -> None:
    h4_series = _flat_series("TEST", "H4", 20, "1")  # true range constant = 2
    d1_series = _flat_series("TEST", "D1", 20, "2")  # true range constant = 4
    contract = ContractSpec(
        instrument_id="TEST",
        account_currency="EUR",
        minimum_lot=Decimal("1"),
        price_tick_size=Decimal("1"),
        tick_value=Decimal("1"),
        quote_currency="EUR",
    )
    r1_eur = Decimal("50")

    results = screen_instrument({"H4": h4_series, "D1": d1_series}, contract, r1_eur)

    assert len(results) == 5
    for metrics in results:
        assert metrics.observations == 20
        assert metrics.insufficient_data_observations == 13
        assert metrics.valid_observations == 7
        assert metrics.data_quality_error is None
        assert metrics.classification in {"TO_CALIBRATE", "NON_OPERATIONAL"}

    h4_1x = next(m for m in results if m.proxy_name == "H4_ATR14x1.0")
    # ATR=2, multiplier=1.0 -> stop_distance=2 -> risk = 2/1 * 1 * 1 = 2 (compatible with R1=50)
    assert h4_1x.max_risk_eur == Decimal("2")
    assert h4_1x.minimum_size_compatible_count == 7


def test_screen_instrument_missing_timeframe_is_insufficient_data() -> None:
    h4_series = _flat_series("TEST", "H4", 20, "1")
    contract = ContractSpec(
        instrument_id="TEST",
        account_currency="EUR",
        minimum_lot=Decimal("1"),
        price_tick_size=Decimal("1"),
        tick_value=Decimal("1"),
        quote_currency="EUR",
    )
    results = screen_instrument({"H4": h4_series}, contract, Decimal("50"))
    d1_results = [m for m in results if m.timeframe == "D1"]
    assert all(m.classification == "INSUFFICIENT_DATA" for m in d1_results)
    assert all(m.data_quality_error == "missing_timeframe_data" for m in d1_results)


def test_screen_instrument_short_series_yields_data_quality_error() -> None:
    h4_series = _flat_series("TEST", "H4", 5, "1")  # fewer than ATR period (14)
    contract = ContractSpec(
        instrument_id="TEST",
        account_currency="EUR",
        minimum_lot=Decimal("1"),
        price_tick_size=Decimal("1"),
        tick_value=Decimal("1"),
        quote_currency="EUR",
    )
    results = screen_instrument({"H4": h4_series}, contract, Decimal("50"))
    h4_results = [m for m in results if m.timeframe == "H4"]
    assert all(m.classification == "INSUFFICIENT_DATA" for m in h4_results)
    assert all(m.data_quality_error is not None and "insufficient_atr_warmup" in m.data_quality_error for m in h4_results)


def test_screen_instrument_missing_contract_fields_is_non_operational() -> None:
    h4_series = _flat_series("TEST", "H4", 20, "1")
    d1_series = _flat_series("TEST", "D1", 20, "2")
    contract = ContractSpec(instrument_id="TEST", account_currency="EUR")  # nothing supplied
    results = screen_instrument({"H4": h4_series, "D1": d1_series}, contract, Decimal("50"))
    assert all(m.classification == "NON_OPERATIONAL" for m in results)
    assert all(m.valid_observations == 0 for m in results)
    assert all(m.external_data_required_observations == 7 for m in results)
