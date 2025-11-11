# Quick Reference: Fallback Agent Usage

## Switching Between Agents

### Use OpenAI Agent (Recommended for Production)
```bash
# In backend/.env
OPENAI_API_KEY=sk-your-actual-api-key-here

# Restart backend
docker compose restart backend

# Verify
docker compose logs backend | grep "OpenAI client initialized"
```

### Use Fallback Agent (Development/Testing/No API Key)
```bash
# In backend/.env
OPENAI_API_KEY=

# Restart backend
docker compose restart backend

# Verify  
docker compose logs backend | grep "fallback"
```

## Supported Formats (Both Agents)

### Data Input Formats
```
Q1=100, Q2=150, Q3=200, Q4=175
2020=100, 2021=150, 2022=200
Jan=50, Feb=60, Mar=70
Apple=25, Banana=30, Orange=20
Product A=500, Product B=750
```

### Chart Type Requests
```
"Create a bar chart: ..."
"Make a line chart with ..."
"Show me a chart with ..."
"Chart these values: ..."
```

### Style Changes
```
"Change it to BNR colors"
"Use FD style"
"Make it in yellow colors"
"Create it in teal"
```

## Differences

| Feature | OpenAI | Fallback |
|---------|--------|----------|
| Natural language | Better | Basic |
| Data extraction | Flexible | Requires `key=value` format |
| Ambiguous requests | Handles well | May need clarification |
| Cost | $$ per request | Free |
| Speed | ~1-3 seconds | <100ms |
| Offline | No | Yes |

## When to Use Each

**OpenAI Agent:**
- Production with paying customers
- Complex/ambiguous user inputs
- Natural language processing needed
- Budget allows API costs

**Fallback Agent:**
- Development/testing
- Demo environments
- Cost-sensitive applications
- Offline requirements
- Simple, structured inputs

## Testing

```bash
# Test current mode
python3 test_final_verification.py

# Test with fallback specifically
# 1. Set OPENAI_API_KEY= in backend/.env
# 2. docker compose restart backend
# 3. python3 test_final_verification.py
```

## Troubleshooting

**OpenAI not working?**
- Check API key is valid
- Check internet connection
- View logs: `docker compose logs backend --tail=50`
- System auto-falls back to rule-based agent on error

**Fallback not extracting data?**
- Use `key=value` format
- Ensure spaces around `=` or no spaces consistently
- Provide at least 2 data points
- Use explicit chart type in request

## Examples

### OpenAI (More Flexible)
```
"Show me sales data for Q1 through Q4: 100, 150, 200, 175"
"I need a chart comparing our products, A is 500, B is 750"
"Can you visualize monthly revenue: Jan 50, Feb 60, Mar 70"
```

### Fallback (Needs Structure)
```
"Create a bar chart: Q1=100, Q2=150, Q3=200, Q4=175"
"Make a line chart with Jan=50, Feb=60, Mar=70"
"Chart: Product A=500, Product B=750"
```

## Logs

Check which agent is active:
```bash
docker compose logs backend | grep -E "(OpenAI|fallback)"
```

Expected output:
- With key: `INFO - OpenAI client initialized successfully`
- Without key: `WARNING - No OpenAI API key found. Using fallback rule-based agent.`
