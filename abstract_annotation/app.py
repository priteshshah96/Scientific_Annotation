# langflow/app.py
from langflow.interface.utils import launch_langflow
from abstract_annotation.interface.settings import Settings
import os

# Import our components
from abstract_annotation.components import (
    DataLoaderComponent,
    BatchProcessorComponent,
    AnnotatorComponent,
    EvaluatorComponent
)

def register_components():
    """Register all custom components"""
    components = [
        DataLoaderComponent,
        BatchProcessorComponent,
        AnnotatorComponent,
        EvaluatorComponent
    ]
    
    for component in components:
        component.add_component(component)

def setup_settings():
    """Setup LangFlow settings"""
    return Settings(
        dev=True,
        host=os.getenv("LANGFLOW_HOST", "0.0.0.0"),
        port=int(os.getenv("LANGFLOW_PORT", "7860")),
        remove_api_keys=False,
        cache_folder="./cache",
        flow_folder="./flows"
    )

def main():
    """Main function to start LangFlow"""
    try:
        # Register our components
        register_components()
        
        # Setup settings
        settings = setup_settings()
        
        # Launch the app
        launch_langflow(
            settings=settings,
            open_browser=True,
            auth=False,
        )
        
    except Exception as e:
        print(f"Error starting LangFlow: {str(e)}")
        raise