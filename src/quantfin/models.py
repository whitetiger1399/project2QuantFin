"""Auditable model registry for daily return prediction."""

from __future__ import annotations

from itertools import product
from typing import Any

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import ElasticNet, Lasso, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from quantfin.io import stable_object_hash


class HistoricalMeanRegressor(BaseEstimator, RegressorMixin):
    def fit(self, X: np.ndarray, y: np.ndarray) -> "HistoricalMeanRegressor":
        self.mean_ = float(np.mean(y))
        self.n_features_in_ = X.shape[1]
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.full(X.shape[0], self.mean_, dtype=float)


class NormalizedRidge(BaseEstimator, RegressorMixin):
    """Ridge with mean-squared-error penalty lambda independent of sample size."""

    def __init__(self, penalty: float = 1.0) -> None:
        self.penalty = penalty

    def fit(self, X: np.ndarray, y: np.ndarray) -> "NormalizedRidge":
        self.model_ = Ridge(alpha=float(self.penalty) * len(y), fit_intercept=True, solver="auto")
        self.model_.fit(X, y)
        self.coef_ = self.model_.coef_
        self.intercept_ = self.model_.intercept_
        self.n_features_in_ = X.shape[1]
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model_.predict(X)


def _grid(parameters: dict[str, list[Any]]) -> list[dict[str, Any]]:
    keys = list(parameters)
    return [dict(zip(keys, values)) for values in product(*(parameters[key] for key in keys))]


def enumerate_model_configs(model_config: dict[str, Any], profile: str) -> list[dict[str, Any]]:
    if profile not in model_config["profiles"]:
        raise ValueError(f"Unknown model profile: {profile}")
    selected = model_config["profiles"][profile]
    families = selected["families"]
    configurations: list[dict[str, Any]] = []

    for family in families:
        if family in {"historical_mean", "autoregression"}:
            family_parameters = [{}]
        elif family == "rff_ridge":
            family_parameters = [
                {"n_components": components, "penalty": penalty, "gamma_scale": gamma_scale}
                for components, penalty, gamma_scale in product(
                    selected["rff_components"],
                    selected["rff_alphas"],
                    model_config["grids"]["rff_ridge"]["gamma_scale"],
                )
            ]
        else:
            family_parameters = _grid(model_config["grids"][family])

        for parameters in family_parameters:
            payload = {"family": family, "parameters": parameters}
            configurations.append(
                {
                    **payload,
                    "config_id": f"{family}_{stable_object_hash(payload)[:10]}",
                }
            )
    return configurations


