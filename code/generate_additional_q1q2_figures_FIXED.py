#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_additional_q1q2_figures_FIXED.py

Additional Q1/Q2 figures for the biosurfactant synthetic expansion study.

Validated role in the final working baseline:
- Generates Figure 4: Privacy–utility trade-off (TSTR vs DCR median).
- Generates Figure 5: Utility and ranking summary (TSTR, ranks, ΔTSTR, ΔRank).
- Corrects the previous "ranking evolution" interpretation by separating ΔTSTR
  from ΔRank. In the validated biosurfactant run, ΔRank = 0 for all generators.

Inputs:
    --baseline     Path to Baseline evaluation_results.json
    --sensitivity  Path to Sensitivity evaluation_results.json
    --outdir       Output directory

Outputs:
    fig4_privacy_utility_tradeoff.png/.pdf
    fig5_utility_ranking_summary.png/.pdf
    fig5_ranking_evolution.png/.pdf  (compatibility alias)

This script is intentionally independent from the heavy EXPAND pipeline.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


DEFAULT_GENERATOR_ORDER = ["GaussianCopula", "TVAE", "CTGAN", "TabDDPM"]
DISPLAY_NAMES = {
    "gaussian_copula": "Gaussian Copula",
    "GaussianCopula": "Gaussian Copula",
    "gaussian": "Gaussian Copula",
    "TVAE": "TVAE",
    "tvae": "TVAE",
    "CTGAN": "CTGAN",
    "ctgan": "CTGAN",
    "TabDDPM": "TabDDPM",
    "tabddpm": "TabDDPM",
}
COLORS = {
    "Gaussian Copula": "#e78ac3",
    "TVAE": "#66c2a5",
    "CTGAN": "#8da0cb",
    "TabDDPM": "#fc8d62",
}


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _to_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except Exception:
        return None


def _display_name(raw: str) -> str:
    return DISPLAY_NAMES.get(raw, raw)


