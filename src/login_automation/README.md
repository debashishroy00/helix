# Helix Login Automation Module

A dedicated login automation system within the Helix project for handling enterprise application authentication. This module uses hardcoded, reliable selector patterns rather than the 10-layer architecture, as login flows require specific handling.

## 🎯 Overview

While Helix's 10-layer architecture excels at finding dynamic UI elements, login pages have specific requirements:
- Fixed selector patterns that rarely change
- Domain-specific auth flows (SSO, MFA, custom domains)
- Session management and credential handling
- Retry mechanisms for authentication failures

This module provides robust, deterministic login automation for:
- **Salesforce** (with custom domain handling)
- **SAP** (with client field support)
- **Oracle Cloud** (with identity domain routing)
- **Workday** (with tenant URL support)

## 📁 Module Structure

```
src/login_automation/
├── __init__.py              # Module exports
├── login_handler.py         # Core login handler with app-specific methods
├── orchestrator.py          # Multi-app orchestration and reporting
├── config.py               # Configuration utilities
├── cli.py                  # Command-line interface
├── config/
│   └── login_config.json   # Login configuration and selectors
├── logs/                   # Login automation logs
├── screenshots/            # Debug screenshots
└── reports/               # Login reports
```

## 🚀 Usage

### From Helix Project Root

```bash
# Single app login
python -m src.login_automation.cli salesforce

# Multiple apps
python -m src.login_automation.cli salesforce workday

# All apps in parallel
python -m src.login_automation.cli --all --parallel

# Headless mode with report
python -m src.login_automation.cli --all --headless --report
```

### Programmatic Usage

```python
from src.login_automation import LoginOrchestrator

async def automate_logins():
    orchestrator = LoginOrchestrator()
    
    # Login to single app
    result = await orchestrator.run_single_app("salesforce")
    
    # Login to multiple apps
    results = await orchestrator.run_multiple_apps(["salesforce", "workday"])
    
    # Generate report
    print(orchestrator.generate_report(results))
```

### Integration with Helix Tests

```python
from src.login_automation import LoginHandler

async def setup_authenticated_session():
    """Use login automation to set up authenticated test session."""
    handler = LoginHandler()
    await handler.setup_browser()
    
    credentials = {
        "username": "test@example.com",
        "password": "password",
        "org_url": "https://test.salesforce.com"
    }
    
    success, message = await handler.login_to_app("salesforce", credentials)
    if success:
        # Now use Helix's 10-layer system for element finding
        from src.core.universal_locator import UniversalLocator
        locator = UniversalLocator()
        # ... continue with test automation
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the Helix project root:

```bash
# Salesforce
SALESFORCE_USERNAME=your-email@company.com
SALESFORCE_PASSWORD=your-password
SALESFORCE_ORG_URL=https://your-org.lightning.force.com
SALESFORCE_SECURITY_TOKEN=optional-token

# SAP
SAP_USERNAME=your-username
SAP_PASSWORD=your-password
SAP_LOGIN_URL=https://your-sap-server/login
SAP_CLIENT=100

# Oracle
ORACLE_USERNAME=your-username
ORACLE_PASSWORD=your-password
ORACLE_LOGIN_URL=https://cloud.oracle.com/sign-in
ORACLE_IDENTITY_DOMAIN=your-domain

# Workday
WORKDAY_USERNAME=your-email@company.com
WORKDAY_PASSWORD=your-password
WORKDAY_TENANT_URL=https://your-tenant.workday.com
```

### Selector Configuration

Edit `config/login_config.json` to update selectors:

```json
{
  "apps": {
    "salesforce": {
      "selectors": {
        "username": ["#username", "input[name='username']"],
        "password": ["#password", "input[name='password']"],
        "login_button": ["#Login", "input[type='submit']"]
      }
    }
  }
}
```

## 🏗 Architecture Decisions

### Why Separate from 10-Layer System?

1. **Deterministic Patterns**: Login elements have fixed IDs/names that rarely change
2. **Speed**: No need for AI or complex analysis for `#username` and `#password`
3. **Reliability**: Hardcoded patterns are more reliable for critical auth flows
4. **Maintenance**: Login flows change less frequently than application UIs

### Integration Points

- **Pre-authentication**: Use this module to establish authenticated sessions
- **Post-login**: Use Helix's 10-layer system for dynamic element identification
- **Test Setup**: Automated login before running Helix test suites
- **Session Management**: Handle re-authentication when sessions expire

## 📊 Features

### App-Specific Handling

Each app has custom logic for:
- **Salesforce**: Custom domain detection and submission
- **SAP**: Client field and session management
- **Oracle**: Identity domain routing
- **Workday**: Tenant URL construction

### Robust Error Handling

- Multiple selector fallbacks per element
- Configurable retry mechanisms
- Screenshot capture on failures
- Detailed error messages

### MFA Support

- Automatic MFA detection
- Configurable wait times for manual entry
- Future support for automated MFA handling

### Reporting

- Detailed login reports with timings
- Success/failure analysis
- Screenshot paths for debugging
- Performance metrics

## 🔍 Debugging

### Enable Debug Logging

```python
# In login_config.json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

### Check Screenshots

Failed logins automatically save screenshots to `src/login_automation/screenshots/`

### View Logs

Logs are saved to `src/login_automation/logs/helix_login_automation.log`

## 🎯 Best Practices

1. **Credential Security**: Never commit credentials to version control
2. **Selector Updates**: Periodically verify selectors still work
3. **Error Monitoring**: Check logs regularly for authentication issues
4. **Session Reuse**: Consider caching authenticated sessions
5. **Parallel Execution**: Use for faster multi-app testing

## 🔄 Extending for New Apps

1. Add app configuration to `login_config.json`
2. Create login method in `LoginHandler` class
3. Add credential mapping in `config.py`
4. Test thoroughly with different auth scenarios

Example:
```python
async def login_servicenow(self, credentials: Dict[str, str]) -> Tuple[bool, str]:
    """Login to ServiceNow."""
    # App-specific implementation
    pass
```

## 🚀 Integration with Helix Workflow

```python
# 1. Login using this module
from src.login_automation import LoginHandler
handler = LoginHandler()
await handler.setup_browser()
success, _ = await handler.login_to_app("salesforce", credentials)

# 2. Use Helix for element finding after login
from src.api.dependencies import get_universal_locator
locator = get_universal_locator()
result = await locator.find_element(handler.page, context)

# 3. Continue with test automation
# ...
```

This module complements Helix's 10-layer architecture by handling the specific requirements of enterprise login flows, ensuring reliable authentication before dynamic element identification begins.