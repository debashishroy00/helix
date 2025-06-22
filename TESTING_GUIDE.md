# Helix Testing Guide

## 🚀 Quick Start Testing

### 1. Start the Development Environment

```bash
cd /mnt/c/projects/helix

# Option A: Automated setup
python scripts/dev_start.py

# Option B: Manual setup
cp .env.example .env
# Edit .env and add your OpenAI API key
docker-compose up -d
```

### 2. Verify Services Are Running

```bash
# Check all containers are healthy
docker-compose ps

# Test API health
curl http://localhost:8000/

# Expected response:
# {"service":"Helix","status":"operational","version":"0.1.0","timestamp":"..."}
```

### 3. Run Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_universal_locator.py -v
```

## 🎯 API Testing

### Test Element Identification

```bash
# Test 1: Simple button search
curl -X POST "http://localhost:8000/find_element" \
     -H "Content-Type: application/json" \
     -d '{
       "platform": "salesforce_lightning",
       "url": "https://developer.salesforce.com/docs",
       "intent": "search button",
       "page_type": "documentation"
     }'
```

```bash
# Test 2: Form submission
curl -X POST "http://localhost:8000/find_element" \
     -H "Content-Type: application/json" \
     -d '{
       "platform": "salesforce_lightning", 
       "url": "https://login.salesforce.com",
       "intent": "login button",
       "page_type": "login"
     }'
```

```bash
# Test 3: Complex element with context
curl -X POST "http://localhost:8000/find_element" \
     -H "Content-Type: application/json" \
     -d '{
       "platform": "sap_fiori",
       "url": "https://sapui5.hana.ondemand.com",
       "intent": "submit button in expense form",
       "page_type": "form",
       "additional_context": {"form_type": "expense_report"}
     }'
```

### Expected Response Format

```json
{
  "found": true,
  "selector": "button[type=\"submit\"]",
  "strategy_type": "semantic_intent",
  "confidence": 0.85,
  "time_taken_ms": 1250.5,
  "attempts_count": 3,
  "error": null
}
```

## 🧪 Layer-Specific Testing

### Test Layer 1: Semantic Intent

```python
# Create test file: test_semantic_layer.py
import asyncio
from src.layers.semantic_intent import SemanticIntentLayer
from src.models.element import ElementContext, Platform

async def test_semantic_layer():
    layer = SemanticIntentLayer()
    
    context = ElementContext(
        platform=Platform.SALESFORCE_LIGHTNING,
        page_type="form",
        intent="submit button"
    )
    
    # Mock page object
    class MockPage:
        pass
    
    strategies = await layer.generate_strategies(MockPage(), context)
    
    print(f"Generated {len(strategies)} strategies:")
    for strategy in strategies:
        print(f"  - {strategy.selector} (confidence: {strategy.confidence})")

# Run the test
asyncio.run(test_semantic_layer())
```

### Test Layer 3: Visual Fingerprinting

```python
# test_visual_layer.py
import asyncio
from src.layers.visual_fingerprint import VisualFingerprintLayer
from src.models.element import ElementContext, Platform

async def test_visual_layer():
    layer = VisualFingerprintLayer()
    
    context = ElementContext(
        platform=Platform.SALESFORCE_LIGHTNING,
        page_type="form", 
        intent="submit button"
    )
    
    # Mock page with screenshot capability
    class MockPage:
        async def screenshot(self):
            # Return a small test image (1x1 pixel PNG)
            return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    
    strategies = await layer.generate_strategies(MockPage(), context)
    
    print(f"Visual layer generated {len(strategies)} strategies:")
    for strategy in strategies:
        print(f"  - {strategy.selector} (confidence: {strategy.confidence})")

asyncio.run(test_visual_layer())
```

## 🌐 Live Website Testing

### Test Real Websites (with caution)

```bash
# Test on public documentation sites
curl -X POST "http://localhost:8000/find_element" \
     -H "Content-Type: application/json" \
     -d '{
       "platform": "salesforce_lightning",
       "url": "https://developer.salesforce.com/docs/atlas.en-us.lightning.meta/lightning/",
       "intent": "search input field",
       "page_type": "documentation"
     }'
```

```bash
# Test on demo sites
curl -X POST "http://localhost:8000/find_element" \
     -H "Content-Type: application/json" \
     -d '{
       "platform": "salesforce_lightning",
       "url": "https://www.lightningdesignsystem.com/",
       "intent": "navigation menu",
       "page_type": "landing"
     }'
```

## 📊 Performance Testing

### Load Testing Script

```python
# load_test.py
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

async def test_endpoint(session, test_data):
    start_time = time.time()
    async with session.post('http://localhost:8000/find_element', json=test_data) as resp:
        result = await resp.json()
        elapsed = (time.time() - start_time) * 1000
        return elapsed, result.get('found', False)

