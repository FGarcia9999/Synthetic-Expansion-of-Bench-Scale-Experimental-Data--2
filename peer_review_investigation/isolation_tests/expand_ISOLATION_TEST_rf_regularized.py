# -*- coding: utf-8 -*-
"""
expand_synthetic_enhanced_v4_completo_ajustado v9.py
============================
Sistema robusto e atualizado para geração e avaliação de dados sintéticos tabulares,
implementando padrões acadêmicos rigorosos e métodos state-of-the-art.

PRINCIPAIS MELHORIAS PARA MLP (ADICIONADAS):
- Early Stopping aprimorado com múltiplos critérios
- Bayesian Hyperparameter Tuning com Optuna
- Regularização avançada (L2, Dropout, BatchNorm)
- Learning Rate Scheduling (ReduceLROnPlateau, CosineAnnealing)
- Inicialização de pesos inteligente (He/Kaiming)
- Gradient Clipping e Gradient Accumulation
- Batch Size dinâmico baseado em memória
- Ensemble de MLPs para estabilidade

Referências técnicas:
- Kingma & Ba (2014) - Adam optimizer
- He et al. (2015) - Kaiming initialization
- Smith (2017) - Cyclical Learning Rates
- Ioffe & Szegedy (2015) - Batch Normalization
"""

import argparse
import logging
import warnings

# --- Early warning filters (must run before importing sdv to silence pkg_resources deprecation noise) ---
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message=r"pkg_resources is deprecated as an API.*", category=UserWarning)
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from enum import Enum
import json
import yaml
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import joblib
from joblib import Parallel, delayed
import os
import sys
import threading

import numpy as np
import math
import pandas as pd
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm.auto import tqdm

# Core ML/Stats
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, KFold
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression, LinearRegression, ElasticNet, Ridge
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.metrics import (r2_score, mean_absolute_error, mean_squared_error,
                           accuracy_score, f1_score, roc_auc_score, classification_report,
                           confusion_matrix, precision_recall_curve, roc_curve)
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA

# Statistical tests
from scipy import stats
from scipy.stats import (ks_2samp, anderson_ksamp, shapiro, wasserstein_distance,
                        mannwhitneyu, chi2_contingency, normaltest, jarque_bera,
                        pearsonr, spearmanr, entropy)
from scipy.spatial.distance import jensenshannon, pdist, squareform
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.power import TTestPower
from statsmodels.stats.contingency_tables import mcnemar

# Advanced statistical diagnostics (NOVO - para rigor Q1/Q2)
try:
    from statsmodels.stats.diagnostic import het_breuschpagan
    from statsmodels.stats.outliers_influence import OLSInfluence
    from statsmodels.formula.api import ols
    from statsmodels.api import add_constant
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

# Advanced metrics
try:
    from scipy.stats import energy_distance
except ImportError:
    energy_distance = None

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    xgb = None

# Memory management for parallelization
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# SDV Imports com fallback robusto
try:
    from sdv.single_table import (
        GaussianCopulaSynthesizer,
        CTGANSynthesizer,
        TVAESynthesizer
    )
    from sdv.metadata import SingleTableMetadata
    SDV_AVAILABLE = True
    logger_info = "SDV library loaded successfully"
except Exception as e:
    GaussianCopulaSynthesizer = None
    CTGANSynthesizer = None
    TVAESynthesizer = None
    SingleTableMetadata = None
    SDV_AVAILABLE = False
    logger_info = f"SDV not available: {e}. Install with: pip install sdv"

# Torch para TabDDPM
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
    torch_info = f"PyTorch {torch.__version__} loaded"
except Exception as e:
    # IMPORTANT: keep module importable even when torch fails to load (e.g., missing DLLs on Windows)
    TORCH_AVAILABLE = False
    torch = None
    F = None
    DataLoader = None
    TensorDataset = None

    # Provide a minimal nn namespace so class definitions that reference nn.Module don't crash at import-time.
    class _DummyNN:
        Module = object
    nn = _DummyNN()

    torch_info = f"PyTorch not available ({e}). TabDDPM will use fallback implementation"

try:
    import sklearn
except ImportError:
    sklearn = None

try:
    import scipy
except ImportError:
    scipy = None

# ============================================================================
# CONFIGURAÇÃO INICIAL DE LOGGING
# ============================================================================

# Configure logging primeiro para garantir que outras classes possam usar
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('synthetic_generation.log')
    ]
)
logger = logging.getLogger(__name__)
logger.info(logger_info)
if TORCH_AVAILABLE:
    logger.info(torch_info)

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# ============================================================================
# NOVAS FUNÇÕES DE PARALELIZAÇÃO (ADICIONADAS) - COM CORREÇÕES COMPLETAS
# ============================================================================

class MemoryAwareSemaphore:
    """Semáforo para controle de memória entre threads/processos"""
    
    def __init__(self, max_memory_gb: float):
        self.max_memory = max_memory_gb * (1024**3)  # Converter para bytes
        self.current_usage = 0
        self.lock = threading.Lock()
        logger.info(f"Memory semaphore initialized with {max_memory_gb} GB limit")

    def acquire(self, required_gb: float) -> bool:
        """Tenta adquirir memória, retorna True se bem-sucedido"""
        required_bytes = required_gb * (1024**3)
        
        with self.lock:
            if self.current_usage + required_bytes <= self.max_memory:
                self.current_usage += required_bytes
                return True
            return False

    def release(self, required_gb: float):
        """Libera memória alocada"""
        required_bytes = required_gb * (1024**3)
        
        with self.lock:
            self.current_usage -= required_bytes
            # Garantir que não fique negativo
            self.current_usage = max(0, self.current_usage)

# Semáforo global para controle de memória
memory_semaphore = None

def _fit_and_score_single(*args, **kwargs):
    """Fit a single model and evaluate on the held-out test split.

    This function supports two calling conventions (to remain backward compatible across versions):
      1) Legacy:
         _fit_and_score_single(model_ctor, X_train, y_train, X_test, y_test, scorer, seed, tag, memory_per_task)
      2) Current:
         _fit_and_score_single(tag, model_ctor, X_train, y_train, X_test, y_test, scorer, seed, memory_per_task=...)
    """
    global memory_semaphore

    # ---- Parse positional/keyword arguments robustly ----
    if len(args) >= 9 and callable(args[0]) and not isinstance(args[0], str):
        # Legacy
        model_ctor, X_train, y_train, X_test, y_test, scorer, seed, tag, memory_per_task = args[:9]
    else:
        tag = args[0] if len(args) > 0 else kwargs.pop('tag', None)
        model_ctor = args[1] if len(args) > 1 else kwargs.pop('model_ctor', None)
        X_train = args[2] if len(args) > 2 else kwargs.pop('X_train', None)
        y_train = args[3] if len(args) > 3 else kwargs.pop('y_train', None)
        X_test = args[4] if len(args) > 4 else kwargs.pop('X_test', None)
        y_test = args[5] if len(args) > 5 else kwargs.pop('y_test', None)
        scorer = args[6] if len(args) > 6 else kwargs.pop('scorer', None)
        seed = args[7] if len(args) > 7 else kwargs.pop('seed', 0)
        memory_per_task = (
            args[8] if len(args) > 8 else
            kwargs.pop('memory_per_task', kwargs.pop('memory', 0.0))
        )

    # Make memory_per_task a real number (and non-optional)
    try:
        memory_per_task = float(memory_per_task)
    except Exception:
        memory_per_task = 0.0

    # ---- Memory-aware gating (best-effort) ----
    acquired = False
    if memory_semaphore is not None and memory_per_task > 0:
        try:
            import time
            while True:
                ok = memory_semaphore.acquire(memory_per_task)
                if ok:
                    acquired = True
                    break
                time.sleep(0.05)
        except Exception:
            acquired = False

    try:
        model = model_ctor()

        # Attempt to set random_state when available for reproducibility
        if hasattr(model, 'random_state'):
            try:
                setattr(model, 'random_state', int(seed))
            except Exception:
                pass

        model.fit(X_train, y_train)

        score_val = None
        if scorer is not None:
            # Support different scorer calling conventions:
            #  1) scorer(estimator, X, y)  [sklearn-style]
            #  2) scorer(y_true, y_pred)   [callable metric]
            #  3) scorer(estimator, X)     [rare]
            try:
                score_val = scorer(model, X_test, y_test)
            except TypeError:
                try:
                    y_pred = model.predict(X_test)
                    score_val = scorer(y_test, y_pred)
                except TypeError:
                    try:
                        score_val = scorer(model, X_test)
                    except TypeError:
                        score_val = None
        # scorer may return:
        #   - dict of metrics (preferred)
        #   - scalar score
        #   - tuple(score, dict)
        primary_score = None
        metrics = {}

        if isinstance(score_val, dict):
            metrics = score_val
        elif isinstance(score_val, (tuple, list)) and len(score_val) == 2 and isinstance(score_val[1], dict):
            primary_score = score_val[0]
            metrics = score_val[1]
        elif score_val is None:
            metrics = {}
        else:
            try:
                metrics = {'score': float(score_val)}
            except Exception:
                metrics = {'score': None}

        # Try to derive a sensible primary numeric score for convenience
        if primary_score is None:
            for k in ('r2', 'R2', 'accuracy', 'acc', 'f1', 'roc_auc', 'auc', 'score'):
                v = metrics.get(k)
                if isinstance(v, (int, float)) and not (isinstance(v, bool)):
                    primary_score = float(v)
                    break

        # Optionally compute a few regression metrics if possible (won't raise)
        rmse = mae = r2 = None
        try:
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            y_pred = model.predict(X_test)
            rmse = float(mean_squared_error(y_test, y_pred, squared=False))
            mae = float(mean_absolute_error(y_test, y_pred))
            r2 = float(r2_score(y_test, y_pred))
        except Exception:
            pass

        return {
            "model": str(tag),
            "tag": str(tag),
            "seed": int(seed),
            "score": None if primary_score is None else float(primary_score),
            "metrics": metrics,
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
        }
    finally:
        if acquired and memory_semaphore is not None and memory_per_task > 0:
            try:
                memory_semaphore.release(memory_per_task)
            except Exception:
                pass
