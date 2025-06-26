"""
Canvas Element Handler for Helix AI Engine
==========================================
Handles canvas-based UI elements (signature pads, charts, drawing areas)
"""

from typing import List, Dict, Any, Optional
from src.models.element import ElementStrategy, ElementContext, StrategyType, PerformanceTier
from src.layers.base import BaseLayer


class CanvasHandler(BaseLayer):
    """
    Specialized handler for canvas elements.
    Critical for signature pads, charts, and custom drawing interfaces.
    """
    
    def __init__(self):
        super().__init__(StrategyType.VISUAL_FINGERPRINT)
        
        # Common canvas patterns
        self.canvas_patterns = {
            "signature": {
                "identifiers": ["signature", "sign", "autograph", "handwriting"],
                "common_sizes": [(400, 200), (500, 250), (600, 150)],
                "typical_ids": ["signature-pad", "signaturePad", "sig-canvas"]
            },
            "chart": {
                "identifiers": ["chart", "graph", "plot", "visualization"],
                "libraries": ["chartjs", "d3", "highcharts", "echarts"],
                "typical_classes": ["chart-container", "graph-canvas"]
            },
            "drawing": {
                "identifiers": ["draw", "paint", "sketch", "canvas-draw"],
                "typical_attributes": ["drawable", "drawing-board"]
            }
        }
        
    async def generate_strategies(
        self, 
        page: Any, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate canvas-specific strategies."""
        
        strategies = []
        
        # Strategy 1: Direct canvas identification
        strategies.extend(self._generate_canvas_identification_strategies(context))
        
        # Strategy 2: Canvas interaction strategies
        strategies.extend(self._generate_canvas_interaction_strategies(context))
        
        # Strategy 3: Canvas context strategies
        strategies.extend(self._generate_canvas_context_strategies(context))
        
        return strategies
    
    def _generate_canvas_identification_strategies(
        self, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies to identify canvas elements."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Determine canvas type from intent
        canvas_type = self._infer_canvas_type(intent_lower)
        
        # Canvas by ID patterns
        if canvas_type == "signature":
            for canvas_id in self.canvas_patterns["signature"]["typical_ids"]:
                strategies.append(
                    ElementStrategy(
                        selector=f"canvas#{canvas_id}",
                        confidence=0.85,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Common signature canvas ID: {canvas_id}",
                        metadata={
                            "element_type": "canvas",
                            "canvas_type": "signature",
                            "interaction_type": "draw"
                        }
                    )
                )
        
        # Canvas by semantic attributes
        for identifier in self.canvas_patterns.get(canvas_type, {}).get("identifiers", []):
            strategies.extend([
                ElementStrategy(
                    selector=f"canvas[id*='{identifier}' i]",
                    confidence=0.75,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning=f"Canvas with {identifier} in ID",
                    metadata={"canvas_type": canvas_type}
                ),
                ElementStrategy(
                    selector=f"canvas[class*='{identifier}' i]",
                    confidence=0.70,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning=f"Canvas with {identifier} in class",
                    metadata={"canvas_type": canvas_type}
                ),
                ElementStrategy(
                    selector=f"canvas[data-purpose*='{identifier}' i]",
                    confidence=0.80,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning=f"Canvas with {identifier} purpose",
                    metadata={"canvas_type": canvas_type}
                )
            ])
        
        # Generic canvas fallback
        strategies.append(
            ElementStrategy(
                selector="canvas:visible",
                confidence=0.50,
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.FAST,
                reasoning="Any visible canvas element",
                metadata={
                    "canvas_type": "unknown",
                    "requires_context": True
                }
            )
        )
        
        return strategies
    
    def _generate_canvas_interaction_strategies(
        self, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies for interacting with canvas elements."""
        
        strategies = []
        canvas_type = self._infer_canvas_type(context.intent.lower())
        
        # Interaction-based strategies
        if canvas_type == "signature":
            strategies.append(
                ElementStrategy(
                    selector="canvas[interactive='signature']",
                    confidence=0.90,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning="Interactive signature canvas",
                    metadata={
                        "interaction": {
                            "type": "draw",
                            "method": "mouse/touch",
                            "clear_button": "look_nearby"
                        }
                    }
                )
            )
            
            # Look for associated controls
            strategies.append(
                ElementStrategy(
                    selector="canvas:near(button:contains('Clear'))",
                    confidence=0.75,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning="Canvas near clear button (likely signature)",
                    metadata={
                        "canvas_type": "signature",
                        "has_controls": True
                    }
                )
            )
        
        elif canvas_type == "chart":
            strategies.append(
                ElementStrategy(
                    selector="canvas[role='img'][aria-label*='chart' i]",
                    confidence=0.80,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning="Accessible chart canvas",
                    metadata={
                        "canvas_type": "chart",
                        "interaction": "view_only"
                    }
                )
            )
        
        return strategies
    
    def _generate_canvas_context_strategies(
        self, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on canvas context and surroundings."""
        
        strategies = []
        
        # Container-based identification
        container_patterns = [
            ("signature", "div.signature-container canvas"),
            ("signature", "div.signature-wrapper canvas"),
            ("signature", "form canvas[required]"),
            ("chart", "div.chart-wrapper canvas"),
            ("chart", "figure canvas"),
            ("drawing", "div.drawing-area canvas")
        ]
        
        canvas_type = self._infer_canvas_type(context.intent.lower())
        
        for pattern_type, selector in container_patterns:
            if pattern_type == canvas_type or canvas_type == "unknown":
                strategies.append(
                    ElementStrategy(
                        selector=selector,
                        confidence=0.65,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.MEDIUM,
                        reasoning=f"Canvas in {pattern_type} container",
                        metadata={
                            "canvas_type": pattern_type,
                            "container_based": True
                        }
                    )
                )
        
        # Size-based identification for signatures
        if canvas_type == "signature":
            for width, height in self.canvas_patterns["signature"]["common_sizes"]:
                strategies.append(
                    ElementStrategy(
                        selector=f"canvas[width='{width}'][height='{height}']",
                        confidence=0.60,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Canvas with signature dimensions {width}x{height}",
                        metadata={
                            "canvas_type": "signature",
                            "size_based": True
                        }
                    )
                )
        
        return strategies
    
    def _infer_canvas_type(self, intent: str) -> str:
        """Infer canvas type from intent."""
        
        intent_lower = intent.lower()
        
        # Check each pattern type
        for canvas_type, patterns in self.canvas_patterns.items():
            for identifier in patterns["identifiers"]:
                if identifier in intent_lower:
                    return canvas_type
        
        # Additional intent mappings
        if any(word in intent_lower for word in ["draw", "write", "sign"]):
            return "signature"
        elif any(word in intent_lower for word in ["graph", "data", "visualization"]):
            return "chart"
        elif any(word in intent_lower for word in ["paint", "sketch"]):
            return "drawing"
        
        return "unknown"