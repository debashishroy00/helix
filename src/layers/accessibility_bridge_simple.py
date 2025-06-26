"""
Simplified Accessibility Bridge Layer - No BeautifulSoup
========================================================
A simplified version that uses regex parsing instead of BeautifulSoup
to eliminate the dependency while maintaining core functionality.
"""

import re
from typing import List, Optional, Any, Dict
from src.models.element import ElementStrategy, ElementContext, StrategyType, PerformanceTier
from src.layers.base import BaseLayer


class AccessibilityBridgeLayer(BaseLayer):
    """
    Simplified accessibility bridge layer using regex-based parsing.
    """
    
    def __init__(self):
        super().__init__(StrategyType.ACCESSIBILITY_BRIDGE)
        
        # ARIA role mappings to common intents
        self.aria_role_mappings = {
            "button": ["button", "submit", "save", "cancel", "confirm", "apply", "login", "signin"],
            "textbox": ["input", "field", "username", "email", "password", "search", "text"],
            "searchbox": ["search", "find", "query", "filter"],
            "combobox": ["dropdown", "select", "combo", "picker"],
            "menu": ["menu", "navigation", "nav"],
            "link": ["link", "url", "href", "navigate"],
        }
    
    async def generate_strategies(
        self, 
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on accessibility attributes using regex."""
        
        strategies = []
        
        # Get HTML content
        if hasattr(page, 'content'):
            html_content = await page.content()
        else:
            html_content = context.html_content or ""
        
        if not html_content:
            return strategies
        
        # Strategy 1: ARIA role-based selection
        role_strategies = self._generate_aria_role_strategies(html_content, context)
        strategies.extend(role_strategies)
        
        # Strategy 2: ARIA label strategies
        label_strategies = self._generate_aria_label_strategies(html_content, context)
        strategies.extend(label_strategies)
        
        return strategies
    
    def _generate_aria_role_strategies(
        self, 
        html_content: str, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on ARIA roles using regex."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Find the most relevant ARIA role for the intent
        relevant_roles = []
        for role, keywords in self.aria_role_mappings.items():
            if any(keyword in intent_lower for keyword in keywords):
                relevant_roles.append(role)
        
        # Generate strategies for each relevant role
        for role in relevant_roles:
            # Check if elements with this role exist in HTML
            role_pattern = rf'role=["\']?{re.escape(role)}["\']?'
            if re.search(role_pattern, html_content, re.IGNORECASE):
                confidence = 0.85 if role in ["button", "textbox", "searchbox"] else 0.75
                
                strategies.append(ElementStrategy(
                    selector=f"[role='{role}']",
                    confidence=confidence,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.INSTANT,
                    reasoning=f"Element with ARIA role '{role}'",
                    metadata={"method": "aria_role", "role": role}
                ))
        
        return strategies
    
    def _generate_aria_label_strategies(
        self, 
        html_content: str, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on ARIA labels using regex."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Common intent keywords
        intent_keywords = intent_lower.split()
        
        for keyword in intent_keywords:
            if len(keyword) > 2:  # Skip very short words
                # Check for aria-label containing the keyword
                label_pattern = rf'aria-label=["\'][^"\']*{re.escape(keyword)}[^"\']*["\']'
                if re.search(label_pattern, html_content, re.IGNORECASE):
                    strategies.append(ElementStrategy(
                        selector=f'[aria-label*="{keyword}" i]',
                        confidence=0.8,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"ARIA label contains '{keyword}'",
                        metadata={"method": "aria_label", "keyword": keyword}
                    ))
        
        return strategies