# langflow/components/__init__.py

from .data_loader import DataLoaderComponent
from .batch_processor import BatchProcessorComponent
from .annotator import AnnotatorComponent
from .evaluator import EvaluatorComponent

# List all available components
COMPONENTS_LIST = [
    DataLoaderComponent,
    BatchProcessorComponent,
    AnnotatorComponent,
    EvaluatorComponent
]

# Dict mapping component names to their classes
COMPONENTS = {
    "DataLoader": DataLoaderComponent,
    "BatchProcessor": BatchProcessorComponent,
    "Annotator": AnnotatorComponent,
    "Evaluator": EvaluatorComponent
}

# Version info
__version__ = "0.1.0"

# Make components available at package level
__all__ = [
    "DataLoaderComponent",
    "BatchProcessorComponent",
    "AnnotatorComponent",
    "EvaluatorComponent",
    "COMPONENTS_LIST",
    "COMPONENTS"
]

def get_component(name: str):
    """Get component class by name"""
    return COMPONENTS.get(name)

def list_components():
    """List all available components"""
    return list(COMPONENTS.keys())