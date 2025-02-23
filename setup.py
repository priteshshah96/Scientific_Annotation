# setup.py
from setuptools import setup, find_packages

setup(
    name="scientific_annotation",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langflow",
        "langchain",
        "openai",
        "anthropic",
        "transformers",
        "torch",
        "sentence-transformers",
        "numpy",
        "scikit-learn",
        "pandas",
        "pydantic",
        "tqdm",
        "plotly"
    ],
)