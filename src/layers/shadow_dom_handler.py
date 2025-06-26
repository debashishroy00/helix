"""
Shadow DOM Handler for Helix AI Engine
=====================================
Handles elements inside shadow DOM (Lightning Components, Web Components)
"""

from typing import List, Dict, Any, Optional
from src.models.element import ElementStrategy, ElementContext, StrategyType, PerformanceTier
from src.layers.base import BaseLayer


class ShadowDOMHandler(BaseLayer):
    """
    Specialized handler for Shadow DOM elements.
    Critical for Salesforce Lightning and modern web components.
    """
    
    def __init__(self):
        super().__init__(StrategyType.STRUCTURAL_PATTERN)
        
        # Known shadow DOM patterns
        self.shadow_host_patterns = [
            # Salesforce Lightning
            "lightning-[a-z-]+",
            "force-[a-z-]+", 
            "flexipage-[a-z-]+",
            
            # Standard web components
            "[a-z]+-[a-z-]+",  # Custom elements convention
            
            # Common component libraries
            "vaadin-[a-z-]+",
            "paper-[a-z-]+",
            "iron-[a-z-]+",
            "mwc-[a-z-]+"
        ]
        
    async def generate_strategies(
        self, 
        page: Any, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate shadow DOM piercing strategies."""
        
        strategies = []
        
        # Strategy 1: Direct shadow piercing
        strategies.extend(self._generate_shadow_piercing_strategies(context))
        
        # Strategy 2: JavaScript execution strategies
        strategies.extend(self._generate_js_shadow_strategies(context))
        
        # Strategy 3: Recursive shadow search
        strategies.extend(self._generate_recursive_shadow_strategies(context))
        
        return strategies
    
    def _generate_shadow_piercing_strategies(
        self, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies that pierce through shadow DOM."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Map intent to element types
        element_type = self._infer_element_type(intent_lower)
        
        # Lightning component patterns
        if "salesforce" in context.platform or "lightning" in context.platform:
            # Standard Lightning components
            if "button" in intent_lower:
                strategies.extend([
                    ElementStrategy(
                        selector="pierce/lightning-button button",
                        confidence=0.85,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.MEDIUM,
                        reasoning="Lightning button shadow pierce",
                        metadata={"shadow_pierce": True, "depth": 1}
                    ),
                    ElementStrategy(
                        selector="pierce/lightning-button[variant='brand'] button",
                        confidence=0.80,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.MEDIUM,
                        reasoning="Lightning brand button shadow pierce",
                        metadata={"shadow_pierce": True, "depth": 1}
                    )
                ])
            
            elif "input" in intent_lower or "field" in intent_lower:
                strategies.extend([
                    ElementStrategy(
                        selector="pierce/lightning-input input",
                        confidence=0.85,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.MEDIUM,
                        reasoning="Lightning input shadow pierce",
                        metadata={"shadow_pierce": True, "depth": 1}
                    ),
                    ElementStrategy(
                        selector="pierce/lightning-input-field input",
                        confidence=0.80,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.MEDIUM,
                        reasoning="Lightning input field shadow pierce",
                        metadata={"shadow_pierce": True, "depth": 1}
                    )
                ])
        
        # Generic web component patterns
        strategies.append(
            ElementStrategy(
                selector=f"pierce/*/{element_type}",
                confidence=0.65,
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.EXPENSIVE,
                reasoning="Generic shadow DOM element search",
                metadata={"shadow_pierce": True, "depth": "any"}
            )
        )
        
        return strategies
    
    def _generate_js_shadow_strategies(
        self, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate JavaScript-based shadow DOM strategies."""
        
        strategies = []
        element_type = self._infer_element_type(context.intent.lower())
        
        # JavaScript shadow root traversal
        js_selectors = [
            # Find by element type inside any shadow root
            f"js/shadowRoot:{element_type}",
            
            # Find by text content inside shadow DOM
            f"js/shadowRoot:*[text*='{context.intent}']",
            
            # Find by common attributes
            f"js/shadowRoot:{element_type}[type='submit']" if "button" in context.intent.lower() else None,
            f"js/shadowRoot:input[type='email']" if "email" in context.intent.lower() else None,
        ]
        
        for selector in js_selectors:
            if selector:
                strategies.append(
                    ElementStrategy(
                        selector=selector,
                        confidence=0.70,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.EXPENSIVE,
                        reasoning="JavaScript shadow DOM traversal",
                        metadata={
                            "requires_js": True,
                            "shadow_traverse": True
                        }
                    )
                )
        
        return strategies
    
    def _generate_recursive_shadow_strategies(
        self, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate recursive shadow DOM search strategies."""
        
        strategies = []
        
        # Deep shadow DOM search patterns
        shadow_patterns = [
            # Multi-level shadow DOM
            "deep/*/shadow/*/shadow/*",
            
            # Component-specific patterns
            "deep/lightning-*/shadow/slot/*",
            "deep/force-*/shadow/*",
        ]
        
        element_type = self._infer_element_type(context.intent.lower())
        
        for pattern in shadow_patterns:
            strategies.append(
                ElementStrategy(
                    selector=f"{pattern}/{element_type}",
                    confidence=0.60,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.EXPENSIVE,
                    reasoning="Deep recursive shadow DOM search",
                    metadata={
                        "shadow_recursive": True,
                        "max_depth": 5
                    }
                )
            )
        
        return strategies
    
    def _infer_element_type(self, intent: str) -> str:
        """Infer element type from intent."""
        
        intent_lower = intent.lower()
        
        if any(word in intent_lower for word in ["button", "submit", "click", "save", "cancel"]):
            return "button"
        elif any(word in intent_lower for word in ["input", "field", "text", "email", "password"]):
            return "input"
        elif any(word in intent_lower for word in ["link", "navigate", "href"]):
            return "a"
        elif any(word in intent_lower for word in ["dropdown", "select", "picker"]):
            return "select"
        elif any(word in intent_lower for word in ["checkbox", "check"]):
            return "input[type='checkbox']"
        elif any(word in intent_lower for word in ["radio"]):
            return "input[type='radio']"
        else:
            return "*"  # Any element