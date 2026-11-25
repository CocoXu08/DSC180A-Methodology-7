# DSC 180A Methodology Assignment 7
**Agentic Programming: Bike Sharing Demand Forecasting**

**Author:** Ziling Xu

## Results

This project investigates daily bike-sharing demand forecasting using
temporally valid features, explicit baselines, and automated verification.
The data were split chronologically: 2011 for training, the first half of
2012 for validation, and the second half of 2012 for testing.

I added a 14-day rolling mean of historical demand (cnt_roll_14) to the
original feature set. The feature is calculated after calendar reindexing
and uses only the 14 days preceding the prediction date.

| Stage | Model | Validation R² | Validation MAE | Test R² | Test MAE |
|---|---|---:|---:|---:|---:|
| Before | baseline_mean | -0.9318 | 2002.2 | -2.1441 | 2847.7 |
| Before | baseline_persistence | 0.4507 | 900.6 | 0.5099 | 840.1 |
| Before | ridge | 0.6475 | 832.9 | 0.5833 | 947.1 |
| Before | hgb | 0.2185 | 1296.6 | -0.4975 | 1972.6 |
| After | baseline_mean | -0.8583 | 1965.6 | -2.0333 | 2793.1 |
| After | baseline_persistence | 0.4507 | 900.6 | 0.5099 | 840.1 |
| After | ridge | 0.6919 | 763.2 | 0.6268 | 870.9 |
| After | hgb | 0.1643 | 1341.2 | -0.6534 | 2087.9 |

The number of features increased from 14 to 15. Increasing the
historical warm-up period from 7 to 14 days reduced the training sample
from 348 to 334 observations. The validation and test sets remained
unchanged at 182 and 184 observations, respectively.

Because the training sample also changed, the improvement cannot be
attributed exclusively to the additional feature.

The feature retention decision was based on validation performance.
The starter pipeline automatically printed test metrics during the
before-and-after runs, but those metrics were not used to select the
feature or tune hyperparameters.

The final untransformed results can be reproduced with:

    make all

They are stored in reports/metrics.json.

## Headline finding

Ridge regression outperformed histogram gradient boosting in the
presence of a growing demand trend. After adding the new feature,
ridge achieved a validation R² of 0.6919 and a test R² of 0.6268,
whereas HGB achieved 0.1643 and -0.6534, respectively. This result is
consistent with the limited extrapolation ability of tree-based models.
Although HGB performed worse than the persistence baseline, its test
MAE of 2087.9 was still better than the mean baseline's MAE of 2793.1.
The 14-day rolling feature improved ridge's validation R² by 0.0444
and reduced its validation MAE from 832.9 to 763.2, so I retained the
feature despite its negative effect on HGB's validation performance.

## Exercise 4: target transformation

The original HGB model predicts the absolute number of daily bike
rentals. Because demand increased between the training and evaluation
periods, the model may struggle to predict values outside the range
observed during training.

To address this limitation, I transformed the target into the daily
change in demand:

    delta_t = cnt_t - cnt_lag_1

The predicted demand was then reconstructed as:

    predicted_cnt_t = cnt_lag_1 + predicted_delta_t

This formulation allows the model to learn changes in demand rather
than its absolute level. Both ridge and HGB were evaluated using the
same feature set, training observations, validation observations,
and original hyperparameters.

| Model | Validation R² | Validation MAE |
|---|---:|---:|
| Baseline mean | -0.8583 | 1965.6 |
| Baseline persistence | 0.4507 | 900.6 |
| Original ridge | 0.6919 | 763.2 |
| Differenced ridge | 0.6915 | 763.0 |
| Original HGB | 0.1643 | 1341.2 |
| Differenced HGB | 0.6161 | 823.5 |

The transformation substantially improved HGB's validation R²,
from 0.1643 to 0.6161, while reducing MAE from 1341.2 to 823.5.
The transformed HGB also outperformed the persistence baseline on
both evaluation metrics. However, ridge still achieved the strongest
overall validation performance.

Ridge's performance remained nearly unchanged after transformation.
Unlike a tree-based model, a linear model can extrapolate beyond the
range of its training observations. Differencing therefore offers
less additional benefit to ridge in this experiment.

I consider this transformation methodologically defensible rather
than simply a way to improve HGB's score. Yesterday's demand is
available at prediction time in a one-day-ahead forecasting setting.
The transformation does not introduce current or future demand into
the prediction features, and all predictions are converted back to
the original demand scale before evaluation.

