from __future__ import annotations

import hashlib
import json
from typing import Any

import pandas as pd


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_dataframe(df: pd.DataFrame) -> str:
    canonical = df.to_csv(index=False, lineterminator="\n", float_format="%.17g")
    return sha256_text(canonical)


def canonical_json_hash(obj: Any) -> str:
    text = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return sha256_text(text)
