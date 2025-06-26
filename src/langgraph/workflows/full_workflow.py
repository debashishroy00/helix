"""
Helix Automation: Full LangGraph Workflow
Orchestrates all agents in a complete automation pipeline
"""

import asyncio
import time
from typing import Dict, Any

from src.langgraph.state.helix_state import HelixAutomationState, create_initial_state
from src.langgraph.agents.agent_1_parser.test_case_parser import agent_1_parser
from src.langgraph.agents.agent_2_intent.intent_extractor import agent_2_intent_extractor
from src.langgraph.agents.agent_3_platform.platform_detector import agent_3_platform_detector
from src.langgraph.agents.agent_4_helix.helix_element_finder import agent_4_helix_element_finder


class HelixAutomationWorkflow:
    """
    Complete Helix Automation workflow using LangGraph pattern
    Phase 2: Linear pipeline with Agents 1-4
    """
    
    def __init__(self):
        self.agents = {
            "parse_test_case": agent_1_parser,
            "extract_intent": agent_2_intent_extractor,
            "detect_platform": agent_3_platform_detector,
            "find_elements": agent_4_helix_element_finder
        }
        
        # Linear workflow for Phase 2
        self.workflow_sequence = [
            "parse_test_case",
            "extract_intent", 
            "detect_platform",
            "find_elements"
        ]
    
    async def ainvoke(self, initial_state: HelixAutomationState) -> HelixAutomationState:
        """Execute the full workflow"""
        
        print("🚀 Starting Helix Automation full workflow...")
        print(f"📝 Input: {initial_state['raw_input'][:100]}...")
        
        workflow_start_time = time.time()
        current_state = initial_state.copy()
        
        # Execute agents in sequence
        for agent_name in self.workflow_sequence:
            print(f"\n🔄 Executing {agent_name}...")
            
            try:
                agent_function = self.agents[agent_name]
                current_state = await agent_function(current_state)
                
                # Check for critical errors that should stop the workflow
                if self.should_stop_workflow(current_state, agent_name):
                    print(f"⚠️  Workflow stopped after {agent_name} due to critical errors")
                    break
                    
            except Exception as e:
                error_msg = f"Agent {agent_name} failed: {str(e)}"
                current_state["errors"].append(error_msg)
                print(f"❌ {error_msg}")
                
                # For critical agents, stop the workflow
                if agent_name in ["parse_test_case"]:
                    print(f"💥 Critical agent {agent_name} failed, stopping workflow")
                    break
        
        # Generate final results
        current_state = await self.generate_final_results(current_state)
        
        # Calculate overall metrics
        total_time = time.time() - workflow_start_time
        current_state["performance_metrics"]["total_workflow_duration"] = total_time
        
        # Display final summary
        self.display_workflow_summary(current_state, total_time)
        
        return current_state
    
    def should_stop_workflow(self, state: HelixAutomationState, agent_name: str) -> bool:
        """
        Determine if workflow should stop based on current state
        """
        
        # Stop if parsing completely failed
        if agent_name == "parse_test_case":
            if state.get("parsing_confidence", 0) == 0.0:
                return True
        
        # Stop if no intents could be extracted
        elif agent_name == "extract_intent":
            if state.get("intent_confidence", 0) == 0.0:
                return True
        
        # Platform detection failure is not critical, can continue with generic
        elif agent_name == "detect_platform":
            if state.get("platform_confidence", 0) == 0.0:
                # Set default platform and continue
                state["platform_context"] = {
                    "primary_platform": "generic_web",
                    "confidence": 0.5,
                    "evidence": ["fallback to generic web"],
                    "detection_method": "fallback"
                }
                state["platform_confidence"] = 0.5
        
        # Element finding failure is not critical for Phase 2
        # (will be critical when we add self-healing in Phase 3)
        
        return False
    
    async def generate_final_results(self, state: HelixAutomationState) -> HelixAutomationState:
        """
        Generate final workflow results and determine execution readiness
        """
        
        # Calculate overall confidence score
        confidence_components = [
            state.get("parsing_confidence", 0) * 0.2,
            state.get("intent_confidence", 0) * 0.3,
            state.get("platform_confidence", 0) * 0.2,
            state.get("element_success_rate", 0) * 0.3
        ]
        
        overall_confidence = sum(confidence_components)
        state["confidence_score"] = overall_confidence
        
        # Determine execution readiness
        min_parsing_confidence = 0.5
        min_intent_confidence = 0.4
        min_element_success = 0.6
        
        is_ready = (
            state.get("parsing_confidence", 0) >= min_parsing_confidence and
            state.get("intent_confidence", 0) >= min_intent_confidence and
            state.get("element_success_rate", 0) >= min_element_success
        )
        
        state["execution_ready"] = is_ready
        
        # Generate mock script for Phase 2 (will be replaced by Agent 6 in Phase 4)
        if is_ready:
            state["final_script"] = await self.generate_mock_automation_script(state)
        
        return state
    
    async def generate_mock_automation_script(self, state: HelixAutomationState) -> str:
        """
        Generate a mock automation script based on the workflow results
        Phase 2: Enhanced mock generation
        """
        
        platform_context = state.get("platform_context", {})
        primary_platform = platform_context.get("primary_platform", "generic_web")
        enriched_steps = state.get("enriched_steps", [])
        element_strategies = state.get("element_strategies", [])
        
        script_lines = [
            "// Generated by Helix Automation - Phase 2",
            f"// Target Platform: {platform_context.get('platform_name', 'Generic Web')}",
            f"// Confidence Score: {state.get('confidence_score', 0):.1%}",
            "",
            "const { chromium } = require('playwright');",
            "",
            "async function runHelixAutomation() {",
            "  const browser = await chromium.launch({ headless: false });",
            "  const page = await browser.newPage();",
            "",
            "  try {"
        ]
        
        # Add platform-specific setup
        if primary_platform == "salesforce_lightning":
            script_lines.extend([
                "    // Salesforce Lightning specific setup",
                "    await page.setViewportSize({ width: 1200, height: 800 });",
                "    await page.waitForTimeout(2000);"
            ])
        elif primary_platform.startswith("sap"):
            script_lines.extend([
                "    // SAP specific setup", 
                "    await page.setViewportSize({ width: 1024, height: 768 });",
                "    await page.waitForTimeout(3000);"
            ])
        
        script_lines.append("")
        
        # Generate actions from element strategies
        step_counter = 1
        for strategy in element_strategies:
            if strategy.get("success", False):
                target = strategy["target"]
                selector = strategy["strategy"]["selector"] if strategy.get("strategy") else ""
                element_type = target.get("element_type", "unknown")
                semantic_intent = target.get("semantic_intent", "")
                description = target.get("description", "Action")
                
                # Skip if no selector
                if not selector:
                    continue
                
                script_lines.append(f"    // Step {step_counter}: {description}")
                
                if element_type == "input" or "field" in element_type:
                    if "username" in semantic_intent or "email" in semantic_intent:
                        script_lines.append(f"    await page.fill('{selector}', 'test@company.com');")
                    elif "password" in semantic_intent:
                        script_lines.append(f"    await page.fill('{selector}', 'password123');")
                    elif target.get("value"):
                        script_lines.append(f"    await page.fill('{selector}', '{target['value']}');")
                    else:
                        script_lines.append(f"    await page.fill('{selector}', 'test_value');")
                
                elif element_type == "button" or element_type == "link":
                    script_lines.append(f"    await page.click('{selector}');")
                    
                    # Add wait logic based on intent
                    if "login" in semantic_intent:
                        script_lines.append("    await page.waitForLoadState('networkidle');")
                    elif "navigation" in semantic_intent:
                        script_lines.append("    await page.waitForTimeout(2000);")
                
                elif element_type == "dropdown" or element_type == "select":
                    if target.get("value"):
                        script_lines.append(f"    await page.selectOption('{selector}', '{target['value']}');")
                    else:
                        script_lines.append(f"    await page.selectOption('{selector}', {{ index: 0 }});")
                
                else:
                    # Generic interaction
                    script_lines.append(f"    await page.click('{selector}');")
                
                script_lines.append("    await page.waitForTimeout(1000);")
                script_lines.append("")
                step_counter += 1
        
        # Add verification steps
        verification_steps = [step for step in enriched_steps 
                            if any("verify" in elem.get("semantic_intent", "") 
                                  for elem in step.get("target_elements", []))]
        
        if verification_steps:
            script_lines.append("    // Verification steps")
            for step in verification_steps:
                description = step.get("description", "")
                script_lines.append(f"    // TODO: Verify - {description}")
            script_lines.append("")
        
        script_lines.extend([
            "    console.log('✅ Automation completed successfully');",
            "",
            "  } catch (error) {",
            "    console.error('❌ Automation failed:', error);",
            "    throw error;",
            "  } finally {",
            "    await browser.close();",
            "  }",
            "}",
            "",
            "// Execute the automation",
            "runHelixAutomation().catch(console.error);"
        ])
        
        return "\n".join(script_lines)
    
    def display_workflow_summary(self, state: HelixAutomationState, total_time: float):
        """
        Display comprehensive workflow summary
        """
        
        print("\n" + "=" * 70)
        print("🎯 HELIX AUTOMATION WORKFLOW SUMMARY")
        print("=" * 70)
        
        # Overall results
        print(f"⏱️  Total execution time: {total_time:.2f}s")
        print(f"🎯 Overall confidence: {state.get('confidence_score', 0):.1%}")
        print(f"✅ Execution ready: {state.get('execution_ready', False)}")
        
        # Agent performance
        print(f"\n📊 Agent Performance:")
        metrics = state.get("performance_metrics", {})
        for agent, duration in metrics.items():
            if "duration" in agent:
                agent_name = agent.replace("_duration", "").replace("agent_", "Agent ")
                print(f"   {agent_name}: {duration:.2f}s")
        
        # Parsing results
        parsed_case = state.get("parsed_test_case", {})
        print(f"\n📝 Parsing Results:")
        print(f"   Test ID: {parsed_case.get('test_id', 'N/A')}")
        print(f"   Title: {parsed_case.get('title', 'N/A')}")
        print(f"   Steps parsed: {len(parsed_case.get('steps', []))}")
        print(f"   Confidence: {state.get('parsing_confidence', 0):.1%}")
        
        # Intent extraction results
        enriched_steps = state.get("enriched_steps", [])
        semantic_intents = state.get("semantic_intents", [])
        print(f"\n🧠 Intent Extraction Results:")
        print(f"   Enriched steps: {len(enriched_steps)}")
        print(f"   Total intents: {len(semantic_intents)}")
        print(f"   Confidence: {state.get('intent_confidence', 0):.1%}")
        
        # Platform detection results
        platform_context = state.get("platform_context", {})
        print(f"\n🌐 Platform Detection Results:")
        print(f"   Primary platform: {platform_context.get('platform_name', 'N/A')}")
        print(f"   Confidence: {state.get('platform_confidence', 0):.1%}")
        alternatives = state.get("alternative_platforms", [])
        if alternatives:
            print(f"   Alternatives: {', '.join(alternatives[:3])}")
        
        # Element finding results
        element_strategies = state.get("element_strategies", [])
        print(f"\n🔍 Element Finding Results:")
        print(f"   Elements found: {len([s for s in element_strategies if s.get('success')])}/{len(element_strategies)}")
        print(f"   Success rate: {state.get('element_success_rate', 0):.1%}")
        
        # Error summary
        errors = state.get("errors", [])
        if errors:
            print(f"\n❌ Errors ({len(errors)}):")
            for error in errors[:5]:  # Show first 5 errors
                print(f"   {error}")
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more")
        
        # Final output
        if state.get("execution_ready"):
            script_length = len(state.get("final_script", ""))
            print(f"\n📄 Generated Script:")
            print(f"   Script length: {script_length} characters")
            print(f"   Framework: Playwright")
        else:
            print(f"\n⚠️  Script generation skipped - execution not ready")
        
        print("=" * 70)


