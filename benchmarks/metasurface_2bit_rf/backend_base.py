"""Backend interface for metasurface unit-cell simulation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict


class BackendBase(ABC):
    """Abstract simulation backend contract."""

    @abstractmethod
    def simulate(self, params: Dict[str, float], f0: float) -> Dict[str, object]:
        """Return phase_deg, amp, and metadata diagnostics."""
        raise NotImplementedError
