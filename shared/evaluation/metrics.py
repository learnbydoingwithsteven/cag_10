"""
Evaluation metrics for CAG applications.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass
import logging
from rouge_score import rouge_scorer
from bert_score import score as bert_score
from sklearn.metrics import precision_recall_fscore_support
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


@dataclass
class EvaluationResult:
    """Container for evaluation results."""
    metric_name: str
    score: float
    details: Dict[str, Any]
    timestamp: str


class MetricCalculator:
    """Base class for metric calculation."""

    def __init__(self, name: str):
        self.name = name

    def calculate(
        self,
        predictions: List[str],
        references: List[str],
        **kwargs
    ) -> EvaluationResult:
        """Calculate metric score."""
        raise NotImplementedError


class BLEUMetric(MetricCalculator):
    """BLEU score for text generation quality."""

    def __init__(self):
        super().__init__("BLEU")
        self.smoothing = SmoothingFunction()

    def calculate(
        self,
        predictions: List[str],
        references: List[str],
        **kwargs
    ) -> EvaluationResult:
        """
        Calculate BLEU score.

        Args:
            predictions: List of predicted texts
            references: List of reference texts

        Returns:
            EvaluationResult with BLEU score
        """
        scores = []
        for pred, ref in zip(predictions, references):
            pred_tokens = nltk.word_tokenize(pred.lower())
            ref_tokens = [nltk.word_tokenize(ref.lower())]
            
            score = sentence_bleu(
                ref_tokens,
                pred_tokens,
                smoothing_function=self.smoothing.method1
            )
            scores.append(score)

        avg_score = np.mean(scores)
        
        return EvaluationResult(
            metric_name=self.name,
            score=avg_score,
            details={
                "individual_scores": scores,
                "std": np.std(scores),
                "min": np.min(scores),
                "max": np.max(scores)
            },
            timestamp=str(np.datetime64('now'))
        )


class ROUGEMetric(MetricCalculator):
    """ROUGE scores for summarization quality."""

    def __init__(self):
        super().__init__("ROUGE")
        self.scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'],
            use_stemmer=True
        )

    def calculate(
        self,
        predictions: List[str],
        references: List[str],
        **kwargs
    ) -> EvaluationResult:
        """
        Calculate ROUGE scores.

        Args:
            predictions: List of predicted texts
            references: List of reference texts

        Returns:
            EvaluationResult with ROUGE scores
        """
        rouge1_scores = []
        rouge2_scores = []
        rougeL_scores = []

        for pred, ref in zip(predictions, references):
            scores = self.scorer.score(ref, pred)
            rouge1_scores.append(scores['rouge1'].fmeasure)
            rouge2_scores.append(scores['rouge2'].fmeasure)
            rougeL_scores.append(scores['rougeL'].fmeasure)

        return EvaluationResult(
            metric_name=self.name,
            score=np.mean(rougeL_scores),  # Use ROUGE-L as primary score
            details={
                "rouge1": {
                    "mean": np.mean(rouge1_scores),
                    "std": np.std(rouge1_scores)
                },
                "rouge2": {
                    "mean": np.mean(rouge2_scores),
                    "std": np.std(rouge2_scores)
                },
                "rougeL": {
                    "mean": np.mean(rougeL_scores),
                    "std": np.std(rougeL_scores)
                }
            },
            timestamp=str(np.datetime64('now'))
        )


class BERTScoreMetric(MetricCalculator):
    """BERTScore for semantic similarity."""

    def __init__(self, model_type: str = "microsoft/deberta-xlarge-mnli"):
        super().__init__("BERTScore")
        self.model_type = model_type

    def calculate(
        self,
        predictions: List[str],
        references: List[str],
        **kwargs
    ) -> EvaluationResult:
        """
        Calculate BERTScore.

        Args:
            predictions: List of predicted texts
            references: List of reference texts

        Returns:
            EvaluationResult with BERTScore
        """
        P, R, F1 = bert_score(
            predictions,
            references,
            model_type=self.model_type,
            verbose=False
        )

        return EvaluationResult(
            metric_name=self.name,
            score=F1.mean().item(),
            details={
                "precision": {
                    "mean": P.mean().item(),
                    "std": P.std().item()
                },
                "recall": {
                    "mean": R.mean().item(),
                    "std": R.std().item()
                },
                "f1": {
                    "mean": F1.mean().item(),
                    "std": F1.std().item()
                }
            },
            timestamp=str(np.datetime64('now'))
        )


class ContextRelevanceMetric(MetricCalculator):
    """Measure relevance of retrieved context."""

    def __init__(self):
        super().__init__("ContextRelevance")

    def calculate(
        self,
        context_scores: List[List[float]],
        **kwargs
    ) -> EvaluationResult:
        """
        Calculate context relevance metrics.

        Args:
            context_scores: List of relevance scores for each query

        Returns:
            EvaluationResult with context relevance metrics
        """
        all_scores = [score for scores in context_scores for score in scores]
        
        if not all_scores:
            return EvaluationResult(
                metric_name=self.name,
                score=0.0,
                details={},
                timestamp=str(np.datetime64('now'))
            )

        avg_top_score = np.mean([max(scores) if scores else 0 for scores in context_scores])
        
        return EvaluationResult(
            metric_name=self.name,
            score=np.mean(all_scores),
            details={
                "avg_top_score": avg_top_score,
                "std": np.std(all_scores),
                "min": np.min(all_scores),
                "max": np.max(all_scores),
                "num_queries": len(context_scores),
                "avg_contexts_per_query": np.mean([len(scores) for scores in context_scores])
            },
            timestamp=str(np.datetime64('now'))
        )


class LatencyMetric(MetricCalculator):
    """Measure response latency."""

    def __init__(self):
        super().__init__("Latency")

    def calculate(
        self,
        latencies: List[float],
        **kwargs
    ) -> EvaluationResult:
        """
        Calculate latency metrics.

        Args:
            latencies: List of latency values in milliseconds

        Returns:
            EvaluationResult with latency metrics
        """
        return EvaluationResult(
            metric_name=self.name,
            score=np.mean(latencies),
            details={
                "mean_ms": np.mean(latencies),
                "median_ms": np.median(latencies),
                "p50_ms": np.percentile(latencies, 50),
                "p95_ms": np.percentile(latencies, 95),
                "p99_ms": np.percentile(latencies, 99),
                "std_ms": np.std(latencies),
                "min_ms": np.min(latencies),
                "max_ms": np.max(latencies)
            },
            timestamp=str(np.datetime64('now'))
        )


class TokenUsageMetric(MetricCalculator):
    """Measure token usage and cost."""

    def __init__(self, cost_per_1k_tokens: float = 0.0):
        super().__init__("TokenUsage")
        self.cost_per_1k_tokens = cost_per_1k_tokens

    def calculate(
        self,
        token_usages: List[Dict[str, int]],
        **kwargs
    ) -> EvaluationResult:
        """
        Calculate token usage metrics.

        Args:
            token_usages: List of token usage dicts

        Returns:
            EvaluationResult with token usage metrics
        """
        total_tokens = sum(usage.get('total', 0) for usage in token_usages)
        prompt_tokens = sum(usage.get('prompt_tokens', 0) for usage in token_usages)
        completion_tokens = sum(usage.get('completion_tokens', 0) for usage in token_usages)

        avg_total = total_tokens / len(token_usages) if token_usages else 0
        estimated_cost = (total_tokens / 1000) * self.cost_per_1k_tokens

        return EvaluationResult(
            metric_name=self.name,
            score=avg_total,
            details={
                "total_tokens": total_tokens,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "avg_tokens_per_request": avg_total,
                "estimated_cost_usd": estimated_cost,
                "num_requests": len(token_usages)
            },
            timestamp=str(np.datetime64('now'))
        )


class AccuracyMetric(MetricCalculator):
    """Measure classification accuracy."""

    def __init__(self):
        super().__init__("Accuracy")

    def calculate(
        self,
        predictions: List[Any],
        references: List[Any],
        **kwargs
    ) -> EvaluationResult:
        """
        Calculate accuracy metrics.

        Args:
            predictions: List of predicted labels
            references: List of reference labels

        Returns:
            EvaluationResult with accuracy metrics
        """
        correct = sum(p == r for p, r in zip(predictions, references))
        accuracy = correct / len(predictions) if predictions else 0

        # Calculate precision, recall, F1 if applicable
        try:
            precision, recall, f1, _ = precision_recall_fscore_support(
                references,
                predictions,
                average='weighted',
                zero_division=0
            )
        except:
            precision = recall = f1 = 0.0

        return EvaluationResult(
            metric_name=self.name,
            score=accuracy,
            details={
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "correct": correct,
                "total": len(predictions)
            },
            timestamp=str(np.datetime64('now'))
        )


class EvaluationSuite:
    """Suite of evaluation metrics."""

    def __init__(self):
        self.metrics = {
            "bleu": BLEUMetric(),
            "rouge": ROUGEMetric(),
            "bert_score": BERTScoreMetric(),
            "context_relevance": ContextRelevanceMetric(),
            "latency": LatencyMetric(),
            "token_usage": TokenUsageMetric(),
            "accuracy": AccuracyMetric()
        }

    def evaluate(
        self,
        predictions: Optional[List[str]] = None,
        references: Optional[List[str]] = None,
        context_scores: Optional[List[List[float]]] = None,
        latencies: Optional[List[float]] = None,
        token_usages: Optional[List[Dict[str, int]]] = None,
        pred_labels: Optional[List[Any]] = None,
        ref_labels: Optional[List[Any]] = None,
        metrics_to_run: Optional[List[str]] = None
    ) -> Dict[str, EvaluationResult]:
        """
        Run evaluation suite.

        Args:
            predictions: Predicted texts
            references: Reference texts
            context_scores: Context relevance scores
            latencies: Response latencies
            token_usages: Token usage data
            pred_labels: Predicted labels
            ref_labels: Reference labels
            metrics_to_run: Specific metrics to run (None = all applicable)

        Returns:
            Dictionary of evaluation results
        """
        results = {}

        if metrics_to_run is None:
            metrics_to_run = list(self.metrics.keys())

        # Text generation metrics
        if predictions and references:
            if "bleu" in metrics_to_run:
                results["bleu"] = self.metrics["bleu"].calculate(predictions, references)
            if "rouge" in metrics_to_run:
                results["rouge"] = self.metrics["rouge"].calculate(predictions, references)
            if "bert_score" in metrics_to_run:
                results["bert_score"] = self.metrics["bert_score"].calculate(predictions, references)

        # Context relevance
        if context_scores and "context_relevance" in metrics_to_run:
            results["context_relevance"] = self.metrics["context_relevance"].calculate(
                context_scores=context_scores
            )

        # Latency
        if latencies and "latency" in metrics_to_run:
            results["latency"] = self.metrics["latency"].calculate(latencies=latencies)

        # Token usage
        if token_usages and "token_usage" in metrics_to_run:
            results["token_usage"] = self.metrics["token_usage"].calculate(
                token_usages=token_usages
            )

        # Accuracy
        if pred_labels and ref_labels and "accuracy" in metrics_to_run:
            results["accuracy"] = self.metrics["accuracy"].calculate(
                predictions=pred_labels,
                references=ref_labels
            )

        return results

    def get_summary(self, results: Dict[str, EvaluationResult]) -> Dict[str, Any]:
        """Get summary of evaluation results."""
        summary = {
            "num_metrics": len(results),
            "metrics": {}
        }

        for metric_name, result in results.items():
            summary["metrics"][metric_name] = {
                "score": result.score,
                "key_details": {
                    k: v for k, v in result.details.items()
                    if isinstance(v, (int, float, str))
                }
            }

        return summary
