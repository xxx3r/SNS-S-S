"""Bounded synthetic beam-link loss abstraction for QST-META-0001.

This module is a data-link accounting model. It is not evidence of physical
power-beam performance, metasurface hardware readiness, or space qualification.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from math import cos, exp, isfinite, radians
from typing import Iterable


@dataclass(frozen=True)
class BeamLinkParameters:
    input_energy_Wh: float
    aperture_efficiency: float
    transmitter_conversion_efficiency: float
    receiver_coupling: float
    steering_exponent: float
    pointing_sigma_deg: float
    control_base_Wh: float
    control_per_degree_Wh: float
    minimum_useful_fraction: float

    def validate(self) -> None:
        values = asdict(self)
        if not all(isfinite(value) for value in values.values()):
            raise ValueError("beam-link parameters must be finite")
        for name in (
            "aperture_efficiency",
            "transmitter_conversion_efficiency",
            "receiver_coupling",
            "minimum_useful_fraction",
        ):
            if not 0.0 <= values[name] <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")
        if self.input_energy_Wh <= 0.0:
            raise ValueError("input_energy_Wh must be positive")
        if self.steering_exponent <= 0.0:
            raise ValueError("steering_exponent must be positive")
        if self.pointing_sigma_deg <= 0.0:
            raise ValueError("pointing_sigma_deg must be positive")
        if self.control_base_Wh < 0.0 or self.control_per_degree_Wh < 0.0:
            raise ValueError("control-energy terms must be non-negative")


SYNTHETIC_PARAMETERS = BeamLinkParameters(
    input_energy_Wh=1.0,
    aperture_efficiency=0.8,
    transmitter_conversion_efficiency=0.72,
    receiver_coupling=0.75,
    steering_exponent=2.0,
    pointing_sigma_deg=2.0,
    control_base_Wh=0.04,
    control_per_degree_Wh=0.0005,
    minimum_useful_fraction=0.25,
)

STEERING_ANGLES_DEG = (0.0, 20.0, 40.0, 60.0)
POINTING_ERRORS_DEG = (0.0, 1.0, 3.0)


def _rounded(value: float) -> float:
    return round(value, 12)


def evaluate_beam_link(
    parameters: BeamLinkParameters,
    *,
    steering_angle_deg: float,
    pointing_error_deg: float,
) -> dict[str, float | bool]:
    """Evaluate one deterministic point in the declared synthetic model."""

    parameters.validate()
    if not isfinite(steering_angle_deg) or not isfinite(pointing_error_deg):
        raise ValueError("angles must be finite")
    if not 0.0 <= steering_angle_deg <= 90.0:
        raise ValueError("steering_angle_deg must be in [0, 90]")
    if pointing_error_deg < 0.0:
        raise ValueError("pointing_error_deg must be non-negative")

    steering_cosine = max(cos(radians(steering_angle_deg)), 0.0)
    steering_penalty = (
        0.0
        if steering_angle_deg == 90.0
        else steering_cosine ** parameters.steering_exponent
    )
    pointing_penalty = exp(
        -0.5 * (pointing_error_deg / parameters.pointing_sigma_deg) ** 2
    )
    gross_delivered_energy_Wh = (
        parameters.input_energy_Wh
        * parameters.aperture_efficiency
        * parameters.transmitter_conversion_efficiency
        * parameters.receiver_coupling
        * steering_penalty
        * pointing_penalty
    )
    control_energy_Wh = (
        parameters.control_base_Wh
        + parameters.control_per_degree_Wh * abs(steering_angle_deg)
    )
    net_delivered_energy_Wh = gross_delivered_energy_Wh - control_energy_Wh
    net_delivered_fraction = net_delivered_energy_Wh / parameters.input_energy_Wh

    return {
        "steering_angle_deg": steering_angle_deg,
        "pointing_error_deg": pointing_error_deg,
        "steering_penalty": _rounded(steering_penalty),
        "pointing_penalty": _rounded(pointing_penalty),
        "gross_delivered_energy_Wh": _rounded(gross_delivered_energy_Wh),
        "control_energy_Wh": _rounded(control_energy_Wh),
        "net_delivered_energy_Wh": _rounded(net_delivered_energy_Wh),
        "net_delivered_fraction": _rounded(net_delivered_fraction),
        "useful_on_declared_synthetic_boundary": (
            net_delivered_fraction >= parameters.minimum_useful_fraction
        ),
    }


def build_synthetic_sweep(
    parameters: BeamLinkParameters = SYNTHETIC_PARAMETERS,
    *,
    steering_angles_deg: Iterable[float] = STEERING_ANGLES_DEG,
    pointing_errors_deg: Iterable[float] = POINTING_ERRORS_DEG,
) -> dict[str, object]:
    """Build the deterministic, bounded QST-META-0001 sweep artifact."""

    parameters.validate()
    angles = tuple(steering_angles_deg)
    errors = tuple(pointing_errors_deg)
    if not angles or not errors:
        raise ValueError("sweep axes must be non-empty")

    points = [
        evaluate_beam_link(
            parameters,
            steering_angle_deg=angle,
            pointing_error_deg=error,
        )
        for angle in angles
        for error in errors
    ]
    useful_count = sum(
        bool(point["useful_on_declared_synthetic_boundary"]) for point in points
    )
    erased_everywhere = useful_count == 0

    return {
        "schema": "sns.qst-meta-beam-link-sweep.v1",
        "quest_id": "QST-META-0001",
        "synthetic": True,
        "model": {
            "steering_penalty": "max(cos(steering_angle), 0) ** steering_exponent",
            "pointing_penalty": "exp(-0.5 * (pointing_error / pointing_sigma) ** 2)",
            "net_energy": "input * aperture * conversion * coupling * steering * pointing - control",
        },
        "parameters": asdict(parameters),
        "sweep": {
            "steering_angles_deg": list(angles),
            "pointing_errors_deg": list(errors),
            "points": points,
        },
        "summary": {
            "point_count": len(points),
            "useful_point_count": useful_count,
            "limited_point_count": len(points) - useful_count,
            "minimum_net_delivered_fraction": min(
                point["net_delivered_fraction"] for point in points
            ),
            "maximum_net_delivered_fraction": max(
                point["net_delivered_fraction"] for point in points
            ),
            "relay_losses_erase_modeled_benefit_on_declared_grid": erased_everywhere,
            "outcome": (
                "MODELED_BENEFIT_ERASED_ON_DECLARED_GRID"
                if erased_everywhere
                else "BOUNDED_BENEFIT_WITH_LOSS_LIMITS"
            ),
        },
        "limitations": [
            "All parameters and sweep points are synthetic and uncalibrated.",
            "The usefulness threshold is a declared model boundary, not a hardware requirement.",
            "The abstraction excludes diffraction, range, thermal limits, materials, dynamics, and receiver architecture.",
            "Negative net energy is retained rather than clipped so control-cost failures remain visible.",
        ],
        "nonclaims": [
            "No physical power-beam performance is established.",
            "No metasurface architecture or receiver technology is selected.",
            "No hardware readiness or space qualification is implied.",
        ],
    }


def falsifier_fixture() -> dict[str, object]:
    """Return a conservative synthetic fixture useful for testing the falsifier."""

    return build_synthetic_sweep(
        replace(
            SYNTHETIC_PARAMETERS,
            control_base_Wh=0.5,
            minimum_useful_fraction=0.5,
        )
    )
