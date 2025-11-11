"""
Evaluation 3: Test color scheme selection and persistence

This eval tests:
1. Agent's ability to detect appropriate color schemes from context
2. Persistence of color scheme decisions across requests
"""

import asyncio
import json
from pathlib import Path

from app.agents.chart_agent import analyze_chart_request
from app.services.persistence import persistence

# Test cases: (request, expected_color_scheme, description)
COLOR_SCHEME_TESTS = [
    # FD (Financial Dagblad) - Financial/Business context
    (
        "Create a chart of quarterly revenue: Q1=1.2M, Q2=1.5M, Q3=1.8M, Q4=2.1M",
        "fd",
        "Quarterly revenue (financial keyword)",
    ),
    (
        "Show stock market performance: Monday=150, Tuesday=155, Wednesday=148, Thursday=152, Friday=156",
        "fd",
        "Stock market (financial context)",
    ),
    (
        "Chart corporate profits: 2020=5.2B, 2021=6.1B, 2022=7.5B, 2023=8.9B",
        "fd",
        "Corporate profits (business keyword)",
    ),
    (
        "Make a chart of investment returns: Fund A=8.5%, Fund B=7.2%, Fund C=9.1%, Fund D=7.8%",
        "fd",
        "Investment returns (financial keyword)",
    ),
    (
        "Create a chart showing economic growth: 2020=2.1%, 2021=3.5%, 2022=2.8%, 2023=3.2%",
        "fd",
        "Economic growth (economics keyword)",
    ),
    (
        "Show me market share data: CompanyA=35%, CompanyB=28%, CompanyC=22%, CompanyD=15%",
        "fd",
        "Market share (business context)",
    ),
    (
        "Chart the bond yields: 1Y=3.2%, 5Y=3.8%, 10Y=4.1%, 30Y=4.5%",
        "fd",
        "Bond yields (financial instrument)",
    ),
    # BNR (BNR Nieuwsradio) - News/Media/Broadcasting context
    (
        "Chart BNR listener numbers: Monday=50K, Tuesday=52K, Wednesday=48K, Thursday=55K, Friday=58K",
        "bnr",
        "BNR explicitly mentioned",
    ),
    (
        "Show news broadcast ratings: Morning=125K, Afternoon=95K, Evening=180K, Night=45K",
        "bnr",
        "News broadcast (media keyword)",
    ),
    (
        "Create a chart of radio show popularity: Show A=75, Show B=82, Show C=68, Show D=91",
        "bnr",
        "Radio show (broadcasting keyword)",
    ),
    (
        "Make a chart of media coverage: Print=120, Online=450, TV=380, Radio=210",
        "bnr",
        "Media coverage (media keyword)",
    ),
    (
        "Chart podcast downloads: Episode1=25K, Episode2=28K, Episode3=32K, Episode4=29K",
        "bnr",
        "Podcast (broadcasting/media)",
    ),
    (
        "Show entertainment viewership: Series A=1.2M, Series B=950K, Series C=1.5M",
        "bnr",
        "Entertainment (lifestyle/media)",
    ),
    # Neutral/Default - Should default to FD
    ("Chart this data: A=10, B=20, C=30, D=40", "fd", "No context - defaults to FD"),
    (
        "Make a chart: Monday=5, Tuesday=7, Wednesday=6, Thursday=8",
        "fd",
        "Generic days - defaults to FD",
    ),
    (
        "Create a chart: Product1=100, Product2=150, Product3=120",
        "fd",
        "Generic products - defaults to FD",
    ),
]


