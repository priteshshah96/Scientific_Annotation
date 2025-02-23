# tests/test_loader.py

import pytest
from abstract_annotation.components import DataLoaderComponent
from . import GROUND_TRUTH_DIR

@pytest.fixture
def data_loader():
    return DataLoaderComponent()

def test_loader_initialization(data_loader):
    """Test if data loader can be initialized"""
    assert data_loader is not None
    assert hasattr(data_loader, 'process')

def test_ground_truth_discovery(data_loader):
    """Test if loader can discover annotators"""
    result = data_loader.process(
        ground_truth_dir=str(GROUND_TRUTH_DIR),
        include_dh=True
    )
    
    assert 'annotators' in result
    assert len(result['annotators']) >= 2  # At least Sumedh and Tiya
    assert 'Sumedh' in result['annotators']
    assert 'Tiya' in result['annotators']

def test_annotation_loading(data_loader):
    """Test if annotations are loaded correctly"""
    result = data_loader.process(
        ground_truth_dir=str(GROUND_TRUTH_DIR),
        include_dh=True
    )
    
    assert 'annotations' in result
    assert result['annotations']  # Should not be empty