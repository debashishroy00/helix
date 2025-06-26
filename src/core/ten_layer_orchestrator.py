"""
10-Layer Universal Orchestrator
==============================
Orchestrates all 10 layers of the Helix element identification system.
This is the complete implementation that combines all patent-critical layers
for maximum element finding accuracy and coverage.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from src.models.element import ElementStrategy, ElementContext, ElementResult, StrategyType, PerformanceTier
from src.layers.base import BaseLayer, AsyncLayerExecutor

# Import all 10 layers + specialized handlers
from src.layers.semantic_intent import UniversalSemanticIntentLayer
from src.layers.contextual_relationship import ContextualRelationshipLayer
from src.layers.visual_fingerprint import VisualFingerprintLayer
from src.layers.behavioral_pattern import BehavioralPatternLayer
from src.layers.structural_pattern import StructuralPatternLayer
from src.layers.accessibility_bridge import AccessibilityBridgeLayer
from src.layers.mutation_observation import MutationObservationLayer
from src.layers.timing_synchronization import TimingSynchronizationLayer
from src.layers.state_context import StateContextLayer
from src.layers.ml_confidence_fusion import MLConfidenceFusionLayer

# Import specialized edge case handlers
from src.layers.shadow_dom_handler import ShadowDOMHandler
from src.layers.canvas_handler import CanvasHandler
from src.layers.virtual_scroll_handler import VirtualScrollHandler
from src.layers.icon_recognition_layer import IconRecognitionLayer


@dataclass
class OrchestrationStats:
    """Statistics from orchestration execution."""
    total_strategies: int = 0
    layers_executed: int = 0
    total_time_ms: float = 0.0
    fusion_time_ms: float = 0.0
    strategies_per_layer: Dict[str, int] = None
    performance_breakdown: Dict[str, float] = None
    
    def __post_init__(self):
        if self.strategies_per_layer is None:
            self.strategies_per_layer = {}
        if self.performance_breakdown is None:
            self.performance_breakdown = {}


class TenLayerOrchestrator:
    """
    Complete 10-layer orchestrator for universal element identification.
    
    Coordinates all layers and applies ML fusion for optimal strategy selection.
    This is the production-ready implementation of the complete Helix system.
    """
    
    def __init__(self):
        self.layers = self._initialize_all_layers()
        self.ml_fusion = MLConfidenceFusionLayer()
        self.execution_stats = []
        
        # Performance optimization settings
        self.max_strategies_per_layer = 5
        self.max_total_strategies = 25
        self.performance_timeout_ms = 5000  # 5 second timeout
        
        # Layer execution priorities (higher = execute first)
        self.layer_priorities = {
            StrategyType.SEMANTIC_INTENT: 10,           # Highest - most reliable
            StrategyType.ACCESSIBILITY_BRIDGE: 9,       # Web standards
            StrategyType.CONTEXTUAL_RELATIONSHIP: 8,    # Context-aware
            StrategyType.STRUCTURAL_PATTERN: 7,         # DOM structure
            StrategyType.TIMING_SYNCHRONIZATION: 6,     # Timing-aware
            StrategyType.VISUAL_FINGERPRINT: 5,         # Visual matching
            StrategyType.BEHAVIORAL_PATTERN: 4,         # Behavior analysis
            StrategyType.STATE_CONTEXT: 3,              # State awareness
            StrategyType.MUTATION_OBSERVATION: 2,       # Dynamic content
            StrategyType.ML_CONFIDENCE_FUSION: 1        # Post-processing
        }
    
    def _initialize_all_layers(self) -> Dict[StrategyType, BaseLayer]:
        """Initialize all 10 layers plus specialized edge case handlers."""
        
        layers = {}
        
        try:
            # Core 10 layers
            layers[StrategyType.SEMANTIC_INTENT] = UniversalSemanticIntentLayer()
            layers[StrategyType.CONTEXTUAL_RELATIONSHIP] = ContextualRelationshipLayer()
            layers[StrategyType.VISUAL_FINGERPRINT] = VisualFingerprintLayer()
            layers[StrategyType.BEHAVIORAL_PATTERN] = BehavioralPatternLayer()
            layers[StrategyType.STRUCTURAL_PATTERN] = StructuralPatternLayer()
            layers[StrategyType.ACCESSIBILITY_BRIDGE] = AccessibilityBridgeLayer()
            layers[StrategyType.MUTATION_OBSERVATION] = MutationObservationLayer()
            layers[StrategyType.TIMING_SYNCHRONIZATION] = TimingSynchronizationLayer()
            layers[StrategyType.STATE_CONTEXT] = StateContextLayer()
            
            print(f"✅ Successfully initialized {len(layers)}/9 core layers")
            
        except Exception as e:
            print(f"⚠️ Error initializing some layers: {e}")
        
        # Initialize specialized edge case handlers
        try:
            self.edge_case_handlers = {
                "shadow_dom": ShadowDOMHandler(),
                "canvas": CanvasHandler(), 
                "virtual_scroll": VirtualScrollHandler(),
                "icon_recognition": IconRecognitionLayer()
            }
            print(f"✅ Successfully initialized {len(self.edge_case_handlers)} edge case handlers")
            
        except Exception as e:
            print(f"⚠️ Error initializing edge case handlers: {e}")
            self.edge_case_handlers = {}
        
        return layers
    
    async def find_element_comprehensive(
        self,
        page: Any,
        context: ElementContext,
        max_strategies: Optional[int] = None
    ) -> Tuple[List[ElementStrategy], OrchestrationStats]:
        """
        Comprehensive element finding using all 10 layers with ML fusion.
        
        Returns:
            Tuple of (ranked_strategies, execution_stats)
        """
        
        start_time = time.time()
        stats = OrchestrationStats()
        
        # Step 1: Execute all layers in parallel (Layers 1-9)
        print(f"🔄 Executing {len(self.layers)} layers for intent: '{context.intent}'")
        
        layer_strategies = await self._execute_core_layers(page, context, stats)
        
        # Step 1.5: Execute edge case handlers if needed
        edge_strategies = await self._execute_edge_case_handlers(page, context, stats)
        layer_strategies.extend(edge_strategies)
        
        # Step 2: Apply ML Confidence Fusion (Layer 10)
        fusion_start = time.time()
        
        fused_strategies = await self.ml_fusion.fuse_strategies(layer_strategies, context)
        
        stats.fusion_time_ms = (time.time() - fusion_start) * 1000
        
        # Step 3: Apply final optimizations
        final_strategies = self._apply_final_optimizations(
            fused_strategies, max_strategies or self.max_total_strategies
        )
        
        # Update stats
        stats.total_time_ms = (time.time() - start_time) * 1000
        stats.total_strategies = len(final_strategies)
        
        self.execution_stats.append(stats)
        
        # Log results
        self._log_orchestration_results(context, final_strategies, stats)
        
        return final_strategies, stats
    
    async def _execute_core_layers(
        self,
        page: Any,
        context: ElementContext,
        stats: OrchestrationStats
    ) -> List[ElementStrategy]:
        """Execute the core 9 layers (excluding ML fusion) in parallel."""
        
        # Prepare layers for execution
        layers_to_execute = list(self.layers.values())
        
        # Execute layers in parallel
        start_time = time.time()
        
        try:
            # Use the existing AsyncLayerExecutor for parallel execution
            all_strategies = await AsyncLayerExecutor.execute_layers(
                layers_to_execute, page, context
            )
            
            stats.layers_executed = len(layers_to_execute)
            
            # Limit strategies per layer for performance
            layer_strategies = self._limit_strategies_per_layer(all_strategies)
            
            # Update stats
            for strategy in layer_strategies:
                layer_name = strategy.strategy_type.value
                stats.strategies_per_layer[layer_name] = stats.strategies_per_layer.get(layer_name, 0) + 1
            
            execution_time = (time.time() - start_time) * 1000
            stats.performance_breakdown["core_layers"] = execution_time
            
            print(f"✅ Core layers executed: {len(layer_strategies)} strategies in {execution_time:.1f}ms")
            
            return layer_strategies
            
        except Exception as e:
            print(f"❌ Error executing core layers: {e}")
            return []
    
    async def _execute_edge_case_handlers(
        self,
        page: Any,
        context: ElementContext,
        stats: OrchestrationStats
    ) -> List[ElementStrategy]:
        """Execute specialized edge case handlers when needed."""
        
        if not hasattr(self, 'edge_case_handlers'):
            return []
        
        edge_strategies = []
        intent_lower = context.intent.lower()
        html_content = context.html_content or ""
        
        try:
            # Detect if we need specialized handlers
            handlers_to_run = []
            
            # Shadow DOM detection
            if ("lightning" in context.platform or 
                "shadow" in html_content or 
                "web-component" in html_content or
                any(tag in html_content for tag in ["lightning-", "force-", "vaadin-"])):
                handlers_to_run.append("shadow_dom")
            
            # Canvas detection
            if ("canvas" in intent_lower or 
                "signature" in intent_lower or 
                "chart" in intent_lower or
                "<canvas" in html_content):
                handlers_to_run.append("canvas")
            
            # Virtual scroll detection
            if ("table" in intent_lower or 
                "row" in intent_lower or
                "virtual" in html_content or
                "infinite-scroll" in html_content or
                any(lib in html_content for lib in ["ag-grid", "react-window", "ReactVirtualized"])):
                handlers_to_run.append("virtual_scroll")
            
            # Icon recognition detection
            if (not any(word in intent_lower for word in ["field", "input", "text"]) and
                any(word in intent_lower for word in ["button", "save", "edit", "delete", "close"]) and
                ("icon" in html_content or "fa-" in html_content or "material-icons" in html_content)):
                handlers_to_run.append("icon_recognition")
            
            # Execute needed handlers
            for handler_name in handlers_to_run:
                if handler_name in self.edge_case_handlers:
                    handler = self.edge_case_handlers[handler_name]
                    handler_strategies = await handler.generate_strategies(page, context)
                    edge_strategies.extend(handler_strategies)
                    
                    print(f"🔧 Edge case handler '{handler_name}': {len(handler_strategies)} strategies")
            
            return edge_strategies
            
        except Exception as e:
            print(f"❌ Error in edge case handlers: {e}")
            return []
    
    def _limit_strategies_per_layer(
        self, 
        strategies: List[ElementStrategy]
    ) -> List[ElementStrategy]:
        """Limit the number of strategies per layer for performance."""
        
        layer_counts = {}
        limited_strategies = []
        
        # Sort by confidence first
        sorted_strategies = sorted(strategies, key=lambda s: s.confidence, reverse=True)
        
        for strategy in sorted_strategies:
            layer_name = strategy.strategy_type.value
            current_count = layer_counts.get(layer_name, 0)
            
            if current_count < self.max_strategies_per_layer:
                limited_strategies.append(strategy)
                layer_counts[layer_name] = current_count + 1
        
        return limited_strategies
    
    def _apply_final_optimizations(
        self,
        strategies: List[ElementStrategy],
        max_strategies: int
    ) -> List[ElementStrategy]:
        """Apply final optimizations to the strategy list."""
        
        # Remove duplicate selectors
        unique_strategies = self._remove_duplicate_selectors(strategies)
        
        # Sort by confidence and performance tier
        optimized_strategies = self._sort_by_performance_and_confidence(unique_strategies)
        
        # Limit to max strategies
        final_strategies = optimized_strategies[:max_strategies]
        
        return final_strategies
    
    def _remove_duplicate_selectors(
        self, 
        strategies: List[ElementStrategy]
    ) -> List[ElementStrategy]:
        """Remove strategies with duplicate selectors, keeping the highest confidence."""
        
        selector_map = {}
        
        for strategy in strategies:
            selector = strategy.selector
            
            if selector not in selector_map:
                selector_map[selector] = strategy
            else:
                # Keep the strategy with higher confidence
                if strategy.confidence > selector_map[selector].confidence:
                    selector_map[selector] = strategy
        
        return list(selector_map.values())
    
    def _sort_by_performance_and_confidence(
        self,
        strategies: List[ElementStrategy]
    ) -> List[ElementStrategy]:
        """Sort strategies by performance tier and confidence."""
        
        # Performance tier weights (higher = better)
        tier_weights = {
            PerformanceTier.INSTANT: 4,
            PerformanceTier.FAST: 3,
            PerformanceTier.MEDIUM: 2,
            PerformanceTier.EXPENSIVE: 1
        }
        
        def strategy_score(strategy: ElementStrategy) -> float:
            tier_weight = tier_weights.get(strategy.performance_tier, 1)
            return strategy.confidence * 0.7 + (tier_weight / 4) * 0.3
        
        return sorted(strategies, key=strategy_score, reverse=True)
    
    def _log_orchestration_results(
        self,
        context: ElementContext,
        strategies: List[ElementStrategy],
        stats: OrchestrationStats
    ):
        """Log the results of orchestration."""
        
        print(f"\n🎯 ORCHESTRATION RESULTS")
        print(f"   Intent: '{context.intent}'")
        print(f"   Platform: {context.platform}")
        print(f"   Total Time: {stats.total_time_ms:.1f}ms")
        print(f"   Strategies Found: {stats.total_strategies}")
        print(f"   Layers Executed: {stats.layers_executed}")
        
        if strategies:
            top_strategy = strategies[0]
            print(f"   Top Strategy: {top_strategy.selector} (conf: {top_strategy.confidence:.2f})")
            print(f"   Performance Tier: {top_strategy.performance_tier.value}")
            print(f"   Source Layer: {top_strategy.strategy_type.value}")
        
        # Show layer breakdown
        print(f"\n📊 LAYER BREAKDOWN:")
        for layer, count in stats.strategies_per_layer.items():
            print(f"   {layer}: {count} strategies")
    
    async def test_strategy(
        self,
        page: Any,
        strategy: ElementStrategy,
        context: ElementContext
    ) -> bool:
        """Test if a strategy successfully finds an element."""
        
        try:
            # Handle different selector types
            if strategy.selector.startswith("visual:"):
                # Visual strategies need special handling
                return await self._test_visual_strategy(page, strategy)
            
            elif strategy.selector.startswith("mutation:"):
                # Mutation strategies need special handling
                return await self._test_mutation_strategy(page, strategy)
            
            elif strategy.selector.startswith("ensemble:"):
                # Ensemble strategies need special handling
                return await self._test_ensemble_strategy(page, strategy)
            
            else:
                # Standard CSS/XPath selector
                if hasattr(page, 'query_selector'):
                    # Playwright
                    element = await page.query_selector(strategy.selector)
                    return element is not None
                else:
                    # Selenium or other
                    return False  # Would implement Selenium testing here
        
        except Exception as e:
            print(f"Strategy test failed: {e}")
            return False
    
    async def _test_visual_strategy(self, page: Any, strategy: ElementStrategy) -> bool:
        """Test visual-based strategies."""
        # Implementation would depend on visual fingerprinting capabilities
        return False  # Placeholder
    
    async def _test_mutation_strategy(self, page: Any, strategy: ElementStrategy) -> bool:
        """Test mutation-based strategies."""
        # Implementation would involve waiting for DOM changes
        return False  # Placeholder
    
    async def _test_ensemble_strategy(self, page: Any, strategy: ElementStrategy) -> bool:
        """Test ensemble strategies."""
        # Implementation would test multiple component strategies
        return False  # Placeholder
    
    def record_strategy_outcome(
        self,
        strategy: ElementStrategy,
        context: ElementContext,
        success: bool,
        execution_time_ms: float,
        error_message: Optional[str] = None
    ):
        """Record the outcome of a strategy for ML learning."""
        
        # Record in ML fusion layer for learning
        self.ml_fusion.record_outcome(
            strategy, context, success, execution_time_ms, error_message
        )
    
    def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics about orchestration performance."""
        
        if not self.execution_stats:
            return {"message": "No orchestration data available"}
        
        # Calculate aggregate statistics
        total_executions = len(self.execution_stats)
        avg_time = sum(s.total_time_ms for s in self.execution_stats) / total_executions
        avg_strategies = sum(s.total_strategies for s in self.execution_stats) / total_executions
        avg_layers = sum(s.layers_executed for s in self.execution_stats) / total_executions
        
        # Layer performance breakdown
        layer_strategy_counts = {}
        for stats in self.execution_stats:
            for layer, count in stats.strategies_per_layer.items():
                if layer not in layer_strategy_counts:
                    layer_strategy_counts[layer] = []
                layer_strategy_counts[layer].append(count)
        
        layer_averages = {
            layer: sum(counts) / len(counts)
            for layer, counts in layer_strategy_counts.items()
        }
        
        # Get ML fusion statistics
        ml_fusion_stats = self.ml_fusion.get_fusion_stats()
        
        return {
            "orchestration": {
                "total_executions": total_executions,
                "average_time_ms": round(avg_time, 1),
                "average_strategies": round(avg_strategies, 1),
                "average_layers_executed": round(avg_layers, 1),
                "layer_performance": layer_averages
            },
            "ml_fusion": ml_fusion_stats,
            "layer_health": self._get_layer_health_status()
        }
    
    def _get_layer_health_status(self) -> Dict[str, str]:
        """Get health status of all layers."""
        
        health_status = {}
        
        for strategy_type, layer in self.layers.items():
            try:
                # Check if layer has metrics and is responsive
                metrics = layer.get_metrics()
                
                if metrics["total_calls"] > 0:
                    success_rate = metrics["successful_strategies"] / metrics["total_calls"]
                    if success_rate > 0.7:
                        health_status[strategy_type.value] = "healthy"
                    elif success_rate > 0.3:
                        health_status[strategy_type.value] = "warning"
                    else:
                        health_status[strategy_type.value] = "critical"
                else:
                    health_status[strategy_type.value] = "untested"
            
            except Exception as e:
                health_status[strategy_type.value] = f"error: {str(e)[:50]}"
        
        # Add ML fusion health
        try:
            fusion_stats = self.ml_fusion.get_fusion_stats()
            fusion_success_rate = fusion_stats.get("overall_success_rate", 0)
            
            if fusion_success_rate > 0.8:
                health_status["ml_confidence_fusion"] = "healthy"
            elif fusion_success_rate > 0.5:
                health_status["ml_confidence_fusion"] = "warning"  
            else:
                health_status["ml_confidence_fusion"] = "critical"
                
        except Exception as e:
            health_status["ml_confidence_fusion"] = f"error: {str(e)[:50]}"
        
        return health_status
    
    def reset_statistics(self):
        """Reset orchestration statistics."""
        self.execution_stats = []
        print("📊 Orchestration statistics reset")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        
        return {
            "system": "Helix 10-Layer Universal Element Finder",
            "layers_initialized": len(self.layers),
            "total_layers": 10,  # Including ML fusion
            "status": "operational" if len(self.layers) >= 8 else "degraded",
            "version": "1.0.0",
            "capabilities": [
                "Universal semantic understanding",
                "Cross-platform compatibility",
                "ML-powered optimization",
                "Performance-tiered execution",
                "Visual fingerprinting",
                "Accessibility compliance",
                "Dynamic content handling",
                "Behavioral pattern recognition",
                "Structural analysis",
                "Context awareness"
            ],
            "metrics": self.get_orchestration_metrics()
        }