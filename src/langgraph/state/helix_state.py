"""
Helix Automation: LangGraph State Definition
Phase 1: Minimal LangGraph Integration
"""

from typing_extensions import TypedDict
from typing import List, Dict, Any, Optional

class HelixAutomationState(TypedDict):
    """
    LangGraph State Schema for Helix Automation Platform
    Phase 1: Minimal state for basic workflow
    """
    
    # Input Stage
    raw_input: str  # Manual test case in any format
    input_metadata: Dict[str, Any]  # File type, source, etc.
    
    # Parsing Stage (Future Agent 1)
    parsed_test_case: Optional[Dict[str, Any]]
    parsing_confidence: float
    parsing_errors: List[str]
    
    # Intent Extraction Stage (Future Agent 2) 
    enriched_steps: List[Dict[str, Any]]
    semantic_intents: List[Dict[str, Any]]
    intent_confidence: float
    
    # Platform Detection Stage (Future Agent 3)
    platform_context: Optional[Dict[str, Any]]
    platform_confidence: float
    alternative_platforms: List[str]
    
    # Element Finding Stage (Agent 4 - Existing Helix Engine)
    element_strategies: List[Dict[str, Any]]
    element_success_rate: float
    failed_elements: List[Dict[str, Any]]
    
    # Action Orchestration Stage (Future Agent 5)
    automation_steps: List[Dict[str, Any]]
    framework_selection: str
    
    # Script Generation Stage (Future Agent 6)
    generated_script: Optional[str]
    script_metadata: Dict[str, Any]
    
    # Validation Stage (Future Agent 7)
    validation_results: Dict[str, Any]
    optimization_suggestions: List[Dict[str, Any]]
    
    # Self-Healing Stage (Future Agent 8)
    healing_attempts: int
    healing_success: bool
    healing_log: List[Dict[str, Any]]
    
    # Final Output
    final_script: Optional[str]
    execution_ready: bool
    confidence_score: float
    
    # System State
    current_agent: str
    retry_count: int
    max_retries: int
    errors: List[str]
    performance_metrics: Dict[str, Any]


# Default state initialization for Phase 1
def create_initial_state(raw_input: str, input_metadata: Dict[str, Any] = None) -> HelixAutomationState:
    """Create initial state for LangGraph workflow"""
    
    return HelixAutomationState(
        # Input
        raw_input=raw_input,
        input_metadata=input_metadata or {},
        
        # Processing states - defaults
        parsed_test_case=None,
        parsing_confidence=0.0,
        parsing_errors=[],
        
        enriched_steps=[],
        semantic_intents=[],
        intent_confidence=0.0,
        
        platform_context=None,
        platform_confidence=0.0,
        alternative_platforms=[],
        
        element_strategies=[],
        element_success_rate=0.0,
        failed_elements=[],
        
        automation_steps=[],
        framework_selection="",
        
        generated_script=None,
        script_metadata={},
        
        validation_results={},
        optimization_suggestions=[],
        
        healing_attempts=0,
        healing_success=False,
        healing_log=[],
        
        # Final output
        final_script=None,
        execution_ready=False,
        confidence_score=0.0,
        
        # System state
        current_agent="",
        retry_count=0,
        max_retries=3,
        errors=[],
        performance_metrics={}
    )