# QST-ARCI-0001: ARCI v0.1 Draft + Synthetic Target

Status: Active, scaffold implemented  
Priority: P0  
Tags: [ARCI, ASTEROID, UNCERTAINTY]

## Hypothesis

A transparent scorecard with separate evidence confidence can make asteroid-target reasoning more useful without pretending to know exact resource value.

## Current baseline

`src/arci/model.py` implements seven dimensions, weights, uncertainty bounds, grade, and recommendation.

## Remaining method

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
