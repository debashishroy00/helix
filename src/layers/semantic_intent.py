"""
Layer 1: Semantic Intent Recognition
====================================

This layer uses GPT-4 to understand the natural language intent and generate
multiple possible selectors based on semantic understanding.

Patent Justification:
- Handles dynamic IDs/classes by understanding WHAT the element does
- Works when traditional selectors change but functionality remains
- Provides human-like understanding of UI elements

Example:
    Intent: "submit button"
    Generates: button[type="submit"], .submit-btn, #submitForm, etc.
"""

import os
from typing import List, Dict, Any, Optional
import json
import re
from openai import AsyncOpenAI

from src.layers.base import BaseLayer
from src.models.element import ElementStrategy, ElementContext, StrategyType


class SemanticIntentLayer(BaseLayer):
    """
    Layer 1: Uses AI to understand intent and generate semantic selectors.
    
    This is the first layer because it provides the most human-like
    understanding of what we're looking for.
    """
    
    def __init__(self):
        super().__init__(StrategyType.SEMANTIC_INTENT)
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Model selection based on complexity
        self.use_fast_model = os.getenv("USE_GPT_35_TURBO", "true").lower() == "true"
        self.fast_model = "gpt-3.5-turbo-1106"  # 10x faster, cheaper
        self.accurate_model = "gpt-4-turbo-preview"  # More accurate
        
        # Patterns that require GPT-4's advanced reasoning
        self.complex_patterns = [
            "complex", "nested", "multiple", "conditional",
            "dynamic", "context-aware", "state-dependent",
            "workflow", "multi-step", "advanced"
        ]
        
        # Platform-specific patterns learned over time
        self.platform_hints = {
            "salesforce_lightning": {
                "button": ["lightning-button", "slds-button"],
                "input": ["lightning-input", "slds-input"],
                "modal": ["slds-modal", "lightning-modal"]
            },
            "sap_fiori": {
                "button": ["sapMBtn", "sapUiBtn"],
                "input": ["sapMInput", "sapUiInput"],
                "table": ["sapMTable", "sapUiTable"]
            },
            "workday": {
                "button": ["css-", "wd-", "WDFF"],
                "input": ["gwt-", "WDFF-"]
            }
        }
    
    async def generate_strategies(
        self, 
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """
        Use GPT-4 to understand intent and generate multiple selector strategies.
        """
        # Build the prompt with context
        prompt = self._build_prompt(context)
        
        try:
            # Select model based on complexity and user preference
            model = self._select_model(context)
            
            # Call GPT for semantic understanding
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(model)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=500
            )
            
            # Parse the response
            content = response.choices[0].message.content
            strategies = self._parse_gpt_response(content, context)
            
            return strategies
            
        except Exception as e:
            print(f"Semantic layer error: {str(e)}")
            # Fallback to basic pattern matching
            return self._fallback_strategies(context)
    
    def _build_prompt(self, context: ElementContext) -> str:
        """Build a detailed prompt for GPT-4."""
        platform_hint = ""
        if context.platform.value in self.platform_hints:
            hints = self.platform_hints[context.platform.value]
            platform_hint = f"\nPlatform-specific hints: {json.dumps(hints)}"
        
        return f"""Given the following context, generate CSS selectors and XPath expressions
to find a UI element:

Intent: {context.intent}
Platform: {context.platform.value}
Page Type: {context.page_type}
{platform_hint}

Generate 5-7 different selectors that could match this element, ordered by likelihood.
Consider:
1. Semantic HTML (button, input, a, etc.)
2. ARIA attributes (role, aria-label, etc.)
3. Common class patterns for this platform
4. Text content or placeholders
5. Form associations (labels, etc.)

Format each selector as:
SELECTOR: <css or xpath>
CONFIDENCE: <0.0-1.0>
REASON: <why this might work>

Focus on selectors that would remain stable even if IDs/classes change."""
    
    def _get_system_prompt(self, model: str) -> str:
        """System prompt to guide GPT behavior based on model capability."""
        base_prompt = """You are an expert at identifying UI elements across different platforms.
You understand how different frameworks (Salesforce Lightning, SAP UI5, etc.) structure their DOM.
Generate multiple strategies for finding elements, focusing on semantic meaning over brittle selectors.
Always prefer selectors that understand WHAT the element does rather than HOW it's styled."""
        
        # Adjust complexity based on model
        if "gpt-4" in model:
            return base_prompt + """
Use advanced reasoning to understand complex element relationships and state-dependent selectors.
Consider user permissions, workflow states, and dynamic content."""
        else:
            # GPT-3.5-turbo - keep it simple and fast
            return base_prompt + """
Focus on simple, reliable patterns. Prefer common HTML attributes and standard CSS selectors.
Avoid overly complex logic - prioritize speed and common patterns."""
    
    def _parse_gpt_response(self, content: str, context: ElementContext) -> List[ElementStrategy]:
        """Parse GPT-4's response into strategy objects."""
        strategies = []
        
        # Parse numbered sections (GPT-4's actual format)
        sections = re.split(r'\n\d+\.\s*', content)
        
        for section in sections[1:]:  # Skip first empty split
            try:
                # Extract SELECTOR (handles css: and xpath: prefixes)
                selector_match = re.search(r'SELECTOR:\s*(?:css:|xpath:)?\s*`?([^`\n]+)`?', section)
                if not selector_match:
                    continue
                
                selector = selector_match.group(1).strip()
                
                # Extract CONFIDENCE
                confidence_match = re.search(r'CONFIDENCE:\s*(\d*\.?\d+)', section)
                confidence = float(confidence_match.group(1)) if confidence_match else 0.8
                
                # Extract REASON
                reason_match = re.search(r'REASON:\s*(.+?)(?=\n\d+\.|$)', section, re.DOTALL)
                reason = reason_match.group(1).strip() if reason_match else "GPT-4 generated strategy"
                reason = ' '.join(reason.split())  # Clean up whitespace
                
                # Handle multiple selectors separated by commas
                selector_candidates = []
                if ',' in selector and not ('(' in selector and ')' in selector):
                    # Simple comma split if no complex selectors
                    selector_candidates = [s.strip() for s in selector.split(',')]
                else:
                    # Single selector or complex selector with commas
                    selector_candidates = [selector.strip()]
                
                # Create strategy for each selector
                for sel in selector_candidates:
                    # Remove extra quotes/backticks
                    sel = sel.replace('`', '').strip()
                    
                    # Validate selector syntax
                    if self._is_valid_selector(sel):
                        strategy = ElementStrategy(
                            strategy_type=self.layer_type,
                            selector=sel,
                            confidence=min(confidence, 0.95),  # Cap at 0.95 for semantic
                            metadata={
                                "reason": reason,
                                "platform": context.platform.value,
                                "gpt_generated": True
                            }
                        )
                        strategies.append(strategy)
                        
            except Exception as e:
                # Continue parsing other sections if one fails
                continue
        
        # If no valid strategies from GPT, use fallback
        if not strategies:
            strategies = self._fallback_strategies(context)
        
        return strategies
    
    def _is_valid_selector(self, selector: str) -> bool:
        """Basic validation of CSS/XPath selector syntax."""
        if selector.startswith("//") or selector.startswith(".//"):
            # XPath
            return "/" in selector and len(selector) > 3
        else:
            # CSS
            return len(selector) > 1 and not selector.isspace()
    
    def _fallback_strategies(self, context: ElementContext) -> List[ElementStrategy]:
        """Generate basic strategies when GPT-4 fails."""
        strategies = []
        intent_lower = context.intent.lower()
        
        # Common patterns based on intent
        if "button" in intent_lower or "submit" in intent_lower:
            strategies.extend([
                ElementStrategy(
                    strategy_type=self.layer_type,
                    selector='button[type="submit"]',
                    confidence=0.7,
                    metadata={"reason": "Standard submit button", "fallback": True}
                ),
                ElementStrategy(
                    strategy_type=self.layer_type,
                    selector='input[type="submit"]',
                    confidence=0.6,
                    metadata={"reason": "Input submit element", "fallback": True}
                ),
                ElementStrategy(
                    strategy_type=self.layer_type,
                    selector='button:contains("Submit")',
                    confidence=0.5,
                    metadata={"reason": "Button with Submit text", "fallback": True}
                )
            ])
        
        elif "search" in intent_lower:
            strategies.extend([
                ElementStrategy(
                    strategy_type=self.layer_type,
                    selector='input[type="search"]',
                    confidence=0.8,
                    metadata={"reason": "Search input field", "fallback": True}
                ),
                ElementStrategy(
                    strategy_type=self.layer_type,
                    selector='input[placeholder*="search" i]',
                    confidence=0.7,
                    metadata={"reason": "Input with search placeholder", "fallback": True}
                )
            ])
        
        elif "login" in intent_lower or "sign in" in intent_lower:
            strategies.extend([
                ElementStrategy(
                    strategy_type=self.layer_type,
                    selector='button:contains("Login"), button:contains("Sign In")',
                    confidence=0.8,
                    metadata={"reason": "Login/Sign In button", "fallback": True}
                ),
                ElementStrategy(
                    strategy_type=self.layer_type,
                    selector='input[type="submit"][value*="Login" i]',
                    confidence=0.6,
                    metadata={"reason": "Login submit input", "fallback": True}
                )
            ])
        
        # Generic fallback based on element type keywords
        element_types = ["button", "input", "link", "dropdown", "checkbox", "radio"]
        for elem_type in element_types:
            if elem_type in intent_lower:
                strategies.append(
                    ElementStrategy(
                        strategy_type=self.layer_type,
                        selector=elem_type if elem_type != "link" else "a",
                        confidence=0.4,
                        metadata={"reason": f"Generic {elem_type} element", "fallback": True}
                    )
                )
                break
        
        return strategies
    
    def _select_model(self, context: ElementContext) -> str:
        """
        Select the appropriate GPT model based on complexity and preferences.
        
        GPT-3.5-turbo: 10x faster, 10x cheaper, good for simple patterns
        GPT-4: More accurate for complex patterns
        """
        # Always use fast model if configured
        if not self.use_fast_model:
            return self.accurate_model
        
        # Check if intent indicates complexity requiring GPT-4
        intent_lower = context.intent.lower()
        
        # Use GPT-4 for complex patterns
        if any(pattern in intent_lower for pattern in self.complex_patterns):
            print(f"Using GPT-4 for complex pattern: {context.intent}")
            return self.accurate_model
        
        # Use GPT-4 for complex platforms with unusual patterns
        if context.platform.value in ["workday", "oracle_cloud"] and len(intent_lower.split()) > 5:
            return self.accurate_model
        
        # Default to fast model for simple patterns
        print(f"Using GPT-3.5-turbo for simple pattern: {context.intent}")
        return self.fast_model