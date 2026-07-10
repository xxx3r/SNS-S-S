# SNS v0.2 System Definition

**Status:** Summer 2026 research definition  
**Readiness:** simulation and critique, not hardware qualification

## 1. System identity

SNS is a family of ultra-light, energy-aware sensing and relay nodes operating as a swarm around asteroids, SBSP infrastructure, or other target environments.

The long-horizon physical archetype remains:

- a small hardened **seed** containing control, sensing, survival storage, and communications
- an ultra-light deployable **kite** providing PV area and possibly programmable optical / electromagnetic regions

Near-term proto-SNS systems may be tiles, flakes, hosted payload modules, or deployable-film units rather than literal 10 mm spheres.

## 2. Design invariant

`maximize useful mission information and energy throughput per unit mass, area, and complexity`

Every subsystem must justify:

- mass
- area
- power
- heat
- pointing burden
- manufacturing complexity
- data value

## 3. Role specialization

### Scout

Coverage, illumination mapping, and local environmental sensing. Small survival battery; no assumption of meaningful bulk energy storage.

### Sensor

Higher-value targeted measurement with conservative movement and communication duty cycles.

### Relay

Pulse buffer, pointing hardware, and intermittent data or energy transfer.

### Storage

Larger node or host-mounted reservoir. Wh-scale capacity belongs here, not inside every 10 mm seed.

## 4. Energy architecture

```text
incident sunlight
  ├─ direct loads
  ├─ pulse buffer
  ├─ survival battery
  ├─ relay / host delivery
  ├─ controlled reflection
  └─ curtailment / waste heat
```

The seed battery is sized for shadow survival and scheduling gaps. It is not sized to absorb all PV output.

### Summer 2026 seed envelope

For a true 10 mm core, use a research range near `0.02–0.15 Wh` usable electrical storage, with geometry sweeps extending beyond this range only as sensitivity studies.

### Required storage states

- battery energy and state of charge
- pulse-buffer energy
- battery / core / film temperature
- battery health
- predicted shadow duration
- curtailed power
- host or network storage availability

## 5. Control modes

- `HARVEST`
- `SCOUT`
- `COMM_BEAM`
- `MOVE`
- `IDLE`
- `SLEEP`
- `REFLECT`

Expensive work should occur preferentially in illumination. Darkness is primarily for survival, minimal sensing, and state preservation.

## 6. Environment interfaces

Each environment must expose:

- local solar flux
- illumination state
- temperature proxy or model
- coverage region
- line of sight to host / receiver

Canonical Summer 2026 environments are rotating asteroid and idealized GEO ring.

## 7. Open engineering gates

- combined radiation, vacuum, and thermal-cycle PV lifetime
- deployable-film mass and reliability
- thermal rejection under high incident flux
- pulse-power delivery and beam pointing
- partial-connectivity swarm control
- realistic data value versus a conventional orbiter
- manufacturing yield and deployment survival
- debris, governance, and beam-safety constraints

## 8. Model interpretation

A successful simulation demonstrates consistency with declared assumptions. It does not demonstrate manufacturability, mission approval, or economic viability.
