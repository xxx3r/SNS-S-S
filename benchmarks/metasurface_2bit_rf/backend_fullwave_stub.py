"""Full-wave backend stub with explicit TODO integration hooks."""

from __future__ import annotations

from typing import Dict

from .backend_base import BackendBase


class FullwaveStubBackend(BackendBase):
    """Placeholder for meep/openEMS/RCWA integration."""

    def simulate(self, params: Dict[str, float], f0: float) -> Dict[str, object]:
        raise RuntimeError(
            "Full-wave backend is a stub. TODO: wire meep/openEMS/RCWA in this class "
            "and return {phase_deg, amp, meta}."
        )
