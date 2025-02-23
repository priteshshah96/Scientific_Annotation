# tests/test_batch_processor.py

import pytest
from abstract_annotation.components import BatchProcessorComponent, DataLoaderComponent
from . import GROUND_TRUTH_DIR, TEST_CONFIG

@pytest.fixture
def batch_processor():
    """Create batch processor instance"""
    return BatchProcessorComponent()

@pytest.fixture
def sample_data():
    """Get sample data for batch processing"""
    loader = DataLoaderComponent()
    return loader.process(
        ground_truth_dir=str(GROUND_TRUTH_DIR),
        include_dh=True
    )

def test_processor_initialization(batch_processor):
    """Test if batch processor can be initialized"""
    assert batch_processor is not None
    assert hasattr(batch_processor, 'process')

def test_batch_creation(batch_processor, sample_data):
    """Test batch creation from annotations"""
    result = batch_processor.process(
        annotations=sample_data['annotations'],
        batch_size=5
    )
    
    assert 'batches' in result
    assert isinstance(result['batches'], list)
    
    # Check batch sizes
    for batch in result['batches']:
        assert len(batch) <= 5  # Should not exceed batch size

def test_token_limit_handling(batch_processor, sample_data):
    """Test handling of token limits"""
    result = batch_processor.process(
        annotations=sample_data['annotations'],
        batch_size=5,
        max_tokens=1000  # Set small token limit
    )
    
    for batch in result['batches']:
        total_tokens = sum(len(ann['text'].split()) for ann in batch)
        assert total_tokens <= 1000  # Should not exceed token limit

def test_batch_stats(batch_processor, sample_data):
    """Test batch statistics generation"""
    result = batch_processor.process(
        annotations=sample_data['annotations'],
        batch_size=5,
        show_stats=True
    )
    
    assert 'stats' in result
    stats = result['stats']
    
    assert 'total_batches' in stats
    assert 'average_batch_size' in stats
    assert 'total_annotations' in stats

def test_error_handling(batch_processor):
    """Test error handling for invalid inputs"""
    with pytest.raises(Exception):
        batch_processor.process(
            annotations={},  # Empty annotations
            batch_size=5
        )