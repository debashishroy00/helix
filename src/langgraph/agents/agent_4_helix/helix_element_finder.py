"""
Helix Automation: Agent 4 - LangGraph Integration
Wraps existing 10-layer Helix AI Engine as a LangGraph node
"""

import asyncio
import httpx
import time
from typing import Dict, Any, List
from src.langgraph.state.helix_state import HelixAutomationState

async def agent_4_helix_element_finder(state: HelixAutomationState) -> HelixAutomationState:
    """
    LangGraph Node: Integration with existing 10-layer Helix AI Engine
    This wraps your existing Helix Engine API as a LangGraph agent
    """
    
    print(f"🤖 Agent 4 (Helix Engine): Finding elements...")
    start_time = time.time()
    
    try:
        # For Phase 1: Create mock enriched steps if not provided by Agent 2
        if not state.get("enriched_steps"):
            # Parse raw input to create basic enriched steps
            enriched_steps = parse_raw_input_to_steps(state["raw_input"])
            state["enriched_steps"] = enriched_steps
        
        # For Phase 1: Create mock platform context if not provided by Agent 3  
        if not state.get("platform_context"):
            platform_context = detect_basic_platform(state["raw_input"])
            state["platform_context"] = platform_context
        
        enriched_steps = state["enriched_steps"]
        platform_context = state["platform_context"]
        
        element_strategies = []
        successful_finds = 0
        total_elements = 0
        
        # Process each step to find elements
        for step in enriched_steps:
            if step.get("target_elements"):
                for target in step["target_elements"]:
                    total_elements += 1
                    
                    # Call existing Helix AI Engine API
                    strategy = await call_helix_ai_engine(
                        intent=target["semantic_intent"],
                        platform=platform_context["primary_platform"],
                        context={
                            "page_context": step.get("context", {}),
                            "step_description": step["description"],
                            "platform_hints": platform_context.get("evidence", [])
                        }
                    )
                    
                    element_strategies.append({
                        "step_id": step["step_number"],
                        "target": target,
                        "strategy": strategy,
                        "success": strategy["found"],
                        "confidence": strategy["confidence"]
                    })
                    
                    if strategy["found"]:
                        successful_finds += 1
        
        # Calculate success rate
        success_rate = successful_finds / total_elements if total_elements > 0 else 0.0
        
        # Update state
        state["element_strategies"] = element_strategies
        state["element_success_rate"] = success_rate
        state["failed_elements"] = [
            es for es in element_strategies if not es["success"]
        ]
        state["current_agent"] = "Agent 4 (Helix Engine)"
        
        # Update performance metrics
        execution_time = time.time() - start_time
        state["performance_metrics"]["agent_4_duration"] = execution_time
        
        print(f"✅ Found {successful_finds}/{total_elements} elements ({success_rate:.1%}) in {execution_time:.2f}s")
        
    except Exception as e:
        state["element_success_rate"] = 0.0
        state["errors"].append(f"Agent 4 (Helix Engine) failed: {str(e)}")
        print(f"❌ Agent 4 failed: {e}")
    
    return state


async def call_helix_ai_engine(intent: str, platform: str, context: Dict) -> Dict:
    """
    Interface to existing 10-layer Helix AI Engine
    This calls the actual Helix Engine API that's already working
    """
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8000/find_element_comprehensive",
                json={
                    "intent": intent,
                    "platform": platform,
                    "context": context,
                    "html_content": context.get("page_content", "")
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "found": result.get("found", False),
                    "selector": result.get("best_strategy", {}).get("selector", ""),
                    "confidence": result.get("confidence", 0.0),
                    "method": result.get("strategy", "unknown"),
                    "fallback_strategies": result.get("fallback_strategies", []),
                    "timing_ms": result.get("timing", 0),
                    "layers_executed": result.get("layers_executed", 0)
                }
            else:
                return {
                    "found": False,
                    "selector": "",
                    "confidence": 0.0,
                    "method": "api_error",
                    "error": f"API returned {response.status_code}"
                }
                
    except Exception as e:
        return {
            "found": False,
            "selector": "",
            "confidence": 0.0,
            "method": "connection_error", 
            "error": str(e)
        }


