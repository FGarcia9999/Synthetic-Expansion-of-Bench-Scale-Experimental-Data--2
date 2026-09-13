from __future__ import annotations

import hashlib


def derive_seed(
    master: int,
    *,
    purpose: str,
    scenario: str = "",
    repeat: int | str = "",
    fold: int | str = "",
    generator: str = "",
    realisation: int | str = "",
    model: str = "",
) -> int:
    """Derive a deterministic positive 31-bit seed from a stable token string."""
    token = f"{master}|{purpose}|{scenario}|{repeat}|{fold}|{generator}|{realisation}|{model}"
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    seed = int.from_bytes(digest[:4], "big") & 0x7FFFFFFF
    return seed or 1
