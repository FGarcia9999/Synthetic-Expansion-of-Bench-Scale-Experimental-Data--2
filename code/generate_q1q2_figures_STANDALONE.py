#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_q1q2_figures_STANDALONE.py
====================================

ROBUST standalone script to generate Q1/Q2 publication figures.

Usage:
    python generate_q1q2_figures_STANDALONE.py \
        --baseline exp_out_v5_doe0pct_tau010 \
        --sensitivity exp_out_v5_doe1pct_tau010

Output:
    Creates fig1, fig2, fig3 in each scenario's bundle_q1q2/q1q2_figures/
"""

import argparse
import json
import sys
from pathlib import Path
import traceback

# Force UTF-8 for Windows
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def generate_figures_for_scenario(scenario_dir: Path, scenario_name: str) -> bool:
    """Generate all 3 figures for a single scenario."""
    
    print(f"\n{'='*60}")
    print(f"SCENARIO: {scenario_name}")
    print(f"{'='*60}")
    
    # Import here to catch errors early
    try:
        import numpy as np
        import pandas as pd
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("Install with: pip install numpy pandas matplotlib seaborn --break-system-packages")
        return False
    
    # Paths
    eval_json = scenario_dir / 'evaluation_results.json'
    fig_dir = scenario_dir / 'bundle_q1q2' / 'q1q2_figures'
    
    # Validate inputs
    if not eval_json.exists():
        print(f"[ERROR] Not found: {eval_json}")
        return False
    
    # Create output directory
    fig_dir.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Output directory: {fig_dir}")
    
    # Load data
    try:
        with open(eval_json, 'r', encoding='utf-8') as f:
            eval_data = json.load(f)
        print(f"[OK] Loaded evaluation data from {eval_json.name}")
    except Exception as e:
        print(f"[ERROR] Failed to load JSON: {e}")
        traceback.print_exc()
        return False
    
    # Configure plotting
    plt.style.use('seaborn-v0_8-paper')
    sns.set_palette("husl")
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.titlesize'] = 16
    
    # Extract generators
    generators = [g for g in eval_data.keys() if g in ['gaussian_copula', 'ctgan', 'tvae', 'tabddpm']]
    print(f"[INFO] Found {len(generators)} generators: {generators}")
    
    if not generators:
        print("[ERROR] No generators found in evaluation data!")
        return False
    
    success_count = 0
    
    # ========================================================================
    # FIGURE 1: Utility Comparison (TSTR by generator)
    # ========================================================================
    print("\n[FIG1] Generating Utility Comparison...")
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        gen_names = []
        tstr_values = []
        
        for gen in generators:
            try:
                utility = eval_data[gen].get('utility', {})
                best_model = utility.get('best_model', 'rf')
                model_results = utility.get('model_results', {})
                
                if best_model in model_results:
                    tstr = model_results[best_model].get('TSTR')
                    if tstr is not None:
                        if isinstance(tstr, dict):
                            tstr_val = tstr.get('mean', 0)
                        else:
                            tstr_val = float(tstr)
                        
                        gen_names.append(gen.replace('_', ' ').title())
                        tstr_values.append(tstr_val)
                        print(f"  {gen}: TSTR = {tstr_val:.4f}")
            except Exception as e:
                print(f"  [WARN] Skipping {gen}: {e}")
        
        if gen_names:
            colors = sns.color_palette("husl", len(gen_names))
            bars = ax.bar(range(len(gen_names)), tstr_values, color=colors, alpha=0.85, edgecolor='black', linewidth=1.2)
            
            ax.set_xlabel('Generator', fontweight='bold', fontsize=12)
            ax.set_ylabel('TSTR (R²; signed)', fontweight='bold', fontsize=12)
            ax.set_title(f'Generator Performance Comparison - {scenario_name}', 
                        fontweight='bold', fontsize=14, pad=20)
            ax.set_xticks(range(len(gen_names)))
            ax.set_xticklabels(gen_names, rotation=25, ha='right')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.axhline(0.0, color='red', linewidth=1.5, linestyle='--', alpha=0.6, label='Baseline (0)')
            ax.legend()
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                va = 'bottom' if height >= 0 else 'top'
                offset = 0.02 if height >= 0 else -0.02
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + offset,
                    f'{height:.3f}',
                    ha='center', va=va, fontsize=9, fontweight='bold'
                )
            
            plt.tight_layout()
            
            # Save with absolute paths and verify
            fig1_png = fig_dir / 'fig1_utility_comparison.png'
            fig1_pdf = fig_dir / 'fig1_utility_comparison.pdf'
            
            plt.savefig(str(fig1_png), dpi=300, bbox_inches='tight', facecolor='white')
            plt.savefig(str(fig1_pdf), bbox_inches='tight', facecolor='white')
            plt.close(fig)
            
            # VERIFY files exist
            if fig1_png.exists() and fig1_pdf.exists():
                print(f"  [SUCCESS] Figure 1 saved:")
                print(f"    PNG: {fig1_png} ({fig1_png.stat().st_size} bytes)")
                print(f"    PDF: {fig1_pdf} ({fig1_pdf.stat().st_size} bytes)")
                success_count += 1
            else:
                print(f"  [ERROR] Files not created!")
                return False
        else:
            print("  [WARN] No valid TSTR data found")
    except Exception as e:
        print(f"  [ERROR] Failed to create Figure 1: {e}")
        traceback.print_exc()
    
    # ========================================================================
    # FIGURE 2: Privacy Comparison (DCR median)
    # ========================================================================
    print("\n[FIG2] Generating Privacy Comparison...")
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        gen_names = []
        dcr_values = []
        
        for gen in generators:
            try:
                privacy = eval_data[gen].get('privacy', {})
                dcr_data = privacy.get('distance_to_closest_record', {})
                dcr = dcr_data.get('median_distance')
                
                if dcr is not None:
                    gen_names.append(gen.replace('_', ' ').title())
                    dcr_values.append(float(dcr))
                    print(f"  {gen}: DCR median = {dcr:.4f}")
            except Exception as e:
                print(f"  [WARN] Skipping {gen}: {e}")
        
        if gen_names:
            colors = sns.color_palette("husl", len(gen_names))
            bars = ax.bar(range(len(gen_names)), dcr_values, color=colors, alpha=0.85, edgecolor='black', linewidth=1.2)
            
            ax.set_xlabel('Generator', fontweight='bold', fontsize=12)
            ax.set_ylabel('DCR Median Distance (Higher = Better Privacy)', fontweight='bold', fontsize=12)
            ax.set_title(f'Privacy Risk Comparison - {scenario_name}', 
                        fontweight='bold', fontsize=14, pad=20)
            ax.set_xticks(range(len(gen_names)))
            ax.set_xticklabels(gen_names, rotation=25, ha='right')
            ax.axhline(0.1, color='red', linestyle='--', linewidth=1.5, alpha=0.6, 
                      label='Risk threshold (0.1)')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.legend()
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            plt.tight_layout()
            
            # Save with absolute paths
            fig2_png = fig_dir / 'fig2_privacy_comparison.png'
            fig2_pdf = fig_dir / 'fig2_privacy_comparison.pdf'
            
            plt.savefig(str(fig2_png), dpi=300, bbox_inches='tight', facecolor='white')
            plt.savefig(str(fig2_pdf), bbox_inches='tight', facecolor='white')
            plt.close(fig)
            
            # VERIFY
            if fig2_png.exists() and fig2_pdf.exists():
                print(f"  [SUCCESS] Figure 2 saved:")
                print(f"    PNG: {fig2_png} ({fig2_png.stat().st_size} bytes)")
                print(f"    PDF: {fig2_pdf} ({fig2_pdf.stat().st_size} bytes)")
                success_count += 1
            else:
                print(f"  [ERROR] Files not created!")
                return False
        else:
            print("  [WARN] No valid DCR data found")
    except Exception as e:
        print(f"  [ERROR] Failed to create Figure 2: {e}")
        traceback.print_exc()
    
    # ========================================================================
    # FIGURE 3: Fidelity Comparison (Correlation preservation)
    # ========================================================================
    print("\n[FIG3] Generating Fidelity Comparison...")
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        gen_names = []
        corr_values = []
        
        for gen in generators:
            try:
                fidelity = eval_data[gen].get('fidelity', {})
                corr_pres = fidelity.get('correlation_preservation', {})
                corr = corr_pres.get('correlation_of_correlations')
                
                if corr is not None:
                    gen_names.append(gen.replace('_', ' ').title())
                    corr_values.append(abs(float(corr)))  # Absolute value
                    print(f"  {gen}: Corr-of-Corr = {corr:.4f}")
            except Exception as e:
                print(f"  [WARN] Skipping {gen}: {e}")
        
        if gen_names:
            colors = sns.color_palette("husl", len(gen_names))
            bars = ax.bar(range(len(gen_names)), corr_values, color=colors, alpha=0.85, edgecolor='black', linewidth=1.2)
            
            ax.set_xlabel('Generator', fontweight='bold', fontsize=12)
            ax.set_ylabel('|Correlation of Correlations| (Closer to 1 = Better)', fontweight='bold', fontsize=12)
            ax.set_title(f'Fidelity Comparison - {scenario_name}', 
                        fontweight='bold', fontsize=14, pad=20)
            ax.set_xticks(range(len(gen_names)))
            ax.set_xticklabels(gen_names, rotation=25, ha='right')
            ax.set_ylim(0, 1)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            plt.tight_layout()
            
            # Save
            fig3_png = fig_dir / 'fig3_fidelity_comparison.png'
            fig3_pdf = fig_dir / 'fig3_fidelity_comparison.pdf'
            
            plt.savefig(str(fig3_png), dpi=300, bbox_inches='tight', facecolor='white')
            plt.savefig(str(fig3_pdf), bbox_inches='tight', facecolor='white')
            plt.close(fig)
            
            # VERIFY
            if fig3_png.exists() and fig3_pdf.exists():
                print(f"  [SUCCESS] Figure 3 saved:")
                print(f"    PNG: {fig3_png} ({fig3_png.stat().st_size} bytes)")
                print(f"    PDF: {fig3_pdf} ({fig3_pdf.stat().st_size} bytes)")
                success_count += 1
            else:
                print(f"  [ERROR] Files not created!")
                return False
        else:
            print("  [WARN] No valid correlation data found")
    except Exception as e:
        print(f"  [ERROR] Failed to create Figure 3: {e}")
        traceback.print_exc()
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"SCENARIO {scenario_name}: {success_count}/3 figures created")
    print(f"{'='*60}")
    
    return success_count == 3


def main():
    ap = argparse.ArgumentParser(description='Generate Q1/Q2 figures (ROBUST)')
    ap.add_argument('--baseline', required=True, help='Baseline scenario directory')
    ap.add_argument('--sensitivity', required=True, help='Sensitivity scenario directory')
    args = ap.parse_args()
    
    baseline_dir = Path(args.baseline)
    sensitivity_dir = Path(args.sensitivity)
    
    print("\n" + "="*70)
    print("Q1/Q2 FIGURE GENERATOR (ROBUST STANDALONE VERSION)")
    print("="*70)
    
    # Validate directories
    if not baseline_dir.exists():
        print(f"[ERROR] Baseline directory not found: {baseline_dir}")
        return 1
    
    if not sensitivity_dir.exists():
        print(f"[ERROR] Sensitivity directory not found: {sensitivity_dir}")
        return 1
    
    # Generate for both scenarios
    baseline_ok = generate_figures_for_scenario(baseline_dir, "Baseline (0% DOE-noise)")
    sensitivity_ok = generate_figures_for_scenario(sensitivity_dir, "Sensitivity (1% DOE-noise)")
    
    # Final report
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Baseline:    {'SUCCESS' if baseline_ok else 'FAILED'}")
    print(f"Sensitivity: {'SUCCESS' if sensitivity_ok else 'FAILED'}")
    
    if baseline_ok and sensitivity_ok:
        print("\n[SUCCESS] ALL FIGURES GENERATED!")
        print("\nFigures created:")
        for scenario in [baseline_dir, sensitivity_dir]:
            fig_dir = scenario / 'bundle_q1q2' / 'q1q2_figures'
            print(f"\n  {scenario.name}:")
            for fig in sorted(fig_dir.glob('*.png')):
                print(f"    - {fig.name} ({fig.stat().st_size} bytes)")
        return 0
    else:
        print("\n[ERROR] Some figures failed to generate!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
