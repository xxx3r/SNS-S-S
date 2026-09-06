# QST-ARCI-0001: ARCI v0.1 Draft + Synthetic Target

Status: Completed — accepted synthetic assessment merged in PR #54  
Priority: P0  
Tags: [ARCI, ASTEROID, UNCERTAINTY]

## Hypothesis

A transparent scorecard with separate evidence confidence can make asteroid-target reasoning more useful without pretending to know exact resource value.

## Current baseline

`src/arci/model.py` implements seven dimensions, weights, uncertainty bounds, grade, and recommendation.

## Completed method

- Create one clearly synthetic target.
- Attach evidence types and missing-data flags.
- Run weight and confidence sensitivity.
- Define the next-measurement recommendation.

## Success criteria

- Reproducible JSON assessment.
- Score and confidence shown separately.
- Weight sensitivity does not hide major reversals.
- No unsupported dollar valuation.

## Artifacts

- `configs/arci_synthetic_target.json`
- `experiments/arci_example.py`
- `outputs/qst_arci_0001/`

## Falsifier

If small arbitrary weight changes dominate the result, ARCI should remain a multidimensional dashboard rather than a headline grade.

## Completion disposition — 2026-09-06

Merged PR #54 and its accepted output satisfy every declared method and success criterion:

- one clearly synthetic target carries explicit evidence types and missing-data flags;
- score 0.685 and confidence 0.5225 remain separate;
- all 28 bounded weight/confidence cases remain `research-only`, with no major grade reversal;
- the artifact names `surface_operations` as the largest weighted confidence gap and recommends synthetic regolith-cohesion/dust-response measurement;
- no external observation, unsupported dollar valuation, belief, queue, or architecture claim was introduced.

The falsifier was not triggered on the declared bounded perturbations. That result supports ARCI v0.1 as a transparent research dashboard for this synthetic fixture; it does not calibrate the ontology or establish a real asteroid grade. Any surface-operations evidence campaign is a distinct successor question requiring its own accepted quest slice.
