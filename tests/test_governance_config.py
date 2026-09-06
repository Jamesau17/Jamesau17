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


def test_r4_circuit_breaker_threshold_is_locked_at_150_eur() -> None:
    r4 = load_yaml(RISK_RULES_PATH)["risk_rules"]["R4_circuit_breaker"]
    threshold = r4["threshold_drawdown_from_hwm"]
    assert threshold["value"] == 150
    assert threshold["currency"] == "EUR"
    assert threshold["status"] == "LOCKED"


def test_r4_blocks_new_entries_and_scaling_without_automatic_liquidation() -> None:
    r4 = load_yaml(RISK_RULES_PATH)["risk_rules"]["R4_circuit_breaker"]
    actions = r4["trigger_actions"]["value"]
    assert any("block all new entries" in action for action in actions)
    assert any("scaling" in action for action in actions)
    assert any("reanalysis" in action for action in actions)
    assert r4["automatic_liquidation_on_threshold"]["value"] is False


def test_r4_strategic_specification_is_not_external_data_required() -> None:
    status_doc = load_yaml(SYSTEM_STATUS_PATH)["components"]["r4_circuit_breaker"]
    assert status_doc["status"] != "EXTERNAL_DATA_REQUIRED"
    assert status_doc["status"] == "LOCKED"

    constitution_text = (REPO_ROOT / "CONSTITUTION.md").read_text(encoding="utf-8")
    r4_section = constitution_text.split("## 2. Risk Rules")[1].split("## 3. Economic Objective")[0]
    assert "EXTERNAL_DATA_REQUIRED" not in r4_section


def test_economic_gate_minimum_is_200_eur_and_4r() -> None:
    minimum = load_yaml(RISK_RULES_PATH)["economic_gate"]["minimum"]
    assert minimum["net_potential"]["value"] == 200
    assert minimum["net_potential"]["currency"] == "EUR"
    assert minimum["net_r_multiple"]["value"] == 4
    assert minimum["net_r_multiple"]["unit"] == "R"


def test_economic_gate_preferred_is_300_eur_and_6r() -> None:
    preferred = load_yaml(RISK_RULES_PATH)["economic_gate"]["preferred"]
    assert preferred["net_potential"]["value"] == 300
    assert preferred["net_potential"]["currency"] == "EUR"
    assert preferred["net_r_multiple"]["value"] == 6
    assert preferred["net_r_multiple"]["unit"] == "R"


def test_economic_gate_strategic_specification_is_not_external_data_required() -> None:
    status_doc = load_yaml(SYSTEM_STATUS_PATH)["components"]["economic_gate"]
    assert status_doc["status"] != "EXTERNAL_DATA_REQUIRED"
    assert status_doc["status"] == "LOCKED"


def test_r_max_dependencies_not_populated_with_guessed_numbers() -> None:
    dependencies = load_yaml(RISK_RULES_PATH)["r_max"]["dependencies"]
    for name in (
        "cluster_correlation_constraints",
        "contractual_instrument_constraints",
        "minimum_trade_size",
        "margin_constraints",
        "execution_constraints",
    ):
        dep = dependencies[name]
        assert dep["value"] is None
        assert dep["status"] in {"TO_CALIBRATE", "EXTERNAL_DATA_REQUIRED"}


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


def test_python_package_initializers_are_correctly_named() -> None:
    package_dirs = [
        REPO_ROOT / "src",
        REPO_ROOT / "src" / "domain",
        REPO_ROOT / "src" / "risk",
        REPO_ROOT / "src" / "data",
        REPO_ROOT / "src" / "structure",
        REPO_ROOT / "src" / "events",
        REPO_ROOT / "src" / "journal",
        REPO_ROOT / "tests",
    ]
    for package_dir in package_dirs:
        assert (package_dir / "__init__.py").is_file(), f"missing __init__.py in {package_dir}"
        assert not (package_dir / "init.py").exists(), f"found invalid init.py in {package_dir}"
