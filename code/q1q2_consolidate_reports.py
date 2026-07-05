#!/usr/bin/env python3
"""Consolidate Q1/Q2 scenario artifacts into a single Markdown report.

This script is intentionally lightweight and wrapper-friendly:
- It does NOT depend on the internal implementation of the EXPAND script.
- It copies only key figures (fig1–fig3) into a consolidated folder so the
  consolidated Markdown can embed images reliably.
- It builds a cross-scenario summary table from evaluation_results.json (best-model utility,
  fidelity, and privacy metrics).

Designed to be called by the PowerShell master runner.

Robustness notes (v3):
- Accepts either a *bundle* directory (…/bundle_q1q2) or a *scenario* directory
  (…/exp_out_… containing evaluation_results.json).
- Figure discovery is resilient:
    * prefers <bundle_q1q2>/q1q2_figures/
    * falls back to <bundle_q1q2>/figures/ and recursive search (including OLD/ archives)
- Fidelity extraction prefers:
    fidelity.correlation_preservation.correlation_of_correlations (abs)
  and falls back to older/alternate schemas.
- Privacy extraction:
    * DCR median (median_distance/median)
    * frac(DCR < 0.1) from privacy_risk_counts.distance_below_0.1 / n_synthetic (when available)
    * MIA AUC from privacy.membership_inference (or older variants), best-effort.

This script will NOT generate figures; it only copies them if already present.
If figures are missing, rerun the figure step (see PIPELINE_ORQUESTRACAO_COMPLETO.md).
"""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List


@dataclass
class ScenarioInfo:
    name: str
    scenario_dir: Path          # directory that contains evaluation_results.json
    bundle_dir: Path            # directory that contains q1q2_figures/
    eval_json: Path
    config_json: Path
    figures_dir: Path           # preferred figures dir (may not exist)


# -------------------------------
# IO helpers
# -------------------------------

def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _to_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        v = float(x)
        if v != v:  # NaN
            return None
        return v
    except Exception:
        return None


# -------------------------------
# Path resolution
# -------------------------------

def _normalize_bundle_and_scenario(root: Path) -> Tuple[Path, Path]:
    """
    Accept either:
      - bundle dir: <scenario>/bundle_q1q2
      - scenario dir: <scenario> (contains evaluation_results.json) and has bundle_q1q2 inside
    Returns: (scenario_dir, bundle_dir)
    """
    root = root.resolve()

    # If user passed scenario dir
    if (root / "evaluation_results.json").exists():
        scenario_dir = root
        bundle_dir = root / "bundle_q1q2"
        if bundle_dir.exists():
            return scenario_dir, bundle_dir
        # tolerate alternative layout: search
        for cand in root.glob("**/bundle_q1q2"):
            if cand.is_dir():
                return scenario_dir, cand.resolve()
        return scenario_dir, bundle_dir  # may not exist; downstream will handle

    # If user passed bundle dir
    if root.name.lower() == "bundle_q1q2" or (root / "q1q2_figures").exists():
        bundle_dir = root
        scenario_dir = root.parent
        return scenario_dir, bundle_dir

    # Best-effort: look for bundle_q1q2 inside given root
    for cand in root.glob("**/bundle_q1q2"):
        if cand.is_dir():
            return cand.parent.resolve(), cand.resolve()

    # Fall back: treat as bundle anyway
    return root.parent.resolve(), root.resolve()


def _find_eval_config(scenario_dir: Path, bundle_dir: Path) -> Tuple[Path, Path, Optional[Dict[str, Any]]]:
    """
    Best-effort locate eval/config json paths and return parsed config (if readable).

    Prefer 'report_input.json' (wrapper output) if present in bundle_dir because it contains
    a normalized 'config' section; otherwise fall back to experiment_config.json.
    """
    eval_json = scenario_dir / "evaluation_results.json"
    config_json = scenario_dir / "experiment_config.json"
    parsed_cfg: Optional[Dict[str, Any]] = None

    report_input = bundle_dir / "report_input.json"
    if report_input.exists():
        try:
            wrapped = _read_json(report_input)
            if isinstance(wrapped, dict) and isinstance(wrapped.get("config"), dict):
                parsed_cfg = wrapped["config"]
        except Exception:
            parsed_cfg = None

    if parsed_cfg is None and config_json.exists():
        try:
            parsed_cfg = _read_json(config_json)
        except Exception:
            parsed_cfg = None

    return eval_json, config_json, parsed_cfg


