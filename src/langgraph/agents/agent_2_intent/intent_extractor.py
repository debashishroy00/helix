"""
Helix Automation: Agent 2 - Intent Extractor
LangGraph Node for extracting semantic intents from parsed test cases
"""

import asyncio
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from src.langgraph.state.helix_state import HelixAutomationState


@dataclass
class SemanticIntent:
    """Represents a semantic intent extracted from a test step"""
    intent_type: str
    target_element: str
    action: str
    value: Optional[str] = None
    context: Optional[str] = None
    confidence: float = 0.0


async def agent_2_intent_extractor(state: HelixAutomationState) -> HelixAutomationState:
    """
    LangGraph Node: Extract semantic intents from parsed test cases
    Updates shared state with enriched steps containing semantic information
    """
    
    print(f"🤖 Agent 2 (Intent Extractor): Extracting semantic intents...")
    start_time = time.time()
    
    try:
        parsed_test_case = state.get("parsed_test_case")
        if not parsed_test_case or not parsed_test_case.get("steps"):
            state["intent_confidence"] = 0.0
            state["errors"].append("No parsed test case available for intent extraction")
            return state
        
        # Extract intents from each test step
        enriched_steps = []
        semantic_intents = []
        total_confidence = 0.0
        
        for step in parsed_test_case["steps"]:
            # Extract semantic intents from step
            step_intents = extract_intents_from_step(step)
            
            # Create enriched step with target elements
            enriched_step = create_enriched_step(step, step_intents)
            enriched_steps.append(enriched_step)
            
            # Collect all semantic intents
            semantic_intents.extend([intent.__dict__ for intent in step_intents])
            
            # Calculate average confidence
            if step_intents:
                step_confidence = sum(intent.confidence for intent in step_intents) / len(step_intents)
                total_confidence += step_confidence
        
        # Calculate overall intent confidence
        intent_confidence = total_confidence / len(enriched_steps) if enriched_steps else 0.0
        
        # Update state
        state["enriched_steps"] = enriched_steps
        state["semantic_intents"] = semantic_intents
        state["intent_confidence"] = intent_confidence
        state["current_agent"] = "Agent 2 (Intent Extractor)"
        
        # Update performance metrics
        execution_time = time.time() - start_time
        state["performance_metrics"]["agent_2_duration"] = execution_time
        
        print(f"✅ Extracted intents for {len(enriched_steps)} steps ({intent_confidence:.1%} confidence) in {execution_time:.2f}s")
        
        # Show intent summary
        intent_types = {}
        for intent in semantic_intents:
            intent_type = intent["intent_type"]
            intent_types[intent_type] = intent_types.get(intent_type, 0) + 1
        
        print(f"📊 Intent distribution: {dict(intent_types)}")
        
    except Exception as e:
        state["intent_confidence"] = 0.0
        state["errors"].append(f"Agent 2 (Intent Extractor) failed: {str(e)}")
        print(f"❌ Intent extraction failed: {e}")
    
    return state


def extract_intents_from_step(step: Dict[str, Any]) -> List[SemanticIntent]:
    """
    Extract semantic intents from a single test step
    """
    
    description = step.get("description", "").lower()
    action = step.get("action", "").lower()
    test_data = step.get("test_data", {})
    expected_result = step.get("expected_result", "").lower()
    
    intents = []
    
    # Navigation intents
    if any(keyword in description for keyword in ["navigate", "go to", "open", "visit", "browse"]):
        url_intent = extract_navigation_intent(description, test_data)
        if url_intent:
            intents.append(url_intent)
    
    # Authentication intents
    auth_intents = extract_authentication_intents(description, test_data)
    intents.extend(auth_intents)
    
    # Form interaction intents
    form_intents = extract_form_intents(description, test_data, action)
    intents.extend(form_intents)
    
    # Button/Link click intents
    click_intents = extract_click_intents(description, expected_result)
    intents.extend(click_intents)
    
    # Selection intents (dropdowns, lists, etc.)
    selection_intents = extract_selection_intents(description, test_data)
    intents.extend(selection_intents)
    
    # Verification intents
    verification_intents = extract_verification_intents(description, expected_result)
    intents.extend(verification_intents)
    
    # Wait/Timing intents
    wait_intents = extract_wait_intents(description)
    intents.extend(wait_intents)
    
    # If no specific intents found, create a generic one
    if not intents:
        generic_intent = create_generic_intent(description, action, test_data)
        if generic_intent:
            intents.append(generic_intent)
    
    return intents


