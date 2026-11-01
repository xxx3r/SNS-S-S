# November 2026 Monthly scientific decision | SYNTH R2 × PTM/REF

**Decision source:** accepted `main` `006f7b2cd133cc39629e0584a1f6c40db937e272`; explicit-human request in Issue #30; November Trio v2 authority.  
**Decision:** prefer **A1, a separately validated development-only service/depletion semantics extension**. Keep R2 generation and the sealed holdout stopped until that extension passes its prospective validation freeze and Monthly or explicit human authority accepts the resulting semantics. A2 remains a valid narrower fallback, but it cannot answer the quest's useful-service question. PTM/REF documentation intake is deferred; no architecture is selected.

## Evidence ledger

| Claim | Status | Evidence and boundary |
|---|---|---|
| Failed electrical cases have no accepted numeric `useful_host_delivery_Wh`. | **ACCEPTED REPOSITORY RESULT** | `ThermalShadowResult` reports full requested consumption, derated available energy, final margin and PASS/FAIL, but no depletion time, cutoff, shedding or partial service. R1 therefore returns `null` on electrical failure. |
| Existing R0/R1 campaign configuration can support an R2 policy-benefit claim as written. | **CONTRADICTED BY ACCEPTED RESULT** | The protocol itself marks useful delivery and a stepwise action trace missing. Three holdout worlds are exploratory and cannot support a confirmatory claim. |
| The accepted SIM2 fixture shows a survey advantage. | **ACCEPTED, NARROW** | PR #139 records `+0.007575757575757569` time-average fresh-coverage delta in both declared constant-rotation regimes, with zero dead-agent difference. This does not establish irregular-rotation or asteroid mission value. PR #140 owns its appraisal. |
| W-doped VO2 can supply a drop-in `epsilon_cold=0.10`, `epsilon_hot=0.80` SNS surface. | **CONTRADICTED / UNKNOWN** | The 2013 primary coating paper reports one optimized W-doped multilayer near `epsilon_high=0.81` and `Delta epsilon=0.43`, implying a much higher low state than 0.10; performance belongs to a coating stack and test method, not a universal material constant. No SNS-installed surface is qualified. DOI: `10.1016/j.solmat.2013.07.023`. |
| PTM's claimed `3.956×` radiation-term discrepancy proves the full thermal model wrong. | **INDEPENDENT REPORT, NOT REPOSITORY-QUALIFIED** | The exact net-radiation term is proportional to `T^4 - T_sink^4`; a tangent linearization can differ from a secant calculation. The reported factor, body areas, view factors, emissivities and node temperatures still require source-bound reproduction. |
| H10, K12, S12 and S15 describe one interchangeable geometry. | **CONTRADICTED BY INTAKE** | They are different historical/reference stages. Bare-volume or CAD containment does not prove contacts, clearances, folding, support mass, electrical continuity or usable energy. |
| 450 nm Cu-Cu hybrid bonding demonstrates a thinner or lower-energy SNS node. | **DRAFT HYPOTHESIS ONLY** | The 2026 ECTC paper is a test-structure interconnect-pitch result, not a spacecraft package or system-energy result. DOI: `10.1109/ECTC51846.2026.00130`. |

## Track A decision: useful-service semantics

| Route | What it answers | Smallest validation / falsifier | Main risk | Authority | Disposition |
|---|---|---|---|---|---|
| **A1 — stepwise depletion/service extension** | Under the frozen fixed thermostat demand, how much host load and heater demand are actually served before energy becomes inaccessible? | Development-only analytic fixtures: abundant battery reproduces the accepted full-service trajectory; zero battery serves zero energy; one-step partial depletion matches hand calculation; 30 s vs 60 s timestep remains within a prospectively declared tolerance; every step satisfies energy conservation. Any failure blocks adoption. | A service-allocation rule is a new scientific assumption; temperature-dependent accessibility and heater coupling can be implemented incorrectly. | Monthly chooses the route; Post-Game owns the prospective protocol/validation slice; later Monthly/human acceptance is required before R2. | **PREFERRED** |
| **A2 — narrower supported-metric comparison** | Which bounded worlds pass/fail and how margins, temperatures and demanded energy differ under the existing aggregate evaluator? | Re-freeze the question and prove every reported field already exists; retain all failed worlds; prohibit “useful delivery” or policy-benefit language. | Changes the question. Negative final margin is not delivered host energy and cannot rank partial service. | Monthly/human must approve a new frozen criterion. | **FALLBACK ONLY** |
| **STOP** | Preserves truthful uncertainty. | Use if A1 cannot satisfy conservation/regression/timestep tests or no one accepts the service rule. | No R2 policy-benefit result. | Monthly/human. | **REQUIRED UNTIL A1 IS ACCEPTED** |

### A1 prospective semantics boundary

The next slice must freeze semantics before code or results:

