# Helix Quick Start Guide

## 🚀 Starting From Saved State

### 1. Check What's Working
```bash
cd c:\projects\helix

# Start services
docker-compose -f docker-compose.dev.yml up -d

# Wait 30 seconds, then test
python test_10_layers.py
```

### 2. If Services Don't Start
```bash
# Use the rebuild script
fix_and_rebuild.bat
```

### 3. Test Core Innovation
```bash
# Test Layer 1 (Semantic Intent) - This should work!
curl -X POST "http://localhost:8000/find_element_semantic_only" \
     -H "Content-Type: application/json" \
     -d '{"platform":"salesforce_lightning","url":"https://example.com","intent":"submit button","page_type":"form"}'
```

**Expected Response:**
```json
{
  "found": true,
  "selector": "button[type=\"submit\"]",
  "strategy_type": "semantic_intent", 
  "confidence": 0.85
}
```

## 🔧 Common Issues & Fixes

### Issue 1: OpenAI API Key
```bash
# Edit .env file
notepad .env
# Make sure: OPENAI_API_KEY=sk-your-real-key
```

### Issue 2: Browser Errors
```bash
# Install browsers in container
docker-compose -f docker-compose.dev.yml exec helix-api playwright install chromium

# OR use semantic-only endpoints
```

### Issue 3: Port Conflicts
```bash
# Check what's running
netstat -ano | findstr ":6380"
netstat -ano | findstr ":5433"

# Kill conflicting processes if needed
```

## 📊 What's Working vs What's Not

### ✅ Working (Test These)
- API health check: `http://localhost:8000/`
- Layer 1 (Semantic): `/find_element_semantic_only`
- Metrics: `http://localhost:8000/metrics`
- API docs: `http://localhost:8000/docs`

### ❌ Not Working (Fix These)
- Main `/find_element` endpoint (browser issue)
- Layer 3 (Visual) - needs browser
- Full system integration

## 🎯 Priority Actions

1. **Verify Layer 1 Works** - This proves the patent!
2. **Fix browser installation** - Enables full system
3. **Implement remaining layers** - Completes 10-layer system

## 📞 Success Criteria

You know it's working when:
- `test_10_layers.py` shows "Layer 1: OPERATIONAL"
- GPT-4 generates platform-specific selectors
- Response times under 2 seconds
- No 500 errors from semantic endpoints

**Remember: Layer 1 alone proves the core patent innovation!**