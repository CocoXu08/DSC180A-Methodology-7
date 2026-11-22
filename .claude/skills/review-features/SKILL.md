---
name: review-features
description: Review a model feature for target leakage, correctness, and test coverage.
allowed-tools: Read, Grep, Glob, Bash(make test), Bash(git diff:*)
---

# Feature review: $ARGUMENTS

Review the specified feature using the following workflow.

1. Read CLAUDE.md, src/config.py, src/features.py,
   tests/test_leakage.py, and tests/test_contract.py.

2. Verify that the feature uses only information
   available at prediction time.

3. Check that the feature is not forbidden and has
   been explicitly classified as an approved feature.

4. For lagged or rolling features, verify calendar
   alignment, window length, and shift direction.
   Check that existing feature definitions remain correct.

5. Inspect the relevant tests. Check for duplicate
   test names and assertions that can be silently skipped.

6. Run make test and inspect the actual output.
   Do not claim success unless the tests pass.

7. Report:
   - Feature name
   - Availability argument
   - Leakage risk
   - Test coverage and actual test result
   - Findings supported by code
   - Final verdict: PASS or FAIL

Do not modify files, train models, or commit changes.
Report any problems instead of fixing them.
