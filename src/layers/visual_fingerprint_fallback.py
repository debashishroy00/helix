"""
Layer 3: Visual Fingerprinting (Fallback Version)
=================================================

Fallback version of visual fingerprinting layer that works without cv2/PIL.
This provides basic visual strategies without computer vision dependencies.
"""

import asyncio
from typing import List, Dict, Any
from src.layers.base import BaseLayer
from src.models.element import ElementStrategy, ElementContext, StrategyType


class VisualFingerprintLayer(BaseLayer):
    """
    Layer 3: Visual fingerprinting fallback without CV dependencies.
    """
    
    def __init__(self):
        super().__init__(StrategyType.VISUAL_FINGERPRINT)
    
    async def generate_strategies(
        self, 
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """
        Generate basic visual strategies without computer vision.
        """
        strategies = []
        
        # Add a basic strategy indicating visual processing is unavailable
        strategies.append(ElementStrategy(
            selector="/* Visual processing unavailable - install cv2/PIL for full capabilities */",
            confidence=0.05,
            strategy_type=self.strategy_type,
            performance_tier="expensive",
            reasoning="Visual dependencies not available - basic fallback strategy"
        ))
        
        # Add some basic visual-intent based selectors
        intent_lower = context.intent.lower()
        
        if "button" in intent_lower:
            strategies.extend([
                ElementStrategy(
                    selector="button[class*='btn']",
                    confidence=0.3,
                    strategy_type=self.strategy_type,
                    performance_tier="fast",
                    reasoning="Button class pattern matching"
                ),
                ElementStrategy(
                    selector="input[type='button']",
                    confidence=0.25,
                    strategy_type=self.strategy_type,
                    performance_tier="fast",
                    reasoning="Button input type"
                )
            ])
        
        if "image" in intent_lower or "icon" in intent_lower:
            strategies.extend([
                ElementStrategy(
                    selector="img",
                    confidence=0.3,
                    strategy_type=self.strategy_type,
                    performance_tier="fast",
                    reasoning="Image element"
                ),
                ElementStrategy(
                    selector="[class*='icon']",
                    confidence=0.25,
                    strategy_type=self.strategy_type,
                    performance_tier="fast",
                    reasoning="Icon class pattern"
                )
            ])
        
        if "text" in intent_lower or "label" in intent_lower:
            strategies.extend([
                ElementStrategy(
                    selector="span, label, p",
                    confidence=0.2,
                    strategy_type=self.strategy_type,
                    performance_tier="fast",
                    reasoning="Text element types"
                )
            ])
        
        return strategies