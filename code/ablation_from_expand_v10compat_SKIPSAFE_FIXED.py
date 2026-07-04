#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ablation_from_expand_v10compat_SKIPSAFE.py
==========================================

Post-hoc ablation/summary generator for the EXPAND pipeline outputs.

Inputs:
  --eval_json   evaluation_results.json (expand output)
  --article_md  article_table.md (optional, enriches with best_model, deltas, etc.)
  --scenario    label (e.g., "main_0porcento" / "sensitivity_1porcento")
  --outdir      output directory

Outputs:
  <outdir>/ablation_comparison.csv
  <outdir>/ablation_tstr_best.png (optional)
  <outdir>/ablation_delta_same_model.png (optional)
  <outdir>/ablation_fidelity_vs_privacy.png (optional)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _load_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def _safe_get(d: Dict[str, Any], path: List[str], default=np.nan):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _read_article_md(p: Path) -> Optional[pd.DataFrame]:
    # article_table.md produced by expand is a markdown table.
    # We parse it with a simple heuristic (pipes).
    try:
        txt = p.read_text(encoding="utf-8")
    except Exception:
        return None
    lines = [ln.strip() for ln in txt.splitlines() if ln.strip().startswith("|")]
    if len(lines) < 3:
        return None
    header = [h.strip() for h in lines[0].strip("|").split("|")]
    # skip separator line (---)
    rows = []
    for ln in lines[2:]:
        parts = [x.strip() for x in ln.strip("|").split("|")]
        if len(parts) != len(header):
            continue
        rows.append(parts)
    df = pd.DataFrame(rows, columns=header)
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval_json", required=True)
    ap.add_argument("--article_md", default=None)
    ap.add_argument("--scenario", default="main")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--force", action="store_true", help="Overwrite outputs if they exist.")
    ap.add_argument("--skip_if_exists", action="store_true", help="Skip if outputs already exist.")
    args = ap.parse_args()

    # Create output directory FIRST
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    
    # Check if already exists
    out_csv = outdir / "ablation_comparison.csv"
    if out_csv.exists() and args.skip_if_exists and not args.force:
        print(f"[SKIP] ablation already exists: {out_csv.resolve()}")
        return

    # Load data
    evald = _load_json(Path(args.eval_json))
    art_df = _read_article_md(Path(args.article_md)) if args.article_md else None
    art_map = {}
    if art_df is not None and not art_df.empty:
        # normalize column names a bit
        cols = {c.strip(): c for c in art_df.columns}
        gen_col = cols.get("generator") or cols.get("Generator") or cols.get("Generator ")
        if gen_col:
            for _, r in art_df.iterrows():
                art_map[str(r[gen_col]).strip()] = r.to_dict()

    rows = []
    for gen, res in evald.items():
        util = res.get("utility", {})
        model_results = util.get("model_results", {})
        # pick best model by TSTR mean
        best_model = None
        best_tstr = -1e18
        for m, mr in (model_results or {}).items():
            tstr = _safe_get(mr, ["TSTR", "mean"], np.nan)
            try:
                tstr = float(tstr)
            except Exception:
                continue
            if np.isfinite(tstr) and tstr > best_tstr:
                best_tstr = tstr
                best_model = m

        # gather metrics (best model)
        if best_model and isinstance(model_results.get(best_model), dict):
            mr = model_results[best_model]
            trtr = _safe_get(mr, ["TRTR", "mean"], np.nan)
            # paired tests are available per-model; p-values here are not multiple-testing corrected
            p_t = _safe_get(mr, ["statistical_tests", "paired_t_test", "pvalue"], np.nan)
            eff = _safe_get(mr, ["statistical_tests", "effect_size", "cohens_d"], np.nan)
        else:
            trtr = np.nan
            p_t = np.nan
            eff = np.nan

        # global metrics from expand evaluation
        fidelity = res.get("fidelity", {})
        privacy = res.get("privacy", {})
        cvr = _safe_get(fidelity, ["constraint_violation_rate"], np.nan)
        ks_mean = _safe_get(fidelity, ["ks_mean_stat"], np.nan)
        corr_of_corr = _safe_get(fidelity, ["correlation_preservation", "correlation_of_correlations"], np.nan)

        risk_frac = _safe_get(privacy, ["risk_frac_dcr_lt_0p1"], np.nan)
        risk_med = _safe_get(privacy, ["distance_to_closest_record", "median_distance"], np.nan)

        # enrich from article_table.md if present (these are already "article-ready")
        art = art_map.get(gen, {})
        delta_same = art.get("TSTR_minus_TRTR_best_same_model", np.nan)
        tstr_best_art = art.get("TSTR_best", np.nan)
        best_model_art = art.get("best_model", best_model)

        rows.append({
            "Scenario": args.scenario,
            "Generator": gen,
            "BestModel": best_model_art,
            "TSTR_best": tstr_best_art if tstr_best_art not in ("", None) else best_tstr,
            "TRTR_best_model": trtr,
            "Delta_same_model": delta_same,
            "corr_of_corr": corr_of_corr,
            "KS_mean_stat": ks_mean,
            "CVR": cvr,
            "risk_frac_dcr_lt_0p1": risk_frac,
            "risk_median_dcr": risk_med,
            "p_paired_t": p_t,
            "cohens_d": eff,
        })

    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"[OK] Wrote: {out_csv.resolve()}")

    # Simple plots (optional)
    # TSTR by generator
    try:
        fig = plt.figure(figsize=(7, 4))
        ax = fig.add_subplot(111)
        ax.bar(df["Generator"], pd.to_numeric(df["TSTR_best"], errors="coerce"))
        ax.set_ylabel("TSTR (best)")
        ax.set_title(f"TSTR_best by generator ({args.scenario})")
        plt.xticks(rotation=45, ha="right")
        fig.tight_layout()
        fig.savefig(outdir / "ablation_tstr_best.png", dpi=200, bbox_inches="tight")
        plt.close(fig)
    except Exception:
        pass

    # Delta (same-model) by generator if available
    try:
        delta_num = pd.to_numeric(df["Delta_same_model"], errors="coerce")
        if delta_num.notna().any():
            fig = plt.figure(figsize=(7, 4))
            ax = fig.add_subplot(111)
            ax.bar(df["Generator"], delta_num)
            ax.set_ylabel("Δ (same-model)")
            ax.set_title(f"Δ=TSTR−TRTR (same-model) by generator ({args.scenario})")
            plt.xticks(rotation=45, ha="right")
            fig.tight_layout()
            fig.savefig(outdir / "ablation_delta_same_model.png", dpi=200, bbox_inches="tight")
            plt.close(fig)
    except Exception:
        pass

    # Fidelity vs Privacy scatter (corr_of_corr vs risk_frac)
    try:
        x = pd.to_numeric(df["corr_of_corr"], errors="coerce")
        y = pd.to_numeric(df["risk_frac_dcr_lt_0p1"], errors="coerce")
        if x.notna().any() and y.notna().any():
            fig = plt.figure(figsize=(6, 4))
            ax = fig.add_subplot(111)
            ax.scatter(x, y)
            for _, r in df.iterrows():
                xcor = pd.to_numeric(r["corr_of_corr"], errors="coerce")
                ycor = pd.to_numeric(r["risk_frac_dcr_lt_0p1"], errors="coerce")
                if pd.notna(xcor) and pd.notna(ycor):
                    ax.annotate(str(r["Generator"]), (float(xcor), float(ycor)), fontsize=8)
            ax.set_xlabel("corr_of_corr (higher=better)")
            ax.set_ylabel("risk_frac_dcr_lt_0p1 (lower=better)")
            ax.set_title(f"Fidelity vs proximity risk ({args.scenario})")
            fig.tight_layout()
            fig.savefig(outdir / "ablation_fidelity_vs_privacy.png", dpi=200, bbox_inches="tight")
            plt.close(fig)
    except Exception:
        pass


if __name__ == "__main__":
    main()