However, this approach assumes that yesterday's actual demand is
available. The same assumption would not necessarily hold for
multi-day-ahead forecasts.

The transformation experiment evaluated validation data only.
No transformed model was evaluated on the test set, and the
committed metrics file preserves the original untransformed pipeline.

The experiment can be reproduced with:

    python -m experiments.target_transformation

## Exercise 5: ridge vs persistence

I would retain the persistence baseline for deployment if the primary
objective were to minimize absolute daily forecasting error.
Although ridge outperformed persistence on validation, achieving an
R² of 0.6919 compared with 0.4507 and an MAE of 763.2 compared with
900.6, the test results provide a more mixed conclusion. Ridge achieved
a higher test R² of 0.6268 compared with persistence's 0.5099, but its
test MAE of 870.9 was worse than persistence's 840.1. R² is based on
squared errors and therefore places more weight on large forecasting
errors, whereas MAE measures average absolute error directly.
Persistence is also simpler to implement, requires no model fitting,
and has no estimated parameters. If avoiding large forecasting errors
were the primary business objective, ridge could be preferable.
However, without an explicit cost function that places greater weight
on large errors, I would retain persistence and continue evaluating
ridge on additional future observations before deployment.

## Attribution

Model: qwen3.5:9b via Ollama, configured as bikeshare-coder with a
65,536-token context window and accessed through Claude Code.
I did not switch between local model sizes during the experiment.
ChatGPT (GPT-6) was also used for implementation guidance, debugging,
methodological discussion, and drafting documentation.

### Agent-generated or AI-assisted work

- The initial implementation of cnt_roll_14 in src/features.py.
- The initial adjustment to LAG_WARMUP in src/config.py.
- The initial 14-day rolling feature test in tests/test_leakage.py.
- Temporary code modifications for the seeded-fault experiments.
- Assistance with the additional feature contract test.
- Assistance with the review-features skill and CLAUDE.md rules.
- Assistance with the target transformation experiment script.
- Structured audit output generated by agent/audit.py.
- Assistance with experimental documentation and this report.

### Human decisions and verification

- Selected the 14-day rolling mean as an additional historical
  demand feature.
- Reviewed the feature definition to ensure it used strictly
  historical observations.
- Detected and corrected the unintended changes to the existing
  7-day lag and rolling features caused by changing LAG_WARMUP.
- Detected a duplicate test function name and replaced conditional
  assertions with explicit checks to avoid silently skipped tests.
- Verified the actual model metrics rather than accepting the
  agent's initial performance claims.
- Retained the new feature based on the improvement in ridge's
  validation performance.
- Introduced and restored temporary faults to evaluate the
  effectiveness and limitations of the verification system.
- Confirmed that the raw dataset remained unchanged after the
  attempted Bash overwrite.
- Evaluated daily demand differencing using validation data only.
- Preserved the untransformed pipeline and its final metrics.
- Reviewed the trade-off between ridge and persistence using both
  R² and MAE.

The verification process demonstrated that an agent can produce
plausible code while introducing unintended methodological changes.
For example, changing the historical warm-up constant unintentionally
altered the original seven-day features. The agent also introduced a
duplicate test name and reported an inaccurate validation result.
These issues required human review and independent execution.

The seeded-fault experiments showed that the PostToolUse hook detected
the inclusion of forbidden target-related columns and the removal of
the rolling feature's historical shift. However, removing the unknown
weather-label check was not detected by the existing test suite.
A separate synthetic-input check exposed this limitation. The original
validation behavior was subsequently restored.

The Bash overwrite attempt was denied by the project's permission
configuration. Raw data integrity was independently verified using
the file hash and a byte-for-byte comparison. Fault recovery was
performed manually, so autonomous agent repair turns were not measured.

The custom review-features skill packages the repeated process of
checking feature availability, leakage, calendar alignment, test
coverage, and unintended changes to existing features.

The SDK-based self-audit reported no leakage, valid temporal splitting,
both baselines present, and reproducibility, with high confidence and
an empty findings list. Its raw output is preserved in
reports/audit.jsonl. The reported repository identifier was "..",
which is a limitation of the generated output. The audit conclusion
is treated as additional evidence, not as proof that the repository
is free from methodological errors.

Overall, this assignment demonstrated that the value of agentic
programming depends on explicit specifications, independent
verification, reproducible experiments, and human methodological
judgment rather than trusting the agent's claims alone.
