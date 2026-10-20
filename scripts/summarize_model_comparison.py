"""Create a reproducible comparison table and plot from completed model runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from quantfin.io import stable_object_hash


ROOT = Path(__file__).resolve().parents[1]


def _run_dir(run_id: str) -> Path:
    directory = ROOT / "artifacts" / "runs" / run_id
    if not (directory / "run_manifest.json").is_file():
        raise FileNotFoundError(f"Completed run manifest not found: {directory}")
    manifest = json.loads((directory / "run_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status") != "complete":
        raise ValueError(f"Run is not complete: {run_id}")
    return directory


def _load_metrics(run_id: str, stage: str) -> pd.DataFrame:
    directory = _run_dir(run_id)
    metrics = pd.read_csv(directory / "config_metrics.csv")
    metrics.insert(0, "stage", stage)
    metrics.insert(1, "run_id", run_id)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screening-run-id", required=True)
    parser.add_argument("--confirmation-run-id", required=True)
    parser.add_argument("--output-root", default="artifacts/research/model_comparisons")
    args = parser.parse_args()

    screening = _load_metrics(args.screening_run_id, "screening")
    confirmation = _load_metrics(args.confirmation_run_id, "confirmation")
    metrics = pd.concat([screening, confirmation], ignore_index=True)
    metrics["rank_within_stage"] = metrics.groupby("stage")["median_annual_net_sharpe"].rank(
        ascending=False, method="min"
    )
    metrics = metrics.sort_values(["stage", "rank_within_stage", "family", "config_id"])

    output_id = "comparison_" + stable_object_hash(
        {"screening": args.screening_run_id, "confirmation": args.confirmation_run_id}
    )[:12]
    output = ROOT / args.output_root / output_id
    output.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output / "comparison_metrics.csv", index=False)

    selected = metrics.loc[
        metrics["family"].isin(["historical_mean", "autoregression"])
        | metrics["rank_within_stage"].le(10)
    ].copy()
    selected.to_csv(output / "comparison_top10.csv", index=False)

    plot_data = metrics.loc[metrics["rank_within_stage"].le(10)].copy()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5), constrained_layout=True)
    for stage, axis in zip(["screening", "confirmation"], axes):
        frame = plot_data.loc[plot_data["stage"].eq(stage)].sort_values("median_annual_net_sharpe")
        if frame.empty:
            axis.set_visible(False)
            continue
        labels = frame["family"].astype(str) + "\n" + frame["config_id"].str[-10:]
        axis.barh(labels, frame["median_annual_net_sharpe"], color="#2f657b")
        axis.axvline(0.0, color="#555555", linewidth=0.8)
        axis.set_title(stage.capitalize())
        axis.set_xlabel("Median annual net Sharpe")
        axis.tick_params(axis="y", labelsize=7)
    fig.suptitle("Comparative model screening and confirmation")
    fig.savefig(output / "comparison_median_sharpe.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    summary = {
        "screening_run_id": args.screening_run_id,
        "confirmation_run_id": args.confirmation_run_id,
        "rows": int(len(metrics)),
        "families": sorted(metrics["family"].unique().tolist()),
        "output_directory": str(output),
        "final_test_run": None,
        "interpretation": "Comparison is limited to screening and confirmation; the frozen final holdout is not rerun.",
    }
    (output / "comparison_manifest.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
