# langflow/components/evaluator.py

from abstract_annotation import CustomComponent
from typing import Dict, List, Any
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import torch

class EvaluatorComponent(CustomComponent):
    """Component for evaluating annotation quality against ground truth"""
    
    display_name: str = "Annotation Evaluator"
    description: str = "Evaluates annotation quality against ground truth data"

    def __init__(self):
        super().__init__()
        self.sentence_model = None

    def build_config(self):
        return {
            "evaluation_type": {
                "display_name": "Evaluation Type",
                "type": "select",
                "options": ["full", "summary_only", "arguments_only"],
                "value": "full",
                "required": True,
                "info": "What aspects to evaluate"
            },
            "similarity_threshold": {
                "display_name": "Similarity Threshold",
                "type": "number",
                "value": 0.8,
                "min": 0.0,
                "max": 1.0,
                "step": 0.05,
                "required": True,
                "info": "Threshold for semantic similarity"
            },
            "detailed_metrics": {
                "display_name": "Show Detailed Metrics",
                "type": "boolean",
                "value": True,
                "required": False,
                "info": "Show detailed evaluation metrics"
            }
        }

    def initialize_similarity_model(self):
        """Initialize the sentence transformer model"""
        if self.sentence_model is None:
            model_name = 'sentence-transformers/all-MiniLM-L6-v2'
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.sentence_model = SentenceTransformer(model_name).to(device)

    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        self.initialize_similarity_model()
        
        # Get embeddings
        embedding1 = self.sentence_model.encode([text1], convert_to_tensor=True)
        embedding2 = self.sentence_model.encode([text2], convert_to_tensor=True)
        
        # Calculate similarity
        similarity = cosine_similarity(
            embedding1.cpu().numpy(),
            embedding2.cpu().numpy()
        )[0][0]
        
        return float(similarity)

    def evaluate_summary(self, predicted: str, ground_truth: str) -> Dict:
        """Evaluate summary quality"""
        similarity = self.calculate_semantic_similarity(predicted, ground_truth)
        
        return {
            "similarity_score": similarity,
            "matches_threshold": similarity >= self.similarity_threshold
        }

    def evaluate_arguments(
        self,
        predicted: Dict,
        ground_truth: Dict
    ) -> Dict:
        """Evaluate argument extraction quality"""
        metrics = {
            "total_matches": 0,
            "total_ground_truth": 0,
            "total_predicted": 0,
            "category_scores": {}
        }
        
        for category in ground_truth.keys():
            gt_args = ground_truth[category]
            pred_args = predicted.get(category, [])
            
            if isinstance(gt_args, dict):  # Handle nested Object structure
                category_score = self.evaluate_nested_arguments(pred_args, gt_args)
            else:  # Handle flat list structure
                category_score = self.evaluate_argument_list(pred_args, gt_args)
            
            metrics["category_scores"][category] = category_score
            metrics["total_matches"] += category_score["matches"]
            metrics["total_ground_truth"] += category_score["total_ground_truth"]
            metrics["total_predicted"] += category_score["total_predicted"]
        
        # Calculate overall metrics
        if metrics["total_ground_truth"] > 0:
            metrics["recall"] = metrics["total_matches"] / metrics["total_ground_truth"]
        else:
            metrics["recall"] = 0
            
        if metrics["total_predicted"] > 0:
            metrics["precision"] = metrics["total_matches"] / metrics["total_predicted"]
        else:
            metrics["precision"] = 0
            
        if metrics["precision"] + metrics["recall"] > 0:
            metrics["f1"] = 2 * (metrics["precision"] * metrics["recall"]) / (metrics["precision"] + metrics["recall"])
        else:
            metrics["f1"] = 0
        
        return metrics

    def evaluate_argument_list(
        self,
        predicted: List[str],
        ground_truth: List[str]
    ) -> Dict:
        """Evaluate a list of arguments"""
        matches = 0
        for gt_arg in ground_truth:
            # Find best matching prediction
            best_similarity = 0
            for pred_arg in predicted:
                similarity = self.calculate_semantic_similarity(gt_arg, pred_arg)
                best_similarity = max(best_similarity, similarity)
                
            if best_similarity >= self.similarity_threshold:
                matches += 1
        
        return {
            "matches": matches,
            "total_ground_truth": len(ground_truth),
            "total_predicted": len(predicted),
            "match_rate": matches / len(ground_truth) if ground_truth else 0
        }

    def evaluate_nested_arguments(
        self,
        predicted: Dict,
        ground_truth: Dict
    ) -> Dict:
        """Evaluate nested argument structure (like Object)"""
        metrics = {
            "matches": 0,
            "total_ground_truth": 0,
            "total_predicted": 0,
            "sub_categories": {}
        }
        
        for key in ground_truth.keys():
            gt_list = ground_truth[key]
            pred_list = predicted.get(key, [])
            
            sub_metrics = self.evaluate_argument_list(pred_list, gt_list)
            metrics["sub_categories"][key] = sub_metrics
            
            metrics["matches"] += sub_metrics["matches"]
            metrics["total_ground_truth"] += sub_metrics["total_ground_truth"]
            metrics["total_predicted"] += sub_metrics["total_predicted"]
        
        return metrics

    def process(
        self,
        annotations: List[Dict],
        ground_truth: Dict[str, Dict],
        evaluation_type: str = "full",
        similarity_threshold: float = 0.8,
        detailed_metrics: bool = True
    ) -> Dict[str, Any]:
        """Process and evaluate annotations"""
        try:
            self.similarity_threshold = similarity_threshold
            results = []
            
            for annotation in annotations:
                paper_code = annotation['paper_code']
                if paper_code not in ground_truth:
                    continue
                    
                gt = ground_truth[paper_code]
                evaluation = {
                    "paper_code": paper_code,
                    "event_type": annotation['event_type']
                }
                
                # Evaluate summary if requested
                if evaluation_type in ["full", "summary_only"]:
                    evaluation["summary_metrics"] = self.evaluate_summary(
                        annotation['annotation']['summary'],
                        gt['summary']
                    )
                
                # Evaluate arguments if requested
                if evaluation_type in ["full", "arguments_only"]:
                    evaluation["argument_metrics"] = self.evaluate_arguments(
                        annotation['annotation']['arguments'],
                        gt['arguments']
                    )
                
                results.append(evaluation)
            
            # Calculate aggregate metrics
            aggregates = self.calculate_aggregate_metrics(results)
            
            output = {
                "evaluations": results if detailed_metrics else None,
                "aggregate_metrics": aggregates
            }
            
            return output
            
        except Exception as e:
            raise Exception(f"Error in evaluation process: {str(e)}")

    def calculate_aggregate_metrics(self, results: List[Dict]) -> Dict:
        """Calculate aggregate metrics across all evaluations"""
        aggregates = {
            "total_evaluated": len(results),
            "summary_metrics": {
                "average_similarity": 0,
                "threshold_match_rate": 0
            },
            "argument_metrics": {
                "average_precision": 0,
                "average_recall": 0,
                "average_f1": 0
            }
        }
        
        # Calculate averages
        if results:
            # Summary metrics
            if "summary_metrics" in results[0]:
                similarities = [r["summary_metrics"]["similarity_score"] for r in results]
                threshold_matches = [r["summary_metrics"]["matches_threshold"] for r in results]
                
                aggregates["summary_metrics"]["average_similarity"] = np.mean(similarities)
                aggregates["summary_metrics"]["threshold_match_rate"] = np.mean(threshold_matches)
            
            # Argument metrics
            if "argument_metrics" in results[0]:
                aggregates["argument_metrics"]["average_precision"] = np.mean(
                    [r["argument_metrics"]["precision"] for r in results]
                )
                aggregates["argument_metrics"]["average_recall"] = np.mean(
                    [r["argument_metrics"]["recall"] for r in results]
                )
                aggregates["argument_metrics"]["average_f1"] = np.mean(
                    [r["argument_metrics"]["f1"] for r in results]
                )
        
        return aggregates