"""
Evaluation 2: Test that the agent correctly extracts chart data

Tests data extraction accuracy including:
- X-axis labels extraction
- Y-axis values extraction
- Chart type selection (respects explicit requests)
- Handling of different data formats
"""

import asyncio

from app.agents.chart_agent import analyze_chart_request

# Test cases: (request, expected_data, allow_flexible_chart_type)
TEST_CASES = [
    (
        "Give me a chart with the number of check-ins per day for public transport (OV): Monday=4.1, Tuesday=4.2, Wednesday=4.4, Thursday=4.7, Friday=4.2, Saturday=2.3, Sunday=1.7",
        {
            "chart_type": "line",  # Days = time series, should be line
            "x_labels": [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ],
            "y_values": [4.1, 4.2, 4.4, 4.7, 4.2, 2.3, 1.7],
            "color_scheme": None,  # No specific color scheme expected
        },
        True,  # Flexible - could be bar or line for days
    ),
    (
        "I want a chart that shows how many billion euros of student debt students have in recent years. The values are: 2020 = 25, 2021 = 26, 2022 = 26.5, 2023 = 27.3, 2024 = 27.9, 2025 = 29",
        {
            "chart_type": "line",  # Time series, should be line
            "x_labels": ["2020", "2021", "2022", "2023", "2024", "2025"],
            "y_values": [25.0, 26.0, 26.5, 27.3, 27.9, 29.0],
            "color_scheme": "fd",  # Financial/debt data = FD
        },
        False,  # Strict - years should always be line
    ),
    (
        "Make a bar chart: Apple=50, Banana=30, Orange=45",
        {
            "chart_type": "bar",  # Explicit bar request
            "x_labels": ["Apple", "Banana", "Orange"],
            "y_values": [50.0, 30.0, 45.0],
            "color_scheme": None,  # No specific color scheme expected
        },
        False,  # Strict - explicit request must be honored
    ),
    # Additional test cases for better coverage
    (
        "Create a bar chart: Q1=100, Q2=150, Q3=200, Q4=175",
        {
            "chart_type": "bar",  # Explicit bar request (should override time series)
            "x_labels": ["Q1", "Q2", "Q3", "Q4"],
            "y_values": [100.0, 150.0, 200.0, 175.0],
            "color_scheme": None,  # No specific color scheme expected
        },
        False,  # Strict - explicit bar request
    ),
    (
        "Show me a line chart: North=500, South=750, East=600, West=550",
        {
            "chart_type": "line",  # Explicit line request (should override categorical)
            "x_labels": ["North", "South", "East", "West"],
            "y_values": [500.0, 750.0, 600.0, 550.0],
            "color_scheme": None,  # No specific color scheme expected
        },
        False,  # Strict - explicit line request
    ),
    (
        "Chart this financial data: 2020=10.5, 2021=12.3, 2022=15.8, 2023=18.2",
        {
            "chart_type": "line",  # Years = time series (no explicit type)
            "x_labels": ["2020", "2021", "2022", "2023"],
            "y_values": [10.5, 12.3, 15.8, 18.2],
            "color_scheme": "fd",  # Financial keyword = FD
        },
        False,  # Strict - time series should be line
    ),
    (
        "Make a chart with ProductA=1250, ProductB=980, ProductC=1450, ProductD=1100",
        {
            "chart_type": "bar",  # Products = categories (no explicit type)
            "x_labels": ["ProductA", "ProductB", "ProductC", "ProductD"],
            "y_values": [1250.0, 980.0, 1450.0, 1100.0],
            "color_scheme": None,  # No specific color scheme expected
        },
        False,  # Strict - categorical should be bar
    ),
    (
        "Create a line chart showing Jan=25.5, Feb=27.8, Mar=26.3, Apr=29.1, May=31.5, Jun=33.2",
        {
            "chart_type": "line",  # Explicit line + months = definitely line
            "x_labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "y_values": [25.5, 27.8, 26.3, 29.1, 31.5, 33.2],
            "color_scheme": None,  # No specific color scheme expected
        },
        False,  # Strict - explicit request
    ),
    (
        "Bar chart: Dog=42, Cat=38, Bird=25, Fish=15",
        {
            "chart_type": "bar",  # Starts with "Bar chart"
            "x_labels": ["Dog", "Cat", "Bird", "Fish"],
            "y_values": [42.0, 38.0, 25.0, 15.0],
            "color_scheme": None,  # No specific color scheme expected
        },
        False,  # Strict - explicit bar
    ),
    (
        "Plot this: Week1=100, Week2=120, Week3=105, Week4=130, Week5=125",
        {
            "chart_type": "line",  # Weeks = time series
            "x_labels": ["Week1", "Week2", "Week3", "Week4", "Week5"],
            "y_values": [100.0, 120.0, 105.0, 130.0, 125.0],
            "color_scheme": None,  # No specific color scheme expected
        },
        False,  # Strict - time series
    ),
    # NEW: Color scheme specific tests
    (
        "Chart corporate revenue: Q1=2.5M, Q2=3.1M, Q3=3.8M, Q4=4.2M",
        {
            "chart_type": "line",  # Quarters = time series
            "x_labels": ["Q1", "Q2", "Q3", "Q4"],
            "y_values": [2.5, 3.1, 3.8, 4.2],
            "color_scheme": "fd",  # Corporate/revenue = FD
        },
        False,  # Strict
    ),
    (
        "Show BNR news ratings: Morning=125K, Afternoon=95K, Evening=180K",
        {
            "chart_type": "bar",  # Categories
            "x_labels": ["Morning", "Afternoon", "Evening"],
            "y_values": [125.0, 95.0, 180.0],
            "color_scheme": "bnr",  # BNR explicitly mentioned = BNR
        },
        False,  # Strict
    ),
]


