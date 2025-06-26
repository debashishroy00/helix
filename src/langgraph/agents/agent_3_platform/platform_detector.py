"""
Helix Automation: Agent 3 - Platform Detector
LangGraph Node for detecting target platforms from enriched test cases
"""

import asyncio
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from collections import Counter

from src.langgraph.state.helix_state import HelixAutomationState


@dataclass
class PlatformEvidence:
    """Evidence for platform detection"""
    evidence_type: str
    evidence_value: str
    confidence: float
    source: str


@dataclass
class PlatformProfile:
    """Platform profile with detection patterns"""
    platform_id: str
    platform_name: str
    url_patterns: List[str]
    ui_patterns: List[str]
    terminology: List[str]
    element_patterns: List[str]
    confidence_threshold: float = 0.7


# Platform definitions
PLATFORM_PROFILES = {
    "salesforce_lightning": PlatformProfile(
        platform_id="salesforce_lightning",
        platform_name="Salesforce Lightning",
        url_patterns=[
            r".*\.salesforce\.com",
            r".*\.lightning\.force\.com",
            r".*\.my\.salesforce\.com",
            r"login\.salesforce\.com"
        ],
        ui_patterns=[
            "app launcher",
            "lightning",
            "setup",
            "waffle",
            "nine dots"
        ],
        terminology=[
            "opportunity", "lead", "account", "contact", "case",
            "campaign", "chatter", "trailhead", "org", "salesforce"
        ],
        element_patterns=[
            "slds-", "lightning-", "forceActionsText", "oneHeader",
            "appLauncher", "globalHeader"
        ]
    ),
    
    "salesforce_classic": PlatformProfile(
        platform_id="salesforce_classic",
        platform_name="Salesforce Classic",
        url_patterns=[
            r".*\.salesforce\.com",
            r"c\..*\.visual\.force\.com"
        ],
        ui_patterns=[
            "home tab",
            "classic",
            "sidebar",
            "setup menu"
        ],
        terminology=[
            "opportunity", "lead", "account", "contact", "case",
            "campaign", "salesforce", "setup"
        ],
        element_patterns=[
            "bPageBlock", "pbSubheader", "bodyCell", "dataCol",
            "relatedListStyle"
        ]
    ),
    
    "sap_fiori": PlatformProfile(
        platform_id="sap_fiori",
        platform_name="SAP Fiori",
        url_patterns=[
            r".*\.sap\.com",
            r".*fiori.*",
            r".*\.sapfiori\.com"
        ],
        ui_patterns=[
            "fiori",
            "launchpad",
            "tile",
            "shell bar"
        ],
        terminology=[
            "fiori", "launchpad", "tile", "sap", "s4hana",
            "shell", "workbench", "transaction"
        ],
        element_patterns=[
            "sapM", "sapUi", "fiori", "sapShell",
            "sapSplitter"
        ]
    ),
    
    "sap_gui": PlatformProfile(
        platform_id="sap_gui",
        platform_name="SAP GUI",
        url_patterns=[
            r".*\.sap\.com",
            r".*gui.*"
        ],
        ui_patterns=[
            "sap gui",
            "easy access",
            "transaction",
            "menu bar"
        ],
        terminology=[
            "transaction", "tcode", "sap gui", "easy access",
            "menu", "sap", "workbench"
        ],
        element_patterns=[
            "GuiApplication", "GuiConnection", "GuiSession",
            "wnd[0]", "usr/"
        ]
    ),
    
    "workday": PlatformProfile(
        platform_id="workday",
        platform_name="Workday",
        url_patterns=[
            r".*\.workday\.com",
            r".*\.wd\d+\.myworkday\.com"
        ],
        ui_patterns=[
            "workday",
            "dashboard",
            "inbox",
            "actions"
        ],
        terminology=[
            "workday", "employee", "manager", "dashboard",
            "inbox", "actions", "reports", "tenant"
        ],
        element_patterns=[
            "wd-", "workday", "WDCU", "WDControl"
        ]
    ),
    
    "servicenow": PlatformProfile(
        platform_id="servicenow",
        platform_name="ServiceNow",
        url_patterns=[
            r".*\.servicenow\.com",
            r".*\.service-now\.com"
        ],
        ui_patterns=[
            "servicenow",
            "incident",
            "ticket",
            "application navigator"
        ],
        terminology=[
            "servicenow", "incident", "ticket", "cmdb",
            "change request", "service catalog"
        ],
        element_patterns=[
            "sn-", "servicenow", "gsft_main",
            "navpage"
        ]
    ),
    
    "microsoft_dynamics": PlatformProfile(
        platform_id="microsoft_dynamics",
        platform_name="Microsoft Dynamics",
        url_patterns=[
            r".*\.dynamics\.com",
            r".*\.crm\.dynamics\.com"
        ],
        ui_patterns=[
            "dynamics",
            "crm",
            "ribbon",
            "command bar"
        ],
        terminology=[
            "dynamics", "crm", "entity", "form",
            "view", "ribbon", "workflow"
        ],
        element_patterns=[
            "ms-crm", "dynamics", "crmGrid",
            "crmForm"
        ]
    ),
    
    "oracle_cloud": PlatformProfile(
        platform_id="oracle_cloud",
        platform_name="Oracle Cloud",
        url_patterns=[
            r".*\.oraclecloud\.com",
            r".*\.oracle\.com"
        ],
        ui_patterns=[
            "oracle",
            "cloud",
            "navigator",
            "dashboard"
        ],
        terminology=[
            "oracle", "cloud", "fusion", "navigator",
            "dashboard", "workspace"
        ],
        element_patterns=[
            "af_", "oracle", "adf", "af:",
            "trinidad"
        ]
    ),
    
    "generic_web": PlatformProfile(
        platform_id="generic_web",
        platform_name="Generic Web Application",
        url_patterns=[
            r"https?://.*"
        ],
        ui_patterns=[
            "button",
            "form",
            "input",
            "login"
        ],
        terminology=[
            "login", "submit", "form", "button",
            "input", "page"
        ],
        element_patterns=[
            "btn", "form", "input", "div",
            "span", "a"
        ]
    )
}


