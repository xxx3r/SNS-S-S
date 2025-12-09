# AGENTS.md — SNS-S-S

This file defines how AI coding agents should collaborate on this
repository.

## 1. Project Intent

SNS-S-S is a **public, educational simulation** for exploring how
Solar-Nano-Sphere (SNS) swarms might behave as space-based solar power
infrastructure.

Your job as an AI coding agent is to:

* Turn the high-level design in `/docs/*.txt` into clean, tested Python
  code.
* Keep the code **small, readable, and well-documented**.
* Make it easy for humans to:
  - run experiments,
  - inspect results,
  - and extend the framework in future phases.

## 2. Ground Rules

1. **Clarity over cleverness**

   Prefer explicit, well-named classes and functions. Avoid unnecessary
   metaprogramming, heavy abstractions, or opaque one-liners.

2. **Minimal dependencies**

   Standard library + `numpy` + `matplotlib` (and optionally `pytest`,
   `pandas`) should be enough.

   Do not add heavy frameworks (no TensorFlow/PyTorch/RL libraries) in
   this initial phase unless explicitly requested.

3. **Document as you go**

   Every public class and function should have a short docstring
   describing:
   - purpose,
   - inputs,
   - outputs,
   - and any key assumptions.

4. **Keep configs in files**

   Simulation parameters should live in simple config objects and/or
   external YAML/JSON files in `configs/`, not scattered constants.

5. **Tests are first-class**

   When adding new behavior, add or update tests in `tests/` so that
   humans can quickly verify that the simulation still behaves as
   expected.

## 3. Recommended Directory Layout

When populating the repo, target something like:

```text
src/
  world/
    __init__.py
    asteroid_world.py
  agents/
    __init__.py
    sns_agent.py
  host/
    __init__.py
    host_collector.py
  sim/
    __init__.py
    config.py
    simulation.py
  utils/
    __init__.py
    math_utils.py
    plotting.py

experiments/
  baseline_vs_coordinated.py
  sweep_eta_beam.py
  sweep_area_vs_count.py

configs/
  asteroid_baseline.yaml
  asteroid_coordinated.yaml

docs/
  (this is where the .txt design files live)

tests/
  test_asteroid_world.py
  test_sns_agent.py
  test_simulation_smoke.py
```

Any variations should be documented in `README.md`.

## 4. Implementation Roadmap for AI Agents

If you are implementing this from scratch, the suggested order is:

1. **World + agent skeletons**
   * Implement `AsteroidWorld` with `is_sunlit(theta, t)`.
   * Implement `SNSAgent` with state and a basic `step()` method that
     only supports HARVEST and IDLE.

2. **Host + core simulation loop**
   * Add `HostCollector`.
   * Implement a simple `Simulation` class that runs a fixed number of
     timesteps and records energies.

3. **Metrics + plotting**
   * Implement `MetricsRecorder` and basic matplotlib plots.

4. **Coordination logic**
   * Extend SNSAgent to support COMM_BEAM and MOVE modes.
   * Add configurable policy functions (baseline vs coordinated).

5. **Experiments folder**
   * Implement scripts described in
     `docs/04_experiments_and_metrics_for_codex.txt`.

6. **Tests**
   * Add smoke tests and a few unit tests to cover basic energy
     bookkeeping.

## 5. Communication with Human Collaborators

* Use clear commit messages, e.g.:
  - `feat: add AsteroidWorld with basic day/night model`
  - `feat: implement SNSAgent HARVEST/IDLE modes`
  - `feat: add baseline vs coordinated experiment script`
  - `test: add smoke test for short simulation run`

* When making non-trivial design choices, update the relevant `.txt`
  documentation under `docs/` or add a short `docs/CHANGELOG.txt`
  entry so humans can follow the reasoning.

## 6. Stretch Goals (Optional)

If the basic system is stable and well-tested, possible extensions
include:

* Adding a second environment (e.g., a GEO ring segment).
* Implementing simple CLI entrypoints via `python -m` or `typer/click`
  (if dependencies remain light).
* Providing a small Jupyter or Colab notebook in `notebooks/` that
  demonstrates end-to-end runs.

Focus first on getting a robust, well-structured **Asteroid Scout**
scenario running; everything else can build on that foundation.
