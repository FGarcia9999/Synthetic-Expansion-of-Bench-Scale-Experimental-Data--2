#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wrap_expand_for_report_v10_AUTOMATED_SKIPSAFE.py
================================================

Creates a report_generator-compatible JSON (report_input.json) by wrapping the
already-produced outputs from the EXPAND pipeline (v8+).

This is POST-PROCESSING ONLY; it does NOT re-run experiments.

Inputs (required):
  --eval_json     <scenario_dir>/evaluation_results.json
  --config_json   <scenario_dir>/experiment_config.json
  --out_json      <scenario_dir>/bundle_q1q2/report_input.json

Optional:
  --domain        default: biosurfactant
  --title         human-readable title
  --scenario      label (e.g., baseline_0pct, sensitivity_1pct)
  --artifacts_dir directory containing artifacts to be referenced (figures, tables, texts)
  --artifact_glob_root root path used to compute relative artifact links

Idempotency:
  By default, if --out_json already exists, the script exits successfully without overwriting.
  Use --force to overwrite.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _load_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))



def _write_json(p: Path, obj: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def _find_synthetic_dir(scenario_dir: Path) -> Optional[Path]:
    # Common locations used by the runners (baseline/sensitivity)
    candidates = [
        scenario_dir / "synthetic_datasets",
        scenario_dir.parent / f"{scenario_dir.name}_SENSITIVITY" / "synthetic_datasets",
        scenario_dir.parent / f"{scenario_dir.name}_BASELINE" / "synthetic_datasets",
    ]

    # Relaxed search: sometimes the suffix is appended or the directory is duplicated
    for pat in [f"{scenario_dir.name}*SENSITIVITY*/synthetic_datasets", f"{scenario_dir.name}*BASELINE*/synthetic_datasets"]:
        for p in scenario_dir.parent.glob(pat):
            candidates.append(p)

    for c in candidates:
        if c and c.exists():
            # accept csv or parquet
            if any(c.glob("*.csv")) or any(c.glob("*.parquet")):
                return c

    # Fallback: locate any synthetic_datasets folder mentioning the scenario name (bounded search)
    for c in scenario_dir.parent.glob("**/synthetic_datasets"):
        if scenario_dir.name in str(c) and (any(c.glob("*.csv")) or any(c.glob("*.parquet"))):
            return c

    return None


def _compute_synthetic_validation(synth_dir: Path, max_rows: int = 200000) -> Dict[str, Any]:
    import numpy as np
    import pandas as pd
    from datetime import datetime

    def _df_read(p: Path) -> pd.DataFrame:
        if p.suffix.lower() == ".parquet":
            return pd.read_parquet(p)
        return pd.read_csv(p)

    out: Dict[str, Any] = {
        "synthetic_dir": str(synth_dir),
        "generated_at_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "datasets": {},
        "summary": {},
        "notes": "Auto-generated quick validation (replace/extend with domain-specific checks as needed).",
    }

    files = sorted(list(synth_dir.glob("*.csv")) + list(synth_dir.glob("*.parquet")))
    for f in files:
        try:
            df = _df_read(f)
        except Exception as e:
            out["datasets"][f.stem] = {"file": str(f), "error": f"failed_to_read: {e}"}
            continue

        n_rows, n_cols = int(df.shape[0]), int(df.shape[1])
        df_use = df
        if n_rows > max_rows:
            df_use = df.sample(n=max_rows, random_state=0)

        # numeric summary
        num = df_use.select_dtypes(include=["number"])
        nan_total = int(df_use.isna().sum().sum())
        inf_total = int(np.isinf(num.to_numpy()).sum()) if num.shape[1] else 0
        dup_rows = int(df_use.duplicated().sum())

        per_col = {}
        for col in df_use.columns:
            s = df_use[col]
            col_info = {
                "dtype": str(s.dtype),
                "nan": int(s.isna().sum()),
            }
            if pd.api.types.is_numeric_dtype(s):
                arr = pd.to_numeric(s, errors="coerce")
                col_info.update({
                    "min": float(np.nanmin(arr.to_numpy())) if arr.notna().any() else None,
                    "max": float(np.nanmax(arr.to_numpy())) if arr.notna().any() else None,
                    "mean": float(np.nanmean(arr.to_numpy())) if arr.notna().any() else None,
                    "std": float(np.nanstd(arr.to_numpy(), ddof=1)) if arr.notna().sum() > 1 else None,
                    "neg_frac": float((arr < 0).mean()) if arr.notna().any() else None,
                    "zero_frac": float((arr == 0).mean()) if arr.notna().any() else None,
                })
            per_col[col] = col_info

        out["datasets"][f.stem] = {
            "file": str(f),
            "n_rows": n_rows,
            "n_cols": n_cols,
            "nan_total": nan_total,
            "inf_total_numeric": inf_total,
            "duplicate_rows_sampled": dup_rows,
            "columns": per_col,
        }

    # summary across datasets
    out["summary"] = {
        "n_datasets": len(out["datasets"]),
        "datasets_with_read_error": [k for k, v in out["datasets"].items() if "error" in v],
        "max_rows_checked_per_dataset": max_rows,
    }
    return out

def _normalize_config(cfg: Dict[str, Any], scenario: Optional[str], title: Optional[str], domain: str) -> Dict[str, Any]:
    out = dict(cfg) if isinstance(cfg, dict) else {}
    out.setdefault("random_seed", out.get("seed", out.get("Seed", "N/A")))
    out.setdefault("n_runs", out.get("n_runs", out.get("NRuns", out.get("runs", "N/A"))))
    out.setdefault("confidence_level", out.get("confidence_level", 0.95))
    out.setdefault("domain", out.get("domain", domain))
    if scenario:
        out.setdefault("scenario", scenario)
    if title:
        out.setdefault("title", title)
    return out


def _collect_artifacts(art_dir: Path, root_override: Optional[Path] = None) -> Dict[str, Any]:
    root = (root_override or art_dir).resolve()
    art_dir = art_dir.resolve()

    out: Dict[str, Any] = {"root": str(root), "files": [], "figures": {}, "tables": {}, "texts": {}}

    def rel(p: Path) -> str:
        try:
            return str(p.resolve().relative_to(root))
        except Exception:
            return str(p.resolve())

    core = [
        "evaluation_results.json", "experiment_config.json", "comprehensive_report.md",
        "article_table.csv", "article_table.md", "results_discussion.txt",
        "figures.tex", "figures_manifest.json",
    ]
    for fname in core:
        p = art_dir / fname
        if p.exists():
            out["files"].append(rel(p))

    for sub in ["q1q2_figures", "delta_per_feature", "synthetic_datasets"]:
        d = art_dir / sub
        if d.exists() and d.is_dir():
            out["files"].append(rel(d))

    fig_dir = art_dir / "q1q2_figures"
    if fig_dir.exists():
        for p in sorted(fig_dir.rglob('*.png')):
            out["figures"].setdefault("png", []).append(rel(p))
        for p in sorted(fig_dir.rglob('*.pdf')):
            out["figures"].setdefault("pdf", []).append(rel(p))

    dpf = art_dir / "delta_per_feature"
    if dpf.exists():
        for p in sorted(dpf.rglob('*.csv')):
            out["tables"].setdefault("delta_per_feature_csv", []).append(rel(p))

    report_dir = art_dir / 'bundle_q1q2' / 'report_q1q2'
    if report_dir.exists():
        for p in sorted(report_dir.rglob('*.tex')):
            out["tables"].setdefault('tex', []).append(rel(p))
        for p in sorted(report_dir.rglob('*.md')):
            out["texts"].setdefault('md', []).append(rel(p))

    for p in sorted(art_dir.glob('*.md')):
        out["texts"].setdefault('md', []).append(rel(p))
    for p in sorted(art_dir.glob('*.txt')):
        out["texts"].setdefault('txt', []).append(rel(p))

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--eval_json', required=True)
    ap.add_argument('--config_json', required=True)
    ap.add_argument('--out_json', required=True)
    ap.add_argument('--domain', default='biosurfactant')
    ap.add_argument('--title', default=None)
    ap.add_argument('--scenario', default=None)
    ap.add_argument('--artifacts_dir', default=None)
    ap.add_argument('--artifact_glob_root', default=None)
    ap.add_argument('--force', action='store_true', help='Overwrite out_json if it exists.')
    args = ap.parse_args()

    out_path = Path(args.out_json)
    if out_path.exists() and not args.force:
        print(f'[SKIP] report_input already exists: {out_path.resolve()}')
        return 0

    eval_path = Path(args.eval_json)
    cfg_path = Path(args.config_json)
    if not eval_path.exists():
        raise FileNotFoundError(f'eval_json not found: {eval_path}')
    if not cfg_path.exists():
        raise FileNotFoundError(f'config_json not found: {cfg_path}')

    evald = _load_json(eval_path)
    cfg = _load_json(cfg_path)

    # Auto validation of synthetic datasets (creates bundle_q1q2/synthetic_validation.json)
    scenario_dir = eval_path.parent
    synth_dir = _find_synthetic_dir(scenario_dir)
    validation: Dict[str, Any] = {}
    if synth_dir is not None:
        try:
            validation = _compute_synthetic_validation(synth_dir)
        except Exception as e:
            validation = {"synthetic_dir": str(synth_dir), "error": f"validation_failed: {e}"}

    out_json_path = Path(args.out_json)
    synth_val_path = out_json_path.parent / "synthetic_validation.json"
    if validation:
        _write_json(synth_val_path, validation)

    wrapped: Dict[str, Any] = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'config': _normalize_config(cfg, args.scenario, args.title, args.domain),
        'validation': validation,
        'evaluation': evald,
        'a_priori_analysis': None,
        'delta_justification': None,
        'artifacts': None,
    }

    if args.artifacts_dir:
        art_dir = Path(args.artifacts_dir)
        root_override = Path(args.artifact_glob_root) if args.artifact_glob_root else None
        if art_dir.exists():
            wrapped['artifacts'] = _collect_artifacts(art_dir, root_override=root_override)
        else:
            wrapped['artifacts'] = {'error': f'artifacts_dir not found: {art_dir}'}

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(wrapped, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'[OK] Wrote report input JSON: {out_path.resolve()}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
