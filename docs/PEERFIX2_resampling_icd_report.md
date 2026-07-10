# PEERFIX2 Utility Resampling and ICD Aggregation Report

> Mode: exported synthetic datasets. This is a downstream-model resampling audit unless the supplied dirs come from fold-specific generator refits.

## Utility: best downstream model per generator

### baseline_0pct
| generator       | model   | scheme         |   n_score_units |   TSTR_mean |   TSTR_ci95_low |   TSTR_ci95_high |   TRTR_mean |   Delta_mean |
|:----------------|:--------|:---------------|----------------:|------------:|----------------:|-----------------:|------------:|-------------:|
| tvae            | lr      | repeated_kfold |               3 |      0.1935 |          0.1935 |           0.1935 |     -0.6541 |       0.8477 |
| gaussian_copula | lr      | repeated_kfold |               3 |      0.1908 |          0.1908 |           0.1908 |     -0.6541 |       0.8449 |
| tabddpm         | lr      | repeated_kfold |               3 |      0.0657 |          0.0657 |           0.0657 |     -0.6541 |       0.7198 |
| ctgan           | lr      | repeated_kfold |               3 |     -0.0777 |         -0.0777 |          -0.0777 |     -0.6541 |       0.5764 |

### sensitivity_1pct
| generator       | model   | scheme         |   n_score_units |   TSTR_mean |   TSTR_ci95_low |   TSTR_ci95_high |   TRTR_mean |   Delta_mean |
|:----------------|:--------|:---------------|----------------:|------------:|----------------:|-----------------:|------------:|-------------:|
| gaussian_copula | lr      | repeated_kfold |               3 |      0.1957 |          0.1957 |           0.1957 |     -0.6541 |       0.8498 |
| tvae            | lr      | repeated_kfold |               3 |      0.1226 |          0.1226 |           0.1226 |     -0.6541 |       0.7767 |
| ctgan           | lr      | repeated_kfold |               3 |      0.0009 |          0.0009 |           0.0009 |     -0.6541 |       0.6551 |
| tabddpm         | lr      | repeated_kfold |               3 |     -0.5444 |         -0.5444 |          -0.5444 |     -0.6541 |       0.1097 |

## ICD aggregation

### baseline_0pct
| generator       |   n_realisations |   ICD_mean | ICD_ci95_low   | ICD_ci95_high   |   mean_S_mean |   mean_M_mean |   mean_D_mean |   spurious_rate_mean |
|:----------------|-----------------:|-----------:|:---------------|:----------------|--------------:|--------------:|--------------:|---------------------:|
| tvae            |                1 |     0.6670 |                |                 |        1.0000 |        0.0000 |        1.0000 |               0.0000 |
| tabddpm         |                1 |     0.5000 |                |                 |        1.0000 |        0.0000 |        0.5000 |               0.0000 |
| gaussian_copula |                1 |     0.3330 |                |                 |        0.5000 |        0.0000 |        0.5000 |               0.0000 |
| ctgan           |                1 |     0.0000 |                |                 |        0.0000 |        0.0000 |        0.0000 |               0.0000 |

### sensitivity_1pct
| generator       |   n_realisations |   ICD_mean | ICD_ci95_low   | ICD_ci95_high   |   mean_S_mean |   mean_M_mean |   mean_D_mean |   spurious_rate_mean |
|:----------------|-----------------:|-----------:|:---------------|:----------------|--------------:|--------------:|--------------:|---------------------:|
| tvae            |                1 |     0.4630 |                |                 |        1.0000 |        0.0000 |        0.5000 |               0.3750 |
| gaussian_copula |                1 |     0.3330 |                |                 |        0.5000 |        0.0000 |        0.5000 |               0.0000 |
| tabddpm         |                1 |     0.3080 |                |                 |        0.5000 |        0.0000 |        0.5000 |               0.2500 |
| ctgan           |                1 |     0.1540 |                |                 |        0.5000 |        0.0000 |        0.0000 |               0.1250 |

## Interpretation guardrails
- LOOCV R² is computed after aggregating all out-of-fold predictions; it is not computed on single held-out points.
- If `n_realisations=1`, ICD confidence intervals are intentionally blank; the final manuscript should use repeated synthetic realisations.
- For leakage-free utility claims, synthetic data must be regenerated inside each training fold. Exported full-dataset synthetic samples are suitable only as a downstream-model audit.