async def test_color_scheme_detection():
    """Test that agent correctly detects color schemes from context"""
    print("=" * 80)
    print("COLOR SCHEME DETECTION TESTS")
    print("=" * 80)
    print()

    passed = 0
    failed = 0

    for i, (request, expected_color, description) in enumerate(COLOR_SCHEME_TESTS, 1):
        print(f"Test {i}/{len(COLOR_SCHEME_TESTS)}: {description}")
        print(f"  Request: '{request[:70]}...'")

        try:
            result = await analyze_chart_request(request)

            if not result.is_valid:
                print(f"  ❌ FAIL: Request was rejected")
                print(f"  Reason: {result.reason}")
                failed += 1
            elif result.color_scheme == expected_color:
                print(f"  ✅ PASS: Color scheme = {result.color_scheme}")
                passed += 1
            else:
                print(f"  ❌ FAIL: Expected {expected_color}, got {result.color_scheme}")
                failed += 1

        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            failed += 1

        print()

    print("=" * 80)
    print(f"DETECTION RESULTS: {passed}/{len(COLOR_SCHEME_TESTS)} passed")
    print("=" * 80)
    print()

    return passed, failed


async def test_color_change_conversation():
    """Test that agent handles color/style change requests in conversation"""
    print("=" * 80)
    print("COLOR CHANGE IN CONVERSATION TESTS")
    print("=" * 80)
    print()

    # Simulate conversation history
    conversation_history = [
        {
            "role": "user",
            "content": "Create a bar chart: Q1=100, Q2=150, Q3=200, Q4=175",
            "timestamp": "2025-11-11T10:00:00",
        },
        {
            "role": "assistant",
            "content": "I've created a bar chart for you!",
            "timestamp": "2025-11-11T10:00:01",
            "metadata": {
                "chart_type": "bar",
                "x_labels": ["Q1", "Q2", "Q3", "Q4"],
                "y_values": [100.0, 150.0, 200.0, 175.0],
            },
        },
    ]

    # Test cases: (request, expected_color, description)
    conversation_tests = [
        ("Could you now create it in the BNR colors?", "bnr", "Request to change to BNR colors"),
        ("Change to FD style", "fd", "Request to change to FD style"),
        ("Make it with yellow colors", "bnr", "Request for yellow colors (BNR)"),
        ("Use the teal color scheme", "fd", "Request for teal colors (FD)"),
        ("Can you recreate it in BNR style?", "bnr", "Request to recreate in BNR style"),
    ]

    passed = 0
    failed = 0

    for i, (request, expected_color, description) in enumerate(conversation_tests, 1):
        print(f"Test {i}/{len(conversation_tests)}: {description}")
        print(f"  Request: '{request}'")

        try:
            result = await analyze_chart_request(request, conversation_history)

            # Check if request was accepted
            if not result.is_valid:
                print(f"  ❌ FAIL: Request was refused")
                print(f"  Reason: {result.reason}")
                failed += 1
                print()
                continue

            # Check if data was extracted from history
            if not result.x_labels or not result.y_values:
                print(f"  ❌ FAIL: No data extracted from conversation")
                failed += 1
                print()
                continue

            # Check if correct color scheme was selected
            if result.color_scheme == expected_color:
                print(f"  ✅ PASS: Color = {result.color_scheme}, Data = {result.x_labels}")
                passed += 1
            else:
                print(f"  ❌ FAIL: Expected {expected_color}, got {result.color_scheme}")
                failed += 1

        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            failed += 1

        print()

    print("=" * 80)
    print(f"CONVERSATION RESULTS: {passed}/{len(conversation_tests)} passed")
    print("=" * 80)
    print()

    return passed, failed