async def load_test():
    test_cases = [
        {
            "platform": "salesforce_lightning",
            "url": "https://example.com",
            "intent": "submit button",
            "page_type": "form"
        },
        {
            "platform": "sap_fiori", 
            "url": "https://example.com",
            "intent": "search field",
            "page_type": "list"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(50):  # 50 concurrent requests
            test_data = test_cases[i % len(test_cases)]
            tasks.append(test_endpoint(session, test_data))
        
        results = await asyncio.gather(*tasks)
        
        times = [r[0] for r in results]
        successes = [r[1] for r in results]
        
        print(f"Average response time: {sum(times)/len(times):.2f}ms")
        print(f"Success rate: {sum(successes)/len(successes)*100:.1f}%")
        print(f"Max response time: {max(times):.2f}ms")

asyncio.run(load_test())
```

## 🔍 Integration Testing

### Test Complete Workflow

```python
# integration_test.py
import asyncio
import aiohttp

async def integration_test():
    """Test complete element identification workflow"""
    
    test_scenarios = [
        {
            "name": "Login Form",
            "request": {
                "platform": "salesforce_lightning",
                "url": "https://login.salesforce.com",
                "intent": "username field",
                "page_type": "login"
            },
            "expected_found": True
        },
        {
            "name": "Search Button", 
            "request": {
                "platform": "salesforce_lightning",
                "url": "https://developer.salesforce.com",
                "intent": "search button",
                "page_type": "documentation"
            },
            "expected_found": True
        },
        {
            "name": "Non-existent Element",
            "request": {
                "platform": "salesforce_lightning", 
                "url": "https://example.com",
                "intent": "quantum flux capacitor button",
                "page_type": "impossible"
            },
            "expected_found": False
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for scenario in test_scenarios:
            print(f"\n🧪 Testing: {scenario['name']}")
            
            async with session.post('http://localhost:8000/find_element', 
                                   json=scenario['request']) as resp:
                result = await resp.json()
                
                print(f"   Found: {result['found']}")
                print(f"   Time: {result['time_taken_ms']:.1f}ms")
                print(f"   Strategy: {result.get('strategy_type', 'none')}")
                
                if result['found'] == scenario['expected_found']:
                    print("   ✅ PASS")
                else:
                    print("   ❌ FAIL")

asyncio.run(integration_test())
```

## 📈 Metrics Testing

### Check System Metrics

```bash
# Get performance metrics
curl http://localhost:8000/metrics

# Expected response includes:
# - total_requests
# - success_rate  
# - average_time_ms
# - cache_hit_rate
# - strategy_success_rates
```

### Test Feedback System

```bash
curl -X POST "http://localhost:8000/feedback" \
     -H "Content-Type: application/json" \
     -d '{
       "feedback_id": "test_fb_001",
       "platform": "salesforce_lightning",
       "intent": "submit button",
       "selector_attempted": "button[type=\"submit\"]",
       "was_successful": true,
       "comments": "Worked perfectly on the account creation form"
     }'
```

## 🏗️ Test Generation

### Generate Complete Test Cases

```bash
curl -X POST "http://localhost:8000/generate_test" \
     -H "Content-Type: application/json" \
     -d '{
       "platform": "salesforce_lightning",
       "start_url": "https://example.my.salesforce.com",
       "test_name": "Create New Account",
       "test_steps": [
         {
           "action": "click",
           "intent": "Accounts tab",
           "page_type": "home"
         },
         {
           "action": "click", 
           "intent": "New button",
           "page_type": "list"
         },
         {
           "action": "type",
           "intent": "Account Name field",
           "page_type": "form",
           "data": "Test Account 123"
         },
         {
           "action": "click",
           "intent": "Save button", 
           "page_type": "form"
         }
       ]
     }'
```

## 🐛 Debugging Failed Tests

### Enable Debug Logging

```bash
# Set environment variable for verbose logging
export LOG_LEVEL=DEBUG

# Restart the service
docker-compose restart helix-api

# Check logs
docker-compose logs -f helix-api
```

### Common Issues and Solutions

1. **OpenAI API Key Not Set**
   ```bash
   # Error: Semantic layer failing
   # Solution: Check .env file has valid OPENAI_API_KEY
   ```

2. **Browser Dependencies Missing**
   ```bash
   # Error: Screenshot/visual layer failing
   # Solution: Install Playwright browsers
   playwright install chromium
   ```

3. **Database Connection Issues**
   ```bash
   # Error: Cache not working
   # Solution: Verify PostgreSQL and Redis are running
   docker-compose ps
   ```

4. **Timeout Issues**
   ```bash
   # Error: Requests timing out
   # Solution: Increase timeout_ms in requests
   # Or check if target website is accessible
   ```

## ✅ Success Criteria

The system passes testing when:

- ✅ Unit tests pass (95%+ coverage)
- ✅ API endpoints respond in <2 seconds
- ✅ Element found rate >70% with current 2 layers
- ✅ System handles 100+ concurrent requests
- ✅ Cache hit rate >30% after multiple runs
- ✅ All Docker services start successfully
- ✅ Metrics endpoint provides valid data

## 📋 Test Checklist

- [ ] Environment setup complete
- [ ] Unit tests passing
- [ ] API health check successful
- [ ] Element identification working
- [ ] Performance within targets
- [ ] Error handling robust
- [ ] Metrics collection working
- [ ] Docker services healthy
- [ ] Load testing successful
- [ ] Integration tests complete

Run this checklist before considering the system production-ready!