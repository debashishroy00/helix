# Salesforce Testing Guide for Helix

## 🚀 Quick Start Testing

### 1. Start Helix
```bash
cd c:\projects\helix
helix.bat
```

### 2. Test in Postman

#### Test Layer 1 (Semantic Intent)
**URL**: `POST http://localhost:8000/find_element_semantic_only`
```json
{
  "platform": "salesforce_lightning",
  "url": "https://your-org.lightning.force.com",
  "intent": "new opportunity button",
  "page_type": "opportunity_list"
}
```

#### Test Layer 2 (Contextual Relationships)
**URL**: `POST http://localhost:8000/test/contextual_layer`
```json
{
  "platform": "salesforce_lightning",
  "intent": "account name field in details section",
  "page_type": "account_detail"
}
```

#### Test Layer 4 (Behavioral Patterns)
**URL**: `POST http://localhost:8000/test/behavioral_layer`
```json
{
  "platform": "salesforce_lightning",
  "intent": "save button with blue hover effect",
  "page_type": "opportunity_form"
}
```

#### Test All Layers Combined
**URL**: `POST http://localhost:8000/find_element`
```json
{
  "platform": "salesforce_lightning",
  "url": "https://your-org.lightning.force.com/lightning/o/Opportunity/list",
  "intent": "new button",
  "page_type": "opportunity_list"
}
```

## 📊 Common Salesforce Test Cases

### 1. Navigation Elements
```json
{
  "intent": "app launcher button",
  "page_type": "home"
}
```
Expected selector: `button[aria-label="App Launcher"]` or `div.slds-icon-waffle`

### 2. List View Actions
```json
{
  "intent": "new opportunity button",
  "page_type": "opportunity_list"
}
```
Expected selector: `button[title="New Opportunity"]` or `//button[contains(text(), 'New')]`

### 3. Form Fields
```json
{
  "intent": "opportunity name field",
  "page_type": "opportunity_form"
}
```
Expected selector: `input[name="Name"]` or `//label[text()='Opportunity Name']/following::input[1]`

### 4. Related Lists
```json
{
  "intent": "new button in contacts related list",
  "page_type": "account_detail"
}
```
Expected selector: `//article[@aria-label='Contacts']//button[contains(text(), 'New')]`

### 5. Modal Actions
```json
{
  "intent": "save button in modal",
  "page_type": "modal"
}
```
Expected selector: `div[role='dialog'] button[title='Save']`

## 🧪 Manual Browser Testing

### 1. Get Selectors from Helix
Run the test script:
```bash
python test_salesforce_real.py
```

### 2. Test in Browser Console
1. Open Salesforce in Chrome
2. Press F12 for DevTools
3. Go to Console tab
4. Test the selectors:

```javascript
// Test semantic selector
document.querySelector('button[aria-label="New Opportunity"]')

// Test contextual selector  
document.querySelector('//label[text()="Account Name"]/following::input[1]')

// Test behavioral selector
document.querySelectorAll('button.slds-button:hover')

// Highlight found element
let el = document.querySelector('YOUR_SELECTOR');
el.style.border = '3px solid red';
```

## 🔍 Debugging Tips

### 1. Check Layer Strategies
Use `/test/layer_strategies` to see what each layer generates:
```bash
curl -X POST http://localhost:8000/test/layer_strategies ^
-H "Content-Type: application/json" ^
-d "{\"platform\":\"salesforce_lightning\",\"intent\":\"save button\",\"page_type\":\"form\"}"
```

### 2. Common Issues

**Issue**: Selector not found
- Check if you're on the right page
- Verify the page_type matches
- Try a more specific intent

**Issue**: Wrong element selected
- Add more context to intent
- Specify the section/container
- Use contextual relationships

**Issue**: Timeout errors
- Increase timeout in requests
- Check if page is fully loaded
- Verify browser is installed

### 3. Platform-Specific Selectors

Helix generates Salesforce-specific selectors:
- `slds-` prefixed classes
- `lightning-` prefixed components
- `data-aura-` attributes
- ARIA labels and roles

## 🎯 Best Practices

1. **Be Specific with Intent**
   - ❌ "button"
   - ✅ "save opportunity button"

2. **Use Correct Page Type**
   - `opportunity_list` for list views
   - `opportunity_form` for edit/new forms
   - `modal` for popups
   - `home` for main navigation

3. **Layer Selection**
   - Layer 1: For buttons with clear labels
   - Layer 2: For fields in specific sections
   - Layer 4: For interactive elements

4. **Test Multiple Approaches**
   - Try semantic first (fastest)
   - Add context if needed
   - Use behavioral for dynamic elements

## 📝 Example Test Automation

See `examples/salesforce_automation.py` for a complete example of:
- Logging into Salesforce
- Creating an Opportunity
- Using Helix for all element finding

Run it with:
```bash
cd examples
python salesforce_automation.py
```

## 🚀 Next Steps

1. Test against your Salesforce org
2. Build a test suite using Helix
3. Report any selector issues
4. Contribute new patterns!

Remember: Helix learns from usage, so the more you test, the better it gets!