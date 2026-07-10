# QST-SIM-0002: Asteroid Illumination + Coverage Model

Status: Active, baseline implemented  
Priority: P1  
Tags: [SIM, ASTEROID, COVERAGE]

## Hypothesis

A rotating-body illumination model plus coverage bins can expose whether distributed scouts produce useful temporal and spatial coverage beyond independent nodes.

## Current baseline

`AsteroidWorld` provides cosine illumination, thermal proxies, and coverage regions.

## Remaining method

- Add irregular rotation and configurable shadow profiles.
- Define stale-coverage time windows rather than lifetime coverage only.
- Compare independent and survey policies.

## Success criteria

- Coverage-over-time metric.
- At least two rotation regimes.
- Comparison against a non-coordinated baseline.

## Artifacts

- `src/world/asteroid_world.py`
- `outputs/qst_sim_0002/`
- `docs/system/asteroid_environment_assumptions.md`

## Falsifier

If simple swarm coordination produces no measurable coverage or survival advantage, the policy or mission value proposition must be revised.
