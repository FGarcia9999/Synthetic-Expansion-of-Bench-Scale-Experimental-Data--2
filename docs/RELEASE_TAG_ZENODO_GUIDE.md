# RELEASE_TAG_ZENODO_GUIDE

## Por que fazer release/tag antes da submissão
Branch é móvel; tag/release é referência estável. Para revisão Q1/Q2, o ideal é apontar o Data Availability Statement para uma release versionada e, se possível, DOI Zenodo.

## Sequência recomendada

```powershell
git switch peer-review-revisions-v1
git status
python -m py_compile .\code\q1q2_peerfix2_cv_icd.py .\code\q1q2_peerfix2_orchestrate.py .\code\q1q2_peerfix2_collect_fold_refit.py
git add code docs outputs data README.md SAFE_BASELINE_MANIFEST.md
git commit -m "Add PEERFIX2 resampling and ICD aggregation workflow"
git tag -a v0.2.0-peerfix2 -m "PEERFIX2 final validation workflow for Q1/Q2 submission"
git push origin peer-review-revisions-v1
git push origin v0.2.0-peerfix2
```

Depois:
1. GitHub → Releases → Draft a new release → escolha `v0.2.0-peerfix2`.
2. Título sugerido: `PEERFIX2 Q1/Q2 validation workflow`.
3. Anexe pacote com manuscrito, dados, códigos e outputs finais.
4. Zenodo → GitHub integration → habilitar o repositório → gerar DOI da release.
5. Atualizar o Data Availability Statement com o DOI.

## Observação sobre tokens
Nunca cole PAT em prompt, README, commit, script ou print. Use GitHub CLI (`gh auth login`) ou variável de ambiente local temporária.
