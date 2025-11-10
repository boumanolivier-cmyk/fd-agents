"""
Test explicit chart type requests to verify priority over data-based inference
"""
import requests
import time

BASE_URL = "http://localhost:8000/api"

test_cases = [
    {
        "name": "Explicit BAR request with time data (quarters)",
        "message": "Create a bar chart: Q1=100, Q2=150, Q3=200, Q4=175",
        "expected_type": "bar",
        "reason": "User explicitly requested 'bar chart' - should override time series inference"
    },
    {
        "name": "Explicit LINE request with categorical data",
        "message": "Make a line chart: Apple=25, Banana=30, Orange=20",
        "expected_type": "line",
        "reason": "User explicitly requested 'line chart' - should override categorical inference"
    },
    {
        "name": "Explicit BAR request with year data",
        "message": "Show me a bar chart with 2020=100, 2021=150, 2022=200",
        "expected_type": "bar",
        "reason": "User explicitly requested 'bar chart' - should override time series inference"
    },
    {
        "name": "No explicit request - time data (should be line)",
        "message": "Chart this: Jan=50, Feb=60, Mar=70, Apr=80",
        "expected_type": "line",
        "reason": "No explicit request, months indicate time series - should be line"
    },
    {
        "name": "No explicit request - categorical data (should be bar)",
        "message": "Show chart: Dogs=40, Cats=35, Birds=25",
        "expected_type": "bar",
        "reason": "No explicit request, categories - should be bar"
    },
    {
        "name": "Explicit BAR with 'bar graph' variation",
        "message": "I need a bar graph: Q1=10, Q2=20, Q3=15, Q4=25",
        "expected_type": "bar",
        "reason": "User said 'bar graph' - should be bar"
    },
    {
        "name": "Explicit LINE with 'line graph' variation",
        "message": "Can you make a line graph with ProductA=100, ProductB=200, ProductC=150",
        "expected_type": "line",
        "reason": "User said 'line graph' - should be line even with categorical data"
    }
]

def run_tests():
    session_id = f"explicit-type-test-{int(time.time())}"
    
    print("=" * 80)
    print("EXPLICIT CHART TYPE PRIORITY TEST SUITE")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"TEST {i}/{len(test_cases)}: {test['name']}")
        print("-" * 80)
        print(f"Message: {test['message']}")
        print(f"Expected: {test['expected_type'].upper()} chart")
        print(f"Reason: {test['reason']}")
        print()
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"message": test['message'], "session_id": session_id},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "").lower()
                
                # Check if the response mentions the expected chart type
                if test['expected_type'] in response_text:
                    print(f"✅ PASS - Response: {data.get('response')}")
                    passed += 1
                else:
                    print(f"❌ FAIL - Expected '{test['expected_type']}' chart but got: {data.get('response')}")
                    failed += 1
            else:
                print(f"❌ FAIL - HTTP {response.status_code}: {response.text}")
                failed += 1
                
        except Exception as e:
            print(f"❌ FAIL - Error: {str(e)}")
            failed += 1
        
        print()
        time.sleep(1)  # Small delay between requests
    
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Passed: {passed}/{len(test_cases)}")
    print(f"Failed: {failed}/{len(test_cases)}")
    print(f"Success rate: {(passed/len(test_cases)*100):.1f}%")
    print("=" * 80)
    
    return passed == len(test_cases)

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
