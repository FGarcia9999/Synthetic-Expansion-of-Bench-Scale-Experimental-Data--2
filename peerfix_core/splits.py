from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator

import numpy as np
from sklearn.model_selection import RepeatedKFold

from .seeds import derive_seed


@dataclass(frozen=True)
class SplitRecord:
    repeat: int
    fold: int
    train_idx: np.ndarray
    test_idx: np.ndarray


def repeated_row_kfold(
    n_rows: int,
    *,
    n_splits: int = 5,
    n_repeats: int = 10,
    seed: int = 123,
) -> Iterator[SplitRecord]:
    if n_rows < n_splits:
        raise ValueError("n_rows must be >= n_splits")
    rkf = RepeatedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=seed)
    X = np.zeros((n_rows, 1), dtype=float)
    for k, (tr, te) in enumerate(rkf.split(X)):
        repeat = k // n_splits + 1
        fold = k % n_splits + 1
        yield SplitRecord(repeat, fold, np.asarray(tr, int), np.asarray(te, int))


def repeated_group_condition_kfold(
    groups: Iterable[object],
    *,
    n_splits: int = 5,
    n_repeats: int = 10,
    master_seed: int = 123,
) -> Iterator[SplitRecord]:
    """Repeated grouped CV with deterministic load-balanced group assignment.

    Each unique group is wholly assigned to exactly one test fold per repeat.
    Assignment is randomized deterministically, then greedily balanced by row count.
    """
    groups = np.asarray(list(groups), dtype=object)
    if groups.ndim != 1:
        raise ValueError("groups must be one-dimensional")
    unique = list(dict.fromkeys(groups.tolist()))
    if len(unique) < n_splits:
        raise ValueError("number of unique groups must be >= n_splits")

    group_to_indices = {g: np.flatnonzero(groups == g) for g in unique}
    for repeat in range(1, n_repeats + 1):
        rng = np.random.default_rng(
            derive_seed(master_seed, purpose="group_split", repeat=repeat)
        )
        tie = {g: float(rng.random()) for g in unique}
        ordered = sorted(unique, key=lambda g: (-len(group_to_indices[g]), tie[g]))
        fold_groups: list[list[object]] = [[] for _ in range(n_splits)]
        fold_load = [0] * n_splits
        for g in ordered:
            min_load = min(fold_load)
            candidate_folds = [i for i, load in enumerate(fold_load) if load == min_load]
            chosen = int(rng.choice(candidate_folds))
            fold_groups[chosen].append(g)
            fold_load[chosen] += len(group_to_indices[g])

        all_idx = np.arange(len(groups), dtype=int)
        for fold, gs in enumerate(fold_groups, start=1):
            mask = np.isin(groups, np.asarray(gs, dtype=object))
            test_idx = all_idx[mask]
            train_idx = all_idx[~mask]
            if np.intersect1d(train_idx, test_idx).size:
                raise RuntimeError("group split overlap")
            yield SplitRecord(repeat, fold, train_idx, test_idx)