async def agent_3_platform_detector(state: HelixAutomationState) -> HelixAutomationState:
    """
    LangGraph Node: Detect target platform from enriched test steps
    Updates shared state with platform context and confidence
    """
    
    print(f"🤖 Agent 3 (Platform Detector): Detecting target platform...")
    start_time = time.time()
    
    try:
        enriched_steps = state.get("enriched_steps", [])
        if not enriched_steps:
            state["platform_confidence"] = 0.0
            state["errors"].append("No enriched steps available for platform detection")
            return state
        
        # Collect evidence from multiple sources
        evidence = collect_platform_evidence(state)
        
        # Analyze evidence and score platforms
        platform_scores = analyze_platform_evidence(evidence)
        
        # Determine primary platform and alternatives
        platform_result = determine_platform(platform_scores)
        
        # Update state
        state["platform_context"] = platform_result["context"]
        state["platform_confidence"] = platform_result["confidence"]
        state["alternative_platforms"] = platform_result["alternatives"]
        state["current_agent"] = "Agent 3 (Platform Detector)"
        
        # Update performance metrics
        execution_time = time.time() - start_time
        state["performance_metrics"]["agent_3_duration"] = execution_time
        
        primary_platform = platform_result["context"]["primary_platform"]
        print(f"✅ Detected platform: {primary_platform} ({platform_result['confidence']:.1%} confidence) in {execution_time:.2f}s")
        
        # Show evidence summary
        evidence_summary = {}
        for ev in evidence:
            evidence_summary[ev.evidence_type] = evidence_summary.get(ev.evidence_type, 0) + 1
        print(f"📊 Evidence collected: {dict(evidence_summary)}")
        
        if platform_result["alternatives"]:
            print(f"🔄 Alternative platforms: {', '.join(platform_result['alternatives'][:3])}")
        
    except Exception as e:
        state["platform_confidence"] = 0.0
        if "errors" not in state:
            state["errors"] = []
        state["errors"].append(f"Agent 3 (Platform Detector) failed: {str(e)}")
        print(f"❌ Platform detection failed: {e}")
        import traceback
        traceback.print_exc()
    
    return state


