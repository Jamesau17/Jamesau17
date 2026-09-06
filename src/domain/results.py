"""Shared result types for calculations that may be blocked by missing data."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.domain.status import Status


@dataclass(frozen=True)
class ExternalDataRequired:
    """Signals that a calculation cannot proceed without external data.

    Never a stand-in for zero or an estimate — callers must branch on this
    explicitly rather than treat it as a numeric result.
    """

    missing: tuple[str, ...] = field(default_factory=tuple)
    status: Status = Status.EXTERNAL_DATA_REQUIRED
