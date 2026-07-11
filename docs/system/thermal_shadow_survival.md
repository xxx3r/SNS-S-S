# Thermal-Derated Shadow Survival v0.1

## Engineering question

Can a small SNS node survive a two-hour eclipse once battery-temperature derating, thermostatic heater demand, passive cooling, and optional phase-change buffering are coupled in one inspectable model?

## Model

`src/sim/thermal_storage.py` uses a fixed-step lumped thermal state:

- passive heat flow: `G * (T_environment - T_node)`;
- heater power activates below a declared threshold;
- electrical consumption is base load plus heater demand;
- available battery energy is derated from the minimum temperature reached;
- PCM contributes a finite latent-energy reservoir at a declared transition temperature;
- thermal and electrical PASS/FAIL are reported separately.

The model is deliberately first-order. It does not yet include radiative view factors, internal component gradients, battery self-heating, temperature-dependent conductance, PCM sensible heat, hysteresis, aging, or electrochemical rate effects.

## Acceptance criteria for this slice

1. A declared two-hour case is reproducible from JSON.
2. Thermal and electrical status remain separate.
3. A 2 g PCM case preserves more temperature and uses less heater energy than the no-PCM case.
4. A deliberately undersized battery still fails electrically despite a larger PCM buffer.
5. Focused tests cover derating, PCM benefit, PCM limitation, and invalid inputs.

## Reproduce

```bash
python experiments/thermal_shadow_survival.py \
  --config configs/thermal_shadow_survival.json \
  --out outputs/qst_stor_0002

pytest -q tests/test_thermal_storage.py
```

## Interpretation boundary

A simulation PASS means only that this proxy's declared criteria passed. The parameter values are engineering placeholders for sensitivity work, not measured SNS hardware properties or space qualification evidence.

## Next measurement

Replace the placeholder thermal capacitance and conductance with geometry-derived ranges, then sweep eclipse duration, initial temperature, PCM mass, and duty cycle.
