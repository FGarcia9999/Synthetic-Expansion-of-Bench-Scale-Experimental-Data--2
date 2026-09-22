from __future__ import annotations

from scripts import external_audit as base

CSV_SHA256 = "41dba19fe743147ab249951c2e388a2f6c0647fa55af7b306e7fe54223f2f5d2"

base.EXPECTED_HASH.update({
    "ext_c_ei": CSV_SHA256,
    "ext_c_dst": CSV_SHA256,
})
base.EXPECTED_N.update({
    "ext_c_ei": 19,
    "ext_c_dst": 19,
})

if __name__ == "__main__":
    base.main()