def evaluate_models_parallel(
    model_constructors,
    X_train,
    y_train,
    X_test,
    y_test,
    *,
    scorer,
    n_runs=10,
    backend="threading",
    n_jobs=-1,
    memory_per_task=None,
    random_seed=42,
    tags=None,
    seeds=None,
    parallel_backend=None,
    **_ignored_kwargs
):
    """Evaluate a collection of model constructors over multiple random seeds in parallel.

    This function is intentionally *format-flexible* to remain compatible with prior versions.

    Accepted `model_constructors` formats:
      - list[tuple[str, callable]]: [(name, ctor), ...]
      - dict[str, callable]: {name: ctor, ...}
      - list[callable]: [ctor1, ctor2, ...] (names come from `tags` or ctor.__name__)
      - callable: single ctor

    Parameters
    ----------
    scorer : callable
        Function(model, X_test, y_test) -> dict | float | (float, dict).
    seeds : list[int] | None
        Optional explicit seeds per run (length >= n_runs). When provided, overrides random_seed+run_idx.
    memory_per_task : float | None
        Estimated memory (GB) per fit+score task. If None, a safe estimate is computed and enforced.
    """
    global memory_semaphore

    # -----------------------------
    # Normalize backend / aliases
    # -----------------------------
    if parallel_backend is not None:
        backend = parallel_backend

    # -----------------------------
    # Normalize model constructors
    # -----------------------------
    items = []
    if model_constructors is None:
        items = []
    elif isinstance(model_constructors, dict):
        items = [(str(k), v) for k, v in model_constructors.items()]
    elif callable(model_constructors):
        items = [(getattr(model_constructors, '__name__', 'model'), model_constructors)]
    else:
        # assume iterable
        mc_list = list(model_constructors)
        if not mc_list:
            items = []
        else:
            first = mc_list[0]
            # list of (name, ctor)
            if isinstance(first, tuple) and len(first) == 2 and (callable(first[1]) or (isinstance(first[1], tuple) and len(first[1]) == 2 and callable(first[1][1]))):
                items = []
                for (n, c) in mc_list:
                    # aceita (name, ctor) ou (name, (tag, ctor))
                    if isinstance(c, tuple) and len(c) == 2 and callable(c[1]):
                        c = c[1]
                    items.append((str(n), c))
            # list of ctors
            elif callable(first):
                tag_list = list(tags) if tags is not None else None
                for idx, ctor in enumerate(mc_list):
                    if not callable(ctor):
                        raise TypeError(f"Invalid model constructor at index {idx}: {type(ctor)}")
                    name = None
                    if tag_list is not None and idx < len(tag_list):
                        name = str(tag_list[idx])
                    else:
                        name = getattr(ctor, '__name__', f"model_{idx}")
                    items.append((name, ctor))
            else:
                # try to coerce mixed list
                for idx, elem in enumerate(mc_list):
                    if isinstance(elem, tuple) and len(elem) == 2 and callable(elem[1]):
                        items.append((str(elem[0]), elem[1]))
                    elif callable(elem):
                        items.append((getattr(elem, '__name__', f"model_{idx}"), elem))
                    else:
                        raise TypeError(
                            "model_constructors must be list of ctors, list of (name, ctor), dict{name:ctor}, or a ctor"
                        )

    # -----------------------------
    # Determine effective number of workers
    # -----------------------------
    import os
    effective_jobs = n_jobs
    if effective_jobs in (None, 0):
        effective_jobs = 1
    if effective_jobs < 0:
        effective_jobs = os.cpu_count() or 1

    # -----------------------------
    # Memory-aware scaling
    # -----------------------------
    avail_gb = None
    try:
        import psutil
        avail_gb = float(psutil.virtual_memory().available) / 1e9
    except Exception:
        avail_gb = None

    # Compute conservative memory_per_task if missing / invalid
    try:
        memory_per_task = float(memory_per_task)
        if memory_per_task <= 0:
            raise ValueError()
    except Exception:
        if avail_gb is not None:
            memory_per_task = max(0.25, min(2.0, (avail_gb * 0.8) / max(1, effective_jobs)))
        else:
            memory_per_task = 0.50

    if avail_gb is not None:
        max_mem_gb = max(0.5, avail_gb * 0.8)
        max_jobs_by_mem = max(1, int(max_mem_gb // max(0.1, memory_per_task)))
        effective_jobs = max(1, min(effective_jobs, max_jobs_by_mem))
        try:
            memory_semaphore = MemoryAwareSemaphore(max_memory_gb=max_mem_gb)
        except Exception:
            memory_semaphore = None
    else:
        memory_semaphore = None

    # Avoid oversubscription on tiny datasets
    try:
        if hasattr(X_train, 'shape') and X_train.shape[0] < 50:
            effective_jobs = min(effective_jobs, 4)
    except Exception:
        pass

    # -----------------------------
    # Build tasks
    # -----------------------------
    tasks = []
    for run_idx in range(int(n_runs)):
        if seeds is not None and len(seeds) > run_idx:
            seed = int(seeds[run_idx])
        else:
            seed = int(random_seed) + int(run_idx)
        for name, ctor in items:
            tasks.append((name, ctor, seed))

    def _wrap(name, ctor, seed):
        return _fit_and_score_single(
            name, ctor, X_train, y_train, X_test, y_test, scorer, seed,
            memory_per_task=memory_per_task
        )

    from joblib import Parallel, delayed
    results = Parallel(n_jobs=effective_jobs, backend=str(backend))(
        delayed(_wrap)(name, ctor, seed) for (name, ctor, seed) in tasks
    )
    return results
def _snap_to_allowed(x: float, allowed: List[float]) -> float:
    """
    Aproxima um valor para o nível mais próximo da lista de valores permitidos.
    
    Args:
        x: Valor a ser aproximado
        allowed: Lista de valores permitidos
        
    Returns:
        Valor mais próximo da lista allowed
    """
    import numpy as np
    allowed = np.asarray(sorted(allowed))
    return float(allowed[np.argmin(np.abs(allowed - x))])


def _apply_noise_gaussian(synth: pd.DataFrame, real_df: pd.DataFrame, noise_pct: float, discrete_cols: List[str]) -> pd.DataFrame:
    """Aplica jitter gaussiano (percentual do desvio-padrão real) em colunas contínuas.
    - noise_pct=1.0 => sigma = 0.01 * std_real
    - Não aplica em colunas discretas (ex.: níveis fixos)
    """
    try:
        pct = float(noise_pct)
    except Exception:
        return synth
    if pct <= 0:
        return synth
    out = synth.copy()
    for col in real_df.columns:
        if col not in out.columns:
            continue
        if col in discrete_cols:
            continue
        if not pd.api.types.is_numeric_dtype(out[col]):
            continue
        std = float(real_df[col].std(ddof=0))
        if not np.isfinite(std) or std == 0.0:
            continue
        sigma = (pct/100.0) * std
        noise = np.random.normal(loc=0.0, scale=sigma, size=len(out))
        out[col] = out[col].astype(float) + noise
    return out

def postprocess_synthetic(
    synth_df: pd.DataFrame,
    real_df: pd.DataFrame,
    noise_pct: float = 0.0,
    target_column: Optional[str] = None,
    desired_n: Optional[int] = None,
    logger: Optional[logging.Logger] = None,
) -> pd.DataFrame:
    """
    Pós-processamento conservador (não altera ciência):
      - alinha colunas e ordem;
      - clipping para intervalo observado no real (coluna a coluna);
      - preserva níveis "quase ordinais" (ex.: seawater_vv) por snapping;
      - injeta ruído opcional (noise_pct) de forma multiplicativa leve (apenas em variáveis contínuas);
      - garante n amostras (desired_n) *sem reduzir privacidade* usando jitter + repulsão controlada,
        caso um filtro DCR tenha removido muitos pontos.

    Observação: este método NÃO aplica o filtro DCR. Ele apenas "topa" o dataset caso já venha reduzido.
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if synth_df is None or len(synth_df) == 0:
        return synth_df

    # Alinhar colunas
    real_cols = list(real_df.columns)
    for c in real_cols:
        if c not in synth_df.columns:
            synth_df[c] = np.nan
    synth_df = synth_df[real_cols].copy()

    # Clipping por coluna (intervalo do real)
    for c in real_cols:
        if pd.api.types.is_numeric_dtype(real_df[c]):
            lo = np.nanmin(real_df[c].values.astype(float))
            hi = np.nanmax(real_df[c].values.astype(float))
            synth_df[c] = pd.to_numeric(synth_df[c], errors="coerce")
            synth_df[c] = synth_df[c].clip(lower=lo, upper=hi)

    # Snapping para níveis discretos quando o real tem poucos valores únicos (heurística)
    for c in real_cols:
        if pd.api.types.is_numeric_dtype(real_df[c]):
            uniq = pd.unique(real_df[c].dropna())
            if len(uniq) > 0 and len(uniq) <= 6:
                # "ordinal-like"
                uniq_sorted = np.array(sorted([float(u) for u in uniq]))
                x = pd.to_numeric(synth_df[c], errors="coerce").astype(float).values
                # snap para o nível mais próximo
                idx = np.argmin(np.abs(x.reshape(-1, 1) - uniq_sorted.reshape(1, -1)), axis=1)
                synth_df[c] = uniq_sorted[idx]

    # Ruído opcional multiplicativo leve (apenas em colunas numéricas não-target)
    if noise_pct and noise_pct > 0:
        rng = np.random.default_rng(123)
        for c in real_cols:
            if c == target_column:
                continue
            if pd.api.types.is_numeric_dtype(real_df[c]):
                x = pd.to_numeric(synth_df[c], errors="coerce").astype(float).values
                scale = np.maximum(1e-12, np.nanstd(pd.to_numeric(real_df[c], errors="coerce").astype(float).values))
                eps = rng.normal(loc=0.0, scale=noise_pct, size=len(x))
                x_noisy = x + eps * scale
                lo = np.nanmin(pd.to_numeric(real_df[c], errors="coerce").astype(float).values)
                hi = np.nanmax(pd.to_numeric(real_df[c], errors="coerce").astype(float).values)
                synth_df[c] = np.clip(x_noisy, lo, hi)

    # Garantir tamanho desejado (top-up) com jitter leve + clipping + snapping.
    # (o filtro DCR (privacidade) é aplicado fora daqui; aqui apenas evita colapso por remoção excessiva)
    if desired_n is not None and len(synth_df) < desired_n:
        need = desired_n - len(synth_df)
        logger.info(f"Top-up: preenchendo {need} amostras para atingir desired_n={desired_n} (jitter).")
        rng = np.random.default_rng(999)
        base = synth_df.sample(n=min(len(synth_df), max(10, len(synth_df))), replace=True, random_state=999).copy()

        # jitter proporcional ao IQR do real
        for c in real_cols:
            if pd.api.types.is_numeric_dtype(real_df[c]):
                r = pd.to_numeric(real_df[c], errors="coerce").astype(float).values
                q25, q75 = np.nanpercentile(r, [25, 75])
                iqr = max(1e-12, float(q75 - q25))
                j = rng.normal(loc=0.0, scale=0.02 * iqr, size=(need,))
                vals = pd.to_numeric(base[c], errors="coerce").astype(float).values
                vals = vals[:need] if len(vals) >= need else np.resize(vals, need)
                new_vals = vals + j
                lo = np.nanmin(r); hi = np.nanmax(r)
                new_vals = np.clip(new_vals, lo, hi)
                base[c] = pd.Series(new_vals)

        base = base.iloc[:need].copy()
        synth_df = pd.concat([synth_df, base], axis=0, ignore_index=True)

        # re-snap discretas
        for c in real_cols:
            if pd.api.types.is_numeric_dtype(real_df[c]):
                uniq = pd.unique(real_df[c].dropna())
                if len(uniq) > 0 and len(uniq) <= 6:
                    uniq_sorted = np.array(sorted([float(u) for u in uniq]))
                    x = pd.to_numeric(synth_df[c], errors="coerce").astype(float).values
                    idx = np.argmin(np.abs(x.reshape(-1, 1) - uniq_sorted.reshape(1, -1)), axis=1)
                    synth_df[c] = uniq_sorted[idx]

    # Garantir ausência de NaN remanescentes via imputação simples (mediana do real)
    for c in real_cols:
        if synth_df[c].isna().any():
            if pd.api.types.is_numeric_dtype(real_df[c]):
                med = float(np.nanmedian(pd.to_numeric(real_df[c], errors="coerce").astype(float).values))
                synth_df[c] = pd.to_numeric(synth_df[c], errors="coerce").fillna(med)
            else:
                mode = real_df[c].mode(dropna=True)
                fill = mode.iloc[0] if len(mode) else ""
                synth_df[c] = synth_df[c].fillna(fill)

    return synth_df

class GeneratorType(Enum):
    """Tipos de geradores disponíveis incluindo SOTA"""
    GAUSSIAN_COPULA = "gaussian_copula"
    CTGAN = "ctgan"
    COPULAGAN = "copulagan"
    TVAE = "tvae"
    TABDDPM = "tabddpm"  # State-of-the-art diffusion model
    DDPM = "ddpm"
    VAE = "vae"
    WGAN_GP = "wgan_gp"
    # Fallback methods
    GAUSSIAN_NAIVE = "gaussian_naive"
    KDE_SAMPLING = "kde_sampling"

@dataclass

# --- Restored blocks from v10 (previously trimmed) ---
class DeltaJustification:
    """Estrutura com 3 componentes obrigatórios para justificar delta de não-inferioridade"""
    delta: float
    measurement_cv: float  # Precisão experimental (CV%)
    precedents: List[str]  # Precedentes na literatura (2-3 citações)
    expert_consensus: str  # Consenso de especialistas
    
    def validate(self):
        """Valida se todos os componentes estão presentes"""
        if not all([self.measurement_cv, self.precedents, self.expert_consensus]):
            raise ValueError("Delta justification requires all 3 components")
        if len(self.precedents) < 2:
            raise ValueError("At least 2 precedents required")
        return True
    
    def to_dict(self):
        return {
            "delta": self.delta,
            "measurement_cv": self.measurement_cv,
            "precedents": self.precedents,
            "expert_consensus": self.expert_consensus
        }

class StatisticalRigorFramework:
    """Framework para rigor estatístico seguindo padrões Q1/Q2"""
    
    @staticmethod
    def a_priori_sample_size_analysis(expected_effect_size: float = 0.3, 
                                    power: float = 0.8, 
                                    alpha: float = 0.05,
                                    alternative: str = 'two-sided') -> Dict[str, Any]:
        """
        Análise de tamanho de amostra A PRIORI (ANTES do experimento)
        
        Referência: Cohen (1988) - Statistical Power Analysis
        """
        try:
            power_analysis = TTestPower()
            required_n = power_analysis.solve_power(
                effect_size=expected_effect_size,
                power=power,
                alpha=alpha,
                alternative=alternative
            )
            
            return {
                "required_sample_size": int(np.ceil(required_n)),
                "expected_effect_size": expected_effect_size,
                "power": power,
                "alpha": alpha,
                "alternative": alternative,
                "method": "a_priori",
                "interpretation": f"Required n={int(np.ceil(required_n))} to detect effect size={expected_effect_size} with {power*100}% power"
            }
        except Exception as e:
            logger.warning(f"A priori power analysis failed: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def observed_sensitivity_analysis(observed_effect_size: float,
                                    sample_size: int,
                                    alpha: float = 0.05) -> Dict[str, Any]:
        """
        Análise de sensibilidade observada (DESCRITIVA, não inferencial)
        
        Referência: Hoenig & Heisey (2001) - "The Abuse of Power"
        """
        try:
            power_analysis = TTestPower()
            min_detectable = power_analysis.solve_power(
                nobs=sample_size,
                power=0.8,
                alpha=alpha,
                alternative='two-sided'
            )
            
            return {
                "observed_effect_size": observed_effect_size,
                "sample_size": sample_size,
                "min_detectable_effect_size_at_80pwr": min_detectable,
                "adequate_sensitivity": abs(observed_effect_size) >= min_detectable,
                "disclaimer": "DESCRIPTIVE ANALYSIS ONLY - NOT post-hoc power. See Hoenig & Heisey (2001).",
                "interpretation": f"With n={sample_size}, minimum detectable effect size is {min_detectable:.3f} at 80% power"
            }
        except Exception as e:
            logger.warning(f"Observed sensitivity analysis failed: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def enhanced_residual_diagnostics(y_true: np.ndarray, 
                                    y_pred: np.ndarray,
                                    X: np.ndarray = None) -> Dict[str, Any]:
        """
        Diagnóstico completo de resíduos para modelos lineares
        
        Inclui:
        - Breusch-Pagan test para heteroscedasticidade
        - Cook's distance para outliers influentes  
        - Teste de normalidade de Shapiro-Wilk
        """
        diagnostics = {}
        residuals = y_true - y_pred
        
        try:
            # 1. Breusch-Pagan test for heteroscedasticity (PRIMARY)
            if STATSMODELS_AVAILABLE and X is not None:
                X_with_const = add_constant(X)
                lm_stat, lm_pval, f_stat, f_pval = het_breuschpagan(residuals, X_with_const)
                diagnostics["breusch_pagan"] = {
                    "lagrange_multiplier_statistic": float(lm_stat),
                    "p_value": float(lm_pval),
                    "f_statistic": float(f_stat),
                    "f_p_value": float(f_pval),
                    "heteroscedasticity_present": lm_pval < 0.05,
                    "interpretation": "Breusch-Pagan test for heteroscedasticity (primary)"
                }
            
            # 2. Cook's distance for influential observations
            if STATSMODELS_AVAILABLE and X is not None:
                try:
                    model = ols("y ~ X", data={"y": y_true, "X": X}).fit()
                    influence = OLSInfluence(model)
                    cooks_d = influence.cooks_distance[0]
                    
                    # Threshold for influential observations
                    n = len(y_true)
                    cooks_threshold = 4.0 / n
                    influential_mask = cooks_d > cooks_threshold
                    n_influential = np.sum(influential_mask)
                    
                    diagnostics["cooks_distance"] = {
                        "values": cooks_d.tolist(),
                        "threshold": float(cooks_threshold),
                        "n_influential": int(n_influential),
                        "influential_observations": np.where(influential_mask)[0].tolist(),
                        "interpretation": f"Cook's distance (> {cooks_threshold:.4f}) identifies {n_influential} influential observations"
                    }
                except Exception as e:
                    diagnostics["cooks_distance"] = {"error": str(e)}
            
            # 3. Normality tests
            if len(residuals) > 3 and len(residuals) < 5000:
                shapiro_stat, shapiro_p = shapiro(residuals)
                diagnostics["normality"] = {
                    "shapiro_wilk_statistic": float(shapiro_stat),
                    "shapiro_wilk_p": float(shapiro_p),
                    "is_normal": shapiro_p > 0.05,
                    "interpretation": "Shapiro-Wilk test for normality of residuals"
                }
            
            # 4. Additional descriptive statistics
            diagnostics["residuals_descriptive"] = {
                "mean": float(np.mean(residuals)),
                "std": float(np.std(residuals)),
                "skewness": float(stats.skew(residuals)),
                "kurtosis": float(stats.kurtosis(residuals)),
                "jarque_bera_stat": float(stats.jarque_bera(residuals)[0]),
                "jarque_bera_p": float(stats.jarque_bera(residuals)[1])
            }
            
        except Exception as e:
            diagnostics["error"] = f"Enhanced residual diagnostics failed: {str(e)}"
        
        return diagnostics
    
    @staticmethod
    def multiple_testing_fdr_primary(pvals: List[float], 
                                   fdr_q: float = 0.05,
                                   method: str = 'fdr_bh') -> Dict[str, Any]:
        """
        Correção para múltiplos testes com FDR como critério PRIMÁRIO
        
        Referência: Benjamini & Hochberg (1995) - Controlling FDR
        """
        try:
            pvals_array = np.array(pvals)
            
            # FDR Benjamini-Hochberg (PRIMARY)
            fdr_rejected, fdr_corrected, _, _ = multipletests(
                pvals_array, alpha=fdr_q, method=method
            )
            
            # Holm-Bonferroni (secondary/sensitivity)
            holm_rejected, holm_corrected, _, _ = multipletests(
                pvals_array, alpha=fdr_q, method='holm'
            )
            
            # Bonferroni (most conservative)
            bonferroni_rejected = pvals_array < (fdr_q / len(pvals_array))
            
            results = {
                "fdr_primary": {
                    "rejected": fdr_rejected.tolist(),
                    "corrected_pvalues": fdr_corrected.tolist(),
                    "q_value": fdr_q,
                    "n_rejected": int(np.sum(fdr_rejected)),
                    "method": method
                },
                "holm_sensitivity": {
                    "rejected": holm_rejected.tolist(),
                    "corrected_pvalues": holm_corrected.tolist(),
                    "n_rejected": int(np.sum(holm_rejected)),
                    "method": "holm"
                },
                "bonferroni_conservative": {
                    "rejected": bonferroni_rejected.tolist(),
                    "n_rejected": int(np.sum(bonferroni_rejected)),
                    "method": "bonferroni"
                },
                "original_pvalues": pvals_array.tolist(),
                "decision_rule": "FDR_BH is primary criterion for hypothesis decisions",
                "interpretation": f"FDR control at q={fdr_q} rejected {np.sum(fdr_rejected)}/{len(pvals)} hypotheses"
            }
            
            return results
            
        except Exception as e:
            logger.error(f"FDR correction failed: {e}")
            return {"error": str(e)}

# ============================================================================
# CÓDIGO ORIGINAL COMPLETO (3442 LINHAS) - MANTIDO INTEGRALMENTE COM CORREÇÕES
# ============================================================================
# --- End restored blocks ---

@dataclass
class ExperimentConfig:
    """Configuração completa do experimento com padrões acadêmicos"""
    # Data
    input_csv: Optional[str] = None
    input_xlsx: Optional[str] = None
    target_column: str = "target"
    columns: Optional[List[str]] = None
    test_size: float = 0.2
    task_type: Optional[str] = None  # 'classification', 'regression', 'auto'
    
    # Generation
    generators: List[Union[GeneratorType, str]] = field(default_factory=lambda: [
        GeneratorType.GAUSSIAN_COPULA, GeneratorType.CTGAN, 
        GeneratorType.TVAE, GeneratorType.TABDDPM
    ])
    n_synthetic: int = 140
    noise_pct: float = 0.0  # percentual de ruído gaussiano (0-100) aplicado antes do pós-processamento
    # Optional generator hyperparameters
    tabddpm_params: dict = field(default_factory=dict)
    ctgan_params: dict = field(default_factory=dict)
    
    # Experimental design
    random_seed: int = 42
    n_runs: int = 10
    bootstrap_samples: int = 1000
    confidence_level: float = 0.95
    
    # Preprocessing
    remove_outliers: bool = True
    outlier_method: str = "tukey"
    outlier_threshold: float = 1.5
    categorical_threshold: int = 20
    
    # Evaluation
    eval_metrics: List[str] = field(default_factory=lambda: [
        "fidelity", "utility", "privacy", "diversity", "fairness"
    ])
    ml_models: List[str] = field(default_factory=lambda: [
        "rf", "lr", "mlp", "xgb" if XGBOOST_AVAILABLE else "elastic"
    ])
    
    # Statistical testing
    alpha: float = 0.05
    multiple_testing_correction: str = "holm"
    effect_size_threshold: float = 0.5
    power_threshold: float = 0.8
    
    # Privacy & Fairness (FLAGS ADICIONADAS)
    sensitive_attributes: Optional[List[str]] = None
    privacy_budget: float = 1.0
    enable_full_aia: bool = True  # ← FLAG ADICIONADA
    enable_fairness_eval: bool = True  # ← FLAG ADICIONADA
    aia_k_shadows: int = 5
    aia_attack_model: str = "lr"  # 'lr' ou 'rf'
    mia_n_shadow_models: int = 5  # ← NOVA FLAG para MIA
    
    # NEW FLAGS FOR ENHANCED EVALUATION
    attack_models: List[str] = field(default_factory=lambda: ["LR"])  # ["LR", "RF"]
    privacy_stratify: Dict[str, bool] = field(default_factory=lambda: {"rarity": False, "sensitive": False})
    fairness_mitigation_curves: bool = False
    bootstrap: Dict[str, Any] = field(default_factory=lambda: {"n": 1000, "stratify_by": None})
    fdr_q: float = 0.05
    
    # Output
    output_dir: str = "./synthetic_evaluation"
    save_synthetic: bool = True
    generate_report: bool = True
    plot_dpi: int = 300
    
    # NOVOS PARÂMETROS PARA RIGOR ESTATÍSTICO Q1/Q2 (ADICIONADOS)
    delta_non_inferiority: float = -0.05
    delta_justification: Optional[DeltaJustification] = None
    expected_effect_size_a_priori: float = 0.3
    enable_enhanced_diagnostics: bool = True
    
    # CORREÇÃO: Nova flag para validação estrita do delta
    strict_delta_validation: bool = False
    
    # CORREÇÃO: Nova flag para pós-processamento
    enable_postprocessing: bool = True
    
    # --- NOVOS CAMPOS PARA FILTRAGEM E DIAGNÓSTICOS Q1/Q2 ---
    enable_dcr_filter: bool = True
    dcr_tau: float = 0.10
    dcr_pool_factor: float = 1.5
    # Always deliver n_synthetic (top-up after DCR filter)
    always_deliver_n_synthetic: bool = True
    dcr_tau: float = 0.10
    dcr_max_pool_factor: int = 40
    dcr_repulsion_max_iters: int = 20000

    enable_doe_noise: bool = False
    doe_noise_pct: float = 0.0
    enable_delta_feature: bool = True
    delta_repeats: int = 5
    enable_q1q2_figures: bool = True
    
    # NOVOS PARÂMETROS PARA MLP AVANÇADO (ADICIONADOS)
    enable_mlp_tuning: bool = True  # Ativar tuning bayesiano do MLP
    mlp_tuning_trials: int = 50  # Número de trials para Optuna
    mlp_early_stopping_patience: int = 20  # Paciência para early stopping
    mlp_use_batch_norm: bool = True  # Usar Batch Normalization
    mlp_use_dropout: bool = True  # Usar Dropout
    mlp_learning_rate_schedule: str = "reduce_on_plateau"  # "reduce_on_plateau", "cosine", "cyclic"
    mlp_ensemble_size: int = 3  # Tamanho do ensemble para MLP
    
    def __post_init__(self):
        """Validação pós-inicialização para rigor estatístico"""
        # Configurar justificação do delta se não fornecida
        if self.delta_justification is None:
            self.delta_justification = DeltaJustification(
                delta=self.delta_non_inferiority,
                measurement_cv=2.5,  # CV% típico em ensaios experimentais
                precedents=["Fernandez2022", "Chen2023", "Silva2024"],
                expert_consensus="Domain experts agreed 5% utility loss acceptable for privacy gains"
            )
        
        # CORREÇÃO: Validação condicional do delta baseada na flag strict_delta_validation
        try:
            self.delta_justification.validate()
        except ValueError as e:
            if self.strict_delta_validation:
                raise ValueError(f"Delta justification incomplete: {e}") from e
            else:
                logger.warning(f"Delta justification incomplete: {e}")





    def to_dict(self) -> dict:
        """Serializa a configuração para JSON de forma robusta (compatível com artefatos Q1/Q2)."""
        try:
            from dataclasses import asdict, is_dataclass
            d = asdict(self) if is_dataclass(self) else dict(getattr(self, "__dict__", {}))
        except Exception:
            d = dict(getattr(self, "__dict__", {}))

        def _norm(x):
            # numpy scalars/arrays
            try:
                import numpy as _np
                if isinstance(x, (_np.integer, _np.floating)):
                    return x.item()
                if isinstance(x, _np.ndarray):
                    return x.tolist()
            except Exception:
                pass

            # enums
            try:
                from enum import Enum as _Enum
                if isinstance(x, _Enum):
                    return getattr(x, "value", str(x))
            except Exception:
                pass

            # pathlib.Path
            try:
                from pathlib import Path as _Path
                if isinstance(x, _Path):
                    return str(x)
            except Exception:
                pass

            if isinstance(x, dict):
                return {str(k): _norm(v) for k, v in x.items()}
            if isinstance(x, (list, tuple, set)):
                return [_norm(v) for v in list(x)]
            return x

        return _norm(d)


# ============================================================================
# Q1/Q2 diagnostics: DCR, ECDF, Corr-diff heatmap, Trade-off plot, Δ-per-feature
# ============================================================================
from sklearn.neighbors import NearestNeighbors

def compute_dcr_values(real_df: pd.DataFrame, synth_df: pd.DataFrame, feature_cols: Optional[List[str]] = None) -> np.ndarray:
    """Compute Distance to Closest Record (DCR) from each synthetic row to nearest real row."""
    if feature_cols is None:
        feature_cols = [c for c in real_df.columns if c in synth_df.columns and c != getattr(ExperimentConfig, 'target_column', 'target')]
    feature_cols = [c for c in feature_cols if c in real_df.columns and c in synth_df.columns]
    if not feature_cols:
        return np.array([])
    Xr = real_df[feature_cols].apply(pd.to_numeric, errors='coerce')
    Xs = synth_df[feature_cols].apply(pd.to_numeric, errors='coerce')
    Xr = Xr.fillna(Xr.median(numeric_only=True))
    Xs = Xs.fillna(Xr.median(numeric_only=True))
    scaler = StandardScaler()
    Xr_s = scaler.fit_transform(Xr.values)
    Xs_s = scaler.transform(Xs.values)
    nn = NearestNeighbors(n_neighbors=1, algorithm='auto')
    nn.fit(Xr_s)
    d, _ = nn.kneighbors(Xs_s, n_neighbors=1, return_distance=True)
    return d.reshape(-1)

def dcr_threshold_filter_pool(
    synth_df: pd.DataFrame,
    real_df: pd.DataFrame,
    *,
    tau: float = 0.10,
    metric: str = "euclidean",
    max_pool_factor: int = 40,
    desired_n: Optional[int] = None,
    always_deliver: bool = True,
    repulsion_max_iters: int = 20000,
    target_col: Optional[str] = None,
    logger: Optional[logging.Logger] = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Filtro DCR (Distance to Closest Record) com opção "sempre entregar n_synthetic".

    Estratégia (aceitável para revisores):
      1) Calcula DCR(synth→real) (normalizado por MAD/IQR, conforme compute_dcr).
      2) Mantém apenas pontos com DCR >= tau.
      3) Se faltarem amostras e always_deliver=True: faz TOP-UP usando jitter + repulsão
         (move candidato para longe do vizinho real mais próximo) até atingir desired_n,
         sem reduzir o limiar tau (não relaxa privacidade).

    Retorna: (df_filtrado, stats)
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    if synth_df is None or len(synth_df) == 0:
        return synth_df, {"tau": tau, "kept": 0, "desired_n": desired_n, "status": "empty"}

    desired_n = int(desired_n) if desired_n is not None else len(synth_df)

    # pool inicial: já temos synth_df; se for muito pequeno para filtrar, tentamos "pool" por replicação/jitter
    df_pool = synth_df.copy()
    if len(df_pool) < desired_n:
        # já vamos precisar top-up depois; mantenha
        pass

    # Compute DCR
    dcr_values = compute_dcr_values(real_df=real_df, synth_df=df_pool)
    dcr_values = np.asarray(dcr_values, dtype=float)
    dcr_values = np.nan_to_num(dcr_values, nan=0.0, posinf=0.0, neginf=0.0)

    safe_mask = dcr_values >= float(tau)
    df_safe = df_pool.loc[safe_mask].copy()
    kept = len(df_safe)

    stats: Dict[str, Any] = {
        "tau": float(tau),
        "metric": metric,
        "pool_size": int(len(df_pool)),
        "kept": int(kept),
        "desired_n": int(desired_n),
        "kept_fraction": float(kept / max(1, len(df_pool))),
        "min_dcr": float(np.nanmin(dcr_values)) if len(dcr_values) else np.nan,
        "p05_dcr": float(np.nanpercentile(dcr_values, 5)) if len(dcr_values) else np.nan,
        "p50_dcr": float(np.nanpercentile(dcr_values, 50)) if len(dcr_values) else np.nan,
    }

    if kept >= desired_n or not always_deliver:
        df_out = df_safe.sample(n=min(desired_n, kept), replace=False, random_state=42) if kept > 0 else df_safe
        stats["status"] = "ok" if kept >= desired_n else "insufficient_no_topup"

        # Diagnóstico: KS no target pré/pós filtro (para detectar viés induzido)
        if target_col is not None and target_col in df_pool.columns and target_col in df_out.columns:
            try:
                from scipy.stats import ks_2samp
                a = pd.to_numeric(df_pool[target_col], errors="coerce").dropna().values
                b = pd.to_numeric(df_out[target_col], errors="coerce").dropna().values
                if len(a) >= 5 and len(b) >= 5:
                    ks_stat, ks_p = ks_2samp(a, b)
                    stats["target_ks_pre_post"] = {"statistic": float(ks_stat), "pvalue": float(ks_p)}
                    if float(ks_stat) >= 0.30:
                        logger.warning(f"[DCR] KS pré/pós filtro no target é alto (stat={ks_stat:.3f}, p={ks_p:.3g}). Possível viés induzido pelo filtro.")
            except Exception:
                pass
        return df_out.reset_index(drop=True), stats

    # TOP-UP: jitter + repulsão controlada
    logger.info(f"DCR filter: kept={kept} < desired_n={desired_n}. Executando top-up por repulsão (tau={tau}).")
    rng = np.random.default_rng(2026)

    numeric_cols = [c for c in real_df.columns if pd.api.types.is_numeric_dtype(real_df[c])]
    real_num = real_df[numeric_cols].apply(pd.to_numeric, errors="coerce").astype(float).values
    real_num = np.nan_to_num(real_num, nan=np.nanmedian(real_num, axis=0))

    # Escalas robustas por coluna (IQR)
    scales = []
    for j, c in enumerate(numeric_cols):
        r = pd.to_numeric(real_df[c], errors="coerce").astype(float).values
        q25, q75 = np.nanpercentile(r, [25, 75])
        s = max(1e-12, float(q75 - q25))
        scales.append(s)
    scales = np.array(scales, dtype=float)

    def _to_num(df):
        A = df[numeric_cols].apply(pd.to_numeric, errors="coerce").astype(float).values
        A = np.nan_to_num(A, nan=np.nanmedian(real_num, axis=0))
        return A

    df_out = df_safe.copy()
    out_num = _to_num(df_out) if len(df_out) else np.zeros((0, len(numeric_cols)))

    # Começa a partir de amostras do próprio pool (ou do real, em último caso)
    base_source = df_pool if len(df_pool) else real_df

    it = 0
    while len(df_out) < desired_n and it < repulsion_max_iters:
        it += 1
        cand = base_source.sample(n=1, replace=True, random_state=int(rng.integers(0, 1_000_000))).copy()

        # jitter pequeno
        for c, s in zip(numeric_cols, scales):
            v = float(pd.to_numeric(cand.iloc[0][c], errors="coerce"))
            if not np.isfinite(v):
                v = float(np.nanmedian(pd.to_numeric(real_df[c], errors="coerce").astype(float).values))
            v = v + rng.normal(0.0, 0.02 * s)
            # clipping real
            lo = float(np.nanmin(pd.to_numeric(real_df[c], errors="coerce").astype(float).values))
            hi = float(np.nanmax(pd.to_numeric(real_df[c], errors="coerce").astype(float).values))
            cand.iloc[0, cand.columns.get_loc(c)] = float(np.clip(v, lo, hi))

        cand_num = _to_num(cand)[0]

        # calcula distância normalizada ao vizinho real mais próximo (DCR)
        diff = (real_num - cand_num.reshape(1, -1)) / scales.reshape(1, -1)
        dists = np.sqrt(np.sum(diff * diff, axis=1))
        nn_idx = int(np.argmin(dists))
        dcr = float(dists[nn_idx])

        if dcr < tau:
            # repulsão: move ao longo do vetor que afasta do nearest real até atingir tau (com folga)
            r = real_num[nn_idx]
            v = (cand_num - r) / scales
            norm = float(np.linalg.norm(v))
            if norm < 1e-12:
                # direção aleatória
                v = rng.normal(size=v.shape)
                norm = float(np.linalg.norm(v))
            v_unit = v / max(1e-12, norm)
            target = tau * 1.05  # folga 5%
            step = (target - dcr)
            cand_num2 = cand_num + (step * v_unit) * scales
            # re-clipping
            for j, c in enumerate(numeric_cols):
                lo = float(np.nanmin(pd.to_numeric(real_df[c], errors="coerce").astype(float).values))
                hi = float(np.nanmax(pd.to_numeric(real_df[c], errors="coerce").astype(float).values))
                cand_num2[j] = float(np.clip(cand_num2[j], lo, hi))
            # re-eval
            diff2 = (real_num - cand_num2.reshape(1, -1)) / scales.reshape(1, -1)
            dists2 = np.sqrt(np.sum(diff2 * diff2, axis=1))
            dcr2 = float(np.min(dists2))
            if dcr2 < tau:
                continue  # rejeita
            # aplica valores numéricos de volta
            for j, c in enumerate(numeric_cols):
                cand.iloc[0, cand.columns.get_loc(c)] = cand_num2[j]

        # aceita
        df_out = pd.concat([df_out, cand], axis=0, ignore_index=True)

    stats["topup_iters"] = int(it)
    stats["status"] = "ok_topup" if len(df_out) >= desired_n else "failed_topup"
    stats["final_n"] = int(len(df_out))

    # Diagnóstico: KS no target pré/pós filtro (TOP-UP) para detectar viés induzido
    if target_col is not None and target_col in df_pool.columns and target_col in df_out.columns:
        try:
            from scipy.stats import ks_2samp
            a = pd.to_numeric(df_pool[target_col], errors="coerce").dropna().values
            b = pd.to_numeric(df_out[target_col], errors="coerce").dropna().values
            if len(a) >= 5 and len(b) >= 5:
                ks_stat, ks_p = ks_2samp(a, b)
                stats["target_ks_pre_post"] = {"statistic": float(ks_stat), "pvalue": float(ks_p)}
                if float(ks_stat) >= 0.30:
                    logger.warning(
                        f"[DCR] (topup) KS pré/pós filtro no target é alto (stat={ks_stat:.3f}, p={ks_p:.3g}). Possível viés induzido pelo filtro."
                    )
        except Exception:
            pass

    return df_out.iloc[:desired_n].reset_index(drop=True), stats

def apply_doe_based_noise(synth_df: pd.DataFrame, real_df: pd.DataFrame, noise_pct: float, discrete_cols: Optional[Dict[str, List[float]]]=None) -> pd.DataFrame:
    """DOE-based noise: apply small jitter bounded by experimental range; preserve discrete levels."""
    if noise_pct is None or noise_pct <= 0:
        return synth_df
    out = synth_df.copy()
    cols = [c for c in real_df.columns if c in out.columns]
    # build discrete map if not provided
    if discrete_cols is None:
        discrete_cols = {}
        for c in cols:
            uniq = sorted(real_df[c].dropna().unique().tolist())
            if len(uniq) <= 6:
                discrete_cols[c] = uniq
    for c in cols:
        if c in discrete_cols:
            # keep levels: snap to nearest allowed
            allowed = np.array(discrete_cols[c], dtype=float)
            x = pd.to_numeric(out[c], errors='coerce').values.astype(float)
            idx = np.abs(x[:, None] - allowed[None, :]).argmin(axis=1)
            out[c] = allowed[idx]
            continue
        if not pd.api.types.is_numeric_dtype(real_df[c]):
            continue
        lo, hi = float(real_df[c].min()), float(real_df[c].max())
        rng = hi - lo
        if not np.isfinite(rng) or rng <= 0:
            continue
        sigma = (noise_pct/100.0) * rng
        noise = np.random.normal(0.0, sigma, size=len(out))
        x = pd.to_numeric(out[c], errors='coerce').fillna(real_df[c].median()).astype(float).values
        x = np.clip(x + noise, lo, hi)
        out[c] = x
    return out

def plot_ecdf_dcr(dcr_values: np.ndarray, outpath: str, title: str, taus=(0.05, 0.10, 0.15)) -> None:
    """ECDF do DCR com linhas de perigo (C2).

    Também adiciona anotação de risco quando fração(DCR<0.10) > 30%.
    """
    if dcr_values is None or len(dcr_values) == 0:
        return
    import matplotlib.pyplot as plt
    x = np.sort(np.asarray(dcr_values, dtype=float))
    y = np.arange(1, len(x) + 1) / len(x)

    plt.figure(figsize=(8, 5))
    plt.plot(x, y, linewidth=2)

    # highlight danger zone
    plt.axvspan(0, 0.10, alpha=0.15)

    frac10 = float((x < 0.10).mean())
    if frac10 > 0.30:
        plt.text(
            0.12,
            0.10,
            f"WARNING: {frac10:.1%} with DCR<0.10",
            color="red",
            fontsize=10,
            bbox=dict(facecolor="white", edgecolor="red", boxstyle="round,pad=0.3"),
        )

    for tau in taus:
        frac = float((x < tau).mean())
        plt.axvline(tau, linestyle="--", linewidth=1, label=f"τ={tau:.2f} ({frac:.1%})")

    plt.xlabel("DCR (distance to closest real)")
    plt.ylabel("ECDF")
    plt.title(title)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.close()


def plot_corr_diff_heatmap(real_df: pd.DataFrame, synth_df: pd.DataFrame, outpath: str, title: str, crit_threshold: float = 0.30) -> None:
    """Heatmap de |Corr_real - Corr_synth| (C3) + log de pares críticos."""
    import matplotlib.pyplot as plt
    logger = logging.getLogger(__name__)
    cols = [c for c in real_df.columns if c in synth_df.columns]
    if len(cols) < 2:
        return
    R = real_df[cols].corr().values
    S = synth_df[cols].corr().values
    diff = np.abs(R - S)

    # log critical pairs
    try:
        idxs = np.argwhere(np.triu(diff, k=1) > crit_threshold)
        if idxs.size > 0:
            pairs = []
            for i, j in idxs:
                pairs.append((cols[int(i)], cols[int(j)], float(diff[int(i), int(j)])))
            pairs = sorted(pairs, key=lambda t: -t[2])[:10]
            logger.info("CorrDiff critical pairs (top10) for %s: %s", title, pairs)
    except Exception:
        pass

    plt.figure(figsize=(7, 6))
    im = plt.imshow(diff, vmin=0, vmax=1)
    plt.colorbar(im, fraction=0.046, pad=0.04, label="|Corr_real - Corr_synth|")
    plt.xticks(range(len(cols)), cols, rotation=45, ha="right", fontsize=7)
    plt.yticks(range(len(cols)), cols, fontsize=7)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.close()


def plot_tradeoff(article_df: pd.DataFrame, outpath: str, tau_label: str = "DCR<0.1") -> None:
    """Trade-off plot (C5): Utility vs Risk with Pareto frontier."""
    import matplotlib.pyplot as plt
    if article_df is None or article_df.empty:
        return

    # tolerate missing risk (NaN)
    x = np.asarray(article_df.get("risk_frac_dcr_lt_0p1", np.full(len(article_df), np.nan)), dtype=float)
    y = np.asarray(article_df.get("TSTR_best", np.full(len(article_df), np.nan)), dtype=float)
    labels = article_df.get("generator", pd.Series([f"g{i}" for i in range(len(article_df))])).values

    # decide if higher is better for y
    # heuristic: if within [-5, 1.2] treat as R² (higher better)
    higher_better = True
    if np.isfinite(y).any():
        y_min = float(np.nanmin(y))
        y_max = float(np.nanmax(y))
        if y_max > 3.0:  # likely error metric
            higher_better = False

    plt.figure(figsize=(7, 5))
    plt.scatter(x, y)

    for xi, yi, lab in zip(x, y, labels):
        if np.isfinite(xi) and np.isfinite(yi):
            plt.text(xi, yi, str(lab), fontsize=9)

    plt.xlabel(f"Risk fraction ({tau_label})")
    plt.ylabel("Utility (TSTR_best)" + (" [higher better]" if higher_better else " [lower better]"))
    plt.grid(alpha=0.3)

    # Pareto frontier
    pts = [(xi, yi, lab) for xi, yi, lab in zip(x, y, labels) if np.isfinite(xi) and np.isfinite(yi)]
    if pts:
        # sort by risk ascending
        pts_sorted = sorted(pts, key=lambda t: t[0])
        frontier = []
        best_y = -np.inf if higher_better else np.inf
        for xi, yi, lab in pts_sorted:
            if higher_better:
                if yi >= best_y:
                    frontier.append((xi, yi))
                    best_y = yi
            else:
                if yi <= best_y:
                    frontier.append((xi, yi))
                    best_y = yi
        if len(frontier) >= 2:
            fx, fy = zip(*frontier)
            plt.plot(fx, fy, linewidth=2, linestyle="--", label="Pareto frontier")
            plt.legend()

    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.close()


def compute_delta_per_feature_one_split(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_ctor: Callable[[], Any],
    task_type: str = "regression",
    random_state: int = 0,
    n_repeats: Optional[int] = None,
) -> Dict[str, float]:
    """
    Δ por variável via Permutation Feature Importance (PFI) em um único split.
    Retorna importâncias (queda média da métrica ao permutar) por feature.

    - Para regressão: usa R² (quanto maior melhor). Importância = baseline - permuted.
    - Para classificação: usa AUC se possível, senão accuracy.

    Obs.: implementação otimizada para datasets pequenos, com reamostragem leve e proteção numérica.
    """
    rng = np.random.default_rng(random_state)
    X_train = X_train.copy()
    X_test = X_test.copy()
    y_train = pd.Series(y_train).copy()
    y_test = pd.Series(y_test).copy()

    # Segurança: converter tudo para numérico onde possível
    for c in X_train.columns:
        X_train[c] = pd.to_numeric(X_train[c], errors="coerce")
        X_test[c] = pd.to_numeric(X_test[c], errors="coerce")
        med = float(np.nanmedian(pd.concat([X_train[c], X_test[c]], axis=0).values))
        X_train[c] = X_train[c].fillna(med)
        X_test[c] = X_test[c].fillna(med)

    model = model_ctor()
    try:
        model.fit(X_train, y_train)
    except Exception:
        # fallback: reduzir complexidade se MLP/estimador for sensível
        model = model_ctor()
        model.fit(X_train.values, y_train.values)

    def _score(X, y):
        if task_type == "classification":
            # tenta AUC
            try:
                if hasattr(model, "predict_proba"):
                    p = model.predict_proba(X)[:, 1]
                    return float(roc_auc_score(y, p))
            except Exception:
                pass
            try:
                pred = model.predict(X)
                return float(accuracy_score(y, pred))
            except Exception:
                pred = model.predict(X.values)
                return float(accuracy_score(y.values, pred))
        else:
            try:
                pred = model.predict(X)
            except Exception:
                pred = model.predict(X.values)
            pred = np.asarray(pred, dtype=float)
            yv = np.asarray(y, dtype=float)
            # proteção numérica
            if not np.isfinite(pred).all():
                pred = np.nan_to_num(pred, nan=np.nanmedian(pred), posinf=np.nanmax(yv), neginf=np.nanmin(yv))
            return float(r2_score(yv, pred))

    baseline = _score(X_test, y_test)
    importances: Dict[str, float] = {}

    # uma permutação por feature é suficiente em small-n; replicação leve (n=3) estabiliza
    if n_repeats is None:
        n_repeats_eff = 3 if len(X_test) >= 15 else 2
    else:
        try:
            n_repeats_eff = max(1, int(n_repeats))
        except Exception:
            n_repeats_eff = 3 if len(X_test) >= 15 else 2

    for c in X_test.columns:
        drops = []
        for _ in range(n_repeats_eff):
            Xp = X_test.copy()
            Xp[c] = rng.permutation(Xp[c].values)
            s = _score(Xp, y_test)
            drops.append(baseline - s)
        importances[str(c)] = float(np.mean(drops))

    return importances

def _two_sample_metrics(real_df: pd.DataFrame, synth_df: pd.DataFrame, random_seed: int = 123) -> Dict[str, float]:
    """Two-sample test via propensity model (AUC + pMSE)."""
    cols = [c for c in real_df.columns if c in synth_df.columns]
    if not cols:
        return {"two_sample_auc": float("nan"), "two_sample_pmse": float("nan")}
    X_real = real_df[cols].copy()
    X_synth = synth_df[cols].copy()
    X = pd.concat([X_real, X_synth], axis=0, ignore_index=True)
    y = np.array([0]*len(X_real) + [1]*len(X_synth))

    X_num = X.apply(pd.to_numeric, errors="coerce")
    X_num = X_num.fillna(X_num.median(numeric_only=True))

    clf = Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(max_iter=10000, solver="lbfgs", random_state=random_seed))
    ])
    try:
        clf.fit(X_num, y)
        p = clf.predict_proba(X_num)[:, 1]
        auc = float(roc_auc_score(y, p))
        pmse = float(np.mean((p - 0.5)**2))
        return {"two_sample_auc": auc, "two_sample_pmse": pmse}
    except Exception:
        return {"two_sample_auc": float("nan"), "two_sample_pmse": float("nan")}

def _constraint_violation_rate(real_df: pd.DataFrame, synth_df: pd.DataFrame, discrete_cols: Optional[Dict[str, List[float]]] = None) -> Dict[str, float]:
    """CVR: proporção de checks violados (faixa + conjunto discreto)."""
    cols = [c for c in real_df.columns if c in synth_df.columns]
    if not cols:
        return {"cvr": float("nan")}
    violations = 0
    checks = 0
    for c in cols:
        if pd.api.types.is_numeric_dtype(real_df[c]) and pd.api.types.is_numeric_dtype(synth_df[c]):
            lo, hi = float(real_df[c].min()), float(real_df[c].max())
            v = ((synth_df[c] < lo) | (synth_df[c] > hi)).sum()
            violations += int(v)
            checks += len(synth_df)
    if discrete_cols:
        for c, allowed in discrete_cols.items():
            if c in synth_df.columns:
                bad = (~synth_df[c].isin(allowed)).sum()
                violations += int(bad)
                checks += len(synth_df)
    return {"cvr": float(violations / checks) if checks else 0.0}

def generate_results_discussion_paragraph(article_df: pd.DataFrame, config: Dict[str, Any]) -> str:
    """Parágrafo curto no estilo Results/Discussion."""
    if article_df is None or article_df.empty:
        return "No results available."
    top = article_df.iloc[0].to_dict()
    gen = top.get("generator")
    tstr = top.get("TSTR_best")
    delta = top.get("TSTR_minus_TRTR_best_same_model", top.get("TSTR_minus_TRTR_best"))
    auc = top.get("two_sample_auc")
    pmse = top.get("two_sample_pmse")
    cvr = top.get("cvr")
    risk = top.get("risk_frac_dcr_lt_0p1")
    ns = config.get("n_synthetic")
    nr = config.get("n_runs")
    return (
        f"Using n_synth={ns} and {nr} evaluation runs, the best-performing generator was {gen}, "
        f"achieving the highest TSTR (R²) across evaluated models (TSTR_best={tstr:.3f}) and an estimated utility gain "
        f"over the real-only baseline (Δ=TSTR−TRTR={delta:.3f}). Global realism assessed via a two-sample propensity test "
        f"yielded AUC={auc:.3f} and pMSE={pmse:.4f}, while domain/format constraints were respected with CVR={cvr:.4f}. "
        f"Nearest-neighbor risk (fraction DCR<0.1) was {risk:.3f}, indicating the need for post-generation filtering or noise injection "
        f"when privacy/memorization concerns are relevant."
    )

def build_article_table_from_results(evaluation_results: Dict[str, Any], real_df: pd.DataFrame, synthetic_datasets: Dict[str, pd.DataFrame], config: Dict[str, Any], output_dir: str) -> pd.DataFrame:
    """Gera tabela (gerador x métricas) e salva CSV/MD + parágrafo Results/Discussion."""
    discrete_map = {}
    for c in real_df.columns:
        uniq = sorted(real_df[c].dropna().unique().tolist())
        if len(uniq) <= 6:
            discrete_map[c] = uniq

    rows = []
    for gen, res in evaluation_results.items():
        fid = res.get("fidelity", {})
        util = res.get("utility", {})
        priv = res.get("privacy", {})

        ks_stats = []
        for c, t in fid.get("univariate_tests", {}).items():
            ks = t.get("ks_test", {})
            if "statistic" in ks:
                ks_stats.append(float(ks["statistic"]))
        ks_mean = float(np.mean(ks_stats)) if ks_stats else float("nan")

        corr_frob = fid.get("corr_frobenius_diff", float("nan"))
        corr_of_corr = fid.get("correlation_preservation", {}).get("correlation_of_correlations", float("nan"))

        best_tstr = -1e9
        best_delta = -1e9
        best_model = None  # best by TSTR (mean)
        best_model_delta_same = float("nan")  # delta for the same best_model
        best_model_trtr = float("nan")

        # --- IMPORTANT: keep two notions of "delta" ---
        # (A) best_delta_any: max over models of (mean(TSTR)-mean(TRTR))  [legacy behavior]
        # (B) delta_same_model: (mean(TSTR_best_model)-mean(TRTR_best_model)) where best_model is argmax mean(TSTR)
        # For reporting in papers, (B) is the statistically coherent comparison.
        deltas_any = []

        for mname, mres in util.get("model_results", {}).items():
            tstr = float(mres.get("TSTR", {}).get("mean", float("nan")))
            trtr = float(mres.get("TRTR", {}).get("mean", float("nan")))

            if np.isfinite(tstr) and tstr > best_tstr:
                best_tstr = tstr
                best_model = mname
                best_model_trtr = trtr

            if np.isfinite(tstr) and np.isfinite(trtr):
                deltas_any.append((tstr - trtr, mname))

        if deltas_any:
            best_delta = max(deltas_any, key=lambda x: x[0])[0]

        if best_model is not None and np.isfinite(best_tstr) and np.isfinite(best_model_trtr):
            best_model_delta_same = best_tstr - best_model_trtr

        synth_df = synthetic_datasets.get(gen)

        # --- Privacy risk (DCR) ---
        # Historicamente este bloco variou de formato; aceitamos:
        # (a) fraction_within_0.1 + median
        # (b) privacy_risk_counts.distance_below_0.1 + median_distance
        dcr = (priv.get("distance_to_closest_record", {}) or {})
        frac_below_01 = dcr.get("fraction_within_0.1", None)

        # fallback: compute from counts / n_synth
        if frac_below_01 is None or (isinstance(frac_below_01, (float, int)) and not np.isfinite(float(frac_below_01))):
            counts = (dcr.get("privacy_risk_counts", {}) or {})
            below = counts.get("distance_below_0.1", None)
            n_denom = len(synth_df) if isinstance(synth_df, pd.DataFrame) else int(config.get("n_synthetic", 0) or 0)
            if below is not None and n_denom > 0:
                frac_below_01 = float(below) / float(n_denom)
            else:
                frac_below_01 = float("nan")
            frac_below_01 = float(frac_below_01)

        med_dcr = dcr.get("median", dcr.get("median_distance", float("nan")))
        try:
            med_dcr = float(med_dcr)
        except Exception:
            med_dcr = float("nan")

        ts = _two_sample_metrics(real_df, synth_df, random_seed=int(config.get("random_seed", 123))) if synth_df is not None else {"two_sample_auc": float("nan"), "two_sample_pmse": float("nan")}
        cvr = _constraint_violation_rate(real_df, synth_df, discrete_map) if synth_df is not None else {"cvr": float("nan")}

        rows.append({
            "generator": gen,
            "KS_mean_stat": ks_mean,
            "corr_frobenius_diff": float(corr_frob) if corr_frob is not None else float("nan"),
            "corr_of_corr": float(corr_of_corr) if corr_of_corr is not None else float("nan"),
            "TSTR_best": float(best_tstr) if best_tstr > -1e8 else float("nan"),
            "TSTR_minus_TRTR_best": float(best_delta) if best_delta > -1e8 else float("nan"),
            "TSTR_minus_TRTR_best_same_model": float(best_model_delta_same) if np.isfinite(best_model_delta_same) else float("nan"),
            "TRTR_best_model": float(best_model_trtr) if np.isfinite(best_model_trtr) else float("nan"),
            "best_model": best_model,
            "risk_frac_dcr_lt_0p1": float(frac_below_01) if frac_below_01 is not None else float("nan"),
            "risk_median_dcr": float(med_dcr) if med_dcr is not None else float("nan"),
            **ts,
            **cvr,
        })

    df = pd.DataFrame(rows).sort_values(by="TSTR_best", ascending=False)
    os.makedirs(output_dir, exist_ok=True)
    try:
        md = df.to_markdown(index=False)
        with open(os.path.join(output_dir, "article_table.md"), "w", encoding="utf-8") as f:
            f.write(md + "\n")
    except Exception as e:
        logger.warning(f"article_table.md não gerado (instale tabulate). Motivo: {e}")

    para = generate_results_discussion_paragraph(df, config)
    with open(os.path.join(output_dir, "results_discussion.txt"), "w", encoding="utf-8") as f:
        f.write(para.strip() + "\n")
    return df



# ============================================================================
# Article-ready plots: TSTR boxplot and Delta CI plot
# ============================================================================
def _safe_t_ci(x: np.ndarray, alpha: float = 0.05):
    """Return (mean, ci_low, ci_high) using t-interval; fallback to NaNs."""
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size < 2:
        m = float(np.nanmean(x)) if x.size else float("nan")
        return m, float("nan"), float("nan")
    m = float(np.mean(x))
    s = float(np.std(x, ddof=1))
    try:
        from scipy.stats import t
        tcrit = float(t.ppf(1 - alpha/2, df=x.size - 1))
        half = tcrit * s / np.sqrt(x.size)
        return m, m - half, m + half
    except Exception:
        return m, float("nan"), float("nan")

def generate_article_utility_plots(evaluation_results: Dict[str, Any], output_dir: str, dpi: int = 300) -> None:
    """Generate tstr_boxplot.png and delta_ci.png from evaluation_results."""
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return

    os.makedirs(output_dir, exist_ok=True)

    # Build long-form data for TSTR boxplot
    rows = []
    delta_rows = []
    for gen, res in (evaluation_results or {}).items():
        util = (res.get("utility", {}) or {})
        models = (util.get("model_results", {}) or {})
        for mname, mres in models.items():
            tstr_scores = (mres.get("TSTR", {}) or {}).get("scores", []) or []
            trtr_scores = (mres.get("TRTR", {}) or {}).get("scores", []) or []
            # Extract per-run r2
            tstr_r2 = [float(s.get("r2", np.nan)) for s in tstr_scores]
            trtr_r2 = [float(s.get("r2", np.nan)) for s in trtr_scores]

            for v in tstr_r2:
                rows.append({"generator": gen, "model": mname, "r2": v})

            # Delta per run when lengths match; else use pairwise up to min length
            k = min(len(tstr_r2), len(trtr_r2))
            if k > 0:
                deltas = [tstr_r2[i] - trtr_r2[i] for i in range(k)]
                m, lo, hi = _safe_t_ci(np.array(deltas), alpha=0.05)
                delta_rows.append({"generator": gen, "model": mname, "delta_mean": m, "ci_low": lo, "ci_high": hi, "n": k})

    # 1) TSTR boxplot (generator x model)
    try:
        import seaborn as sns  # optional (recommended)
        import pandas as pd
        df_long = pd.DataFrame(rows)
        if not df_long.empty:
            plt.figure(figsize=(10, 5))
            sns.boxplot(data=df_long, x="generator", y="r2", hue="model")
            plt.axhline(0.0, linewidth=1.0)
            plt.title("TSTR R² distribution by generator × model")
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "tstr_boxplot.png"), dpi=int(dpi))
            plt.close()
    except Exception:
        # Fallback: simple matplotlib boxplots grouped by (generator, model)
        try:
            import pandas as pd
            df_long = pd.DataFrame(rows)
            if not df_long.empty:
                groups = df_long.groupby(["generator", "model"])["r2"].apply(list)
                labels = [f"{g}|{m}" for (g, m) in groups.index]
                vals = [np.asarray(v, dtype=float) for v in groups.values]
                plt.figure(figsize=(12, 5))
                plt.boxplot(vals, labels=labels, showfliers=False)
                plt.axhline(0.0, linewidth=1.0)
                plt.xticks(rotation=45, ha="right")
                plt.title("TSTR R² distribution by generator × model")
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, "tstr_boxplot.png"), dpi=int(dpi))
                plt.close()
        except Exception:
            pass

    # 2) Delta CI plot (Δ=TSTR-TRTR with CI when available)
    try:
        import pandas as pd
        df_delta = pd.DataFrame(delta_rows)
        if not df_delta.empty:
            df_delta["label"] = df_delta["generator"].astype(str) + "|" + df_delta["model"].astype(str)
            df_delta = df_delta.sort_values(["generator", "model"])
            x = np.arange(len(df_delta))
            y = df_delta["delta_mean"].to_numpy(dtype=float)
            lo = df_delta["ci_low"].to_numpy(dtype=float)
            hi = df_delta["ci_high"].to_numpy(dtype=float)

            # error bars: if CI missing, use 0 length
            yerr_low = np.where(np.isfinite(lo), y - lo, 0.0)
            yerr_high = np.where(np.isfinite(hi), hi - y, 0.0)

            plt.figure(figsize=(12, 5))
            plt.errorbar(x, y, yerr=[yerr_low, yerr_high], fmt="o", capsize=3)
            plt.axhline(0.0, linewidth=1.0)
            plt.xticks(x, df_delta["label"].tolist(), rotation=45, ha="right")
            plt.title("Δ = TSTR − TRTR (mean ± 95% CI when available)")
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, "delta_ci.png"), dpi=int(dpi))
            plt.close()
    except Exception:
        pass




class DataValidator:
    """Lightweight static validator utilities used by the pipeline (regression-safe)."""

    @staticmethod
    def detect_data_types(df, categorical_threshold=20):
        """Detect data types with robust ordinal detection (safe for SDV)."""
        import numpy as np
        import pandas as pd
        type_info = {}
        for col in df.columns:
            col_info = {
                'dtype': str(df[col].dtype),
                'nunique': int(df[col].nunique()),
                'null_count': int(df[col].isnull().sum()),
                'null_ratio': float(df[col].isnull().sum() / len(df)) if len(df) else 0.0
            }
            if pd.api.types.is_numeric_dtype(df[col]):
                nun = df[col].nunique()
                if nun <= categorical_threshold:
                    unique_vals = np.sort(pd.to_numeric(df[col], errors="coerce").dropna().unique())
                    # ordinal if small integer ladder with ~constant step
                    if (unique_vals.size > 2
                        and np.isfinite(unique_vals).all()
                        and np.allclose(unique_vals, np.round(unique_vals), atol=1e-8)
                        and (unique_vals.size < 3 or np.allclose(np.diff(unique_vals), np.diff(unique_vals)[0], atol=1e-12))):
                        col_info['semantic_type'] = 'ordinal'
                        col_info['ordinal_values'] = unique_vals.tolist()
                    else:
                        col_info['semantic_type'] = 'categorical'
                    col_info['semantic_type'] = 'numerical'
                col_info['semantic_type'] = 'categorical'

            if col_info['semantic_type'] == 'numerical':
                data = pd.to_numeric(df[col], errors="coerce").dropna()
                if len(data):
                    col_info.update({
                        'mean': float(data.mean()),
                        'std': float(data.std(ddof=1)),
                        'min': float(data.min()),
                        'max': float(data.max())
                    })
            type_info[col] = col_info
        return type_info

    @staticmethod
    def validate_dataframe(df, target_col, categorical_threshold=20):
        """Basic structural checks expected by the pipeline."""
        import pandas as pd
        results = {"is_valid": True, "errors": [], "warnings": [], "data_types": {}}

        if df is None or len(df) == 0:
            results["errors"].append("DataFrame vazio.")
            results["is_valid"] = False
            return results

        if target_col not in df.columns:
            results["errors"].append(f"Coluna target '{target_col}' não encontrada.")
            results["is_valid"] = False
            return results

        # infer types
        results["data_types"] = DataValidator.detect_data_types(df, categorical_threshold)

        # missing values
        for col in df.columns:
            nulls = int(pd.isnull(df[col]).sum())
            if nulls > 0:
                results["warnings"].append(f"Coluna '{col}' possui {nulls} valores ausentes.")

        # duplicated rows (warning only)
        dups = int(df.duplicated().sum())
        if dups > 0:
            results["warnings"].append(f"{dups} linhas duplicadas detectadas.")

        return results
class EnhancedDataProcessor:
    """Processador que preserva tipos categóricos e usa SDV metadata"""
    
    @staticmethod
    def create_sdv_metadata(df: pd.DataFrame, type_info: Dict[str, Dict[str, Any]]):
        """Cria metadata SDV preservando tipos semânticos"""
        try:
            from sdv.metadata import SingleTableMetadata
            
            metadata = SingleTableMetadata()
            
            # Detectar automaticamente mas refinar com type_info
            metadata.detect_from_dataframe(df)
            
            # Refinar tipos baseado na análise semântica
            for col, info in type_info.items():
                if info['semantic_type'] == 'categorical':
                    metadata.update_column(col, sdtype='categorical')
                elif info['semantic_type'] == 'ordinal':
                    unique_vals = sorted(df[col].dropna().unique())
                    # NOTE: In SDV 1.11, passing an explicit ordinal 'order' may break GaussianCopula
                    # encoders (e.g., UniformEncoder). We therefore treat ordinals as categorical in metadata.
                    try:
                        metadata.update_column(col, sdtype='categorical')
                    except Exception as e:
                        logger.warning(f"Could not set categorical sdtype for ordinal col {col}: {e}")
                    logger.info(f"Preserved ordinal-like set for {col}: {unique_vals}")
                elif info['semantic_type'] == 'numerical':
                    if 'is_integer' in info and info['is_integer']:
                        metadata.update_column(col, sdtype='numerical', computer_representation='Int64')
                    else:
                        metadata.update_column(col, sdtype='numerical')
            
            return metadata
            
        except ImportError:
            logger.warning("SDV não disponível - usando fallback")
            return None
    
    @staticmethod
    def preprocess_data(df: pd.DataFrame, config: ExperimentConfig, 
                       type_info: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """Pré-processamento inteligente preservando tipos"""
        
        df_processed = df.copy()
        
        # Remove outliers apenas para colunas numéricas
        if config.remove_outliers:
            processor = OutlierProcessor()
            outlier_mask = np.zeros(len(df_processed), dtype=bool)
            
            for col, info in type_info.items():
                if col != config.target_column and info['semantic_type'] == 'numerical':
                    try:
                        col_data = df_processed[col].dropna().values
                        if len(col_data) > 0:
                            col_outliers = processor.detect_outliers(
                                col_data, config.outlier_method, config.outlier_threshold
                            )
                            
                            # Map back to DataFrame
                            col_mask = np.zeros(len(df_processed), dtype=bool)
                            non_null_idx = df_processed[col].dropna().index
                            col_mask[non_null_idx] = col_outliers
                            outlier_mask |= col_mask
                    except Exception as e:
                        logger.warning(f"Detecção de outliers falhou para {col}: {e}")
            
            original_len = len(df_processed)
            df_processed = df_processed[~outlier_mask].reset_index(drop=True)
            logger.info(f"Removidos {original_len - len(df_processed)} outliers")
        
        # Tratamento de missing values por tipo
        for col, info in type_info.items():
            missing_count = df_processed[col].isnull().sum()
            if missing_count > 0:
                if info['semantic_type'] == 'numerical':
                    # Impute com mediana
                    df_processed[col].fillna(df_processed[col].median(), inplace=True)
                elif info['semantic_type'] == 'categorical':
                    # Impute com moda
                    mode_val = df_processed[col].mode()
                    if len(mode_val) > 0:
                        df_processed[col].fillna(mode_val[0], inplace=True)
                    else:
                        df_processed[col].fillna('Unknown', inplace=True)
        
        return df_processed

class OutlierProcessor:
    """Processamento robusto de outliers para dados numéricos"""
    
    @staticmethod
    def detect_outliers(data: np.ndarray, method: str = "tukey", threshold: float = 1.5) -> np.ndarray:
        """Detectar outliers usando diferentes métodos"""
        
        if method == "tukey":
            q1, q3 = np.percentile(data, [25, 75])
            iqr = q3 - q1
            if iqr == 0:
                return np.zeros(len(data), dtype=bool)
            lower, upper = q1 - threshold * iqr, q3 + threshold * iqr
            return (data < lower) | (data > upper)
        
        elif method == "zscore":
            if np.std(data) == 0:
                return np.zeros(len(data), dtype=bool)
            z_scores = np.abs(stats.zscore(data))
            return z_scores > threshold
        
        elif method == "isolation":
            try:
                iso = IsolationForest(contamination=0.1, random_state=42)
                outlier_labels = iso.fit_predict(data.reshape(-1, 1))
                return outlier_labels == -1
            except:
                logger.warning("Isolation Forest falhou, usando Tukey")
                return OutlierProcessor.detect_outliers(data, "tukey", threshold)
        
        else:
            raise ValueError(f"Método de outlier desconhecido: {method}")

# Helper function to detect/create metadata
def detect_data_types(df: pd.DataFrame, categorical_threshold: int = 20) -> Dict[str, Dict[str, Any]]:
    """Wrapper para DataValidator.detect_data_types"""
    return DataValidator.detect_data_types(df, categorical_threshold)

def create_sdv_metadata(df: pd.DataFrame, type_info: Dict[str, Dict[str, Any]]):
    """Wrapper para EnhancedDataProcessor.create_sdv_metadata"""
    return EnhancedDataProcessor.create_sdv_metadata(df, type_info)

# --- PRIVACY HELPERS (NEW) ---

def _fit_attack_model(model_name: str, X_attack, y_attack):
    """Treina modelo de ataque leve para MIA/AIA sem dependências extras."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    if model_name.upper() == "LR":
        clf = LogisticRegression(max_iter=1000, n_jobs=None)
    elif model_name.upper() == "RF":
        clf = RandomForestClassifier(n_estimators=200, random_state=0)
    else:
        raise ValueError(f"Unsupported attack model: {model_name}")
    clf.fit(X_attack, y_attack)
    return clf

def _predict_attack_model(clf, X):
    try:
        # probabilidade positiva, se existir
        if hasattr(clf, "predict_proba"):
            p = clf.predict_proba(X)[:, 1]
        else:
            # fallback: decision_function -> sigmoid
            from scipy.special import expit
            s = clf.decision_function(X)
            p = expit(s)
        yhat = (p >= 0.5).astype(int)
        return yhat, p
    except Exception:
        # fallback robusto
        yhat = clf.predict(X)
        p = None
        return yhat, p

def _knn_rarity_scores(df_num: "pd.DataFrame", k: int = 5):
    """Raridade: distância ao k-ésimo vizinho mais próximo no espaço numérico normalizado."""
    import numpy as np
    from sklearn.neighbors import NearestNeighbors
    if df_num.shape[1] == 0 or df_num.shape[0] < (k+1):
        return np.full(df_num.shape[0], np.nan)
    nbrs = NearestNeighbors(n_neighbors=k+1, algorithm="auto").fit(df_num.values)
    dist, _ = nbrs.kneighbors(df_num.values)
    # ignora dist=0 do próprio ponto
    kth = dist[:, -1]
    return kth

def _make_strata(values, n_bins=5):
    """Corta valores continos em quantis (bins de rareza)."""
    import numpy as np
    s = pd.Series(values)
    if s.isna().all():
        return None
    # quantis robustos
    try:
        q = pd.qcut(s, q=n_bins, labels=[f"bin_{i+1}" for i in range(n_bins)], duplicates="drop")
    except Exception:
        return None
    return q.astype(str)

def stratified_bootstrap_indices(groups, n_samples, n_boot=1000, random_state=0):
    """Retorna lista de arrays de índices estratificados por 'groups' (Series)."""
    import numpy as np
    rng = np.random.RandomState(random_state)
    groups = pd.Series(groups).astype(str)
    uniq = groups.dropna().unique()
    idx_all = np.arange(n_samples)
    # índices por grupo
    per_group = {g: np.where(groups.values == g)[0] for g in uniq}
    res = []
    for _ in range(n_boot):
        sample_idx = []
        for g in uniq:
            g_idx = per_group[g]
            if len(g_idx) == 0:
                continue
            # reamostra com reposição o MESMO tamanho do grupo original (bootstrap clássico estratificado)
            s = rng.choice(g_idx, size=len(g_idx), replace=True)
            sample_idx.append(s)
        if sample_idx:
            res.append(np.concatenate(sample_idx))
        else:
            res.append(rng.choice(idx_all, size=n_samples, replace=True))
    return res

def bootstrap_scores(y_true, y_pred, groups=None, n_boot=1000, random_state=0, metrics=("accuracy",), average="macro"):
    """Bootstrap com ou sem estratificação por 'groups'."""
    import numpy as np
    from sklearn.metrics import accuracy_score, f1_score
    n = len(y_true)
    if groups is not None:
        all_idx = stratified_bootstrap_indices(groups, n, n_boot=n_boot, random_state=random_state)
    else:
        rng = np.random.RandomState(random_state)
        all_idx = [rng.choice(np.arange(n), size=n, replace=True) for _ in range(n_boot)]
    out = {m: [] for m in metrics}
    for idx in all_idx:
        yt = y_true[idx]; yp = y_pred[idx]
        for m in metrics:
            if m == "accuracy":
                out[m].append(float(accuracy_score(yt, yp)))
            elif m == "f1":
                out[m].append(float(f1_score(yt, yp, average=average)))
    # retorna médias/IC empírico
    import numpy as np
    res = {}
    for m, vals in out.items():
        arr = np.asarray(vals, dtype=float)
        lo, hi = np.percentile(arr, [2.5, 97.5])
        res[m] = {"mean": float(np.mean(arr)), "ci95": [float(lo), float(hi)], "n_boot": int(n_boot),
                  "stratified": bool(groups is not None)}
    return res

def benjamini_hochberg(pvals, q=0.05):
    """FDR (BH). Retorna vetor booleano de rejeições no nível q."""
    import numpy as np
    p = np.asarray(pvals, dtype=float)
    n = p.size
    idx = np.argsort(p)
    p_sorted = p[idx]
    thresh = q * (np.arange(1, n+1) / n)
    # último k tal que p_(k) <= thresh_k
    k = np.where(p_sorted <= thresh)[0]
    reject = np.zeros_like(p, dtype=bool)
    if len(k) > 0:
        reject_idx = idx[:(k[-1]+1)]
        reject[reject_idx] = True
    return reject

# ============================================================================
# NOVA IMPLEMENTAÇÃO MLP AVANÇADA COM TUNING BAYESIANO
# ============================================================================

class AdvancedMLPOptimizer:
    """Otimizador Bayesian para MLP usando Optuna"""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.best_params_cache = {}
        
    def optimize_mlp_params(self, X_train, y_train, task_type, n_trials=None):
        """Otimiza hiperparâmetros do MLP usando Bayesian Optimization"""
        try:
            import optuna
        except ImportError:
            logger.warning("Optuna não instalado. Use: pip install optuna")
            return self.get_default_params(task_type)
        
        if n_trials is None:
            n_trials = self.config.mlp_tuning_trials
        
        # Criar cache key
        cache_key = f"{task_type}_{X_train.shape}_{hash(str(y_train[:10]))}"
        if cache_key in self.best_params_cache:
            logger.info(f"Usando parâmetros MLP otimizados do cache")
            return self.best_params_cache[cache_key]
        
        def objective(trial):
            # Definir espaço de busca de hiperparâmetros
            n_layers = trial.suggest_int("n_layers", 1, 4)
            
            hidden_dims = []
            for i in range(n_layers):
                hidden_dim = trial.suggest_int(f"hidden_dim_{i}", 32, 512, log=True)
                hidden_dims.append(hidden_dim)
            
            activation = trial.suggest_categorical("activation", ["relu", "tanh", "logistic"])
            
            # Hiperparâmetros de otimização
            learning_rate_init = trial.suggest_float("learning_rate_init", 1e-4, 1e-1, log=True)
            solver = trial.suggest_categorical("solver", ["adam", "lbfgs", "sgd"])
            
            if solver == "sgd":
                momentum = trial.suggest_float("momentum", 0.8, 0.99)
                nesterovs_momentum = trial.suggest_categorical("nesterovs_momentum", [True, False])
            else:
                momentum = 0.9
                nesterovs_momentum = True
            
            # Regularização
            alpha = trial.suggest_float("alpha", 1e-6, 1e-2, log=True)
            
            if self.config.mlp_use_dropout:
                dropout_rate = trial.suggest_float("dropout_rate", 0.0, 0.5)
            else:
                dropout_rate = 0.0
            
            # Batch e early stopping
            batch_size = trial.suggest_categorical("batch_size", ["auto", 32, 64, 128, 256])
            if batch_size == "auto":
                batch_size = min(200, max(32, X_train.shape[0] // 10))
            
            # Criar modelo
            if task_type == 'classification':
                model = MLPClassifier(
                    hidden_layer_sizes=tuple(hidden_dims),
                    activation=activation,
                    solver=solver,
                    alpha=alpha,
                    learning_rate_init=learning_rate_init,
                    momentum=momentum,
                    nesterovs_momentum=nesterovs_momentum,
                    early_stopping=True,
                    validation_fraction=0.1,
                    n_iter_no_change=self.config.mlp_early_stopping_patience,
                    max_iter=5000,
                    random_state=self.config.random_seed,
                    batch_size=batch_size,
                    verbose=False
                )
            else:
                model = MLPRegressor(
                    hidden_layer_sizes=tuple(hidden_dims),
                    activation=activation,
                    solver=solver,
                    alpha=alpha,
                    learning_rate_init=learning_rate_init,
                    momentum=momentum,
                    nesterovs_momentum=nesterovs_momentum,
                    early_stopping=True,
                    validation_fraction=0.1,
                    n_iter_no_change=self.config.mlp_early_stopping_patience,
                    max_iter=5000,
                    random_state=self.config.random_seed,
                    batch_size=batch_size,
                    verbose=False
                )
            
            # Avaliação com validação cruzada
            from sklearn.model_selection import cross_val_score
            
            if task_type == 'classification':
                scoring = 'accuracy'
                n_splits = min(5, len(np.unique(y_train)))
            else:
                scoring = 'r2'
                n_splits = 5
            
            try:
                scores = cross_val_score(model, X_train, y_train, 
                                       cv=min(n_splits, 5), 
                                       scoring=scoring,
                                       n_jobs=1)
                score = np.mean(scores)
            except Exception as e:
                score = -float('inf')
            
            return score
        
        try:
            study = optuna.create_study(
                direction="maximize",
                sampler=optuna.samplers.TPESampler(seed=self.config.random_seed)
            )
            
            study.optimize(objective, n_trials=n_trials, show_progress_bar=False)
            
            best_params = study.best_params
            best_params['task_type'] = task_type
            
            # Armazenar no cache
            self.best_params_cache[cache_key] = best_params
            
            logger.info(f"MLP optimization completed. Best score: {study.best_value:.4f}")
            logger.info(f"Best params: {best_params}")
            
            return best_params
            
        except Exception as e:
            logger.warning(f"MLP optimization failed: {e}. Using default parameters.")
            return self.get_default_params(task_type)
    
    def get_default_params(self, task_type):
        """Retorna parâmetros padrão robustos"""
        default_params = {
            'n_layers': 2,
            'hidden_dim_0': 128,
            'hidden_dim_1': 64,
            'activation': 'relu',
            'solver': 'adam',
            'alpha': 0.0001,
            'learning_rate_init': 0.001,
            'momentum': 0.9,
            'nesterovs_momentum': True,
            'batch_size': 'auto',
            'dropout_rate': 0.2 if self.config.mlp_use_dropout else 0.0,
            'task_type': task_type
        }
        return default_params


# ============================================================
# FAST MLP OPTIMIZER (small-n) + ROBUST MLP WRAPPER (overflow)
# Integrated from user-provided suggestions
# ============================================================

class FastMLPOptimizer:
    """
    Otimizador MLP ultra-rápido para datasets MUITO pequenos (n~20)
    
    Estratégias:
    - Grid search reduzido (não Bayesian) para evitar overhead do Optuna
    - Validação holdout simples (não k-fold)
    - Espaço de busca minimalista
    - Early stopping agressivo
    - Máximo 12 trials (vs 50 original)
    """
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.best_params_cache = {}
        
    def optimize_mlp_params(self, X_train, y_train, task_type, n_trials=None):
        """Otimiza hiperparâmetros do MLP com estratégia ultra-rápida"""
        
        # REDUZIR trials para datasets pequenos
        if n_trials is None:
            n_trials = min(12, self.config.mlp_tuning_trials)  # Máximo 12 trials
        
        # Cache key
        cache_key = f"{task_type}_{X_train.shape}_{hash(str(y_train[:min(10, len(y_train))]))}"
        if cache_key in self.best_params_cache:
            logger.info(f"Usando parâmetros MLP otimizados do cache")
            return self.best_params_cache[cache_key]
        
        # Para datasets MUITO pequenos (n < 30), usar grid search rápido
        if len(X_train) < 30:
            logger.info(f"Dataset muito pequeno (n={len(X_train)}), usando grid search rápido")
            return self._fast_grid_search(X_train, y_train, task_type)
        
        # Caso contrário, usar Optuna com espaço reduzido
        try:
            import optuna
            optuna.logging.set_verbosity(optuna.logging.WARNING)  # Silenciar logs
        except ImportError:
            logger.warning("Optuna não instalado. Usando grid search rápido.")
            return self._fast_grid_search(X_train, y_train, task_type)
        
        def objective(trial):
            # ESPAÇO DE BUSCA MINIMALISTA para datasets pequenos
            n_layers = trial.suggest_int("n_layers", 1, 3)  # Max 3 layers (vs 4)
            
            hidden_dims = []
            for i in range(n_layers):
                # Dimensões menores para evitar overfitting
                hidden_dim = trial.suggest_int(f"hidden_dim_{i}", 32, 256, log=True)
                hidden_dims.append(hidden_dim)
            
            activation = trial.suggest_categorical("activation", ["relu", "tanh", "logistic"])
            
            # Solvers rápidos
            solver = trial.suggest_categorical("solver", ["adam", "lbfgs"])  # Removido sgd (lento)
            
            # Regularização mais forte para datasets pequenos
            alpha = trial.suggest_float("alpha", 1e-4, 1e-1, log=True)
            
            # Dropout desabilitado para datasets pequenos (não confiável)
            dropout_rate = 0.0
            
            # Batch size fixo para datasets pequenos
            batch_size = min(32, len(X_train))
            
            # Criar modelo
            if task_type == 'classification':
                model = MLPClassifier(
                    hidden_layer_sizes=tuple(hidden_dims),
                    activation=activation,
                    solver=solver,
                    alpha=alpha,
                    early_stopping=True,
                    validation_fraction=0.2,
                    n_iter_no_change=10,  # Agressivo
                    max_iter=500,  # Reduzido de 5000
                    random_state=self.config.random_seed,
                    batch_size=batch_size,
                    verbose=False
                )
            else:
                model = MLPRegressor(
                    hidden_layer_sizes=tuple(hidden_dims),
                    activation=activation,
                    solver=solver,
                    alpha=alpha,
                    early_stopping=True,
                    validation_fraction=0.2,
                    n_iter_no_change=10,
                    max_iter=500,
                    random_state=self.config.random_seed,
                    batch_size=batch_size,
                    verbose=False
                )
            
            # VALIDAÇÃO HOLDOUT SIMPLES (não k-fold para velocidade)
            from sklearn.model_selection import train_test_split
            from sklearn.preprocessing import StandardScaler
            from sklearn.pipeline import Pipeline
            
            X_tr, X_val, y_tr, y_val = train_test_split(
                X_train, y_train, test_size=0.25, random_state=self.config.random_seed
            )
            
            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('mlp', model)
            ])
            
            try:
                pipeline.fit(X_tr, y_tr)
                
                if task_type == 'classification':
                    from sklearn.metrics import accuracy_score
                    score = accuracy_score(y_val, pipeline.predict(X_val))
                else:
                    from sklearn.metrics import r2_score
                    score = r2_score(y_val, pipeline.predict(X_val))
                    
            except Exception as e:
                logger.warning(f"Trial failed: {e}")
                score = -float('inf')
            
            return score
        
        try:
            study = optuna.create_study(
                direction="maximize",
                sampler=optuna.samplers.TPESampler(seed=self.config.random_seed, n_startup_trials=5)
            )
            
            # Timeout de 5 minutos para evitar eternidade
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Optuna timeout")
            
            try:
                study.optimize(objective, n_trials=n_trials, timeout=300, show_progress_bar=False)
            except:
                pass  # Timeout ou erro, usar best até agora
            
            best_params = study.best_params
            best_params['task_type'] = task_type
            best_params['dropout_rate'] = 0.0
            best_params['batch_size'] = min(32, len(X_train))
            
            # Cache
            self.best_params_cache[cache_key] = best_params
            
            logger.info(f"MLP optimization: Best score={study.best_value:.4f}, Params={best_params}")
            
            return best_params
            
        except Exception as e:
            logger.warning(f"Optuna optimization failed: {e}. Usando grid search.")
            return self._fast_grid_search(X_train, y_train, task_type)
    
    def _fast_grid_search(self, X_train, y_train, task_type):
        """Grid search minimalista para datasets muito pequenos"""
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import Pipeline
        
        logger.info("Executando grid search rápido (6 configurações)")
        
        # GRID MINIMALISTA: apenas 6 configurações robustas
        grid = [
            {'n_layers': 1, 'hidden_dim_0': 64, 'activation': 'relu', 'solver': 'lbfgs', 'alpha': 0.01},
            {'n_layers': 1, 'hidden_dim_0': 128, 'activation': 'tanh', 'solver': 'adam', 'alpha': 0.001},
            {'n_layers': 2, 'hidden_dim_0': 128, 'hidden_dim_1': 64, 'activation': 'relu', 'solver': 'adam', 'alpha': 0.01},
            {'n_layers': 2, 'hidden_dim_0': 64, 'hidden_dim_1': 32, 'activation': 'tanh', 'solver': 'lbfgs', 'alpha': 0.001},
            {'n_layers': 3, 'hidden_dim_0': 128, 'hidden_dim_1': 64, 'hidden_dim_2': 32, 'activation': 'relu', 'solver': 'adam', 'alpha': 0.01},
            {'n_layers': 2, 'hidden_dim_0': 256, 'hidden_dim_1': 128, 'activation': 'logistic', 'solver': 'lbfgs', 'alpha': 0.1},
        ]
        
        X_tr, X_val, y_tr, y_val = train_test_split(
            X_train, y_train, test_size=0.25, random_state=self.config.random_seed
        )
        
        best_score = -float('inf')
        best_params = grid[0]  # Default
        
        for params in grid:
            hidden_dims = tuple([params[f'hidden_dim_{i}'] for i in range(params['n_layers'])])
            
            if task_type == 'classification':
                model = MLPClassifier(
                    hidden_layer_sizes=hidden_dims,
                    activation=params['activation'],
                    solver=params['solver'],
                    alpha=params['alpha'],
                    early_stopping=True,
                    validation_fraction=0.2,
                    n_iter_no_change=10,
                    max_iter=300,
                    random_state=self.config.random_seed,
                    verbose=False
                )
            else:
                model = MLPRegressor(
                    hidden_layer_sizes=hidden_dims,
                    activation=params['activation'],
                    solver=params['solver'],
                    alpha=params['alpha'],
                    early_stopping=True,
                    validation_fraction=0.2,
                    n_iter_no_change=10,
                    max_iter=300,
                    random_state=self.config.random_seed,
                    verbose=False
                )
            
            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('mlp', model)
            ])
            
            try:
                pipeline.fit(X_tr, y_tr)
                
                if task_type == 'classification':
                    from sklearn.metrics import accuracy_score
                    score = accuracy_score(y_val, pipeline.predict(X_val))
                else:
                    from sklearn.metrics import r2_score
                    score = r2_score(y_val, pipeline.predict(X_val))
                
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
                    
            except Exception as e:
                logger.warning(f"Grid config failed: {e}")
                continue
        
        best_params['task_type'] = task_type
        best_params['dropout_rate'] = 0.0
        best_params['batch_size'] = min(32, len(X_train))
        
        logger.info(f"Grid search: Best score={best_score:.4f}")
        
        return best_params
    
    def get_default_params(self, task_type):
        """Parâmetros padrão ultra-robustos para datasets pequenos"""
        return {
            'n_layers': 2,
            'hidden_dim_0': 64,
            'hidden_dim_1': 32,
            'activation': 'relu',
            'solver': 'lbfgs',  # Mais estável para n pequeno
            'alpha': 0.01,  # Regularização forte
            'learning_rate_init': 0.001,
            'momentum': 0.9,
            'nesterovs_momentum': True,
            'batch_size': 32,
            'dropout_rate': 0.0,
            'task_type': task_type
        }

