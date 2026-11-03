from pathlib import Path
import argparse
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def find_latest_dataset() -> Path:
    """Find the latest generated features_and_labels.parquet."""

    datasets = list(
        PROCESSED_DIR.glob(
            "features_*/features_and_labels.parquet"
        )
    )

    if not datasets:
        raise FileNotFoundError(
            f"No feature datasets found in {PROCESSED_DIR}"
        )

    # Dataset names contain timestamps in YYYYMMDDTHHMMSSZ format.
    # Sort by timestamp rather than filesystem modification time.
    return max(
        datasets,
        key=lambda path: path.parent.name.split("_")[2],
    )


def audit_dataset(path: Path) -> None:
    print(f"\nAuditing dataset: {path}")
    print("=" * 80)

    df = pd.read_parquet(path)
    inspect_temporal_violations(df)

    print(f"\nRows and columns: {df.shape}")

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nMissing values (top 30):")
    print(
        df.isna()
        .sum()
        .sort_values(ascending=False)
        .head(30)
    )

    print("\nDuplicate rows:", df.duplicated().sum())

    print("\nDate columns:")
    for col in df.columns:
        if "date" in col.lower() or "session" in col.lower():
            print(col, df[col].min(), df[col].max())

    if "split" in df.columns:
        print("\nDataset splits:")
        print(df["split"].value_counts(dropna=False))


def inspect_temporal_violations(df: pd.DataFrame) -> None:
    """Identify rows violating signal, entry, and label chronology."""


    required = [
        "signal_session",
        "entry_session",
        "label_end_session",
        "label_available_session",
        "target_return",
    ]

    if all(col in df.columns for col in required):
        print("\nTemporal ordering audit:")

        signal = pd.to_datetime(df["signal_session"])
        entry = pd.to_datetime(df["entry_session"])
        label_end = pd.to_datetime(df["label_end_session"])
        available = pd.to_datetime(df["label_available_session"])

        dates = [signal, entry, label_end, available]

        complete = (
            df["target_return"].notna()
            & pd.concat(dates, axis=1).notna().all(axis=1)
        )

        partial = ~complete

        print(f"Complete observations: {int(complete.sum())}")
        print(f"Incomplete observations: {int(partial.sum())}")

        checks = {
            "signal < entry": signal < entry,
            "entry < label_end": entry < label_end,
            "label_end <= available": label_end <= available,
        }

        failures = 0

        for name, valid in checks.items():
            invalid = complete & ~valid
            count = int(invalid.sum())
            failures += count
            status = "PASS" if count == 0 else "FAIL"
            print(f"{status}: {name} ({count} violations)")

        print("\nIncomplete observations:")
        print(
            df.loc[partial, required + ["split"]]
            .to_string(index=False)
        )

        if failures == 0:
            print("\nPASS: All complete observations satisfy temporal ordering.")
        else:
            print("\nFAIL: Temporal violations exist in complete observations.")

        print("\nIncomplete observations by split:")

    incomplete = df["target_return"].isna()

    print(
        df.loc[incomplete, "split"]
        .value_counts(dropna=False)
    )

    invalid_training = incomplete & df["split"].isin(
        ["initial_train", "screening", "confirmation"]
    )

    if invalid_training.any():
        print(
            "FAIL: Incomplete observations found "
            "in training or model-selection periods."
        )
    else:
        print(
            "PASS: No incomplete observations in "
            "training or model-selection periods."
        )


def main():
    parser = argparse.ArgumentParser(
        description="Audit generated feature datasets."
    )

    parser.add_argument(
        "--dataset",
        type=Path,
        default=None,
        help="Optional explicit Parquet dataset path.",
    )

    args = parser.parse_args()

    path = (
        args.dataset.resolve()
        if args.dataset
        else find_latest_dataset()
    )

    if not path.is_file():
        raise FileNotFoundError(path)

    audit_dataset(path)


if __name__ == "__main__":
    main()
