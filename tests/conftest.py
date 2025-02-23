# tests/conftest.py

import pytest
from pathlib import Path
from . import GROUND_TRUTH_DIR, UNANNOTATED_DIR

@pytest.fixture(scope="session")
def ground_truth_dir():
    """Provide ground truth directory"""
    return GROUND_TRUTH_DIR

@pytest.fixture(scope="session")
def unannotated_dir():
    """Provide unannotated data directory"""
    return UNANNOTATED_DIR