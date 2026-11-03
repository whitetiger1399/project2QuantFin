
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "artifacts" / "cross_market" / "runs"


def main():
    final_path = sorted(
        RUNS.glob("cm_final_test_*/predictions.parquet")
    )[-1]

    slice_path = sorted(
        RUNS.glob("cm_final_slice_*/predictions.parquet")
    )[-1]

    final = pd.read_parquet(final_path)
    subset = pd.read_parquet(slice_path)

    keys = ["decision_date", "asset", "config_id"]

    merged = subset.merge(
        final,
        on=keys,
        how="left",
        suffixes=("_slice", "_final"),
        validate="one_to_one",
        indicator=True,
    )

    unmatched = int((merged["_merge"] != "both").sum())

    print("Unmatched rows:", unmatched)

    if unmatched:
        raise AssertionError("Slice contains rows absent from final run.")

    for column in [
        "prediction",
        "target_oc_return",
        "benchmark_nifty_it_cc_return",
        "benchmark_nifty50_cc_return",
        "benchmark_cohort_ew_oc_return",
    ]:
        np.testing.assert_allclose(
            merged[f"{column}_slice"],
            merged[f"{column}_final"],
            rtol=0,
            atol=0,
            equal_nan=True,
        )

    manifest = json.loads(
        (slice_path.parent / "manifest.json").read_text()
    )

    print("Source run:", manifest.get("source_run_id"))
    print("Model reselection:", manifest.get("model_reselection_performed"))
    print("Refit performed:", manifest.get("refit_performed"))

    assert manifest.get("model_reselection_performed") is False
    assert manifest.get("refit_performed") is False

    print("PASS: Derived slice matches the frozen final run.")


if __name__ == "__main__":
    main()
