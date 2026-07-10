# PIPELINE_ORQUESTRACAO_PEERFIX2 — sequência final antes da submissão

## Objetivo
Fechar os dois pontos estatísticos ainda pendentes:

1. TSTR/TRTR/Δ com LOOCV ou k-fold repetido, sem calcular R² em um único ponto isolado.
2. ICD com média ± IC95% em baseline e sensibilidade, usando múltiplas realizações sintéticas.

## Decisão metodológica recomendada
Para submissão Q1/Q2, use dois blocos complementares:

### Bloco A — ICD agregado por realizações sintéticas completas
Rode o pipeline completo 10 vezes por cenário, mudando a seed. Cada rodada gera uma realização sintética completa por gerador. Depois agregue o ICD como média ± IC95%.

### Bloco B — Utilidade estrita com refit por fold
Para evitar vazamento de informação, o dado sintético de cada fold deve ser gerado **somente a partir dos 19 pontos de treino** (LOOCV) ou do subconjunto de treino do k-fold. O teste fica completamente fora da geração sintética.

## Comandos principais — PowerShell

### 0) Preparação
```powershell
cd C:\Users\famg\Downloads\Synthetic-Expansion-of-Bench-Scale-Experimental-Data--2
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 1) Gerar plano de execução PEERFIX2
```powershell
python .\code\q1q2_peerfix2_orchestrate.py `
  --expand_script .\code\expand_synthetic_enhanced_v10_TUNED_Q1Q2_FIXED25_TABDDPM_PATCHED_v9_Q1Q2_ARTIFACTS_PEERFIX1.py `
  --real .\data\dados.csv `
  --target surface_tension_mNm `
  --outdir .\runs\peerfix2_final_validation `
  --mode both `
  --cv repeated_kfold `
  --n_splits 5 `
  --n_repeats_cv 10 `
  --n_generator_repeats 10 `
  --n_synthetic 140 `
  --seed 123
```

O comando acima cria `commands.ps1`. Revise o arquivo antes de executar.

### 2) Executar o plano
```powershell
.\runs\peerfix2_final_validation\commands.ps1
```

### 3) Agregar ICD das realizações completas
```powershell
python .\code\q1q2_peerfix2_cv_icd.py `
  --real .\data\dados.csv `
  --target surface_tension_mNm `
  --baseline_synth ".\runs\peerfix2_final_validation\full_repeats\baseline_0pct\seed_*\synthetic_datasets" `
  --sensitivity_synth ".\runs\peerfix2_final_validation\full_repeats\sensitivity_1pct\seed_*\synthetic_datasets" `
  --scheme repeated_kfold `
  --n_splits 5 `
  --n_repeats 10 `
  --outdir .\outputs\peerfix2_final_tables
```

### 4) Coletar utilidade estrita por fold
```powershell
python .\code\q1q2_peerfix2_collect_fold_refit.py `
  --fold_root .\runs\peerfix2_final_validation\fold_refit_cv `
  --target surface_tension_mNm `
  --outdir .\outputs\peerfix2_final_tables
```

### 5) Gerar figuras finais
Rode os scripts de figuras usando os CSVs de `outputs\peerfix2_final_tables`. Atualize captions para informar explicitamente se a figura usa resultados PEERFIX2 finais.

## Critério de submissão
Submeta somente depois de:

- `fold_refit_utility_best_models.csv` existir para baseline e sensibilidade.
- `icd_aggregated_combined.csv` conter `n_realisations >= 10` por cenário/gerador.
- O README não exibir interpretações antigas no fluxo principal.
- A versão final do manuscrito não conter “NOTA DE REVISÃO”, checklist interno ou comentários de trabalho.
