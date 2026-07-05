from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from datetime import datetime


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def get_nested(d, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def fmt(x, nd=3):
    if x is None:
        return "NA"
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return str(x)


def extract_rows(eval_data: dict, n_synthetic: int):
    rows = []

    for gen, d in eval_data.items():
        if not isinstance(d, dict):
            continue

        util = d.get("utility", {}) or {}
        best_model = util.get("best_model")

        model_results = util.get("model_results", {}) or {}

        tstr = None
        trtr = None

        if best_model and best_model in model_results:
            mr = model_results.get(best_model, {}) or {}
            tstr_obj = mr.get("TSTR")
            trtr_obj = mr.get("TRTR")

            if isinstance(tstr_obj, dict):
                tstr = tstr_obj.get("mean")
            else:
                tstr = tstr_obj

            if isinstance(trtr_obj, dict):
                trtr = trtr_obj.get("mean")
            else:
                trtr = trtr_obj

        # fallback: choose model with highest TSTR if best_model missing
        if tstr is None and model_results:
            best_candidate = None
            best_val = None
            for model_name, mr in model_results.items():
                t = mr.get("TSTR") if isinstance(mr, dict) else None
                val = t.get("mean") if isinstance(t, dict) else t
                try:
                    val_f = float(val)
                except Exception:
                    continue
                if best_val is None or val_f > best_val:
                    best_val = val_f
                    best_candidate = model_name
            best_model = best_model or best_candidate
            tstr = best_val

        dcr = get_nested(d, "privacy", "distance_to_closest_record", default={}) or {}
        median_dcr = dcr.get("median_distance")
        risk_count = get_nested(dcr, "privacy_risk_counts", "distance_below_0.1", default=None)

        risk_frac = None
        if risk_count is not None and n_synthetic:
            risk_frac = float(risk_count) / float(n_synthetic)

        fidelity = d.get("fidelity", {}) or {}
        corr = fidelity.get("correlation", {}) or {}
        corr_avg = corr.get("corr_avg")
        if corr_avg is None:
            corr_avg = corr.get("correlation_of_correlations")
        if corr_avg is None:
            corr_avg = fidelity.get("corr_avg")

        rows.append({
            "generator": gen,
            "best_model": best_model,
            "TSTR_R2": tstr,
            "TRTR_R2": trtr,
            "median_DCR": median_dcr,
            "risk_frac_DCR_lt_0p1": risk_frac,
            "risk_count_DCR_lt_0p1": risk_count,
            "corr_avg": corr_avg,
        })

    rows.sort(key=lambda r: (r["TSTR_R2"] is None, -(float(r["TSTR_R2"]) if r["TSTR_R2"] is not None else -999)))
    return rows


def write_csv(rows, path: Path):
    fieldnames = [
        "generator",
        "best_model",
        "TSTR_R2",
        "TRTR_R2",
        "median_DCR",
        "risk_frac_DCR_lt_0p1",
        "risk_count_DCR_lt_0p1",
        "corr_avg",
    ]

    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def write_md_table(rows, path: Path):
    lines = []
    lines.append("| Generator | Best model | TSTR R2 | TRTR R2 | Median DCR | DCR<0.1 (%) | Corr-of-corr |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")

    for r in rows:
        risk_pct = None if r["risk_frac_DCR_lt_0p1"] is None else 100 * float(r["risk_frac_DCR_lt_0p1"])
        lines.append(
            f"| {r['generator']} | {r['best_model']} | {fmt(r['TSTR_R2'])} | {fmt(r['TRTR_R2'])} | "
            f"{fmt(r['median_DCR'])} | {fmt(risk_pct, 1)} | {fmt(r['corr_avg'])} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_figures_tex(outdir: Path):
    figdir = outdir / "q1q2_figures"
    figs = [
        ("fig1_utility_comparison", "Generator utility comparison using TSTR signed R2."),
        ("fig2_privacy_comparison", "Median distance to closest real record (DCR); higher values indicate lower proximity to original experimental records."),
        ("fig3_fidelity_comparison", "Fidelity comparison based on preservation of correlation structure."),
    ]

    lines = []
    for name, caption in figs:
        png = figdir / f"{name}.png"
        if png.exists():
            rel = f"q1q2_figures/{name}.png"
            lines.extend([
                "\\begin{figure}[htbp]",
                "\\centering",
                f"\\includegraphics[width=0.92\\linewidth]{{{rel}}}",
                f"\\caption{{{caption}}}",
                f"\\label{{fig:{name}}}",
                "\\end{figure}",
                "",
            ])

    (outdir / "figures.tex").write_text("\n".join(lines), encoding="utf-8")


def write_report(rows, cfg, scenario, title, outdir: Path):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    best = rows[0] if rows else None

    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"Scenario: **{scenario}**")
    lines.append(f"Generated at: {now}")
    lines.append("")
    lines.append("## Experimental and computational setup")
    lines.append("")
    lines.append(f"- Target variable: `{cfg.get('target_column', 'surface_tension_mNm')}`")
    lines.append(f"- Number of synthetic samples per generator: `{cfg.get('n_synthetic', 'NA')}`")
    lines.append(f"- Number of repeated evaluations: `{cfg.get('n_runs', 'NA')}`")
    lines.append(f"- DOE noise enabled: `{cfg.get('enable_doe_noise', 'NA')}`")
    lines.append(f"- DOE noise percentage: `{cfg.get('doe_noise_pct', 'NA')}`")
    lines.append(f"- DCR threshold tau: `{cfg.get('dcr_tau', 'NA')}`")
    lines.append("")
    lines.append("## Main performance table")
    lines.append("")
    lines.append("| Generator | Best model | TSTR R2 | TRTR R2 | Median DCR | DCR<0.1 (%) | Corr-of-corr |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")

    for r in rows:
        risk_pct = None if r["risk_frac_DCR_lt_0p1"] is None else 100 * float(r["risk_frac_DCR_lt_0p1"])
        lines.append(
            f"| {r['generator']} | {r['best_model']} | {fmt(r['TSTR_R2'])} | {fmt(r['TRTR_R2'])} | "
            f"{fmt(r['median_DCR'])} | {fmt(risk_pct, 1)} | {fmt(r['corr_avg'])} |"
        )

    lines.append("")
    lines.append("## Results summary")
    lines.append("")

    if best:
        lines.append(
            f"The best utility result was obtained by **{best['generator']}**, "
            f"with TSTR signed R2 = **{fmt(best['TSTR_R2'])}** using the `{best['best_model']}` model."
        )
        lines.append("")

    lines.append(
        "The results confirm that synthetic-data quality in small-n bioprocess datasets should not be judged by a single metric. "
        "Utility, proximity to real records, and preservation of correlation structure describe complementary aspects of model behavior."
    )
    lines.append("")
    lines.append(
        "In this biosurfactant dataset, the most useful generators are those that preserve predictive behavior for surface tension "
        "while avoiding excessive proximity to the original DOE records. This supports the use of synthetic expansion as a controlled "
        "proxy for process-model exploration, provided that physical and chemical plausibility is interpreted together with statistical metrics."
    )
    lines.append("")
    lines.append("## Figure references")
    lines.append("")
    lines.append("- Figure 1: Utility comparison based on TSTR signed R2.")
    lines.append("- Figure 2: Median DCR comparison.")
    lines.append("- Figure 3: Fidelity comparison based on correlation preservation.")
    lines.append("")
    lines.append("## Notes for manuscript integration")
    lines.append("")
    lines.append(
        "These outputs are intended to support the Results and Discussion sections of the manuscript. "
        "For the final article, captions should clarify that DCR median and DCR risk fraction are different privacy/proximity indicators."
    )
    lines.append("")

    md_path = outdir / "comprehensive_report.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    tex_lines = []
    tex_lines.append("\\section*{" + title.replace("_", "\\_") + "}")
    tex_lines.append("")
    tex_lines.append("\\subsection*{Main performance table}")
    tex_lines.append("\\begin{tabular}{lllllll}")
    tex_lines.append("\\hline")
    tex_lines.append("Generator & Best model & TSTR R2 & TRTR R2 & Median DCR & DCR$<0.1$ (\\%) & Corr. \\\\")
    tex_lines.append("\\hline")
    for r in rows:
        risk_pct = None if r["risk_frac_DCR_lt_0p1"] is None else 100 * float(r["risk_frac_DCR_lt_0p1"])
        tex_lines.append(
            f"{r['generator'].replace('_','\\_')} & {str(r['best_model']).replace('_','\\_')} & "
            f"{fmt(r['TSTR_R2'])} & {fmt(r['TRTR_R2'])} & {fmt(r['median_DCR'])} & "
            f"{fmt(risk_pct, 1)} & {fmt(r['corr_avg'])} \\\\"
        )
    tex_lines.append("\\hline")
    tex_lines.append("\\end{tabular}")
    tex_lines.append("")
    tex_lines.append("\\input{figures.tex}")
    tex_lines.append("")

    tex_path = outdir / "comprehensive_report.tex"
    tex_path.write_text("\n".join(tex_lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--scenario", required=True)
    ap.add_argument("--title", required=True)
    args = ap.parse_args()

    root = Path(args.root)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    eval_json = root / "evaluation_results.json"
    config_json = root / "experiment_config.json"

    ev = read_json(eval_json)
    cfg = read_json(config_json)

    n_synth = int(cfg.get("n_synthetic", 140))
    rows = extract_rows(ev, n_synth)

    write_csv(rows, outdir / "article_table.csv")
    write_md_table(rows, outdir / "article_table.md")
    write_figures_tex(outdir)
    write_report(rows, cfg, args.scenario, args.title, outdir)

    print("[OK] Wrote fallback report files:")
    for fn in ["comprehensive_report.md", "comprehensive_report.tex", "article_table.csv", "article_table.md", "figures.tex"]:
        p = outdir / fn
        print(f" - {p} ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
