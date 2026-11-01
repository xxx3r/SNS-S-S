# QST-SIM-0002 asteroid environment assumptions

The November 1 rotation-policy protocol is a fixed synthetic comparison, not an asteroid mission model.

## Frozen comparison

- two policies: the existing `baseline` and `survey` implementations;
- two constant rotation periods: 2 hours and 12 hours;
- six agents, 12 body-fixed coverage bins, 2-hour duration and 60-second timestep;
- identical asymmetric role placement in all cases: scout, scout, relay, storage, sensor, relay;
- a 600-second freshness window and 600-second warmup;
- four worlds and 2,880 agent-step records maximum.

After each step, the experiment records the sampled region for scout and sensor agents. The primary endpoint is time-average fresh coverage after warmup. Rotation affects the declared illumination environment; policy affects agent mode and movement. The older artifact used an identical externally supplied observation schedule for both rotations and therefore could not measure this interaction.

## Interpretation boundary

The fixed spherical body, cosine illumination, constant rotation, simple energy model and rule-based policies omit shape, tumbling, occlusion, terrain, sensor footprint, navigation error, communications, orbital dynamics and real target properties. A positive survey-minus-baseline delta is evidence about this simulator fixture only. A null or negative delta is retained and challenges the present simple-coordination value claim on the declared fixture.

No parameter may be tuned after output inspection. Irregular rotation, additional regimes, policy optimization and real-target inference require a separately accepted protocol.