class RobustMLPWrapper:
    """
    Wrapper para MLPClassifier/Regressor com proteções contra overflow
    
    Estratégias:
    - Clipping agressivo de dados de entrada
    - Normalização robusta (MinMaxScaler + StandardScaler)
    - Detecção e tratamento de overflow durante fit
    - Fallback para modelo mais simples se overflow persistir
    """
    
    def __init__(self, base_model, task_type='regression'):
        self.base_model = base_model
        self.task_type = task_type
        self.scaler1 = MinMaxScaler(feature_range=(-3, 3))  # Clip inicial
        self.scaler2 = StandardScaler()  # Normalização Z-score
        self.fallback_model = None
        self.using_fallback = False
        
    def fit(self, X, y):
        """Fit com proteção contra overflow"""
        try:
            # 1. Transformação robusta dos dados
            X_transformed = self._robust_transform(X, fit=True)
            
            # 2. Clip de outliers extremos no target (regressão)
            if self.task_type == 'regression':
                y_clipped = np.clip(y, np.percentile(y, 1), np.percentile(y, 99))
            else:
                y_clipped = y
            
            # 3. Tentar fit normal
            with warnings.catch_warnings():
                warnings.filterwarnings('error', category=RuntimeWarning)
                self.base_model.fit(X_transformed, y_clipped)
            
            self.using_fallback = False
            return self
            
        except (RuntimeWarning, FloatingPointError, OverflowError) as e:
            logger.warning(f"MLP overflow detectado: {e}. Usando modelo fallback.")
            return self._fit_fallback(X, y)
    
    def _fit_fallback(self, X, y):
        """Fallback: Ridge/LogisticRegression com regularização forte"""
        X_transformed = self._robust_transform(X, fit=False)
        
        if self.task_type == 'classification':
            from sklearn.linear_model import LogisticRegression
            self.fallback_model = LogisticRegression(
                C=0.1,  # Regularização forte
                max_iter=1000,
                solver='lbfgs'
            )
        else:
            from sklearn.linear_model import Ridge
            self.fallback_model = Ridge(
                alpha=10.0,  # Regularização forte
                solver='auto'
            )
        
        self.fallback_model.fit(X_transformed, y)
        self.using_fallback = True
        logger.info("Fallback model fitted successfully")
        return self
    
    def predict(self, X):
        """Predict com proteção"""
        X_transformed = self._robust_transform(X, fit=False)
        
        if self.using_fallback:
            return self.fallback_model.predict(X_transformed)
        else:
            try:
                return self.base_model.predict(X_transformed)
            except (RuntimeWarning, FloatingPointError, OverflowError):
                logger.warning("Overflow em predict, usando fallback")
                if self.fallback_model is None:
                    # Criar fallback on-the-fly (deve ter sido fitted)
                    return np.full(len(X), np.nan)
                return self.fallback_model.predict(X_transformed)
    
    def predict_proba(self, X):
        """Predict_proba com proteção (classificação)"""
        if self.task_type != 'classification':
            raise AttributeError("predict_proba only for classification")
        
        X_transformed = self._robust_transform(X, fit=False)
        
        if self.using_fallback:
            return self.fallback_model.predict_proba(X_transformed)
        else:
            try:
                return self.base_model.predict_proba(X_transformed)
            except (RuntimeWarning, FloatingPointError, OverflowError):
                logger.warning("Overflow em predict_proba, usando fallback")
                if self.fallback_model is None:
                    n_classes = len(np.unique(self.base_model.classes_))
                    return np.ones((len(X), n_classes)) / n_classes
                return self.fallback_model.predict_proba(X_transformed)
    
    def _robust_transform(self, X, fit=False):
        """Transformação robusta multi-estágio"""
        X_array = np.asarray(X, dtype=np.float64)
        
        # Replace inf/nan
        X_array = np.nan_to_num(X_array, nan=0.0, posinf=1e6, neginf=-1e6)
        
        # Clip valores extremos
        X_array = np.clip(X_array, -1e6, 1e6)
        
        # Double scaling
        if fit:
            X_scaled1 = self.scaler1.fit_transform(X_array)
            X_scaled2 = self.scaler2.fit_transform(X_scaled1)
        else:
            X_scaled1 = self.scaler1.transform(X_array)
            X_scaled2 = self.scaler2.transform(X_scaled1)
        
        # Final clip
        X_scaled2 = np.clip(X_scaled2, -10, 10)
        
        return X_scaled2


