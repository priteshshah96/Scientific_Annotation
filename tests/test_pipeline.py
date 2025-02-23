# tests/test_pipeline.py

import pytest
from abstract_annotation.components import (
    DataLoaderComponent,
    BatchProcessorComponent,
    AnnotatorComponent,
    EvaluatorComponent
)
from . import GROUND_TRUTH_DIR, TEST_CONFIG

@pytest.fixture
def pipeline_components():
    """Create all pipeline components"""
    return {
        'loader': DataLoaderComponent(),
        'processor': BatchProcessorComponent(),
        'annotator': AnnotatorComponent(),
        'evaluator': EvaluatorComponent()
    }

def test_full_pipeline(pipeline_components):
    """Test full pipeline execution"""
    # Load data
    load_result = pipeline_components['loader'].process(
        ground_truth_dir=str(GROUND_TRUTH_DIR),
        include_dh=True
    )
    assert 'annotations' in load_result
    
    # Create batches
    batch_result = pipeline_components['processor'].process(
        annotations=load_result['annotations'],
        batch_size=5
    )
    assert 'batches' in batch_result
    
    # Run annotation
    annotation_result = pipeline_components['annotator'].process(
        batches=batch_result['batches']
    )
    assert 'results' in annotation_result
    
    # Evaluate results
    eval_result = pipeline_components['evaluator'].process(
        predictions=annotation_result['results'],
        ground_truth=load_result['annotations']
    )
    assert 'metrics' in eval_result

def test_component_integration(pipeline_components):
    """Test if components can work together"""
    # Test loader -> processor
    load_result = pipeline_components['loader'].process(
        ground_truth_dir=str(GROUND_TRUTH_DIR),
        include_dh=True
    )
    
    assert pipeline_components['processor'].process(
        annotations=load_result['annotations'],
        batch_size=5
    ) is not None
    
    # Test processor -> annotator
    batch_result = pipeline_components['processor'].process(
        annotations=load_result['annotations'],
        batch_size=5
    )
    
    assert pipeline_components['annotator'].process(
        batches=batch_result['batches']
    ) is not None

def test_error_propagation(pipeline_components):
    """Test how errors propagate through pipeline"""
    with pytest.raises(Exception):
        # Start with invalid data
        load_result = pipeline_components['loader'].process(
            ground_truth_dir="invalid/path",
            include_dh=True
        )