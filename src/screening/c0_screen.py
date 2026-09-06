"""C0-SCREEN — capital/instrument feasibility screen.

Answers one preliminary question: for a given instrument and current
contractual specification, how often would plausible H4/D1 stop-distance
proxies cause the minimum legally tradable position size to violate
current risk limits?

This is NOT a strategy backtest, entry-signal engine, or final structural
validation, and it produces no PnL/win-rate/performance metric. Stop
distances here are PROVISIONAL ATR-based proxies only (see PROXIES below),
predeclared and never tuned for best results.

Ordering (locked by the mission, not a design choice made here):
  1. provisional stop-distance observation (ATR proxy)
  2. actual contract specification
  3. monetary risk at minimum legally tradable size
  4. FX conversion to account currency when required
  5. compare minimum-size risk against R1
  6. also report compatibility under configurable R2 residual scenarios
R_max is never calculated or compared against here — that would be
circular, since minimum-size admissibility must be decided first.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Literal

from src.data.models import MarketDataSeries
from src.data.quality import DataQualityError
from src.domain.config_loader import load_yaml
from src.domain.results import ExternalDataRequired
from src.risk.calculators import minimum_position_risk
from src.risk.contract_specs import ContractSpec
from src.risk.fx import FXRate
from src.screening.atr import compute_atr_series

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RISK_RULES_PATH = REPO_ROOT / "config" / "risk_rules.yaml"

ObservationStatus = Literal["VALID", "INSUFFICIENT_DATA", "EXTERNAL_DATA_REQUIRED"]
# CANDIDATE/CONSTRAINED require classification_thresholds to be supplied (never
# invented here). Until then, combinations that aren't deterministically
# NON_OPERATIONAL or INSUFFICIENT_DATA report the descriptive status TO_CALIBRATE
# instead of a guessed CANDIDATE/CONSTRAINED split.
Classification = Literal["CANDIDATE", "CONSTRAINED", "NON_OPERATIONAL", "INSUFFICIENT_DATA", "TO_CALIBRATE"]


@dataclass(frozen=True)
class ProxyDefinition:
    """A PROVISIONAL stop-distance proxy. Feasibility probe only — not a trading stop."""

    timeframe: str
    name: str
    atr_period: int
    multiplier: Decimal


# Predeclared, fixed set. Do not add variants or tune multipliers here —
# these are feasibility probes, not a parameter search.
PROXIES: tuple[ProxyDefinition, ...] = (
    ProxyDefinition("H4", "H4_ATR14x1.0", 14, Decimal("1.0")),
    ProxyDefinition("H4", "H4_ATR14x1.5", 14, Decimal("1.5")),
    ProxyDefinition("H4", "H4_ATR14x2.0", 14, Decimal("2.0")),
    ProxyDefinition("D1", "D1_ATR14x0.5", 14, Decimal("0.5")),
    ProxyDefinition("D1", "D1_ATR14x1.0", 14, Decimal("1.0")),
)

# Analytical scenarios only, not Constitution thresholds — see CONSTITUTION.md
# §3a (R2 residual capacity is a real dependency of R_max; these four values
# are illustrative reporting scenarios, not a strategic rule).
R2_RESIDUAL_SCENARIOS_EUR: tuple[Decimal, ...] = (
    Decimal("100"),
    Decimal("75"),
    Decimal("50"),
    Decimal("25"),
)


def load_r1_eur(config_path: Path = DEFAULT_RISK_RULES_PATH) -> Decimal:
    data = load_yaml(config_path)
    return Decimal(str(data["risk_rules"]["R1_max_risk_per_position"]["value"]))


@dataclass(frozen=True)
class ObservationResult:
    timestamp: object
    status: ObservationStatus
    stop_distance: Decimal | None
    minimum_size_risk_eur: Decimal | None
    missing: tuple[str, ...] = field(default_factory=tuple)


def evaluate_proxy(
    series: MarketDataSeries,
    proxy: ProxyDefinition,
    contract: ContractSpec,
    fx_rate: FXRate | None = None,
) -> list[ObservationResult]:
    atr_points = compute_atr_series(series.bars, period=proxy.atr_period)

    results: list[ObservationResult] = []
    for atr_point in atr_points:
        if atr_point.value is None:
            results.append(
                ObservationResult(
                    timestamp=atr_point.timestamp,
                    status="INSUFFICIENT_DATA",
                    stop_distance=None,
                    minimum_size_risk_eur=None,
                )
            )
            continue

        stop_distance = atr_point.value * proxy.multiplier
        risk = minimum_position_risk(stop_distance, contract, fx_rate)
        if isinstance(risk, ExternalDataRequired):
            results.append(
                ObservationResult(
                    timestamp=atr_point.timestamp,
                    status="EXTERNAL_DATA_REQUIRED",
                    stop_distance=stop_distance,
                    minimum_size_risk_eur=None,
                    missing=risk.missing,
                )
            )
        else:
            results.append(
                ObservationResult(
                    timestamp=atr_point.timestamp,
                    status="VALID",
                    stop_distance=stop_distance,
                    minimum_size_risk_eur=risk,
                )
            )
    return results


@dataclass(frozen=True)
class R2ScenarioResult:
    residual_eur: Decimal
    compatible_count: int
    incompatible_count: int
    compatibility_percentage: Decimal | None


@dataclass(frozen=True)
class ClassificationThresholds:
    """Classification policy is configuration, never an invented constant.

    Left at its default (None), C0-SCREEN reports raw measurements only —
    it never guesses where CANDIDATE ends and CONSTRAINED begins.
    """

    min_compatibility_percentage: Decimal | None = None


@dataclass(frozen=True)
class ProxyMetrics:
    instrument: str
    timeframe: str
    proxy_name: str
    observations: int
    valid_observations: int
    insufficient_data_observations: int
    external_data_required_observations: int
    minimum_size_compatible_count: int
    minimum_size_incompatible_count: int
    compatibility_percentage: Decimal | None
    incompatibility_percentage: Decimal | None
    median_risk_eur: Decimal | None
    p25_risk_eur: Decimal | None
    p75_risk_eur: Decimal | None
    p90_risk_eur: Decimal | None
    max_risk_eur: Decimal | None
    r2_scenarios: tuple[R2ScenarioResult, ...]
    classification: Classification
    data_quality_error: str | None = None


def _percentile(sorted_values: list[Decimal], pct: Decimal) -> Decimal:
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = Decimal(len(sorted_values) - 1) * pct
    lower_index = int(rank)
    upper_index = min(lower_index + 1, len(sorted_values) - 1)
    if lower_index == upper_index:
        return sorted_values[lower_index]
    lower_weight = Decimal(upper_index) - rank
    upper_weight = rank - Decimal(lower_index)
    return sorted_values[lower_index] * lower_weight + sorted_values[upper_index] * upper_weight


def classify(
    *,
    total_observations: int,
    valid_count: int,
    external_required_count: int,
    compatible_count: int,
    thresholds: ClassificationThresholds | None,
) -> Classification:
    if total_observations == 0:
        return "INSUFFICIENT_DATA"
    if valid_count == 0:
        return "NON_OPERATIONAL" if external_required_count > 0 else "INSUFFICIENT_DATA"
    if compatible_count == 0:
        # No legal minimum size satisfies R1 across any valid tested observation.
        return "NON_OPERATIONAL"
    if thresholds is None or thresholds.min_compatibility_percentage is None:
        return "TO_CALIBRATE"
    compat_pct = Decimal(compatible_count) / valid_count * 100
    return "CANDIDATE" if compat_pct >= thresholds.min_compatibility_percentage else "CONSTRAINED"


def aggregate(
    *,
    instrument: str,
    timeframe: str,
    proxy_name: str,
    observations: list[ObservationResult],
    r1_eur: Decimal,
    r2_residual_scenarios_eur: tuple[Decimal, ...] = R2_RESIDUAL_SCENARIOS_EUR,
    thresholds: ClassificationThresholds | None = None,
) -> ProxyMetrics:
    total = len(observations)
    valid = [o for o in observations if o.status == "VALID"]
    insufficient = [o for o in observations if o.status == "INSUFFICIENT_DATA"]
    external_required = [o for o in observations if o.status == "EXTERNAL_DATA_REQUIRED"]

    risks = [o.minimum_size_risk_eur for o in valid if o.minimum_size_risk_eur is not None]
    compatible = [r for r in risks if r <= r1_eur]
    incompatible = [r for r in risks if r > r1_eur]
    risks_sorted = sorted(risks)

    compat_pct = Decimal(len(compatible)) / len(risks) * 100 if risks else None
    incompat_pct = Decimal(len(incompatible)) / len(risks) * 100 if risks else None

    r2_results = tuple(
        _r2_scenario(residual, risks, r1_eur) for residual in r2_residual_scenarios_eur
    )

    classification = classify(
        total_observations=total,
        valid_count=len(valid),
        external_required_count=len(external_required),
        compatible_count=len(compatible),
        thresholds=thresholds,
    )

    return ProxyMetrics(
        instrument=instrument,
        timeframe=timeframe,
        proxy_name=proxy_name,
        observations=total,
        valid_observations=len(valid),
        insufficient_data_observations=len(insufficient),
        external_data_required_observations=len(external_required),
        minimum_size_compatible_count=len(compatible),
        minimum_size_incompatible_count=len(incompatible),
        compatibility_percentage=compat_pct,
        incompatibility_percentage=incompat_pct,
        median_risk_eur=_percentile(risks_sorted, Decimal("0.5")) if risks_sorted else None,
        p25_risk_eur=_percentile(risks_sorted, Decimal("0.25")) if risks_sorted else None,
        p75_risk_eur=_percentile(risks_sorted, Decimal("0.75")) if risks_sorted else None,
        p90_risk_eur=_percentile(risks_sorted, Decimal("0.90")) if risks_sorted else None,
        max_risk_eur=risks_sorted[-1] if risks_sorted else None,
        r2_scenarios=r2_results,
        classification=classification,
    )


def _r2_scenario(
    residual_eur: Decimal, risks: list[Decimal], r1_eur: Decimal
) -> R2ScenarioResult:
    limit = min(r1_eur, residual_eur)
    compatible_count = sum(1 for r in risks if r <= limit)
    incompatible_count = len(risks) - compatible_count
    pct = Decimal(compatible_count) / len(risks) * 100 if risks else None
    return R2ScenarioResult(
        residual_eur=residual_eur,
        compatible_count=compatible_count,
        incompatible_count=incompatible_count,
        compatibility_percentage=pct,
    )


def screen_instrument(
    series_by_timeframe: dict[str, MarketDataSeries],
    contract: ContractSpec,
    r1_eur: Decimal,
    fx_rate: FXRate | None = None,
    thresholds: ClassificationThresholds | None = None,
    r2_residual_scenarios_eur: tuple[Decimal, ...] = R2_RESIDUAL_SCENARIOS_EUR,
) -> list[ProxyMetrics]:
    results: list[ProxyMetrics] = []
    for proxy in PROXIES:
        series = series_by_timeframe.get(proxy.timeframe)
        if series is None:
            results.append(
                ProxyMetrics(
                    instrument=contract.instrument_id,
                    timeframe=proxy.timeframe,
                    proxy_name=proxy.name,
                    observations=0,
                    valid_observations=0,
                    insufficient_data_observations=0,
                    external_data_required_observations=0,
                    minimum_size_compatible_count=0,
                    minimum_size_incompatible_count=0,
                    compatibility_percentage=None,
                    incompatibility_percentage=None,
                    median_risk_eur=None,
                    p25_risk_eur=None,
                    p75_risk_eur=None,
                    p90_risk_eur=None,
                    max_risk_eur=None,
                    r2_scenarios=(),
                    classification="INSUFFICIENT_DATA",
                    data_quality_error="missing_timeframe_data",
                )
            )
            continue

        try:
            observations = evaluate_proxy(series, proxy, contract, fx_rate)
        except DataQualityError as exc:
            results.append(
                ProxyMetrics(
                    instrument=contract.instrument_id,
                    timeframe=proxy.timeframe,
                    proxy_name=proxy.name,
                    observations=0,
                    valid_observations=0,
                    insufficient_data_observations=0,
                    external_data_required_observations=0,
                    minimum_size_compatible_count=0,
                    minimum_size_incompatible_count=0,
                    compatibility_percentage=None,
                    incompatibility_percentage=None,
                    median_risk_eur=None,
                    p25_risk_eur=None,
                    p75_risk_eur=None,
                    p90_risk_eur=None,
                    max_risk_eur=None,
                    r2_scenarios=(),
                    classification="INSUFFICIENT_DATA",
                    data_quality_error=f"{exc.reason}: {exc.detail}",
                )
            )
            continue

        results.append(
            aggregate(
                instrument=contract.instrument_id,
                timeframe=proxy.timeframe,
                proxy_name=proxy.name,
                observations=observations,
                r1_eur=r1_eur,
                r2_residual_scenarios_eur=r2_residual_scenarios_eur,
                thresholds=thresholds,
            )
        )
    return results