def check_data_match(actual, expected, allow_flexible_chart_type=False):
    """
    Check if extracted data matches expected data

    Args:
        actual: The ChartData result from the agent
        expected: Expected data dict with chart_type, x_labels, y_values, color_scheme
        allow_flexible_chart_type: If True, allows either bar or line for chart_type

    Returns:
        List of error messages (empty if all checks pass)
    """
    errors = []

    # Check chart type
    if not allow_flexible_chart_type:
        if actual.chart_type != expected["chart_type"]:
            errors.append(
                f"Chart type mismatch: expected {expected['chart_type']}, "
                f"got {actual.chart_type}"
            )
    else:
        # For flexible cases, just verify it's a valid chart type
        if actual.chart_type not in ["bar", "line"]:
            errors.append(
                f"Invalid chart type: got {actual.chart_type}, " f"expected 'bar' or 'line'"
            )

    # Check color scheme if specified in expected
    if "color_scheme" in expected and expected["color_scheme"] is not None:
        if actual.color_scheme != expected["color_scheme"]:
            errors.append(
                f"Color scheme mismatch: expected {expected['color_scheme']}, "
                f"got {actual.color_scheme}"
            )

    # Check x_labels
    if actual.x_labels != expected["x_labels"]:
        errors.append(
            f"X-labels mismatch: expected {expected['x_labels']}, " f"got {actual.x_labels}"
        )

    # Check y_values (with some tolerance for floating point)
    if actual.y_values:
        if len(actual.y_values) != len(expected["y_values"]):
            errors.append(
                f"Y-values length mismatch: expected {len(expected['y_values'])}, "
                f"got {len(actual.y_values)}"
            )
        else:
            for i, (actual_val, expected_val) in enumerate(
                zip(actual.y_values, expected["y_values"])
            ):
                if abs(actual_val - expected_val) > 0.01:  # Small tolerance for floating point
                    errors.append(
                        f"Y-value mismatch at index {i}: expected {expected_val}, "
                        f"got {actual_val}"
                    )
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

    for i, (request, expected, allow_flexible) in enumerate(TEST_CASES, 1):
        print(f"Test {i}/{len(TEST_CASES)}:")
        print(f"  Request: '{request[:80]}...'")
        if allow_flexible:
            print(f"  (Flexible chart type allowed)")
        print()

        try:
            result = await analyze_chart_request(request)

            if not result.is_valid:
                print(f"  ❌ FAIL: Request was refused (should be accepted)")
                print(f"  Reason: {result.reason}")
                failed += 1
            else:
                errors = check_data_match(
                    result, expected, allow_flexible_chart_type=allow_flexible
                )

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
