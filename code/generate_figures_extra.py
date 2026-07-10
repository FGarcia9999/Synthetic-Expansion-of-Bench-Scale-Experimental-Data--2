"""
Gera as 4 figuras suplementares adicionais, a partir de dados reais (PEERFIX1)
ou, no caso da Figura 8, como diagrama conceitual do protocolo (nao empirico).
"""
import json
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "figure.dpi": 200,
})

GEN_ORDER = ["gaussian_copula", "ctgan", "tvae", "tabddpm"]
GEN_LABEL = {"gaussian_copula": "Gaussian Copula", "ctgan": "CTGAN", "tvae": "TVAE", "tabddpm": "TabDDPM"}
GEN_COLOR = {"gaussian_copula": "#4C72B0", "ctgan": "#DD8452", "tvae": "#55A868", "tabddpm": "#C44E52"}

BASE = "/home/claude/final_fix/out_PEERFIX1_baseline"
SENS = "/home/claude/final_fix/out_PEERFIX1_sensitivity"
OUT = "/home/claude/figures"
FACTORS = ["seawater_vv", "urea_pv", "ammonium_sulfate_pv", "kh2po4_pv"]
TARGET = "surface_tension_mNm"

real_df = pd.read_csv("/home/claude/icd_work/dados_real.csv")

# ----------------------------------------------------------------------
# Figure 6: DCR ECDF (baseline), recomputed directly from CSVs
# ----------------------------------------------------------------------
scaler = StandardScaler().fit(real_df[FACTORS + [TARGET]])
real_scaled = scaler.transform(real_df[FACTORS + [TARGET]])
nn = NearestNeighbors(n_neighbors=1).fit(real_scaled)

fig, ax = plt.subplots(figsize=(6.5, 4.5))
for g in GEN_ORDER:
    sdf = pd.read_csv(f"{BASE}/synthetic_datasets/{g}_synthetic.csv")
    s_scaled = scaler.transform(sdf[FACTORS + [TARGET]])
    dist, _ = nn.kneighbors(s_scaled)
    dist = np.sort(dist.ravel())
    ecdf_y = np.arange(1, len(dist) + 1) / len(dist)
    ax.plot(dist, ecdf_y, label=GEN_LABEL[g], color=GEN_COLOR[g], linewidth=2)
ax.axvline(0.1, color="gray", linestyle="--", linewidth=1, label="τ = 0.1 (Fig. 3 threshold)")
ax.set_xlabel("Standardised Euclidean distance to nearest real record (DCR)")
ax.set_ylabel("Empirical cumulative fraction of synthetic samples")
ax.set_title("Figure 6. Distance-to-Closest-Record ECDF — baseline scenario")
ax.legend(frameon=False, loc="lower right")
ax.set_xlim(left=0)
fig.tight_layout()
fig.savefig(f"{OUT}/fig6_dcr_ecdf.png")
plt.close(fig)

# ----------------------------------------------------------------------
# Figure 7: TSTR boxplot over the 10 internal runs (baseline), best model per generator
# ----------------------------------------------------------------------
with open(f"{BASE}/evaluation_results.json", encoding="utf-8-sig") as f:
    d_base = json.load(f)


def best_model_name(res):
    best_model, best_val = None, -1e9
    for m, mres in res["utility"]["model_results"].items():
        if mres["TSTR"]["mean"] > best_val:
            best_val, best_model = mres["TSTR"]["mean"], m
    return best_model


fig, ax = plt.subplots(figsize=(7, 4.5))
box_data, box_labels, box_colors = [], [], []
for g in GEN_ORDER:
    bm = best_model_name(d_base[g])
    raw = d_base[g]["utility"]["model_results"][bm]["TSTR"]["raw"]
    box_data.append(raw)
    box_labels.append(f"{GEN_LABEL[g]}\n(best: {bm})")
    box_colors.append(GEN_COLOR[g])
bp = ax.boxplot(box_data, labels=box_labels, patch_artist=True, showmeans=True,
                 medianprops={"color": "black"}, meanprops={"marker": "D", "markerfacecolor": "white", "markeredgecolor": "black"})
for patch, c in zip(bp["boxes"], box_colors):
    patch.set_facecolor(c); patch.set_alpha(0.6)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_ylabel("TSTR (R², best downstream model per generator)")
ax.set_title("Figure 7. TSTR distribution over 10 evaluation runs — baseline scenario")
fig.tight_layout()
fig.savefig(f"{OUT}/fig7_tstr_boxplot.png")
plt.close(fig)

