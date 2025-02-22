# data_parser.py
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

class DataParser:
    def __init__(self, data_dir: str = "data"):
        """
        Initialize DataParser
        Args:
            data_dir (str): Directory containing JSON files
        """
        self.data_dir = Path(data_dir)
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def load_single_file(self, file_path: str) -> Dict:
        """
        Load a single JSON file
        Args:
            file_path (str): Path to JSON file
        Returns:
            Dict: Parsed JSON data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.logger.info(f"Successfully loaded file: {file_path}")
                return data
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON from {file_path}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            raise

    def parse_paper(self, paper: Dict) -> Dict:
        """
        Parse individual paper data
        Args:
            paper (Dict): Single paper data
        Returns:
            Dict: Parsed paper data
        """
        try:
            parsed_paper = {
                "paper_code": paper["paper_code"],
                "abstract": paper.get("abstract", ""),
                "events": self.parse_events(paper.get("events", []))
            }
            return parsed_paper
        except KeyError as e:
            self.logger.error(f"Missing required field in paper: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error parsing paper: {e}")
            raise

    def parse_events(self, events: List[Dict]) -> List[Dict]:
        """
        Parse events from a paper
        Args:
            events (List[Dict]): List of events
        Returns:
            List[Dict]: Parsed events
        """
        parsed_events = []
        for event in events:
            try:
                # Get event type (first key in dict)
                event_type = next(iter(event.keys()))
                
                parsed_event = {
                    "event_type": event_type,
                    "text": event.get("Text", ""),
                    "main_action": event.get("Main Action", ""),
                    "arguments": self.parse_arguments(event.get("Arguments", {}))
                }
                parsed_events.append(parsed_event)
            except Exception as e:
                self.logger.warning(f"Error parsing event: {e}")
                continue
        return parsed_events

    def parse_arguments(self, arguments: Dict) -> Dict:
        """
        Parse arguments structure
        Args:
            arguments (Dict): Arguments dictionary
        Returns:
            Dict: Parsed arguments
        """
        return {
            "Agent": arguments.get("Agent", []),
            "Object": {
                "Primary_Object": arguments.get("Object", {}).get("Primary Object", []),
                "Primary_Modifier": arguments.get("Object", {}).get("Primary Modifier", []),
                "Secondary_Object": arguments.get("Object", {}).get("Secondary Object", []),
                "Secondary_Modifier": arguments.get("Object", {}).get("Secondary Modifier", [])
            },
            "Context": arguments.get("Context", []),
            "Purpose": arguments.get("Purpose", []),
            "Method": arguments.get("Method", []),
            "Results": arguments.get("Results", []),
            "Analysis": arguments.get("Analysis", []),
            "Challenge": arguments.get("Challenge", []),
            "Ethical": arguments.get("Ethical", []),
            "Implications": arguments.get("Implications", []),
            "Contradictions": arguments.get("Contradictions", [])
        }

    def load_and_parse_all(self) -> List[Dict]:
        """
        Load and parse all JSON files in data directory
        Returns:
            List[Dict]: List of parsed papers
        """
        all_papers = []
        for json_file in self.data_dir.glob("*.json"):
            try:
                data = self.load_single_file(str(json_file))
                for paper in data.get("papers", []):
                    parsed_paper = self.parse_paper(paper)
                    all_papers.append(parsed_paper)
            except Exception as e:
                self.logger.error(f"Error processing file {json_file}: {e}")
                continue
        return all_papers

    def get_statistics(self, papers: List[Dict]) -> Dict:
        """
        Get statistics about the parsed papers
        Args:
            papers (List[Dict]): List of parsed papers
        Returns:
            Dict: Statistics about the dataset
        """
        stats = {
            "total_papers": len(papers),
            "total_events": 0,
            "event_types": {},
            "argument_types": {
                "Agent": 0,
                "Primary_Object": 0,
                "Secondary_Object": 0,
                "Context": 0,
                "Purpose": 0,
                "Method": 0,
                "Results": 0,
                "Analysis": 0,
                "Implications": 0
            }
        }

        for paper in papers:
            for event in paper["events"]:
                stats["total_events"] += 1
                event_type = event["event_type"]
                stats["event_types"][event_type] = stats["event_types"].get(event_type, 0) + 1

        return stats

# Example usage
if __name__ == "__main__":
    parser = DataParser()
    
    # Example with a single file
    try:
        sample_file = "DH_annotation_23_6_annotated.json"
        data = parser.load_single_file(sample_file)
        
        # Process each paper
        for paper in data["papers"]:
            parsed_paper = parser.parse_paper(paper)
            print(f"\nProcessed Paper: {parsed_paper['paper_code']}")
            print(f"Number of events: {len(parsed_paper['events'])}")
            
            # Print first event as example
            if parsed_paper['events']:
                first_event = parsed_paper['events'][0]
                print(f"\nFirst Event Type: {first_event['event_type']}")
                print(f"Main Action: {first_event['main_action']}")
    
    except Exception as e:
        print(f"Error in processing: {e}")