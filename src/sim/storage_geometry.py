"""Geometry-first storage calculations for Solar-Nano-Sphere concepts.

The model is intentionally small and explicit. It asks whether a spherical core can
contain enough battery energy to survive a prescribed shadow interval under a mixed
sleep/active duty profile. It does not model electrochemistry, thermal derating,
radiation degradation, or packaging beyond the supplied battery-volume fraction.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import asdict, dataclass
from typing import Iterable, Iterator, Mapping, Sequence


@dataclass(frozen=True)
class StorageAuditAssumptions:
    """Global assumptions shared by every point in the parameter sweep."""

    usable_fraction: float = 0.80
    discharge_efficiency: float = 0.90
    charge_efficiency: float = 0.90
    reserve_fraction: float = 0.20
    active_duty_cycle: float = 0.01
    battery_density_g_cm3: float = 2.0
    pv_charge_power_W: float = 27.0
    max_charge_c_rate: float = 1.0

    def validate(self) -> None:
        """Raise ``ValueError`` when an assumption is outside its physical domain."""

        for name in ("usable_fraction", "discharge_efficiency", "charge_efficiency"):
            value = getattr(self, name)
            if not 0.0 < value <= 1.0:
                raise ValueError(f"{name} must be in (0, 1], got {value}")
        if self.reserve_fraction < 0.0:
            raise ValueError("reserve_fraction must be non-negative")
        if not 0.0 <= self.active_duty_cycle <= 1.0:
            raise ValueError("active_duty_cycle must be in [0, 1]")
        for name in ("battery_density_g_cm3", "pv_charge_power_W", "max_charge_c_rate"):
            if getattr(self, name) <= 0.0:
                raise ValueError(f"{name} must be positive")


@dataclass(frozen=True)
class StorageAuditPoint:
    """One storage-geometry scenario from the Cartesian parameter sweep."""

    core_diameter_mm: float
    battery_volume_fraction: float
    battery_energy_density_Wh_L: float
    sleep_power_uW: float
    active_power_mW: float
    shadow_duration_h: float

    def validate(self) -> None:
        """Raise ``ValueError`` when a scenario input is invalid."""

        if self.core_diameter_mm <= 0.0:
            raise ValueError("core_diameter_mm must be positive")
        if not 0.0 < self.battery_volume_fraction <= 1.0:
            raise ValueError("battery_volume_fraction must be in (0, 1]")
        if self.battery_energy_density_Wh_L <= 0.0:
            raise ValueError("battery_energy_density_Wh_L must be positive")
        if self.sleep_power_uW < 0.0 or self.active_power_mW < 0.0:
            raise ValueError("power values must be non-negative")
        if self.shadow_duration_h <= 0.0:
            raise ValueError("shadow_duration_h must be positive")


DEFAULT_SWEEP: Mapping[str, Sequence[float]] = {
    "core_diameter_mm": (10.0, 20.0, 30.0),
    "battery_volume_fraction": (0.15, 0.30, 0.50),
    "battery_energy_density_Wh_L": (220.0, 450.0, 600.0, 1000.0),
    "sleep_power_uW": (10.0, 100.0, 1000.0),
    "active_power_mW": (1.0, 10.0, 100.0),
    "shadow_duration_h": (0.5, 2.0, 12.0, 72.0),
}


def sphere_volume_liters(diameter_mm: float) -> float:
    """Return the volume of a sphere in litres for a diameter in millimetres."""

    if diameter_mm <= 0.0:
        raise ValueError("diameter_mm must be positive")
    radius_mm = diameter_mm / 2.0
    volume_mm3 = (4.0 / 3.0) * math.pi * radius_mm**3
    return volume_mm3 / 1_000_000.0


def evaluate_storage_point(
    point: StorageAuditPoint,
    assumptions: StorageAuditAssumptions | None = None,
) -> dict[str, float | str]:
    """Evaluate one storage geometry and return transparent engineering metrics.

    ``required_storage_Wh`` includes discharge losses and the configured reserve.
    ``survival_duration_h`` is therefore a mission-qualified duration using the same
    reserve policy. ``pv_fill_time_s`` is an energy-only lower bound; the separate
    ``charge_limited_fill_time_s`` applies a configurable maximum C-rate.
    """

    assumptions = assumptions or StorageAuditAssumptions()
    assumptions.validate()
    point.validate()

    core_volume_L = sphere_volume_liters(point.core_diameter_mm)
    battery_volume_L = core_volume_L * point.battery_volume_fraction
    gross_battery_Wh = battery_volume_L * point.battery_energy_density_Wh_L
    usable_battery_Wh = gross_battery_Wh * assumptions.usable_fraction

    sleep_power_W = point.sleep_power_uW * 1e-6
    duty_averaged_active_power_W = point.active_power_mW * 1e-3 * assumptions.active_duty_cycle
    average_shadow_load_W = sleep_power_W + duty_averaged_active_power_W

    required_storage_Wh = (
        average_shadow_load_W
        * point.shadow_duration_h
        * (1.0 + assumptions.reserve_fraction)
        / assumptions.discharge_efficiency
    )
    storage_margin_Wh = usable_battery_Wh - required_storage_Wh

    if average_shadow_load_W == 0.0:
        survival_duration_h = math.inf
    else:
        survival_duration_h = (
            usable_battery_Wh
            * assumptions.discharge_efficiency
            / ((1.0 + assumptions.reserve_fraction) * average_shadow_load_W)
        )

    ideal_charge_power_W = assumptions.pv_charge_power_W * assumptions.charge_efficiency
    pv_fill_time_s = usable_battery_Wh / ideal_charge_power_W * 3600.0

    max_cell_charge_power_W = gross_battery_Wh * assumptions.max_charge_c_rate
    effective_charge_power_W = min(ideal_charge_power_W, max_cell_charge_power_W)
    charge_limited_fill_time_s = usable_battery_Wh / effective_charge_power_W * 3600.0

    battery_volume_cm3 = battery_volume_L * 1000.0
    battery_mass_estimate_g = battery_volume_cm3 * assumptions.battery_density_g_cm3

    status = "PASS" if storage_margin_Wh >= -1e-12 else "FAIL"

    return {
        **asdict(point),
        "core_volume_L": core_volume_L,
        "battery_volume_L": battery_volume_L,
        "gross_battery_Wh": gross_battery_Wh,
        "usable_battery_Wh": usable_battery_Wh,
        "average_shadow_load_mW": average_shadow_load_W * 1000.0,
        "survival_duration_h": survival_duration_h,
        "required_storage_Wh": required_storage_Wh,
        "storage_margin_Wh": storage_margin_Wh,
        "pv_fill_time_s": pv_fill_time_s,
        "charge_limited_fill_time_s": charge_limited_fill_time_s,
        "battery_mass_estimate_g": battery_mass_estimate_g,
        "status": status,
    }


def iter_storage_sweep(
    sweep: Mapping[str, Iterable[float]] | None = None,
    assumptions: StorageAuditAssumptions | None = None,
) -> Iterator[dict[str, float | str]]:
    """Yield every evaluated point in the Cartesian storage parameter sweep."""

    sweep = sweep or DEFAULT_SWEEP
    required_keys = tuple(DEFAULT_SWEEP)
    missing = [key for key in required_keys if key not in sweep]
    if missing:
        raise ValueError(f"Sweep is missing required keys: {', '.join(missing)}")

    value_lists = [tuple(float(value) for value in sweep[key]) for key in required_keys]
    if any(not values for values in value_lists):
        raise ValueError("Every sweep dimension must contain at least one value")

    for values in itertools.product(*value_lists):
        point = StorageAuditPoint(**dict(zip(required_keys, values)))
        yield evaluate_storage_point(point, assumptions)


def summarize_storage_sweep(rows: Sequence[Mapping[str, float | str]]) -> dict:
    """Return compact pass-rate and capacity summaries for audit output files."""

    if not rows:
        raise ValueError("rows must not be empty")

    pass_count = sum(row["status"] == "PASS" for row in rows)
    per_diameter: dict[str, dict[str, float | int]] = {}
    for diameter in sorted({float(row["core_diameter_mm"]) for row in rows}):
        subset = [row for row in rows if float(row["core_diameter_mm"]) == diameter]
        subset_pass = sum(row["status"] == "PASS" for row in subset)
        capacities = [float(row["usable_battery_Wh"]) for row in subset]
        per_diameter[f"{diameter:g}_mm"] = {
            "scenario_count": len(subset),
            "pass_count": subset_pass,
            "pass_rate": subset_pass / len(subset),
            "usable_battery_Wh_min": min(capacities),
            "usable_battery_Wh_max": max(capacities),
        }

    margins = [float(row["storage_margin_Wh"]) for row in rows]
    ideal_fill = [float(row["pv_fill_time_s"]) for row in rows]
    limited_fill = [float(row["charge_limited_fill_time_s"]) for row in rows]

    return {
        "scenario_count": len(rows),
        "pass_count": pass_count,
        "fail_count": len(rows) - pass_count,
        "pass_rate": pass_count / len(rows),
        "storage_margin_Wh_min": min(margins),
        "storage_margin_Wh_max": max(margins),
        "pv_fill_time_s_min": min(ideal_fill),
        "pv_fill_time_s_max": max(ideal_fill),
        "charge_limited_fill_time_s_min": min(limited_fill),
        "charge_limited_fill_time_s_max": max(limited_fill),
        "by_core_diameter": per_diameter,
    }
