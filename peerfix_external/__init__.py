"""Post-freeze PEERFIX external-validation adapters.

This namespace may map external experimental designs into the frozen PEERFIX-Core
contract. It must not modify the frozen Core implementation or retune Core rules.
"""

from .icd_design import evaluate_design_icd_matched_n, fit_design_model

__all__ = ["evaluate_design_icd_matched_n", "fit_design_model"]
