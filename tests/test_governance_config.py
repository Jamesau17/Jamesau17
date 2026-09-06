"""Bootstrap/governance tests.

These verify the governance mechanism itself (config parses, unknown
critical parameters are never silently defaulted, status vocabulary is
valid) — not any trading behavior.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.domain.config_loader import GovernanceError, load_yaml
from src.domain.status import VALID_STATUSES

REPO_ROOT = Path(__file__).resolve().parents[1]
RISK_RULES_PATH = REPO_ROOT / "config" / "risk_rules.yaml"
SYSTEM_STATUS_PATH = REPO_ROOT / "config" / "system_status.yaml"


def test_risk_rules_yaml_parses() -> None:
    data = load_yaml(RISK_RULES_PATH)
    assert "account" in data
    assert "risk_rules" in data


def test_system_status_yaml_parses() -> None:
    data = load_yaml(SYSTEM_STATUS_PATH)
    assert "components" in data


def test_locked_account_values_are_present_and_not_null() -> None:
    data = load_yaml(RISK_RULES_PATH)
    account = data["account"]
    assert account["reference_capital"]["value"] == 1000
    assert account["reference_capital"]["status"] == "LOCKED"
    assert account["max_simultaneous_positions"]["value"] == 2
    assert account["max_simultaneous_positions"]["status"] == "LOCKED"


def test_locked_risk_rule_values_match_constitution() -> None:
    rules = load_yaml(RISK_RULES_PATH)["risk_rules"]
    assert rules["R1_max_risk_per_position"]["value"] == 50
    assert rules["R2_max_aggregate_open_risk"]["value"] == 100
    assert rules["R3_max_realized_loss_rolling_window"]["value"] == 100
    assert rules["R3_max_realized_loss_rolling_window"]["window_days"] == 14


def test_r4_circuit_breaker_is_unresolved_not_guessed() -> None:
    r4 = load_yaml(RISK_RULES_PATH)["risk_rules"]["R4_circuit_breaker"]
    assert r4["value"] is None
    assert r4["status"] == "NON_OPERATIONAL"


def test_economic_gate_implementation_is_unresolved_not_guessed() -> None:
    gate = load_yaml(RISK_RULES_PATH)["economic_gate"]["implementation"]
    assert gate["value"] is None
    assert gate["status"] == "NON_OPERATIONAL"


def test_vantage_specification_is_unresolved_not_guessed() -> None:
    vantage = load_yaml(RISK_RULES_PATH)["vantage_broker_specification"]
    assert vantage["value"] is None
    assert vantage["status"] == "EXTERNAL_DATA_REQUIRED"


def test_every_status_in_risk_rules_is_valid_vocabulary() -> None:
    def walk(node: object) -> None:
        if isinstance(node, dict):
            if "status" in node:
                assert node["status"] in VALID_STATUSES
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(load_yaml(RISK_RULES_PATH))
    walk(load_yaml(SYSTEM_STATUS_PATH))


def test_null_value_without_status_is_rejected(tmp_path: Path) -> None:
    bad_config = tmp_path / "bad.yaml"
    bad_config.write_text("param:\n  value: null\n", encoding="utf-8")
    with pytest.raises(GovernanceError):
        load_yaml(bad_config)


def test_null_value_with_invalid_status_is_rejected(tmp_path: Path) -> None:
    bad_config = tmp_path / "bad.yaml"
    bad_config.write_text("param:\n  value: null\n  status: MADE_UP\n", encoding="utf-8")
    with pytest.raises(GovernanceError):
        load_yaml(bad_config)


def test_system_status_components_have_valid_status() -> None:
    components = load_yaml(SYSTEM_STATUS_PATH)["components"]
    for name, component in components.items():
        assert component["status"] in VALID_STATUSES, f"{name} has invalid status"