def parse_raw_input_to_steps(raw_input: str) -> List[Dict[str, Any]]:
    """
    Phase 1: Basic parsing of raw input to enriched steps
    Later this will be replaced by Agent 1 (Parser)
    """
    
    # Simple parsing for common patterns
    lines = raw_input.strip().split('\n')
    enriched_steps = []
    
    step_number = 1
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Extract basic actions and intents
        target_elements = []
        
        if any(word in line.lower() for word in ['login', 'sign in']):
            if 'button' in line.lower():
                target_elements.append({
                    "semantic_intent": "login button",
                    "description": line,
                    "element_type": "button"
                })
            elif 'username' in line.lower() or 'email' in line.lower():
                target_elements.append({
                    "semantic_intent": "username field",
                    "description": line,
                    "element_type": "input"
                })
            elif 'password' in line.lower():
                target_elements.append({
                    "semantic_intent": "password field", 
                    "description": line,
                    "element_type": "input"
                })
        
        elif 'app launcher' in line.lower():
            target_elements.append({
                "semantic_intent": "app launcher button",
                "description": line,
                "element_type": "button"
            })
            
        elif 'opportunity' in line.lower() and 'new' in line.lower():
            target_elements.append({
                "semantic_intent": "new opportunity button",
                "description": line,
                "element_type": "button"
            })
        
        if target_elements:  # Only add steps with target elements
            enriched_steps.append({
                "step_number": step_number,
                "description": line,
                "target_elements": target_elements,
                "context": {}
            })
            step_number += 1
    
    return enriched_steps


def detect_basic_platform(raw_input: str) -> Dict[str, Any]:
    """
    Phase 1: Basic platform detection 
    Later this will be replaced by Agent 3 (Platform Detector)
    """
    
    raw_lower = raw_input.lower()
    
    if 'salesforce' in raw_lower:
        return {
            "primary_platform": "salesforce_lightning",
            "confidence": 0.9,
            "evidence": ["salesforce mentioned in input"],
            "alternatives": ["salesforce_classic"]
        }
    elif 'sap' in raw_lower:
        return {
            "primary_platform": "sap_fiori",
            "confidence": 0.8,
            "evidence": ["sap mentioned in input"],
            "alternatives": ["sap_gui"]
        }
    elif 'workday' in raw_lower:
        return {
            "primary_platform": "workday",
            "confidence": 0.8,
            "evidence": ["workday mentioned in input"],
            "alternatives": []
        }
    else:
        # Default to generic web platform
        return {
            "primary_platform": "generic_web",
            "confidence": 0.5,
            "evidence": ["no specific platform detected"],
            "alternatives": ["salesforce_lightning", "sap_fiori"]
        }


# Test function for Agent 4
async def test_agent_4():
    """Test Agent 4 in isolation"""
    
    from src.langgraph.state.helix_state import create_initial_state
    
    # Create test state
    test_input = """
    Login to Salesforce with username test@company.com
    Click the app launcher button
    Create new opportunity
    """
    
    initial_state = create_initial_state(test_input)
    
    print("🧪 Testing Agent 4 (Helix Engine Integration)...")
    
    # Run Agent 4
    result_state = await agent_4_helix_element_finder(initial_state)
    
    print(f"\n📊 Results:")
    print(f"- Elements found: {len(result_state['element_strategies'])}")
    print(f"- Success rate: {result_state['element_success_rate']:.1%}")
    print(f"- Execution time: {result_state['performance_metrics'].get('agent_4_duration', 0):.2f}s")
    print(f"- Errors: {len(result_state['errors'])}")
    
    if result_state['errors']:
        print("❌ Errors:")
        for error in result_state['errors']:
            print(f"   {error}")
    
    return result_state


if __name__ == "__main__":
    asyncio.run(test_agent_4())