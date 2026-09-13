"""PEERFIX-Core v1.0 pre-freeze implementation primitives."""

from .seeds import derive_seed
from .splits import repeated_row_kfold, repeated_group_condition_kfold
from .utility import evaluate_generator_utility, default_regression_models
from .icd import evaluate_icd_matched_n
from .dcr import compute_dcr
from .generators import GeneratorSpec, available_generators, build_generator, seed_everything
from .tabddpm import SmallNTabDDPM, TabDDPMConfig

__all__ = [
    "derive_seed",
    "repeated_row_kfold", "repeated_group_condition_kfold",
    "evaluate_generator_utility", "default_regression_models",
    "evaluate_icd_matched_n",
    "compute_dcr",
    "GeneratorSpec", "available_generators", "build_generator", "seed_everything",
    "SmallNTabDDPM", "TabDDPMConfig",
]

__version__ = "1.0.0-pre.1"