async def test_color_scheme_persistence():
    """Test that color scheme decisions are persisted"""
    print("=" * 80)
    print("COLOR SCHEME PERSISTENCE TESTS")
    print("=" * 80)
    print()

    memory_file = Path("/app/data/persistent-memory.json")

    # Test 1: Initial state should be 'fd'
    print("Test 1: Check initial persistent memory")
    initial_color = persistence.get_persistent_color_scheme()
    if initial_color == "fd":
        print(f"  ✅ PASS: Initial color scheme is 'fd'")
        test1_pass = True
    else:
        print(f"  ❌ FAIL: Expected 'fd', got '{initial_color}'")
        test1_pass = False
    print()

    # Test 2: Set to BNR and verify persistence
    print("Test 2: Set color scheme to 'bnr'")
    persistence.set_persistent_color_scheme("bnr")

    # Read directly from file to verify
    with open(memory_file, "r") as f:
        data = json.load(f)

    if data.get("color_scheme") == "bnr":
        print(f"  ✅ PASS: Color scheme persisted to file as 'bnr'")
        test2_pass = True
    else:
        print(f"  ❌ FAIL: Expected 'bnr' in file, got '{data.get('color_scheme')}'")
        test2_pass = False
    print()

    # Test 3: Verify retrieval after persistence
    print("Test 3: Retrieve persisted color scheme")
    retrieved_color = persistence.get_persistent_color_scheme()
    if retrieved_color == "bnr":
        print(f"  ✅ PASS: Retrieved 'bnr' from persistent memory")
        test3_pass = True
    else:
        print(f"  ❌ FAIL: Expected 'bnr', got '{retrieved_color}'")
        test3_pass = False
    print()

    # Test 4: Agent decision updates persistent memory
    print("Test 4: Agent decision updates persistent memory")

    # Reset to FD first
    persistence.set_persistent_color_scheme("fd")

    # Make a BNR-related request
    result = await analyze_chart_request(
        "Chart BNR listener data: Monday=50K, Tuesday=52K, Wednesday=48K"
    )

    # If agent decided on BNR, simulate what the route would do
    if result.color_scheme == "bnr":
        persistence.set_persistent_color_scheme(result.color_scheme)

    # Check if it was persisted
    final_color = persistence.get_persistent_color_scheme()
    if result.color_scheme == "bnr" and final_color == "bnr":
        print(f"  ✅ PASS: Agent selected 'bnr' and it was persisted")
        test4_pass = True
    else:
        print(f"  ❌ FAIL: Agent={result.color_scheme}, Persisted={final_color}")
        test4_pass = False
    print()

    # Cleanup: Reset to FD
    persistence.set_persistent_color_scheme("fd")

    print("=" * 80)
    passed = sum([test1_pass, test2_pass, test3_pass, test4_pass])
    print(f"PERSISTENCE RESULTS: {passed}/4 passed")
    print("=" * 80)
    print()

    return passed, 4 - passed


async def run_eval():
    """Run all color scheme evaluation tests"""
    print("=" * 80)
    print("EVALUATION 3: Color Scheme Selection and Persistence")
    print("=" * 80)
    print()

    # Run detection tests
    detection_passed, detection_failed = await test_color_scheme_detection()

    # Run conversation tests (NEW)
    conversation_passed, conversation_failed = await test_color_change_conversation()

    # Run persistence tests
    persistence_passed, persistence_failed = await test_color_scheme_persistence()

    # Final summary
    total_passed = detection_passed + conversation_passed + persistence_passed
    total_tests = len(COLOR_SCHEME_TESTS) + 5 + 4  # detection + conversation + persistence
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print("=" * 80)
    print("OVERALL COLOR SCHEME EVAL SUMMARY")
    print("=" * 80)
    print(f"Detection Tests: {detection_passed}/{len(COLOR_SCHEME_TESTS)} passed")
    print(f"Conversation Tests: {conversation_passed}/5 passed")
    print(f"Persistence Tests: {persistence_passed}/4 passed")
    print(f"Total: {total_passed}/{total_tests} passed ({success_rate:.1f}%)")

    if success_rate >= 90:
        print(f"\n✅ SUCCESS - Color scheme eval passed at {success_rate:.1f}%")
    else:
        print(f"\n⚠️  BELOW TARGET - Color scheme eval at {success_rate:.1f}% (target: 90%)")

    print("=" * 80)

    return success_rate


if __name__ == "__main__":
    asyncio.run(run_eval())