def extract_navigation_intent(description: str, test_data: Dict[str, Any]) -> Optional[SemanticIntent]:
    """Extract navigation/URL intents"""
    
    # Look for URLs in description or test data
    url_patterns = [
        r'https?://[^\s]+',
        r'www\.[^\s]+',
        r'[^\s]+\.[a-z]{2,}[/\w]*'
    ]
    
    url = None
    
    # Check description for URL
    for pattern in url_patterns:
        match = re.search(pattern, description)
        if match:
            url = match.group(0)
            break
    
    # Check test data for URL
    if not url:
        for key, value in test_data.items():
            if any(keyword in key.lower() for keyword in ["url", "link", "address", "site"]):
                url = str(value)
                break
    
    # Check for platform-specific navigation
    platform_urls = {
        "salesforce": "https://login.salesforce.com",
        "sap": "https://sap.com",
        "workday": "https://workday.com",
        "servicenow": "https://servicenow.com"
    }
    
    for platform, default_url in platform_urls.items():
        if platform in description:
            url = url or default_url
            break
    
    if url:
        return SemanticIntent(
            intent_type="navigation",
            target_element="page",
            action="navigate",
            value=url,
            context=f"Navigate to {url}",
            confidence=0.9 if url.startswith("http") else 0.7
        )
    
    return None


def extract_authentication_intents(description: str, test_data: Dict[str, Any]) -> List[SemanticIntent]:
    """Extract authentication-related intents (login, password, etc.)"""
    
    intents = []
    
    # Username/Email intent
    username_keywords = ["username", "user name", "email", "user id", "login", "account"]
    if any(keyword in description for keyword in username_keywords):
        username_value = None
        
        # Look for username in test data
        for key, value in test_data.items():
            if any(keyword in key.lower() for keyword in username_keywords):
                username_value = str(value)
                break
        
        # Look for email patterns in description
        if not username_value:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', description)
            if email_match:
                username_value = email_match.group(0)
        
        intents.append(SemanticIntent(
            intent_type="authentication",
            target_element="username_field",
            action="input",
            value=username_value,
            context="Enter username/email for login",
            confidence=0.9 if username_value else 0.7
        ))
    
    # Password intent
    password_keywords = ["password", "pwd", "passcode", "secret"]
    if any(keyword in description for keyword in password_keywords):
        password_value = None
        
        # Look for password in test data
        for key, value in test_data.items():
            if any(keyword in key.lower() for keyword in password_keywords):
                password_value = str(value)
                break
        
        intents.append(SemanticIntent(
            intent_type="authentication",
            target_element="password_field",
            action="input",
            value=password_value,
            context="Enter password for login",
            confidence=0.9 if password_value else 0.7
        ))
    
    # Login button intent
    login_button_keywords = ["login", "sign in", "log in", "authenticate"]
    if any(keyword in description for keyword in login_button_keywords) and \
       any(action_word in description for action_word in ["click", "press", "tap", "button"]):
        
        intents.append(SemanticIntent(
            intent_type="authentication",
            target_element="login_button",
            action="click",
            value=None,
            context="Click login/sign in button",
            confidence=0.9
        ))
    
    return intents


