# `service_depletion_v1` prospective semantics

This development-only interface implements the November A1 decision for
`QST-SYNTH-0001`. It does not modify the accepted R0/R1 evaluator, generate a
world, inspect sealed holdout bytes, or authorize R2.

The model begins with accessible energy after the existing discharge-efficiency,
reserve, and temperature-capacity rules. Accessible energy never increases. At
each existing thermal timestep, the fixed host request and any thermostat-heater
request receive one shared proportional service fraction. Only served heater
energy enters the thermal update. The first partially served step defines the
cutoff; all later service is zero.

Every step records requested and served host/heater energy, service fraction,
remaining accessible energy, energy made inaccessible by further temperature
derating, temperature, and conservation residual. The frozen identity is:

`initial accessible = served host + served heater + remaining accessible + inaccessible derating`.

The development override may reduce initial accessible energy for analytic zero
and one-step controls, but it cannot create energy above the model-derived limit.
The frozen tolerances and prohibited inferences are machine-readable in
`configs/synthetic_worlds/service_depletion_v1.json`.

Passing these tests validates only the declared model interface. It does not
validate battery chemistry, installed capacity, packaging, radiator performance,
architecture, or flight readiness. R2 and the sealed holdout remain stopped until
Monthly or explicit-human authority accepts the semantics separately.
