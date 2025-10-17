"""
Comprehensive evaluation runner for all CAG applications.
"""

import asyncio
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from evaluation.metrics import EvaluationSuite
from evaluation.test_datasets import TestDatasetLoader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ApplicationEvaluator:
    """Evaluator for a single CAG application."""

    def __init__(self, app_name: str, app_config: Dict[str, Any]):
        self.app_name = app_name
        self.app_config = app_config
        self.evaluation_suite = EvaluationSuite()

    async def run_evaluation(self, test_dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run evaluation on test dataset.

        Args:
            test_dataset: List of test cases

        Returns:
            Evaluation results
        """
        logger.info(f"Evaluating {self.app_name}...")

        predictions = []
        references = []
        context_scores = []
        latencies = []
        token_usages = []

        # Import app-specific client
        app_client = self._get_app_client()

        for i, test_case in enumerate(test_dataset):
            logger.info(f"Processing test case {i+1}/{len(test_dataset)}")

            try:
                # Make prediction
                result = await app_client.predict(test_case["query"])

                predictions.append(result["answer"])
                references.append(test_case["expected_answer"])
                context_scores.append([c["relevance_score"] for c in result.get("context_chunks", [])])
                latencies.append(result["latency_ms"])
                token_usages.append(result["token_usage"])

            except Exception as e:
                logger.error(f"Error on test case {i}: {str(e)}")
                continue

        # Run evaluation metrics
        eval_results = self.evaluation_suite.evaluate(
            predictions=predictions,
            references=references,
            context_scores=context_scores,
            latencies=latencies,
            token_usages=token_usages
        )

        # Calculate aggregate scores
        aggregate_score = self._calculate_aggregate_score(eval_results)

        return {
            "app_name": self.app_name,
            "timestamp": datetime.now().isoformat(),
            "num_test_cases": len(test_dataset),
            "num_successful": len(predictions),
            "aggregate_score": aggregate_score,
            "metrics": {
                name: {
                    "score": result.score,
                    "details": result.details
                }
                for name, result in eval_results.items()
            }
        }

    def _get_app_client(self):
        """Get application-specific client."""
        # Import dynamically based on app name
        app_module = self.app_name.replace("_", "")
        try:
            module = __import__(f"{self.app_name}.backend.client", fromlist=["AppClient"])
            return module.AppClient(self.app_config)
        except ImportError:
            logger.warning(f"No client found for {self.app_name}, using mock client")
            return MockAppClient()

    def _calculate_aggregate_score(self, eval_results: Dict[str, Any]) -> float:
        """Calculate weighted aggregate score."""
        weights = {
            "bleu": 0.15,
            "rouge": 0.15,
            "bert_score": 0.25,
            "context_relevance": 0.20,
            "latency": 0.15,
            "token_usage": 0.10
        }

        # Normalize latency (lower is better)
        normalized_scores = {}
        for metric, result in eval_results.items():
            if metric == "latency":
                # Normalize to 0-1 range (assuming 5000ms is worst case)
                normalized_scores[metric] = max(0, 1 - (result.score / 5000))
            elif metric == "token_usage":
                # Normalize to 0-1 range (assuming 5000 tokens is worst case)
                normalized_scores[metric] = max(0, 1 - (result.score / 5000))
            else:
                normalized_scores[metric] = result.score

        # Calculate weighted sum
        aggregate = sum(
            normalized_scores.get(metric, 0) * weight
            for metric, weight in weights.items()
        )

        return aggregate


class MockAppClient:
    """Mock client for testing."""

    async def predict(self, query: str) -> Dict[str, Any]:
        """Mock prediction."""
        return {
            "answer": "Mock answer",
            "context_chunks": [],
            "latency_ms": 100,
            "token_usage": {"total": 50}
        }


class EvaluationRunner:
    """Main evaluation runner for all applications."""

    def __init__(self, output_dir: str = "./evaluation_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dataset_loader = TestDatasetLoader()

    async def run_all_evaluations(self) -> Dict[str, Any]:
        """
        Run evaluations for all applications.

        Returns:
            Combined evaluation results
        """
        logger.info("Starting comprehensive evaluation...")

        apps = [
            ("app_01_legal_analyzer", {"port": 8001}),
            ("app_02_medical_assistant", {"port": 8002}),
            ("app_03_code_reviewer", {"port": 8003}),
            ("app_04_support_agent", {"port": 8004}),
            ("app_05_financial_analyzer", {"port": 8005}),
            ("app_06_paper_summarizer", {"port": 8006}),
            ("app_07_product_recommender", {"port": 8007}),
            ("app_08_educational_tutor", {"port": 8008}),
            ("app_09_compliance_checker", {"port": 8009}),
            ("app_10_fact_checker", {"port": 8010}),
        ]

        all_results = {}

        for app_name, app_config in apps:
            try:
                # Load test dataset for this app
                test_dataset = self.dataset_loader.load_dataset(app_name)

                # Create evaluator
                evaluator = ApplicationEvaluator(app_name, app_config)

                # Run evaluation
                results = await evaluator.run_evaluation(test_dataset)

                all_results[app_name] = results

                # Save individual results
                self._save_results(app_name, results)

            except Exception as e:
                logger.error(f"Error evaluating {app_name}: {str(e)}")
                all_results[app_name] = {"error": str(e)}

        # Generate summary
        summary = self._generate_summary(all_results)

        # Save summary
        self._save_summary(summary)

        logger.info("Evaluation complete!")
        return summary

    def _save_results(self, app_name: str, results: Dict[str, Any]):
        """Save results for individual app."""
        output_file = self.output_dir / f"{app_name}_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Saved results to {output_file}")

    def _save_summary(self, summary: Dict[str, Any]):
        """Save evaluation summary."""
        output_file = self.output_dir / "summary.json"
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Saved summary to {output_file}")

    def _generate_summary(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate evaluation summary."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "num_apps": len(all_results),
            "apps": {},
            "overall": {
                "avg_aggregate_score": 0,
                "avg_latency": 0,
                "total_test_cases": 0
            }
        }

        total_score = 0
        total_latency = 0
        total_cases = 0

        for app_name, results in all_results.items():
            if "error" in results:
                summary["apps"][app_name] = {"status": "failed", "error": results["error"]}
                continue

            summary["apps"][app_name] = {
                "status": "success",
                "aggregate_score": results["aggregate_score"],
                "num_test_cases": results["num_test_cases"],
                "key_metrics": {
                    name: data["score"]
                    for name, data in results["metrics"].items()
                }
            }

            total_score += results["aggregate_score"]
            total_cases += results["num_test_cases"]

            if "latency" in results["metrics"]:
                total_latency += results["metrics"]["latency"]["score"]

        num_successful = sum(1 for r in all_results.values() if "error" not in r)
        if num_successful > 0:
            summary["overall"]["avg_aggregate_score"] = total_score / num_successful
            summary["overall"]["avg_latency"] = total_latency / num_successful
        summary["overall"]["total_test_cases"] = total_cases

        return summary


class TestDatasetLoader:
    """Loader for test datasets."""

    def load_dataset(self, app_name: str) -> List[Dict[str, Any]]:
        """
        Load test dataset for application.

        Args:
            app_name: Application name

        Returns:
            List of test cases
        """
        # Load from file or generate synthetic data
        dataset_file = Path(f"./test_datasets/{app_name}.json")

        if dataset_file.exists():
            with open(dataset_file) as f:
                return json.load(f)

        # Generate synthetic test data
        logger.warning(f"No dataset found for {app_name}, generating synthetic data")
        return self._generate_synthetic_dataset(app_name)

    def _generate_synthetic_dataset(self, app_name: str) -> List[Dict[str, Any]]:
        """Generate synthetic test dataset."""
        # App-specific test cases
        test_cases = {
            "app_01_legal_analyzer": [
                {
                    "query": "What are the requirements for filing a motion to dismiss?",
                    "expected_answer": "A motion to dismiss must be filed within the time allowed for filing an answer..."
                },
                {
                    "query": "Explain the doctrine of res judicata",
                    "expected_answer": "Res judicata prevents parties from relitigating claims that have been finally decided..."
                }
            ],
            "app_02_medical_assistant": [
                {
                    "query": "What are the symptoms of type 2 diabetes?",
                    "expected_answer": "Common symptoms include increased thirst, frequent urination, increased hunger..."
                }
            ],
            "app_03_code_reviewer": [
                {
                    "query": "Review this Python function for security issues",
                    "expected_answer": "The function has SQL injection vulnerability..."
                }
            ]
        }

        return test_cases.get(app_name, [
            {
                "query": "Sample query",
                "expected_answer": "Sample answer"
            }
        ] * 5)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run CAG application evaluations")
    parser.add_argument("--output-dir", default="./evaluation_results", help="Output directory")
    parser.add_argument("--save-metrics", action="store_true", help="Save detailed metrics")
    args = parser.parse_args()

    runner = EvaluationRunner(output_dir=args.output_dir)
    summary = await runner.run_all_evaluations()

    # Print summary
    print("\n" + "="*80)
    print("EVALUATION SUMMARY")
    print("="*80)
    print(f"Total Apps: {summary['num_apps']}")
    print(f"Average Aggregate Score: {summary['overall']['avg_aggregate_score']:.3f}")
    print(f"Average Latency: {summary['overall']['avg_latency']:.2f}ms")
    print(f"Total Test Cases: {summary['overall']['total_test_cases']}")
    print("\nPer-App Scores:")
    for app_name, app_data in summary['apps'].items():
        if app_data['status'] == 'success':
            print(f"  {app_name}: {app_data['aggregate_score']:.3f}")
        else:
            print(f"  {app_name}: FAILED")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
