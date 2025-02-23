# langflow/components/annotator.py

from abstract_annotation import CustomComponent
from typing import Dict, List, Any
from langchain.chat_models import ChatOpenAI, ChatAnthropic
from transformers import pipeline
import torch
import json

class AnnotatorComponent(CustomComponent):
    """Component for annotating abstracts using different models"""
    
    display_name: str = "Abstract Annotator"
    description: str = "Annotates scientific abstracts using selected model"

    def build_config(self):
        return {
            "model_type": {
                "display_name": "Model Type",
                "type": "select",
                "options": ["api", "small_model"],
                "value": "api",
                "required": True,
                "info": "Type of model to use"
            },
            "model_name": {
                "display_name": "Model Name",
                "type": "select",
                "options": [
                    # API Models
                    "gpt-3.5-turbo",
                    "gpt-4",
                    "claude-3-sonnet",
                    # Local Models
                    "flan-t5-large",
                    "llama-2-7b"
                ],
                "value": "gpt-3.5-turbo",
                "required": True,
                "info": "Specific model to use"
            },
            "api_key": {
                "display_name": "API Key",
                "type": "password",
                "required": False,
                "show_if": {
                    "model_name": ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"]
                },
                "info": "API key for selected model"
            },
            "temperature": {
                "display_name": "Temperature",
                "type": "number",
                "value": 0.0,
                "min": 0.0,
                "max": 1.0,
                "step": 0.1,
                "required": False,
                "info": "Model temperature (randomness)"
            }
        }

    def initialize_model(self, model_name: str, api_key: str = None):
        """Initialize the selected model"""
        if model_name in ["gpt-3.5-turbo", "gpt-4"]:
            return ChatOpenAI(
                model=model_name,
                openai_api_key=api_key,
                temperature=self.temperature
            )
        elif "claude" in model_name:
            return ChatAnthropic(
                model=model_name,
                anthropic_api_key=api_key,
                temperature=self.temperature
            )
        else:
            # Initialize local models
            device = "cuda" if torch.cuda.is_available() else "cpu"
            return pipeline(
                "text2text-generation",
                model=model_name,
                device=device
            )

    def get_prompt(self, event_type: str, text: str) -> str:
        """Generate prompt for annotation"""
        return f"""Analyze this scientific abstract segment and provide structured annotation.

Event Type: {event_type}
Text: {text}

Instructions:
1. Generate a brief summary (3-7 words) of this segment
2. Identify the main action (primary verb)
3. Extract arguments from the text using these categories:
   - Agent: Who/what performs the action
   - Object: Primary and secondary objects with modifiers
   - Context: Background information
   - Purpose: Goals or objectives
   - Method: Approaches used
   - Results: Outcomes found
   - Analysis: Interpretations
   - Challenge: Problems/issues
   - Ethical: Ethical considerations
   - Implications: Consequences
   - Contradictions: Conflicting elements

Format your response as a JSON object:
{{
    "summary": "brief summary here",
    "main_action": "primary verb",
    "arguments": {{
        "Agent": ["list", "of", "agents"],
        "Object": {{
            "Primary_Object": ["main objects"],
            "Primary_Modifier": ["modifiers"],
            "Secondary_Object": ["other objects"],
            "Secondary_Modifier": ["other modifiers"]
        }},
        "Context": ["list", "of", "context"],
        "Purpose": ["list", "of", "purposes"],
        "Method": ["list", "of", "methods"],
        "Results": ["list", "of", "results"],
        "Analysis": ["list", "of", "analysis"],
        "Challenge": ["list", "of", "challenges"],
        "Ethical": ["list", "of", "considerations"],
        "Implications": ["list", "of", "implications"],
        "Contradictions": ["list", "of", "contradictions"]
    }}
}}"""

    async def process_batch(self, model, batch: List[Dict]) -> List[Dict]:
        """Process a batch of events"""
        results = []
        for event in batch:
            prompt = self.get_prompt(event['event_type'], event['text'])
            
            try:
                if isinstance(model, (ChatOpenAI, ChatAnthropic)):
                    response = await model.apredict(prompt)
                    annotation = json.loads(response)
                else:
                    # Handle local models
                    response = model(prompt, max_length=1000)
                    annotation = json.loads(response[0]['generated_text'])
                
                results.append({
                    'paper_code': event['paper_code'],
                    'event_type': event['event_type'],
                    'annotation': annotation
                })
                
            except Exception as e:
                print(f"Error processing event: {str(e)}")
                results.append({
                    'paper_code': event['paper_code'],
                    'event_type': event['event_type'],
                    'error': str(e)
                })
                
        return results

    async def process(
        self,
        batches: List[List[Dict]],
        model_type: str,
        model_name: str,
        api_key: str = None,
        temperature: float = 0.0
    ) -> Dict[str, Any]:
        """Process all batches"""
        try:
            self.temperature = temperature
            model = self.initialize_model(model_name, api_key)
            
            all_results = []
            errors = []
            
            for batch in batches:
                try:
                    batch_results = await self.process_batch(model, batch)
                    all_results.extend(batch_results)
                except Exception as e:
                    errors.append(str(e))
            
            return {
                "annotations": all_results,
                "stats": {
                    "total_processed": len(all_results),
                    "successful": len([r for r in all_results if 'error' not in r]),
                    "failed": len([r for r in all_results if 'error' in r]),
                    "errors": errors
                }
            }
            
        except Exception as e:
            raise Exception(f"Error in annotation process: {str(e)}")