"""Compare direct and differenced targets on validation data only."""

import pandas as pd

from sklearn.base import clone
from sklearn.metrics import r2_score, mean_absolute_error

from src.config import PROCESSED, TARGET
from src.features import feature_columns
from src.train import MODELS, temporal_split


def main():
    df = pd.read_parquet(PROCESSED)
    cols = feature_columns(df)

    train, valid, _ = temporal_split(df)

    X_train = train[cols]
    X_valid = valid[cols]

    y_train = train[TARGET]
    y_valid = valid[TARGET]

    # Report both baselines and the original models.
    print("Original models - validation only")
    print("-" * 60)

    for name, estimator in MODELS.items():
        model = clone(estimator)
        model.fit(X_train, y_train)
        pred = model.predict(X_valid)

        print(
            f"{name:25s} "
            f"R2 = {r2_score(y_valid, pred):.4f}  "
            f"MAE = {mean_absolute_error(y_valid, pred):.1f}"
        )

    # Transform the target into daily demand changes.
    y_train_delta = y_train - train["cnt_lag_1"]

    print("\nDifferenced target - validation only")
    print("-" * 60)

    for name in ["ridge", "hgb"]:
        model = clone(MODELS[name])
        model.fit(X_train, y_train_delta)

        # Convert predicted changes back to ride counts.
        delta_pred = model.predict(X_valid)
        pred = valid["cnt_lag_1"].to_numpy() + delta_pred

        print(
            f"{name + '_delta':25s} "
            f"R2 = {r2_score(y_valid, pred):.4f}  "
            f"MAE = {mean_absolute_error(y_valid, pred):.1f}"
        )


if __name__ == "__main__":
    main()
