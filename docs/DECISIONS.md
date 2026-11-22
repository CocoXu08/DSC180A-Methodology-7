# Decisions

One line per methodological decision: what you chose, why, and what it changed.
Agents append here via the `/new-feature` skill; you append here by hand.

- Exclude `casual`, `registered`: they sum to `cnt` exactly. Leaky model R^2 1.000 -> honest ridge 0.583.
- Exclude `cnt_2d_bfr`: a shipped 2-day lag we cannot test the alignment of. Build our own lags instead.
- Exclude `instant`, `yr`, `days_since_2011`: time indexes let a tree predict a flat constant past 2011 and a linear model extrapolate a trend we have no grounds for.
- Split 2011 / H1 2012 / H2 2012 by date. Test set touched once, after all feature work.
- Report mean and persistence baselines with every score. Persistence (test R^2 0.510, MAE 840) is within 0.07 R^2 of ridge and beats it on MAE; that caveat goes in the report.
- Add `cnt_roll_14`: 14-day rolling average using strictly earlier calendar dates, with shift(1) before rolling. Validation R^2: Ridge 0.6475 -> 0.6919 (+0.0444); HGB 0.2185 -> 0.1643 (-0.0542). Retain for Ridge because the improvement exceeds 0.01. Training rows decreased from 348 to 334, so the improvement cannot be attributed solely to the new feature.
- Target transformation: predict daily demand changes (cnt - cnt_lag_1) and reconstruct ride counts using yesterday's observed demand. Validation R^2: HGB 0.1643 -> 0.6161; Ridge 0.6919 -> 0.6915. HGB MAE decreased from 1341.2 to 823.5. The transformation is defensible for one-day-ahead forecasting because yesterday's demand is available at prediction time. This experiment evaluated validation data only. The original untransformed pipeline remains unchanged.
