"""Analytic resonant-response backend for rapid local benchmarking."""

from __future__ import annotations

import math
from typing import Dict

from .backend_base import BackendBase


class AnalyticResonantBackend(BackendBase):
    """Simple physically-plausible resonant scatterer model.

    Geometry parameters:
    - r_mm: effective resonator radius [mm]
    - h_mm: effective resonator height [mm]
    """

    def simulate(self, params: Dict[str, float], f0: float) -> Dict[str, object]:
        r_mm = float(params["r_mm"])
        h_mm = float(params["h_mm"])

        # Map geometry -> effective resonance and loaded Q.
        fr = 8.0e9 + (r_mm - 1.0) * 1.0e9 + (h_mm - 2.0) * 0.8e9
        q = max(10.0, 35.0 + (h_mm - 2.0) * 8.0 - (r_mm - 1.0) * 5.0)

        x = 2.0 * q * (f0 - fr) / fr
        phase_rad = 2.0 * math.atan(x)
        phase_deg = (math.degrees(phase_rad) + 360.0) % 360.0

        # Lorentzian-like amplitude response with mild geometric loss factor.
        amp = 1.0 / math.sqrt(1.0 + x * x)
        amp *= max(0.05, 1.0 - 0.08 * abs(r_mm - 1.0) - 0.04 * abs(h_mm - 2.0))
        amp = max(0.0, min(1.0, amp))

        return {
            "phase_deg": phase_deg,
            "amp": amp,
            "meta": {"fr_hz": fr, "q": q, "x": x},
        }
