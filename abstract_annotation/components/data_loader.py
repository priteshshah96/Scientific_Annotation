# langflow/components/data_loader.py

from abstract_annotation import CustomComponent
from typing import Dict, List, Set
from pathlib import Path
import json
import logging

class DataLoaderComponent(CustomComponent):
    display_name: str = "Paper Data Loader"
    description: str = "Dynamically loads annotations from all annotators"

    def build_config(self):
        return {
            "ground_truth_dir": {
                "display_name": "Ground Truth Directory",
                "type": "folder",
                "required": True,
                "info": "Directory containing annotator folders"
            },
            "include_dh": {
                "display_name": "Include DH Annotations",
                "type": "boolean",
                "value": True,
                "info": "Include DH annotation files"
            },
            "show_stats": {
                "display_name": "Show Statistics",
                "type": "boolean",
                "value": True,
                "info": "Display detailed annotation statistics"
            }
        }

    def get_annotators(self, ground_truth_dir: Path) -> List[str]:
        """Automatically discover all annotator folders"""
        return [
            folder.name 
            for folder in ground_truth_dir.iterdir() 
            if folder.is_dir() and not folder.name.startswith('.')  # Skip hidden folders
        ]

    def load_annotator_files(self, annotator_dir: Path, annotator_id: str, include_dh: bool) -> Dict:
        """Load all annotation files for one annotator"""
        annotations = {}
        
        # Get all JSON files
        json_files = list(annotator_dir.glob("*.json"))
        
        for file_path in json_files:
            # Skip DH files if not included
            if not include_dh and "DH_annotation" in file_path.name:
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    file_annotations = data.get('papers', data)
                    
                    for paper in file_annotations:
                        paper_code = paper['paper_code']
                        if paper_code not in annotations:
                            annotations[paper_code] = []
                            
                        # Add metadata
                        paper['metadata'] = {
                            'annotator_id': annotator_id,
                            'source_file': file_path.name,
                            'is_dh': "DH_annotation" in file_path.name
                        }
                        
                        annotations[paper_code].append(paper)
                        
            except Exception as e:
                logging.error(f"Error loading {file_path}: {str(e)}")
                continue
                
        return annotations

    def get_annotation_stats(self, all_annotations: Dict, annotators: List[str]) -> Dict:
        """Generate detailed statistics about annotations"""
        stats = {
            "annotators": {
                "total": len(annotators),
                "names": annotators
            },
            "papers": {
                "total_unique": len(all_annotations),
                "by_annotator_count": {},  # How many papers have 1, 2, 3... annotators
                "multi_annotated": []  # List of papers with multiple annotators
            },
            "annotations": {
                "by_annotator": {},  # Count per annotator
                "by_type": {  # Regular vs DH
                    "regular": 0,
                    "dh": 0
                }
            }
        }
        
        # Process each paper's annotations
        for paper_code, paper_annotations in all_annotations.items():
            # Count unique annotators for this paper
            annotator_set = set(ann['metadata']['annotator_id'] for ann in paper_annotations)
            num_annotators = len(annotator_set)
            
            # Update papers by annotator count
            if num_annotators not in stats["papers"]["by_annotator_count"]:
                stats["papers"]["by_annotator_count"][num_annotators] = 0
            stats["papers"]["by_annotator_count"][num_annotators] += 1
            
            # Track multi-annotated papers
            if num_annotators > 1:
                stats["papers"]["multi_annotated"].append({
                    "paper_code": paper_code,
                    "annotators": list(annotator_set),
                    "file_counts": {
                        annotator: len([
                            ann for ann in paper_annotations 
                            if ann['metadata']['annotator_id'] == annotator
                        ]) for annotator in annotator_set
                    }
                })
            
            # Update annotation counts
            for annotation in paper_annotations:
                metadata = annotation['metadata']
                annotator = metadata['annotator_id']
                
                # Initialize annotator stats if needed
                if annotator not in stats["annotations"]["by_annotator"]:
                    stats["annotations"]["by_annotator"][annotator] = {
                        "total": 0,
                        "regular": 0,
                        "dh": 0
                    }
                
                # Update counts
                stats["annotations"]["by_annotator"][annotator]["total"] += 1
                if metadata['is_dh']:
                    stats["annotations"]["by_annotator"][annotator]["dh"] += 1
                    stats["annotations"]["by_type"]["dh"] += 1
                else:
                    stats["annotations"]["by_annotator"][annotator]["regular"] += 1
                    stats["annotations"]["by_type"]["regular"] += 1
        
        return stats

    def process(
        self,
        ground_truth_dir: str,
        include_dh: bool = True,
        show_stats: bool = True
    ) -> Dict:
        """Process and load all annotations"""
        try:
            ground_truth_path = Path(ground_truth_dir)
            
            # Discover annotators
            annotators = self.get_annotators(ground_truth_path)
            logging.info(f"Found annotators: {annotators}")
            
            # Load all annotations
            all_annotations = {}
            
            for annotator_id in annotators:
                annotator_dir = ground_truth_path / annotator_id
                annotations = self.load_annotator_files(
                    annotator_dir, 
                    annotator_id, 
                    include_dh
                )
                
                # Merge annotations
                for paper_code, paper_annotations in annotations.items():
                    if paper_code not in all_annotations:
                        all_annotations[paper_code] = []
                    all_annotations[paper_code].extend(paper_annotations)
            
            output = {
                "annotations": all_annotations,
                "annotators": annotators
            }
            
            # Add statistics if requested
            if show_stats:
                output["stats"] = self.get_annotation_stats(all_annotations, annotators)
            
            return output
            
        except Exception as e:
            raise Exception(f"Error loading annotations: {str(e)}")