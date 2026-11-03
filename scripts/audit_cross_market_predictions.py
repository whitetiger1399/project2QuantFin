
from pathlib import Path
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "artifacts" / "cross_market" / "runs"


def audit_run(path: Path):
    df = pd.read_parquet(path)

    print(f"\nRUN: {path.parent.name}")
    print(f"Rows: {len(df):,}")

    required = [
        "decision_date",
        "asset",
        "prediction",
        "config_id",
        "feature_set",
        "family",
    ]

    missing = set(required) - set(df.columns)

    if missing:
        print(f"FAIL: Missing columns: {missing}")
        return

    keys = ["decision_date", "asset", "config_id"]

    duplicates = df.duplicated(subset=keys).sum()
    print(f"Duplicate prediction keys: {duplicates}")

    prediction = pd.to_numeric(
        df["prediction"], errors="coerce"
    )

    invalid = (~np.isfinite(prediction)).sum()
    print(f"Nonfinite predictions: {invalid}")

    print("Decision range:",
          df["decision_date"].min(),
          "to",
          df["decision_date"].max())

    print("Unique assets:", df["asset"].nunique())
    print("Unique configurations:", df["config_id"].nunique())

    print("\nFeature sets:")
    print(df["feature_set"].value_counts())

    print("\nModel families:")
    print(df["family"].value_counts())

    if "target_oc_return" in df.columns:
        print(
            "Missing realized targets:",
            df["target_oc_return"].isna().sum()
        )


def main():
    paths = sorted(
        RUNS_DIR.glob("cm_*/predictions.parquet")
    )

    if not paths:
        raise FileNotFoundError(
            f"No predictions found in {RUNS_DIR}"
        )

    for path in paths:
        audit_run(path)


if __name__ == "__main__":
    main()
