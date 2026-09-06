#!/usr/bin/env python3
"""Run C0-SCREEN against real inputs.

This script performs no calculation on its own — it only wires real CSV
market data, a real contract-specification JSON file, and an optional FX
rate JSON file into src.screening.c0_screen.

If required real inputs are not supplied, it reports
EMPIRICAL_RUN_STATUS: BLOCKED_EXTERNAL_DATA rather than fabricating a run.
Synthetic/test fixtures must never be passed here to produce a result that
looks like a real screen.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.csv_loader import load_ohlcv_csv  # noqa: E402
from src.risk.contract_specs import ContractSpec  # noqa: E402
from src.risk.fx import FXRate  # noqa: E402
from src.screening.c0_screen import load_r1_eur, screen_instrument  # noqa: E402
from src.screening.report import build_report, report_to_dict  # noqa: E402


def _load_contract_spec(path: Path) -> ContractSpec:
    raw = json.loads(path.read_text(encoding="utf-8"))
    decimal_fields = {
        "contract_size",
        "minimum_lot",
        "lot_increment",
        "price_tick_size",
        "tick_value",
        "leverage",
        "spread",
        "commission",
        "swap",
    }
    kwargs = dict(raw)
    for field_name in decimal_fields:
        if kwargs.get(field_name) is not None:
            kwargs[field_name] = Decimal(str(kwargs[field_name]))
    if kwargs.get("source_timestamp"):
        kwargs["source_timestamp"] = datetime.fromisoformat(kwargs["source_timestamp"])
    return ContractSpec(**kwargs)


def _load_fx_rate(path: Path) -> FXRate:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return FXRate(
        pair=raw["pair"],
        source=raw["source"],
        timestamp=datetime.fromisoformat(raw["timestamp"]),
        rate=Decimal(str(raw["rate"])),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run C0-SCREEN on real market/contract data.")
    parser.add_argument("--h4-csv", type=Path, help="H4 OHLCV CSV file")
    parser.add_argument("--d1-csv", type=Path, help="D1 OHLCV CSV file")
    parser.add_argument("--contract-spec", type=Path, help="Contract specification JSON file")
    parser.add_argument("--fx-rate", type=Path, help="Optional FX rate JSON file")
    parser.add_argument("--source", default="unspecified", help="Market data source label")
    parser.add_argument("--output", type=Path, help="Write JSON report to this path")
    args = parser.parse_args()

    if args.h4_csv is None and args.d1_csv is None:
        print("EMPIRICAL_RUN_STATUS: BLOCKED_EXTERNAL_DATA")
        print("Reason: no real H4 or D1 OHLCV CSV supplied (--h4-csv / --d1-csv).")
        return 1
    if args.contract_spec is None:
        print("EMPIRICAL_RUN_STATUS: BLOCKED_EXTERNAL_DATA")
        print("Reason: no real contract specification supplied (--contract-spec).")
        return 1

    retrieval_timestamp = datetime.now(timezone.utc)
    series_by_timeframe = {}
    market_data_provenance = {}
    if args.h4_csv is not None:
        series = load_ohlcv_csv(args.h4_csv, source=args.source, retrieval_timestamp=retrieval_timestamp)
        series_by_timeframe["H4"] = series
        market_data_provenance["H4"] = series.provenance
    if args.d1_csv is not None:
        series = load_ohlcv_csv(args.d1_csv, source=args.source, retrieval_timestamp=retrieval_timestamp)
        series_by_timeframe["D1"] = series
        market_data_provenance["D1"] = series.provenance

    contract = _load_contract_spec(args.contract_spec)
    fx_rate = _load_fx_rate(args.fx_rate) if args.fx_rate else None
    r1_eur = load_r1_eur()

    proxy_metrics = screen_instrument(series_by_timeframe, contract, r1_eur, fx_rate=fx_rate)
    report = build_report(
        market_data_provenance=market_data_provenance,
        contract=contract,
        r1_eur=r1_eur,
        proxy_metrics=proxy_metrics,
        fx_rate=fx_rate,
        generated_at=retrieval_timestamp,
    )

    output_json = json.dumps(report_to_dict(report), indent=2)
    if args.output:
        args.output.write_text(output_json, encoding="utf-8")
        print(f"EMPIRICAL_RUN_STATUS: COMPLETED — report written to {args.output}")
    else:
        print("EMPIRICAL_RUN_STATUS: COMPLETED")
        print(output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
