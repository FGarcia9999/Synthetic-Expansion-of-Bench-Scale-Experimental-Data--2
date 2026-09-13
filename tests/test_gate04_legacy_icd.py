from __future__ import annotations

import pandas as pd

from peerfix_core.icd import evaluate_icd_legacy_full_n


def _real() -> pd.DataFrame:
    rows = [
        (0,0.0,0.2,0.5,45.05),(100,0.0,0.2,0.5,46.47),
        (0,0.5,0.2,0.5,53.30),(100,0.5,0.2,0.5,53.57),
        (0,0.0,0.6,0.5,52.27),(100,0.0,0.6,0.5,53.24),
        (0,0.5,0.6,0.5,50.58),(100,0.5,0.6,0.5,46.67),
        (0,0.0,0.2,1.5,47.54),(100,0.0,0.2,1.5,43.76),
        (0,0.5,0.2,1.5,47.61),(100,0.5,0.2,1.5,47.58),
        (0,0.0,0.6,1.5,42.35),(100,0.0,0.6,1.5,50.98),
        (0,0.5,0.6,1.5,42.22),(100,0.5,0.6,1.5,48.44),
        (50,0.25,0.4,1.0,49.44),(50,0.25,0.4,1.0,44.26),
        (50,0.25,0.4,1.0,47.75),(50,0.25,0.4,1.0,49.21),
    ]
    return pd.DataFrame(rows, columns=[
        "seawater_vv","urea_pv","ammonium_sulfate_pv","kh2po4_pv","surface_tension_mNm"
    ])


def test_legacy_icd_identical_data_is_bounded_and_perfect_on_reference_components():
    real = _real()
    res = evaluate_icd_legacy_full_n(
        real,
        real.copy(),
        target="surface_tension_mNm",
        factors=["seawater_vv","urea_pv","ammonium_sulfate_pv","kh2po4_pv"],
        reference_terms=["kh2po4_pv"],
    )
    assert res["historical_comparability_only"] is True
    assert res["mean_S"] == 1.0
    assert res["mean_M"] == 1.0
    assert res["mean_D"] == 1.0
    assert res["spurious_rate"] == 0.0
    assert res["ICD"] == 1.0


def test_legacy_icd_secondary_reference_set_executes():
    real = _real()
    synth = pd.concat([real] * 7, ignore_index=True).iloc[:140].copy()
    res = evaluate_icd_legacy_full_n(
        real,
        synth,
        target="surface_tension_mNm",
        factors=["seawater_vv","urea_pv","ammonium_sulfate_pv","kh2po4_pv"],
        reference_terms=["kh2po4_pv", "urea_pv:ammonium_sulfate_pv"],
    )
    assert len(res["effects"]) == 2
    assert res["n_synthetic"] == 140
    assert res["ICD"] <= 1.0
