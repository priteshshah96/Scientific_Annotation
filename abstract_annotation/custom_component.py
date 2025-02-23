# langflow/custom_component.py
from abstract_annotation.interface.custom_component import CustomComponent as LangflowCustomComponent

class CustomComponent(LangflowCustomComponent):
    """Base class for all custom components"""
    
    @staticmethod
    def add_component(component_class):
        """Register a new component"""
        LangflowCustomComponent.add_component(component_class)