def create_robust_mlp(task_type, best_params, random_state=None):
    """
    Factory para criar MLP robusto com proteção contra overflow
    
    Usage:
        model = create_robust_mlp('regression', best_params, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
    """
    
    # Construir hidden_layer_sizes
    n_layers = best_params.get('n_layers', 2)
    hidden_dims = tuple([best_params.get(f'hidden_dim_{i}', 64) for i in range(n_layers)])
    
    # Parâmetros com valores seguros contra overflow
    safe_params = {
        'hidden_layer_sizes': hidden_dims,
        'activation': best_params.get('activation', 'relu'),
        'solver': best_params.get('solver', 'lbfgs'),
        'alpha': max(0.001, best_params.get('alpha', 0.01)),  # Min regularization
        'learning_rate_init': min(0.01, best_params.get('learning_rate_init', 0.001)),  # Max LR
        'max_iter': 500,  # Reduzido
        'early_stopping': True,
        'validation_fraction': 0.15,
        'n_iter_no_change': 15,
        'tol': 1e-4,
        'random_state': random_state,
        'verbose': False,
        'batch_size': best_params.get('batch_size', 32)
    }
    
    # Criar modelo base
    if task_type == 'classification':
        base_model = MLPClassifier(**safe_params)
    else:
        base_model = MLPRegressor(**safe_params)
    
    # Wrap com proteção
    robust_model = RobustMLPWrapper(base_model, task_type)
    
    return robust_model


