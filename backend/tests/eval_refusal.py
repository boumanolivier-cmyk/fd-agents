"""
Evaluation 1: Test that the agent correctly refuses/allows chart requests
"""
import asyncio
from app.agents.chart_agent import analyze_chart_request


# Test cases: (request, should_accept)
TEST_CASES = [
    # Should ACCEPT - valid chart requests
    ("Make a bar chart showing sales by month", True),
    ("Create a line chart of temperature over time", True),
    ("Give me a chart with Monday=4.1, Tuesday=4.2, Wednesday=4.4", True),
    ("I want a chart that shows student debt over the years", True),
    ("Show me a bar chart comparing revenue across regions", True),
    ("Can you make a line chart for this data: 2020=25, 2021=26, 2022=26.5", True),
    ("Chart the number of check-ins per day", True),
    
    # Should REFUSE - not chart requests
    ("What's the weather today?", False),
    ("Help me write an essay", False),
    ("Can you make a pie chart?", False),
    ("Tell me a joke", False),
    ("What's 2+2?", False),
    ("Write me a poem about charts", False),
    ("How do I cook pasta?", False),
    ("Can you help with my homework?", False),
    ("Make me a scatter plot", False),
    ("Create a histogram", False),
]


async def run_eval():
    """Run the evaluation tests"""
    print("=" * 80)
    print("EVALUATION 1: Request Validation (Refusal/Acceptance)")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for i, (request, should_accept) in enumerate(TEST_CASES, 1):
        print(f"Test {i}/{len(TEST_CASES)}: ", end="")
        
        try:
            result = await analyze_chart_request(request)
            actual_accept = result.is_valid
            
            if actual_accept == should_accept:
                print(f"✅ PASS")
                print(f"  Request: '{request}'")
                print(f"  Expected: {'ACCEPT' if should_accept else 'REFUSE'}")
                print(f"  Actual: {'ACCEPT' if actual_accept else 'REFUSE'}")
                if not actual_accept:
                    print(f"  Reason: {result.reason}")
                passed += 1
            else:
                print(f"❌ FAIL")
                print(f"  Request: '{request}'")
                print(f"  Expected: {'ACCEPT' if should_accept else 'REFUSE'}")
                print(f"  Actual: {'ACCEPT' if actual_accept else 'REFUSE'}")
                if result.reason:
                    print(f"  Reason: {result.reason}")
                failed += 1
        
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            failed += 1
        
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed}/{len(TEST_CASES)} passed, {failed}/{len(TEST_CASES)} failed")
    print(f"Success rate: {(passed/len(TEST_CASES)*100):.1f}%")
    print("=" * 80)
    
    return passed, failed


if __name__ == "__main__":
    asyncio.run(run_eval())
