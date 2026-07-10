# Summer 2026 Repository Architecture

## Operating thesis

SNS-S-S is now one coupled instrument with four loops:

1. **Physical loop**: environment → PV → direct loads → storage / delivery / curtailment.
2. **Swarm loop**: sensing → local policy → coverage / relay / survival behavior.
3. **Confidence loop**: observations → ARCI dimensions → score + uncertainty → next measurement.
4. **Research loop**: literature → belief shift → quest → artifact → revised model.

The code and documentation should mirror these loops.

## Package boundaries

### `src/world`

Defines what each node can observe: illumination, temperature proxy, coverage region, and host line of sight.

### `src/agents`

Defines node role, mode, state, local energy ledger, health, and policy.

### `src/sim`

Builds scenarios, advances time, and aggregates mission metrics. It must not hide physical assumptions inside plotting or experiment scripts.

### `src/arci`

Combines explicit normalized dimensions and evidence confidence. ARCI does not ingest undocumented intuition.

### `src/research`

Parses weekly roundups and normalizes suggested actions into quest drafts.

## Data contracts

### Environment sample

- `sunlit`
- `flux_W_m2`
- `equilibrium_temperature_K`
- `region_id`
- `line_of_sight_to_host`

### Agent step result

- harvested energy
- direct-use energy
- battery charge
- capacitor charge
- load energy
- beam input
- delivered energy
- curtailed energy
- battery and capacitor states
- temperature, role, mode, health, and region

### Metrics summary

A run is not complete without final energy-flow totals, coverage, survival, and role/mode/health distributions.

## Backward compatibility

The Q1 2026 fields `energy_max`, `initial_energy`, and `COMM_BEAM` remain accepted. Their interpretation is narrower:

- `energy_max` means survival-battery capacity.
- `COMM_BEAM` means relay mode.
- old asteroid experiments remain controls, not canonical system definitions.

## Extension order

1. thermal derating and phase-change buffer
2. pointing / metasurface loss model
3. stochastic PV degradation
4. partial connectivity and delayed communication
5. ARCI worked examples from public asteroid data
6. calibration against higher-fidelity external tools
