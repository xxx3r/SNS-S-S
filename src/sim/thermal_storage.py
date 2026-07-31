"""Minimal coupled electrical/thermal shadow-survival model for SNS nodes.

This is a first-order lumped model, not a qualification model. It couples battery
capacity derating, passive heat leak, thermostatic heater demand, eclipse duration,
and an optional phase-change-material (PCM) latent-heat buffer.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ThermalShadowScenario:
    eclipse_duration_h: float
    time_step_s: float
    initial_temperature_K: float
    environment_temperature_K: float
    thermal_capacity_J_K: float
    thermal_conductance_W_K: float
    heater_threshold_K: float
    heater_power_W: float
    base_load_W: float
    nominal_battery_Wh: float
    discharge_efficiency: float = 0.90
    reserve_fraction: float = 0.20
    derating_reference_K: float = 293.15
    derating_floor_K: float = 243.15
    minimum_capacity_fraction: float = 0.50
    minimum_operating_temperature_K: float = 233.15
    pcm_mass_kg: float = 0.0
    pcm_latent_heat_J_kg: float = 0.0
    pcm_transition_temperature_K: float = 273.15

    def validate(self) -> None:
        positive = (
            "eclipse_duration_h",
            "time_step_s",
            "thermal_capacity_J_K",
            "nominal_battery_Wh",
            "discharge_efficiency",
        )
        for name in positive:
            if getattr(self, name) <= 0.0:
                raise ValueError(f"{name} must be positive")
        if self.thermal_conductance_W_K < 0.0:
            raise ValueError("thermal_conductance_W_K must be non-negative")
        if self.heater_power_W < 0.0 or self.base_load_W < 0.0:
            raise ValueError("electrical loads must be non-negative")
        if not 0.0 < self.discharge_efficiency <= 1.0:
            raise ValueError("discharge_efficiency must be in (0, 1]")
        if not 0.0 <= self.reserve_fraction < 1.0:
            raise ValueError("reserve_fraction must be in [0, 1)")
        if not 0.0 < self.minimum_capacity_fraction <= 1.0:
            raise ValueError("minimum_capacity_fraction must be in (0, 1]")
        if self.derating_floor_K >= self.derating_reference_K:
            raise ValueError("derating_floor_K must be below derating_reference_K")
        if self.pcm_mass_kg < 0.0 or self.pcm_latent_heat_J_kg < 0.0:
            raise ValueError("PCM inputs must be non-negative")


@dataclass(frozen=True)
class ThermalShadowResult:
    final_temperature_K: float
    minimum_temperature_K: float
    consumed_energy_Wh: float
    heater_energy_Wh: float
    derated_available_energy_Wh: float
    electrical_margin_Wh: float
    pcm_latent_energy_used_J: float
    pcm_latent_energy_remaining_J: float
    temperature_status: str
    electrical_status: str
    status: str


def capacity_fraction_at_temperature(scenario: ThermalShadowScenario, temperature_K: float) -> float:
    """Piecewise-linear capacity proxy between reference and floor temperature."""

    if temperature_K >= scenario.derating_reference_K:
        return 1.0
    if temperature_K <= scenario.derating_floor_K:
        return scenario.minimum_capacity_fraction
    span = scenario.derating_reference_K - scenario.derating_floor_K
    position = (temperature_K - scenario.derating_floor_K) / span
    return scenario.minimum_capacity_fraction + position * (1.0 - scenario.minimum_capacity_fraction)


def simulate_thermal_shadow(scenario: ThermalShadowScenario) -> ThermalShadowResult:
    """Integrate one eclipse and return coupled thermal/electrical PASS/FAIL metrics."""

    scenario.validate()
    duration_s = scenario.eclipse_duration_h * 3600.0
    temperature_K = scenario.initial_temperature_K
    minimum_temperature_K = temperature_K
    consumed_energy_Wh = 0.0
    heater_energy_Wh = 0.0
    pcm_remaining_J = scenario.pcm_mass_kg * scenario.pcm_latent_heat_J_kg
    pcm_initial_J = pcm_remaining_J
    elapsed_s = 0.0

    while elapsed_s < duration_s - 1e-12:
        dt_s = min(scenario.time_step_s, duration_s - elapsed_s)
        heater_on = temperature_K < scenario.heater_threshold_K
        heater_power_W = scenario.heater_power_W if heater_on else 0.0

        consumed_energy_Wh += (scenario.base_load_W + heater_power_W) * dt_s / 3600.0
        heater_energy_Wh += heater_power_W * dt_s / 3600.0

        passive_heat_W = scenario.thermal_conductance_W_K * (
            scenario.environment_temperature_K - temperature_K
        )
        net_heat_J = (passive_heat_W + heater_power_W) * dt_s
        unconstrained_temperature_K = temperature_K + net_heat_J / scenario.thermal_capacity_J_K

        crossing_pcm_from_above = (
            net_heat_J < 0.0
            and temperature_K >= scenario.pcm_transition_temperature_K
            and unconstrained_temperature_K < scenario.pcm_transition_temperature_K
        )
        held_at_pcm = (
            net_heat_J < 0.0
            and abs(temperature_K - scenario.pcm_transition_temperature_K) < 1e-12
            and pcm_remaining_J > 0.0
        )

        if crossing_pcm_from_above and pcm_remaining_J > 0.0:
            sensible_to_transition_J = (
                scenario.pcm_transition_temperature_K - temperature_K
            ) * scenario.thermal_capacity_J_K
            residual_cooling_J = net_heat_J - sensible_to_transition_J
            latent_used_J = min(pcm_remaining_J, -residual_cooling_J)
            pcm_remaining_J -= latent_used_J
            residual_cooling_J += latent_used_J
            temperature_K = scenario.pcm_transition_temperature_K + (
                residual_cooling_J / scenario.thermal_capacity_J_K
            )
        elif held_at_pcm:
            latent_used_J = min(pcm_remaining_J, -net_heat_J)
            pcm_remaining_J -= latent_used_J
            residual_cooling_J = net_heat_J + latent_used_J
            temperature_K += residual_cooling_J / scenario.thermal_capacity_J_K
        else:
            temperature_K = unconstrained_temperature_K

        minimum_temperature_K = min(minimum_temperature_K, temperature_K)
        elapsed_s += dt_s

    capacity_fraction = capacity_fraction_at_temperature(scenario, minimum_temperature_K)
    available_Wh = (
        scenario.nominal_battery_Wh
        * capacity_fraction
        * scenario.discharge_efficiency
        * (1.0 - scenario.reserve_fraction)
    )
    electrical_margin_Wh = available_Wh - consumed_energy_Wh
    temperature_status = (
        "PASS" if minimum_temperature_K >= scenario.minimum_operating_temperature_K else "FAIL"
    )
    electrical_status = "PASS" if electrical_margin_Wh >= -1e-12 else "FAIL"
    status = "PASS" if temperature_status == electrical_status == "PASS" else "FAIL"

    return ThermalShadowResult(
        final_temperature_K=temperature_K,
        minimum_temperature_K=minimum_temperature_K,
        consumed_energy_Wh=consumed_energy_Wh,
        heater_energy_Wh=heater_energy_Wh,
        derated_available_energy_Wh=available_Wh,
        electrical_margin_Wh=electrical_margin_Wh,
        pcm_latent_energy_used_J=pcm_initial_J - pcm_remaining_J,
        pcm_latent_energy_remaining_J=pcm_remaining_J,
        temperature_status=temperature_status,
        electrical_status=electrical_status,
        status=status,
    )


def scenario_with_result(scenario: ThermalShadowScenario) -> dict[str, float | str]:
    """Return a flat, artifact-friendly record for one scenario."""

    return {**asdict(scenario), **asdict(simulate_thermal_shadow(scenario))}
