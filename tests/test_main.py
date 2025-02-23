# tests/test_main.py

import logging
from pathlib import Path
from abstract_annotation.components import (
    DataLoaderComponent,
    BatchProcessorComponent,
    AnnotatorComponent,
    EvaluatorComponent
)
from . import GROUND_TRUTH_DIR, TEST_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_full_pipeline():
    """Test the entire pipeline"""
    try:
        # Initialize components
        data_loader = DataLoaderComponent()
        batch_processor = BatchProcessorComponent()
        annotator = AnnotatorComponent()
        evaluator = EvaluatorComponent()

        logger.info("Testing full pipeline...")

        # Load data
        load_result = data_loader.process(
            ground_truth_dir=str(GROUND_TRUTH_DIR),
            **TEST_CONFIG
        )
        
        logger.info(f"Found {len(load_result['annotators'])} annotators")
        for annotator_name in load_result['annotators']:
            logger.info(f"  - {annotator_name}")

        if 'stats' in load_result:
            stats = load_result['stats']
            logger.info("\nAnnotation Statistics:")
            logger.info(f"Total Papers: {stats['papers']['total_unique']}")
            logger.info(f"Total Annotators: {stats['annotators']['total']}")

        return load_result

    except Exception as e:
        logger.error(f"Pipeline test failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_full_pipeline()