# QST-SIM-0002: Asteroid Illumination + Coverage Model

Status: Active, baseline implemented  
Priority: P1  
Tags: [SIM, ASTEROID, COVERAGE]

## Hypothesis

A rotating-body illumination model plus coverage bins can expose whether distributed scouts produce useful temporal and spatial coverage beyond independent nodes.

## Current baseline

`AsteroidWorld` provides cosine illumination, thermal proxies, and coverage regions.

## Remaining method

- Preserve the accepted constant-rotation comparison without repeating its four worlds.
- Treat irregular rotation and configurable shadow profiles as a separately frozen future protocol, not an extension of the accepted matrix.
- Keep resource accounting distinct from coverage-policy appraisal.

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

## November 1 fixed-matrix result

PR #138 prospectively froze, and PR #139 accepted, one four-case synthetic comparison: baseline versus survey under rotation periods of `7200 s` and `43200 s`. The survey-minus-baseline primary endpoint, time-average fresh coverage after the fixed warmup, was `+0.007575757575757569` in both regimes. Every case had zero dead agents; final fresh coverage was `0.25` in every case.

This supports only a small simple-coordination coverage effect on the declared fixture. Equal deltas do not distinguish the two constant-rotation regimes, and the zero dead-agent delta supplies no survival advantage. The result does not support irregular rotation, parameter tuning, a real-asteroid mission claim, or protected architecture selection. The four worlds must not be repeated merely to seek a larger or rotation-sensitive effect.
