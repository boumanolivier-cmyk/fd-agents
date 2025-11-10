"""Run all evaluation tests"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.eval_refusal import run_eval as run_refusal_eval
from tests.eval_chart_data import run_eval as run_data_eval


async def run_all_evals():
    """Run all evaluation tests"""
    print("\n" + "=" * 80)
    print(" " * 20 + "AI CHART GENERATOR - EVALUATION SUITE")
    print("=" * 80 + "\n")
    
    total_passed = 0
    total_failed = 0
    
    # Run Eval 1: Refusal/Acceptance
    passed1, failed1 = await run_refusal_eval()
    total_passed += passed1
    total_failed += failed1
    
    print("\n\n")
    
    # Run Eval 2: Data Extraction
    passed2, failed2 = await run_data_eval()
    total_passed += passed2
    total_failed += failed2
    
    # Final summary
    print("\n" + "=" * 80)
    print(" " * 30 + "FINAL SUMMARY")
    print("=" * 80)
    print(f"Total tests: {total_passed + total_failed}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Overall success rate: {(total_passed/(total_passed + total_failed)*100):.1f}%")
    print("=" * 80 + "\n")
    
    return total_failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_evals())
    sys.exit(0 if success else 1)
