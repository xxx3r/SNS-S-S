# QST-SBSP-0001: Relay Chain Reality Check

Status: Active
Updated: 2026-02-15
Tags: [SBSP, META, CTRL, DOCS]

## Hypothesis
If SNS framing explicitly treats relay chains as loss-minimization systems (coherence + pointing + coupling) rather than energy multipliers, then link-budget assumptions and design tradeoffs will stay physically grounded.

## Method
- Inputs: `calendar/roundups/2026-02-08.md`, current SNS docs, metasurface + beamforming references.
- Procedure: Draft a short technical note with definitions, non-goals, and practical relay design levers.
- Metrics: Note published in docs; references to metasurface and uncertainty-aware beamforming included.

## Success Criteria
- Must: Note states "no energy multiplication" and prioritizes coherence, pointing, and loss accounting.
- Nice-to-have: Includes an example relay-chain loss budget table.

## Artifacts
- docs/relay_chain_reality_check.md

## Risks
- Oversimplifying relay physics could hide thermal, phase-noise, or control loop limits.

## Next Step
Create a one-page draft note and link it from the docs index.
