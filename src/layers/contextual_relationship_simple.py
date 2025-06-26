"""
Simplified Contextual Relationship Layer - No Dependencies
==========================================================
A simplified version that removes external dependencies while
maintaining core functionality for element relationship analysis.
"""

import re
from typing import List, Optional, Any, Dict
from src.models.element import ElementStrategy, ElementContext, StrategyType, PerformanceTier
from src.layers.base import BaseLayer


class ContextualRelationshipLayer(BaseLayer):
    """
    Simplified contextual relationship layer without external dependencies.
    """
    
    def __init__(self):
        super().__init__(StrategyType.CONTEXTUAL_RELATIONSHIP)
        
        # Common contextual patterns
        self.context_patterns = {
            "form_field_relationships": [
                ("label", "input"),
                ("fieldset", "input"),
                ("legend", "input")
            ],
            "navigation_relationships": [
                ("nav", "a"),
                ("menu", "a"),
                ("header", "button")
            ],
            "action_relationships": [
                ("form", "button"),
                ("dialog", "button"),
                ("modal", "button")
            ]
        }
    
    async def generate_strategies(
        self, 
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on contextual relationships using regex."""
        
        strategies = []
        
        # Get HTML content
        if hasattr(page, 'content'):
            html_content = await page.content()
        else:
            html_content = context.html_content or ""
        
        if not html_content:
            return strategies
        
        # Strategy 1: Label-field relationships
        label_strategies = self._analyze_label_relationships(html_content, context)
        strategies.extend(label_strategies)
        
        # Strategy 2: Form context relationships
        form_strategies = self._analyze_form_relationships(html_content, context)
        strategies.extend(form_strategies)
        
        return strategies
    
    def _analyze_label_relationships(
        self, 
        html_content: str, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Analyze label-field relationships using regex."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Look for labels that might relate to our intent
        intent_keywords = intent_lower.split()
        
        for keyword in intent_keywords:
            if len(keyword) > 2:  # Skip very short words
                # Pattern to find labels containing the keyword that reference inputs
                label_for_pattern = rf'<label[^>]*for=["\']([^"\']+)["\'][^>]*>[^<]*{re.escape(keyword)}[^<]*</label>'
                matches = re.finditer(label_for_pattern, html_content, re.IGNORECASE)
                
                for match in matches:
                    target_id = match.group(1)
                    strategies.append(ElementStrategy(
                        selector=f'#{target_id}',
                        confidence=0.85,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Input referenced by label containing '{keyword}'",
                        metadata={"method": "label_for", "keyword": keyword, "target_id": target_id}
                    ))
        
        return strategies
    
    def _analyze_form_relationships(
        self, 
        html_content: str, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Analyze form context relationships using regex."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Look for form elements that might be relevant
        if any(keyword in intent_lower for keyword in ["submit", "save", "button", "send"]):
            # Pattern to find submit buttons within forms
            form_submit_pattern = r'<form[^>]*>[\s\S]*?<(button|input)[^>]*type=["\']submit["\'][^>]*>[\s\S]*?</form>'
            matches = re.finditer(form_submit_pattern, html_content, re.IGNORECASE)
            
            if matches:
                strategies.append(ElementStrategy(
                    selector='form button[type="submit"], form input[type="submit"]',
                    confidence=0.8,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning="Submit button within form context",
                    metadata={"method": "form_submit", "context": "form"}
                ))
        
        return strategies