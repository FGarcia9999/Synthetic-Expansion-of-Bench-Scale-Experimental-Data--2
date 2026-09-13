from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from .hashing import sha256_file


GATE04_BASE_PROTOCOL = Path("config/PEERFIX_CORE_v1.0_PRE_FREEZE_REV2.yaml")
GATE04_AMENDMENT = Path("config/PEERFIX_CORE_v1.0_PRE_FREEZE_REV3_AMENDMENT.yaml")
EXPECTED_LABEL = "PEERFIX_CORE_v1.0_PRE_FREEZE_REV3"


def combined_protocol_sha256(base_path: str | Path, amendment_path: str | Path) -> str:
    """Hash the executable Gate 0.4 protocol pair in declared order."""
    base = Path(base_path).read_bytes()
    amendment = Path(amendment_path).read_bytes()
    return hashlib.sha256(base + b"\n" + amendment).hexdigest()


def _load_yaml(path: Path) -> dict[str, Any]:
    obj = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError(f"protocol file is not a mapping: {path}")
    return obj


def validate_gate04_preflight(repo_root: str | Path = ".") -> dict[str, Any]:
    """Fail closed unless the authorized dataset and REV2+REV3 protocol are intact."""
    root = Path(repo_root)
    base_path = root / GATE04_BASE_PROTOCOL
    amendment_path = root / GATE04_AMENDMENT
    if not base_path.is_file() or not amendment_path.is_file():
        raise RuntimeError("Gate 0.4 protocol pair is incomplete")

    base = _load_yaml(base_path)
    amendment = _load_yaml(amendment_path)
    proto = base.get("protocol", {})
    am = amendment.get("protocol_amendment", {})
    if proto.get("id") != "PEERFIX_CORE_v1.0_PRE_FREEZE_REV2":
        raise RuntimeError("unexpected Gate 0.4 base protocol id")
    if am.get("id") != EXPECTED_LABEL:
        raise RuntimeError("unexpected Gate 0.4 amendment id")
    if am.get("extends") != str(GATE04_BASE_PROTOCOL):
        raise RuntimeError("REV3 amendment does not extend the expected REV2 file")

    provenance = base.get("provenance", {}).get("derivation_dataset", {})
    data_rel = Path(str(provenance.get("path", "")))
    data_path = root / data_rel
    if not data_path.is_file():
        raise RuntimeError(f"authorized derivation dataset missing: {data_rel}")
    expected_data_sha = str(provenance.get("sha256", ""))
    actual_data_sha = sha256_file(data_path)
    if actual_data_sha != expected_data_sha:
        raise RuntimeError(
            f"authorized derivation dataset hash mismatch: {actual_data_sha} != {expected_data_sha}"
        )

    df = pd.read_csv(data_path)
    expected_n = int(provenance.get("n_rows", -1))
    if len(df) != expected_n:
        raise RuntimeError(f"derivation row count mismatch: {len(df)} != {expected_n}")
    factors = list(provenance.get("factors", []))
    target = str(provenance.get("target", ""))
    expected_cols = factors + [target]
    if list(df.columns) != expected_cols:
        raise RuntimeError(
            f"derivation schema mismatch: {list(df.columns)} != {expected_cols}"
        )
    if not df.apply(pd.to_numeric, errors="coerce").notna().all().all():
        raise RuntimeError("derivation dataset contains non-numeric or missing canonical values")

    sensitivity = amendment.get("historical_sensitivity_override", {}).get("clean_core_semantics", {})
    if sensitivity.get("perturbed_columns") != [target]:
        raise RuntimeError("REV3 sensitivity must perturb only the declared derivation response")
    if sensitivity.get("target_clipping_to_observed_range") is not False:
        raise RuntimeError("REV3 sensitivity target clipping must remain disabled")
    if float(sensitivity.get("percent", -1.0)) != 1.0:
        raise RuntimeError("REV3 historical sensitivity percent must remain 1.0")

    external_block = base.get("freeze_gates", {}).get(
        "external_confirmatory_execution_before_gate_0_5"
    )
    amendment_block = amendment.get("freeze_gates_override", {}).get(
        "external_confirmatory_execution_before_gate_0_5"
    )
    if external_block != "prohibited" or amendment_block != "prohibited":
        raise RuntimeError("external confirmatory execution prohibition is not intact")

    protocol_sha = combined_protocol_sha256(base_path, amendment_path)
    return {
        "protocol_label": EXPECTED_LABEL,
        "protocol_sha256": protocol_sha,
        "base_protocol_path": str(GATE04_BASE_PROTOCOL),
        "base_protocol_sha256": sha256_file(base_path),
        "amendment_path": str(GATE04_AMENDMENT),
        "amendment_sha256": sha256_file(amendment_path),
        "dataset_path": str(data_rel),
        "dataset_sha256": actual_data_sha,
        "n_rows": len(df),
        "factors": factors,
        "target": target,
        "status": "PASS",
    }
