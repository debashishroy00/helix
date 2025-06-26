#!/usr/bin/env python3
"""
Debug script for Agent 3 Platform Detector
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_agent3_simple():
    """Simple test for Agent 3"""
    
    try:
        from langgraph.state.helix_state import create_initial_state
        from langgraph.agents.agent_3_platform.platform_detector import agent_3_platform_detector
        
        # Create a simple test state with enriched steps
        initial_state = create_initial_state(
            raw_input="Login to Salesforce",
            input_metadata={"format": "test"}
        )
        
        # Add minimal enriched steps
        initial_state["enriched_steps"] = [
            {
                "step_number": 1,
                "description": "Login to Salesforce",
                "target_elements": [
                    {"semantic_intent": "authentication", "element_type": "login_button", "context": "salesforce login"}
                ]
            }
        ]
        
        print("Initial state created successfully")
        print(f"State keys: {list(initial_state.keys())}")
        print(f"Enriched steps: {len(initial_state.get('enriched_steps', []))}")
        
        # Run Agent 3
        print("\nRunning Agent 3...")
        result_state = await agent_3_platform_detector(initial_state)
        
        print("\nAgent 3 completed")
        print(f"Result state type: {type(result_state)}")
        
        if result_state:
            print(f"Platform context: {result_state.get('platform_context')}")
            print(f"Platform confidence: {result_state.get('platform_confidence', 0)}")
            print(f"Errors: {result_state.get('errors', [])}")
        else:
            print("Result state is None!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent3_simple())