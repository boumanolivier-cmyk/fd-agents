"""
Evaluation 1: Test that the agent correctly refuses/allows chart requests

This eval tests the STRICT behavior where the agent requires concrete data points.
Vague requests without data are correctly refused.
"""
import asyncio
from app.agents.chart_agent import analyze_chart_request


# Test cases: (request, should_accept, category, expected_color_scheme)
# expected_color_scheme is optional - None means we don't test for it
TEST_CASES = [
    # Should ACCEPT - valid chart requests WITH DATA
    ("Give me a chart with Monday=4.1, Tuesday=4.2, Wednesday=4.4", True, "concrete_data", None),
    ("Can you make a line chart for this data: 2020=25, 2021=26, 2022=26.5", True, "concrete_data", None),
    ("Create a bar chart: Q1=100, Q2=150, Q3=200, Q4=175", True, "explicit_with_data", None),
    ("Show me a line chart: Jan=50, Feb=60, Mar=70, Apr=80", True, "explicit_with_data", None),
    ("Make a chart with Apple=25, Banana=30, Orange=20, Grape=15", True, "concrete_data", None),
    ("Chart this: ProductA=100, ProductB=150, ProductC=200", True, "concrete_data", None),
    ("I need a bar chart with North=500, South=750, East=600, West=550", True, "explicit_with_data", None),
    ("Create a line chart showing: 2020=10, 2021=15, 2022=20, 2023=25", True, "explicit_with_data", None),
    ("Make a bar graph: Dogs=40, Cats=35, Birds=25", True, "explicit_with_data", None),
    ("Plot this data: Week1=100, Week2=120, Week3=115, Week4=130", True, "concrete_data", None),
    
    # NEW: Test color scheme detection (FD for financial/business)
    ("Create a chart of quarterly revenue: Q1=1.2M, Q2=1.5M, Q3=1.8M, Q4=2.1M", True, "concrete_data", "fd"),
    ("Show me stock prices: Monday=150, Tuesday=155, Wednesday=148, Thursday=152", True, "concrete_data", "fd"),
    ("Chart corporate profits: 2020=5.2B, 2021=6.1B, 2022=7.5B, 2023=8.9B", True, "concrete_data", "fd"),
    ("Make a chart of investment returns: Fund A=8.5%, Fund B=7.2%, Fund C=9.1%", True, "concrete_data", "fd"),
    
    # NEW: Test color scheme detection (BNR for news/media)
    ("Chart BNR listener numbers: Monday=50K, Tuesday=52K, Wednesday=48K, Thursday=55K", True, "concrete_data", "bnr"),
    ("Show me news broadcast ratings: Morning=125K, Afternoon=95K, Evening=180K", True, "concrete_data", "bnr"),
    ("Create a chart of radio show popularity: Show A=75, Show B=82, Show C=68", True, "concrete_data", "bnr"),
    
    # Should REFUSE - vague requests WITHOUT concrete data (strict behavior)
        # Should REFUSE - vague requests WITHOUT concrete data (strict behavior)
    ("Make a bar chart showing sales by month", False, "vague_no_data", None),
    ("Create a line chart of temperature over time", False, "vague_no_data", None),
    ("I want a chart that shows student debt over the years", False, "vague_no_data", None),
    ("Show me a bar chart comparing revenue across regions", False, "vague_no_data", None),
    ("Chart the number of check-ins per day", False, "vague_no_data", None),
    ("Make a chart about quarterly earnings", False, "vague_no_data", None),
    ("Show sales trends", False, "vague_no_data", None),
    
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
        # Parse test case - support both old format (3 items) and new format (4 items)
        if len(test_case) == 4:
            request, should_accept, category, expected_color = test_case
        elif len(test_case) == 3:
            request, should_accept, category = test_case
            expected_color = None
        else:
            request, should_accept = test_case
            category = "uncategorized"
            expected_color = None
        
        print(f"Test {i}/{len(TEST_CASES)} [{category}]: ", end="")
        
        try:
            result = await analyze_chart_request(request)
            actual_accept = result.is_valid
            
            # Check acceptance/refusal
            accept_correct = actual_accept == should_accept
            
            # Check color scheme if expected
            color_correct = True
            if expected_color and result.is_valid:
                color_correct = result.color_scheme == expected_color
            
            if accept_correct and color_correct:
                print(f"✅ PASS")
                print(f"  Request: '{request}'")
                print(f"  Expected: {'ACCEPT' if should_accept else 'REFUSE'}")
                print(f"  Actual: {'ACCEPT' if actual_accept else 'REFUSE'}")
                if expected_color:
                    print(f"  Color Scheme: {result.color_scheme} (expected: {expected_color})")
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
                if expected_color:
                    print(f"  Expected Color: {expected_color}")
                    print(f"  Actual Color: {result.color_scheme}")
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