# Test function for full workflow
async def test_full_workflow():
    """Test the complete workflow end-to-end"""
    
    print("🧪 TESTING COMPLETE HELIX AUTOMATION WORKFLOW")
    print("=" * 60)
    
    # Test cases for different scenarios
    test_cases = [
        {
            "name": "Salesforce Opportunity Creation",
            "input": """
            Test Case: Create New Salesforce Opportunity
            
            Step 1: Navigate to https://login.salesforce.com
            Step 2: Enter username: test@company.com
            Step 3: Enter password: password123
            Step 4: Click Login button
            Step 5: Click the App Launcher (9 dots)
            Step 6: Search for "Opportunities"
            Step 7: Click New Opportunity button
            Step 8: Enter Opportunity Name: "Test Opportunity Q4"
            Step 9: Select Stage: "Prospecting"
            Step 10: Enter Amount: 75000
            Step 11: Click Save button
            Step 12: Verify opportunity is created successfully
            """,
            "metadata": {"format": "plain_text", "platform_hint": "salesforce"}
        },
        {
            "name": "SAP Fiori Navigation",
            "input": """
            Feature: SAP Fiori Navigation
            Scenario: Navigate to Sales Dashboard
            Given I am on the SAP Fiori Launchpad
            When I click on the Sales tile
            And I select Dashboard option
            Then I should see the sales dashboard
            """,
            "metadata": {"format": "gherkin", "platform_hint": "sap"}
        },
        {
            "name": "Generic Web Form",
            "input": """
            1. Open the contact form page
            2. Fill in Name: John Doe
            3. Fill in Email: john@example.com
            4. Fill in Message: Test message
            5. Click Submit button
            6. Verify success message is displayed
            """,
            "metadata": {"format": "plain_text"}
        }
    ]
    
    workflow = HelixAutomationWorkflow()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 50)
        
        # Create initial state
        initial_state = create_initial_state(
            raw_input=test_case["input"],
            input_metadata=test_case["metadata"]
        )
        
        # Execute workflow
        try:
            result = await workflow.ainvoke(initial_state)
            
            # Quick summary for this test case
            print(f"\n✅ Test case {i} completed:")
            print(f"   Confidence: {result.get('confidence_score', 0):.1%}")
            print(f"   Execution ready: {result.get('execution_ready', False)}")
            print(f"   Platform detected: {result.get('platform_context', {}).get('platform_name', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Test case {i} failed: {e}")
    
    print(f"\n🎯 Full workflow testing complete!")


if __name__ == "__main__":
    asyncio.run(test_full_workflow())