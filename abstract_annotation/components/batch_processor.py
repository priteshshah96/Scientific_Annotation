# langflow/components/batch_processor.py

from abstract_annotation import CustomComponent
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class Event:
    event_type: str
    text: str
    paper_code: str

class BatchProcessorComponent(CustomComponent):
    """Component for creating optimized batches for processing"""
    
    display_name: str = "Abstract Batch Processor"
    description: str = "Creates optimized batches of events for processing"

    def build_config(self):
        return {
            "model_type": {
                "display_name": "Model Type",
                "type": "select",
                "options": ["api", "small_model"],
                "value": "api",
                "required": True,
                "info": "Type of model to optimize batches for"
            },
            "max_tokens": {
                "display_name": "Max Tokens per Batch",
                "type": "number",
                "value": 4000 if self.model_type == "api" else 8000,
                "required": True,
                "info": "Maximum tokens allowed in a single batch"
            },
            "show_stats": {
                "display_name": "Show Batch Statistics",
                "type": "boolean",
                "value": True,
                "required": False,
                "info": "Display detailed batch statistics"
            }
        }

    def _estimate_tokens(self, text: str) -> int:
        """Rough token count estimation"""
        # Simple estimation: words * 1.3 for safety margin
        return int(len(text.split()) * 1.3)

    def _extract_events(self, papers: List[Dict]) -> List[Event]:
        """Extract events from papers"""
        events = []
        for paper in papers:
            paper_code = paper['paper_code']
            for event in paper['events']:
                # Determine event type
                event_type = self._get_event_type(event)
                
                events.append(Event(
                    event_type=event_type,
                    text=event['Text'],
                    paper_code=paper_code
                ))
        return events

    def _get_event_type(self, event: Dict) -> str:
        """Extract event type from event dictionary"""
        type_keys = [
            'Background/Introduction',
            'Methods/Approach',
            'Results/Findings',
            'Conclusions/Implications'
        ]
        
        for key in type_keys:
            if key in event:
                return key
        return "Unknown"

    def create_batches(
        self,
        events: List[Event],
        batch_size: int,
        max_tokens: int
    ) -> List[List[Event]]:
        """Create optimized batches of events"""
        batches = []
        current_batch = []
        current_tokens = 0
        
        for event in events:
            event_tokens = self._estimate_tokens(event.text)
            
            # If adding this event would exceed token limit, create new batch
            if current_tokens + event_tokens > max_tokens and current_batch:
                batches.append(current_batch)
                current_batch = []
                current_tokens = 0
            
            # Add event to current batch
            current_batch.append(event)
            current_tokens += event_tokens
            
            # If batch size limit reached, create new batch
            if len(current_batch) >= batch_size:
                batches.append(current_batch)
                current_batch = []
                current_tokens = 0
        
        # Add any remaining events
        if current_batch:
            batches.append(current_batch)
            
        return batches

    def get_batch_stats(self, batches: List[List[Event]]) -> Dict:
        """Generate statistics about the batches"""
        stats = {
            "total_batches": len(batches),
            "total_events": sum(len(batch) for batch in batches),
            "avg_batch_size": sum(len(batch) for batch in batches) / len(batches) if batches else 0,
            "batch_sizes": [len(batch) for batch in batches],
            "batch_tokens": [
                sum(self._estimate_tokens(event.text) for event in batch)
                for batch in batches
            ]
        }
        return stats

    def process(
        self,
        papers: List[Dict],
        batch_size: int,
        model_type: str = "api",
        max_tokens: int = None,
        show_stats: bool = True
    ) -> Dict[str, Any]:
        """Process papers into optimized batches"""
        try:
            # Extract events
            events = self._extract_events(papers)
            
            # Set max tokens if not provided
            if max_tokens is None:
                max_tokens = 4000 if model_type == "api" else 8000
            
            # Create batches
            batches = self.create_batches(events, batch_size, max_tokens)
            
            # Prepare output
            output = {
                "batches": batches,
                "total_events": len(events)
            }
            
            # Add statistics if requested
            if show_stats:
                output["stats"] = self.get_batch_stats(batches)
            
            return output
            
        except Exception as e:
            raise Exception(f"Error processing batches: {str(e)}")

    def format_batch(self, batch: List[Event]) -> List[Dict]:
        """Format batch for output"""
        return [{
            "paper_code": event.paper_code,
            "event_type": event.event_type,
            "text": event.text
        } for event in batch]