def _scenario_from_root(name: str, root: Path) -> ScenarioInfo:
    scenario_dir, bundle_dir = _normalize_bundle_and_scenario(root)
    eval_json, config_json, _ = _find_eval_config(scenario_dir, bundle_dir)
    fig_dir = bundle_dir / "q1q2_figures"
    return ScenarioInfo(
        name=name,
        scenario_dir=scenario_dir,
        bundle_dir=bundle_dir,
        eval_json=eval_json,
        config_json=config_json,
        figures_dir=fig_dir,
    )


# -------------------------------
# Metric extraction
# -------------------------------

def _extract_tstr_best_model(utility: Dict[str, Any]) -> Optional[float]:
    """Extract best-model TSTR (R²) robustly."""
    if not isinstance(utility, dict):
        return None

    best_model = utility.get("best_model")
    model_results = utility.get("model_results") or {}

    def tstr_val(m: Dict[str, Any]) -> Optional[float]:
        t = m.get("TSTR")
        if isinstance(t, dict):
            return _to_float(t.get("mean"))
        return _to_float(t)

    chosen: Optional[float] = None
    if best_model and isinstance(model_results, dict) and best_model in model_results and isinstance(model_results[best_model], dict):
        chosen = tstr_val(model_results[best_model])

    if chosen is not None:
        return chosen

    # fallback: max across models
    best = None
    if isinstance(model_results, dict):
        for _, mr in model_results.items():
            if isinstance(mr, dict):
                v = tstr_val(mr)
                if v is None:
                    continue
                best = v if best is None else max(best, v)
    return best


def _extract_fidelity_corr(eval_block: Dict[str, Any]) -> Optional[float]:
    """Prefer correlation_of_correlations; fallback to corr_avg if present."""
    fidelity = eval_block.get("fidelity") or {}
    if not isinstance(fidelity, dict):
        return None

    corr_pres = fidelity.get("correlation_preservation") or {}
    if isinstance(corr_pres, dict):
        v = _to_float(corr_pres.get("correlation_of_correlations"))
        if v is not None:
            return abs(v)

    corr = fidelity.get("correlation") or {}
    if isinstance(corr, dict):
        v = _to_float(corr.get("corr_avg"))
        if v is not None:
            return v

    return None


def _extract_dcr_metrics(privacy: Dict[str, Any], n_synth: Optional[int]) -> Tuple[Optional[float], Optional[float]]:
    """Return (median_dcr, frac_dcr_lt_0.1) best-effort."""
    if not isinstance(privacy, dict):
        return None, None

    dcr = privacy.get("distance_to_closest_record") or {}
    if not isinstance(dcr, dict):
        return None, None

    median = _to_float(dcr.get("median_distance"))
    if median is None:
        median = _to_float(dcr.get("median"))

    frac = _to_float(dcr.get("fraction_within_0.1"))

    if frac is None:
        counts = dcr.get("privacy_risk_counts") or {}
        if isinstance(counts, dict):
            below = _to_float(counts.get("distance_below_0.1"))
            if below is not None and n_synth and n_synth > 0:
                frac = below / float(n_synth)

    return median, frac


def _extract_mia_auc(privacy: Dict[str, Any]) -> Optional[float]:
    """Best-effort Membership Inference AUC extraction (multiple schemas)."""
    if not isinstance(privacy, dict):
        return None

    mia = privacy.get("membership_inference") or privacy.get("membership_inference_attack")
    if isinstance(mia, dict):
        v = _to_float(mia.get("auc") or mia.get("AUC"))
        if v is not None:
            return v

        by_attack = mia.get("by_attack")
        if isinstance(by_attack, dict) and by_attack:
            if "LR" in by_attack and isinstance(by_attack["LR"], dict):
                v = _to_float(by_attack["LR"].get("auc") or by_attack["LR"].get("AUC"))
                if v is not None:
                    return v
            for _, vv in by_attack.items():
                if isinstance(vv, dict):
                    v = _to_float(vv.get("auc") or vv.get("AUC"))
                    if v is not None:
                        return v

    for k in ("mia_metrics", "mia", "MIA"):
        if k in privacy and isinstance(privacy[k], dict):
            mm = privacy[k]
            for auc_key in ("auc", "AUC", "mia_auc"):
                v = _to_float(mm.get(auc_key))
                if v is not None:
                    return v

    return None


