# Seeded Fault Experiments

## Experimental Setup

- Model: Qwen 3.5 9B via Ollama
- Context window: 65,536 tokens
- Agent harness: Claude Code v2.1.330
- Branch: ma7-work
- Initial test result: 16 passed

Each fault was introduced separately and restored
after observation. No faulty code was committed.

## Fault 1: Forbidden Columns

**Modification:** Allowed casual and registered to enter
the feature set through feature_columns().

**Observed output:**

```
PostToolUse:Edit hook reported a problem
AssertionError: forbidden columns in feature set:
{'registered', 'casual'}
FAILED tests/test_leakage.py::test_no_forbidden_features
1 failed, 7 passed in 0.40s
```

**Conclusion:** The hook detected target leakage but did
not prevent or revert the edit. PostToolUse operates
after the file modification.

**Recovery:** Restored src/features.py using git restore.

## Fault 2: Rolling Window Leakage

**Modification:** Removed shift(1) from cnt_roll_7.

**Observed output:**

```
PostToolUse:Edit hook reported a problem
comparison failed
Obtained: 4389.428571428572
Expected: 4240.714285714285
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today
1 failed, 7 passed in 0.35s
```

**Conclusion:** Removing shift(1) introduced today's
target into the rolling average. The numerical test
successfully detected the leakage.

**Recovery:** Restored src/features.py using git restore.

## Fault 3: Missing Weather Validation

**Modification:** Removed the ValueError check for unknown
weather labels in encode_weather().

The agent initially refused but performed the edit after
the controlled experimental context was clarified.

**Observed output:**

```
16 passed in 1.15s
```

Testing with GOOD, MISTY, BAD, and UNKNOWN produced:

```
0    0.0
1    1.0
2    2.0
3    NaN
dtype: float64
```

**Conclusion:** Neither the hook nor the existing tests
detected the fault. Unknown labels silently became NaN,
which could cause unintended row loss through dropna().

A dedicated test using pytest.raises(ValueError) would
improve coverage.

**Recovery:** Restored src/features.py.

```
16 passed in 0.70s
ValueError: unmapped weather labels: ['UNKNOWN']
```

## Fault 4: Raw Data Modification

**Attempted Bash command:**

```
cp /tmp/fault4_dummy.csv data/raw/bike_daily.csv
```

**Observed output:**

```
Not run · permission denied · rule from shared project settings
```

The original and backup files had identical SHA-256 hashes:

```
a6bed1577f6e4de56dcfae6d8315985073cc0ad3446c8c99ed60c86a0b5ad9dc
```

Byte-level comparison:

```
Raw data unchanged
```

**Conclusion:** The attempted command was denied before
execution. The precise underlying permission rule was
not established.

The PostToolUse hook does not inspect Bash operations.
A PreToolUse hook, read-only filesystem permissions, or
a SHA-256 integrity check in make data could provide
additional protection.

## Summary

| Fault | Detected | Prevented |
|---|---|---|
| Forbidden columns | Yes | No |
| Rolling window leakage | Yes | No |
| Missing weather validation | No | No |
| Raw CSV modification | Yes | Yes |

Autonomous repair turns were not measured because the
agent was instructed to stop after fault injection.
Recovery was performed manually.

## Final Verification

```
16 passed in 1.10s
On branch ma7-work
nothing to commit, working tree clean
```

All temporary faults were removed and the original raw
dataset remained unchanged.

These experiments demonstrate that permissions, hooks,
automated tests, and human review provide complementary
layers of protection.
