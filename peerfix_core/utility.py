from __future__ import annotations

from typing import Callable, Any, Iterable

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .hashing import hash_dataframe
from .seeds import derive_seed
from .splits import SplitRecord

GeneratorFn = Callable[[pd.DataFrame, int, int], pd.DataFrame]


def default_regression_models(seed: int) -> dict[str, Any]:
    return {
        "lr": LinearRegression(),
        "rf": RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=seed,
            n_jobs=1,
        ),
        "gbr": GradientBoostingRegressor(random_state=seed),
        "mlp": Pipeline([
            ("scaler", StandardScaler()),
            ("mlp", MLPRegressor(
                hidden_layer_sizes=(100, 50),
                activation="relu",
                solver="adam",
                alpha=1e-3,
                max_iter=3000,
                early_stopping=True,
                validation_fraction=0.20,
                n_iter_no_change=50,
                random_state=seed,
            )),
        ]),
    }


def _metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
    }


def evaluate_generator_utility(
    real_df: pd.DataFrame,
    *,
    target: str,
    splits: Iterable[SplitRecord],
    generator_name: str,
    generator_fn: GeneratorFn,
    n_synthetic: int = 140,
    master_seed: int = 123,
    scenario: str = "baseline_0pct",
    model_names: tuple[str, ...] = ("lr", "rf", "gbr", "mlp"),
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Leakage-free fold-refit utility evaluation.

    The generator receives only the real training fold. Synthetic data are generated once per
    generator/fold and reused for all fixed downstream models. Scores are computed only after
    out-of-fold predictions are assembled for a complete repeat.

    Downstream-model RNG is deliberately independent of ``generator_name``. Therefore the
    stochastic TRTR baseline for a given scenario/repeat/fold/model is identical across
    generators; generator identity may affect TSTR/AUGTR only through the generated data.
    """
    if target not in real_df.columns:
        raise KeyError(target)
    features = [c for c in real_df.columns if c != target]
    work = real_df.reset_index(drop=False).rename(columns={"index": "__row_id__"})

    pred_rows: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []

    for split in splits:
        train = work.iloc[split.train_idx].copy()
        test = work.iloc[split.test_idx].copy()
        generator_seed = derive_seed(
            master_seed,
            purpose="generator",
            scenario=scenario,
            repeat=split.repeat,
            fold=split.fold,
            generator=generator_name,
        )
        synth = generator_fn(train.drop(columns=["__row_id__"]), n_synthetic, generator_seed)
        if not isinstance(synth, pd.DataFrame) or len(synth) == 0:
            raise RuntimeError(f"generator {generator_name} failed at repeat={split.repeat} fold={split.fold}")
        missing = [c for c in real_df.columns if c not in synth.columns]
        if missing:
            raise ValueError(f"synthetic output missing columns: {missing}")
        synth = synth[real_df.columns].reset_index(drop=True)

        manifest_rows.append({
            "scenario": scenario,
            "repeat": split.repeat,
            "fold": split.fold,
            "generator": generator_name,
            "generator_seed": generator_seed,
            "train_row_ids": train["__row_id__"].astype(int).tolist(),
            "test_row_ids": test["__row_id__"].astype(int).tolist(),
            "synthetic_n": len(synth),
            "synthetic_hash": hash_dataframe(synth),
            "generator_status": "ok",
        })

        Xr, yr = train[features], train[target].to_numpy(float)
        Xt, yt = test[features], test[target].to_numpy(float)
        Xs, ys = synth[features], synth[target].to_numpy(float)
        Xa = pd.concat([Xr, Xs], ignore_index=True)
        ya = np.concatenate([yr, ys])

        for model_name in model_names:
            # Hold stochastic downstream-model initialization constant across generators.
            # Including generator_name here would confound generator comparisons through TRTR.
            model_seed = derive_seed(
                master_seed,
                purpose="downstream",
                scenario=scenario,
                repeat=split.repeat,
                fold=split.fold,
                model=model_name,
            )
            models = default_regression_models(model_seed)
            if model_name not in models:
                raise KeyError(f"unknown model {model_name}")
            regimes = {
                "TRTR": (Xr, yr),
                "TSTR": (Xs, ys),
                "AUGTR": (Xa, ya),
            }
            for regime, (Xfit, yfit) in regimes.items():
                est = clone(models[model_name])
                est.fit(Xfit, yfit)
                pred = np.asarray(est.predict(Xt), dtype=float)
                for rid, y_true, y_hat in zip(test["__row_id__"].astype(int), yt, pred):
                    pred_rows.append({
                        "scenario": scenario,
                        "generator": generator_name,
                        "repeat": split.repeat,
                        "fold": split.fold,
                        "model": model_name,
                        "model_seed": model_seed,
                        "regime": regime,
                        "row_id": int(rid),
                        "y_true": float(y_true),
                        "y_pred": float(y_hat),
                    })

    preds = pd.DataFrame(pred_rows)
    manifest = pd.DataFrame(manifest_rows)
    out_rows: list[dict[str, Any]] = []
    for (repeat, model), g in preds.groupby(["repeat", "model"], sort=True):
        by_regime = {}
        for regime, rg in g.groupby("regime"):
            rg = rg.sort_values("row_id")
            by_regime[regime] = _metrics(rg["y_true"].to_numpy(float), rg["y_pred"].to_numpy(float))
        if set(by_regime) != {"TRTR", "TSTR", "AUGTR"}:
            raise RuntimeError(f"incomplete regime set at repeat {repeat}, model {model}")
        row = {
            "scenario": scenario,
            "generator": generator_name,
            "repeat": int(repeat),
            "model": model,
        }
        for regime in ["TRTR", "TSTR", "AUGTR"]:
            for metric, value in by_regime[regime].items():
                row[f"{regime}_{metric}"] = value
        row["delta_r2"] = row["TSTR_r2"] - row["TRTR_r2"]
        row["augmentation_delta_r2"] = row["AUGTR_r2"] - row["TRTR_r2"]
        out_rows.append(row)
    return pd.DataFrame(out_rows), manifest
