"""
Test for color/style change requests in conversation

This test verifies that when a user asks to change colors/styling,
the agent correctly treats it as a valid chart request and extracts
data from previous conversation.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.chart_agent import analyze_chart_request


async def test_color_change_conversation():
    """Test that agent handles color/style change requests correctly"""
    print("=" * 80)
    print("TEST: Color/Style Change Request Handling")
    print("=" * 80)
    print()
    
    # Simulate conversation history
    conversation_history = [
        {
            "role": "user",
            "content": "Create a bar chart: Q1=100, Q2=150, Q3=200, Q4=175",
            "timestamp": "2025-11-11T10:00:00"
        },
        {
            "role": "assistant",
            "content": "I've created a bar chart for you!",
            "timestamp": "2025-11-11T10:00:01",
            "metadata": {
                "chart_type": "bar",
                "x_labels": ["Q1", "Q2", "Q3", "Q4"],
                "y_values": [100.0, 150.0, 200.0, 175.0]
            }
        }
    ]
    
    # Test cases: (request, expected_accept, expected_color_scheme, description)
    test_cases = [
        (
            "Could you now create it in the BNR colors?",
            True,
            "bnr",
            "Request to change to BNR colors"
        ),
        (
            "Change to FD style",
            True,
            "fd",
            "Request to change to FD style"
        ),
        (
            "Make it with yellow colors",
            True,
            "bnr",
            "Request for yellow colors (BNR)"
        ),
        (
            "Use the teal color scheme",
            True,
            "fd",
            "Request for teal colors (FD)"
        ),
        (
            "Can you recreate it in BNR style?",
            True,
            "bnr",
            "Request to recreate in BNR style"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for i, (request, expected_accept, expected_color, description) in enumerate(test_cases, 1):
        print(f"Test {i}/{len(test_cases)}: {description}")
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
                print(f"  ❌ FAIL: No data extracted from conversation history")
                print(f"  x_labels: {result.x_labels}")
                print(f"  y_values: {result.y_values}")
                failed += 1
                print()
                continue
            
            # Check if correct data was extracted
            expected_x = ["Q1", "Q2", "Q3", "Q4"]
            expected_y = [100.0, 150.0, 200.0, 175.0]
            
            if result.x_labels != expected_x or result.y_values != expected_y:
                print(f"  ❌ FAIL: Incorrect data extracted")
                print(f"  Expected: x={expected_x}, y={expected_y}")
                print(f"  Got: x={result.x_labels}, y={result.y_values}")
                failed += 1
                print()
                continue
            
            # Check if correct color scheme was selected
            if result.color_scheme != expected_color:
                print(f"  ❌ FAIL: Wrong color scheme")
                print(f"  Expected: {expected_color}")
                print(f"  Got: {result.color_scheme}")
                failed += 1
                print()
                continue
            
            print(f"  ✅ PASS")
            print(f"  Data extracted: {result.x_labels}")
            print(f"  Color scheme: {result.color_scheme}")
            passed += 1
            
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            failed += 1
        
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed}/{len(test_cases)} passed")
    success_rate = (passed / len(test_cases) * 100) if len(test_cases) > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    print("=" * 80)
    
    return passed, failed


if __name__ == "__main__":
    asyncio.run(test_color_change_conversation())