def extract_form_intents(description: str, test_data: Dict[str, Any], action: str) -> List[SemanticIntent]:
    """Extract form interaction intents"""
    
    intents = []
    
    # Generic input field intent
    input_keywords = ["enter", "type", "input", "fill"]
    if any(keyword in description for keyword in input_keywords):
        
        # Determine field type from context
        field_type = "text_field"
        if any(keyword in description for keyword in ["name", "title"]):
            field_type = "name_field"
        elif any(keyword in description for keyword in ["amount", "price", "number"]):
            field_type = "number_field"
        elif any(keyword in description for keyword in ["date", "time"]):
            field_type = "date_field"
        elif any(keyword in description for keyword in ["description", "comment", "note"]):
            field_type = "textarea"
        
        # Extract field value
        field_value = None
        if test_data:
            # Take first value from test data
            field_value = str(list(test_data.values())[0])
        
        # Look for quoted values in description
        if not field_value:
            quoted_match = re.search(r'"([^"]+)"', description)
            if quoted_match:
                field_value = quoted_match.group(1)
        
        intents.append(SemanticIntent(
            intent_type="form_interaction",
            target_element=field_type,
            action="input",
            value=field_value,
            context=f"Enter value into {field_type}",
            confidence=0.8 if field_value else 0.6
        ))
    
    return intents


def extract_click_intents(description: str, expected_result: str) -> List[SemanticIntent]:
    """Extract button/link click intents"""
    
    intents = []
    
    click_keywords = ["click", "press", "tap", "select"]
    if any(keyword in description for keyword in click_keywords):
        
        # Determine element type
        element_type = "button"
        if any(keyword in description for keyword in ["link", "hyperlink"]):
            element_type = "link"
        elif any(keyword in description for keyword in ["tab", "menu"]):
            element_type = "menu_item"
        elif any(keyword in description for keyword in ["checkbox", "check box"]):
            element_type = "checkbox"
        elif any(keyword in description for keyword in ["radio", "option"]):
            element_type = "radio_button"
        
        # Extract button/element name
        element_name = extract_element_name_from_description(description)
        
        # Determine semantic intent based on button name/context
        semantic_type = categorize_click_intent(element_name, description, expected_result)
        
        intents.append(SemanticIntent(
            intent_type=semantic_type,
            target_element=element_type,
            action="click",
            value=element_name,
            context=f"Click {element_type}: {element_name}",
            confidence=0.8 if element_name else 0.6
        ))
    
    return intents


def extract_selection_intents(description: str, test_data: Dict[str, Any]) -> List[SemanticIntent]:
    """Extract selection intents (dropdowns, lists, etc.)"""
    
    intents = []
    
    selection_keywords = ["select", "choose", "pick", "dropdown", "list"]
    if any(keyword in description for keyword in selection_keywords):
        
        # Determine selection type
        element_type = "dropdown"
        if any(keyword in description for keyword in ["list", "listbox"]):
            element_type = "listbox"
        elif any(keyword in description for keyword in ["combo", "combobox"]):
            element_type = "combobox"
        
        # Extract selection value
        selection_value = None
        if test_data:
            selection_value = str(list(test_data.values())[0])
        
        # Look for quoted values in description
        if not selection_value:
            quoted_match = re.search(r'"([^"]+)"', description)
            if quoted_match:
                selection_value = quoted_match.group(1)
        
        intents.append(SemanticIntent(
            intent_type="form_interaction",
            target_element=element_type,
            action="select",
            value=selection_value,
            context=f"Select value from {element_type}",
            confidence=0.8 if selection_value else 0.6
        ))
    
    return intents


def extract_verification_intents(description: str, expected_result: str) -> List[SemanticIntent]:
    """Extract verification/assertion intents"""
    
    intents = []
    
    verification_keywords = ["verify", "check", "assert", "confirm", "validate", "ensure"]
    
    # Check both description and expected result
    verification_text = description + " " + expected_result
    
    if any(keyword in verification_text for keyword in verification_keywords):
        
        # Determine what is being verified
        verification_type = "general_verification"
        target_element = "page"
        
        if any(keyword in verification_text for keyword in ["login", "logged in", "authenticated"]):
            verification_type = "authentication_verification"
            target_element = "login_status"
        elif any(keyword in verification_text for keyword in ["page", "displayed", "shown", "loaded"]):
            verification_type = "page_verification"
            target_element = "page"
        elif any(keyword in verification_text for keyword in ["message", "text", "content"]):
            verification_type = "content_verification"
            target_element = "text_element"
        elif any(keyword in verification_text for keyword in ["error", "warning", "alert"]):
            verification_type = "error_verification"
            target_element = "error_message"
        
        # Extract expected value
        expected_value = extract_expected_value(verification_text)
        
        intents.append(SemanticIntent(
            intent_type=verification_type,
            target_element=target_element,
            action="verify",
            value=expected_value,
            context=f"Verify {verification_type}",
            confidence=0.8
        ))
    
    return intents


