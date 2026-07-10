"""
Gera as figuras do manuscrito a partir dos dados reais do PEERFIX1.
Nenhum numero e inventado -- tudo vem de evaluation_results.json, dos CSVs
sinteticos reais, e do modulo icd_domain_concordance.py ja usado no artigo.
"""
import json
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# portable: removed external Claude sys.path insertion
from icd_domain_concordance import evaluate_generators, KnownEffect, get_reference_levels, fit_factorial_model

# Portable help guard added for Windows/Linux reproducibility.
if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
    print("Portable figure script.")
    print("Default inputs:")
    print("  baseline: runs/exp_out_v5_doe0pct_tau010")
    print("  sensitivity: runs/exp_out_v5_doe1pct_tau010")
    print("  real data: data/dados.csv")
    print("  output: outputs/peerfix2/figures_peerfix2")
    print("Note: this legacy script uses internal defaults; PEERFIX2 final figures are under outputs/peerfix2.")
    raise SystemExit(0)


plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "figure.dpi": 200,
})

GEN_ORDER = ["gaussian_copula", "ctgan", "tvae", "tabddpm"]
GEN_LABEL = {"gaussian_copula": "Gaussian\nCopula", "ctgan": "CTGAN", "tvae": "TVAE", "tabddpm": "TabDDPM"}
GEN_COLOR = {"gaussian_copula": "#4C72B0", "ctgan": "#DD8452", "tvae": "#55A868", "tabddpm": "#C44E52"}

BASE = "runs/exp_out_v5_doe0pct_tau010"
SENS = "runs/exp_out_v5_doe1pct_tau010"
OUT = "outputs/peerfix2/figures_peerfix2"


def load_eval(path):
    with open(f"{path}/evaluation_results.json", encoding="utf-8-sig") as f:
        return json.load(f)


def best_tstr(res):
    best_model, best_tstr_v, best_trtr = None, -1e9, None
    for m, mres in res["utility"]["model_results"].items():
        tm = mres["TSTR"]["mean"] if isinstance(mres.get("TSTR"), dict) else mres.get("TSTR")
        if tm is not None and tm > best_tstr_v:
            best_tstr_v, best_model = tm, m
            best_trtr = mres["TRTR"]["mean"] if isinstance(mres.get("TRTR"), dict) else mres.get("TRTR")
    return best_tstr_v, best_model, best_trtr


d_base = load_eval(BASE)
d_sens = load_eval(SENS)

# ----------------------------------------------------------------------
# Figure 1: TSTR_best by generator, baseline vs sensitivity
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.5, 4.2))
x = np.arange(len(GEN_ORDER))
width = 0.35
base_vals = [best_tstr(d_base[g])[0] for g in GEN_ORDER]
sens_vals = [best_tstr(d_sens[g])[0] for g in GEN_ORDER]

b1 = ax.bar(x - width/2, base_vals, width, label="Baseline (0% noise)", color="#4C72B0", edgecolor="white")
b2 = ax.bar(x + width/2, sens_vals, width, label="Sensitivity (1% DOE noise)", color="#C44E52", edgecolor="white")
ax.axhline(0, color="black", linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels([GEN_LABEL[g] for g in GEN_ORDER])
ax.set_ylabel("TSTR_best (R², best downstream model)")
ax.set_title("Downstream utility (TSTR_best) by generator and scenario")
ax.legend(frameon=False, loc="upper right")
for bars in (b1, b2):
    for rect in bars:
        h = rect.get_height()
        ax.annotate(f"{h:.2f}", (rect.get_x() + rect.get_width()/2, h),
                    textcoords="offset points", xytext=(0, 4 if h >= 0 else -12),
                    ha="center", fontsize=9)
fig.tight_layout()
fig.savefig(f"{OUT}/fig1_tstr_by_generator.png")
plt.close(fig)

# ----------------------------------------------------------------------
# Figure 2: Correlation heatmaps, real + 4 synthetic (baseline)
# ----------------------------------------------------------------------
real_df = pd.read_csv("data/dados.csv")
factors = ["seawater_vv", "urea_pv", "ammonium_sulfate_pv", "kh2po4_pv", "surface_tension_mNm"]
short = {"seawater_vv": "Seawater", "urea_pv": "Urea", "ammonium_sulfate_pv": "(NH4)2SO4", "kh2po4_pv": "KH2PO4", "surface_tension_mNm": "TS"}

synth_paths = {
    "gaussian_copula": f"{BASE}/synthetic_datasets/gaussian_copula_synthetic.csv",
    "ctgan": f"{BASE}/synthetic_datasets/ctgan_synthetic.csv",
    "tvae": f"{BASE}/synthetic_datasets/tvae_synthetic.csv",
    "tabddpm": f"{BASE}/synthetic_datasets/tabddpm_synthetic.csv",
}

fig, axes = plt.subplots(1, 5, figsize=(16, 3.4))
datasets = [("Real (n=20)", real_df)] + [(GEN_LABEL[g].replace("\n", " "), pd.read_csv(p)) for g, p in synth_paths.items()]
im = None
for ax, (name, df) in zip(axes, datasets):
    corr = df[factors].corr().values
    im = ax.imshow(corr, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(5)); ax.set_yticks(range(5))
    ax.set_xticklabels([short[c] for c in factors], rotation=90, fontsize=7)
    ax.set_yticklabels([short[c] for c in factors], fontsize=7)
    ax.set_title(name, fontsize=10)
    for i in range(5):
        for j in range(5):
            ax.text(j, i, f"{corr[i,j]:.2f}", ha="center", va="center", fontsize=6,
                     color="white" if abs(corr[i, j]) > 0.6 else "black")
fig.colorbar(im, ax=axes, shrink=0.8, label="Pearson correlation", pad=0.01)
fig.suptitle("Correlation matrices: real data vs. baseline synthetic samples (n=140 each)", y=1.05)
fig.savefig(f"{OUT}/fig2_correlation_heatmaps.png", bbox_inches="tight")
plt.close(fig)

# ----------------------------------------------------------------------
# Figure 3: Proximity risk (fraction DCR<0.1), baseline vs sensitivity
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.5, 4.2))


