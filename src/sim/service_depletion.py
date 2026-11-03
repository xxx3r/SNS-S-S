"""Prospective development-only service/depletion semantics for QST-SYNTH-0001.

This module does not read campaign records or holdout data.  It applies the
Monthly-selected proportional service rule to an explicit, non-increasing
accessible-energy state on the existing thermal-shadow time grid.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .thermal_storage import ThermalShadowScenario, capacity_fraction_at_temperature

EPSILON_WH = 1e-12

@dataclass(frozen=True)
class ServiceStep:
    start_s: float
    end_s: float
    requested_host_Wh: float
    requested_heater_Wh: float
    service_fraction: float
    served_host_Wh: float
    served_heater_Wh: float
    remaining_accessible_Wh: float
    inaccessible_derating_Wh: float
    temperature_K: float
    conservation_residual_Wh: float

@dataclass(frozen=True)
class ServiceDepletionResult:
    initial_accessible_energy_Wh: float
    requested_host_energy_Wh: float
    requested_heater_energy_Wh: float
    served_host_energy_Wh: float
    served_heater_energy_Wh: float
    remaining_accessible_energy_Wh: float
    inaccessible_derating_energy_Wh: float
    cutoff_time_s: Optional[float]
    final_temperature_K: float
    minimum_temperature_K: float
    pcm_latent_energy_used_J: float
    pcm_latent_energy_remaining_J: float
    maximum_conservation_residual_Wh: float
    trace: tuple[ServiceStep, ...]

def _accessible_limit_Wh(scenario: ThermalShadowScenario, temperature_K: float) -> float:
    return (scenario.nominal_battery_Wh * scenario.discharge_efficiency
            * (1.0 - scenario.reserve_fraction)
            * capacity_fraction_at_temperature(scenario, temperature_K))

def _temperature_step(scenario: ThermalShadowScenario, temperature_K: float,
                      served_heater_power_W: float, dt_s: float,
                      pcm_remaining_J: float) -> tuple[float, float]:
    passive_heat_W = scenario.thermal_conductance_W_K * (
        scenario.environment_temperature_K - temperature_K)
    net_heat_J = (passive_heat_W + served_heater_power_W) * dt_s
    unconstrained = temperature_K + net_heat_J / scenario.thermal_capacity_J_K
    crossing = (net_heat_J < 0 and temperature_K >= scenario.pcm_transition_temperature_K
                and unconstrained < scenario.pcm_transition_temperature_K)
    held = (net_heat_J < 0 and abs(temperature_K - scenario.pcm_transition_temperature_K) < 1e-12
            and pcm_remaining_J > 0)
    if crossing and pcm_remaining_J > 0:
        sensible = ((scenario.pcm_transition_temperature_K - temperature_K)
                    * scenario.thermal_capacity_J_K)
        residual = net_heat_J - sensible
        latent = min(pcm_remaining_J, -residual)
        return (scenario.pcm_transition_temperature_K
                + (residual + latent) / scenario.thermal_capacity_J_K,
                pcm_remaining_J - latent)
    if held:
        latent = min(pcm_remaining_J, -net_heat_J)
        return (temperature_K + (net_heat_J + latent) / scenario.thermal_capacity_J_K,
                pcm_remaining_J - latent)
    return unconstrained, pcm_remaining_J

def simulate_service_depletion(
    scenario: ThermalShadowScenario,
    *,
    initial_accessible_energy_Wh: Optional[float] = None,
) -> ServiceDepletionResult:
    """Apply fixed proportional service without optimization or holdout access.

    ``initial_accessible_energy_Wh`` is a development-fixture override.  It may
    reduce, but never increase, the model-derived accessible energy; zero is
    therefore an explicit analytic control rather than an invalid zero-capacity
    battery scenario.
    """
    scenario.validate()
    physical_initial_Wh = _accessible_limit_Wh(scenario, scenario.initial_temperature_K)
    if initial_accessible_energy_Wh is None:
        initial_Wh = physical_initial_Wh
    else:
        if not 0.0 <= initial_accessible_energy_Wh <= physical_initial_Wh + EPSILON_WH:
            raise ValueError("initial_accessible_energy_Wh must be within the model-derived limit")
        initial_Wh = min(initial_accessible_energy_Wh, physical_initial_Wh)

    duration_s = scenario.eclipse_duration_h * 3600.0
    temperature_K = minimum_temperature_K = scenario.initial_temperature_K
    pcm_remaining_J = pcm_initial_J = scenario.pcm_mass_kg * scenario.pcm_latent_heat_J_kg
    remaining_Wh = initial_Wh
    inaccessible_Wh = 0.0
    requested_host_Wh = requested_heater_Wh = 0.0
    served_host_Wh = served_heater_Wh = 0.0
    cutoff_time_s: Optional[float] = None
    elapsed_s = 0.0
    trace: list[ServiceStep] = []

    def apply_derating(temp_K: float) -> None:
        nonlocal remaining_Wh, inaccessible_Wh
        allowed_total = min(initial_Wh, _accessible_limit_Wh(scenario, temp_K))
        allowed_remaining = max(0.0, allowed_total - served_host_Wh - served_heater_Wh)
        if allowed_remaining < remaining_Wh:
            inaccessible_Wh += remaining_Wh - allowed_remaining
            remaining_Wh = allowed_remaining

    while elapsed_s < duration_s - EPSILON_WH:
        apply_derating(temperature_K)
        dt_s = min(scenario.time_step_s, duration_s - elapsed_s)
        heater_requested_W = (scenario.heater_power_W
                              if temperature_K < scenario.heater_threshold_K else 0.0)
        host_request_Wh = scenario.base_load_W * dt_s / 3600.0
        heater_request_Wh = heater_requested_W * dt_s / 3600.0
        total_request_Wh = host_request_Wh + heater_request_Wh
        requested_host_Wh += host_request_Wh
        requested_heater_Wh += heater_request_Wh
        fraction = (min(1.0, remaining_Wh / total_request_Wh)
                    if total_request_Wh > EPSILON_WH else 1.0)
        host_served = host_request_Wh * fraction
        heater_served = heater_request_Wh * fraction
        served_host_Wh += host_served
        served_heater_Wh += heater_served
        remaining_Wh = max(0.0, remaining_Wh - host_served - heater_served)
        if fraction < 1.0 and cutoff_time_s is None:
            cutoff_time_s = elapsed_s + dt_s * fraction

        served_heater_W = heater_served * 3600.0 / dt_s
        temperature_K, pcm_remaining_J = _temperature_step(
            scenario, temperature_K, served_heater_W, dt_s, pcm_remaining_J)
        minimum_temperature_K = min(minimum_temperature_K, temperature_K)
        apply_derating(temperature_K)
        elapsed_s += dt_s
        residual = (initial_Wh - served_host_Wh - served_heater_Wh
                    - remaining_Wh - inaccessible_Wh)
        trace.append(ServiceStep(
            start_s=elapsed_s-dt_s, end_s=elapsed_s,
            requested_host_Wh=host_request_Wh, requested_heater_Wh=heater_request_Wh,
            service_fraction=fraction, served_host_Wh=host_served,
            served_heater_Wh=heater_served, remaining_accessible_Wh=remaining_Wh,
            inaccessible_derating_Wh=inaccessible_Wh, temperature_K=temperature_K,
            conservation_residual_Wh=residual))

    final_residual = (initial_Wh - served_host_Wh - served_heater_Wh
                      - remaining_Wh - inaccessible_Wh)
    max_residual = max([abs(item.conservation_residual_Wh) for item in trace]
                       + [abs(final_residual)])
    return ServiceDepletionResult(
        initial_accessible_energy_Wh=initial_Wh,
        requested_host_energy_Wh=requested_host_Wh,
        requested_heater_energy_Wh=requested_heater_Wh,
        served_host_energy_Wh=served_host_Wh,
        served_heater_energy_Wh=served_heater_Wh,
        remaining_accessible_energy_Wh=remaining_Wh,
        inaccessible_derating_energy_Wh=inaccessible_Wh,
        cutoff_time_s=cutoff_time_s,
        final_temperature_K=temperature_K,
        minimum_temperature_K=minimum_temperature_K,
        pcm_latent_energy_used_J=pcm_initial_J-pcm_remaining_J,
        pcm_latent_energy_remaining_J=pcm_remaining_J,
        maximum_conservation_residual_Wh=max_residual,
        trace=tuple(trace))