def _generator_blocks(eval_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out = {}
    for k, v in eval_data.items():
        if isinstance(v, dict) and any(sec in v for sec in ("utility", "privacy", "fidelity")):
            out[_display_name(k)] = v
    return out


def _extract_tstr(block: Dict[str, Any]) -> Optional[float]:
    utility = block.get("utility") or {}
    model_results = utility.get("model_results") or {}
    best_model = utility.get("best_model")

    def get_val(mr: Dict[str, Any]) -> Optional[float]:
        tstr = mr.get("TSTR")
        if isinstance(tstr, dict):
            return _to_float(tstr.get("mean"))
        return _to_float(tstr)

    if best_model in model_results and isinstance(model_results[best_model], dict):
        val = get_val(model_results[best_model])
        if val is not None:
            return val

    # fallback: maximum signed TSTR (closer to zero is better when values are negative)
    vals = []
    for mr in model_results.values():
        if isinstance(mr, dict):
            val = get_val(mr)
            if val is not None:
                vals.append(val)
    return max(vals) if vals else None


def _extract_dcr_median(block: Dict[str, Any]) -> Optional[float]:
    privacy = block.get("privacy") or {}
    dcr = privacy.get("distance_to_closest_record") or {}
    if not isinstance(dcr, dict):
        return None
    for key in ("median_distance", "median", "median_dcr", "DCR_median"):
        val = _to_float(dcr.get(key))
        if val is not None:
            return val
    return None


def _collect_metrics(path: Path) -> Dict[str, Dict[str, Optional[float]]]:
    data = _read_json(path)
    blocks = _generator_blocks(data)
    metrics = {}
    for gen, block in blocks.items():
        metrics[gen] = {
            "TSTR": _extract_tstr(block),
            "DCR_median": _extract_dcr_median(block),
        }
    return metrics


def _rank_by_tstr(metrics: Dict[str, Dict[str, Optional[float]]]) -> Dict[str, int]:
    vals = [(gen, m.get("TSTR")) for gen, m in metrics.items() if m.get("TSTR") is not None]
    vals.sort(key=lambda x: x[1], reverse=True)  # signed R²: higher/closer to zero is better
    return {gen: i + 1 for i, (gen, _) in enumerate(vals)}


def plot_privacy_utility_tradeoff(
    base: Dict[str, Dict[str, Optional[float]]],
    sens: Dict[str, Dict[str, Optional[float]]],
    outdir: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 6.5))

    gens = [g for g in ["Gaussian Copula", "TVAE", "CTGAN", "TabDDPM"] if g in base or g in sens]
    for gen in gens:
        color = COLORS.get(gen, None)
        bx, by = (base.get(gen, {}).get("TSTR"), base.get(gen, {}).get("DCR_median"))
        sx, sy = (sens.get(gen, {}).get("TSTR"), sens.get(gen, {}).get("DCR_median"))

        if bx is not None and by is not None:
            ax.scatter(bx, by, marker="o", s=110, color=color, edgecolor="black", linewidth=0.8, zorder=3)
            ax.annotate(f"{gen} B", (bx, by), xytext=(5, 5), textcoords="offset points", fontsize=8)

        if sx is not None and sy is not None:
            ax.scatter(sx, sy, marker="^", s=125, color=color, edgecolor="black", linewidth=0.8, zorder=4)
            ax.annotate(f"{gen} S", (sx, sy), xytext=(5, -12), textcoords="offset points", fontsize=8)

        if bx is not None and by is not None and sx is not None and sy is not None:
            ax.annotate(
                "",
                xy=(sx, sy),
                xytext=(bx, by),
                arrowprops=dict(arrowstyle="->", lw=1.2, color=color, alpha=0.85),
                zorder=2,
            )

    ax.axhline(0.1, linestyle="--", linewidth=1.2, color="red", alpha=0.8)
    ax.axvline(0.0, linestyle="--", linewidth=1.0, color="gray", alpha=0.8)

    ax.set_xlabel("Utility: TSTR (signed R²; closer to 0 is better)")
    ax.set_ylabel("Privacy: DCR median (higher is safer)")
    ax.set_title("Privacy–Utility Trade-off: Baseline vs Sensitivity")
    ax.grid(True, alpha=0.25)

    handles = [
        Line2D([0], [0], marker="o", color="w", label="Baseline (0% DOE noise)", markerfacecolor="lightgray",
               markeredgecolor="black", markersize=9),
        Line2D([0], [0], marker="^", color="w", label="Sensitivity (1% DOE noise)", markerfacecolor="lightgray",
               markeredgecolor="black", markersize=10),
        Line2D([0], [0], color="red", linestyle="--", label="DCR risk threshold = 0.1"),
        Line2D([0], [0], color="gray", linestyle="--", label="Perfect utility (TSTR = 0)"),
    ]
    for gen in gens:
        handles.append(Patch(facecolor=COLORS.get(gen, "gray"), edgecolor="black", label=gen))
    ax.legend(handles=handles, fontsize=8, loc="best", frameon=True)

    fig.tight_layout()
    fig.savefig(outdir / "fig4_privacy_utility_tradeoff.png", dpi=300, bbox_inches="tight")
    fig.savefig(outdir / "fig4_privacy_utility_tradeoff.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_utility_ranking_summary(
    base: Dict[str, Dict[str, Optional[float]]],
    sens: Dict[str, Dict[str, Optional[float]]],
    outdir: Path,
) -> None:
    base_rank = _rank_by_tstr(base)
    sens_rank = _rank_by_tstr(sens)

    gens = [g for g in ["Gaussian Copula", "TVAE", "CTGAN", "TabDDPM"] if g in base or g in sens]
    rows = []
    for gen in gens:
        b = base.get(gen, {}).get("TSTR")
        s = sens.get(gen, {}).get("TSTR")
        delta = (s - b) if b is not None and s is not None else None
        dr = (sens_rank.get(gen) - base_rank.get(gen)) if gen in base_rank and gen in sens_rank else None
        rows.append((gen, b, base_rank.get(gen), s, sens_rank.get(gen), delta, dr))

    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    ax.axis("off")
    ax.set_title("Utility and Ranking Summary (TSTR, signed R²)", pad=14)

    columns = ["Generator", "Baseline\nTSTR", "Baseline\nRank", "Sensitivity\nTSTR", "Sensitivity\nRank", "ΔTSTR", "ΔRank"]
    cell_text = []
    for gen, b, br, s, sr, delta, dr in rows:
        arrow = "↑" if (delta is not None and delta > 0) else ("↓" if (delta is not None and delta < 0) else "→")
        cell_text.append([
            gen,
            "—" if b is None else f"{b:.3f}",
            "—" if br is None else str(br),
            "—" if s is None else f"{s:.3f}",
            "—" if sr is None else str(sr),
            "—" if delta is None else f"{arrow} {delta:+.3f}",
            "—" if dr is None else f"{dr:+d}",
        ])

    table = ax.table(cellText=cell_text, colLabels=columns, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.0, 1.55)

    # header and generator-color cells
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight="bold")
            cell.set_facecolor("#f0f0f0")
        if row > 0 and col == 0:
            gen = cell.get_text().get_text()
            cell.set_facecolor(COLORS.get(gen, "#ffffff"))
            cell.set_text_props(weight="bold")

    note = (
        "Ranking is based on TSTR (signed R²; closer to zero is better). "
        "ΔTSTR = Sensitivity − Baseline; ΔRank = Sensitivity rank − Baseline rank."
    )
    ax.text(0.5, -0.08, note, transform=ax.transAxes, ha="center", va="top", fontsize=8)

    fig.tight_layout()
    fig.savefig(outdir / "fig5_utility_ranking_summary.png", dpi=300, bbox_inches="tight")
    fig.savefig(outdir / "fig5_utility_ranking_summary.pdf", bbox_inches="tight")
    # compatibility alias for previous orchestration name
    shutil.copy2(outdir / "fig5_utility_ranking_summary.png", outdir / "fig5_ranking_evolution.png")
    shutil.copy2(outdir / "fig5_utility_ranking_summary.pdf", outdir / "fig5_ranking_evolution.pdf")
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True, help="Path to Baseline evaluation_results.json")
    ap.add_argument("--sensitivity", required=True, help="Path to Sensitivity evaluation_results.json")
    ap.add_argument("--outdir", required=True, help="Output directory for additional figures")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    base = _collect_metrics(Path(args.baseline))
    sens = _collect_metrics(Path(args.sensitivity))

    plot_privacy_utility_tradeoff(base, sens, outdir)
    plot_utility_ranking_summary(base, sens, outdir)

    print(f"[OK] Wrote additional Q1/Q2 figures to: {outdir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