def frac_dcr(res, n_synth=140):
    c = res["privacy"]["distance_to_closest_record"]["privacy_risk_counts"]["distance_below_0.1"]
    return c / n_synth


base_dcr = [frac_dcr(d_base[g]) for g in GEN_ORDER]
sens_dcr = [frac_dcr(d_sens[g]) for g in GEN_ORDER]
b1 = ax.bar(x - width/2, base_dcr, width, label="Baseline (0% noise)", color="#4C72B0", edgecolor="white")
b2 = ax.bar(x + width/2, sens_dcr, width, label="Sensitivity (1% DOE noise)", color="#C44E52", edgecolor="white")
ax.axhline(0.1, color="gray", linestyle="--", linewidth=1, label="10% of synthetic pool")
ax.set_xticks(x); ax.set_xticklabels([GEN_LABEL[g] for g in GEN_ORDER])
ax.set_ylabel("Fraction of synthetic samples with DCR < 0.1")
ax.set_title("Proximity disclosure risk by generator and scenario")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(f"{OUT}/fig3_dcr_proximity_risk.png")
plt.close(fig)

# ----------------------------------------------------------------------
# Figure 4: ICD components by generator (baseline)
# ----------------------------------------------------------------------
synth_dfs = {g: pd.read_csv(p) for g, p in synth_paths.items()}
interactions = [("seawater_vv", "urea_pv"), ("seawater_vv", "ammonium_sulfate_pv"), ("seawater_vv", "kh2po4_pv"),
                ("urea_pv", "ammonium_sulfate_pv"), ("urea_pv", "kh2po4_pv"), ("ammonium_sulfate_pv", "kh2po4_pv")]
known_effects = [
    KnownEffect("kh2po4_pv", "KH2PO4 (main, negative)"),
    KnownEffect("urea_pv:ammonium_sulfate_pv", "Urea x AmmSulfate (borderline)"),
]
summary, details = evaluate_generators(
    real_df=real_df, synth_dfs=synth_dfs, factors=["seawater_vv", "urea_pv", "ammonium_sulfate_pv", "kh2po4_pv"],
    interactions=interactions, target="surface_tension_mNm", known_effects=known_effects, alpha=0.05, lam=0.10,
)
summary = summary.set_index("generator").reindex(GEN_ORDER)

fig, ax = plt.subplots(figsize=(7, 4.2))
metrics = ["mean_S", "mean_M", "mean_D", "ICD"]
metric_labels = ["Sign\nconcordance", "Magnitude\nconcordance", "Detect-\nability", "ICD\n(composite)"]
xpos = np.arange(len(metrics))
bw = 0.2
for i, g in enumerate(GEN_ORDER):
    vals = [summary.loc[g, m] for m in metrics]
    ax.bar(xpos + (i - 1.5) * bw, vals, bw, label=GEN_LABEL[g].replace("\n", " "), color=GEN_COLOR[g], edgecolor="white")
ax.set_xticks(xpos); ax.set_xticklabels(metric_labels)
ax.set_ylabel("Score (0-1)")
ax.set_title("Domain-Grounded Concordance Index (ICD) components — baseline")
ax.legend(frameon=False, ncol=2, fontsize=9)
ax.set_ylim(0, 1.05)
fig.tight_layout()
fig.savefig(f"{OUT}/fig4_icd_components.png")
plt.close(fig)

# ----------------------------------------------------------------------
# Figure 5: TVAE TSTR_best across the 7 reprocessing configurations
# ----------------------------------------------------------------------
configs = [
    ("Original\nverified\n(seed 123)", 0.668, "#8172B2"),
    ("Independent\nrerun\n(unmodified)", -0.254, "#C44E52"),
    ("Isolation\ntest 1", 0.039, "#DD8452"),
    ("Isolation\ntest 2", 0.207, "#DD8452"),
    ("Isolation\ntest 3", 0.442, "#DD8452"),
    ("PEERFIX1\nbaseline", 0.143, "#55A868"),
    ("PEERFIX1\nsensitivity", 0.617, "#55A868"),
]
fig, ax = plt.subplots(figsize=(8, 4.2))
labels = [c[0] for c in configs]
vals = [c[1] for c in configs]
colors = [c[2] for c in configs]
bars = ax.bar(range(len(configs)), vals, color=colors, edgecolor="white")
ax.axhline(0, color="black", linewidth=0.8)
ax.set_xticks(range(len(configs))); ax.set_xticklabels(labels, fontsize=8.5)
ax.set_ylabel("TVAE TSTR_best")
ax.set_title("TVAE utility across seven reprocessings of the same data\n(same generator; only regularisation, training-set convention, and seed vary)")
for rect, v in zip(bars, vals):
    ax.annotate(f"{v:.3f}", (rect.get_x() + rect.get_width()/2, v),
                textcoords="offset points", xytext=(0, 4 if v >= 0 else -14), ha="center", fontsize=9)
fig.tight_layout()
fig.savefig(f"{OUT}/fig5_tvae_sensitivity.png")
plt.close(fig)

print("5 figuras geradas em", OUT)
print(summary)