def _detect_generators(eval_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Return only generator blocks, filtering out non-generator keys."""
    out: Dict[str, Dict[str, Any]] = {}
    if not isinstance(eval_data, dict):
        return out
    for gen, d in eval_data.items():
        if not isinstance(d, dict):
            continue
        if not any(k in d for k in ("utility", "fidelity", "privacy", "diversity")):
            continue
        out[str(gen)] = d
    return out


def _extract_metrics(eval_data: Dict[str, Any], cfg: Optional[Dict[str, Any]]) -> Dict[str, Dict[str, Optional[float]]]:
    """Return per-generator metrics: TSTR_R2, Fidelity_abs_corr, DCR_median, DCR_frac_lt_0.1, MIA_AUC."""
    out: Dict[str, Dict[str, Optional[float]]] = {}
    n_synth = None
    if isinstance(cfg, dict):
        try:
            ns = cfg.get("n_synthetic", cfg.get("n_synth", cfg.get("n_generated")))
            n_synth = int(ns) if ns is not None else None
        except Exception:
            n_synth = None

    gens = _detect_generators(eval_data)
    for gen, d in gens.items():
        utility = d.get("utility") or {}
        privacy = d.get("privacy") or {}

        util_r2 = _extract_tstr_best_model(utility)
        fid = _extract_fidelity_corr(d)
        dcr_med, dcr_frac = _extract_dcr_metrics(privacy, n_synth=n_synth)
        auc = _extract_mia_auc(privacy)

        out[gen] = {
            "TSTR_R2": util_r2,
            "Fidelity_abs_corr": fid,
            "DCR_median": dcr_med,
            "DCR_frac_lt_0.1": dcr_frac,
            "MIA_AUC": auc,
        }

    return out


# -------------------------------
# Figure discovery & copy
# -------------------------------

FIG_SPECS = (
    ("fig1", "fig1_utility_comparison.png"),
    ("fig2", "fig2_privacy_comparison.png"),
    ("fig3", "fig3_fidelity_comparison.png"),
)


def _find_latest_match(root: Path, fname: str) -> Optional[Path]:
    """Recursive search for fname under root; return most recently modified match.

    Uses case-insensitive filename comparison (helps on mixed-case artifacts).
    """
    if not root.exists() or not root.is_dir():
        return None
    target = fname.lower()
    matches: List[Path] = []
    try:
        for p in root.rglob("*"):
            if p.is_file() and p.name.lower() == target:
                matches.append(p)
    except Exception:
        return None
    if not matches:
        return None
    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0]


def _locate_fig_dir(scn: ScenarioInfo) -> Tuple[Path, List[str]]:
    """
    Return (best_guess_fig_root, debug_candidates).
    We still copy per-file (recursive fallback), but this identifies where we looked first.
    """
    cands = [
        scn.bundle_dir / "q1q2_figures",
        scn.bundle_dir / "figures",
        scn.bundle_dir,  # last resort
        scn.scenario_dir / "bundle_q1q2" / "q1q2_figures",
        scn.scenario_dir / "q1q2_figures",
    ]
    debug = [str(c) for c in cands]
    for c in cands:
        if c.exists() and c.is_dir():
            return c, debug
    return scn.bundle_dir / "q1q2_figures", debug


def _copy_key_figures(scn: ScenarioInfo, dst_fig_dir: Path, verbose: bool = False) -> Tuple[Dict[str, Path], List[str]]:
    """
    Copy fig1–fig3 PNG/PDF if they exist.
    Returns (mapping id->dest png path, logs).
    """
    _safe_mkdir(dst_fig_dir)
    mapping: Dict[str, Path] = {}
    logs: List[str] = []

    src_root, cand_debug = _locate_fig_dir(scn)
    if verbose:
        logs.append(f"[fig] {scn.name}: candidate roots:")
        for c in cand_debug:
            logs.append(f"  - {c}")
        logs.append(f"[fig] {scn.name}: selected root: {src_root}")

    for fig_id, fname in FIG_SPECS:
        # Prefer direct path under selected root
        direct = src_root / fname
        src = direct if direct.exists() else _find_latest_match(src_root, fname)

        if src and src.exists():
            dst = dst_fig_dir / fname
            shutil.copy2(src, dst)
            mapping[fig_id] = dst
            if verbose:
                logs.append(f"[fig] copied {fig_id}: {src} -> {dst}")
        else:
            if verbose:
                logs.append(f"[fig] missing {fig_id}: looked for {fname} under {src_root} (direct + recursive)")

        # also copy pdf if present (best-effort)
        pdf_name = Path(fname).with_suffix(".pdf").name
        direct_pdf = src_root / pdf_name
        src_pdf = direct_pdf if direct_pdf.exists() else _find_latest_match(src_root, pdf_name)
        if src_pdf and src_pdf.exists():
            shutil.copy2(src_pdf, dst_fig_dir / pdf_name)
            if verbose:
                logs.append(f"[fig] copied {fig_id} pdf: {src_pdf} -> {dst_fig_dir / pdf_name}")

    return mapping, logs


def _md_escape_path(p: Path) -> str:
    return str(p).replace("\\", "/")


def build_consolidated_report(
    baseline: ScenarioInfo,
    sensitivity: ScenarioInfo,
    outdir: Path,
    embed_figures: bool = True,
    verbose: bool = False,
) -> Path:
    _safe_mkdir(outdir)
    figs_root = outdir / "figures"
    _safe_mkdir(figs_root)

    # Copy figures for reliable embedding
    base_figs, base_logs = _copy_key_figures(baseline, figs_root / "baseline", verbose=verbose) if embed_figures else ({}, [])
    sens_figs, sens_logs = _copy_key_figures(sensitivity, figs_root / "sensitivity", verbose=verbose) if embed_figures else ({}, [])

    # Load evals and compute summary
    eval_base = _read_json(baseline.eval_json) if baseline.eval_json.exists() else {}
    eval_sens = _read_json(sensitivity.eval_json) if sensitivity.eval_json.exists() else {}

    # Load config (prefer wrapper report_input.json if present, else experiment_config.json)
    _, _, cfg_base = _find_eval_config(baseline.scenario_dir, baseline.bundle_dir)
    _, _, cfg_sens = _find_eval_config(sensitivity.scenario_dir, sensitivity.bundle_dir)

    m_base = _extract_metrics(eval_base, cfg_base)
    m_sens = _extract_metrics(eval_sens, cfg_sens)

    gens = sorted(set(m_base.keys()) | set(m_sens.keys()))

    def fmt(x: Optional[float]) -> str:
        if x is None:
            return "—"
        return f"{x:.3f}"

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    def _cfg_field(cfg: Optional[Dict[str, Any]], *keys: str, default: str = "N/A") -> str:
        if not isinstance(cfg, dict):
            return default
        for k in keys:
            if cfg.get(k) not in (None, ""):
                return str(cfg.get(k))
        return default

    real_file = _cfg_field(cfg_base, "input_file", "input", "data_file", default="dados.csv")
    target = _cfg_field(cfg_base, "target", "target_col", "y_col", default="surface_tension_mNm")

    md_lines: List[str] = []
    md_lines.append("# Q1/Q2 Consolidated Report (Baseline 0% vs Sensitivity 1%)")
    md_lines.append("")
    md_lines.append(f"Generated at (UTC): {now}")
    md_lines.append("")

    md_lines.append("## Inputs")
    md_lines.append("")
    md_lines.append(f"- Real dataset: `{real_file}`")
    md_lines.append(f"- Target: `{target}`")
    md_lines.append("")
    md_lines.append("Scenario output roots:")
    md_lines.append(f"- Baseline scenario dir: `{baseline.scenario_dir}`")
    md_lines.append(f"- Baseline bundle dir: `{baseline.bundle_dir}`")
    md_lines.append(f"- Sensitivity scenario dir: `{sensitivity.scenario_dir}`")
    md_lines.append(f"- Sensitivity bundle dir: `{sensitivity.bundle_dir}`")
    md_lines.append("")

    md_lines.append("## Cross-scenario summary (utility, fidelity, privacy)")
    md_lines.append("")
    md_lines.append(
        "| Generator | Baseline TSTR (R²) | Sensitivity TSTR (R²) | Δ (Sens−Base) | "
        "Baseline |corr| (abs) | Sensitivity |corr| (abs) | "
        "Baseline DCR median | Sensitivity DCR median | "
        "Baseline frac(DCR<0.1) | Sensitivity frac(DCR<0.1) | "
        "Baseline MIA AUC | Sensitivity MIA AUC |"
    )
    md_lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for g in gens:
        b = m_base.get(g, {})
        s = m_sens.get(g, {})
        b_r2 = b.get("TSTR_R2")
        s_r2 = s.get("TSTR_R2")
        delta = (s_r2 - b_r2) if (s_r2 is not None and b_r2 is not None) else None
        md_lines.append(
            "| "
            + g
            + " | "
            + fmt(b_r2)
            + " | "
            + fmt(s_r2)
            + " | "
            + fmt(delta)
            + " | "
            + fmt(b.get("Fidelity_abs_corr"))
            + " | "
            + fmt(s.get("Fidelity_abs_corr"))
            + " | "
            + fmt(b.get("DCR_median"))
            + " | "
            + fmt(s.get("DCR_median"))
            + " | "
            + fmt(b.get("DCR_frac_lt_0.1"))
            + " | "
            + fmt(s.get("DCR_frac_lt_0.1"))
            + " | "
            + fmt(b.get("MIA_AUC"))
            + " | "
            + fmt(s.get("MIA_AUC"))
            + " |"
        )

    md_lines.append("")
    md_lines.append("## Scenario sections")
    md_lines.append("")

    def add_section(scn: ScenarioInfo, figs: Dict[str, Path], logs: List[str]) -> None:
        md_lines.append(f"### {scn.name}")
        md_lines.append("")
        md_lines.append(f"- Scenario dir: `{scn.scenario_dir}`")
        md_lines.append(f"- Bundle dir: `{scn.bundle_dir}`")
        md_lines.append(f"- Eval JSON: `{scn.eval_json}`")
        md_lines.append(f"- Config JSON: `{scn.config_json}`")
        md_lines.append("")

        reports = sorted(scn.bundle_dir.glob("report_q1q2*.md")) + sorted(scn.bundle_dir.glob("report_*.md"))
        reports = [r for r in reports if r.is_file()]
        if reports:
            for rp in reports:
                md_lines.append(f"- Report: `{rp}`")
        else:
            md_lines.append("- Report: (not found in bundle dir; check runner logs)")
        md_lines.append("")

        if embed_figures:
            md_lines.append("#### Key figures")
            md_lines.append("")
            if figs:
                for fig_id in ("fig1", "fig2", "fig3"):
                    if fig_id in figs:
                        rel = figs[fig_id].relative_to(outdir)
                        md_lines.append(f"**{fig_id.upper()}**")
                        md_lines.append("")
                        md_lines.append(f"![]({_md_escape_path(rel)})")
                        md_lines.append("")
            else:
                md_lines.append("_(no figures found to embed; see diagnostics below)_")
                md_lines.append("")

        if verbose and logs:
            md_lines.append("#### Figure diagnostics (verbose)")
            md_lines.append("")
            md_lines.extend([f"- {line}" for line in logs])
            md_lines.append("")

    add_section(baseline, base_figs, base_logs)
    add_section(sensitivity, sens_figs, sens_logs)

    if embed_figures and (not base_figs or not sens_figs):
        md_lines.append("## Notes")
        md_lines.append("")
        md_lines.append(
            "This consolidator **does not generate figures**. If the `bundle_q1q2/q1q2_figures/` folder "
            "does not contain `fig1_utility_comparison.*`, `fig2_privacy_comparison.*`, `fig3_fidelity_comparison.*`, "
            "please rerun the figure step (e.g., `generate_q1q2_figures_STANDALONE.py` or the bundle step with "
            "`--enable_q1q2_figures`) for each scenario."
        )
        md_lines.append("")

    out_md = outdir / "report_q1q2_consolidated.md"
    out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return out_md


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline_bundle", required=True, help="Path to Baseline bundle_q1q2 OR scenario directory")
    ap.add_argument("--sensitivity_bundle", required=True, help="Path to Sensitivity bundle_q1q2 OR scenario directory")
    ap.add_argument("--outdir", required=True, help="Output directory for consolidated artifacts")
    ap.add_argument("--no_embed_figures", action="store_true", help="Do not copy/embed figures")
    ap.add_argument("--verbose", action="store_true", help="Include figure diagnostics in the Markdown report")
    args = ap.parse_args()

    baseline = _scenario_from_root("Baseline (0% DOE-noise)", Path(args.baseline_bundle))
    sensitivity = _scenario_from_root("Sensitivity (1% DOE-noise)", Path(args.sensitivity_bundle))

    out = build_consolidated_report(
        baseline,
        sensitivity,
        outdir=Path(args.outdir).resolve(),
        embed_figures=not args.no_embed_figures,
        verbose=args.verbose,
    )

    print(f"[OK] Wrote consolidated report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