def build_estimator(
    configuration: dict[str, Any],
    *,
    random_seed: int,
    n_jobs: int,
    input_feature_count: int,
) -> tuple[BaseEstimator, list[str] | None]:
    family = configuration["family"]
    parameters = configuration["parameters"]
    impute_scale = [("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]

    if family == "historical_mean":
        return HistoricalMeanRegressor(), None
    if family == "autoregression":
        columns = ["spy_log_return_lag_0", "spy_log_return_lag_1", "spy_log_return_lag_2"]
        return Pipeline([*impute_scale, ("model", Ridge(alpha=0.0, solver="svd"))]), columns
    if family == "ridge":
        return Pipeline([*impute_scale, ("model", NormalizedRidge(parameters["alpha"]))]), None
    if family == "lasso":
        return Pipeline(
            [
                *impute_scale,
                (
                    "model",
                    Lasso(
                        alpha=parameters["alpha"],
                        max_iter=20_000,
                        tol=1e-7,
                        selection="cyclic",
                        random_state=random_seed,
                    ),
                ),
            ]
        ), None
    if family == "elastic_net":
        return Pipeline(
            [
                *impute_scale,
                (
                    "model",
                    ElasticNet(
                        alpha=parameters["alpha"],
                        l1_ratio=parameters["l1_ratio"],
                        max_iter=20_000,
                        tol=1e-7,
                        selection="cyclic",
                        random_state=random_seed,
                    ),
                ),
            ]
        ), None
    if family == "pca_ridge":
        return Pipeline(
            [
                *impute_scale,
                ("pca", PCA(n_components=parameters["n_components"], random_state=random_seed)),
                ("model", NormalizedRidge(parameters["alpha"])),
            ]
        ), None
    if family in {"random_forest", "extra_trees"}:
        ensemble_class = RandomForestRegressor if family == "random_forest" else ExtraTreesRegressor
        model = ensemble_class(
            n_estimators=parameters["n_estimators"],
            max_depth=parameters["max_depth"],
            min_samples_leaf=parameters["min_samples_leaf"],
            max_features=parameters["max_features"],
            n_jobs=n_jobs,
            random_state=random_seed,
        )
        return Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", model)]), None
    if family == "hist_gradient_boosting":
        model = HistGradientBoostingRegressor(
            max_leaf_nodes=parameters["max_leaf_nodes"],
            l2_regularization=parameters["l2_regularization"],
            learning_rate=parameters["learning_rate"],
            max_iter=parameters["max_iter"],
            min_samples_leaf=parameters["min_samples_leaf"],
            early_stopping=False,
            random_state=random_seed,
        )
        return Pipeline([("imputer", SimpleImputer(strategy="median")), ("model", model)]), None
    if family == "rff_ridge":
        gamma = float(parameters["gamma_scale"]) / max(1, input_feature_count)
        return Pipeline(
            [
                *impute_scale,
                (
                    "rff",
                    RBFSampler(
                        gamma=gamma,
                        n_components=parameters["n_components"],
                        random_state=random_seed,
                    ),
                ),
                ("model", NormalizedRidge(parameters["penalty"])),
            ]
        ), None
    raise ValueError(f"Unsupported model family: {family}")


def model_complexity(estimator: BaseEstimator, configuration: dict[str, Any], input_count: int) -> dict[str, Any]:
    family = configuration["family"]
    parameters = configuration["parameters"]
    if family == "historical_mean":
        return {"trainable_parameters": 1, "approximation_features": 1}
    if family == "autoregression":
        return {"trainable_parameters": 4, "approximation_features": 3}
    if family in {"ridge", "lasso", "elastic_net"}:
        return {"trainable_parameters": input_count + 1, "approximation_features": input_count}
    if family == "pca_ridge":
        components = int(parameters["n_components"])
        return {
            "trainable_parameters": components + 1,
            "approximation_features": components,
            "pca_loading_values": components * input_count,
        }
    if family == "rff_ridge":
        components = int(parameters["n_components"])
        return {
            "trainable_parameters": components + 1,
            "approximation_features": components,
            "random_projection_values_not_trained": components * input_count,
        }
    if family in {"random_forest", "extra_trees"}:
        model = estimator.named_steps["model"]
        nodes = int(sum(tree.tree_.node_count for tree in model.estimators_))
        leaves = int(sum(tree.tree_.n_leaves for tree in model.estimators_))
        return {"trainable_parameters": leaves, "tree_nodes": nodes, "tree_leaves": leaves}
    if family == "hist_gradient_boosting":
        model = estimator.named_steps["model"]
        return {
            "trainable_parameters": int(model.n_iter_ * parameters["max_leaf_nodes"]),
            "boosting_iterations": int(model.n_iter_),
        }
    return {"trainable_parameters": None, "approximation_features": None}


def extract_feature_diagnostics(
    estimator: BaseEstimator,
    configuration: dict[str, Any],
    feature_names: list[str],
) -> list[dict[str, Any]]:
    """Return standardized coefficients or native tree importances when meaningful."""
    family = configuration["family"]
    if family in {"historical_mean", "rff_ridge", "hist_gradient_boosting"}:
        return []
    model = estimator.named_steps["model"]
    if family in {"autoregression", "ridge", "lasso", "elastic_net"}:
        coefficients = np.asarray(model.coef_, dtype=float).ravel()
        measure = "standardized_coefficient"
    elif family == "pca_ridge":
        pca = estimator.named_steps["pca"]
        coefficients = np.asarray(pca.components_.T @ np.asarray(model.coef_).ravel())
        measure = "projected_standardized_coefficient"
    elif family in {"random_forest", "extra_trees"}:
        coefficients = np.asarray(model.feature_importances_, dtype=float)
        measure = "impurity_importance"
    else:
        return []
    if len(coefficients) != len(feature_names):
        return []
    return [
        {"feature": name, "value": float(value), "measure": measure}
        for name, value in zip(feature_names, coefficients)
    ]

