# Method implementation and publication checks

This package preserves the 39 calculation, parsing, template and export functions extracted from `CSF_SWARA_COCOSO_App_FIXED.py`. Their abstract syntax is checked against the archived author source. New `service.py` validation checks reject incomplete or ambiguous inputs before those functions run.

## Material differences from the revised maturity workbook

| Element | Supplied Python implementation | Previously revised workbook |
|---|---|---|
| Default SWARA comparative importance | Each sorted criterion's own score when S is absent | Difference between consecutive sorted scores |
| SWARA ties | Sort by score, then accuracy; score-as-S can produce different weights for equal scores | Equal scores imply a zero gap and equal weights |
| Optimistic/pessimistic scenarios | Add/subtract radius from components, then clip each component to [0,1] | Geometry-limited directional displacement |
| CoCoSo S/P | Apply fuzzy operators, then score the aggregates | Convert valid scenarios to scalar scores; S=sum(W*z), P=sum(z^W) |
| Nonpositive score handling | Shift a score vector by its minimum plus epsilon | Explicit denominator/domain checks |
| Scenario combination | Equal mean of optimistic and pessimistic K | Gamma-weighted combination, baseline gamma=0.5 |
| Expert weights from linguistic expertise | Uses h=1-T²-I²-F² in the supplied expert-weight expression | Uses explicitly entered expert parameters |

The package intentionally does not call these two implementations equivalent. Choosing a paper's final algorithm requires an explicit methodological decision, rather than a packaging change.

## Spherical validity

Component bounds alone do not establish T²+I²+F² <= 1. For example, the supplied pessimistic transformation of `[0.1, 0.9, 0.1, 0.2]` returns `[0, 1, 0.3, 0.2]`, whose center has squared norm 1.09. Fuzzy power and aggregate intermediates also require separate domain review. The interface reports how many scenario centers violate the unit sphere; a zero count for scenarios does not certify all intermediates or validate the method.

No arithmetic changes were made to hide or repair this issue. Results remain those of the author's supplied implementation. A scientifically revised release should receive a new version and separate regression baselines.

## Packaging changes

- Separated numerical functions from the Streamlit interface.
- Preserved original author attribution and archived the unmodified source.
- Added complete-pair, identifier, rating, weight, parameter and file-size checks.
- Required criterion weights for CoCoSo rather than silently falling back to equal weights.
- Added synthetic demonstrations, explicit execution, stale-result clearing and run metadata.
- Removed network font loading from the new interface.
- Added source launchers, portable Windows build, deployment files and tests.

The app is not a replacement for the 8-level / 24-cell maturity workbook: it does not implement that workbook's sequential maturity gating, essential-indicator rules, CML or BMI.
