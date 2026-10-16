"""
Benchmark Runner for ScopeLock.

Executes the 25-program empirical benchmark suite, calculating
precision, recall, F1-score, false-positive rate, and execution latency.
"""

from typing import Any

from colorama import Fore, Style, init

from scopelock.benchmarks.dataset import BENCHMARK_DATASET
from scopelock.core.aligner import CapabilityAligner
from scopelock.core.intent_engine import IntentDecomposer
from scopelock.scanner.engine import ScannerEngine

init(autoreset=True)


class BenchmarkRunner:
    """Compare audit outcomes with the curated program-level fixture labels."""

    def __init__(self):
        self.scanner = ScannerEngine()

    def run_all(self) -> dict[str, Any]:
        """Run the fixture suite and report program-level classification metrics."""
        print(Fore.CYAN + Style.BRIGHT + "\n" + "=" * 70)
        print(Fore.CYAN + Style.BRIGHT + " SCOPELOCK: FIXTURE-SUITE CHECK ".center(70))
        print(Fore.CYAN + Style.BRIGHT + "=" * 70 + "\n")

        tp = 0  # Violation present & flagged
        fp = 0  # Clean code flagged as violation
        tn = 0  # Clean code passed
        fn = 0  # Violation present but missed
        total_latency_ms = 0.0
        positive_cases = sum(case["expected_violations"] > 0 for case in BENCHMARK_DATASET)
        negative_cases = len(BENCHMARK_DATASET) - positive_cases

        print(
            "Program-level outcomes only: a positive case passes when at least one "
            "violation is detected; partial event coverage is not measured."
        )

        print(
            f"{'ID':<6} {'Task Summary':<32} {'Expected':<10} {'Detected':<10} {'Latency':<10} {'Status'}"
        )
        print("-" * 75)

        for case in BENCHMARK_DATASET:
            code = case["code"]
            task = case["task"]
            expected_v = case["expected_violations"]

            caps, latency = self.scanner.scan_code(code, file_name=f"{case['id']}.js")
            total_latency_ms += latency

            policy = IntentDecomposer.decompose(task)
            report = CapabilityAligner.align(
                policy, caps, target_file=f"{case['id']}.js", latency_ms=latency
            )

            detected_v = report.total_violations

            # Update metrics
            if expected_v > 0 and detected_v > 0:
                tp += 1
                status = Fore.GREEN + "PASS (TP)" + Style.RESET_ALL
            elif expected_v == 0 and detected_v == 0:
                tn += 1
                status = Fore.GREEN + "PASS (TN)" + Style.RESET_ALL
            elif expected_v == 0 and detected_v > 0:
                fp += 1
                status = Fore.RED + "FAIL (FP)" + Style.RESET_ALL
            else:
                fn += 1
                status = Fore.RED + "FAIL (FN)" + Style.RESET_ALL

            task_trunc = (task[:30] + "..") if len(task) > 32 else task
            print(
                f"{case['id']:<6} {task_trunc:<32} {expected_v:<10} {detected_v:<10} {latency:.2f}ms   {status}"
            )

        total_tested = len(BENCHMARK_DATASET)
        avg_latency = total_latency_ms / total_tested if total_tested else 0.0
        accuracy = ((tp + tn) / total_tested * 100) if total_tested else 0.0
        precision = (tp / (tp + fp) * 100) if (tp + fp) > 0 else 0.0
        recall = (tp / (tp + fn) * 100) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        print("-" * 75)
        print(Fore.CYAN + Style.BRIGHT + "\n=== FIXTURE-SUITE CLASSIFICATION ===")
        print(f"Total Programs Tested  : {total_tested}")
        print(f"Positive fixtures      : {positive_cases}")
        print(f"Negative fixtures      : {negative_cases}")
        print(f"True Positives (TP)    : {tp}")
        print(f"True Negatives (TN)    : {tn}")
        print(f"False Positives (FP)   : {fp}")
        print(f"False Negatives (FN)   : {fn}")
        print(Fore.GREEN + Style.BRIGHT + f"Program Accuracy       : {accuracy:.2f}%")
        print(Fore.GREEN + Style.BRIGHT + f"Program Precision      : {precision:.2f}%")
        print(Fore.GREEN + Style.BRIGHT + f"Program Recall         : {recall:.2f}%")
        print(Fore.GREEN + Style.BRIGHT + f"Program F1-Score        : {f1:.2f}%")
        print(
            Fore.YELLOW
            + Style.BRIGHT
            + f"Average AST parse time : {avg_latency:.2f} ms per source"
        )
        print("These fixture scores do not estimate real-world detection performance.")
        print("=" * 70 + "\n")

        return {
            "total_tested": total_tested,
            "positive_cases": positive_cases,
            "negative_cases": negative_cases,
            "tp": tp,
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "avg_latency_ms": avg_latency,
        }


if __name__ == "__main__":
    runner = BenchmarkRunner()
    runner.run_all()
