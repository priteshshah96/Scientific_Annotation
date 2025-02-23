# main.py
import os
import argparse
from abstract_annotation.app import main as start_langflow

def parse_args():
    parser = argparse.ArgumentParser(description='Abstract Annotation Pipeline')
    
    parser.add_argument(
        '--host',
        type=str,
        default="0.0.0.0",
        help='Host to run the LangFlow server'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=7860,
        help='Port to run the LangFlow server'
    )
    
    parser.add_argument(
        '--dev',
        action='store_true',
        help='Run in development mode'
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Set environment variables
    os.environ["LANGFLOW_HOST"] = args.host
    os.environ["LANGFLOW_PORT"] = str(args.port)
    
    if args.dev:
        os.environ["LANGFLOW_DEV"] = "true"
    
    # Start LangFlow
    start_langflow()