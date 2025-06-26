"""
Virtual Scroll Handler for Helix AI Engine
==========================================
Handles virtual scrolling tables and lists where elements are not in DOM
"""

from typing import List, Dict, Any, Optional
from src.models.element import ElementStrategy, ElementContext, StrategyType, PerformanceTier
from src.layers.base import BaseLayer


class VirtualScrollHandler(BaseLayer):
    """
    Specialized handler for virtual scrolling elements.
    Critical for large data tables and infinite scroll lists.
    """
    
    def __init__(self):
        super().__init__(StrategyType.MUTATION_OBSERVATION)
        
        # Known virtual scrolling patterns
        self.virtual_patterns = {
            "libraries": {
                "react-window": ["react-window", "FixedSizeList", "VariableSizeList"],
                "react-virtualized": ["ReactVirtualized__Table", "ReactVirtualized__List"],
                "ag-grid": ["ag-root", "ag-body-viewport"],
                "material-table": ["MuiTable-root", "MuiTableBody-root"],
                "primereact": ["p-datatable-scrollable-body"],
                "antd": ["ant-table-body", "rc-virtual-list"]
            },
            "indicators": {
                "attributes": ["data-virtualized", "virtual-scroll", "infinite-scroll"],
                "classes": ["virtual-list", "virtual-table", "infinite-scroll-component"],
                "viewport_containers": ["viewport", "scroll-container", "virtual-scroller"]
            }
        }
        
    async def generate_strategies(
        self, 
        page: Any, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate virtual scroll handling strategies."""
        
        strategies = []
        
        # Strategy 1: Detect virtual scroll containers
        strategies.extend(self._generate_container_detection_strategies(context))
        
        # Strategy 2: Scroll-and-find strategies
        strategies.extend(self._generate_scroll_search_strategies(context))
        
        # Strategy 3: Data attribute strategies
        strategies.extend(self._generate_data_strategies(context))
        
        return strategies
    
    def _generate_container_detection_strategies(
        self, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies to detect virtual scroll containers."""
        
        strategies = []
        
        # Library-specific patterns
        for library, patterns in self.virtual_patterns["libraries"].items():
            for pattern in patterns:
                strategies.append(
                    ElementStrategy(
                        selector=f"[class*='{pattern}']",
                        confidence=0.85,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Virtual scroll container: {library}",
                        metadata={
                            "virtual_scroll": True,
                            "library": library,
                            "requires_scroll": True
                        }
                    )
                )
        
        # Generic virtual scroll indicators
        for attr in self.virtual_patterns["indicators"]["attributes"]:
            strategies.append(
                ElementStrategy(
                    selector=f"[{attr}]",
                    confidence=0.80,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning=f"Virtual scroll by attribute: {attr}",
                    metadata={
                        "virtual_scroll": True,
                        "detection_method": "attribute"
                    }
                )
            )
        
        # Viewport-based detection
        viewport_selectors = [
            "div[style*='overflow'][style*='height']",
            "div.viewport[data-total-rows]",
            "[role='grid'][aria-rowcount]"
        ]
        
        for selector in viewport_selectors:
            strategies.append(
                ElementStrategy(
                    selector=selector,
                    confidence=0.70,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning="Potential virtual scroll viewport",
                    metadata={
                        "virtual_scroll": "possible",
                        "requires_verification": True
                    }
                )
            )
        
        return strategies
    
    def _generate_scroll_search_strategies(
        self, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies that scroll to find elements."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Determine what we're looking for
        search_text = self._extract_search_text(intent_lower)
        
        # Scroll-based search strategies
        if search_text:
            strategies.extend([
                ElementStrategy(
                    selector=f"virtual-scroll:text='{search_text}'",
                    confidence=0.75,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.EXPENSIVE,
                    reasoning="Virtual scroll search by text",
                    metadata={
                        "action": "scroll_until_found",
                        "search_text": search_text,
                        "max_scrolls": 50
                    }
                ),
                ElementStrategy(
                    selector=f"virtual-scroll:contains('{search_text}')",
                    confidence=0.70,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.EXPENSIVE,
                    reasoning="Virtual scroll partial text match",
                    metadata={
                        "action": "scroll_search",
                        "partial_match": True
                    }
                )
            ])
        
        # Row/cell based strategies
        if "row" in intent_lower or "cell" in intent_lower:
            strategies.extend([
                ElementStrategy(
                    selector="virtual-scroll:row[data-row-index]",
                    confidence=0.65,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.EXPENSIVE,
                    reasoning="Virtual table row by index",
                    metadata={
                        "element_type": "table_row",
                        "scroll_strategy": "indexed"
                    }
                ),
                ElementStrategy(
                    selector="virtual-scroll:cell[data-value]",
                    confidence=0.60,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.EXPENSIVE,
                    reasoning="Virtual table cell by value",
                    metadata={
                        "element_type": "table_cell",
                        "scroll_strategy": "value_search"
                    }
                )
            ])
        
        return strategies
    
    def _generate_data_strategies(
        self, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on data attributes and patterns."""
        
        strategies = []
        
        # AG-Grid specific
        if "grid" in context.platform.lower() or "table" in context.intent.lower():
            strategies.extend([
                ElementStrategy(
                    selector="div.ag-body-viewport",
                    confidence=0.80,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning="AG-Grid virtual viewport",
                    metadata={
                        "grid_type": "ag-grid",
                        "virtual_scroll": True,
                        "api_available": "window.agGrid"
                    }
                ),
                ElementStrategy(
                    selector="[ref='eBodyViewport'] [row-id]",
                    confidence=0.75,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning="AG-Grid virtual rows",
                    metadata={
                        "requires_scroll": True
                    }
                )
            ])
        
        # React Virtual List patterns
        strategies.extend([
            ElementStrategy(
                selector="div[data-test-id='virtual-list'] > div",
                confidence=0.70,
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.MEDIUM,
                reasoning="React virtual list items",
                metadata={
                    "framework": "react",
                    "virtual_type": "list"
                }
            ),
            ElementStrategy(
                selector="[style*='transform'][style*='translateY']",
                confidence=0.65,
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.MEDIUM,
                reasoning="Transformed virtual elements",
                metadata={
                    "detection": "css_transform",
                    "virtual_positioning": True
                }
            )
        ])
        
        # Infinite scroll patterns
        strategies.append(
            ElementStrategy(
                selector="div.infinite-scroll-component__outerdiv",
                confidence=0.75,
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.MEDIUM,
                reasoning="Infinite scroll container",
                metadata={
                    "scroll_type": "infinite",
                    "load_more_required": True
                }
            )
        )
        
        return strategies
    
    def _extract_search_text(self, intent: str) -> Optional[str]:
        """Extract search text from intent."""
        
        # Common patterns for finding specific data
        patterns = [
            r"containing ['\"](.*?)['\"]",
            r"with text ['\"](.*?)['\"]",
            r"row with (.*)",
            r"find (.*) in table",
            r"locate (.*)"
        ]
        
        import re
        for pattern in patterns:
            match = re.search(pattern, intent, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # If no pattern matches, see if intent contains specific data
        if len(intent.split()) <= 5:  # Short intents might be direct search
            return intent
        
        return None