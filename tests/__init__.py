# tests/__init__.py

import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import our components
from abstract_annotation.components import (
    DataLoaderComponent,
    BatchProcessorComponent,
    AnnotatorComponent,
    EvaluatorComponent
)

# Test data paths
TEST_DATA_DIR = PROJECT_ROOT / "data"
GROUND_TRUTH_DIR = TEST_DATA_DIR / "ground_truth"
UNANNOTATED_DIR = TEST_DATA_DIR / "unannotated"

__all__ = [
    "DataLoaderComponent",
    "BatchProcessorComponent",
    "AnnotatorComponent",
    "EvaluatorComponent",
    "GROUND_TRUTH_DIR",
    "UNANNOTATED_DIR"
]