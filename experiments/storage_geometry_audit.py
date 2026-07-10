"""Run QST-STOR-0001 and write reproducible storage geometry audit artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.sim.storage_geometry import (  # noqa: E402
    DEFAULT_SWEEP,
    StorageAuditAssumptions,
    iter_storage_sweep,
    summarize_storage_sweep,
)


def load_audit_config(
    path: Path,
) -> tuple[dict[str, Sequence[float]], StorageAuditAssumptions, tuple[float, ...]]:
    """Load sweep dimensions, assumptions, and duty-cycle stress cases."""

    data = json.loads(path.read_text())
    sweep = data.get("sweep", DEFAULT_SWEEP)
    assumptions = StorageAuditAssumptions(**data.get("assumptions", {}))
    sensitivity = tuple(
        float(value)
        for value in data.get(
            "sensitivity_active_duty_cycles",
            (0.0, assumptions.active_duty_cycle, 0.05, 0.10, 1.0),
        )
    )
    return sweep, assumptions, sensitivity


def _write_csv(rows: Sequence[Mapping[str, float | str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(summary: Mapping, assumptions: StorageAuditAssumptions, path: Path) -> None:
    by_diameter = summary["by_core_diameter"]
    lines = [
        "# QST-STOR-0001 Storage Geometry Audit",
        "",
        f"- Scenarios: **{summary['scenario_count']}**",
        f"- PASS: **{summary['pass_count']}**",
        f"- FAIL: **{summary['fail_count']}**",
        f"- Overall pass rate: **{summary['pass_rate']:.1%}**",
        "",
        "## Assumptions",
        "",
        f"- Usable battery fraction: {assumptions.usable_fraction:.0%}",
        f"- Discharge efficiency: {assumptions.discharge_efficiency:.0%}",
        f"- Reserve fraction: {assumptions.reserve_fraction:.0%}",
        f"- Shadow active duty cycle: {assumptions.active_duty_cycle:.1%}",
        f"- Battery bulk density estimate: {assumptions.battery_density_g_cm3:g} g/cm³",
        f"- Conservative PV charging source: {assumptions.pv_charge_power_W:g} W",
        f"- Maximum battery charge rate: {assumptions.max_charge_c_rate:g}C",
        "",
        "## Results by core diameter",
        "",
        "| Core | Scenarios | PASS | Pass rate | Usable capacity range (Wh) |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for label, values in by_diameter.items():
        lines.append(
            f"| {label.replace('_', ' ')} | {values['scenario_count']} | {values['pass_count']} | "
            f"{values['pass_rate']:.1%} | {values['usable_battery_Wh_min']:.6f}–"
            f"{values['usable_battery_Wh_max']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Active-duty-cycle stress test",
            "",
            "| Active duty in shadow | Overall pass rate | 10 mm | 20 mm | 30 mm |",
            "| ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for stress in summary["active_duty_cycle_sensitivity"]:
        rates = stress["by_core_diameter"]

        def rate(label: str) -> str:
            value = rates.get(label, {}).get("pass_rate")
            return "n/a" if value is None else f"{value:.1%}"

        lines.append(
            f"| {stress['active_duty_cycle']:.1%} | {stress['pass_rate']:.1%} | "
            f"{rate('10_mm')} | {rate('20_mm')} | {rate('30_mm')} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "`pv_fill_time_s` is an ideal energy-only lower bound. It deliberately shows the geometry mismatch, "
            "but it is not a safe battery charging schedule. `charge_limited_fill_time_s` applies the configured "
            "C-rate and is the more realistic minimum charging time.",
            "",
            "PASS means the usable battery can cover the selected shadow duration after discharge losses and the "
            "reserve policy. Thermal, radiation, aging, wiring, and converter derating are not yet included, so PASS "
            "is a geometry gate rather than flight qualification.",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def run_storage_geometry_audit(config_path: Path, output_dir: Path) -> tuple[list[dict], dict]:
    """Execute the configured sweep and write CSV, JSON, and Markdown artifacts."""

    sweep, assumptions, sensitivity_duties = load_audit_config(config_path)
    rows = list(iter_storage_sweep(sweep, assumptions))
    summary = summarize_storage_sweep(rows)

    sensitivity_rows = []
    for duty_cycle in sensitivity_duties:
        stress_assumptions = StorageAuditAssumptions(
            **{**asdict(assumptions), "active_duty_cycle": duty_cycle}
        )
        stress_summary = summarize_storage_sweep(
            list(iter_storage_sweep(sweep, stress_assumptions))
        )
        sensitivity_rows.append(
            {
                "active_duty_cycle": duty_cycle,
                "pass_count": stress_summary["pass_count"],
                "fail_count": stress_summary["fail_count"],
                "pass_rate": stress_summary["pass_rate"],
                "by_core_diameter": stress_summary["by_core_diameter"],
            }
        )
    summary["active_duty_cycle_sensitivity"] = sensitivity_rows
    summary["assumptions"] = asdict(assumptions)
    summary["sweep"] = {key: list(values) for key, values in sweep.items()}

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(rows, output_dir / "storage_geometry_sweep.csv")
    flat_sensitivity = [
        {
            "active_duty_cycle": row["active_duty_cycle"],
            "pass_count": row["pass_count"],
            "fail_count": row["fail_count"],
            "pass_rate": row["pass_rate"],
            "pass_rate_10_mm": row["by_core_diameter"].get("10_mm", {}).get("pass_rate", ""),
            "pass_rate_20_mm": row["by_core_diameter"].get("20_mm", {}).get("pass_rate", ""),
            "pass_rate_30_mm": row["by_core_diameter"].get("30_mm", {}).get("pass_rate", ""),
        }
        for row in sensitivity_rows
    ]
    _write_csv(flat_sensitivity, output_dir / "active_duty_cycle_sensitivity.csv")
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    _write_markdown(summary, assumptions, output_dir / "README.md")
    return rows, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "storage_geometry_audit.json",
        help="JSON file containing sweep dimensions and assumptions.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "outputs" / "qst_stor_0001",
        help="Directory for audit artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows, summary = run_storage_geometry_audit(args.config, args.out)
    print(f"Evaluated {len(rows)} storage geometries")
    print(f"PASS {summary['pass_count']} / FAIL {summary['fail_count']}")
    print(f"Wrote {args.out / 'storage_geometry_sweep.csv'}")
    print(f"Wrote {args.out / 'summary.json'}")
    print(f"Wrote {args.out / 'active_duty_cycle_sensitivity.csv'}")
    print(f"Wrote {args.out / 'README.md'}")


if __name__ == "__main__":
    main()
