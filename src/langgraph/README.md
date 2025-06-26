# Helix Automation LangGraph Integration

This directory contains the LangGraph-powered multi-agent system for universal test automation.

## Directory Structure

```
src/langgraph/
├── agents/                    # Individual AI agents
│   ├── agent_1_parser/       # Parses manual test cases (Excel, Word, Gherkin, Plain text)
│   ├── agent_2_intent/       # Extracts semantic intents using NLP
│   ├── agent_3_platform/     # Detects target platform (Salesforce, SAP, etc.)
│   ├── agent_4_helix/        # Existing Helix Engine integration
│   ├── agent_5_orchestrator/ # Orchestrates automation actions
│   ├── agent_6_generator/    # Generates test scripts (Playwright, Selenium, etc.)
│   ├── agent_7_validator/    # Validates and optimizes generated scripts
│   └── agent_8_healing/      # Self-healing for failed element finding
│
├── workflows/                 # LangGraph workflow definitions
│   ├── minimal_workflow.py   # Phase 1 minimal integration
│   └── full_workflow.py      # Complete 8-agent workflow (coming soon)
│
├── state/                    # State management
│   └── helix_state.py       # Shared state schema for all agents
│
└── utils/                   # Utility functions and helpers
```

## Agent Overview

### Agent 1: Test Case Parser
- **Input**: Manual test cases in various formats (Excel, Word, Gherkin, Plain text)
- **Output**: Structured test case with steps, actions, and test data
- **Confidence**: Parsing confidence score

### Agent 2: Intent Extractor
- **Input**: Parsed test case from Agent 1
- **Output**: Enriched steps with semantic intents
- **Technology**: Transformers, spaCy, sentence-transformers

### Agent 3: Platform Detector
- **Input**: Enriched steps from Agent 2
- **Output**: Target platform context (Salesforce, SAP, Workday, etc.)
- **Confidence**: Platform detection confidence with alternatives

### Agent 4: Helix Element Finder
- **Input**: Enriched steps and platform context
- **Output**: Element finding strategies using 10-layer Helix Engine
- **Integration**: Wraps existing Helix API

### Agent 5: Action Orchestrator
- **Input**: Element strategies from Agent 4
- **Output**: Orchestrated automation steps
- **Framework**: Selects appropriate automation framework

### Agent 6: Script Generator
- **Input**: Orchestrated actions from Agent 5
- **Output**: Generated test script (Playwright, Selenium, etc.)
- **Templates**: Framework-specific code generation

### Agent 7: Script Validator
- **Input**: Generated script from Agent 6
- **Output**: Validation results and optimization suggestions
- **Checks**: Syntax, logic, best practices

### Agent 8: Self-Healing Monitor
- **Input**: Failed elements from Agent 4
- **Output**: Alternative strategies and healing attempts
- **Recovery**: Retry logic with different approaches

## Workflow Execution

The agents are connected through LangGraph's conditional workflow system:

1. **Linear Flow**: Agent 1 → 2 → 3 → 4
2. **Conditional**: If Agent 4 success < 95%, trigger Agent 8 (Self-Healing)
3. **Continue**: Agent 5 → 6 → 7
4. **Validation Loop**: Agent 7 can trigger regeneration if needed

## State Management

All agents share a common state defined in `state/helix_state.py`:
- Input data and metadata
- Processing results from each agent
- Confidence scores and error tracking
- Performance metrics
- Final output and execution readiness

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements-langgraph.txt
   ```

2. Run minimal workflow:
   ```python
   from src.langgraph.workflows.minimal_workflow import MinimalHelixWorkflow
   from src.langgraph.state.helix_state import create_initial_state
   
   workflow = MinimalHelixWorkflow()
   state = create_initial_state("Click login button on Salesforce")
   result = await workflow.ainvoke(state)
   ```

## Development Status

- ✅ Phase 1: Minimal integration with Agent 4 (Complete)
- 🔄 Phase 2: Implementing Agents 1, 2, 3 (In Progress)
- ⏳ Phase 3: Conditional logic and self-healing
- ⏳ Phase 4: Script generation pipeline
- ⏳ Phase 5: Production features