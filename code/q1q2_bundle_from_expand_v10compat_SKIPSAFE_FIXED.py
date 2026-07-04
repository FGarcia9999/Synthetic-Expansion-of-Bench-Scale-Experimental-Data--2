#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
q1q2_bundle_from_expand_v10compat_SKIPSAFE.py
==============================================

Generates Q1/Q2 publication-ready figures from EXPAND pipeline outputs.

Inputs:
  --real_csv      Path to original dados.csv
  --eval_json     Path to evaluation_results.json
  --config_json   Path to experiment_config.json
  --outdir        Output directory for bundle

Outputs:
  <outdir>/q1q2_figures/          PNG and PDF figures
  <outdir>/figures_manifest.json  List of generated figures
  <outdir>/figures.tex            LaTeX snippet for including figures
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List
import warnings
warnings.filterwarnings('ignore')

# Force UTF-8 output for Windows console
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--real_csv', required=True)
    ap.add_argument('--eval_json', required=True)
    ap.add_argument('--config_json', required=True)
    ap.add_argument('--outdir', required=True)
    # Optional metadata
    ap.add_argument('--scenario', nargs='+', default=None)
    ap.add_argument('--title', nargs='+', default=None)
    ap.add_argument('--domain', nargs='+', default=None)
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args()

    # Normalize optional text args
    scenario_str = ' '.join(args.scenario).strip() if args.scenario else None
    title_str = ' '.join(args.title).strip() if args.title else None
    domain_str = ' '.join(args.domain).strip() if args.domain else None

    outdir = Path(args.outdir)
    fig_dir = outdir / 'q1q2_figures'
    
    # Check if already exists
    manifest_path = outdir / 'figures_manifest.json'
    if manifest_path.exists() and not args.force:
        print(f'[SKIP] Figures already generated: {manifest_path}')
        return 0

    # Create output directory
    fig_dir.mkdir(parents=True, exist_ok=True)
    
    print(f'[INFO] Generating Q1/Q2 figures...')
    print(f'  Real CSV: {args.real_csv}')
    print(f'  Eval JSON: {args.eval_json}')
    print(f'  Config JSON: {args.config_json}')
    print(f'  Output: {fig_dir}')

    # Load data
    try:
        import pandas as pd
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        eval_data = json.loads(Path(args.eval_json).read_text(encoding='utf-8'))
        config = json.loads(Path(args.config_json).read_text(encoding='utf-8'))
        real_df = pd.read_csv(args.real_csv)
        
    except Exception as e:
        print(f'[ERROR] Failed to load data: {e}')
        return 1

    # Configure plotting style
    plt.style.use('seaborn-v0_8-paper')
    sns.set_palette("husl")
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['font.size'] = 10
    plt.rcParams['savefig.bbox'] = 'tight'
    plt.rcParams['savefig.pad_inches'] = 0.1

    generated_figures: List[Dict[str, Any]] = []

    # Extract generators
    generators = [g for g in eval_data.keys() if g in ['gaussian_copula', 'ctgan', 'tvae', 'tabddpm']]
    
    print(f'[INFO] Found {len(generators)} generators: {generators}')

    # ========================================================================
    # FIGURE 1: Utility Comparison (TSTR by generator)
    # ========================================================================
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        gen_names = []
        tstr_values = []
        
        for gen in generators:
            if 'utility' in eval_data[gen]:
                best_model = eval_data[gen]['utility'].get('best_model', 'rf')
                if best_model in eval_data[gen]['utility']['model_results']:
                    tstr = eval_data[gen]['utility']['model_results'][best_model]['TSTR']
                    if isinstance(tstr, dict):
                        tstr_val = tstr.get('mean', 0)
                    else:
                        tstr_val = tstr
                    
                    gen_names.append(gen.replace('_', ' ').title())
                    tstr_values.append(float(tstr_val))
        
        if gen_names:
            colors = sns.color_palette("husl", len(gen_names))
            bars = ax.bar(range(len(gen_names)), tstr_values, color=colors, alpha=0.8)
            
            ax.set_xlabel('Generator', fontweight='bold')
            ax.set_ylabel('TSTR ($R^2$; signed) - higher is better', fontweight='bold')
            ax.set_title('Generator Performance Comparison (Utility via TSTR)', fontweight='bold', fontsize=12)
            ax.set_xticks(range(len(gen_names)))
            ax.set_xticklabels(gen_names, rotation=15, ha='right')
            ax.grid(axis='y', alpha=0.3)
            ax.axhline(0.0, linewidth=1.0, alpha=0.6)
            
            # Add values on bars
            for bar in bars:
                height = bar.get_height()
                va = 'bottom' if height >= 0 else 'top'
                offset = 0.01 if height >= 0 else -0.01
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + offset,
                    f'{height:.3f}',
                    ha='center', va=va, fontsize=9
                )
            
            plt.tight_layout()
            
            fig_path_png = fig_dir / 'fig1_utility_comparison.png'
            fig_path_pdf = fig_dir / 'fig1_utility_comparison.pdf'
            
            plt.savefig(fig_path_png, dpi=300, bbox_inches='tight')
            plt.savefig(fig_path_pdf, bbox_inches='tight')
            plt.close()
            
            generated_figures.append({
                'id': 'fig1',
                'title': 'Utility Comparison (TSTR)',
                'png': str(fig_path_png.relative_to(outdir)),
                'pdf': str(fig_path_pdf.relative_to(outdir))
            })
            
            print(f'  [OK] Generated Figure 1: Utility Comparison')
        
    except Exception as e:
        print(f'  [WARN] Failed to generate Figure 1: {e}')

    # ========================================================================
    # FIGURE 2: Privacy Comparison (DCR median)
    # ========================================================================
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        gen_names = []
        dcr_values = []
        
        for gen in generators:
            if 'privacy' in eval_data[gen]:
                if 'distance_to_closest_record' in eval_data[gen]['privacy']:
                    dcr = eval_data[gen]['privacy']['distance_to_closest_record'].get('median_distance', 0)
                    gen_names.append(gen.replace('_', ' ').title())
                    dcr_values.append(dcr)
        
        if gen_names:
            colors = sns.color_palette("husl", len(gen_names))
            bars = ax.bar(range(len(gen_names)), dcr_values, color=colors, alpha=0.8)
            
            ax.set_xlabel('Generator', fontweight='bold')
            ax.set_ylabel('DCR Median (Higher = Better Privacy)', fontweight='bold')
            ax.set_title('Privacy Comparison', fontweight='bold', fontsize=12)
            ax.set_xticks(range(len(gen_names)))
            ax.set_xticklabels(gen_names, rotation=15, ha='right')
            ax.axhline(0.1, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Risk threshold')
            ax.grid(axis='y', alpha=0.3)
            ax.legend()
            
            # Add values on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            
            fig_path_png = fig_dir / 'fig2_privacy_comparison.png'
            fig_path_pdf = fig_dir / 'fig2_privacy_comparison.pdf'
            
            plt.savefig(fig_path_png, dpi=300, bbox_inches='tight')
            plt.savefig(fig_path_pdf, bbox_inches='tight')
            plt.close()
            
            generated_figures.append({
                'id': 'fig2',
                'title': 'Privacy Comparison (DCR)',
                'png': str(fig_path_png.relative_to(outdir)),
                'pdf': str(fig_path_pdf.relative_to(outdir))
            })
            
            print(f'  [OK] Generated Figure 2: Privacy Comparison')
        
    except Exception as e:
        print(f'  [WARN] Failed to generate Figure 2: {e}')

    # ========================================================================
    # FIGURE 3: Fidelity Comparison (Correlation preservation)
    # ========================================================================
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        gen_names = []
        corr_values = []
        
        for gen in generators:
            if 'fidelity' in eval_data[gen]:
                if 'correlation_preservation' in eval_data[gen]['fidelity']:
                    corr = eval_data[gen]['fidelity']['correlation_preservation'].get('correlation_of_correlations', 0)
                    gen_names.append(gen.replace('_', ' ').title())
                    corr_values.append(abs(corr))  # Absolute value for comparison
        
        if gen_names:
            colors = sns.color_palette("husl", len(gen_names))
            bars = ax.bar(range(len(gen_names)), corr_values, color=colors, alpha=0.8)
            
            ax.set_xlabel('Generator', fontweight='bold')
            ax.set_ylabel('|Correlation of Correlations| (Higher = Better)', fontweight='bold')
            ax.set_title('Fidelity Comparison', fontweight='bold', fontsize=12)
            ax.set_xticks(range(len(gen_names)))
            ax.set_xticklabels(gen_names, rotation=15, ha='right')
            ax.set_ylim(0, 1)
            ax.grid(axis='y', alpha=0.3)
            
            # Add values on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            
            fig_path_png = fig_dir / 'fig3_fidelity_comparison.png'
            fig_path_pdf = fig_dir / 'fig3_fidelity_comparison.pdf'
            
            plt.savefig(fig_path_png, dpi=300, bbox_inches='tight')
            plt.savefig(fig_path_pdf, bbox_inches='tight')
            plt.close()
            
            generated_figures.append({
                'id': 'fig3',
                'title': 'Fidelity Comparison (Correlation)',
                'png': str(fig_path_png.relative_to(outdir)),
                'pdf': str(fig_path_pdf.relative_to(outdir))
            })
            
            print(f'  [OK] Generated Figure 3: Fidelity Comparison')
        
    except Exception as e:
        print(f'  [WARN] Failed to generate Figure 3: {e}')

    # ========================================================================
    # Create manifest
    # ========================================================================
    manifest = {
        'generated_at': str(pd.Timestamp.now()),
        'n_figures': len(generated_figures),
        'figures': generated_figures,
        'config': {
            'real_csv': args.real_csv,
            'eval_json': args.eval_json,
            'config_json': args.config_json,
            'scenario': scenario_str,
            'title': title_str,
            'domain': domain_str
        }
    }
    
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'[OK] Manifest written: {manifest_path}')

    # ========================================================================
    # Create LaTeX snippet
    # ========================================================================
    tex_lines = [
        '% Q1/Q2 Figures - Auto-generated',
        '% Include in your LaTeX document',
        '',
    ]
    
    for fig in generated_figures:
        tex_lines.extend([
            f"\\begin{{figure}}[ht]",
            f"  \\centering",
            f"  \\includegraphics[width=0.8\\textwidth]{{{fig['pdf']}}}",
            f"  \\caption{{{fig['title']}}}",
            f"  \\label{{{fig['id']}}}",
            f"\\end{{figure}}",
            '',
        ])
    
    tex_path = outdir / 'figures.tex'
    tex_path.write_text('\n'.join(tex_lines), encoding='utf-8')
    print(f'[OK] LaTeX snippet written: {tex_path}')

    print(f'[SUCCESS] Generated {len(generated_figures)} figures')
    return 0


if __name__ == '__main__':
    sys.exit(main())
