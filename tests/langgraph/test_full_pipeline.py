"""
Helix Automation: Full Pipeline Integration Test
Tests the complete Agent 1 -> 2 -> 3 -> 4 pipeline
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.langgraph.state.helix_state import create_initial_state
from src.langgraph.workflows.full_workflow import HelixAutomationWorkflow
from src.langgraph.agents.agent_1_parser.test_case_parser import test_agent_1
from src.langgraph.agents.agent_2_intent.intent_extractor import test_agent_2
from src.langgraph.agents.agent_3_platform.platform_detector import test_agent_3


async def test_individual_agents():
    """Test each agent individually"""
    
    print("🔬 TESTING INDIVIDUAL AGENTS")
    print("=" * 50)
    
    try:
        print("\n1️⃣  Testing Agent 1 (Parser)...")
        await test_agent_1()
        print("✅ Agent 1 test completed")
    except Exception as e:
        print(f"❌ Agent 1 test failed: {e}")
    
    try:
        print("\n2️⃣  Testing Agent 2 (Intent Extractor)...")
        await test_agent_2()
        print("✅ Agent 2 test completed")
    except Exception as e:
        print(f"❌ Agent 2 test failed: {e}")
    
    try:
        print("\n3️⃣  Testing Agent 3 (Platform Detector)...")
        await test_agent_3()
        print("✅ Agent 3 test completed")
    except Exception as e:
        print(f"❌ Agent 3 test failed: {e}")


async def test_agent_integration():
    """Test agents working together in sequence"""
    
    print("\n🔗 TESTING AGENT INTEGRATION")
    print("=" * 50)
    
    # Test case for sequential agent execution
    test_input = """
    Test Case: Salesforce Login and Navigation
    
    Description: Test user login and basic navigation in Salesforce
    
    Step 1: Navigate to https://login.salesforce.com
    Step 2: Enter username test@company.com
    Step 3: Enter password password123
    Step 4: Click Login button
    Expected: User should be logged in successfully
    
    Step 5: Click the App Launcher button
    Expected: App launcher menu should open
    
    Step 6: Search for Opportunities
    Expected: Search results should show Opportunities app
    
    Step 7: Click Opportunities app
    Expected: Opportunities list page should load
    """
    
    print(f"📝 Test input: {len(test_input)} characters")
    
    # Create initial state
    initial_state = create_initial_state(
        raw_input=test_input,
        input_metadata={"format": "plain_text", "test_type": "integration"}
    )
    
    # Test Agent 1 -> 2 -> 3 sequence
    try:
        from src.langgraph.agents.agent_1_parser.test_case_parser import agent_1_parser
        from src.langgraph.agents.agent_2_intent.intent_extractor import agent_2_intent_extractor
        from src.langgraph.agents.agent_3_platform.platform_detector import agent_3_platform_detector
        
        # Agent 1: Parse
        print("\n🤖 Running Agent 1 (Parser)...")
        state_after_1 = await agent_1_parser(initial_state)
        
        parsed_steps = len(state_after_1.get("parsed_test_case", {}).get("steps", []))
        parsing_confidence = state_after_1.get("parsing_confidence", 0)
        print(f"   ✅ Parsed {parsed_steps} steps with {parsing_confidence:.1%} confidence")
        
        # Agent 2: Extract Intents
        print("\n🧠 Running Agent 2 (Intent Extractor)...")
        state_after_2 = await agent_2_intent_extractor(state_after_1)
        
        enriched_steps = len(state_after_2.get("enriched_steps", []))
        intent_confidence = state_after_2.get("intent_confidence", 0)
        semantic_intents = len(state_after_2.get("semantic_intents", []))
        print(f"   ✅ Enriched {enriched_steps} steps, extracted {semantic_intents} intents with {intent_confidence:.1%} confidence")
        
        # Agent 3: Detect Platform
        print("\n🌐 Running Agent 3 (Platform Detector)...")
        state_after_3 = await agent_3_platform_detector(state_after_2)
        
        platform_context = state_after_3.get("platform_context", {})
        platform_confidence = state_after_3.get("platform_confidence", 0)
        detected_platform = platform_context.get("platform_name", "Unknown")
        print(f"   ✅ Detected platform: {detected_platform} with {platform_confidence:.1%} confidence")
        
        # Summary of data flow
        print(f"\n📊 Integration Results:")
        print(f"   Raw input → {parsed_steps} parsed steps")
        print(f"   Parsed steps → {enriched_steps} enriched steps")
        print(f"   Enriched steps → {semantic_intents} semantic intents")
        print(f"   Platform detected: {detected_platform}")
        
        # Check data consistency
        data_consistent = validate_data_consistency(state_after_3)
        print(f"   Data consistency: {'✅ Valid' if data_consistent else '❌ Issues detected'}")
        
        return state_after_3
        
    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def validate_data_consistency(state):
    """Validate that data flows consistently between agents"""
    
    issues = []
    
    # Check that parsed steps match enriched steps count
    parsed_steps = state.get("parsed_test_case", {}).get("steps", [])
    enriched_steps = state.get("enriched_steps", [])
    
    if len(parsed_steps) != len(enriched_steps):
        issues.append(f"Step count mismatch: {len(parsed_steps)} parsed vs {len(enriched_steps)} enriched")
    
    # Check that enriched steps have target elements
    steps_with_elements = sum(1 for step in enriched_steps if step.get("target_elements"))
    if steps_with_elements == 0:
        issues.append("No target elements found in enriched steps")
    
    # Check platform context
    platform_context = state.get("platform_context")
    if not platform_context or not platform_context.get("primary_platform"):
        issues.append("No platform detected")
    
    # Check confidence scores are reasonable
    parsing_conf = state.get("parsing_confidence", 0)
    intent_conf = state.get("intent_confidence", 0)
    platform_conf = state.get("platform_confidence", 0)
    
    if parsing_conf < 0.3:
        issues.append(f"Low parsing confidence: {parsing_conf:.1%}")
    if intent_conf < 0.3:
        issues.append(f"Low intent confidence: {intent_conf:.1%}")
    if platform_conf < 0.3:
        issues.append(f"Low platform confidence: {platform_conf:.1%}")
    
    # Log issues if any
    if issues:
        print(f"⚠️  Data consistency issues:")
        for issue in issues:
            print(f"     {issue}")
        return False
    
    return True


async def test_full_workflow():
    """Test the complete workflow"""
    
    print("\n🚀 TESTING FULL WORKFLOW")
    print("=" * 50)
    
    workflow = HelixAutomationWorkflow()
    
    # Comprehensive test case
    test_case = {
        "name": "Complete Salesforce Workflow",
        "input": """
        Test Case: Salesforce Opportunity Management
        
        Objective: Test complete opportunity creation workflow
        
        Prerequisites: User has valid Salesforce credentials
        
        Test Steps:
        1. Navigate to Salesforce login page (https://login.salesforce.com)
        2. Enter username: automation.tester@company.com
        3. Enter password: TestPass123!
        4. Click "Log In to Salesforce" button
        5. Wait for dashboard to load
        6. Click the App Launcher (9 dots icon in top left)
        7. Search for "Opportunities" in the search box
        8. Click on "Opportunities" from search results
        9. Click "New" button to create opportunity
        10. Enter Opportunity Name: "Q4 Enterprise Deal"
        11. Select Account: "Acme Corporation"
        12. Select Stage: "Prospecting"
        13. Enter Amount: $150,000
        14. Select Close Date: 3 months from today
        15. Click "Save" button
        16. Verify opportunity appears in list view
        17. Verify opportunity details are correct
        
        Expected Results:
        - User successfully logs into Salesforce
        - App launcher opens when clicked
        - Opportunities app is accessible
        - New opportunity is created with correct details
        - Opportunity appears in the list view
        """,
        "metadata": {
            "format": "plain_text",
            "platform_hint": "salesforce_lightning",
            "test_type": "comprehensive"
        }
    }
    
    print(f"📋 Test: {test_case['name']}")
    print(f"📝 Input length: {len(test_case['input'])} characters")
    
    # Create initial state
    initial_state = create_initial_state(
        raw_input=test_case["input"],
        input_metadata=test_case["metadata"]
    )
    
    # Execute full workflow
    try:
        result = await workflow.ainvoke(initial_state)
        
        # Detailed analysis of results
        print(f"\n📊 WORKFLOW ANALYSIS")
        print("-" * 30)
        
        # Agent performance
        metrics = result.get("performance_metrics", {})
        total_time = metrics.get("total_workflow_duration", 0)
        
        print(f"⏱️  Performance:")
        for metric_name, duration in metrics.items():
            if "duration" in metric_name and metric_name != "total_workflow_duration":
                agent_name = metric_name.replace("_duration", "").replace("agent_", "Agent ")
                percentage = (duration / total_time * 100) if total_time > 0 else 0
                print(f"   {agent_name}: {duration:.2f}s ({percentage:.1f}%)")
        print(f"   Total: {total_time:.2f}s")
        
        # Quality metrics
        print(f"\n🎯 Quality Metrics:")
        print(f"   Overall confidence: {result.get('confidence_score', 0):.1%}")
        print(f"   Parsing confidence: {result.get('parsing_confidence', 0):.1%}")
        print(f"   Intent confidence: {result.get('intent_confidence', 0):.1%}")
        print(f"   Platform confidence: {result.get('platform_confidence', 0):.1%}")
        print(f"   Element success rate: {result.get('element_success_rate', 0):.1%}")
        
        # Content analysis
        parsed_case = result.get("parsed_test_case", {})
        enriched_steps = result.get("enriched_steps", [])
        semantic_intents = result.get("semantic_intents", [])
        element_strategies = result.get("element_strategies", [])
        
        print(f"\n📈 Content Analysis:")
        print(f"   Test steps identified: {len(parsed_case.get('steps', []))}")
        print(f"   Steps enriched: {len(enriched_steps)}")
        print(f"   Semantic intents: {len(semantic_intents)}")
        print(f"   Element strategies: {len(element_strategies)}")
        print(f"   Successful elements: {len([s for s in element_strategies if s.get('success')])}")
        
        # Platform detection
        platform_context = result.get("platform_context", {})
        print(f"\n🌐 Platform Detection:")
        print(f"   Primary: {platform_context.get('platform_name', 'Unknown')}")
        print(f"   Confidence: {result.get('platform_confidence', 0):.1%}")
        alternatives = result.get("alternative_platforms", [])
        if alternatives:
            print(f"   Alternatives: {', '.join(alternatives[:3])}")
        
        # Error analysis
        errors = result.get("errors", [])
        if errors:
            print(f"\n❌ Errors ({len(errors)}):")
            for i, error in enumerate(errors[:5], 1):
                print(f"   {i}. {error}")
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more")
        
        # Final assessment
        execution_ready = result.get("execution_ready", False)
        print(f"\n🎯 Final Assessment:")
        print(f"   Execution ready: {'✅ Yes' if execution_ready else '❌ No'}")
        
        if execution_ready:
            script_length = len(result.get("final_script", ""))
            print(f"   Generated script: {script_length} characters")
            print(f"   Framework: Playwright")
        else:
            print(f"   Reasons not ready:")
            if result.get("parsing_confidence", 0) < 0.5:
                print(f"     - Low parsing confidence")
            if result.get("intent_confidence", 0) < 0.4:
                print(f"     - Low intent confidence")
            if result.get("element_success_rate", 0) < 0.6:
                print(f"     - Low element success rate")
        
        return result
        
    except Exception as e:
        print(f"❌ Full workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def run_comprehensive_tests():
    """Run all tests in sequence"""
    
    print("🧪 HELIX AUTOMATION - COMPREHENSIVE PIPELINE TEST")
    print("Testing Agents 1-4 Integration")
    print("=" * 70)
    
    start_time = asyncio.get_event_loop().time()
    
    # Test 1: Individual agents
    await test_individual_agents()
    
    # Test 2: Agent integration
    integration_result = await test_agent_integration()
    
    # Test 3: Full workflow
    workflow_result = await test_full_workflow()
    
    # Overall assessment
    end_time = asyncio.get_event_loop().time()
    total_test_time = end_time - start_time
    
    print(f"\n" + "=" * 70)
    print("🎯 COMPREHENSIVE TEST SUMMARY")
    print("=" * 70)
    print(f"⏱️  Total test time: {total_test_time:.2f}s")
    
    # Test results
    tests_passed = 0
    total_tests = 3
    
    if integration_result:
        tests_passed += 1
        print("✅ Agent integration test: PASSED")
    else:
        print("❌ Agent integration test: FAILED")
    
    if workflow_result:
        tests_passed += 1
        print("✅ Full workflow test: PASSED")
        
        if workflow_result.get("execution_ready"):
            tests_passed += 1
            print("✅ Execution readiness: PASSED")
        else:
            print("⚠️  Execution readiness: NOT READY")
    else:
        print("❌ Full workflow test: FAILED")
        print("❌ Execution readiness: FAILED")
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if tests_passed == total_tests:
        print("   ✅ All tests passed! Ready for Phase 3 (conditional logic)")
        print("   🔄 Next: Implement Agents 5-8 and conditional workflows")
    elif tests_passed >= 2:
        print("   ⚠️  Core functionality working, minor issues to address")
        print("   🔧 Review error logs and improve element finding")
    else:
        print("   ❌ Significant issues detected")
        print("   🚧 Debug agent failures before proceeding")
    
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())