def extract_wait_intents(description: str) -> List[SemanticIntent]:
    """Extract wait/timing intents"""
    
    intents = []
    
    wait_keywords = ["wait", "pause", "delay", "sleep"]
    if any(keyword in description for keyword in wait_keywords):
        
        # Extract wait duration
        duration_match = re.search(r'(\d+)\s*(second|sec|minute|min|ms|millisecond)', description)
        duration = None
        if duration_match:
            duration = duration_match.group(0)
        
        # Determine wait type
        wait_type = "explicit_wait"
        if any(keyword in description for keyword in ["load", "loading", "loaded"]):
            wait_type = "page_load_wait"
        elif any(keyword in description for keyword in ["element", "appear", "visible"]):
            wait_type = "element_wait"
        
        intents.append(SemanticIntent(
            intent_type="timing",
            target_element="page",
            action="wait",
            value=duration,
            context=f"Wait for condition: {wait_type}",
            confidence=0.8 if duration else 0.6
        ))
    
    return intents


def create_generic_intent(description: str, action: str, test_data: Dict[str, Any]) -> Optional[SemanticIntent]:
    """Create a generic intent when no specific pattern is found"""
    
    if not description.strip():
        return None
    
    # Map generic actions
    action_map = {
        "navigate": "navigation",
        "click": "ui_interaction",
        "input": "form_interaction",
        "select": "form_interaction",
        "verify": "verification",
        "wait": "timing"
    }
    
    intent_type = action_map.get(action, "ui_interaction")
    
    return SemanticIntent(
        intent_type=intent_type,
        target_element="generic_element",
        action=action or "interact",
        value=str(list(test_data.values())[0]) if test_data else None,
        context=description[:100],
        confidence=0.5
    )


def extract_element_name_from_description(description: str) -> Optional[str]:
    """Extract element name from description"""
    
    # Look for quoted text
    quoted_match = re.search(r'"([^"]+)"', description)
    if quoted_match:
        return quoted_match.group(1)
    
    # Look for specific button/element names
    button_patterns = [
        r'click\s+(?:the\s+)?(\w+(?:\s+\w+)*)\s+button',
        r'press\s+(?:the\s+)?(\w+(?:\s+\w+)*)',
        r'tap\s+(?:the\s+)?(\w+(?:\s+\w+)*)',
        r'(\w+(?:\s+\w+)*)\s+button',
    ]
    
    for pattern in button_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def categorize_click_intent(element_name: str, description: str, expected_result: str) -> str:
    """Categorize click intent based on element name and context"""
    
    context = (element_name or "").lower() + " " + description.lower() + " " + expected_result.lower()
    
    if any(keyword in context for keyword in ["login", "sign in", "authenticate"]):
        return "authentication"
    elif any(keyword in context for keyword in ["save", "submit", "create", "add"]):
        return "form_submission"
    elif any(keyword in context for keyword in ["search", "find", "filter"]):
        return "search_interaction"
    elif any(keyword in context for keyword in ["menu", "nav", "launcher", "tab"]):
        return "navigation"
    elif any(keyword in context for keyword in ["delete", "remove", "cancel"]):
        return "destructive_action"
    elif any(keyword in context for keyword in ["edit", "modify", "update"]):
        return "edit_action"
    else:
        return "ui_interaction"


