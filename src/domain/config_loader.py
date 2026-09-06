"""Minimal YAML config loading with governance guarantees.

Guarantees enforced here (nothing else):
- A parameter whose value is null MUST carry a `status` key. Silent
  numerical defaults are never assigned to unknown/critical parameters.
- Loading never invents, estimates, or fills in a missing value.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.domain.status import VALID_STATUSES


class GovernanceError(ValueError):
    """Raised when a config file violates the null-must-have-status rule."""


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    _check_null_parameters_have_status(data, path)
    return data


def _check_null_parameters_have_status(node: Any, path: Path, trail: str = "") -> None:
    if isinstance(node, dict):
        if "value" in node and node["value"] is None:
            status = node.get("status")
            if status is None:
                raise GovernanceError(
                    f"{path}: parameter at '{trail}' has null value with no status metadata"
                )
            if status not in VALID_STATUSES:
                raise GovernanceError(
                    f"{path}: parameter at '{trail}' has invalid status '{status}'"
                )
        for key, value in node.items():
            _check_null_parameters_have_status(value, path, f"{trail}.{key}" if trail else key)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            _check_null_parameters_have_status(item, path, f"{trail}[{index}]")
