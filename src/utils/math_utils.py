"""Mathematical helpers for the SNS-S-S simulation."""

from __future__ import annotations


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp ``value`` between ``min_value`` and ``max_value``.

    Parameters
    ----------
    value: float
        Input value to clamp.
    min_value: float
        Lower bound.
    max_value: float
        Upper bound.

    Returns
    -------
    float
        ``value`` limited to the provided bounds.
    """

    return max(min_value, min(value, max_value))