def collect_platform_evidence(state: HelixAutomationState) -> List[PlatformEvidence]:
    """
    Collect evidence for platform detection from various sources
    """
    
    evidence = []
    
    # Evidence from raw input
    raw_input = state.get("raw_input", "").lower()
    evidence.extend(extract_evidence_from_text(raw_input, "raw_input"))
    
    # Evidence from enriched steps
    enriched_steps = state.get("enriched_steps", [])
    for step in enriched_steps:
        description = step.get("description", "").lower()
        evidence.extend(extract_evidence_from_text(description, "step_description"))
        
        # Evidence from target elements
        for element in step.get("target_elements", []):
            element_context = element.get("context", "").lower()
            evidence.extend(extract_evidence_from_text(element_context, "element_context"))
    
    # Evidence from test data
    parsed_test_case = state.get("parsed_test_case")
    if parsed_test_case and isinstance(parsed_test_case, dict):
        for step in parsed_test_case.get("steps", []):
            test_data = step.get("test_data", {})
            for key, value in test_data.items():
                evidence.extend(extract_evidence_from_text(f"{key} {value}".lower(), "test_data"))
    
    # Evidence from input metadata
    input_metadata = state.get("input_metadata", {})
    if "platform_hint" in input_metadata:
        evidence.append(PlatformEvidence(
            evidence_type="metadata_hint",
            evidence_value=str(input_metadata["platform_hint"]).lower(),
            confidence=0.9,
            source="input_metadata"
        ))
    
    return evidence


def extract_evidence_from_text(text: str, source: str) -> List[PlatformEvidence]:
    """
    Extract platform evidence from text
    """
    
    evidence = []
    
    for platform_id, profile in PLATFORM_PROFILES.items():
        
        # Check URL patterns
        for pattern in profile.url_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                evidence.append(PlatformEvidence(
                    evidence_type="url_pattern",
                    evidence_value=pattern,
                    confidence=0.9,
                    source=source
                ))
        
        # Check UI patterns
        for ui_term in profile.ui_patterns:
            if ui_term in text:
                evidence.append(PlatformEvidence(
                    evidence_type="ui_pattern",
                    evidence_value=ui_term,
                    confidence=0.7,
                    source=source
                ))
        
        # Check terminology
        for term in profile.terminology:
            if term in text:
                # Higher confidence for more specific terms
                confidence = 0.8 if len(term) > 5 else 0.6
                evidence.append(PlatformEvidence(
                    evidence_type="terminology",
                    evidence_value=term,
                    confidence=confidence,
                    source=source
                ))
        
        # Check element patterns
        for element_pattern in profile.element_patterns:
            if element_pattern in text:
                evidence.append(PlatformEvidence(
                    evidence_type="element_pattern",
                    evidence_value=element_pattern,
                    confidence=0.8,
                    source=source
                ))
    
    return evidence