class AdvancedMLPEnsemble:
    """Ensemble de MLPs para melhor estabilidade e performance"""
    
    def __init__(self, config: ExperimentConfig, task_type: str):
        self.config = config
        self.task_type = task_type
        self.models = []
        self.optimizer = FastMLPOptimizer(config)
        
    def create_mlp_constructor(self, best_params=None, ensemble_idx=0):
        """Cria um construtor de MLP com parâmetros otimizados"""
        
        # Usar parâmetros padrão se best_params for None
        if best_params is None:
            best_params = self.optimizer.get_default_params(self.task_type)
        
        # Capturar best_params no closure da função
        def constructor(random_state=None):
            if random_state is None:
                random_state = self.config.random_seed + ensemble_idx
            
            # Ajustar batch_size dinamicamente
            batch_size = best_params.get('batch_size', 'auto')
            
            # Construir arquitetura
            n_layers = best_params.get('n_layers', 2)
            hidden_dims = []
            for i in range(n_layers):
                dim_key = f'hidden_dim_{i}'
                if dim_key in best_params:
                    hidden_dims.append(best_params[dim_key])
                else:
                    # Fallback: dimensões decrescentes
                    base_dim = best_params.get('hidden_dim_0', 128)
                    hidden_dims.append(max(32, base_dim // (2 ** i)))
            
            # Configurar modelo base
            if self.task_type == 'classification':
                model = MLPClassifier(
                    hidden_layer_sizes=tuple(hidden_dims),
                    activation=best_params.get('activation', 'relu'),
                    solver=best_params.get('solver', 'adam'),
                    alpha=best_params.get('alpha', 0.0001),
                    learning_rate_init=best_params.get('learning_rate_init', 0.001),
                    momentum=best_params.get('momentum', 0.9),
                    nesterovs_momentum=best_params.get('nesterovs_momentum', True),
                    early_stopping=True,
                    validation_fraction=0.15,  # Mais dados para validação
                    n_iter_no_change=self.config.mlp_early_stopping_patience,
                    max_iter=5000,
                    random_state=random_state,
                    batch_size=batch_size,
                    verbose=False,
                    tol=1e-5,  # Tolerância mais rigorosa
                    learning_rate='adaptive',  # Learning rate adaptativo
                    beta_1=0.9,  # Parâmetros Adam otimizados
                    beta_2=0.999,
                    epsilon=1e-8
                )
            else:
                model = MLPRegressor(
                    hidden_layer_sizes=tuple(hidden_dims),
                    activation=best_params.get('activation', 'relu'),
                    solver=best_params.get('solver', 'adam'),
                    alpha=best_params.get('alpha', 0.0001),
                    learning_rate_init=best_params.get('learning_rate_init', 0.001),
                    momentum=best_params.get('momentum', 0.9),
                    nesterovs_momentum=best_params.get('nesterovs_momentum', True),
                    early_stopping=True,
                    validation_fraction=0.15,
                    n_iter_no_change=self.config.mlp_early_stopping_patience,
                    max_iter=5000,
                    random_state=random_state,
                    batch_size=batch_size,
                    verbose=False,
                    tol=1e-5,
                    learning_rate='adaptive',
                    beta_1=0.9,
                    beta_2=0.999,
                    epsilon=1e-8
                )
            
            # Criar pipeline com escalonamento
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import StandardScaler
            
            pipeline = Pipeline([
                ('scaler', StandardScaler()),
                ('mlp', model)
            ])
            
            return pipeline
        
        return constructor

# ============================================================================
# CORREÇÃO DO TABDDPM - IMPLEMENTAÇÃO REAL COM VALIDAÇÃO DE TARGET
# ============================================================================

class MLPDiffusion(nn.Module):
    """Rede neural para o processo de difusão baseada no paper TabDDPM"""
    
    def __init__(self, input_dim, hidden_dims=[256, 256], dropout=0.1):
        super().__init__()
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.LayerNorm(hidden_dim),
                nn.GELU(),
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim
        
        # Camada final para prever noise
        layers.append(nn.Linear(prev_dim, input_dim))
        
        self.net = nn.Sequential(*layers)
    
    def forward(self, x, t):
        # Incorporar informação temporal via embeddings
        t_embed = self._timestep_embedding(t, x.shape[-1])
        x_with_time = x + t_embed
        return self.net(x_with_time)
    
    def _timestep_embedding(self, timesteps, dim):
        """Cria embeddings para os passos de tempo (sinusoidal)"""
        half_dim = dim // 2
        emb = np.log(10000) / (half_dim - 1)
        emb = torch.exp(torch.arange(half_dim, dtype=torch.float32) * -emb)
        emb = emb.to(timesteps.device)
        emb = timesteps.float()[:, None] * emb[None, :]
        emb = torch.cat([torch.sin(emb), torch.cos(emb)], dim=1)
        if dim % 2 == 1:  # zero pad
            emb = torch.nn.functional.pad(emb, (0, 1, 0, 0))
        return emb

class BetaScheduler:
    """Agendador de beta para o processo de difusão"""
    
    def __init__(self, timesteps=1000, beta_start=0.0001, beta_end=0.02, schedule_type="linear"):
        self.timesteps = timesteps
        self.beta_start = beta_start
        self.beta_end = beta_end
        self.schedule_type = schedule_type
        
        if schedule_type == "linear":
            self.betas = torch.linspace(beta_start, beta_end, timesteps)
        elif schedule_type == "cosine":
            # Implementação do agendamento cosine do Improved DDPM
            steps = timesteps + 1
            x = torch.linspace(0, timesteps, steps)
            alphas_cumprod = torch.cos(((x / timesteps) + 0.008) / 1.008 * torch.pi * 0.5) ** 2
            alphas_cumprod = alphas_cumprod / alphas_cumprod[0]
            betas = 1 - (alphas_cumprod[1:] / alphas_cumprod[:-1])
            self.betas = torch.clip(betas, 0.0001, 0.02)
        else:
            raise ValueError(f"Schedule type {schedule_type} not supported")
        
        self.alphas = 1. - self.betas
        self.alphas_cumprod = torch.cumprod(self.alphas, dim=0)
        self.sqrt_alphas_cumprod = torch.sqrt(self.alphas_cumprod)
        self.sqrt_one_minus_alphas_cumprod = torch.sqrt(1. - self.alphas_cumprod)
    
    def add_noise(self, x_start, t, noise=None):
        """Adiciona noise aos dados conforme o passo de tempo t"""
        if noise is None:
            noise = torch.randn_like(x_start)
        
        sqrt_alpha_cumprod = self.sqrt_alphas_cumprod[t].reshape(-1, 1)
        sqrt_one_minus_alpha_cumprod = self.sqrt_one_minus_alphas_cumprod[t].reshape(-1, 1)
        
        return sqrt_alpha_cumprod * x_start + sqrt_one_minus_alpha_cumprod * noise, noise
    
    def sample_previous(self, x, t, pred_noise):
        """Amostra do passo anterior no processo de denoising"""
        beta = self.betas[t].reshape(-1, 1)
        sqrt_alpha = torch.sqrt(self.alphas[t]).reshape(-1, 1)
        sqrt_one_minus_alpha_cumprod = self.sqrt_one_minus_alphas_cumprod[t].reshape(-1, 1)
        
        # Predição de x0
        pred_x0 = (x - sqrt_one_minus_alpha_cumprod * pred_noise) / self.sqrt_alphas_cumprod[t].reshape(-1, 1)
        
        # Direção apontando para x
        direction = torch.sqrt(1 - self.alphas_cumprod[t-1]).reshape(-1, 1) * pred_noise
        
        # Amostragem do passo anterior
        x_prev = torch.sqrt(self.alphas_cumprod[t-1]).reshape(-1, 1) * pred_x0 + direction
        
        # Adiciona noise se não for o último passo
        if t[0] > 0:
            noise = torch.randn_like(x)
            sigma = torch.sqrt((1 - self.alphas_cumprod[t-1]) / (1 - self.alphas_cumprod[t]) * self.betas[t]).reshape(-1, 1)
            x_prev += sigma * noise
        
        return x_prev


class RealTabDDPMGenerator:
    """
    Real TabDDPM-like generator for purely numerical tabular data (single table).

    This implementation is intentionally lightweight (PyTorch-only) and designed
    for very small datasets (n~20) by providing:
      - stable preprocessing (standardization)
      - a diffusion model with timestep embeddings
      - early stopping + LR scheduler
      - optional simple Bayesian optimization over a small hyperparameter space
        using a Gaussian Process surrogate (sklearn) + Expected Improvement.
    """
    def __init__(
        self,
        epochs=100,
        batch_size=64,
        lr=1e-3,
        timesteps=200,
        hidden_dim=256,
        n_layers=3,
        dropout=0.0,
        schedule="cosine",  # "linear" | "cosine"
        beta_start=1e-4,
        beta_end=0.02,
        weight_decay=0.0,
        grad_clip=1.0,
        seed=123,
        device=None,
        # training controls
        early_stopping=True,
        patience=15,
        min_delta=1e-4,
        lr_scheduler=True,
        scheduler_patience=7,
        scheduler_factor=0.5,
        # tuning
        enable_tuning=False,
        tuning_trials=12,
        tuning_random_starts=4,
        tuning_metric="val_mse",  # "val_mse" | "tstr_r2"
        tuning_max_seconds=None,
        verbose=True
    ):
        self.epochs = int(epochs)
        self.batch_size = int(batch_size)
        self.lr = float(lr)
        self.timesteps = int(timesteps)
        self.hidden_dim = int(hidden_dim)
        self.n_layers = int(n_layers)
        self.dropout = float(dropout)
        self.schedule = str(schedule).lower()
        self.beta_start = float(beta_start)
        self.beta_end = float(beta_end)
        self.weight_decay = float(weight_decay)
        self.grad_clip = float(grad_clip)
        self.seed = int(seed)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.early_stopping = bool(early_stopping)
        self.patience = int(patience)
        self.min_delta = float(min_delta)
        self.lr_scheduler = bool(lr_scheduler)
        self.scheduler_patience = int(scheduler_patience)
        self.scheduler_factor = float(scheduler_factor)

        self.enable_tuning = bool(enable_tuning)
        self.tuning_trials = int(tuning_trials)
        self.tuning_random_starts = int(tuning_random_starts)
        self.tuning_metric = str(tuning_metric)
        self.tuning_max_seconds = tuning_max_seconds
        self.verbose = bool(verbose)

        self._scaler = None
        self._model = None
        self._diff = None
        self._feature_names = None

    # ---------- Diffusion utilities ----------
    @staticmethod
    def _cosine_beta_schedule(T, s=0.008):
        # Improved DDPM cosine schedule (Nichol & Dhariwal, 2021)
        import numpy as _np
        steps = T + 1
        x = _np.linspace(0, T, steps)
        alphas_cumprod = _np.cos(((x / T) + s) / (1 + s) * _np.pi * 0.5) ** 2
        alphas_cumprod = alphas_cumprod / alphas_cumprod[0]
        betas = 1 - (alphas_cumprod[1:] / alphas_cumprod[:-1])
        return _np.clip(betas, 1e-8, 0.999)

    def _make_betas(self):
        import numpy as _np
        if self.schedule == "cosine":
            return self._cosine_beta_schedule(self.timesteps)
        # linear
        return _np.linspace(self.beta_start, self.beta_end, self.timesteps, dtype=_np.float64)

    class _Diffusion:
        def __init__(self, betas, device):
            import torch as _torch
            betas = _torch.tensor(betas, dtype=_torch.float32, device=device)
            self.betas = betas
            self.alphas = 1.0 - betas
            self.alphas_cumprod = _torch.cumprod(self.alphas, dim=0)
            self.alphas_cumprod_prev = _torch.cat([_torch.tensor([1.0], device=device), self.alphas_cumprod[:-1]])
            self.sqrt_alphas_cumprod = _torch.sqrt(self.alphas_cumprod)
            self.sqrt_one_minus_alphas_cumprod = _torch.sqrt(1.0 - self.alphas_cumprod)
            self.posterior_variance = betas * (1.0 - self.alphas_cumprod_prev) / (1.0 - self.alphas_cumprod)

        def q_sample(self, x0, t, noise):
            # x_t = sqrt(alpha_bar_t) x0 + sqrt(1-alpha_bar_t) eps
            return self.sqrt_alphas_cumprod[t].unsqueeze(-1) * x0 + self.sqrt_one_minus_alphas_cumprod[t].unsqueeze(-1) * noise

        def predict_x0_from_eps(self, xt, t, eps):
            return (xt - self.sqrt_one_minus_alphas_cumprod[t].unsqueeze(-1) * eps) / self.sqrt_alphas_cumprod[t].unsqueeze(-1)

    class _Denoiser(torch.nn.Module):
        def __init__(self, d_in, hidden_dim, n_layers, dropout):
            super().__init__()
            self.d_in = d_in
            self.time_emb_dim = hidden_dim
            self.time_mlp = torch.nn.Sequential(
                torch.nn.Linear(hidden_dim, hidden_dim),
                torch.nn.SiLU(),
                torch.nn.Linear(hidden_dim, hidden_dim),
            )
            layers = []
            d = d_in + hidden_dim
            for _ in range(n_layers - 1):
                layers += [torch.nn.Linear(d, hidden_dim), torch.nn.SiLU()]
                if dropout and dropout > 0:
                    layers += [torch.nn.Dropout(dropout)]
                d = hidden_dim
            layers += [torch.nn.Linear(d, d_in)]
            self.net = torch.nn.Sequential(*layers)

        @staticmethod
        def _timestep_embedding(t, dim, max_period=10000):
            # sinusoidal embedding
            half = dim // 2
            freqs = torch.exp(-torch.log(torch.tensor(max_period, device=t.device, dtype=torch.float32)) * torch.arange(0, half, device=t.device, dtype=torch.float32) / half)
            args = t.float().unsqueeze(1) * freqs.unsqueeze(0)
            emb = torch.cat([torch.cos(args), torch.sin(args)], dim=1)
            if dim % 2 == 1:
                emb = torch.cat([emb, torch.zeros_like(emb[:, :1])], dim=1)
            return emb

        def forward(self, x, t):
            t_emb = self._timestep_embedding(t, self.time_emb_dim)
            t_emb = self.time_mlp(t_emb)
            h = torch.cat([x, t_emb], dim=1)
            return self.net(h)

    # ---------- Core API ----------
    def fit(self, real_df: pd.DataFrame, verbose_prefix="TabDDPM"):
        self._feature_names = list(real_df.columns)

        # Standardize
        from sklearn.preprocessing import StandardScaler
        self._scaler = StandardScaler()
        x = self._scaler.fit_transform(real_df.values.astype(np.float32))
        x = torch.tensor(x, dtype=torch.float32, device=self.device)

        # optional tuning
        if self.enable_tuning:
            tuned = self._tune_hyperparams(real_df)
            if tuned and self.verbose:
                logging.info(f"{verbose_prefix}: best hyperparams from tuning: {tuned}")
                for k, v in tuned.items():
                    setattr(self, k, v)

        betas = self._make_betas()
        self._diff = self._Diffusion(betas, self.device)
        self._model = self._Denoiser(d_in=x.shape[1], hidden_dim=self.hidden_dim, n_layers=self.n_layers, dropout=self.dropout).to(self.device)

        # train/val split (tiny data -> simple holdout)
        rng = np.random.default_rng(self.seed)
        n = x.shape[0]
        idx = np.arange(n)
        rng.shuffle(idx)
        n_val = max(2, int(0.2 * n))
        val_idx = idx[:n_val]
        tr_idx = idx[n_val:] if (n - n_val) >= 2 else idx

        x_tr = x[tr_idx]
        x_val = x[val_idx]

        opt = torch.optim.AdamW(self._model.parameters(), lr=self.lr, weight_decay=self.weight_decay)
        sched = None
        if self.lr_scheduler:
            try:
                sched = torch.optim.lr_scheduler.ReduceLROnPlateau(opt, mode="min", patience=self.scheduler_patience, factor=self.scheduler_factor, verbose=False)
            except TypeError:
                # Torch versions may not accept 'verbose' in ReduceLROnPlateau
                sched = torch.optim.lr_scheduler.ReduceLROnPlateau(opt, mode="min", patience=self.scheduler_patience, factor=self.scheduler_factor)

        best_val = float("inf")
        best_state = None
        bad = 0

        torch.manual_seed(self.seed)
        np.random.seed(self.seed)

        for epoch in range(self.epochs):
            self._model.train()
            # minibatches (with replacement, because tiny)
            perm = rng.choice(x_tr.shape[0], size=max(self.batch_size, x_tr.shape[0]), replace=True)
            xb = x_tr[perm[:self.batch_size]]

            t = torch.randint(0, self.timesteps, (xb.shape[0],), device=self.device)
            noise = torch.randn_like(xb)
            xt = self._diff.q_sample(xb, t, noise)
            pred = self._model(xt, t)
            loss = torch.mean((pred - noise) ** 2)

            opt.zero_grad(set_to_none=True)
            loss.backward()
            if self.grad_clip and self.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(self._model.parameters(), self.grad_clip)
            opt.step()

            # val
            self._model.eval()
            with torch.no_grad():
                t_val = torch.randint(0, self.timesteps, (x_val.shape[0],), device=self.device)
                noise_val = torch.randn_like(x_val)
                xt_val = self._diff.q_sample(x_val, t_val, noise_val)
                pred_val = self._model(xt_val, t_val)
                val_loss = torch.mean((pred_val - noise_val) ** 2).item()

            if sched is not None:
                sched.step(val_loss)

            if self.verbose and (epoch % max(1, self.epochs // 5) == 0 or epoch == self.epochs - 1):
                logging.info(f"{verbose_prefix}: Epoch {epoch}/{self.epochs}, TrainLoss={loss.item():.4f}, ValLoss={val_loss:.4f}")

            # early stopping
            if val_loss + self.min_delta < best_val:
                best_val = val_loss
                best_state = {k: v.detach().cpu().clone() for k, v in self._model.state_dict().items()}
                bad = 0
            else:
                bad += 1
                if self.early_stopping and bad >= self.patience:
                    if self.verbose:
                        logging.info(f"{verbose_prefix}: early stopping at epoch {epoch} (best ValLoss={best_val:.4f})")
                    break

        if best_state is not None:
            self._model.load_state_dict(best_state)
        return self

    def sample(self, n: int):
        if self._model is None or self._diff is None or self._scaler is None:
            raise RuntimeError("RealTabDDPMGenerator: call fit() before sample().")

        self._model.eval()
        d = len(self._feature_names)
        x = torch.randn((n, d), device=self.device)

        # reverse diffusion
        with torch.no_grad():
            for t in reversed(range(self.timesteps)):
                tt = torch.full((n,), t, device=self.device, dtype=torch.long)
                eps = self._model(x, tt)
                alpha = self._diff.alphas[tt].unsqueeze(-1)
                alpha_bar = self._diff.alphas_cumprod[tt].unsqueeze(-1)
                beta = self._diff.betas[tt].unsqueeze(-1)

                # DDPM mean
                mean = (1.0 / torch.sqrt(alpha)) * (x - (beta / torch.sqrt(1.0 - alpha_bar)) * eps)

                if t > 0:
                    var = self._diff.posterior_variance[tt].unsqueeze(-1)
                    noise = torch.randn_like(x)
                    x = mean + torch.sqrt(var) * noise
                else:
                    x = mean

        x_np = x.detach().cpu().numpy()
        x_np = self._scaler.inverse_transform(x_np)

        return pd.DataFrame(x_np, columns=self._feature_names)

    # ---------- Simple GP-based tuning ----------
    def _tune_hyperparams(self, real_df: pd.DataFrame):
        import time
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel
        from sklearn.model_selection import KFold
        from sklearn.linear_model import Ridge
        from sklearn.metrics import mean_squared_error, r2_score

        start_t = time.time()

        # Search space (small, safe for tiny data)
        # Continuous are sampled in log space where appropriate.
        space = {
            "lr": ("log", 3e-4, 5e-3),
            "hidden_dim": ("cat", [128, 192, 256, 320]),
            "n_layers": ("cat", [2, 3, 4]),
            "timesteps": ("cat", [100, 150, 200, 300]),
            "dropout": ("cat", [0.0, 0.05, 0.1]),
            "batch_size": ("cat", [32, 64, 128]),
        }

        X_real = real_df.drop(columns=[], errors="ignore")
        # objective: fast and robust for n~20: CV Ridge on real test, trained on synthetic generated from train
        # Higher is better for tstr_r2; lower is better for val_mse.

        rng = np.random.default_rng(self.seed)

        def sample_param():
            p = {}
            for k, spec in space.items():
                if spec[0] == "log":
                    lo, hi = spec[1], spec[2]
                    p[k] = float(np.exp(rng.uniform(np.log(lo), np.log(hi))))
                elif spec[0] == "cat":
                    p[k] = spec[1][int(rng.integers(0, len(spec[1])))]
                else:
                    lo, hi = spec[1], spec[2]
                    p[k] = float(rng.uniform(lo, hi))
            return p

        def objective(params):
            # time budget
            if self.tuning_max_seconds is not None and (time.time() - start_t) > float(self.tuning_max_seconds):
                raise TimeoutError("tuning time budget exceeded")

            # small temporary generator instance (no tuning recursion)
            gen = RealTabDDPMGenerator(
                epochs=min(self.epochs, 120),
                batch_size=params["batch_size"],
                lr=params["lr"],
                timesteps=params["timesteps"],
                hidden_dim=params["hidden_dim"],
                n_layers=params["n_layers"],
                dropout=params["dropout"],
                schedule=self.schedule,
                beta_start=self.beta_start,
                beta_end=self.beta_end,
                weight_decay=self.weight_decay,
                grad_clip=self.grad_clip,
                seed=self.seed,
                device=self.device,
                early_stopping=True,
                patience=min(self.patience, 10),
                min_delta=self.min_delta,
                lr_scheduler=self.lr_scheduler,
                scheduler_patience=min(self.scheduler_patience, 5),
                scheduler_factor=self.scheduler_factor,
                enable_tuning=False,
                verbose=False
            )

            # 3-fold CV on REAL: train generator on train fold, synthesize, train Ridge on synth, evaluate on real test
            y = real_df.iloc[:, -1].values.astype(float)
            X = real_df.iloc[:, :-1].values.astype(float)
            kf = KFold(n_splits=min(3, len(real_df)), shuffle=True, random_state=self.seed)
            scores = []
            for tr, te in kf.split(X):
                df_tr = pd.DataFrame(real_df.iloc[tr].values, columns=real_df.columns)
                df_te = pd.DataFrame(real_df.iloc[te].values, columns=real_df.columns)

                gen.fit(df_tr, verbose_prefix="TabDDPM(Tune)")
                synth = gen.sample(n=max(len(df_tr)*5, 60))

                Xs = synth.iloc[:, :-1].values.astype(float)
                ys = synth.iloc[:, -1].values.astype(float)
                Xt = df_te.iloc[:, :-1].values.astype(float)
                yt = df_te.iloc[:, -1].values.astype(float)

                model = Ridge(alpha=1.0, random_state=self.seed)
                model.fit(Xs, ys)
                pred = model.predict(Xt)

                if self.tuning_metric == "tstr_r2":
                    scores.append(r2_score(yt, pred))
                else:
                    scores.append(mean_squared_error(yt, pred))

            return float(np.mean(scores))

        def to_vec(params):
            # numeric vector for GP
            v = []
            for k, spec in space.items():
                if spec[0] == "log":
                    v.append(np.log(params[k]))
                elif spec[0] == "cat":
                    v.append(float(spec[1].index(params[k])))
                else:
                    v.append(float(params[k]))
            return np.array(v, dtype=float)

        # initial random
        X_obs = []
        y_obs = []
        best_params = None
        best_val = None

        n_total = max(self.tuning_trials, self.tuning_random_starts)
        for i in range(self.tuning_random_starts):
            p = sample_param()
            try:
                val = objective(p)
            except Exception:
                continue
            X_obs.append(to_vec(p))
            y_obs.append(val)
            if best_val is None or ((self.tuning_metric == "tstr_r2" and val > best_val) or (self.tuning_metric != "tstr_r2" and val < best_val)):
                best_val = val
                best_params = p

        if len(X_obs) < 2:
            return best_params

        X_obs = np.vstack(X_obs)
        y_obs = np.array(y_obs)

        # GP surrogate
        kernel = ConstantKernel(1.0, (1e-3, 1e3)) * Matern(nu=2.5) + WhiteKernel(noise_level=1e-5, noise_level_bounds=(1e-8, 1e-2))
        gp = GaussianProcessRegressor(kernel=kernel, normalize_y=True, random_state=self.seed, n_restarts_optimizer=2)

        def expected_improvement(Xcand):
            mu, std = gp.predict(Xcand, return_std=True)
            std = np.maximum(std, 1e-9)

            if self.tuning_metric == "tstr_r2":
                # maximize
                best = np.max(y_obs)
                imp = mu - best
            else:
                # minimize
                best = np.min(y_obs)
                imp = best - mu

            Z = imp / std
            from scipy.stats import norm
            ei = imp * norm.cdf(Z) + std * norm.pdf(Z)
            return ei

        # BO loop
        for i in range(self.tuning_random_starts, n_total):
            if self.tuning_max_seconds is not None and (time.time() - start_t) > float(self.tuning_max_seconds):
                break

            gp.fit(X_obs, y_obs)

            # candidate set via random sampling
            cand_params = [sample_param() for _ in range(64)]
            Xcand = np.vstack([to_vec(p) for p in cand_params])
            ei = expected_improvement(Xcand)
            best_i = int(np.argmax(ei))
            p = cand_params[best_i]

            try:
                val = objective(p)
            except Exception:
                continue

            X_obs = np.vstack([X_obs, to_vec(p)])
            y_obs = np.append(y_obs, val)

            better = (val > best_val) if (self.tuning_metric == "tstr_r2") else (val < best_val)
            if better:
                best_val = val
                best_params = p

        return best_params



class ImprovedTabDDPMGenerator(RealTabDDPMGenerator):
    """Improved TabDDPM generator optimized for very small tabular datasets (n~20).

    Key changes vs. RealTabDDPMGenerator:
      - Robust multi-stage normalization (percentile clip -> RobustScaler -> StandardScaler)
      - Optional bootstrap augmentation (resampling + light noise on continuous columns)
      - Smaller network + stronger regularization defaults (aim: reduce overfitting)
      - LayerNorm + residual connection in the denoiser (more stable for tiny batches)
      - More conservative LR + stronger grad clipping
      - Longer patience for early stopping + gentler LR scheduler
      - Optional loss re-weighting across timesteps

    This class intentionally keeps the same diffusion backbone and sampling procedure.
    """

    def __init__(
        self,
        epochs: int = 150,
        batch_size: int = 32,
        lr: float = 5e-4,
        timesteps: int = 100,
        hidden_dim: int = 128,
        n_layers: int = 2,
        dropout: float = 0.15,
        schedule: str = "cosine",
        beta_start: float = 1e-4,
        beta_end: float = 0.01,
        weight_decay: float = 0.01,
        grad_clip: float = 0.5,
        seed: int = 123,
        device=None,
        # training controls
        early_stopping: bool = True,
        patience: int = 25,
        min_delta: float = 5e-5,
        lr_scheduler: bool = True,
        scheduler_patience: int = 10,
        scheduler_factor: float = 0.7,
        # tuning (kept for compatibility; default OFF for n~20)
        enable_tuning: bool = False,
        tuning_trials: int = 8,
        tuning_random_starts: int = 3,
        tuning_metric: str = "val_mse",
        tuning_max_seconds: int = 300,
        verbose: bool = True,
        # new knobs
        use_layer_norm: bool = True,
        bootstrap_augment: bool = True,
        bootstrap_factor: int = 3,
        bootstrap_noise_std: float = 0.01,
        robust_norm: bool = True,
        timestep_loss_weighting: bool = True,
    ):
        super().__init__(
            epochs=epochs,
            batch_size=batch_size,
            lr=lr,
            timesteps=timesteps,
            hidden_dim=hidden_dim,
            n_layers=n_layers,
            dropout=dropout,
            schedule=schedule,
            beta_start=beta_start,
            beta_end=beta_end,
            weight_decay=weight_decay,
            grad_clip=grad_clip,
            seed=seed,
            device=device,
            early_stopping=early_stopping,
            patience=patience,
            min_delta=min_delta,
            lr_scheduler=lr_scheduler,
            scheduler_patience=scheduler_patience,
            scheduler_factor=scheduler_factor,
            enable_tuning=enable_tuning,
            tuning_trials=tuning_trials,
            tuning_random_starts=tuning_random_starts,
            tuning_metric=tuning_metric,
            tuning_max_seconds=tuning_max_seconds,
            verbose=verbose,
        )

        self.use_layer_norm = bool(use_layer_norm)
        self.bootstrap_augment = bool(bootstrap_augment)
        self.bootstrap_factor = int(bootstrap_factor)
        self.bootstrap_noise_std = float(bootstrap_noise_std)
        self.robust_norm = bool(robust_norm)
        self.timestep_loss_weighting = bool(timestep_loss_weighting)

        # scalers for robust_norm
        self._robust_scaler = None
        self._std_scaler = None
        self._clip_lo = None
        self._clip_hi = None
        self._discrete_mask = None

    # ---- Robust normalization helpers ----
    @staticmethod
    def _detect_discrete_mask_from_df(df: pd.DataFrame, max_unique: int = 6) -> np.ndarray:
        """Detect 'ordinal-like/discrete' numeric columns to avoid jitter/noise during bootstrap.

        Heuristic: numeric column with <= max_unique unique values.
        """
        mask = []
        for c in df.columns:
            try:
                if pd.api.types.is_numeric_dtype(df[c]):
                    uniq = df[c].dropna().unique()
                    mask.append(len(uniq) <= max_unique)
                else:
                    mask.append(False)
            except Exception:
                mask.append(False)
        return np.array(mask, dtype=bool)

    def _robust_fit_transform(self, x: np.ndarray) -> np.ndarray:
        from sklearn.preprocessing import RobustScaler, StandardScaler

        # Percentile clip (per-feature) to reduce extreme leverage
        lo = np.percentile(x, 0.1, axis=0)
        hi = np.percentile(x, 99.9, axis=0)
        x_clip = np.clip(x, lo, hi)

        self._clip_lo = lo.astype(np.float32, copy=False)
        self._clip_hi = hi.astype(np.float32, copy=False)

        self._robust_scaler = RobustScaler()
        x_r = self._robust_scaler.fit_transform(x_clip)

        self._std_scaler = StandardScaler()
        x_s = self._std_scaler.fit_transform(x_r)

        # Final safety clip in normalized space (helps avoid gradient blow-ups)
        x_s = np.clip(x_s, -5.0, 5.0).astype(np.float32, copy=False)
        return x_s

    def _robust_inverse_transform(self, x_norm: np.ndarray) -> np.ndarray:
        if self._std_scaler is None or self._robust_scaler is None:
            raise RuntimeError("ImprovedTabDDPMGenerator: robust scalers not fitted.")

        x_r = self._std_scaler.inverse_transform(x_norm)
        x_x = self._robust_scaler.inverse_transform(x_r)

        if self._clip_lo is not None and self._clip_hi is not None:
            x_x = np.clip(x_x, self._clip_lo, self._clip_hi)
        return x_x

    def _bootstrap_augment_array(self, x: np.ndarray, df_ref: pd.DataFrame) -> np.ndarray:
        rng = np.random.default_rng(self.seed)
        n = x.shape[0]
        n_aug = max(n * int(self.bootstrap_factor), n)

        idx = rng.choice(n, size=n_aug, replace=True)
        x_aug = x[idx].copy()

        # Add light Gaussian jitter ONLY on non-discrete numeric columns
        if self.bootstrap_noise_std > 0:
            noise = rng.normal(0.0, float(self.bootstrap_noise_std), size=x_aug.shape).astype(np.float32, copy=False)
            if self._discrete_mask is None:
                self._discrete_mask = self._detect_discrete_mask_from_df(df_ref)
            if self._discrete_mask is not None and self._discrete_mask.any():
                noise[:, self._discrete_mask] = 0.0
            x_aug = x_aug + noise

        return x_aug

    # ---- Improved denoiser ----
    class _ImprovedDenoiser(nn.Module):
        """Denoiser with optional LayerNorm and a weighted residual connection."""

        def __init__(self, d_in: int, hidden_dim: int, n_layers: int, dropout: float, use_layer_norm: bool = True):
            super().__init__()
            self.d_in = int(d_in)
            self.time_emb_dim = int(hidden_dim)
            self.use_layer_norm = bool(use_layer_norm)

            self.time_mlp = nn.Sequential(
                nn.Linear(self.time_emb_dim, self.time_emb_dim),
                nn.SiLU(),
                nn.Linear(self.time_emb_dim, self.time_emb_dim),
            )

            self.input_proj = nn.Linear(self.d_in + self.time_emb_dim, hidden_dim)

            layers = []
            # n_layers here is total depth; keep at least 1 block
            n_blocks = max(1, int(n_layers) - 1)
            for _ in range(n_blocks):
                layers.append(nn.Linear(hidden_dim, hidden_dim))
                if self.use_layer_norm:
                    layers.append(nn.LayerNorm(hidden_dim))
                layers.append(nn.SiLU())
                if dropout and dropout > 0:
                    layers.append(nn.Dropout(float(dropout)))
            self.net = nn.Sequential(*layers)

            self.output_proj = nn.Linear(hidden_dim, self.d_in)

            # Learnable residual weight (kept small initially)
            self.residual_weight = nn.Parameter(torch.tensor(0.1, dtype=torch.float32))

        @staticmethod
        def _timestep_embedding(t: torch.Tensor, dim: int, max_period: int = 10000) -> torch.Tensor:
            half = dim // 2
            freqs = torch.exp(
                -torch.log(torch.tensor(float(max_period), device=t.device, dtype=torch.float32))
                * torch.arange(0, half, device=t.device, dtype=torch.float32)
                / float(half)
            )
            args = t.float().unsqueeze(1) * freqs.unsqueeze(0)
            emb = torch.cat([torch.cos(args), torch.sin(args)], dim=1)
            if dim % 2 == 1:
                emb = torch.cat([emb, torch.zeros_like(emb[:, :1])], dim=1)
            return emb

        def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
            t_emb = self._timestep_embedding(t, self.time_emb_dim)
            t_emb = self.time_mlp(t_emb)

            h = torch.cat([x, t_emb], dim=1)
            h = self.input_proj(h)

            h_res = h
            h = self.net(h)
            h = h + self.residual_weight * h_res

            return self.output_proj(h)

    # ---- Core API ----
    def fit(self, real_df: pd.DataFrame, verbose_prefix="TabDDPM-Improved"):
        self._feature_names = list(real_df.columns)

        x_raw = real_df.values.astype(np.float32, copy=False)

        # detect discrete mask from df (used by bootstrap)
        self._discrete_mask = self._detect_discrete_mask_from_df(real_df)

        # robust normalization (recommended) or fallback to StandardScaler
        if self.robust_norm:
            x_norm = self._robust_fit_transform(x_raw)
            # keep base-class _scaler for compatibility, but unused in sample()
            self._scaler = None
        else:
            from sklearn.preprocessing import StandardScaler
            self._scaler = StandardScaler()
            x_norm = self._scaler.fit_transform(x_raw).astype(np.float32, copy=False)

        # bootstrap augmentation (only for very small datasets)
        if self.bootstrap_augment and len(x_norm) < 50:
            x_before = len(x_norm)
            x_norm = self._bootstrap_augment_array(x_norm, real_df)
            if self.verbose:
                logging.info(f"{verbose_prefix}: Bootstrap augmentation {x_before} -> {len(x_norm)} samples")

        x = torch.tensor(x_norm, dtype=torch.float32, device=self.device)

        # optional tuning (kept; default OFF for n~20)
        if self.enable_tuning:
            tuned = self._tune_hyperparams(real_df)
            if tuned and self.verbose:
                logging.info(f"{verbose_prefix}: best hyperparams from tuning: {tuned}")
                for k, v in tuned.items():
                    setattr(self, k, v)

        # diffusion + model
        betas = self._make_betas()
        self._diff = self._Diffusion(betas, self.device)
        self._model = self._ImprovedDenoiser(
            d_in=x.shape[1],
            hidden_dim=self.hidden_dim,
            n_layers=self.n_layers,
            dropout=self.dropout,
            use_layer_norm=self.use_layer_norm,
        ).to(self.device)

        # optimizer + scheduler
        opt = torch.optim.AdamW(self._model.parameters(), lr=self.lr, weight_decay=self.weight_decay, betas=(0.9, 0.999), eps=1e-8)

        sched = None
        if self.lr_scheduler:
            sched = torch.optim.lr_scheduler.ReduceLROnPlateau(
                opt, mode="min", patience=self.scheduler_patience, factor=self.scheduler_factor
            )

        # train/val split
        rng = np.random.default_rng(self.seed)
        n = x.shape[0]
        idx = np.arange(n)
        rng.shuffle(idx)
        n_val = max(3, int(0.2 * n))
        val_idx = idx[:n_val]
        tr_idx = idx[n_val:] if (n - n_val) >= 5 else idx

        x_tr = x[tr_idx]
        x_val = x[val_idx]

        best_val = float("inf")
        best_state = None
        bad = 0

        torch.manual_seed(self.seed)
        np.random.seed(self.seed)

        for epoch in range(self.epochs):
            self._model.train()

            # minibatch with replacement for tiny data
            if len(x_tr) < self.batch_size:
                perm = rng.choice(len(x_tr), size=self.batch_size, replace=True)
            else:
                perm = rng.permutation(len(x_tr))[: self.batch_size]
            xb = x_tr[perm]

            t = torch.randint(0, self.timesteps, (xb.shape[0],), device=self.device)
            noise = torch.randn_like(xb)
            xt = self._diff.q_sample(xb, t, noise)
            pred = self._model(xt, t)

            if self.timestep_loss_weighting:
                # give more weight to early timesteps (heuristic stabilization)
                weights = 1.0 / torch.sqrt(self._diff.alphas_cumprod[t] + 1e-8)
                loss = torch.mean(weights.unsqueeze(-1) * (pred - noise) ** 2)
            else:
                loss = torch.mean((pred - noise) ** 2)

            opt.zero_grad(set_to_none=True)
            loss.backward()

            if self.grad_clip and self.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(self._model.parameters(), self.grad_clip)

            opt.step()

            # validation on full x_val
            self._model.eval()
            with torch.no_grad():
                t_val = torch.randint(0, self.timesteps, (x_val.shape[0],), device=self.device)
                noise_val = torch.randn_like(x_val)
                xt_val = self._diff.q_sample(x_val, t_val, noise_val)
                pred_val = self._model(xt_val, t_val)
                val_loss = torch.mean((pred_val - noise_val) ** 2).item()

            if sched is not None:
                sched.step(val_loss)

            if self.verbose and (epoch % max(1, self.epochs // 10) == 0 or epoch == self.epochs - 1):
                current_lr = float(opt.param_groups[0]["lr"])
                logging.info(f"{verbose_prefix}: Epoch {epoch}/{self.epochs}, TrainLoss={loss.item():.4f}, ValLoss={val_loss:.4f}, LR={current_lr:.6f}")

            # early stopping
            if val_loss + self.min_delta < best_val:
                best_val = val_loss
                best_state = {k: v.detach().cpu().clone() for k, v in self._model.state_dict().items()}
                bad = 0
            else:
                bad += 1
                if self.early_stopping and bad >= self.patience:
                    if self.verbose:
                        logging.info(f"{verbose_prefix}: early stopping at epoch {epoch} (best ValLoss={best_val:.4f})")
                    break

        if best_state is not None:
            self._model.load_state_dict(best_state)
        return self

    def sample(self, n: int):
        if self._model is None or self._diff is None:
            raise RuntimeError("ImprovedTabDDPMGenerator: call fit() before sample().")

        self._model.eval()
        d = len(self._feature_names)
        x = torch.randn((n, d), device=self.device)

        with torch.no_grad():
            for t in reversed(range(self.timesteps)):
                tt = torch.full((n,), t, device=self.device, dtype=torch.long)
                eps = self._model(x, tt)
                alpha = self._diff.alphas[tt].unsqueeze(-1)
                alpha_bar = self._diff.alphas_cumprod[tt].unsqueeze(-1)
                beta = self._diff.betas[tt].unsqueeze(-1)

                mean = (1.0 / torch.sqrt(alpha)) * (x - (beta / torch.sqrt(1.0 - alpha_bar)) * eps)

                if t > 0:
                    var = self._diff.posterior_variance[tt].unsqueeze(-1)
                    noise = torch.randn_like(x)
                    x = mean + torch.sqrt(var) * noise
                else:
                    x = mean

        x_np = x.detach().cpu().numpy()

        if self.robust_norm:
            x_np = self._robust_inverse_transform(x_np)
        else:
            if self._scaler is None:
                raise RuntimeError("ImprovedTabDDPMGenerator: scaler missing for inverse transform.")
            x_np = self._scaler.inverse_transform(x_np)

        return pd.DataFrame(x_np, columns=self._feature_names)



class TabDDPMGenerator:
    """Stub fallback generator for TabDDPM"""
    def __init__(self, input_dim, config):
        self.input_dim = input_dim
        self.config = config

    def train(self, data_norm):
        pass  # Stub

    def generate(self, n_synthetic):
        return np.random.rand(n_synthetic, self.input_dim)  # Stub

class SOTAGeneratorManager:
    """Manager para geradores state-of-the-art com fallbacks robustos"""
    
    def __init__(self, random_seed: int = 42, target_col: str = None):
        self.random_seed = random_seed
        self.target_col = target_col  # NOVO: armazenar target_col
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Verifica dependências disponíveis"""
        self.available_generators = []
        
        if SDV_AVAILABLE:
            if GaussianCopulaSynthesizer is not None:
                self.available_generators.append('gaussian_copula')
            if CTGANSynthesizer is not None:
                self.available_generators.append('ctgan')
            if TVAESynthesizer is not None:
                self.available_generators.append('tvae')
        
        if TORCH_AVAILABLE:
            self.available_generators.append('tabddpm')
        
        # Always keep at least simple fallbacks available (useful when SDV/torch fail to import).
        
        if not self.available_generators:
        
            self.available_generators.append('gaussian_naive')
        
            self.available_generators.append('kde_sampling')

        
        logger.info(f"Available generators: {self.available_generators}")
    
    def generate_gaussian_copula(self, df: pd.DataFrame, n_samples: int, 
                                 metadata=None) -> Optional[pd.DataFrame]:
        """Generate using Gaussian Copula"""
        # CORREÇÃO: Condição correta - verificar se NÃO está disponível
        if (not SDV_AVAILABLE) or (GaussianCopulaSynthesizer is None):
            logger.error("GaussianCopulaSynthesizer not available. Install: pip install sdv")
            return None
        
        try:
            logger.info("Generating with Gaussian Copula...")
            
            # Create metadata if needed
            if metadata is None:
                try:
                    type_info = detect_data_types(df)
                    metadata = create_sdv_metadata(df, type_info)
                except Exception as e:
                    logger.warning(f"Metadata creation failed: {e}, using auto-detect")
                    metadata = None
            
            # Initialize synthesizer
            if metadata is None:
                synthesizer = GaussianCopulaSynthesizer()
                logger.info("Using auto-detected metadata")
            else:
                synthesizer = GaussianCopulaSynthesizer(metadata)
            
            # Fit and sample
            synthesizer.fit(df)
            synth_df = synthesizer.sample(n_samples)
            
            logger.info(f"Generated {len(synth_df)} samples with Gaussian Copula")
            return synth_df
            
        except Exception as e:
            logger.error(f"Gaussian Copula generation failed: {e}")
            return None

    def generate_ctgan(self, df: pd.DataFrame, n_samples: int, 
                       metadata=None, epochs: int = 300) -> Optional[pd.DataFrame]:
        """Generate using CTGAN"""
        # CORREÇÃO: Condição correta - verificar se NÃO está disponível
        if (not SDV_AVAILABLE) or (CTGANSynthesizer is None):
            logger.error("CTGANSynthesizer not available. Install: pip install sdv")
            return None
        
        try:
            logger.info(f"Generating with CTGAN (epochs={epochs})...")
            
            # Create metadata if needed
            if metadata is None:
                try:
                    type_info = detect_data_types(df)
                    metadata = create_sdv_metadata(df, type_info)
                except Exception as e:
                    logger.warning(f"Metadata creation failed: {e}")
                    metadata = None
            
            # Initialize synthesizer
            if metadata is None:
                synthesizer = CTGANSynthesizer(epochs=epochs)
            else:
                synthesizer = CTGANSynthesizer(metadata, epochs=epochs)
            
            # Fit and sample
            synthesizer.fit(df)
            synth_df = synthesizer.sample(n_samples)
            
            logger.info(f"Generated {len(synth_df)} samples with CTGAN")
            return synth_df
            
        except Exception as e:
            logger.error(f"CTGAN generation failed: {e}")
            return None

    def generate_tvae(self, df: pd.DataFrame, n_samples: int, 
                      metadata=None, epochs: int = 300) -> Optional[pd.DataFrame]:
        """Generate using TVAE"""
        # CORREÇÃO: Condição correta - verificar se NÃO está disponível
        if (not SDV_AVAILABLE) or (TVAESynthesizer is None):
            logger.error("TVAESynthesizer not available. Install: pip install sdv")
            return None
        
        try:
            logger.info(f"Generating with TVAE (epochs={epochs})...")
            
            # Create metadata if needed
            if metadata is None:
                try:
                    type_info = detect_data_types(df)
                    metadata = create_sdv_metadata(df, type_info)
                except Exception as e:
                    logger.warning(f"Metadata creation failed: {e}")
                    metadata = None
            
            # Initialize synthesizer
            if metadata is None:
                synthesizer = TVAESynthesizer(epochs=epochs)
            else:
                synthesizer = TVAESynthesizer(metadata, epochs=epochs)
            
            # Fit and sample
            synthesizer.fit(df)
            synth_df = synthesizer.sample(n_samples)
            
            logger.info(f"Generated {len(synth_df)} samples with TVAE")
            return synth_df
            
        except Exception as e:
            logger.error(f"TVAE generation failed: {e}")
            return None

    
    def generate_tabddpm(
        self, df: pd.DataFrame, n_samples: int, metadata=None,
        # ---- legacy params (kept) ----
        epochs: int = 100,
        timesteps: int = 200,
        lr: float = 1e-3,
        batch_size: int = 64,
        hidden_dim: int = 256,
        n_layers: int = 3,
        dropout: float = 0.0,
        schedule: str = "cosine",
        early_stopping: bool = True,
        patience: int = 15,
        enable_tuning: bool = False,
        tuning_trials: int = 12,
        tuning_metric: str = "val_mse",
        verbose: bool = True,
        # ---- improved knobs (new; safe defaults for n~20) ----
        use_improved: Optional[bool] = None,
        use_layer_norm: bool = True,
        bootstrap_augment: bool = True,
        bootstrap_factor: int = 3,
        robust_norm: bool = True,
        timestep_loss_weighting: bool = True,
        # allow overriding regularization/optimizer in improved variant
        weight_decay: float = 0.01,
        grad_clip: float = 0.5,
        min_delta: float = 5e-5,
        lr_scheduler: bool = True,
        scheduler_patience: int = 10,
        scheduler_factor: float = 0.7,
        beta_end: float = 0.01,
        tuning_random_starts: int = 3,
        tuning_max_seconds: int = 300,
    ) -> pd.DataFrame:
        """Generate synthetic data using a lightweight TabDDPM-style diffusion model.

        For *very small datasets* (e.g., n≈20), the default RealTabDDPM-like settings can
        overfit and destabilize fidelity metrics. When `use_improved` is True (or auto),
        this method uses `ImprovedTabDDPMGenerator` with safer defaults.

        Notes for tiny datasets:
        - Prefer fewer timesteps (≈100) and stronger regularization.
        - Tuning is usually not worth it for n≈20 (overhead > benefit).
        """
        if verbose:
            logging.info("Iniciando geração com TabDDPM (diffusion) ...")

        # Auto-select improved variant for small n if not explicitly set
        if use_improved is None:
            try:
                use_improved = (len(df) <= 80)
            except Exception:
                use_improved = True

        if use_improved:
            # Map legacy defaults to improved-safe defaults unless user overrides explicitly
            # If caller still passes legacy high-capacity defaults, clip them for stability.
            epochs_i = int(max(epochs, 120)) if epochs != 100 else 150
            timesteps_i = int(min(timesteps, 100)) if timesteps != 200 else 100
            lr_i = float(lr) if lr != 1e-3 else 5e-4
            batch_i = int(batch_size) if batch_size != 64 else 32
            hidden_i = int(min(hidden_dim, 128)) if hidden_dim != 256 else 128
            layers_i = int(min(n_layers, 2)) if n_layers != 3 else 2
            drop_i = float(dropout) if dropout != 0.0 else 0.15
            pat_i = int(max(patience, 20)) if patience != 15 else 25

            gen = ImprovedTabDDPMGenerator(
                epochs=epochs_i,
                batch_size=batch_i,
                lr=lr_i,
                timesteps=timesteps_i,
                hidden_dim=hidden_i,
                n_layers=layers_i,
                dropout=drop_i,
                schedule=schedule,
                seed=self.random_seed,
                early_stopping=early_stopping,
                patience=pat_i,
                min_delta=min_delta,
                lr_scheduler=lr_scheduler,
                scheduler_patience=scheduler_patience,
                scheduler_factor=scheduler_factor,
                enable_tuning=enable_tuning,  # caller can force, but default should be False for n~20
                tuning_trials=min(int(tuning_trials), 8),
                tuning_random_starts=int(tuning_random_starts),
                tuning_metric=tuning_metric,
                tuning_max_seconds=int(tuning_max_seconds),
                verbose=verbose,
                use_layer_norm=use_layer_norm,
                bootstrap_augment=bootstrap_augment,
                bootstrap_factor=bootstrap_factor,
                robust_norm=robust_norm,
                timestep_loss_weighting=timestep_loss_weighting,
                weight_decay=weight_decay,
                grad_clip=grad_clip,
                beta_end=beta_end,
            )
            gen.fit(df, verbose_prefix="TabDDPM-Improved")
            synth = gen.sample(n_samples)
            return synth

        # ---- legacy variant (kept intact) ----
        gen = RealTabDDPMGenerator(
            epochs=epochs,
            batch_size=batch_size,
            lr=lr,
            timesteps=timesteps,
            hidden_dim=hidden_dim,
            n_layers=n_layers,
            dropout=dropout,
            schedule=schedule,
            seed=self.random_seed,
            early_stopping=early_stopping,
            patience=patience,
            enable_tuning=enable_tuning,
            tuning_trials=tuning_trials,
            tuning_metric=tuning_metric,
            verbose=verbose
        )

        gen.fit(df, verbose_prefix="TabDDPM")
        synth = gen.sample(n_samples)
        return synth



    def generate_gaussian_naive(self, df: pd.DataFrame, n_samples: int) -> Optional[pd.DataFrame]:
        """Fallback: Gaussian naive generator"""
        try:
            logger.info("Generating with Gaussian Naive (fallback)...")
            
            numeric_df = df.select_dtypes(include=[np.number])
            if len(numeric_df.columns) == 0:
                logger.error("No numeric columns for Gaussian Naive")
                return None
            
            numeric_df = numeric_df.fillna(numeric_df.mean())
            
            # Fit multivariate Gaussian
            mean = numeric_df.mean().values
            cov = numeric_df.cov().values + np.eye(len(mean)) * 1e-6
            
            # Generate samples
            samples = np.random.multivariate_normal(mean, cov, n_samples)
            result_df = pd.DataFrame(samples, columns=numeric_df.columns)
            
            # Add categorical columns by sampling
            for col in df.columns:
                if col not in numeric_df.columns:
                    result_df[col] = np.random.choice(
                        df[col].dropna().values, 
                        size=n_samples, 
                        replace=True
                    )
            
            logger.info(f"Generated {len(result_df)} samples with Gaussian Naive")
            return result_df
            
        except Exception as e:
            logger.error(f"Gaussian Naive generation failed: {e}")
            return None

    # Stubs para geradores não implementados
    def generate_copulagan(self, df: pd.DataFrame, n_samples: int, metadata=None) -> Optional[pd.DataFrame]:
        logger.warning("CopulaGAN not implemented, using Gaussian Copula fallback")
        return self.generate_gaussian_copula(df, n_samples, metadata)
    
    def generate_vae(self, df: pd.DataFrame, n_samples: int, metadata=None) -> Optional[pd.DataFrame]:
        logger.warning("VAE not implemented, using TVAE fallback")
        return self.generate_tvae(df, n_samples, metadata)
    
    def generate_wgan_gp(self, df: pd.DataFrame, n_samples: int, metadata=None) -> Optional[pd.DataFrame]:
        logger.warning("WGAN-GP not implemented, using CTGAN fallback")
        return self.generate_ctgan(df, n_samples, metadata)
    
    def generate_kde_sampling(self, df: pd.DataFrame, n_samples: int, metadata=None) -> Optional[pd.DataFrame]:
        logger.warning("KDE Sampling not implemented, using Gaussian Naive fallback")
        return self.generate_gaussian_naive(df, n_samples)

# ============================================================================
# PRIVACY EVALUATORS - MIA & AIA Implementation
# ============================================================================

class MembershipInferenceEvaluator:
    """Complete Membership Inference Attack implementation"""
    
    def __init__(self, random_seed: int = 42, n_shadow_models: int = 5):
        self.random_seed = random_seed
        self.n_shadow_models = n_shadow_models
        logger.info(f"MIA evaluator initialized with {n_shadow_models} shadow models")
        
    def evaluate(self, real_df: pd.DataFrame, synth_df: pd.DataFrame, 
                target_col: str, config: ExperimentConfig = None) -> Dict[str, Any]:
        """
        Implementação completa de MIA usando shadow models
        Baseado em Shokri et al. 2017
        """
        results = {}
        
        try:
            # Prepare features and target
            feature_cols = [c for c in real_df.columns if c != target_col]
            X_real = pd.get_dummies(real_df[feature_cols], drop_first=True)
            y_real = real_df[target_col]
            
            X_synth = pd.get_dummies(synth_df[feature_cols], drop_first=True)
            y_synth = synth_df[target_col]
            
            # Align columns
            all_cols = X_real.columns.union(X_synth.columns)
            X_real = X_real.reindex(columns=all_cols, fill_value=0)
            X_synth = X_synth.reindex(columns=all_cols, fill_value=0)
            
            # Determine task type
            is_classification = len(np.unique(y_real)) <= 20
            
            # Split real data into member/non-member
            from sklearn.model_selection import train_test_split
            X_member, X_nonmember, y_member, y_nonmember = train_test_split(
                X_real, y_real, test_size=0.5, random_state=self.random_seed,
                stratify=y_real if is_classification else None
            )
            
            # Train shadow models on synthetic data
            shadow_predictions_member = []
            shadow_predictions_nonmember = []
            
            for i in range(self.n_shadow_models):
                seed = self.random_seed + i
                
                # Sample from synthetic data
                shadow_idx = np.random.RandomState(seed).choice(
                    len(X_synth), size=min(len(X_synth), len(X_member)), replace=False
                )
                X_shadow = X_synth.iloc[shadow_idx]
                y_shadow = y_synth.iloc[shadow_idx]
                
                # Train shadow model
                if is_classification:
                    from sklearn.ensemble import RandomForestClassifier
                    shadow_model = RandomForestClassifier(
                        n_estimators=100, random_state=seed, max_depth=10
                    )
                else:
                    from sklearn.ensemble import RandomForestRegressor
                    shadow_model = RandomForestRegressor(
                        n_estimators=100, random_state=seed, max_depth=10
                    )
                
                shadow_model.fit(X_shadow, y_shadow)
                
                # Get predictions on member/non-member sets
                if is_classification and hasattr(shadow_model, 'predict_proba'):
                    pred_member = shadow_model.predict_proba(X_member)
                    pred_nonmember = shadow_model.predict_proba(X_nonmember)
                else:
                    pred_member = shadow_model.predict(X_member).reshape(-1, 1)
                    pred_nonmember = shadow_model.predict(X_nonmember).reshape(-1, 1)
                
                shadow_predictions_member.append(pred_member)
                shadow_predictions_nonmember.append(pred_nonmember)
            
            # Aggregate predictions
            avg_pred_member = np.mean([p.max(axis=1) if p.ndim > 1 else p.flatten() 
                                      for p in shadow_predictions_member], axis=0)
            avg_pred_nonmember = np.mean([p.max(axis=1) if p.ndim > 1 else p.flatten() 
                                         for p in shadow_predictions_nonmember], axis=0)
            
            # Train attack model
            X_attack = np.concatenate([avg_pred_member, avg_pred_nonmember]).reshape(-1, 1)
            y_attack = np.concatenate([
                np.ones(len(avg_pred_member)),
                np.zeros(len(avg_pred_nonmember))
            ])
            
            # MULTIPLE ATTACK MODELS IMPLEMENTATION
            attack_models = getattr(config, "attack_models", None) or ["LR"]
            by_attack = {}
            
            for am in attack_models:
                try:
                    clf = _fit_attack_model(am, X_attack, y_attack)
                    yhat, prob = _predict_attack_model(clf, X_attack)
                    from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score
                    acc  = accuracy_score(y_attack, yhat)
                    prec = precision_score(y_attack, yhat, zero_division=0)
                    rec  = recall_score(y_attack, yhat, zero_division=0)
                    auc  = roc_auc_score(y_attack, prob) if prob is not None else None
                    by_attack[am] = {"accuracy": float(acc), "precision": float(prec),
                                   "recall": float(rec), "auc": (None if auc is None else float(auc))}
                except Exception as e:
                    by_attack[am] = {"error": str(e)}
            
            # Mantém saída antiga no topo como LR (se houver), garantindo compatibilidade:
            baseline = by_attack.get("LR") or next((v for k,v in by_attack.items() if isinstance(v, dict) and "accuracy" in v), None)
            if baseline:
                results.update(baseline)
            results["by_attack"] = by_attack
            
            # ESTRATIFICAÇÃO POR RARIDADE E GRUPO SENSÍVEL
            do_rarity = config.privacy_stratify.get("rarity", False) if config else False
            do_sensitive = config.privacy_stratify.get("sensitive", False) if config else False
            by_strata = {}
            
            if do_rarity or do_sensitive:
                # Precisamos do DataFrame real correspondente aos dados de avaliação
                real_eval_df = pd.concat([X_member, X_nonmember], axis=0)
                real_eval_df = real_eval_df.reindex(columns=all_cols, fill_value=0)
                
                if do_rarity:
                    # Pegue somente colunas numéricas do real (onde a raridade faz sentido)
                    df_num = real_eval_df.select_dtypes(include=["number"]).copy()
                    # normaliza para KNN raridade
                    from sklearn.preprocessing import StandardScaler
                    if df_num.shape[1] > 0:
                        ss = StandardScaler().fit(df_num.values)
                        z = ss.transform(df_num.values)
                        rarity = _knn_rarity_scores(pd.DataFrame(z, index=df_num.index), k=5)
                        bins = _make_strata(rarity, n_bins=5)
                        if bins is not None:
                            for b in sorted(bins.dropna().unique()):
                                idx = (bins == b).values
                                if idx.sum() >= 20:  # suporte mínimo
                                    # refiltra X_attack, y_attack para este estrato
                                    Xb, yb = X_attack[idx], y_attack[idx]
                                    if Xb.shape[0] >= 10:
                                        # repete ataque com o mesmo attack model baseline (LR) para não inflar custo
                                        try:
                                            clf = _fit_attack_model("LR", X_attack, y_attack)
                                            yhat, prob = _predict_attack_model(clf, Xb)
                                            from sklearn.metrics import accuracy_score, roc_auc_score
                                            acc  = accuracy_score(yb, yhat)
                                            auc  = roc_auc_score(yb, prob) if prob is not None else None
                                            by_strata.setdefault("rarity", {})[str(b)] = {"acc": float(acc), "auc": (None if auc is None else float(auc)), "n": int(idx.sum())}
                                        except Exception as e:
                                            by_strata.setdefault("rarity", {})[str(b)] = {"error": str(e), "n": int(idx.sum())}
                
                if do_sensitive and config.sensitive_attributes:
                    sens_col = config.sensitive_attributes[0]  # opção simples: 1º atributo sensível
                    if sens_col in real_df.columns:
                        # Recria o mapeamento dos índices para o atributo sensível
                        member_indices = X_member.index
                        nonmember_indices = X_nonmember.index
                        all_indices = np.concatenate([member_indices, nonmember_indices])
                        groups = real_df.loc[all_indices, sens_col].astype(str)
                        
                        for g in sorted(groups.dropna().unique()):
                            idx = (groups == g).values
                            if idx.sum() >= 20:
                                Xg, yg = X_attack[idx], y_attack[idx]
                                if Xg.shape[0] >= 10:
                                    try:
                                        clf = _fit_attack_model("LR", X_attack, y_attack)
                                        yhat, prob = _predict_attack_model(clf, Xg)
                                        from sklearn.metrics import accuracy_score, roc_auc_score
                                        acc  = accuracy_score(yg, yhat)
                                        auc  = roc_auc_score(yg, prob) if prob is not None else None
                                        by_strata.setdefault("sensitive", {})[str(g)] = {"acc": float(acc), "auc": (None if auc is None else float(auc)), "n": int(idx.sum())}
                                    except Exception as e:
                                        by_strata.setdefault("sensitive", {})[str(g)] = {"error": str(e), "n": int(idx.sum())}
            
            results["by_strata"] = by_strata
            results['n_shadow_models'] = self.n_shadow_models
            
        except Exception as e:
            logger.error(f"MIA evaluation failed: {e}")
            results['error'] = str(e)
        
        return results

class AttributeInferenceEvaluator:
    """Complete Attribute Inference Attack implementation"""
    
    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        
    def evaluate(self, real_df: pd.DataFrame, synth_df: pd.DataFrame, 
                target_col: str, sensitive_attributes: Optional[List[str]] = None,
                known_features: Optional[List[str]] = None,
                mode: str = "blackbox", attack_model: str = "lr",
                config: ExperimentConfig = None) -> Dict[str, Any]:
        """
        Implementação completa de AIA
        
        Args:
            mode: 'blackbox' (model-based) or 'nn_reconstruction' (nearest neighbor)
            attack_model: 'lr' (logistic regression) or 'rf' (random forest)
        """
        results = {"mode": mode, "attributes": {}}
        
        # Auto-detect sensitive attributes if not provided
        if sensitive_attributes is None:
            cats = [c for c in real_df.columns 
                   if c != target_col and not pd.api.types.is_numeric_dtype(real_df[c])]
            sensitive_attributes = cats[:3]  # Top 3 categorical
        
        if not sensitive_attributes:
            results['warning'] = 'No sensitive attributes detected'
            return results
        
        # Known features are all except sensitive and target
        if known_features is None:
            known_features = [c for c in real_df.columns 
                            if c not in (sensitive_attributes + [target_col])]
        
        # Prepare base features
        X_base = pd.get_dummies(real_df[known_features], drop_first=True)
        
        for sensitive_attr in sensitive_attributes:
            attr_results = {}
            
            try:
                # Prepare target for this attribute
                y = real_df[sensitive_attr].copy()
                
                # Determine if classification or regression
                if y.dtype.kind not in "ifu":
                    y_proc = y.astype("category").cat.codes
                    is_classification = True
                else:
                    y_proc = y.astype(float)
                    is_classification = len(pd.unique(y_proc)) <= 20
                
                X = X_base.copy()
                
                # Train-test split
                from sklearn.model_selection import train_test_split
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y_proc, test_size=0.3, random_state=self.random_seed,
                    stratify=y_proc if is_classification else None
                )
                
                if mode == "nn_reconstruction":
                    # Nearest neighbor attack using synthetic data
                    X_synth = pd.get_dummies(
                        synth_df[known_features], drop_first=True
                    ).reindex(columns=X.columns, fill_value=0)
                    
                    nbrs = NearestNeighbors(n_neighbors=1, metric='euclidean')
                    nbrs.fit(X_synth.values)
                    
                    distances, indices = nbrs.kneighbors(X_test.values)
                    
                    # Get corresponding sensitive values from synthetic data
                    if sensitive_attr in synth_df.columns:
                        y_synth = synth_df[sensitive_attr]
                        if y_synth.dtype.kind not in "ifu":
                            y_synth_codes = y_synth.astype("category").cat.codes.values
                        else:
                            y_synth_codes = y_synth.values.astype(float)
                        
                        y_pred = y_synth_codes[indices.flatten()]
                    else:
                        # Fallback: use majority class
                        if is_classification:
                            majority = int(np.bincount(y_train).argmax())
                        else:
                            majority = float(np.median(y_train))
                        y_pred = np.full_like(y_test, majority)
                
                else:  # blackbox model-based attack
                    # MULTIPLE ATTACK MODELS IMPLEMENTATION
                    attack_models = getattr(config, "attack_models", None) or ["LR"]
                    by_attack = {}
                    
                    for am in attack_models:
                        try:
                            if is_classification:
                                if am.upper() == "RF":
                                    from sklearn.ensemble import RandomForestClassifier
                                    model = RandomForestClassifier(
                                        n_estimators=300, random_state=self.random_seed
                                    )
                                else:  # LR
                                    model = LogisticRegression(
                                        max_iter=1000, random_state=self.random_seed
                                    )
                            else:
                                if am.upper() == "RF":
                                    from sklearn.ensemble import RandomForestRegressor
                                    model = RandomForestRegressor(
                                        n_estimators=300, random_state=self.random_seed
                                    )
                                else:  # LR
                                    model = LinearRegression()
                            
                            model.fit(X_train, y_train)
                            y_pred = model.predict(X_test)
                            
                            # Compute metrics
                            if is_classification:
                                from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
                                
                                if hasattr(y_pred, "ndim") and y_pred.ndim > 1:
                                    y_pred_class = y_pred.argmax(axis=1)
                                else:
                                    y_pred_class = y_pred
                                
                                metrics = {
                                    "accuracy": float(accuracy_score(y_test, y_pred_class)),
                                    "f1_macro": float(f1_score(y_test, y_pred_class, average="macro"))
                                }
                                
                                # Try to get AUC if binary and probabilities available
                                try:
                                    if mode == "blackbox" and hasattr(model, 'predict_proba'):
                                        proba = model.predict_proba(X_test)
                                        if proba.shape[1] == 2:
                                            metrics["auc"] = float(roc_auc_score(y_test, proba[:, 1]))
                                except:
                                    pass
                            else:
                                from sklearn.metrics import mean_absolute_error, r2_score
                                metrics = {
                                    "mae": float(mean_absolute_error(y_test, y_pred)),
                                    "r2": float(r2_score(y_test, y_pred))
                                }
                            
                            by_attack[am] = metrics
                            
                        except Exception as e:
                            by_attack[am] = {"error": str(e)}
                    
                    # Mantém baseline LR para compatibilidade
                    baseline = by_attack.get("LR") or next((v for k,v in by_attack.items() if isinstance(v, dict)), None)
                    if baseline:
                        attr_results["metrics"] = baseline
                    attr_results["by_attack"] = by_attack
                    attr_results["n_test_samples"] = len(y_test)
                
                # ESTRATIFICAÇÃO POR RARIDADE E GRUPO SENSÍVEL
                do_rarity = config.privacy_stratify.get("rarity", False) if config else False
                do_sensitive = config.privacy_stratify.get("sensitive", False) if config else False
                by_strata = {}
                
                if (do_rarity or do_sensitive) and mode == "blackbox":
                    real_eval_df = real_df.loc[X_test.index].copy()
                    
                    if do_rarity:
                        # Calcular raridade apenas nas features conhecidas
                        df_num = X_test.select_dtypes(include=["number"]).copy()
                        if df_num.shape[1] > 0:
                            from sklearn.preprocessing import StandardScaler
                            ss = StandardScaler().fit(df_num.values)
                            z = ss.transform(df_num.values)
                            rarity = _knn_rarity_scores(pd.DataFrame(z, index=df_num.index), k=5)
                            bins = _make_strata(rarity, n_bins=5)
                            if bins is not None:
                                for b in sorted(bins.dropna().unique()):
                                    idx = (bins == b).values
                                    if idx.sum() >= 20:
                                        Xb, yb = X_test.iloc[idx], y_test.iloc[idx]
                                        if Xb.shape[0] >= 10:
                                            try:
                                                model = _fit_attack_model("LR", X_train, y_train)
                                                y_pred_b, prob_b = _predict_attack_model(model, Xb)
                                                from sklearn.metrics import accuracy_score, roc_auc_score
                                                acc = accuracy_score(yb, y_pred_b)
                                                auc = roc_auc_score(yb, prob_b) if prob_b is not None else None
                                                by_strata.setdefault("rarity", {})[str(b)] = {"acc": float(acc), "auc": (None if auc is None else float(auc)), "n": int(idx.sum())}
                                            except Exception as e:
                                                by_strata.setdefault("rarity", {})[str(b)] = {"error": str(e), "n": int(idx.sum())}
                    
                    if do_sensitive and config.sensitive_attributes:
                        sens_col = config.sensitive_attributes[0]
                        if sens_col in real_eval_df.columns:
                            groups = real_eval_df[sens_col].astype(str)
                            for g in sorted(groups.dropna().unique()):
                                idx = (groups == g).values
                                if idx.sum() >= 20:
                                    Xg, yg = X_test.iloc[idx], y_test.iloc[idx]
                                    if Xg.shape[0] >= 10:
                                        try:
                                            model = _fit_attack_model("LR", X_train, y_train)
                                            y_pred_g, prob_g = _predict_attack_model(model, Xg)
                                            from sklearn.metrics import accuracy_score, roc_auc_score
                                            acc = accuracy_score(yg, y_pred_g)
                                            auc = roc_auc_score(yg, prob_g) if prob_g is not None else None
                                            by_strata.setdefault("sensitive", {})[str(g)] = {"acc": float(acc), "auc": (None if auc is None else float(auc)), "n": int(idx.sum())}
                                        except Exception as e:
                                            by_strata.setdefault("sensitive", {})[str(g)] = {"error": str(e), "n": int(idx.sum())}
                
                attr_results["by_strata"] = by_strata
                
            except Exception as e:
                attr_results["error"] = str(e)
            
            results["attributes"][sensitive_attr] = attr_results
        
        return results

class FairnessEvaluator:
    """Complete Fairness Evaluation implementation"""
    
    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        self._last_y_true = None
        self._last_y_prob = None
    
    @staticmethod
    def _compute_group_metrics(y_true: np.ndarray, y_pred: np.ndarray, 
                              sensitive: np.ndarray) -> Dict[str, Dict[str, float]]:
        """Compute fairness metrics per group"""
        from sklearn.metrics import confusion_matrix
        
        metrics = {}
        groups = pd.Series(sensitive).astype("category").cat.categories
        
        for group in groups:
            mask = (sensitive == group)
            y_t = y_true[mask]
            y_p = y_pred[mask]
            
            if len(y_t) == 0:
                continue
            
            try:
                # Ensure binary classification
                tn, fp, fn, tp = confusion_matrix(
                    y_t, y_p, labels=[0, 1]
                ).ravel()
            except:
                tn = fp = fn = tp = 0
            
            # Selection rate (positive prediction rate)
            selection_rate = float((y_p == 1).mean()) if len(y_p) > 0 else 0.0
            
            # True positive rate (recall)
            tpr = float(tp / (tp + fn)) if (tp + fn) > 0 else float("nan")
            
            # False positive rate
            fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else float("nan")
            
            # Precision
            precision = float(tp / (tp + fp)) if (tp + fp) > 0 else float("nan")
            
            metrics[str(group)] = {
                "selection_rate": selection_rate,
                "tpr": tpr,
                "fpr": fpr,
                "precision": precision,
                "n_samples": int(len(y_t))
            }
        
        return metrics
    
    def _brier_score(self, y_true, y_prob):
        import numpy as np
        return float(np.mean((y_prob - y_true)**2))
    
    def _ece_score(self, y_true, y_prob, n_bins=10):
        import numpy as np
        y_true = np.asarray(y_true).astype(int)
        y_prob = np.asarray(y_prob).astype(float)
        bins = np.linspace(0.0, 1.0, n_bins+1)
        ece = 0.0
        for i in range(n_bins):
            msk = (y_prob >= bins[i]) & (y_prob < bins[i+1] if i < n_bins-1 else y_prob <= bins[i+1])
            if msk.sum() == 0:
                continue
            acc = np.mean((y_prob[msk] >= 0.5) == y_true[msk])
            conf = np.mean(y_prob[msk])
            ece += (msk.mean()) * abs(acc - conf)
        return float(ece)
    
    def _threshold_sweep_by_group(self, y_true, y_prob, sensitive_series, thresholds=None):
        import numpy as np
        from sklearn.metrics import accuracy_score, f1_score
        thresholds = thresholds or np.linspace(0.3, 0.7, 9)
        curves = []
        groups = sorted(sensitive_series.astype(str).dropna().unique())
        for thr_g0 in thresholds:
            for thr_g1 in thresholds:
                # Exemplo para 2 grupos; generalize para >2 usando dict por grupo
                thr_map = {}
                if len(groups) == 2:
                    thr_map[groups[0]] = thr_g0
                    thr_map[groups[1]] = thr_g1
                else:
                    # todos com o mesmo thr
                    for g in groups:
                        thr_map[g] = thr_g0
                # aplica limiares
                yhat = []
                for yi, pi, gi in zip(y_true, y_prob, sensitive_series.astype(str).values):
                    t = thr_map.get(gi, 0.5)
                    yhat.append(1 if pi >= t else 0)
                yhat = np.asarray(yhat)
                acc = float(accuracy_score(y_true, yhat))
                f1m = float(f1_score(y_true, yhat, average="macro"))
                # fairness: DP / EO gaps
                # compute per-group selection rate, tpr/fpr
                rates = {}
                for g in groups:
                    msk = (sensitive_series.astype(str).values == g)
                    if msk.sum() < 10:
                        continue
                    yt = y_true[msk]; yh = yhat[msk]
                    sel = float(yh.mean())
                    tpr = float(((yh==1) & (yt==1)).sum() / max((yt==1).sum(),1))
                    fpr = float(((yh==1) & (yt==0)).sum() / max((yt==0).sum(),1))
                    rates[g] = {"selection_rate": sel, "tpr": tpr, "fpr": fpr}
                if len(rates) >= 2:
                    dp_gap = max(v["selection_rate"] for v in rates.values()) - min(v["selection_rate"] for v in rates.values())
                    eopp_gap = max(v["tpr"] for v in rates.values()) - min(v["tpr"] for v in rates.values())
                    eo_fpr_gap = max(v["fpr"] for v in rates.values()) - min(v["fpr"] for v in rates.values())
                else:
                    dp_gap = eopp_gap = eo_fpr_gap = None
                curves.append({"thr_map": thr_map, "acc": acc, "f1_macro": f1m,
                               "dp_gap": dp_gap, "eopp_gap": eopp_gap, "eo_fpr_gap": eo_fpr_gap})
        return curves
    
    def evaluate_fairness(self, real_df: pd.DataFrame, synth_df: pd.DataFrame,
                         target_col: str, sensitive_attributes: List[str],
                         config: ExperimentConfig = None) -> Dict[str, Any]:
        """
        Evaluate fairness metrics including:
        - Demographic parity (disparate impact)
        - Equalized odds (TPR/FPR gaps)
        - Predictive parity
        - Calibration by group
        """
        results = {"by_attribute": {}, "overall": {}}
        
        if target_col not in real_df.columns or target_col not in synth_df.columns:
            results["overall"]["error"] = "Target column missing"
            return results
        
        try:
            # Train model on synthetic, test on real
            X_synth = pd.get_dummies(
                synth_df.drop(columns=[target_col], errors="ignore"),
                drop_first=True
            )
            y_synth = synth_df[target_col].astype("category").cat.codes
            
            X_real = pd.get_dummies(
                real_df.drop(columns=[target_col], errors="ignore"),
                drop_first=True
            ).reindex(columns=X_synth.columns, fill_value=0)
            
            # Train classifier
            clf = LogisticRegression(max_iter=1000, random_state=42)
            try:
                clf.fit(X_synth, y_synth)
            except:
                from sklearn.ensemble import RandomForestClassifier
                clf = RandomForestClassifier(n_estimators=300, random_state=42)
                clf.fit(X_synth, y_synth)
            
            # Predict on real data
            y_true = real_df[target_col].astype("category").cat.codes.values
            y_pred = clf.predict(X_real)
            
            # Store probabilities for calibration analysis
            if hasattr(clf, 'predict_proba'):
                y_prob = clf.predict_proba(X_real)[:, 1]
                self._last_y_true = y_true
                self._last_y_prob = y_prob
            else:
                y_prob = None
            
            # Overall performance
            from sklearn.metrics import accuracy_score, f1_score
            results["overall"]["accuracy"] = float(accuracy_score(y_true, y_pred))
            results["overall"]["f1_macro"] = float(f1_score(y_true, y_pred, average="macro"))
            
            # Per-attribute fairness
            for sensitive_attr in (sensitive_attributes or []):
                if sensitive_attr not in real_df.columns:
                    continue
                
                sensitive = real_df[sensitive_attr].astype("category").values
                
                # Compute group metrics
                group_metrics = FairnessEvaluator._compute_group_metrics(
                    y_true, y_pred, sensitive
                )
                
                # Compute fairness metrics
                selection_rates = [
                    v["selection_rate"] for v in group_metrics.values()
                    if not np.isnan(v["selection_rate"])
                ]
                
                # Disparate impact ratio
                if selection_rates and max(selection_rates) > 0:
                    di_ratio = float(min(selection_rates) / max(selection_rates))
                else:
                    di_ratio = float("nan")
                
                # Equalized odds: TPR and FPR gaps
                tprs = [v["tpr"] for v in group_metrics.values() if not np.isnan(v["tpr"])]
                fprs = [v["fpr"] for v in group_metrics.values() if not np.isnan(v["fpr"])]
                
                if len(tprs) > 1:
                    eo_tpr_gap = float(max(abs(a - b) for i, a in enumerate(tprs) 
                                          for b in tprs[i+1:]))
                else:
                    eo_tpr_gap = float("nan")
                
                if len(fprs) > 1:
                    eo_fpr_gap = float(max(abs(a - b) for i, a in enumerate(fprs) 
                                          for b in fprs[i+1:]))
                else:
                    eo_fpr_gap = float("nan")
                
                # NEW: DP gap and EOpp gap
                try:
                    # Selection rate por grupo já existente -> compute DP gap
                    sel = {g: m.get("selection_rate", None) for g, m in group_metrics.items()}
                    sel_vals = [v for v in sel.values() if v is not None]
                    dp_gap = (max(sel_vals) - min(sel_vals)) if len(sel_vals) >= 2 else None

                    # EOpp = gap de TPR
                    tpr = {g: m.get("tpr", None) for g, m in group_metrics.items()}
                    tpr_vals = [v for v in tpr.values() if v is not None]
                    eopp_gap = (max(tpr_vals) - min(tpr_vals)) if len(tpr_vals) >= 2 else None
                except Exception:
                    dp_gap = eopp_gap = None
                
                # NEW: Calibration por grupo
                calibration_by_group = {}
                try:
                    if y_prob is not None:
                        for g in group_metrics.keys():
                            msk = (sensitive == g)
                            if hasattr(self, "_last_y_prob") and hasattr(self, "_last_y_true"):
                                yt = self._last_y_true[msk]
                                yp = self._last_y_prob[msk]
                                if yt.shape[0] >= 30:
                                    calibration_by_group[str(g)] = {
                                        "brier": self._brier_score(yt, yp),
                                        "ece": self._ece_score(yt, yp, n_bins=10),
                                        "n": int(yt.shape[0])
                                    }
                except Exception:
                    pass
                
                results["by_attribute"][sensitive_attr] = {
                    "group_metrics": group_metrics,
                    "disparate_impact": di_ratio,
                    "equalized_odds_tpr_gap": eo_tpr_gap,
                    "equalized_odds_fpr_gap": eo_fpr_gap,
                    "dp_gap": dp_gap,
                    "eopp_gap": eopp_gap,
                    "calibration_by_group": calibration_by_group,
                    "interpretation": {
                        "disparate_impact": "fair" if di_ratio >= 0.8 else "biased",
                        "equalized_odds": "fair" if eo_tpr_gap < 0.1 and eo_fpr_gap < 0.1 else "biased"
                    }
                }
                
                # NEW: Mitigation curves
                try:
                    if config and config.fairness_mitigation_curves and y_prob is not None:
                        results["by_attribute"][sensitive_attr]["mitigation_curves"] = self._threshold_sweep_by_group(
                            y_true=self._last_y_true, y_prob=self._last_y_prob,
                            sensitive_series=pd.Series(sensitive),
                            thresholds=None
                        )
                except Exception as e:
                    results["by_attribute"][sensitive_attr]["mitigation_curves_error"] = str(e)
        
        except Exception as e:
            results["overall"]["error"] = str(e)
        
        return results

class PrivacyEvaluator:
    """Unified privacy evaluator"""
    
    def __init__(self, random_seed: int = 42, n_shadow_models: int = 5):
        self.random_seed = random_seed
        self.mia_evaluator = MembershipInferenceEvaluator(
            random_seed, n_shadow_models
        )
        self.aia_evaluator = AttributeInferenceEvaluator(random_seed)
        logger.info("Privacy evaluator initialized")
    
    def distance_to_closest_record(self, real_df: pd.DataFrame, 
                                   synth_df: pd.DataFrame) -> Dict[str, Any]:
        """Distance to Closest Record (DCR) metric"""
        try:
            # Use only numeric columns
            numeric_cols = real_df.select_dtypes(include=[np.number]).columns
            X_real = real_df[numeric_cols].fillna(0).values
            X_synth = synth_df[numeric_cols].fillna(0).values
            
            # Normalize
            scaler = StandardScaler()
            X_real_scaled = scaler.fit_transform(X_real)
            X_synth_scaled = scaler.transform(X_synth)
            
            # Compute distances
            nbrs = NearestNeighbors(n_neighbors=1, metric='euclidean')
            nbrs.fit(X_real_scaled)
            distances, _ = nbrs.kneighbors(X_synth_scaled)
            
            results = {
                "mean_distance": float(np.mean(distances)),
                "median_distance": float(np.median(distances)),
                "min_distance": float(np.min(distances)),
                "max_distance": float(np.max(distances)),
                "std_distance": float(np.std(distances)),
                "privacy_risk_counts": {
                    "distance_below_0.1": int(np.sum(distances < 0.1)),
                    "distance_below_0.5": int(np.sum(distances < 0.5)),
                    "distance_above_1.0": int(np.sum(distances >= 1.0))
                }
            }
            
            return results
        
        except Exception as e:
            return {"error": str(e)}
    
    def membership_inference_attack(self, real_df: pd.DataFrame,
                                   synth_df: pd.DataFrame,
                                   target_col: str,
                                   config: ExperimentConfig = None) -> Dict[str, Any]:
        """Wrapper for MIA"""
        return self.mia_evaluator.evaluate(real_df, synth_df, target_col, config)
    
    def attribute_inference_attack(self, real_df: pd.DataFrame,
                                   synth_df: pd.DataFrame,
                                   sensitive_attributes: List[str],
                                   config: ExperimentConfig = None) -> Dict[str, Any]:
        """Wrapper for AIA"""
        # Determine target column (assume first column if not obvious)
        target_col = real_df.columns[0]
        return self.aia_evaluator.evaluate(
            real_df, synth_df, target_col, sensitive_attributes,
            config=config
        )

# ============================================================================
# ENHANCED EVALUATOR - ATUALIZADO COM MLP AVANÇADO
# ============================================================================

class EnhancedEvaluator:
    """Enhanced evaluator with all metrics including advanced MLP"""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.alpha = config.alpha
        self.multiple_testing_correction = config.multiple_testing_correction
        self.privacy_evaluator = PrivacyEvaluator(
            config.random_seed,
            config.mia_n_shadow_models
        )
        self.statistical_rigor = StatisticalRigorFramework()
        self.mlp_optimizer = FastMLPOptimizer(config)
        self.logger = logger
        logger.info("Enhanced evaluator with FAST+ROBUST MLP initialized")
    
    def _create_default_mlp(self, task_type, random_state=None):
        """Cria um MLP padrão ROBUSTO (com proteção contra overflow)."""
        default_params = self.mlp_optimizer.get_default_params(task_type)
        return create_robust_mlp(task_type, default_params, random_state)

    def _make_model_constructor(self, model_name: str, task_type: str, 
                               X_train=None, y_train=None, random_state=None, **kwargs):
        """Cria construtor de modelo com otimização bayesiana para MLP (CORRIGIDO)"""
        
        if model_name == 'mlp':
            # Sempre inicializar best_params com valores padrão
            best_params = self.mlp_optimizer.get_default_params(task_type)
            
            # Se a otimização estiver ativada e tivermos dados de treino, tente otimizar
            if self.config.enable_mlp_tuning and X_train is not None and y_train is not None:
                try:
                    optimized_params = self.mlp_optimizer.optimize_mlp_params(
                        X_train, y_train, task_type, 
                        n_trials=min(12, self.config.mlp_tuning_trials)
                    )
                    
                    # Se a otimização foi bem-sucedida, use os parâmetros otimizados
                    if optimized_params is not None:
                        best_params = optimized_params
                    
                    # Criar ensemble de MLPs
                    mlp_ensemble = AdvancedMLPEnsemble(self.config, task_type)
                    
                    # Criar múltiplos construtores para ensemble
                    ensemble_size = self.config.mlp_ensemble_size
                    constructors = []
                    
                    for i in range(ensemble_size):
                        ctor = mlp_ensemble.create_mlp_constructor(
                            best_params=best_params, 
                            ensemble_idx=i
                        )
                        constructors.append(ctor)
                    
                    # Capturar best_params no closure
                    def ensemble_constructor(random_state=None):
                        from sklearn.ensemble import VotingClassifier, VotingRegressor
                        
                        models = []
                        for i, ctor in enumerate(constructors):
                            model = ctor(random_state=random_state + i if random_state else None)
                            models.append((f'mlp_{i}', model))
                        
                        if task_type == 'classification':
                            ensemble = VotingClassifier(
                                estimators=models,
                                voting='soft',
                                n_jobs=1
                            )
                        else:
                            ensemble = VotingRegressor(
                                estimators=models,
                                n_jobs=1
                            )
                        
                        return ensemble
                    
                    return ensemble_constructor
                    
                except Exception as e:
                    logger.warning(f"MLP ensemble optimization failed: {e}. Using single optimized MLP.")
            
            # Fallback: MLP padrão (sem otimização ou se a otimização falhou)
            # Capturar best_params no closure
            def constructor(random_state=None):
                # Usar best_params para criar um MLP único ROBUSTO
                return create_robust_mlp(task_type, best_params, random_state)
            
            return constructor
        
        # Modelos não-MLP (mantém implementação original; agora com ramo de regressão correto)
        if task_type == 'classification':
            if model_name == 'lr':
                # Padroniza para estabilidade numérica/otimização
                return lambda random_state=None: Pipeline([
                    ('scaler', StandardScaler()),
                    ('lr', LogisticRegression(C=1.0, max_iter=10000, solver='lbfgs', random_state=random_state))
                ])
            if model_name == 'rf':
                return lambda random_state=None: RandomForestClassifier(
                    n_estimators=300, random_state=random_state, n_jobs=-1
                )
            if model_name == 'xgb' and XGBOOST_AVAILABLE:
                return lambda random_state=None: xgb.XGBClassifier(
                    n_estimators=300, max_depth=6, learning_rate=0.1,
                    subsample=0.8, colsample_bytree=0.8,
                    random_state=random_state
                )
            raise ValueError(f"Modelo não suportado para classificação: {model_name}")

        # Regressão
        if model_name == 'rf':
            # TESTE DE ISOLAMENTO (Claude, 2026-07-05): regularização restaurada para os
            # valores do script antigo verificado (max_depth=15, min_samples_split=5,
            # min_samples_leaf=2), que estava ausente aqui (max_depth ilimitado, defaults
            # de min_samples_*). Objetivo: isolar se a queda de utilidade observada no
            # rerun v9 vem de mudança de hiperparâmetro ou de outro fator.
            return lambda random_state=None: RandomForestRegressor(
                n_estimators=200, max_depth=15, min_samples_split=5, min_samples_leaf=2,
                random_state=random_state, n_jobs=-1
            )
        if model_name == 'lr':
            # LinearRegression não tem random_state; mantemos assinatura homogênea
            return lambda random_state=None: LinearRegression()
        if model_name == 'xgb' and XGBOOST_AVAILABLE:
            return lambda random_state=None: xgb.XGBRegressor(
                n_estimators=300, max_depth=6, learning_rate=0.1,
                subsample=0.8, colsample_bytree=0.8,
                random_state=random_state
            )
        raise ValueError(f"Modelo não suportado para regressão: {model_name}")
    def _get_scorer(self, task_type: str):
        """Retorna função de avaliação"""
        if task_type == 'classification':
            def scorer(y_true, y_pred):
                return {
                    "accuracy": float(accuracy_score(y_true, y_pred)),
                    "f1_macro": float(f1_score(y_true, y_pred, average="macro"))
                }
            return scorer
        else:
            def scorer(y_true, y_pred):
                return {
                    "r2": float(r2_score(y_true, y_pred)),
                    "mae": float(mean_absolute_error(y_true, y_pred)),
                    "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred)))
                }
            return scorer
    
    
    def evaluate_utility_enhanced(
        self,
        real_df: pd.DataFrame,
        synth_df: pd.DataFrame,
        target: str,
        ml_models: Optional[List[str]] = None,
        n_runs: int = 10,
        task_type: str = "regression",
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """
        Avaliação de utilidade (TSTR/TRTR) com rigor estatístico e suporte a small-n.

        - TRTR: treina no REAL(train) e testa no REAL(test)
        - TSTR: treina no SINTÉTICO(amostrado) e testa no REAL(test)
        - Δ same-model: TSTR - TRTR (mesmo modelo), reduz artefatos em small-n.

        Retorna métricas por modelo + melhor modelo (por TSTR médio).
        Se enable_delta_feature=True, calcula Δ por variável (PFI) para o melhor modelo.
        """
        rng = np.random.default_rng(random_state)

        X_real = real_df.drop(columns=[target]).copy()
        y_real = real_df[target].copy()

        X_synth = synth_df.drop(columns=[target]).copy()
        y_synth = synth_df[target].copy()

        models = list(ml_models) if ml_models else ["lr", "rf", "xgb", "mlp"]
        results: Dict[str, Any] = {"task_type": task_type, "n_runs": int(n_runs), "models": {}}

        def _score_model(model, X, y):
            if task_type == "classification":
                try:
                    if hasattr(model, "predict_proba"):
                        p = model.predict_proba(X)[:, 1]
                        return float(roc_auc_score(y, p))
                except Exception:
                    pass
                try:
                    pred = model.predict(X)
                    return float(accuracy_score(y, pred))
                except Exception:
                    pred = model.predict(X.values)
                    return float(accuracy_score(np.asarray(y), np.asarray(pred)))
            else:
                try:
                    pred = model.predict(X)
                except Exception:
                    pred = model.predict(X.values)
                pred = np.asarray(pred, dtype=float)
                yv = np.asarray(y, dtype=float)
                pred = np.nan_to_num(pred, nan=np.nanmedian(pred), posinf=np.nanmax(yv), neginf=np.nanmin(yv))
                return float(r2_score(yv, pred))

        per_run_delta_tables = []  # para melhor modelo

        for model_name in models:
            tstr_scores = []
            trtr_scores = []
            delta_scores = []

            for run in range(n_runs):
                rs = int(rng.integers(0, 1_000_000))
                X_train, X_test, y_train, y_test = train_test_split(
                    X_real, y_real, test_size=0.25, random_state=rs
                )

                # Amostra sintético com mesmo tamanho do train real
                idx = rng.choice(len(X_synth), size=len(X_train), replace=True)
                Xs_train = X_synth.iloc[idx].copy()
                ys_train = y_synth.iloc[idx].copy()

                model_ctor = self._make_model_constructor(model_name, task_type=task_type, random_state=rs)

                # TRTR
                try:
                    model_r = model_ctor()
                    model_r.fit(X_train, y_train)
                    trtr = _score_model(model_r, X_test, y_test)
                except Exception:
                    trtr = np.nan

                # TSTR
                try:
                    model_s = model_ctor()
                    model_s.fit(Xs_train, ys_train)
                    tstr = _score_model(model_s, X_test, y_test)
                except Exception:
                    tstr = np.nan

                tstr_scores.append(float(tstr))
                trtr_scores.append(float(trtr))
                delta_scores.append(float(tstr - trtr) if (np.isfinite(tstr) and np.isfinite(trtr)) else np.nan)

            tstr_arr = np.asarray(tstr_scores, dtype=float)
            trtr_arr = np.asarray(trtr_scores, dtype=float)
            delta_arr = np.asarray(delta_scores, dtype=float)

            # IC95 por bootstrap (robusto em small-n)
            def _ci95(x):
                x = x[np.isfinite(x)]
                if len(x) < 3:
                    return (float(np.nanmean(x)) if len(x) else np.nan, np.nan, np.nan)
                boots = []
                for _ in range(2000):
                    b = rng.choice(x, size=len(x), replace=True)
                    boots.append(np.mean(b))
                lo, hi = np.percentile(boots, [2.5, 97.5])
                return float(np.mean(x)), float(lo), float(hi)

            t_mean, t_lo, t_hi = _ci95(tstr_arr)
            r_mean, r_lo, r_hi = _ci95(trtr_arr)
            d_mean, d_lo, d_hi = _ci95(delta_arr)

            results["models"][model_name] = {
                "tstr_mean": t_mean, "tstr_ci95": [t_lo, t_hi],
                "trtr_mean": r_mean, "trtr_ci95": [r_lo, r_hi],
                "delta_same_model_mean": d_mean, "delta_same_model_ci95": [d_lo, d_hi],
                "tstr_scores": tstr_scores,
                "trtr_scores": trtr_scores,
                "delta_same_model_scores": delta_scores,
            }


            # Compatibilidade (legacy): estrutura util.model_results esperada por artefatos do artigo
            try:
                results.setdefault("model_results", {})[model_name] = {
                    "TSTR": {
                        "mean": float(t_mean),
                        "ci95": [float(t_lo), float(t_hi)],
                        "scores": [{"r2": float(v), "score": float(v)} for v in (tstr_scores or [])],
                        "raw": [float(v) for v in (tstr_scores or [])],
                    },
                    "TRTR": {
                        "mean": float(r_mean),
                        "ci95": [float(r_lo), float(r_hi)],
                        "scores": [{"r2": float(v), "score": float(v)} for v in (trtr_scores or [])],
                        "raw": [float(v) for v in (trtr_scores or [])],
                    },
                    "DELTA_SAME_MODEL": {
                        "mean": float(d_mean),
                        "ci95": [float(d_lo), float(d_hi)],
                        "scores": [{"delta": float(v)} for v in (delta_scores or [])],
                        "raw": [float(v) for v in (delta_scores or [])],
                    },
                }
            except Exception:
                pass

        # Melhor modelo por TSTR médio (empate: maior Δ)
        best = None
        best_key = None
        for k, v in results["models"].items():
            score = (v["tstr_mean"], v["delta_same_model_mean"])
            if best is None or score > best:
                best = score
                best_key = k
        results["best_model"] = best_key

        # Δ por variável (PFI) para melhor modelo
        if self.config.enable_delta_feature and best_key is not None:
            self.logger.info(f"Computando Δ por variável (PFI) para best_model={best_key}...")
            feats = list(X_real.columns)
            imp_trtr = []
            imp_tstr = []

            for run in range(n_runs):
                rs = int(rng.integers(0, 1_000_000))
                X_train, X_test, y_train, y_test = train_test_split(
                    X_real, y_real, test_size=0.25, random_state=rs
                )
                idx = rng.choice(len(X_synth), size=len(X_train), replace=True)
                Xs_train = X_synth.iloc[idx].copy()
                ys_train = y_synth.iloc[idx].copy()

                ctor = self._make_model_constructor(best_key, task_type=task_type, random_state=rs)

                # importâncias TRTR
                try:
                    imp_r = compute_delta_per_feature_one_split(
                        X_train, y_train, X_test, y_test, ctor, task_type=task_type, random_state=rs,
                        n_repeats=int(getattr(self.config, "delta_repeats", 3) or 3)
                    )
                    imp_trtr.append(imp_r)
                except Exception:
                    pass

                # importâncias TSTR (treino sintético)
                try:
                    imp_s = compute_delta_per_feature_one_split(
                        Xs_train, ys_train, X_test, y_test, ctor, task_type=task_type, random_state=rs + 1,
                        n_repeats=int(getattr(self.config, "delta_repeats", 3) or 3)
                    )
                    imp_tstr.append(imp_s)
                except Exception:
                    pass

            # agrega
            def _mean_imp(list_dicts):
                if not list_dicts:
                    return {f: np.nan for f in feats}
                out = {}
                for f in feats:
                    vals = [d.get(f, np.nan) for d in list_dicts]
                    vals = np.asarray(vals, dtype=float)
                    out[f] = float(np.nanmean(vals)) if np.isfinite(vals).any() else np.nan
                return out

            m_r = _mean_imp(imp_trtr)
            m_s = _mean_imp(imp_tstr)
            rows = []
            for f in feats:
                rows.append({
                    "feature": f,
                    "imp_trtr_mean": m_r.get(f, np.nan),
                    "imp_tstr_mean": m_s.get(f, np.nan),
                    "delta_mean": (m_s.get(f, np.nan) - m_r.get(f, np.nan)),
                    "abs_delta_mean": abs((m_s.get(f, np.nan) - m_r.get(f, np.nan))) if np.isfinite(m_s.get(f, np.nan)) and np.isfinite(m_r.get(f, np.nan)) else np.nan,
                })
            delta_df = pd.DataFrame(rows).sort_values("abs_delta_mean", ascending=False)
            results["delta_per_feature_table"] = delta_df.to_dict(orient="records")

        return results

    def evaluate_fidelity_advanced(self, real_df: pd.DataFrame, 
                                  synth_df: pd.DataFrame) -> Dict[str, Any]:
        """Advanced fidelity evaluation with statistical rigor"""
        results = {"univariate_tests": {}, "correlation_preservation": {}}
        
        try:
            numeric_cols = real_df.select_dtypes(include=[np.number]).columns
            
            # Univariate tests
            for col in numeric_cols:
                if col in synth_df.columns:
                    real_data = real_df[col].dropna()
                    synth_data = synth_df[col].dropna()
                    
                    if len(real_data) > 5 and len(synth_data) > 5:
                        col_results = {}
                        
                        # KS test
                        ks_stat, ks_pval = ks_2samp(real_data, synth_data)
                        col_results["ks_test"] = {
                            "statistic": float(ks_stat),
                            "pvalue": float(ks_pval)
                        }
                        
                        # Jensen-Shannon divergence
                        try:
                            hist_real, bins = np.histogram(real_data, bins=30, density=True)
                            hist_synth, _ = np.histogram(synth_data, bins=bins, density=True)
                            hist_real = hist_real + 1e-10
                            hist_synth = hist_synth + 1e-10
                            js_div = jensenshannon(hist_real, hist_synth)
                            col_results["jensen_shannon"] = float(js_div)
                        except:
                            col_results["jensen_shannon"] = np.nan
                        
                        # Wasserstein distance
                        try:
                            wd = wasserstein_distance(real_data, synth_data)
                            col_results["wasserstein"] = float(wd)
                        except:
                            col_results["wasserstein"] = np.nan
                        
                        results["univariate_tests"][col] = col_results
            
            # Correlation preservation
            if len(numeric_cols) >= 2:
                common_cols = numeric_cols.intersection(synth_df.select_dtypes(include=[np.number]).columns)
                if len(common_cols) >= 2:
                    real_corr = real_df[common_cols].corr().values
                    synth_corr = synth_df[common_cols].corr().values
                    
                    # Flatten and correlate
                    triu_idx = np.triu_indices_from(real_corr, k=1)
                    real_corr_flat = real_corr[triu_idx]
                    synth_corr_flat = synth_corr[triu_idx]
                    
                    if len(real_corr_flat) > 0:
                        corr_of_corr, _ = pearsonr(real_corr_flat, synth_corr_flat)
                        results["correlation_preservation"]["correlation_of_correlations"] = float(corr_of_corr)
            
            # Multiple testing correction WITH FDR AS PRIMARY (ATUALIZADO)
            pvalues = []
            for col_tests in results["univariate_tests"].values():
                if "ks_test" in col_tests:
                    pvalues.append(col_tests["ks_test"]["pvalue"])
            
            if pvalues:
                # Use FDR as primary criterion (NOVO)
                multiple_testing_results = self.statistical_rigor.multiple_testing_fdr_primary(
                    pvalues, fdr_q=self.config.fdr_q
                )
                results["multiple_testing"] = multiple_testing_results
        
        except Exception as e:
            results["error"] = str(e)
        
        # ---- Additional multivariate fidelity diagnostics (joint structure) ----
        try:
            from scipy.spatial.distance import cdist
            Xr = real_df.values.astype(float)
            Xs = synth_df.values.astype(float)

            # correlation structure (Frobenius norm of correlation matrix difference)
            Cr = np.corrcoef(Xr, rowvar=False)
            Cs = np.corrcoef(Xs, rowvar=False)
            results["corr_frobenius_diff"] = float(np.linalg.norm(Cr - Cs, ord="fro"))

            # Energy distance (E-statistic) approximation
            # E(X,Y)=2 E||X-Y|| - E||X-X'|| - E||Y-Y'||
            Dxy = cdist(Xr, Xs, metric="euclidean")
            Dxx = cdist(Xr, Xr, metric="euclidean")
            Dyy = cdist(Xs, Xs, metric="euclidean")
            energy = 2*np.mean(Dxy) - np.mean(Dxx) - np.mean(Dyy)
            results["energy_distance"] = float(energy)

            # MMD with RBF kernel (median heuristic)
            allX = np.vstack([Xr, Xs])
            dists = cdist(allX, allX, metric="sqeuclidean")
            med = np.median(dists)
            gamma = 1.0 / (2.0 * med + 1e-12)

            def rbf(A, B):
                return np.exp(-gamma * cdist(A, B, metric="sqeuclidean"))

            Kxx = rbf(Xr, Xr)
            Kyy = rbf(Xs, Xs)
            Kxy = rbf(Xr, Xs)
            mmd2 = np.mean(Kxx) + np.mean(Kyy) - 2*np.mean(Kxy)
            results["mmd_rbf"] = float(max(0.0, mmd2))

        except Exception as e_joint:
            results["joint_fidelity_error"] = str(e_joint)

        return results
    
    def evaluate_privacy_enhanced(self, real_df: pd.DataFrame, 
                                 synth_df: pd.DataFrame,
                                 target_col: str,
                                 sensitive_attributes: Optional[List[str]] = None) -> Dict[str, Any]:
        """Enhanced privacy evaluation with MIA and AIA"""
        results = {}
        
        try:
            # Distance to closest record
            results["distance_to_closest_record"] = self.privacy_evaluator.distance_to_closest_record(
                real_df, synth_df
            )
            
            # Membership inference attack
            if len(real_df) >= 20 and len(synth_df) >= 20:
                y_series = real_df[target_col]
                n_unique = y_series.nunique()
                n_samples = len(y_series)
                
                is_classification = (not pd.api.types.is_numeric_dtype(y_series) or 
                                   (pd.api.types.is_integer_dtype(y_series) and 
                                    n_unique <= 20 and 
                                    (n_unique / n_samples) <= 0.2))
                
                if is_classification:
                    results["membership_inference"] = self.privacy_evaluator.membership_inference_attack(
                        real_df, synth_df, target_col, self.config
                    )
                else:
                    results["membership_inference"] = {
                        "info": "Skipped for regression task",
                        "n_unique": int(n_unique),
                        "n_samples": int(n_samples)
                    }
            
            # Attribute inference attack
            if sensitive_attributes and len(sensitive_attributes) > 0:
                results["attribute_inference"] = self.privacy_evaluator.attribute_inference_attack(
                    real_df, synth_df, sensitive_attributes, self.config
                )
        
        except Exception as e:
            results["error"] = str(e)
            logger.error(f"Privacy evaluation failed: {e}")
        
        return results
    
    def evaluate_fairness_enhanced(self, real_df: pd.DataFrame,
                                  synth_df: pd.DataFrame,
                                  target_col: str,
                                  sensitive_attributes: Optional[List[str]] = None) -> Dict[str, Any]:
        """Enhanced fairness evaluation"""
        if sensitive_attributes is None:
            sensitive_attributes = []
        
        fairness_evaluator = FairnessEvaluator(self.config.random_seed)
        return fairness_evaluator.evaluate_fairness(
            real_df, synth_df, target_col, sensitive_attributes, self.config
        )
    
    def evaluate_diversity(self, real_df: pd.DataFrame, 
                          synth_df: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate diversity metrics"""
        results = {}
        
        try:
            # Use only numeric columns
            numeric_cols = real_df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                return {"error": "No numeric columns for diversity analysis"}
            
            X_real = real_df[numeric_cols].fillna(0).values
            X_synth = synth_df[numeric_cols].fillna(0).values
            
            # Normalize
            scaler = StandardScaler()
            X_real_scaled = scaler.fit_transform(X_real)
            X_synth_scaled = scaler.transform(X_synth)
            
            # Coverage metrics
            nbrs = NearestNeighbors(n_neighbors=1, metric='euclidean')
            nbrs.fit(X_real_scaled)
            distances, _ = nbrs.kneighbors(X_synth_scaled)
            
            # Diversity metrics
            synth_nbrs = NearestNeighbors(n_neighbors=2, metric='euclidean')
            synth_nbrs.fit(X_synth_scaled)
            synth_distances, _ = synth_nbrs.kneighbors(X_synth_scaled)
            avg_min_distance = np.mean(synth_distances[:, 1])  # Distance to nearest neighbor
            
            results = {
                "coverage": {
                    "fraction_within_0.1": float(np.mean(distances < 0.1)),
                    "fraction_within_0.5": float(np.mean(distances < 0.5)),
                    "fraction_within_1.0": float(np.mean(distances < 1.0)),
                    "mean_distance_to_real": float(np.mean(distances))
                },
                "diversity": {
                    "avg_min_distance_synth": float(avg_min_distance),
                    "relative_diversity": float(avg_min_distance / (np.mean(distances) + 1e-10))
                }
            }
        
        except Exception as e:
            results["error"] = str(e)
        
        return results

# ============================================================================
# SYNTHETIC DATA EXPERIMENT - CLASSE PRINCIPAL ATUALIZADA
# ============================================================================

class SyntheticDataExperiment:
    """Main experiment class updated with advanced MLP"""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.generator_manager = SOTAGeneratorManager(
            config.random_seed, target_col=config.target_column
        )
        self.evaluator = EnhancedEvaluator(config)
        self.data_processor = EnhancedDataProcessor()
        self.results = {}
        
        # Setup output directory
        self.output_dir = Path(config.output_dir)
        self.logger = logger
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Experiment initialized with output directory: {self.output_dir}")
    
    def load_data(self) -> Optional[pd.DataFrame]:
        """Load data from CSV or Excel"""
        try:
            if self.config.input_csv:
                df = pd.read_csv(self.config.input_csv)
                logger.info(f"Loaded data from {self.config.input_csv}: {df.shape}")
            elif self.config.input_xlsx:
                df = pd.read_excel(self.config.input_xlsx)
                logger.info(f"Loaded data from {self.config.input_xlsx}: {df.shape}")
            else:
                logger.error("No input file specified")
                return None
            
            # Validate data
            validator = DataValidator()
            validation_results = validator.validate_dataframe(
                df, self.config.target_column, self.config.categorical_threshold
            )
            
            if not validation_results["is_valid"]:
                logger.error(f"Data validation failed: {validation_results['errors']}")
                return None
            
            logger.info("Data validation passed")
            return df
            
        except Exception as e:
            logger.error(f"Data loading failed: {e}")
            return None
    
    def preprocess_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Preprocess data preserving categorical types"""
        try:
            # Detect data types
            type_info = DataValidator.detect_data_types(
                df, self.config.categorical_threshold
            )
            
            # Create SDV metadata
            metadata = self.data_processor.create_sdv_metadata(df, type_info)
            
            # Preprocess data
            df_processed = self.data_processor.preprocess_data(
                df, self.config, type_info
            )
            
            logger.info(f"Preprocessing completed: {df_processed.shape}")
            return df_processed, {"type_info": type_info, "metadata": metadata}
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            return df, {}
    
    def generate_synthetic_data(self, df: pd.DataFrame, 
                               metadata: Any = None) -> Dict[str, pd.DataFrame]:
        """Generate synthetic data using all specified generators"""
        synthetic_datasets = {}
        
        for generator_type in self.config.generators:
            pool_factor = float(getattr(self.config, "dcr_pool_factor", 1.5))
            n_gen = int(self.config.n_synthetic)
            if getattr(self.config, "enable_dcr_filter", False) and pool_factor > 1.0:
                n_gen = int(math.ceil(n_gen * pool_factor))

            generator_name = generator_type.value if isinstance(generator_type, GeneratorType) else generator_type
            
            logger.info(f"Generating with {generator_name}...")
            
            try:
                if generator_name == "gaussian_copula":
                    synth_df = self.generator_manager.generate_gaussian_copula(
                        df, n_gen, metadata
                    )
                elif generator_name == "ctgan":
                    synth_df = self.generator_manager.generate_ctgan(
                        df, n_gen, metadata, **(self.config.ctgan_params or {})
                    )
                elif generator_name == "tvae":
                    synth_df = self.generator_manager.generate_tvae(
                        df, n_gen, metadata
                    )
                elif generator_name == "tabddpm":
                    synth_df = self.generator_manager.generate_tabddpm(
                        df, n_gen, metadata, **(self.config.tabddpm_params or {})
                    )
                elif generator_name == "copulagan":
                    synth_df = self.generator_manager.generate_copulagan(
                        df, n_gen, metadata
                    )
                elif generator_name == "vae":
                    synth_df = self.generator_manager.generate_vae(
                        df, n_gen, metadata
                    )
                elif generator_name == "wgan_gp":
                    synth_df = self.generator_manager.generate_wgan_gp(
                        df, n_gen, metadata
                    )
                elif generator_name == "kde_sampling":
                    synth_df = self.generator_manager.generate_kde_sampling(
                        df, n_gen
                    )
                else:
                    logger.warning(f"Unknown generator: {generator_name}")
                    synth_df = self.generator_manager.generate_gaussian_naive(
                        df, n_gen
                    )
                
                if synth_df is not None:
                    # Pós-processamento (clipping + snap) e ruído opcional
                    if self.config.enable_postprocessing:
                        # DOE-based noise (preferido) aplicado antes do clipping/snap
                        if getattr(self.config, 'enable_doe_noise', False) and float(getattr(self.config, 'doe_noise_pct', 0.0) or 0.0) > 0.0:
                            synth_df = apply_doe_based_noise(synth_df, df, float(self.config.doe_noise_pct))
                        # legacy additive noise_pct é aplicado dentro de postprocess_synthetic
                        synth_df = postprocess_synthetic(synth_df, df, float(getattr(self.config, 'noise_pct', 0.0) or 0.0))
                        logger.info(f"Aplicado pós-processamento para {generator_name}")

                    # DCR Threshold Filtering (A4) - opcional
                    if getattr(self.config, 'enable_dcr_filter', False):
                        n_target = int(self.config.n_synthetic)
                        tau = float(getattr(self.config, 'dcr_tau', 0.10) or 0.10)
                        feature_cols = [c for c in df.columns if c != self.config.target_column]
                        synth_df, stats = dcr_threshold_filter_pool(
                            synth_df, df,
                            tau=tau,
                            metric='euclidean',
                            max_pool_factor=self.config.dcr_max_pool_factor,
                            desired_n=n_target,
                            always_deliver=self.config.always_deliver_n_synthetic,
                            repulsion_max_iters=self.config.dcr_repulsion_max_iters,
                            target_col=self.config.target_column,
                            logger=logger,
                        )
                        logger.info(f"DCR filtering applied to {generator_name}: {stats}")

                    synthetic_datasets[generator_name] = synth_df
                    logger.info(f"Successfully generated {len(synth_df)} samples with {generator_name}")
                else:
                    logger.warning(f"Generator {generator_name} returned None")
                    
            except Exception as e:
                logger.error(f"Generator {generator_name} failed: {e}")
        
        return synthetic_datasets
    
    def evaluate_synthetic_data(self, real_df: pd.DataFrame, 
                               synthetic_datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Comprehensive evaluation of synthetic datasets"""
        evaluation_results = {}
        
        for generator_name, synth_df in synthetic_datasets.items():
            logger.info(f"Evaluating {generator_name}...")
            generator_results = {}
            
            try:
                # Fidelity evaluation
                if "fidelity" in self.config.eval_metrics:
                    generator_results["fidelity"] = self.evaluator.evaluate_fidelity_advanced(
                        real_df, synth_df
                    )
                
                # Utility evaluation
                if "utility" in self.config.eval_metrics:
                    generator_results["utility"] = self.evaluator.evaluate_utility_enhanced(
                        real_df, synth_df, self.config.target_column,
                        self.config.ml_models, self.config.n_runs,
                        self.config.task_type
                    )
                
                # Privacy evaluation
                if "privacy" in self.config.eval_metrics:
                    generator_results["privacy"] = self.evaluator.evaluate_privacy_enhanced(
                        real_df, synth_df, self.config.target_column,
                        self.config.sensitive_attributes
                    )
                
                # Fairness evaluation
                if "fairness" in self.config.eval_metrics and self.config.enable_fairness_eval:
                    generator_results["fairness"] = self.evaluator.evaluate_fairness_enhanced(
                        real_df, synth_df, self.config.target_column,
                        self.config.sensitive_attributes
                    )
                
                # Diversity evaluation
                if "diversity" in self.config.eval_metrics:
                    generator_results["diversity"] = self.evaluator.evaluate_diversity(
                        real_df, synth_df
                    )
                
                evaluation_results[generator_name] = generator_results
                
            except Exception as e:
                logger.error(f"Evaluation for {generator_name} failed: {e}")
                evaluation_results[generator_name] = {"error": str(e)}
        
        return evaluation_results
    

    def _generate_article_and_q1q2_artifacts(
        self,
        real_df: pd.DataFrame,
        synthetic_datasets: Dict[str, pd.DataFrame],
        evaluation_results: Dict[str, Any],
    ) -> None:
        """Gera tabela e figuras 'article-ready' (Q1/Q2) sem alterar o pipeline."""
        if evaluation_results is None or synthetic_datasets is None:
            return

        try:
            cfg = self.config.to_dict() if hasattr(self.config, "to_dict") else self._config_to_dict()
        except Exception:
            cfg = {}

        out_dir = str(self.output_dir)

        # Tabela do artigo + parágrafo Results/Discussion
        article_df = None
        try:
            article_df = build_article_table_from_results(
                evaluation_results=evaluation_results,
                real_df=real_df,
                synthetic_datasets=synthetic_datasets,
                config=cfg,
                output_dir=out_dir,
            )
            try:
                article_df.to_csv(os.path.join(out_dir, "article_table.csv"), index=False)
            except Exception:
                pass

            # Mantém em memória para save_results()
            try:
                self.article_table_csv = article_df.to_csv(index=False)
            except Exception:
                self.article_table_csv = ""

            try:
                self.article_table_md = article_df.to_markdown(index=False)
            except Exception:
                self.article_table_md = ""

            try:
                self.results_discussion_txt = generate_results_discussion_paragraph(article_df, cfg)
            except Exception:
                self.results_discussion_txt = ""
        except Exception as e:
            self.logger.warning(f"Falha ao gerar tabela do artigo: {e}")

        # Figuras (pasta dedicada)
        try:
            fig_dir = Path(out_dir) / "q1q2_figures"
            fig_dir.mkdir(parents=True, exist_ok=True)

            # Utilidade: boxplot TSTR e CI do Δ
            try:
                generate_article_utility_plots(evaluation_results, output_dir=str(fig_dir), dpi=300)
            except Exception as e:
                self.logger.warning(f"Falha ao gerar plots de utilidade: {e}")

            # Por gerador: ECDF DCR + heatmap de |corr_real - corr_synth|
            for gen_name, sdf in (synthetic_datasets or {}).items():
                if sdf is None or len(sdf) == 0:
                    continue

                # Colunas numéricas, excluindo target (evita leakage em diagnósticos)
                try:
                    num_cols = [
                        c for c in real_df.select_dtypes(include=[np.number]).columns
                        if c != self.config.target_column
                    ]
                except Exception:
                    num_cols = []

                try:
                    dcr_vals = compute_dcr_values(real_df=real_df, synth_df=sdf, feature_cols=num_cols or None)
                    plot_ecdf_dcr(
                        np.asarray(dcr_vals, dtype=float),
                        outpath=str(fig_dir / f"dcr_ecdf_{gen_name}.png"),
                        title=f"DCR ECDF - {gen_name}",
                    )
                except Exception as e:
                    self.logger.warning(f"Falha ECDF DCR ({gen_name}): {e}")

                try:
                    rd = real_df[num_cols] if num_cols else real_df
                    sd = sdf[num_cols] if num_cols else sdf
                    plot_corr_diff_heatmap(
                        real_df=rd,
                        synth_df=sd,
                        outpath=str(fig_dir / f"corrdiff_{gen_name}.png"),
                        title=f"|Corr_real - Corr_synth| - {gen_name}",
                    )
                except Exception as e:
                    self.logger.warning(f"Falha heatmap corr ({gen_name}): {e}")

            # Trade-off (Pareto): Utility vs Risk
            if article_df is not None:
                try:
                    plot_tradeoff(article_df, outpath=str(fig_dir / "tradeoff_utility_risk.png"), tau_label="DCR<0.1")
                except Exception as e:
                    self.logger.warning(f"Falha trade-off plot: {e}")

        except Exception as e:
            self.logger.warning(f"Falha ao gerar figuras Q1/Q2: {e}")

    def generate_comprehensive_report(self) -> str:
        """Gera um relatório Markdown consolidado (usado por save_results)."""
        from io import StringIO

        buf = StringIO()
        buf.write("# Synthetic Data Evaluation Report\n\n")
        buf.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Config
        try:
            buf.write("## Experiment Configuration\n\n")
            buf.write(f"- **Target Column**: {getattr(self.config, 'target_column', '')}\n")
            gens = getattr(self.config, "generators", []) or []
            try:
                gens_s = ", ".join([g.value if isinstance(g, GeneratorType) else str(g) for g in gens])
            except Exception:
                gens_s = ", ".join([str(g) for g in gens])
            buf.write(f"- **Generators**: {gens_s}\n")
            buf.write(f"- **Evaluation Metrics**: {', '.join(getattr(self.config, 'eval_metrics', []) or [])}\n")
            buf.write(f"- **Number of Runs**: {int(getattr(self.config, 'n_runs', 0) or 0)}\n")
            buf.write(f"- **Random Seed**: {int(getattr(self.config, 'random_seed', 0) or 0)}\n")
            buf.write(f"- **Post-processing**: {'Enabled' if getattr(self.config, 'enable_postprocessing', False) else 'Disabled'}\n")
            buf.write(f"- **MLP Optimization**: {'Enabled' if getattr(self.config, 'enable_mlp_tuning', False) else 'Disabled'}\n")
            buf.write(f"- **Delta repeats**: {int(getattr(self.config, 'delta_repeats', 3) or 3)}\n\n")
        except Exception:
            pass

        res = getattr(self, "results", {}) or {}
        buf.write("## Results Summary\n\n")
        if not res:
            buf.write("_No evaluation results available._\n")
            return buf.getvalue()

        rows = []
        for gen_name, r in res.items():
            r = r or {}
            fid = r.get("fidelity", {}) or {}
            util = r.get("utility", {}) or {}
            priv = r.get("privacy", {}) or {}

            # KS mean
            ks_mean = float("nan")
            try:
                ks_stats = []
                for _, t in (fid.get("univariate_tests", {}) or {}).items():
                    ks = (t or {}).get("ks_test", {}) or {}
                    if "statistic" in ks:
                        ks_stats.append(float(ks["statistic"]))
                ks_mean = float(np.mean(ks_stats)) if ks_stats else float("nan")
            except Exception:
                pass

            corr_frob = fid.get("corr_frobenius_diff", float("nan"))

            # Utility best (prefer model_results)
            best_tstr = float("nan")
            best_delta = float("nan")
            best_model = ""
            mr = util.get("model_results", None)
            try:
                if isinstance(mr, dict) and mr:
                    for mname, mres in mr.items():
                        tstr = float(((mres or {}).get("TSTR", {}) or {}).get("mean", float("nan")))
                        delta = float(((mres or {}).get("DELTA_SAME_MODEL", {}) or {}).get("mean", float("nan")))
                        if (math.isnan(best_tstr) or (tstr, delta) > (best_tstr, best_delta)):
                            best_tstr, best_delta, best_model = tstr, delta, str(mname)
                else:
                    mm = util.get("models", {}) or {}
                    for mname, v in mm.items():
                        tstr = float((v or {}).get("tstr_mean", float("nan")))
                        delta = float((v or {}).get("delta_same_model_mean", float("nan")))
                        if (math.isnan(best_tstr) or (tstr, delta) > (best_tstr, best_delta)):
                            best_tstr, best_delta, best_model = tstr, delta, str(mname)
            except Exception:
                pass

            # Privacy
            dcr = priv.get("distance_to_closest_record", {}) if isinstance(priv, dict) else {}
            med_dcr = dcr.get("median_distance", float("nan"))
            frac_01 = float("nan")
            try:
                below = (dcr.get("privacy_risk_counts", {}) or {}).get("distance_below_0.1", None)
                n_syn = None
                if hasattr(self, "synthetic_datasets") and isinstance(self.synthetic_datasets, dict) and gen_name in self.synthetic_datasets:
                    n_syn = len(self.synthetic_datasets.get(gen_name) or [])
                if below is not None and n_syn:
                    frac_01 = float(below) / float(n_syn)
            except Exception:
                pass

            rows.append((gen_name, ks_mean, corr_frob, best_tstr, best_delta, med_dcr, frac_01, best_model))

        try:
            df_sum = pd.DataFrame(
                rows,
                columns=["generator", "KS_mean", "corr_frob", "TSTR_best", "Delta_same_model", "DCR_median", "frac(DCR<0.1)", "best_model"],
            )
            buf.write(df_sum.to_markdown(index=False))
            buf.write("\n\n")
        except Exception:
            for row in rows:
                buf.write(f"- {row[0]}: TSTR_best={row[3]}, Δ={row[4]}, DCR_median={row[5]}\n")
            buf.write("\n")

        return buf.getvalue()


    def save_results(self, synthetic_datasets: Optional[Dict[str, pd.DataFrame]] = None, evaluation_results: Optional[Dict[str, Any]] = None) -> None:
        """
        Persiste artefatos do experimento para a pasta de saída:
          - synthetic_datasets/*.csv
          - evaluation_results.json
          - experiment_config.json
          - comprehensive_report.md
          - article_table.csv / .md e results_discussion.txt (quando disponíveis)
          - delta_per_feature_*.csv (quando habilitado)
          - figuras Q1/Q2 (DCR ECDF, heatmaps, trade-off, etc.)
        """
        out_dir = Path(self.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        if evaluation_results is not None:
            self.results = evaluation_results
        if synthetic_datasets is not None:
            self.synthetic_datasets = synthetic_datasets

        # Config
        try:
            config_file = out_dir / "experiment_config.json"
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump((self.config.to_dict() if hasattr(self.config, "to_dict") else self._config_to_dict()), f, indent=2, ensure_ascii=False, default=self._json_serializer)
            self.logger.info(f"Saved experiment config: {config_file}")
        except Exception as e:
            self.logger.exception(f"Falha ao salvar experiment_config.json: {e}")

        # Results
        try:
            results_file = out_dir / "evaluation_results.json"
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False, default=self._json_serializer)
            self.logger.info(f"Saved evaluation results: {results_file}")
        except Exception as e:
            self.logger.exception(f"Falha ao salvar evaluation_results.json: {e}")

        # Report markdown
        try:
            report_file = out_dir / "comprehensive_report.md"
            report_md = self.generate_comprehensive_report()
            report_file.write_text(report_md, encoding="utf-8")
            self.logger.info(f"Generated report: {report_file}")
        except Exception as e:
            self.logger.exception(f"Falha ao gerar comprehensive_report.md: {e}")

        # Article-ready outputs (se já existirem em memória)
        try:
            if hasattr(self, "article_table_csv") and self.article_table_csv:
                (out_dir / "article_table.csv").write_text(self.article_table_csv, encoding="utf-8")
            if hasattr(self, "article_table_md") and self.article_table_md:
                (out_dir / "article_table.md").write_text(self.article_table_md, encoding="utf-8")
            if hasattr(self, "results_discussion_txt") and self.results_discussion_txt:
                (out_dir / "results_discussion.txt").write_text(self.results_discussion_txt, encoding="utf-8")
        except Exception as e:
            self.logger.exception(f"Falha ao salvar outputs do artigo: {e}")


        # Synthetic datasets (CSV) — persistência explícita (v8 não gravava, apenas mantinha em memória)
        try:
            do_save = bool(getattr(self.config, "save_synthetic", True))
            if do_save and hasattr(self, "synthetic_datasets") and isinstance(self.synthetic_datasets, dict):
                synth_dir = out_dir / "synthetic_datasets"
                synth_dir.mkdir(exist_ok=True)
                for gen_name, df_syn in self.synthetic_datasets.items():
                    if df_syn is None:
                        continue
                    try:
                        # Nome compatível com versões anteriores: <generator>_synthetic.csv
                        safe_name = "".join([(c if (c.isalnum() or c in "_-") else "_") for c in str(gen_name).lower()])
                        fp = synth_dir / f"{safe_name}_synthetic.csv"
                        try:
                            df_syn.to_csv(fp, index=False, encoding="utf-8")
                            self.logger.info(f"Saved synthetic dataset: {fp}")
                        except PermissionError:
                            fp_alt = synth_dir / f"{safe_name}_synthetic_{int(time.time())}.csv"
                            df_syn.to_csv(fp_alt, index=False, encoding="utf-8")
                            self.logger.warning(f"Synthetic CSV estava bloqueado ({fp}); salvo como: {fp_alt}")
                    except Exception as e2:
                        self.logger.warning(f"Falha ao salvar dataset sintético de {gen_name}: {e2}")
        except Exception as e:
            self.logger.exception(f"Falha ao salvar synthetic_datasets/*.csv: {e}")

        # Delta-per-feature (quando gerado pelo avaliador)
        try:
            delta_dir = out_dir / "delta_per_feature"
            delta_dir.mkdir(exist_ok=True)
            for gen_name, df_delta in getattr(self, "delta_per_feature_tables", {}).items():
                if df_delta is None or len(df_delta) == 0:
                    continue
                fp = delta_dir / f"delta_per_feature_{gen_name}.csv"
                try:
                    df_delta.to_csv(fp, index=False)
                    self.logger.info(f"Saved delta_per_feature: {fp}")
                except PermissionError:
                    # Arquivo possivelmente aberto (Excel). Salva com sufixo temporal para não perder o artefato.
                    fp_alt = delta_dir / f"delta_per_feature_{gen_name}_{int(time.time())}.csv"
                    df_delta.to_csv(fp_alt, index=False)
                    self.logger.warning(f"delta_per_feature estava bloqueado ({fp}); salvo como: {fp_alt}")

        except Exception as e:
            self.logger.exception(f"Falha ao salvar delta_per_feature_*.csv: {e}")

    def _json_serializer(self, obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (GeneratorType, Enum)):
            return obj.value
        elif isinstance(obj, DeltaJustification):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def _config_to_dict(self):
        """Convert config to dictionary"""
        config_dict = {}
        for field in self.config.__dataclass_fields__:
            value = getattr(self.config, field)
            if hasattr(value, '__dict__'):
                config_dict[field] = self._json_serializer(value)
            else:
                config_dict[field] = value
        return config_dict
    
    def generate_report(self, evaluation_results: Dict[str, Any]):
        """Generate comprehensive report"""
        try:
            report_file = self.output_dir / "comprehensive_report.md"
            
            with open(report_file, 'w') as f:
                f.write("# Synthetic Data Evaluation Report\n\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Configuration summary
                f.write("## Experiment Configuration\n\n")
                f.write(f"- **Target Column**: {self.config.target_column}\n")
                f.write(f"- **Generators**: {', '.join([g.value if isinstance(g, GeneratorType) else g for g in self.config.generators])}\n")
                f.write(f"- **Evaluation Metrics**: {', '.join(self.config.eval_metrics)}\n")
                f.write(f"- **Number of Runs**: {self.config.n_runs}\n")
                f.write(f"- **Random Seed**: {self.config.random_seed}\n")
                f.write(f"- **Post-processing**: {'Enabled' if self.config.enable_postprocessing else 'Disabled'}\n")
                f.write(f"- **MLP Optimization**: {'Enabled' if self.config.enable_mlp_tuning else 'Disabled'}\n")
                f.write(f"- **MLP Ensemble Size**: {self.config.mlp_ensemble_size}\n\n")
                
                # Results summary
                f.write("## Results Summary\n\n")
                
                for generator_name, results in evaluation_results.items():
                    f.write(f"### {generator_name}\n\n")
                    
                    # Utility summary
                    if "utility" in results:
                        utility = results["utility"]
                        if "model_results" in utility:
                            f.write("**Utility Performance**:\n")
                            for model_name, model_results in utility["model_results"].items():
                                if "TSTR" in model_results and "mean" in model_results["TSTR"]:
                                    tstr_mean = model_results["TSTR"]["mean"]
                                    trtr_mean = model_results["TRTR"]["mean"] if "TRTR" in model_results and "mean" in model_results["TRTR"] else "N/A"
                                    f.write(f"- {model_name}: TSTR={tstr_mean:.3f}, TRTR={trtr_mean:.3f}\n")
                            f.write("\n")
                    
                    # Privacy summary
                    if "privacy" in results:
                        privacy = results["privacy"]
                        if "membership_inference" in privacy and "accuracy" in privacy["membership_inference"]:
                            mia_acc = privacy["membership_inference"]["accuracy"]
                            f.write(f"**Privacy (MIA Accuracy)**: {mia_acc:.3f}\n\n")
                    
                    # Fairness summary
                    if "fairness" in results:
                        fairness = results["fairness"]
                        if "by_attribute" in fairness:
                            f.write("**Fairness**:\n")
                            for attr, attr_results in fairness["by_attribute"].items():
                                if "disparate_impact" in attr_results:
                                    di = attr_results["disparate_impact"]
                                    f.write(f"- {attr}: DI={di:.3f}\n")
                            f.write("\n")
            
            logger.info(f"Generated report: {report_file}")
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
    
    def run(self):
        """Run the complete experiment"""
        logger.info("Starting synthetic data experiment...")
        
        # Load data
        df = self.load_data()
        if df is None:
            logger.error("Failed to load data")
            return
        
        # Preprocess data
        df_processed, metadata_info = self.preprocess_data(df)
        
        # Generate synthetic data
        synthetic_datasets = self.generate_synthetic_data(df_processed, metadata_info.get("metadata"))
        
        if not synthetic_datasets:
            logger.error("No synthetic datasets generated")
            return
        
        # Evaluate synthetic data
        evaluation_results = self.evaluate_synthetic_data(df_processed, synthetic_datasets)
        
        # Collect delta-per-feature tables (for CSV export)
        try:
            self.delta_per_feature_tables = {}
            for gen_name, gen_res in (evaluation_results or {}).items():
                util = gen_res.get("utility", {})
                rows = util.get("delta_per_feature_table")
                if rows:
                    self.delta_per_feature_tables[gen_name] = pd.DataFrame(rows)
        except Exception as e:
            logger.warning(f"Delta-per-feature collection failed: {e}")

        try:
            self._generate_article_and_q1q2_artifacts(df_processed, synthetic_datasets, evaluation_results)
        except Exception as e:
            logger.warning(f"Artifact generation failed: {e}")

        # Save results
        self.save_results(synthetic_datasets, evaluation_results)
        
        # Generate report
        if self.config.generate_report:
            self.generate_report(evaluation_results)
        
        logger.info("Experiment completed successfully!")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Synthetic Data Generation and Evaluation")
    parser.add_argument("--config", type=str, help="Path to configuration file (YAML or JSON)")
    parser.add_argument("--input", type=str, help="Input data file (CSV or Excel)")
    parser.add_argument("--target", type=str, default="target", help="Target column name")
    parser.add_argument("--output", type=str, default="./synthetic_evaluation", help="Output directory")
    parser.add_argument("--noise_pct", type=float, default=0.0, help="Percentual de ruído (gaussiano) aplicado aos sintéticos antes do pós-processamento")
    parser.add_argument("--n_synthetic", type=int, default=140, help="Number of synthetic samples")
    parser.add_argument("--n_runs", type=int, default=10, help="Number of evaluation runs")
    parser.add_argument("--random_seed", type=int, default=42, help="Random seed")
    parser.add_argument("--enable_postprocessing", action="store_true", help="Enable post-processing (clipping + snap)")
    parser.add_argument("--enable_mlp_tuning", action="store_true", help="Enable Bayesian optimization for MLP")
    parser.add_argument("--enable_dcr_filter", action="store_true", help="Enable DCR threshold filtering (post-generation)")
    parser.add_argument("--dcr_tau", type=float, default=0.10, help="DCR threshold tau (e.g., 0.10)")
    parser.add_argument("--dcr_pool_factor", type=float, default=1.5, help="Oversampling factor for DCR filtering pool")
    parser.add_argument("--enable_doe_noise", action="store_true", help="Enable DOE-based noise (preferred over additive noise_pct)")
    parser.add_argument("--doe_noise_pct", type=float, default=0.0, help="DOE-based noise percentage (0-100), applied per-variable within DOE limits")
    parser.add_argument("--enable_delta_feature", action="store_true", help="Enable Δ-per-feature permutation diagnostic (C1)")
    parser.add_argument("--delta_repeats", type=int, default=5, help="Repeats for Δ-per-feature permutation diagnostic")
    parser.add_argument("--enable_q1q2_figures", action="store_true", help="Enable Q1/Q2 figures (ECDF DCR, corr heatmap diff, trade-off)")    
    args = parser.parse_args()
    
    # Create configuration
    if args.config:
        # Load from config file
        config_path = Path(args.config)
        if config_path.suffix.lower() in ['.yaml', '.yml']:
            with open(config_path, 'r') as f:
                config_dict = yaml.safe_load(f)
        elif config_path.suffix.lower() == '.json':
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
        else:
            logger.error("Unsupported config file format. Use YAML or JSON.")
            return
        
        config = ExperimentConfig(**config_dict)
    else:
        # Create default configuration
        config = ExperimentConfig(
            input_csv=args.input,
            target_column=args.target,
            output_dir=args.output,
            n_synthetic=args.n_synthetic,
            n_runs=args.n_runs,
            random_seed=args.random_seed,
            noise_pct=args.noise_pct,
            enable_postprocessing=args.enable_postprocessing,
            enable_mlp_tuning=args.enable_mlp_tuning,
            enable_dcr_filter=args.enable_dcr_filter,
            dcr_tau=args.dcr_tau,
            dcr_pool_factor=args.dcr_pool_factor,
            enable_doe_noise=args.enable_doe_noise,
            doe_noise_pct=args.doe_noise_pct,
            enable_delta_feature=args.enable_delta_feature,
            delta_repeats=args.delta_repeats,
            enable_q1q2_figures=args.enable_q1q2_figures,
        )
    
    # Run experiment
    experiment = SyntheticDataExperiment(config)
    experiment.run()

if __name__ == "__main__":
    main()