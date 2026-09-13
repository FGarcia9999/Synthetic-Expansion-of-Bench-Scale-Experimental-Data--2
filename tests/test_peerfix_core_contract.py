from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from peerfix_core.seeds import derive_seed
from peerfix_core.splits import repeated_row_kfold, repeated_group_condition_kfold
from peerfix_core.utility import evaluate_generator_utility
from peerfix_core.icd import evaluate_icd_matched_n
from peerfix_core.dcr import compute_dcr, summarize_dcr
from peerfix_core.hashing import sha256_file

DERIVATION_DATA = Path("data/derivation/peerfix2_historical_manuscript_dataset.csv")
DERIVATION_SHA256 = "c33869c2cb6e5bd58d81d9dc2a70409c25b5147d4348d7fe5753e02beee5cf07"


def make_real() -> pd.DataFrame:
    rows = []
    for a in [0.0, 100.0]:
        for b in [0.0, 0.5]:
            for c in [0.2, 0.6]:
                for d in [0.5, 1.5]:
                    y = 50 - 2.0*d + 0.5*b - 0.4*c + 0.01*a
                    rows.append((a,b,c,d,y))
    for y in [48.0, 48.2, 47.8, 48.1]:
        rows.append((50.0, 0.25, 0.4, 1.0, y))
    return pd.DataFrame(rows, columns=[
        "seawater_vv","urea_pv","ammonium_sulfate_pv","kh2po4_pv","surface_tension_mNm"
    ])


def bootstrap_generator(train: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(train), size=n, replace=True)
    return train.iloc[idx].reset_index(drop=True).copy()


def test_source_confirmed_derivation_dataset_bytes_are_immutable():
    assert DERIVATION_DATA.exists()
    assert sha256_file(DERIVATION_DATA) == DERIVATION_SHA256


def test_seed_is_stable_and_token_sensitive():
    a = derive_seed(123, purpose="x", repeat=1, fold=2, generator="ctgan")
    b = derive_seed(123, purpose="x", repeat=1, fold=2, generator="ctgan")
    c = derive_seed(123, purpose="x", repeat=1, fold=3, generator="ctgan")
    assert a == b
    assert a != c
    assert 0 < a <= 0x7FFFFFFF


def test_row_cv_has_exact_repeat_coverage():
    splits = list(repeated_row_kfold(20, n_splits=5, n_repeats=10, seed=123))
    assert len(splits) == 50
    for r in range(1, 11):
        tests = np.concatenate([s.test_idx for s in splits if s.repeat == r])
        assert sorted(tests.tolist()) == list(range(20))


def test_grouped_cv_never_splits_a_condition():
    real = make_real()
    groups = real[["seawater_vv","urea_pv","ammonium_sulfate_pv","kh2po4_pv"]].astype(str).agg("|".join, axis=1)
    splits = list(repeated_group_condition_kfold(groups, n_splits=5, n_repeats=3, master_seed=123))
    assert len(splits) == 15
    for s in splits:
        tr_g = set(groups.iloc[s.train_idx])
        te_g = set(groups.iloc[s.test_idx])
        assert tr_g.isdisjoint(te_g)


def test_utility_generator_sees_training_only():
    real = make_real()
    splits = list(repeated_row_kfold(len(real), n_splits=5, n_repeats=2, seed=123))
    metrics, manifest = evaluate_generator_utility(
        real,
        target="surface_tension_mNm",
        splits=splits,
        generator_name="test_bootstrap",
        generator_fn=bootstrap_generator,
        n_synthetic=40,
        model_names=("lr",),
    )
    assert len(metrics) == 2
    assert set(["TRTR_r2","TSTR_r2","AUGTR_r2","delta_r2","augmentation_delta_r2"]).issubset(metrics.columns)
    assert len(manifest) == 10
    for _, row in manifest.iterrows():
        assert set(row.train_row_ids).isdisjoint(set(row.test_row_ids))


def test_trtr_stochastic_baseline_is_identical_across_generator_names():
    """Generator identity must not change the stochastic real-only baseline."""
    real = make_real()
    splits = list(repeated_row_kfold(len(real), n_splits=5, n_repeats=2, seed=123))
    a, _ = evaluate_generator_utility(
        real,
        target="surface_tension_mNm",
        splits=splits,
        generator_name="generator_A",
        generator_fn=bootstrap_generator,
        n_synthetic=40,
        model_names=("rf",),
    )
    b, _ = evaluate_generator_utility(
        real,
        target="surface_tension_mNm",
        splits=splits,
        generator_name="generator_B",
        generator_fn=bootstrap_generator,
        n_synthetic=40,
        model_names=("rf",),
    )
    cols = ["TRTR_r2", "TRTR_mae", "TRTR_rmse"]
    np.testing.assert_allclose(a[cols].to_numpy(float), b[cols].to_numpy(float), rtol=0.0, atol=0.0)


def test_icd_matched_n_runs_and_is_bounded_above_one():
    real = make_real()
    rng = np.random.default_rng(7)
    synth = real.sample(n=140, replace=True, random_state=7).reset_index(drop=True).copy()
    synth["surface_tension_mNm"] += rng.normal(0, 0.15, len(synth))
    res = evaluate_icd_matched_n(
        real, synth,
        target="surface_tension_mNm",
        factors=["seawater_vv","urea_pv","ammonium_sulfate_pv","kh2po4_pv"],
        reference_terms=["kh2po4_pv"],
        n_subsamples=50,
        master_seed=123,
    )
    assert 0 <= res["mean_S"] <= 1
    assert 0 <= res["mean_M"] <= 1
    assert 0 <= res["mean_D"] <= 1
    assert 0 <= res["spurious_rate"] <= 1
    assert res["ICD"] <= 1
    assert len(res["effects"]) == 1


def test_dcr_is_diagnostic_and_finite():
    real = make_real()
    synth = real.sample(n=30, replace=True, random_state=1).reset_index(drop=True)
    features = ["seawater_vv","urea_pv","ammonium_sulfate_pv","kh2po4_pv"]
    d = compute_dcr(real, synth, features)
    s = summarize_dcr(d)
    assert len(d) == 30
    assert np.isfinite(d).all()
    assert 0 <= s["fraction_below_0p10"] <= 1
