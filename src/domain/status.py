"""Status vocabulary shared across the project (see CONSTITUTION.md)."""

from __future__ import annotations

from enum import Enum


class Status(str, Enum):
    LOCKED = "LOCKED"
    TO_CALIBRATE = "TO_CALIBRATE"
    EXTERNAL_DATA_REQUIRED = "EXTERNAL_DATA_REQUIRED"
    MEASUREMENT_REQUIRED = "MEASUREMENT_REQUIRED"
    NON_OPERATIONAL = "NON_OPERATIONAL"
    PROVISIONAL = "PROVISIONAL"
    VALIDATED = "VALIDATED"


VALID_STATUSES = frozenset(status.value for status in Status)
