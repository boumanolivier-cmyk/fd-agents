"""
Evaluation 1: Test that the agent correctly refuses/allows chart requests

This eval tests the STRICT behavior where the agent requires concrete data points.
Vague requests without data are correctly refused.
"""
import asyncio
from app.agents.chart_agent import analyze_chart_request


# Test cases: (request, should_accept, category)
TEST_CASES = [
    # Should ACCEPT - valid chart requests WITH DATA
    ("Give me a chart with Monday=4.1, Tuesday=4.2, Wednesday=4.4", True, "concrete_data"),
    ("Can you make a line chart for this data: 2020=25, 2021=26, 2022=26.5", True, "concrete_data"),
    ("Create a bar chart: Q1=100, Q2=150, Q3=200, Q4=175", True, "explicit_with_data"),
    ("Show me a line chart: Jan=50, Feb=60, Mar=70, Apr=80", True, "explicit_with_data"),
    ("Make a chart with Apple=25, Banana=30, Orange=20, Grape=15", True, "concrete_data"),
    ("Chart this: ProductA=100, ProductB=150, ProductC=200", True, "concrete_data"),
    ("I need a bar chart with North=500, South=750, East=600, West=550", True, "explicit_with_data"),
    ("Create a line chart showing: 2020=10, 2021=15, 2022=20, 2023=25", True, "explicit_with_data"),
    ("Make a bar graph: Dogs=40, Cats=35, Birds=25", True, "explicit_with_data"),
    ("Plot this data: Week1=100, Week2=120, Week3=115, Week4=130", True, "concrete_data"),
    
    # Should REFUSE - vague requests WITHOUT concrete data (strict behavior)
    ("Make a bar chart showing sales by month", False, "vague_no_data"),
    ("Create a line chart of temperature over time", False, "vague_no_data"),
    ("I want a chart that shows student debt over the years", False, "vague_no_data"),
    ("Show me a bar chart comparing revenue across regions", False, "vague_no_data"),
    ("Chart the number of check-ins per day", False, "vague_no_data"),
    ("Make a chart about quarterly earnings", False, "vague_no_data"),
    ("Show sales trends", False, "vague_no_data"),
    
    # Should REFUSE - completely wrong requests
    ("What's the weather today?", False, "off_topic"),
    ("Help me write an essay", False, "off_topic"),
    ("Can you make a pie chart?", False, "wrong_chart_type"),
    ("Tell me a joke", False, "off_topic"),
    ("What's 2+2?", False, "off_topic"),
    ("Write me a poem about charts", False, "off_topic"),
    ("How do I cook pasta?", False, "off_topic"),
    ("Can you help with my homework?", False, "off_topic"),
    ("Make me a scatter plot", False, "wrong_chart_type"),
    ("Create a histogram", False, "wrong_chart_type"),
    ("Draw a pie chart with data: A=10, B=20, C=30", False, "wrong_chart_type"),
    ("I need a bubble chart", False, "wrong_chart_type"),
    ("Can you create a heatmap?", False, "wrong_chart_type"),
    ("Make a radar chart", False, "wrong_chart_type"),
]


async def run_eval():
    """Run the evaluation tests"""
    print("=" * 80)
    print("EVALUATION 1: Request Validation (Refusal/Acceptance)")
    print("Testing STRICT behavior - requires concrete data points")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    # Track results by category
    results_by_category = {}
    
    for i, test_case in enumerate(TEST_CASES, 1):
        if len(test_case) == 3:
            request, should_accept, category = test_case
        else:
            request, should_accept = test_case
            category = "uncategorized"
        
        print(f"Test {i}/{len(TEST_CASES)} [{category}]: ", end="")
        
        try:
            result = await analyze_chart_request(request)
            actual_accept = result.is_valid
            
            if actual_accept == should_accept:
                print(f"✅ PASS")
                print(f"  Request: '{request}'")
                print(f"  Expected: {'ACCEPT' if should_accept else 'REFUSE'}")
                print(f"  Actual: {'ACCEPT' if actual_accept else 'REFUSE'}")
                if not actual_accept and result.reason:
                    print(f"  Reason: {result.reason}")
                passed += 1
                
                if category not in results_by_category:
                    results_by_category[category] = {"passed": 0, "failed": 0}
                results_by_category[category]["passed"] += 1
            else:
                print(f"❌ FAIL")
                print(f"  Request: '{request}'")
                print(f"  Expected: {'ACCEPT' if should_accept else 'REFUSE'}")
                print(f"  Actual: {'ACCEPT' if actual_accept else 'REFUSE'}")
                if result.reason:
                    print(f"  Reason: {result.reason}")
                failed += 1
                
                if category not in results_by_category:
                    results_by_category[category] = {"passed": 0, "failed": 0}
                results_by_category[category]["failed"] += 1
        
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            failed += 1
            
            if category not in results_by_category:
                results_by_category[category] = {"passed": 0, "failed": 0}
            results_by_category[category]["failed"] += 1
        
        print()
    
    print("=" * 80)
    print(f"OVERALL RESULTS: {passed}/{len(TEST_CASES)} passed, {failed}/{len(TEST_CASES)} failed")
    print(f"Success rate: {(passed/len(TEST_CASES)*100):.1f}%")
    print("=" * 80)
    print()
    print("RESULTS BY CATEGORY:")
    print("-" * 80)
    for category, stats in sorted(results_by_category.items()):
        total = stats["passed"] + stats["failed"]
        rate = (stats["passed"] / total * 100) if total > 0 else 0
        print(f"  {category:20s}: {stats['passed']:2d}/{total:2d} ({rate:5.1f}%)")
    print("=" * 80)
    
    return passed, failed


if __name__ == "__main__":
    asyncio.run(run_eval())
