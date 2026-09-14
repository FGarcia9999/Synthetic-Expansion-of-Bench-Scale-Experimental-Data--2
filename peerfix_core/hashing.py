from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_dataframe_csv(df: pd.DataFrame) -> str:
    """Return the exact canonical CSV representation used by PEERFIX hashes."""
    return df.to_csv(index=False, lineterminator="\n", float_format="%.17g")


def hash_dataframe(df: pd.DataFrame) -> str:
    return sha256_text(canonical_dataframe_csv(df))


def persist_dataframe_canonical(df: pd.DataFrame, path: str | Path) -> str:
    """Persist exactly the text that is hashed and return its SHA-256 digest.

    The explicit ``newline=''`` prevents platform newline translation, so the bytes
    persisted on disk are the same UTF-8 bytes covered by ``hash_dataframe``.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = canonical_dataframe_csv(df)
    with path.open("w", encoding="utf-8", newline="") as f:
        f.write(text)
    digest = sha256_text(text)
    if sha256_file(path) != digest:
        raise RuntimeError(f"canonical dataframe persistence hash mismatch: {path}")
    return digest


def read_dataframe_canonical(path: str | Path) -> pd.DataFrame:
    """Reload a canonical CSV using pandas round-trip float parsing."""
    return pd.read_csv(Path(path), float_precision="round_trip")


def canonical_json_hash(obj: Any) -> str:
    text = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return sha256_text(text)
