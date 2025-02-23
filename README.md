# Scientific Abstract Annotation Pipeline

A tool for automating the annotation of scientific abstracts using both API-based and open-source language models. Supports event extraction, argument mining, and performance evaluation.

## Features

- **Multiple Model Support**: Use both API models (GPT, Claude) and open-source models
- **Remote Model Storage**: Cache models for faster subsequent runs
- **Evaluation System**: Compare model outputs against ground truth
- **Cost Tracking**: Monitor API usage and costs
- **Web Interface**: Upload documents and view results via Streamlit

## Project Structure

```
Scientific_Annotation/              # Root directory                        
│
├── src/                         
│   ├── __init__.py
│   │
│   ├── pipeline/               
│   │   ├── __init__.py
│   │   ├── processor.py        # Data processing pipeline
│   │   └── schema.py           # Data models
│   │
│   ├── models/                 
│   │   ├── __init__.py
│   │   ├── base.py            # Base model interface
│   │   ├── api_models.py      # GPT/Claude implementations
│   │   └── local_models.py    # Local model implementations
│   │
│   └── utils/                 
│       ├── __init__.py
│       └── helpers.py
│
├── langflow/                   # LangFlow specific code
│   ├── __init__.py
│   ├── components/            # Custom LangFlow components
│   │   ├── __init__.py
│   │   ├── data_loader.py    # Data loading component
│   │   ├── batch_processor.py # Batch processing component
│   │   ├── annotator.py      # Annotation component
│   │   └── evaluator.py      # Evaluation component
│   │
│   ├── flows/                # Saved flow configurations
│   │   └── default_flow.json
│   │
│   └── app.py               # LangFlow server setup
│
├── data/                    # Data files
│   ├── raw/                # Input JSONs
│   ├── processed/          # Processed data
│   └── output/             # Results
│
├── tests/                  
│   ├── __init__.py
│   ├── test_pipeline.py
│   └── test_components.py
│
├── configs/                
│   ├── models.yaml
│   └── pipeline.yaml
│
├── main.py                 # Main entry point to run LangFlow
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/abstract-annotation.git
cd abstract-annotation
```

2. Create and activate conda environment:
```bash
conda create -n abstract_env python=3.10
conda activate abstract_env
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up configuration:
```bash
cp config/example.yaml config/config.yaml
# Edit config.yaml with your API keys and settings
```

## Usage

1. Start the web interface:
```bash
streamlit run src/interface/app.py
```

2. Run from command line:
```bash
python src/main.py --input data/raw/abstracts.json --model gpt-4
```

3. Evaluate results:
```bash
python src/evaluate.py --predictions output/results.json --ground-truth data/annotated/
```

## Core Components

### Model Manager
- Handles both API and open-source models
- Implements caching and version control
- Manages model configurations

```python
from src.models import ModelManager

manager = ModelManager(config_path="config/models.yaml")
model = manager.get_model("gpt-4")
```

### Pipeline
- Processes JSON input
- Extracts events and arguments
- Validates output structure

```python
from src.pipeline import AnnotationPipeline

pipeline = AnnotationPipeline(model=model)
results = pipeline.process(abstract_text)
```

### Evaluator
- Compares against ground truth
- Calculates performance metrics
- Tracks costs and usage

```python
from src.evaluation import Evaluator

evaluator = Evaluator()
metrics = evaluator.evaluate(predictions, ground_truth)
```

## Configuration

Example `config.yaml`:
```yaml
models:
  gpt-4:
    api_key: ${OPENAI_API_KEY}
    cache_dir: "cache/gpt4/"
  claude:
    api_key: ${ANTHROPIC_API_KEY}
    cache_dir: "cache/claude/"

evaluation:
  metrics:
    - accuracy
    - f1_score
  cost_tracking: true

storage:
  remote_url: "s3://your-bucket/models/"
  local_cache: "cache/"
```

## Development

1. Install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest tests/
```

3. Format code:
```bash
black src/
flake8 src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details