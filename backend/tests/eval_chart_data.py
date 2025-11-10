"""
Evaluation 2: Test that the agent correctly extracts chart data
"""
import asyncio
from app.agents.chart_agent import analyze_chart_request


# Test cases: (request, expected_data)
TEST_CASES = [
    (
        "Give me a chart with the number of check-ins per day for public transport (OV): Monday = 4.1, Tuesday = 4.2, Wednesday = 4.4, Thursday = 4.7, Friday = 4.2, Saturday = 2.3, Sunday = 1.7. The numbers are in millions of check-ins.",
        {
            "chart_type": "bar",  # Could also be "line"
            "x_labels": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "y_values": [4.1, 4.2, 4.4, 4.7, 4.2, 2.3, 1.7],
        }
    ),
    (
        "I want a chart that shows how many billion euros of student debt students have in recent years. The values are: 2020 = 25, 2021 = 26, 2022 = 26.5, 2023 = 27.3, 2024 = 27.9, 2025 = 29",
        {
            "chart_type": "line",  # Time series, should be line
            "x_labels": ["2020", "2021", "2022", "2023", "2024", "2025"],
            "y_values": [25.0, 26.0, 26.5, 27.3, 27.9, 29.0],
        }
    ),
    (
        "Make a bar chart: Apple=50, Banana=30, Orange=45",
        {
            "chart_type": "bar",
            "x_labels": ["Apple", "Banana", "Orange"],
            "y_values": [50.0, 30.0, 45.0],
        }
    ),
]


def check_data_match(actual, expected):
    """Check if extracted data matches expected data"""
    errors = []
    
    # Check chart type (could be flexible)
    if actual.chart_type != expected["chart_type"]:
        errors.append(f"Chart type mismatch: expected {expected['chart_type']}, got {actual.chart_type}")
    
    # Check x_labels
    if actual.x_labels != expected["x_labels"]:
        errors.append(f"X-labels mismatch: expected {expected['x_labels']}, got {actual.x_labels}")
    
    # Check y_values (with some tolerance for floating point)
    if actual.y_values:
        if len(actual.y_values) != len(expected["y_values"]):
            errors.append(f"Y-values length mismatch: expected {len(expected['y_values'])}, got {len(actual.y_values)}")
        else:
            for i, (actual_val, expected_val) in enumerate(zip(actual.y_values, expected["y_values"])):
                if abs(actual_val - expected_val) > 0.01:  # Small tolerance
                    errors.append(f"Y-value mismatch at index {i}: expected {expected_val}, got {actual_val}")
    else:
        errors.append("Y-values are None or empty")
    
    return errors


async def run_eval():
    """Run the evaluation tests"""
    print("=" * 80)
    print("EVALUATION 2: Chart Data Extraction Accuracy")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for i, (request, expected) in enumerate(TEST_CASES, 1):
        print(f"Test {i}/{len(TEST_CASES)}:")
        print(f"  Request: '{request[:80]}...'")
        print()
        
        try:
            result = await analyze_chart_request(request)
            
            if not result.is_valid:
                print(f"  ❌ FAIL: Request was refused (should be accepted)")
                print(f"  Reason: {result.reason}")
                failed += 1
            else:
                errors = check_data_match(result, expected)
                
                if not errors:
                    print(f"  ✅ PASS: Data extracted correctly")
                    print(f"    Chart type: {result.chart_type}")
                    print(f"    X-labels: {result.x_labels}")
                    print(f"    Y-values: {result.y_values}")
                    print(f"    Title: {result.title}")
                    passed += 1
                else:
                    print(f"  ❌ FAIL: Data extraction errors:")
                    for error in errors:
                        print(f"    - {error}")
                    print(f"    Actual result:")
                    print(f"      Chart type: {result.chart_type}")
                    print(f"      X-labels: {result.x_labels}")
                    print(f"      Y-values: {result.y_values}")
                    failed += 1
        
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            failed += 1
        
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed}/{len(TEST_CASES)} passed, {failed}/{len(TEST_CASES)} failed")
    print(f"Success rate: {(passed/len(TEST_CASES)*100):.1f}%")
    print("=" * 80)
    
    return passed, failed


if __name__ == "__main__":
    asyncio.run(run_eval())