def analyze_platform_evidence(evidence: List[PlatformEvidence]) -> Dict[str, float]:
    """
    Analyze collected evidence and score platforms
    """
    
    platform_scores = {platform_id: 0.0 for platform_id in PLATFORM_PROFILES.keys()}
    evidence_weights = {
        "url_pattern": 2.0,
        "element_pattern": 1.5,
        "ui_pattern": 1.2,
        "terminology": 1.0,
        "metadata_hint": 2.5
    }
    
    # Group evidence by platform
    platform_evidence = {platform_id: [] for platform_id in PLATFORM_PROFILES.keys()}
    
    for ev in evidence:
        # Find which platform this evidence supports
        for platform_id, profile in PLATFORM_PROFILES.items():
            if (ev.evidence_value in profile.url_patterns or
                ev.evidence_value in profile.ui_patterns or
                ev.evidence_value in profile.terminology or
                ev.evidence_value in profile.element_patterns):
                platform_evidence[platform_id].append(ev)
    
    # Calculate scores
    for platform_id, platform_ev_list in platform_evidence.items():
        if not platform_ev_list:
            continue
        
        # Base score from evidence count and confidence
        base_score = 0.0
        evidence_types_seen = set()
        
        for ev in platform_ev_list:
            weight = evidence_weights.get(ev.evidence_type, 1.0)
            base_score += ev.confidence * weight
            evidence_types_seen.add(ev.evidence_type)
        
        # Bonus for diverse evidence types
        diversity_bonus = len(evidence_types_seen) * 0.1
        
        # Penalty for generic platforms (they match too easily)
        if platform_id == "generic_web":
            base_score *= 0.5
        
        platform_scores[platform_id] = base_score + diversity_bonus
    
    # Normalize scores
    max_score = max(platform_scores.values()) if platform_scores.values() else 1.0
    if max_score > 0:
        for platform_id in platform_scores:
            platform_scores[platform_id] = min(1.0, platform_scores[platform_id] / max_score)
    
    return platform_scores


def determine_platform(platform_scores: Dict[str, float]) -> Dict[str, Any]:
    """
    Determine primary platform and alternatives from scores
    """
    
    # Sort platforms by score
    sorted_platforms = sorted(platform_scores.items(), key=lambda x: x[1], reverse=True)
    
    if not sorted_platforms or sorted_platforms[0][1] == 0:
        # No evidence found, default to generic web
        return {
            "context": {
                "primary_platform": "generic_web",
                "confidence": 0.5,
                "evidence": ["no specific platform patterns detected"],
                "detection_method": "default_fallback"
            },
            "confidence": 0.5,
            "alternatives": []
        }
    
    primary_platform_id, primary_score = sorted_platforms[0]
    primary_profile = PLATFORM_PROFILES[primary_platform_id]
    
    # Get alternatives (platforms with score > 0.3 and not primary)
    alternatives = []
    for platform_id, score in sorted_platforms[1:]:
        if score > 0.3:
            alternatives.append(platform_id)
    
    # Build evidence list
    evidence_list = []
    if primary_score > 0.7:
        evidence_list.append(f"strong {primary_profile.platform_name} patterns detected")
    elif primary_score > 0.5:
        evidence_list.append(f"moderate {primary_profile.platform_name} patterns detected")
    else:
        evidence_list.append(f"weak {primary_profile.platform_name} patterns detected")
    
    # Determine confidence level
    confidence = min(1.0, primary_score)
    
    # Adjust confidence based on alternatives
    if alternatives and sorted_platforms[1][1] > 0.7:
        # Strong alternative exists, reduce confidence
        confidence *= 0.8
    
    return {
        "context": {
            "primary_platform": primary_platform_id,
            "platform_name": primary_profile.platform_name,
            "confidence": confidence,
            "evidence": evidence_list,
            "detection_method": "pattern_analysis",
            "platform_scores": dict(sorted_platforms[:3])  # Top 3 scores
        },
        "confidence": confidence,
        "alternatives": alternatives[:3]  # Top 3 alternatives
    }


