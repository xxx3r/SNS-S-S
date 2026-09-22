# SNS as a Measurement Philosophy for Space Resource Intelligence

Status: repository outline; not externally published  
Quest: `QST-FUND-0001`  
Readiness boundary: model evidence and critique, not hardware, mission, or economic qualification

## Editorial contract

Every technical statement in the eventual public artifact must carry one of these labels:

- **DEMONSTRATED** — reproduced by accepted repository code or data.
- **MODELED** — follows from a declared model and its assumptions.
- **ASSUMED** — an input or boundary chosen for the model, not measured here.
- **SPECULATIVE** — a design possibility or research direction that has not passed the relevant gate.

The article should keep those words visible rather than hiding them in footnotes. It should distinguish “the model is internally consistent” from “the system can be built,” and distinguish target score from evidence confidence.

## One-sentence thesis

SNS is most useful today not as a promise of self-replicating nanomachines, but as a software-first discipline for deciding what to measure next, exposing energy and uncertainty, and testing whether distributed instruments earn their complexity over a better conventional orbiter.

## 1. Original SNS vision: begin with the myth, then narrow it

Narrative move: open with the long-horizon image of numerous light-driven nodes sensing, relaying, and perhaps moving energy through the Solar System.

- **SPECULATIVE:** ultra-light autonomous swarms could eventually distribute sensing and relay functions across targets or infrastructure.
- **ASSUMED:** the motivating value is useful mission information and energy throughput per unit mass, area, and complexity.
- **DEMONSTRATED:** the repository now records explicit energy, coverage, survival, confidence, and failure outputs instead of treating the vision as evidence.

Pivot sentence: the project became more credible when it stopped asking “How grand could the swarm become?” and began asking “Which claim can this model falsify next?”

Primary sources: `docs/00_SNS-S-S_Overview.txt`, `docs/system/sns_v0_2_system_definition.md`, and `docs/architecture/summer_2026_repository_architecture.md`.

## 2. Seed + kite architecture: separate survival from collection area

Explain the current physical archetype:

- a hardened **seed** for control, sensing, survival storage, and communication;
- a deployable **kite** for photovoltaic area and possible optical or electromagnetic functions;
- specialized scout, sensor, relay, and storage roles rather than identical nodes.

Claim ledger:

- **ASSUMED:** the seed/kite split is the working system definition.
- **MODELED:** harvested energy is resolved into direct use, pulse buffer, survival battery, host delivery, controlled reflection, or curtailment.
- **DEMONSTRATED:** repository simulations expose those channels and retain curtailed energy rather than silently treating collection as useful delivery.
- **SPECULATIVE:** literal 10 mm flight seeds, programmable kite surfaces, manufacturing yield, deployment survival, and beam safety remain open engineering gates.

The central correction is architectural: a seed battery is a survival buffer, not a reservoir for all kite output. Wh-scale storage belongs in larger or host-supported roles unless evidence shows otherwise.

## 3. Asteroid surveying pivot: information before extraction

Frame the near-term SNS user as a scientist or mission designer deciding which observations reduce uncertainty, not an operator claiming mineral value from sparse remote sensing.

- **MODELED:** asteroid environments expose illumination, coverage, temperature proxy, and host line of sight.
- **DEMONSTRATED:** current experiments can report energy flow, stale coverage, and synthetic target sensitivity.
- **ASSUMED:** the present environment and policy abstractions are adequate only for discriminating software questions.
- **SPECULATIVE:** economic resource value, autonomous extraction, and mission superiority are outside current evidence.

Near-term testable claim: given an explicit observation schedule and energy ledger, SNS-S-S can identify which missing measurement or resource constraint should be tested next. A successful test produces an inspectable artifact; it does not require nano-scale hardware.

## 4. Storage geometry correction: let volume defeat the slogan

Use the storage audit as the first major example of measurement philosophy changing the design.

- **DEMONSTRATED:** the accepted 1,296-case geometry sweep produced 1,240 PASS cases under its declared electrical assumptions.
- **DEMONSTRATED:** the 10 mm cases span approximately `0.0138–0.2094 Wh` usable storage, not the former generic `0.1–10 Wh` range.
- **MODELED:** at 1% active duty during shadow, 10 mm cases pass `87.3%`; the rate falls to `45.1%` at 100% active duty.
- **ASSUMED:** cell energy density, battery volume fraction, reserve, efficiencies, load, and shadow duration come from the frozen sweep configuration.
- **SPECULATIVE:** thermal, radiation, aging, wiring, converter, manufacturing, and complete package qualification remain unresolved.

Interpretation: the model did not “prove the seed.” It replaced a diffuse capacity claim with a geometry-bounded survival question and made low-activity darkness an explicit control requirement.

## 5. Explicit energy-chain simulation: collection is not delivery

Use the canonical chain:

```text
incident sunlight
  -> direct loads
  -> pulse buffer / survival storage
  -> relay or host delivery
  -> curtailment and waste heat
```

- **MODELED:** every joule must enter an explicit channel.
- **DEMONSTRATED:** the accepted synthetic SIM3 grid reports delivery, curtailment, coverage, temperature, and survival separately.
- **DEMONSTRATED:** increased receiver visibility raised synthetic delivery on one fixed fixture, while curtailment remained orders of magnitude larger than delivery.
- **ASSUMED:** GEO geometry, eclipse fractions, beam efficiency, receiver visibility, role mix, and fixture duration are model inputs.
- **SPECULATIVE:** real ephemerides, relay hardware performance, preferred architecture, and mission readiness are not established.

Editorial warning: never translate high harvested energy into high useful mission output without showing the loss and curtailment path.

## 6. ARCI and uncertainty: a score must reveal what it does not know

