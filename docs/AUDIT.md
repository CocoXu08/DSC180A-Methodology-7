# Exercise 3: Peer Leakage Audit

## 1. Repository Information

- **Reviewer:** Ziling Xu
- **Repository:** https://github.com/zaz003-cyber/DSC180A-Methodology-6
- **Audited commit:** `1e30c29dd031e7c1cceea023c05ef473ac63796b`
- **Audit date:** November 25, 2026
- **Auditing model:** `bikeshare-coder` (Qwen3.5 9B via Ollama and Claude Code)

I independently audited another student's repository. I was not involved in developing the audited code. I cloned the repository into a separate directory and checked out the specified commit to ensure that the review was conducted on a fixed version.

## 2. Auditor's Original Findings (Verbatim)

The following is the auditor's original response, preserved without correcting its statements or line references.

### Leakage Audit Findings

Commit: 1e30c29

**1. Target Leakage — none**

- No forbidden columns (casual, registered, cnt) in feature set; guarded by feature_columns() excluding FORBIDDEN at line 88 (src/features.py)
- Lag features correctly shifted: cnt_lag_1 at line 77, cnt_lag_7 at line 78, both shifted before rolling operations
- Rolling window excludes today: cnt_roll_7 uses .shift(1).rolling(LAG_WARMUP) (line 79); cnt_median_7 uses .shift(1).rolling(7) (line 80)
- Verified by tests in tests/test_leakage.py: lines 37–60, 72–85

**2. Temporal Validity — valid**

- Temporal split at src/train.py:58–64 respects date boundaries (TRAIN_END = "2011-12-31", VALID_END = "2012-06-30")
- No random splitting; partitions are disjoint and ordered by time
- Verified by tests in tests/test_split.py: lines 16–30

**3. Baseline Reporting — complete**

- Both baselines reported for validation (reports/validation.json lines 23–46) and final evaluation (reports/metrics.json lines 23–42):
  - baseline_mean: R² = −0.9318 (valid), −2.1441 (test)
  - baseline_persistence: R² = 0.4507 (valid), 0.5099 (test)
- Persistence baseline correctly implemented as identity predictor at src/train.py:35–47

**4. Reproducibility — assumed valid**

- Models use random_state=0 (src/train.py:54)
- Estimators are cloned before fit (src/train.py:81)
- No non-deterministic operations in feature pipeline

---

Summary: No findings. All five audit criteria satisfied per the auditor checklist.

## 3. Verification Performed

The repository was cloned and checked out at the supplied commit using `git clone` and `git switch --detach`.

The test suite was run using an existing virtual environment:

    ~/Downloads/bikeshare-open-starter/.venv/bin/python -m pytest /Users/xujar/Downloads/ma7-partner-audit/tests/ -v

**Observed result: 21 tests passed.**

I also compared the auditor's claims with the relevant source code and existing metrics files at the reviewed commit.

The training command was not executed during this audit because it could overwrite the existing metrics output. Therefore, I did not independently reproduce the complete training pipeline.

## 4. My Independent Assessment

### Target Leakage — Agree, with qualifications

I agree that there is no confirmed target leakage in the reviewed feature set.

In `src/config.py`, the target and its components (`cnt`, `casual`, and `registered`) are classified as leakage-related columns and included in `FORBIDDEN`.

In `src/features.py`, `feature_columns()` excludes forbidden numeric columns (lines 75–78). The one-day and seven-day lag features are generated from historical values (lines 68–69). Both rolling features shift the target by one day before aggregation (lines 70–71).

The tests also check forbidden columns, historical lags, rolling-window behavior, and potential exact target identities.

One qualification is that actual same-day weather variables may not be known at the start of a forecasting day. Their availability depends on the intended prediction time and whether forecasts or observed weather values are used. This is an assumption to clarify rather than confirmed leakage in the reviewed implementation.

### Temporal Validity — Agree

I agree that the temporal splitting logic is valid.

`src/train.py` uses chronological boundaries for training, validation, and testing (lines 52–58). `src/config.py` defines the training cutoff as December 31, 2011, and the validation cutoff as June 30, 2012.

The corresponding split tests check that the partitions are nonempty, chronologically ordered, and do not overlap.

No random train/test split was identified in the reviewed training code.

### Baseline Reporting — Agree

Both required baselines are implemented in `src/train.py`:

- `baseline_mean`, using `DummyRegressor`
- `baseline_persistence`, predicting `cnt_lag_1`

They appear in the `MODELS` dictionary at lines 45–50.

The existing `reports/metrics.json` includes both baselines alongside ridge and HGB, with validation and test R² and MAE.

The reported validation and test R² values agree with those cited by the auditor.

### Reproducibility — Partially Agree

The repository provides documented commands in `README.md` and `Makefile`. The HGB model uses a fixed random seed, and the training code clones estimators before fitting them.

These are positive signs of reproducibility.

However, the auditor described reproducibility as "assumed valid," and I did not independently rerun the complete data-to-metrics pipeline. I therefore consider reproducibility supported by the implementation and documentation, but not fully verified by this audit.

### Auditor Accuracy

The auditor's overall findings were broadly consistent with the inspected implementation, but some file and line references were inaccurate.

For example, the auditor identified `feature_columns()` at line 88 of `src/features.py`, whereas it actually appears at lines 75–78 in the reviewed commit.

This did not change the overall leakage conclusion, but it reinforces the importance of verifying an agent's claims against the source rather than trusting its references automatically.

## 5. Final Verdict

**No confirmed target-leakage or temporal-splitting issue was identified that demonstrably changed the reported model metrics.**

I agree with the auditor's conclusions regarding target exclusions, lag construction, chronological splitting, and baseline reporting.

I partially agree with its reproducibility assessment because the complete pipeline was not independently rerun.

All 21 existing tests passed. Nevertheless, the passing tests and the automated auditor's conclusion should not be interpreted as guarantees that the repository is free of all methodological errors.

The review illustrates the value of combining an independent AI auditor with manual source verification and explicit documentation of what was and was not tested.

