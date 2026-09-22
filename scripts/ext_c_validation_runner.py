from __future__ import annotations

from scripts import external_validation_runner as base

FACTORS = ["z1_glycerol", "z2_olive_oil", "z3_hexadecane", "z4_glucose"]
CSV = "data/external/ext_c_fontes_carbon_2pow4.csv"
CSV_SHA256 = "41dba19fe743147ab249951c2e388a2f6c0647fa55af7b306e7fe54223f2f5d2"
ADAPTER = "config/external/03_ADAPTER_FONTES_EXT_C.yaml"

base.DATASETS.update({
    "ext_c_ei": {
        "csv": CSV,
        "csv_sha256": CSV_SHA256,
        "adapter": ADAPTER,
        "n": 19,
        "factors": FACTORS,
        "target": "EI_pct",
        "reference_terms": [
            "z1_glycerol",
            "z2_olive_oil",
            "z4_glucose",
            "z1_glycerol:z2_olive_oil",
            "z1_glycerol:z4_glucose",
            "z2_olive_oil:z4_glucose",
            "z3_hexadecane:z4_glucose",
        ],
        "include_quadratic": False,
        "modelability": "PASS",
    },
    "ext_c_dst": {
        "csv": CSV,
        "csv_sha256": CSV_SHA256,
        "adapter": ADAPTER,
        "n": 19,
        "factors": FACTORS,
        "target": "delta_ST_mNm",
        "reference_terms": [
            "z1_glycerol",
            "z2_olive_oil",
            "z3_hexadecane",
            "z4_glucose",
            "z1_glycerol:z4_glucose",
            "z2_olive_oil:z3_hexadecane",
        ],
        "include_quadratic": False,
        "modelability": "PASS",
    },
})

if __name__ == "__main__":
    base.main()