def extract_expected_value(text: str) -> Optional[str]:
    """Extract expected value from verification text"""
    
    # Look for quoted expected values
    quoted_match = re.search(r'"([^"]+)"', text)
    if quoted_match:
        return quoted_match.group(1)
    
    # Look for "should be/show/display X" patterns
    should_patterns = [
        r'should\s+(?:be|show|display)\s+([^\n\r.]+)',
        r'expected\s+(?:to\s+)?(?:be|show|display)\s+([^\n\r.]+)',
        r'verify\s+(?:that\s+)?([^\n\r.]+)'
    ]
    
    for pattern in should_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def create_enriched_step(step: Dict[str, Any], intents: List[SemanticIntent]) -> Dict[str, Any]:
    """Create enriched step with target elements from intents"""
    
    enriched_step = step.copy()
    
    # Convert intents to target elements
    target_elements = []
    for intent in intents:
        target_element = {
            "semantic_intent": intent.intent_type,
            "element_type": intent.target_element,
            "action_type": intent.action,
            "description": step.get("description", ""),
            "value": intent.value,
            "context": intent.context,
            "confidence": intent.confidence
        }
        target_elements.append(target_element)
    
    enriched_step["target_elements"] = target_elements
    enriched_step["intent_count"] = len(intents)
    enriched_step["avg_confidence"] = sum(intent.confidence for intent in intents) / len(intents) if intents else 0.0
    
    return enriched_step


# Test function for Agent 2
async def test_agent_2():
    """Test Agent 2 in isolation"""
    
    from src.langgraph.state.helix_state import create_initial_state
    
    # Create mock parsed test case
    mock_parsed_case = {
        "test_id": "TEST_001",
        "title": "Salesforce Login Test",
        "description": "Test login functionality",
        "steps": [
            {
                "step_number": 1,
                "action": "navigate",
                "description": "Navigate to https://login.salesforce.com",
                "expected_result": "Login page should be displayed",
                "test_data": {}
            },
            {
                "step_number": 2,
                "action": "input",
                "description": "Enter username test@company.com",
                "expected_result": "Username field should be filled",
                "test_data": {"username": "test@company.com"}
            },
            {
                "step_number": 3,
                "action": "input",
                "description": "Enter password secret123",
                "expected_result": "Password field should be filled",
                "test_data": {"password": "secret123"}
            },
            {
                "step_number": 4,
                "action": "click",
                "description": "Click Login button",
                "expected_result": "User should be logged in successfully",
                "test_data": {}
            },
            {
                "step_number": 5,
                "action": "verify",
                "description": "Verify user is logged in",
                "expected_result": "Dashboard should be displayed",
                "test_data": {}
            }
        ]
    }
    
    print("🧪 Testing Agent 2 (Intent Extractor)...")
    
    # Create initial state with parsed test case
    initial_state = create_initial_state(
        raw_input="Mock test case",
        input_metadata={"format": "mock"}
    )
    initial_state["parsed_test_case"] = mock_parsed_case
    
    # Run Agent 2
    result_state = await agent_2_intent_extractor(initial_state)
    
    # Display results
    enriched_steps = result_state.get("enriched_steps", [])
    semantic_intents = result_state.get("semantic_intents", [])
    intent_confidence = result_state.get("intent_confidence", 0)
    errors = result_state.get("errors", [])
    
    print(f"\n📊 Intent Extraction Results:")
    print(f"   - Overall confidence: {intent_confidence:.1%}")
    print(f"   - Enriched steps: {len(enriched_steps)}")
    print(f"   - Total intents extracted: {len(semantic_intents)}")
    
    if errors:
        print(f"❌ Errors:")
        for error in errors:
            print(f"     {error}")
    
    # Show detailed results for each step
    for i, step in enumerate(enriched_steps, 1):
        print(f"\n📝 Step {i}: {step.get('description', 'N/A')[:50]}...")
        target_elements = step.get("target_elements", [])
        print(f"     Target elements: {len(target_elements)}")
        
        for j, element in enumerate(target_elements):
            print(f"       {j+1}. Intent: {element.get('semantic_intent', 'N/A')}")
            print(f"          Element: {element.get('element_type', 'N/A')}")
            print(f"          Action: {element.get('action_type', 'N/A')}")
            print(f"          Confidence: {element.get('confidence', 0):.1%}")
    
    print(f"\n🎯 Agent 2 testing complete!")
    return result_state


if __name__ == "__main__":
    asyncio.run(test_agent_2())