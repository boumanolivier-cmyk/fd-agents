# Test Suite

## 🚀 TL;DR

```bash
# Run all tests
python tests/run_evals.py

# Run individual tests
python tests/eval_refusal.py      # Request validation
python tests/eval_chart_data.py   # Data extraction
python tests/eval_color_scheme.py # Color scheme selection

# Run in Docker
docker compose exec backend python tests/run_evals.py
```

**Expected:** 94%+ success rate across 51 test cases

---

This directory contains the evaluation suite for the AI Chart Generator.

## Overview

The test suite consists of three main evaluations that verify the core functionality of the application:

### 1. Eval 1: Request Validation (`eval_refusal.py`)
**Purpose:** Verify that the agent correctly accepts valid chart requests and refuses invalid ones.

**Tests:**
- ✅ Accepts chart requests with concrete data (e.g., "Monday=4.1, Tuesday=4.2")
- ✅ Accepts explicit chart type requests (e.g., "Create a bar chart: Q1=100, Q2=150")
- ❌ Refuses vague requests without data (e.g., "Make a chart showing sales")
- ❌ Refuses off-topic requests (e.g., "What's the weather?")
- ❌ Refuses unsupported chart types (e.g., "Make a pie chart")

**Acceptance Criteria:** Correctly identifies valid/invalid requests

### 2. Eval 2: Data Extraction (`eval_chart_data.py`)
**Purpose:** Verify that the agent correctly extracts chart data and selects appropriate chart types.

**Tests:**
- Extracts x-axis labels accurately
- Extracts y-axis values correctly
- Respects explicit chart type requests (e.g., "bar chart" → bar chart)
- Intelligently selects chart type based on data (time series → line, categories → bar)
- Detects appropriate color schemes based on context (financial → FD, news → BNR)

**Acceptance Criteria:** Data extraction accuracy and smart chart type selection

### 3. Eval 3: Color Scheme Selection (`eval_color_scheme.py`)
**Purpose:** Verify intelligent color scheme selection and persistence.

**Tests:**
- Detects FD colors for financial/business contexts
- Detects BNR colors for news/media contexts
- Handles explicit color scheme requests
- Tests persistence across conversation
- Validates manual style changes

**Acceptance Criteria:** Correct color scheme selection and persistence

## Running the Tests

### Run All Tests
```bash
# From project root
cd backend
python tests/run_evals.py
```

### Run Individual Evaluations
```bash
# Eval 1: Request Validation
python tests/eval_refusal.py

# Eval 2: Data Extraction
python tests/eval_chart_data.py

# Eval 3: Color Scheme Selection
python tests/eval_color_scheme.py
```

### Run Tests in Docker
```bash
# From project root
docker compose exec backend python tests/run_evals.py
```

## Expected Results

All evaluations should pass with:
- **Eval 1:** 100% accuracy on request validation
- **Eval 2:** 100% accuracy on data extraction
- **Eval 3:** ≥90% accuracy on color scheme selection

## Test Data

Tests use predefined test cases that cover:
- Various data formats and structures
- Different chart types (bar, line)
- Edge cases and boundary conditions
- Real-world usage scenarios
- Conversation context and memory

## Adding New Tests

To add new test cases:

1. Open the relevant eval file (e.g., `eval_refusal.py`)
2. Add your test case to the `TEST_CASES` list
3. Run the evaluation to verify
4. Update this README if adding a new evaluation category

## Troubleshooting

If tests fail:

1. **Check API keys:** Ensure `OPENAI_API_KEY` is set in `backend/.env`
2. **Check dependencies:** Run `pip install -r requirements.txt`
3. **Check logs:** Look at console output for detailed error messages
4. **Run individual tests:** Isolate failures by running specific evals

## Acceptance Criteria (Dutch Requirements)

This test suite fulfills the requirement:
> **7. 2 evals**
> - ✅ Eval 1: Correct weigeren/toelaten request (eval_refusal.py)
> - ✅ Eval 2: Juiste data in grafiek (eval_chart_data.py)
> - ✅ Bonus Eval 3: Color scheme selection (eval_color_scheme.py)
