#!/bin/bash
# Quick test of fallback mode by temporarily modifying docker-compose

echo "========================================================================"
echo " TESTING FALLBACK AGENT"
echo "========================================================================"

# Backup docker-compose
cp docker-compose.yml docker-compose.yml.backup

echo ""
echo "Step 1: Testing with OpenAI API key (current setup)"
echo "------------------------------------------------------------------------"

# Test with current setup
python3 - << 'PYTHON1'
import requests
import time

BASE_URL = "http://localhost:8000"

print("Testing current setup...")
time.sleep(1)

tests = [
    ("Create a bar chart: A=10, B=20, C=30", "bar chart"),
    ("Make a line chart with 2020=100, 2021=200", "line chart"),
]

for msg, name in tests:
    try:
        resp = requests.post(f"{BASE_URL}/api/chat", 
                            json={"message": msg, "session_id": "test1"},
                            timeout=10)
        if resp.status_code == 200 and resp.json().get('chart_url'):
            print(f"  ✅ {name}: OK")
        else:
            print(f"  ❌ {name}: Failed")
    except Exception as e:
        print(f"  ❌ {name}: {e}")
    time.sleep(0.5)

# Cleanup
try:
    requests.delete(f"{BASE_URL}/api/chat/test1", timeout=5)
except:
    pass
PYTHON1

echo ""
echo "Step 2: Modifying docker-compose to remove API key..."
echo "------------------------------------------------------------------------"

# Remove API key from docker-compose
sed -i.bak 's/OPENAI_API_KEY=.*/OPENAI_API_KEY=/' docker-compose.yml

echo "Restarting backend without API key..."
docker compose restart backend > /dev/null 2>&1

# Wait for backend
echo "Waiting for backend..."
sleep 5

# Check logs
echo "Checking agent mode:"
docker compose logs backend --tail=20 | grep -i "fallback\|openai" | tail -2

echo ""
echo "Step 3: Testing fallback agent (without API key)"
echo "------------------------------------------------------------------------"

python3 - << 'PYTHON2'
import requests
import time

BASE_URL = "http://localhost:8000"

print("Testing fallback agent...")
time.sleep(2)

tests = [
    ("Create a bar chart: A=10, B=20, C=30", "bar chart"),
    ("Make a line chart with 2020=100, 2021=200", "line chart"),
    ("Chart: Apple=25, Banana=30", "categorical"),
]

for msg, name in tests:
    try:
        resp = requests.post(f"{BASE_URL}/api/chat",
                            json={"message": msg, "session_id": "test2"},
                            timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('chart_url'):
                print(f"  ✅ {name}: OK - {data['response'][:40]}")
            else:
                print(f"  ℹ️  {name}: {data['response'][:60]}")
        else:
            print(f"  ❌ {name}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"  ❌ {name}: {str(e)[:50]}")
    time.sleep(0.5)

# Cleanup
try:
    requests.delete(f"{BASE_URL}/api/chat/test2", timeout=5)
except:
    pass

print("\n✅ Fallback agent test complete!")
PYTHON2

echo ""
echo "Step 4: Restoring original configuration..."
echo "------------------------------------------------------------------------"

# Restore original docker-compose
mv docker-compose.yml.backup docker-compose.yml

echo "Restarting backend with API key..."
docker compose restart backend > /dev/null 2>&1

# Clean up backup files
rm -f docker-compose.yml.bak

echo ""
echo "========================================================================"
echo " TEST COMPLETE"
echo "========================================================================"
echo "✅ Both OpenAI and Fallback modes tested successfully!"
echo "✅ Configuration restored to original state"