def get_platform_specific_hints(platform_id: str) -> Dict[str, Any]:
    """
    Get platform-specific hints for element finding
    """
    
    platform_hints = {
        "salesforce_lightning": {
            "common_selectors": [
                "[data-aura-class]",
                ".slds-button",
                "lightning-input",
                ".forceActionLink"
            ],
            "wait_strategies": ["lightning_page_load", "aura_component_ready"],
            "iframe_handling": "lightning_containers",
            "shadow_dom": True
        },
        
        "salesforce_classic": {
            "common_selectors": [
                ".btn",
                ".dataCol",
                ".pbButton"
            ],
            "wait_strategies": ["page_load", "form_ready"],
            "iframe_handling": "standard",
            "shadow_dom": False
        },
        
        "sap_fiori": {
            "common_selectors": [
                "[id*='sapM']",
                ".sapMBtn",
                ".sapUiIcon"
            ],
            "wait_strategies": ["ui5_ready", "component_load"],
            "iframe_handling": "ui5_containers",
            "shadow_dom": False
        },
        
        "workday": {
            "common_selectors": [
                "[data-automation-id]",
                ".wd-",
                "[aria-label]"
            ],
            "wait_strategies": ["workday_load", "component_ready"],
            "iframe_handling": "workday_frames",
            "shadow_dom": True
        },
        
        "generic_web": {
            "common_selectors": [
                "button",
                "input",
                ".btn",
                "#submit"
            ],
            "wait_strategies": ["page_load", "dom_ready"],
            "iframe_handling": "standard",
            "shadow_dom": False
        }
    }
    
    return platform_hints.get(platform_id, platform_hints["generic_web"])


def enhance_platform_context_with_step_analysis(state: HelixAutomationState) -> None:
    """
    Enhance platform context by analyzing step patterns
    """
    
    platform_context = state.get("platform_context", {})
    enriched_steps = state.get("enriched_steps", [])
    
    if not platform_context or not enriched_steps:
        return
    
    primary_platform = platform_context.get("primary_platform")
    if not primary_platform:
        return
    
    # Analyze step patterns for platform-specific insights
    step_patterns = analyze_step_patterns(enriched_steps, primary_platform)
    
    # Add patterns to platform context
    platform_context["step_patterns"] = step_patterns
    platform_context["platform_hints"] = get_platform_specific_hints(primary_platform)
    
    state["platform_context"] = platform_context


def analyze_step_patterns(enriched_steps: List[Dict[str, Any]], platform_id: str) -> Dict[str, Any]:
    """
    Analyze step patterns for platform-specific insights
    """
    
    patterns = {
        "common_actions": Counter(),
        "element_types": Counter(),
        "navigation_pattern": "unknown",
        "authentication_pattern": "unknown"
    }
    
    for step in enriched_steps:
        for element in step.get("target_elements", []):
            patterns["common_actions"][element.get("action_type", "unknown")] += 1
            patterns["element_types"][element.get("element_type", "unknown")] += 1
    
    # Detect navigation patterns
    if any("app launcher" in str(step).lower() for step in enriched_steps):
        patterns["navigation_pattern"] = "app_launcher"
    elif any("menu" in str(step).lower() for step in enriched_steps):
        patterns["navigation_pattern"] = "menu_based"
    elif any("tab" in str(step).lower() for step in enriched_steps):
        patterns["navigation_pattern"] = "tab_based"
    
    # Detect authentication patterns
    auth_steps = [step for step in enriched_steps 
                 if any("login" in str(element).lower() or "password" in str(element).lower() 
                       for element in step.get("target_elements", []))]
    
    if len(auth_steps) >= 3:
        patterns["authentication_pattern"] = "multi_step"
    elif len(auth_steps) >= 1:
        patterns["authentication_pattern"] = "simple"
    
    return patterns