1. Integrate an explicit non-increasing accessible-energy state on the existing time grid; never infer delivery from final negative margin.
2. At each step compute requested host and thermostat-heater energy. If insufficient energy remains, apply one declared **proportional service fraction** to both requests. This is a neutral fixed-policy accounting rule, not an optimized survival policy.
3. Couple actual heater energy—not requested heater energy—back into the temperature update.
4. Record requested and served host/heater energy, cutoff/depletion time, inaccessible reserve/derating energy, temperature trajectory and a residual conservation term.
5. Enforce, within frozen numerical tolerance: `initial_accessible = served_host + served_heater + remaining_accessible + inaccessible_or_derated_adjustment`; no negative delivery, no energy creation and no service after cutoff.
6. Do not open the sealed holdout, generate campaign worlds, change ranges, choose a new policy, or claim hardware feasibility. The slice ends with a validated interface or a retained failure.

This extension can answer a model-service question. It cannot validate battery chemistry, installed capacity, radiator performance, packaging or flight readiness.

## Track B decision: physical reference and thermal closure

SYNTH semantics do **not** require a finished spacecraft package. They require an explicit internally conserved model and honest claim boundary. Conversely, PTM/STOR physical claims require a dimensioned witness before adaptive-skin comparison:

- named thermal nodes and heat-flow edges, including radiation to a declared sink and conductive bypasses;
- installed battery, contacts/protection, electronics, PV/fold interface, supports and radiator/coating mass;
- source-backed dimensions, allowable local temperatures, current limits and charge/discharge conditions;
- usable cold energy rather than nameplate energy;
- one complete sun-shadow-sun energy balance with residuals;
- reproducible files and primary-source identities.

The first falsifier is a **mass/volume/energy-closed reference witness**, not an adaptive material sweep. If the reference cannot fit with clearances and electrical continuity, or its conserved thermal/electrical residual exceeds the frozen tolerance, that geometry is rejected. No larger KiteSeed, PV replacement, added radiator, S12/S15 selection or host-assisted architecture is authorized.

## Track C: 2035 integration horizon

Retain 3DI only as a requirements/break-even question. A later study must compare a physical 2026 baseline with bounded future parameters for total installed electronics mass/volume, total node energy under a representative workload, passives/power conversion, leakage, thermal coupling, reliability and manufacturing. A valid null result is that interconnect energy is immaterial to total node demand. This track cannot displace A1 or the physical-reference gate.

## Smallest executable next slice

- **Owner:** `post-game-research` (distinct from Weekly's live PR #140/PV route).
- **Quest/scope:** active `QST-SYNTH-0001`, `thermal-storage`.
- **Artifact:** prospective `service_depletion_v1` protocol plus development-only analytic/regression tests; no campaign result.
- **Budget:** 0 generated worlds, 0 campaign records, at most 60 runtime seconds and 2 MB.
- **Falsifier:** any energy-identity violation, pass-case regression, post-cutoff service, negative delivery, undeclared priority, or timestep instability beyond the frozen tolerance.
- **Preflight:** fresh source/owner check and `validate-standing-request`; stop if PR #140 or another owner claims the same slice.

## Intake and backlog disposition

- **Issue #30 — CONTINUE / Monthly decision made.** A1 is preferred; Post-Game may prepare and validate only the development semantics slice. R2/holdout remains stopped. Review after accepted A1 validation or on 2026-11-15.
- **Issue #131 — DEFER.** Keep as a research candidate. Next condition is the source-backed closed reference witness above; review 2026-11-15.
- **Draft PR #132 — DEFER MERGE.** Its careful claim-register structure is useful, but source archives remain unqualified and its October handoff text is stale. Before reconsideration: bind each numerical claim to a primary source or reproducible artifact, separate verified text from hypotheses, remove obsolete routing, and preserve private archives unless export is explicitly approved.
- **Issue #103 — CONTINUE with Weekly through 2026-12-31.** Record whether the A1 decision prevents repeated holdout access and whether Post-Game produces a distinct validated artifact without a new permission hop.
- **PR #140 — CONTINUE with existing Weekly owner.** Resolve its missing standing-action receipt finding, requalify the exact head, and merge only under Weekly's remaining transaction. Monthly does not duplicate or absorb its PV route.
- **SIM2 resource-collapse proposal — DEFER with Weekly.** PR #139 completed only the rotation-policy comparison. Keep resource accounting as a distinct fallback; do not reuse or widen the accepted four-world matrix. Review 2026-11-08.
- **SIM2 next-measurement proposal — CLOSED COMPLETED.** PR #139 executed the declared baseline-versus-survey matrix under both rotation regimes. Preserve the result and do not regenerate or expand it.
- **STOR auxiliary-safe-mode proposal — DEFER with Monthly.** It remains an architecture-changing alternative requiring a separate accepted Monthly/human architecture or assumption decision. The local fast-rotator falsifier is not a global architecture result. Review 2026-11-15.
- **STOR environmental-margins proposal — DEFER with Monthly.** Do not revive the locally falsified baseline through parameter optimism. Any later work needs a separately accepted, source-bounded margins protocol. Review 2026-11-15.

## Belief and policy effect

No standing-policy, scheduler, quest-membership, protected architecture or consolidated physical-belief change. The scientific decision narrows the next SYNTH question and preserves UNKNOWN where evidence is absent.
