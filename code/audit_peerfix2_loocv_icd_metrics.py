from __future__ import annotations

import json
import math
import statistics as st
from pathlib import Path
from collections import defaultdict

import pandas as pd


ROOT = Path(".")
VALDIR = ROOT / "outputs" / "peerfix2" / "peerfix2_validation"

OUT = Path(r".\\outputs\\loocv_icd_processing_20260710_0203")
OUT.mkdir(parents=True, exist_ok=True)

json_files = sorted(VALDIR.glob("*.json"))

if not json_files:
    raise SystemExit(f"No JSON files found in {VALDIR}")


def walk(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            yield from walk(v, key)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            key = f"{prefix}[{i}]"
            yield from walk(v, key)
    else:
        yield prefix, obj


rows = []

for fp in json_files:
    data = json.loads(fp.read_text(encoding="utf-8"))
    for path, value in walk(data):
        if isinstance(value, bool):
            continue
        if isinstance(value, int) or isinstance(value, float):
            if math.isfinite(float(value)):
                rows.append({
                    "file": fp.name,
                    "metric_path": path,
                    "value": float(value),
                })

df = pd.DataFrame(rows)

if df.empty:
    raise SystemExit("No numeric metrics found in PEERFIX2 JSON files.")

df.to_csv(OUT / "peerfix2_numeric_inventory.csv", index=False, encoding="utf-8-sig")

keywords = [
    "loocv", "leave", "fold", "kfold", "cv",
    "tstr", "trtr", "delta", "Δ",
    "icd", "dcr", "privacy",
    "fidelity", "corr", "utility", "r2", "r_squared"
]

mask = df["metric_path"].str.lower().apply(
    lambda s: any(k.lower() in s for k in keywords)
)

cand = df[mask].copy()
cand.to_csv(OUT / "peerfix2_candidate_metrics_long.csv", index=False, encoding="utf-8-sig")


def ci95(values):
    values = list(values)
    n = len(values)
    if n <= 1:
        return float("nan"), float("nan"), float("nan")
    mean = st.mean(values)
    sd = st.stdev(values)
    se = sd / math.sqrt(n)
    # aproximação conservadora normal; suficiente para auditoria técnica inicial
    half = 1.96 * se
    return mean, mean - half, mean + half


summary_rows = []

for metric_path, g in cand.groupby("metric_path"):
    values = g["value"].tolist()
    mean, lo, hi = ci95(values)
    summary_rows.append({
        "metric_path": metric_path,
        "n": len(values),
        "mean": mean,
        "sd": st.stdev(values) if len(values) > 1 else float("nan"),
        "ci95_low": lo,
        "ci95_high": hi,
        "min": min(values),
        "max": max(values),
        "files": "; ".join(sorted(g["file"].unique())),
    })

summary = pd.DataFrame(summary_rows).sort_values(
    ["metric_path", "n"], ascending=[True, False]
)

summary.to_csv(OUT / "peerfix2_candidate_metrics_summary.csv", index=False, encoding="utf-8-sig")

md = []
md.append("# PEERFIX2 LOOCV/ICD Metric Audit\n")
md.append(f"Validation directory: `{VALDIR}`\n")
md.append(f"JSON files analysed: {len(json_files)}\n")
md.append("\n## Files\n")
for fp in json_files:
    md.append(f"- `{fp.name}` — {fp.stat().st_size} bytes\n")

md.append("\n## Candidate metric summary\n")
md.append("\n")
md.append(summary.to_markdown(index=False))
md.append("\n")

(OUT / "peerfix2_loocv_icd_audit.md").write_text("".join(md), encoding="utf-8")

print("[OK] PEERFIX2 metric inventory generated:")
print(f" - {OUT / 'peerfix2_numeric_inventory.csv'}")
print(f" - {OUT / 'peerfix2_candidate_metrics_long.csv'}")
print(f" - {OUT / 'peerfix2_candidate_metrics_summary.csv'}")
print(f" - {OUT / 'peerfix2_loocv_icd_audit.md'}")
