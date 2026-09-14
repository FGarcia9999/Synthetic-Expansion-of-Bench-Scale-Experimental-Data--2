from __future__ import annotations

import argparse
import json
from pathlib import Path

from peerfix_core.provenance import (
    finalize_full_realisations_directory,
    finalize_utility_directory,
)


def _write_report(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(json.dumps({"status": "PASS", "entries": rows}, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["utility", "full_realisations"], required=True)
    parser.add_argument("--root", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        raise SystemExit(f"missing provenance root: {root}")

    rows: list[dict[str, object]] = []
    if args.phase == "utility":
        completion_files = sorted(root.glob("*/*/*/completion.json"))
        if len(completion_files) != 16:
            raise RuntimeError(f"expected 16 utility combinations, found {len(completion_files)}")
        for completion in completion_files:
            rows.append(finalize_utility_directory(completion.parent))
        if any(int(row["prediction_groups"]) != 600 for row in rows):
            raise RuntimeError("utility provenance expected 600 prediction groups per combination")
    else:
        completion_files = sorted(root.glob("*/*/completion.json"))
        if len(completion_files) != 8:
            raise RuntimeError(f"expected 8 full-realisation combinations, found {len(completion_files)}")
        for completion in completion_files:
            rows.append(finalize_full_realisations_directory(completion.parent))
        if any(int(row["realisations"]) != 10 for row in rows):
            raise RuntimeError("full-realisation provenance expected 10 realisations per combination")
        if any(int(row["unique_synthetic_hashes"]) != 10 for row in rows):
            raise RuntimeError("full-realisation provenance requires 10 unique synthetic hashes")

    _write_report(root / "provenance_roundtrip_report.json", rows)
    print(json.dumps({"status": "PASS", "phase": args.phase, "entries": len(rows)}))


if __name__ == "__main__":
    main()