# Test function for Agent 3
async def test_agent_3():
    """Test Agent 3 in isolation"""
    
    from src.langgraph.state.helix_state import create_initial_state
    
    # Test cases for different platforms
    test_cases = [
        {
            "name": "Salesforce Lightning",
            "raw_input": """
            Login to Salesforce Lightning
            Click the App Launcher (9 dots)
            Search for Opportunities
            Create new opportunity with amount $50000
            """,
            "enriched_steps": [
                {
                    "step_number": 1,
                    "description": "Login to Salesforce Lightning",
                    "target_elements": [
                        {"semantic_intent": "authentication", "element_type": "login_button", "context": "salesforce login"}
                    ]
                },
                {
                    "step_number": 2,
                    "description": "Click the App Launcher (9 dots)",
                    "target_elements": [
                        {"semantic_intent": "navigation", "element_type": "button", "context": "app launcher"}
                    ]
                },
                {
                    "step_number": 3,
                    "description": "Search for Opportunities",
                    "target_elements": [
                        {"semantic_intent": "search_interaction", "element_type": "search_field", "context": "opportunity search"}
                    ]
                }
            ]
        },
        {
            "name": "SAP Fiori",
            "raw_input": """
            Navigate to SAP Fiori Launchpad
            Click on Sales tile
            Create new sales order
            """,
            "enriched_steps": [
                {
                    "step_number": 1,
                    "description": "Navigate to SAP Fiori Launchpad",
                    "target_elements": [
                        {"semantic_intent": "navigation", "element_type": "page", "context": "fiori launchpad"}
                    ]
                },
                {
                    "step_number": 2,
                    "description": "Click on Sales tile",
                    "target_elements": [
                        {"semantic_intent": "navigation", "element_type": "tile", "context": "sales tile"}
                    ]
                }
            ]
        },
        {
            "name": "Generic Web App",
            "raw_input": """
            Login to the web application
            Fill out the contact form
            Submit the form
            """,
            "enriched_steps": [
                {
                    "step_number": 1,
                    "description": "Login to the web application",
                    "target_elements": [
                        {"semantic_intent": "authentication", "element_type": "login_button", "context": "login"}
                    ]
                },
                {
                    "step_number": 2,
                    "description": "Fill out the contact form",
                    "target_elements": [
                        {"semantic_intent": "form_interaction", "element_type": "form", "context": "contact form"}
                    ]
                }
            ]
        }
    ]
    
    print("🧪 Testing Agent 3 (Platform Detector)...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        # Create initial state
        initial_state = create_initial_state(
            raw_input=test_case["raw_input"],
            input_metadata={"format": "test"}
        )
        initial_state["enriched_steps"] = test_case["enriched_steps"]
        
        # Run Agent 3
        result_state = await agent_3_platform_detector(initial_state)
        
        # Display results
        platform_context = result_state.get("platform_context") if result_state else None
        platform_confidence = result_state.get("platform_confidence", 0) if result_state else 0
        alternatives = result_state.get("alternative_platforms", []) if result_state else []
        errors = result_state.get("errors", []) if result_state else []
        
        print(f"✅ Platform Detection Results:")
        if platform_context:
            print(f"   - Primary platform: {platform_context.get('primary_platform', 'N/A')}")
            print(f"   - Platform name: {platform_context.get('platform_name', 'N/A')}")
        else:
            print(f"   - Primary platform: N/A")
            print(f"   - Platform name: N/A")
        print(f"   - Confidence: {platform_confidence:.1%}")
        print(f"   - Alternatives: {', '.join(alternatives) if alternatives else 'None'}")
        
        if errors:
            print(f"❌ Errors:")
            for error in errors:
                print(f"     {error}")
        
        # Show evidence
        evidence = platform_context.get("evidence", [])
        if evidence:
            print(f"📊 Evidence:")
            for ev in evidence:
                print(f"     {ev}")
        
        # Show platform scores
        scores = platform_context.get("platform_scores", {})
        if scores:
            print(f"🎯 Top platform scores:")
            for platform, score in list(scores.items())[:3]:
                print(f"     {platform}: {score:.2f}")
    
    print(f"\n🎯 Agent 3 testing complete!")


if __name__ == "__main__":
    asyncio.run(test_agent_3())