Introduce ARCI as seven explicit dimensions with separate score and confidence.

- **DEMONSTRATED:** the accepted synthetic fixture yields score `0.685`, confidence `0.5225`, and confidence-adjusted score `0.3579125`.
- **DEMONSTRATED:** all 28 bounded weight/confidence perturbations remain `research-only`; no major grade reversal occurs.
- **DEMONSTRATED:** `surface_operations` is the largest weighted confidence gap and therefore the next-measurement recommendation.
- **MODELED:** score and confidence are weighted means, and the current uncertainty band widens as confidence falls.
- **ASSUMED:** dimension definitions, default weights, and perturbation bounds are a transparent v0.1 policy.
- **SPECULATIVE:** ARCI is not calibrated to real asteroid value and does not qualify its own ontology.

The public lesson is procedural: uncertainty is not a disclaimer added after a recommendation; it helps choose the next measurement.

## 7. Why a better orbiter may outperform a swarm

State the countercase directly. A conventional orbiter may win when one platform can provide the required spatial coverage, calibration stability, bandwidth, thermal control, pointing accuracy, and instrument quality with less deployment and coordination risk.

Potential orbiter advantages:

- one calibrated instrument chain instead of cross-node calibration;
- simpler navigation, communications, command, and failure analysis;
- higher power, aperture, thermal mass, and data-return capability per instrument;
- no swarm deployment-yield or partial-connectivity penalty;
- lower operational complexity when simultaneous distributed sampling adds little information.

Potential swarm advantages remain hypotheses: graceful degradation, simultaneous local measurements, geometry diversity, and coverage under occlusion. They are earned only when a matched comparison shows useful information or mission output after coordination, relay, calibration, and loss costs.

- **DEMONSTRATED:** the repository has not yet established general swarm superiority.
- **MODELED:** some bounded coordinated cases improve selected synthetic metrics.
- **SPECULATIVE:** an SNS swarm outperforms a purpose-built orbiter for a real target or mission.

## 8. Reproducible public tables

The outline commits the final artifact to at least these two repository-generated tables. Run them in a clean checkout; do not substitute hand-edited numbers.

### Table A — storage geometry by core diameter

```bash
python experiments/storage_geometry_audit.py \
  --config configs/storage_geometry_audit.json \
  --out outputs/qst_stor_0001
```

Primary generated table: `outputs/qst_stor_0001/README.md`, “Results by core diameter.”  
Machine-readable source: `outputs/qst_stor_0001/summary.json`.

Expected accepted anchors: `1,296` cases; overall pass rate `95.7%`; 10 mm usable range approximately `0.0138–0.2094 Wh`.

### Table B — ARCI synthetic sensitivity

```bash
python experiments/arci_example.py \
  --config configs/arci_synthetic_target.json \
  --out outputs/qst_arci_0001
```

Primary generated data: `outputs/qst_arci_0001/synthetic_target_sensitivity.json`. The final article should render a compact table with baseline score, confidence, adjusted score, perturbation range, grade stability, and next-measurement dimension.

Expected accepted anchors: score `0.685`; confidence `0.5225`; adjusted score `0.3579125`; 28 sensitivity cases; adjusted-score range `0.3442125–0.3716125`; next measurement `surface_operations`.

Optional third figure/table: plot or tabulate useful delivery versus curtailment from `outputs/qst_sim_0003/eclipse_beam_sweep.json` and `outputs/qst_sim_0003/receiver_availability.json`, keeping the synthetic and fixed-fixture labels visible.

## 9. 2026–2035 validation path

This is a gate sequence, not a forecast that later stages will succeed.

| Period | Validation question | Evidence needed | Stop condition |
| --- | --- | --- | --- |
| 2026 | Can the software expose assumptions, losses, uncertainty, and falsifiers? | Reproducible repository experiments, immutable configs, failed cases, and reviewable artifacts | Outputs cannot be reconstructed or conclusions outrun the declared model |
| 2027–2028 | Do higher-fidelity component and environment models preserve the same conclusions? | Thermal-vacuum, radiation, degradation, pointing, communications, and calibration data connected to versioned models | Key margins vanish or uncertainty cannot be bounded |
| 2029–2031 | Does a hosted or small precursor provide useful measurements at tolerable operational cost? | Hardware-in-loop and hosted-flight evidence with complete energy/data ledgers | Conventional instrument achieves the objective more simply or reliably |
| 2032–2035 | Does distributed operation add mission value after deployment and coordination costs? | Matched mission comparisons against a strong orbiter baseline | Swarm benefit disappears after relay, calibration, failure, governance, and lifecycle costs |

- **ASSUMED:** these periods organize validation questions; they are not commitments or readiness dates.
- **SPECULATIVE:** any path to a flight swarm, resource-extraction system, or economic deployment.

## 10. Invitation for expert critique

End the public artifact by asking domain experts to attack the model at its boundaries:

1. Which storage, thermal, radiation, deployment, or calibration assumption is least defensible?
2. Which measurement would most reduce ARCI uncertainty for a real target?
3. Where does a conventional orbiter dominate the distributed concept?
4. Which loss, failure, or operational burden is missing from the explicit ledger?
5. What result would make the seed/kite or swarm framing not worth pursuing?

Critique should be converted into a bounded test, corrected assumption, or explicit stop—not absorbed as vague optimism.

## Falsifier and publication boundary

The framing fails if it cannot name a near-term user or testable claim without depending on nano-scale hardware. This outline meets that gate only at the software-research level: it gives mission designers and researchers reproducible ways to audit storage claims, energy accounting, and measurement uncertainty.

This file is a repository outline. External publication, new factual claims, economic conclusions, and hardware-readiness language require their own review and authority.
