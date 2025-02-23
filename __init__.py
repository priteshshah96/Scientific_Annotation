# __init__.py

from abstract_annotation.components import (
    DataLoaderComponent,
    BatchProcessorComponent,
    AnnotatorComponent,
    EvaluatorComponent,
    components
)

# Version info
__version__ = "0.1.0"

# Components available at package level
__all__ = [
    "DataLoaderComponent",
    "BatchProcessorComponent",
    "AnnotatorComponent",
    "EvaluatorComponent",
    "components"  # Dictionary of components for registration
]

def get_components():
    """Get all available components"""
    return components

def get_component(name: str):
    """Get a specific component by name"""
    return components.get(name)

def list_components():
    """List all available component names"""
    return list(components.keys())

# Package metadata
__author__ = "Pritesh shah"
__email__ = "priteshshahwork@gmail.com"
__description__ = "Scientific Abstract Annotation Pipeline"