# ----------------------------------------------------------------------
# Figure 8: Conceptual pipeline diagram (not data-driven)
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 5.2))
ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")


def box(x, y, w, h, text, fc="#EAF1FB", ec="#4C72B0", fontsize=9.5):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.08",
                        linewidth=1.4, facecolor=fc, edgecolor=ec)
    ax.add_patch(p)
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fontsize, wrap=True)


def arrow(x1, y1, x2, y2):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14, linewidth=1.4, color="#333333")
    ax.add_patch(a)


box(0.3, 2.3, 1.7, 1.4, "Real bench-scale\nfactorial data\n(n=20)", fc="#FDEBD3", ec="#DD8452")
arrow(2.0, 3.0, 2.6, 3.0)

box(2.6, 4.0, 2.1, 1.2, "4 generators:\nGaussian Copula, CTGAN,\nTVAE, TabDDPM", fc="#EAF1FB", ec="#4C72B0")
arrow(3.65, 4.0, 3.65, 3.7)
box(2.6, 2.3, 2.1, 1.2, "Synthetic expansion\n(n_synthetic = 140\nper generator)", fc="#EAF1FB", ec="#4C72B0")
arrow(4.7, 3.0, 5.3, 3.0)

box(5.3, 3.9, 2.0, 0.85, "(a) Fidelity\nKS, Wasserstein,\ncorr_of_corr", fc="#E8F5E9", ec="#55A868", fontsize=8.5)
box(5.3, 2.95, 2.0, 0.85, "(b) Utility\nTSTR/TRTR,\nsame-model Δ", fc="#E8F5E9", ec="#55A868", fontsize=8.5)
box(5.3, 2.0, 2.0, 0.85, "(c) Risk\nDCR proximity", fc="#E8F5E9", ec="#55A868", fontsize=8.5)
box(5.3, 1.05, 2.0, 0.85, "(d) Domain concordance\nICD vs. known\nfactorial effects", fc="#FCEAEA", ec="#C44E52", fontsize=8.5)

for y in (4.32, 3.37, 2.42, 1.47):
    arrow(7.3, y, 7.9, 3.0)

box(7.9, 2.3, 1.8, 1.4, "Auditable\nvalidation report\n(no single-generator\nverdict)", fc="#F5F0FA", ec="#8172B2")

ax.set_title("Figure 8. Conceptual overview of the fidelity–utility–risk–ICD validation protocol", fontsize=12, pad=14)
fig.tight_layout()
fig.savefig(f"{OUT}/fig8_pipeline_diagram.png")
plt.close(fig)

# ----------------------------------------------------------------------
# Figure 9: KH2PO4 vs surface tension, real vs synthetic (the one confirmed effect)
# ----------------------------------------------------------------------
fig, axes = plt.subplots(1, 4, figsize=(15, 3.6), sharey=True, sharex=True)
for ax, g in zip(axes, GEN_ORDER):
    sdf = pd.read_csv(f"{BASE}/synthetic_datasets/{g}_synthetic.csv")
    ax.scatter(sdf["kh2po4_pv"], sdf[TARGET], alpha=0.25, s=14, color=GEN_COLOR[g], label="Synthetic (n=140)")
    ax.scatter(real_df["kh2po4_pv"], real_df[TARGET], color="black", s=45, marker="D", label="Real (n=20)", zorder=5)
    z_real = np.polyfit(real_df["kh2po4_pv"], real_df[TARGET], 1)
    xs = np.linspace(real_df["kh2po4_pv"].min(), real_df["kh2po4_pv"].max(), 50)
    ax.plot(xs, np.poly1d(z_real)(xs), color="black", linewidth=1.5, linestyle="--")
    ax.set_title(GEN_LABEL[g], fontsize=10)
    ax.set_xlabel("KH2PO4 (%w/v)")
axes[0].set_ylabel("Surface tension (mN/m)")
axes[0].legend(frameon=False, fontsize=8, loc="upper right")
fig.suptitle("Figure 9. KH2PO4 vs. surface tension — the single confirmed significant effect (Section 2.1), real vs. synthetic (baseline)", y=1.04)
fig.tight_layout()
fig.savefig(f"{OUT}/fig9_kh2po4_scatter.png", bbox_inches="tight")
plt.close(fig)

print("4 figuras suplementares geradas em", OUT)
