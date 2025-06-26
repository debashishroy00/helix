"""
Simplified Structural Pattern Layer - No BeautifulSoup
======================================================
A simplified version that uses regex parsing instead of BeautifulSoup
to eliminate the dependency while maintaining core functionality.
"""

import re
from typing import List, Optional, Any, Dict
from src.models.element import ElementStrategy, ElementContext, StrategyType, PerformanceTier
from src.layers.base import BaseLayer


class StructuralPatternLayer(BaseLayer):
    """
    Simplified structural pattern layer using regex-based parsing.
    """
    
    def __init__(self):
        super().__init__(StrategyType.STRUCTURAL_PATTERN)
        
        # Common structural patterns for different platforms
        self.platform_patterns = {
            "salesforce_lightning": {
                "form_containers": [".slds-form", ".slds-form-element"],
                "button_containers": [".slds-button-group"],
                "input_containers": [".slds-form-element__control"],
            },
            "generic": {
                "form_containers": [".form", ".form-group"],
                "button_containers": [".btn-group", ".button-group"],
                "input_containers": [".form-control", ".input-group"],
            }
        }
    
    async def generate_strategies(
        self, 
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on structural patterns using regex."""
        
        strategies = []
        
        # Get HTML content
        if hasattr(page, 'content'):
            html_content = await page.content()
        else:
            html_content = context.html_content or ""
        
        if not html_content:
            return strategies
        
        # Strategy 1: Form structure analysis
        form_strategies = self._analyze_form_structure(html_content, context)
        strategies.extend(form_strategies)
        
        # Strategy 2: Platform-specific patterns
        platform_strategies = self._analyze_platform_patterns(html_content, context)
        strategies.extend(platform_strategies)
        
        return strategies
    
    def _analyze_form_structure(
        self, 
        html_content: str, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Analyze form structure using regex."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Look for form elements
        if any(keyword in intent_lower for keyword in ["input", "field", "username", "password", "email"]):
            # Pattern to find inputs within forms
            form_input_pattern = r'<form[^>]*>[\s\S]*?<input[^>]*\s+(?:id|name)=["\']([^"\']+)["\'][^>]*>[\s\S]*?</form>'
            matches = re.finditer(form_input_pattern, html_content, re.IGNORECASE)
            
            for match in matches:
                input_id_or_name = match.group(1)
                if any(keyword in input_id_or_name.lower() for keyword in intent_lower.split()):
                    strategies.append(ElementStrategy(
                        selector=f'form input[id="{input_id_or_name}"], form input[name="{input_id_or_name}"]',
                        confidence=0.75,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Input within form structure: {input_id_or_name}",
                        metadata={"method": "form_structure", "input_identifier": input_id_or_name}
                    ))
        
        return strategies
    
    def _analyze_platform_patterns(
        self, 
        html_content: str, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Analyze platform-specific patterns using regex."""
        
        strategies = []
        platform = context.platform or "generic"
        
        # Get patterns for the platform
        patterns = self.platform_patterns.get(platform, self.platform_patterns["generic"])
        
        # Check for platform-specific class patterns
        for container_type, class_patterns in patterns.items():
            for class_pattern in class_patterns:
                escaped_pattern = re.escape(class_pattern[1:])  # Remove the dot and escape
                class_regex = rf'class=["\'][^"\']*{escaped_pattern}[^"\']*["\']'
                
                if re.search(class_regex, html_content, re.IGNORECASE):
                    strategies.append(ElementStrategy(
                        selector=class_pattern,
                        confidence=0.6,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.MEDIUM,
                        reasoning=f"Platform-specific {container_type} pattern",
                        metadata={"method": "platform_pattern", "pattern_type": container_type, "platform": platform}
                    ))
        
        return strategies