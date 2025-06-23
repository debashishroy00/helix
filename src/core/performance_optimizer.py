"""
Performance Optimizer for Helix
================================

Optimizes the multi-layer system for faster response times.
Target: <2 seconds for 90% of requests.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Set
from concurrent.futures import ThreadPoolExecutor
import functools
from dataclasses import dataclass

from ..models.element import ElementStrategy, ElementContext, StrategyType
from ..layers.base import BaseLayer


@dataclass
class LayerPerformanceProfile:
    """Performance profile for each layer."""
    layer_type: StrategyType
    average_time_ms: float
    success_rate: float
    priority: int  # 1-10, higher = run first
    can_run_parallel: bool
    requires_browser: bool


class PerformanceOptimizer:
    """
    Optimizes multi-layer execution for performance.
    
    Key strategies:
    1. Smart layer ordering based on success rates
    2. Early termination when high-confidence result found
    3. Parallel execution of independent layers
    4. Caching of expensive operations
    5. Timeout management per layer
    """
    
    def __init__(self):
        # Performance profiles for each layer
        self.layer_profiles = {
            StrategyType.SEMANTIC_INTENT: LayerPerformanceProfile(
                layer_type=StrategyType.SEMANTIC_INTENT,
                average_time_ms=800,  # GPT-4 API call
                success_rate=0.85,
                priority=9,
                can_run_parallel=True,
                requires_browser=False
            ),
            StrategyType.CONTEXTUAL_RELATIONSHIP: LayerPerformanceProfile(
                layer_type=StrategyType.CONTEXTUAL_RELATIONSHIP,
                average_time_ms=50,  # Pure computation
                success_rate=0.70,
                priority=8,
                can_run_parallel=True,
                requires_browser=False
            ),
            StrategyType.BEHAVIORAL_PATTERN: LayerPerformanceProfile(
                layer_type=StrategyType.BEHAVIORAL_PATTERN,
                average_time_ms=100,  # Pattern matching
                success_rate=0.60,
                priority=6,
                can_run_parallel=True,
                requires_browser=False
            ),
            StrategyType.VISUAL_FINGERPRINT: LayerPerformanceProfile(
                layer_type=StrategyType.VISUAL_FINGERPRINT,
                average_time_ms=2000,  # Screenshot + OCR
                success_rate=0.90,
                priority=3,
                can_run_parallel=False,
                requires_browser=True
            ),
            StrategyType.TIMING_SYNCHRONIZATION: LayerPerformanceProfile(
                layer_type=StrategyType.TIMING_SYNCHRONIZATION,
                average_time_ms=200,
                success_rate=0.75,
                priority=7,
                can_run_parallel=True,
                requires_browser=False
            ),
            StrategyType.STATE_CONTEXT_AWARENESS: LayerPerformanceProfile(
                layer_type=StrategyType.STATE_CONTEXT_AWARENESS,
                average_time_ms=300,
                success_rate=0.65,
                priority=5,
                can_run_parallel=True,
                requires_browser=False
            )
        }
        
        # Optimization settings
        self.early_termination_confidence = 0.90
        self.max_parallel_layers = 4
        self.layer_timeout_ms = 1000
        self.total_timeout_ms = 2000  # Target: 2 second response
        
    def get_optimized_layer_order(
        self, 
        context: ElementContext,
        available_layers: Dict[StrategyType, BaseLayer]
    ) -> List[BaseLayer]:
        """
        Get optimized order for layer execution based on context.
        """
        # Score layers based on multiple factors
        layer_scores = []
        
        for layer_type, layer in available_layers.items():
            profile = self.layer_profiles.get(layer_type)
            if not profile:
                continue
                
            # Calculate score based on:
            # 1. Success rate (40%)
            # 2. Speed (30%)
            # 3. Context relevance (30%)
            
            success_score = profile.success_rate * 40
            speed_score = (1.0 - min(profile.average_time_ms / 2000, 1.0)) * 30
            relevance_score = self._get_context_relevance(layer_type, context) * 30
            
            total_score = success_score + speed_score + relevance_score
            
            layer_scores.append((layer, total_score, profile))
        
        # Sort by score (highest first)
        layer_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [item[0] for item in layer_scores]
    
    def _get_context_relevance(
        self, 
        layer_type: StrategyType, 
        context: ElementContext
    ) -> float:
        """
        Calculate how relevant a layer is for the given context.
        """
        intent_lower = context.intent.lower()
        
        # Semantic layer is best for clear intent
        if layer_type == StrategyType.SEMANTIC_INTENT:
            if any(word in intent_lower for word in ['button', 'field', 'link', 'save', 'submit']):
                return 0.9
            return 0.7
            
        # Contextual is best for relational queries
        elif layer_type == StrategyType.CONTEXTUAL_RELATIONSHIP:
            if any(word in intent_lower for word in ['next to', 'beside', 'near', 'in section', 'under']):
                return 0.95
            return 0.5
            
        # Behavioral is best for interactive elements
        elif layer_type == StrategyType.BEHAVIORAL_PATTERN:
            if any(word in intent_lower for word in ['hover', 'click', 'focus', 'active']):
                return 0.9
            return 0.6
            
        return 0.5
    
    async def execute_with_optimization(
        self,
        layers: Dict[StrategyType, BaseLayer],
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """
        Execute layers with performance optimization.
        """
        start_time = time.time()
        all_strategies = []
        
        # Get optimized layer order
        ordered_layers = self.get_optimized_layer_order(context, layers)
        
        # Group layers by parallelization capability
        parallel_group = []
        serial_layers = []
        
        for layer in ordered_layers:
            profile = self.layer_profiles.get(layer.layer_type)
            if profile and profile.can_run_parallel:
                parallel_group.append(layer)
            else:
                serial_layers.append(layer)
        
        # Execute parallel layers first
        if parallel_group:
            parallel_strategies = await self._execute_parallel_layers(
                parallel_group[:self.max_parallel_layers],
                page,
                context
            )
            all_strategies.extend(parallel_strategies)
            
            # Check for early termination
            if self._should_terminate_early(all_strategies):
                return all_strategies
        
        # Execute serial layers if needed
        remaining_time = self.total_timeout_ms - (time.time() - start_time) * 1000
        
        for layer in serial_layers:
            if remaining_time <= 0:
                break
                
            try:
                layer_start = time.time()
                strategies = await asyncio.wait_for(
                    layer.execute(page, context),
                    timeout=min(self.layer_timeout_ms / 1000, remaining_time / 1000)
                )
                all_strategies.extend(strategies)
                
                # Check for early termination
                if self._should_terminate_early(all_strategies):
                    break
                    
                remaining_time -= (time.time() - layer_start) * 1000
                
            except asyncio.TimeoutError:
                print(f"Layer {layer.layer_type.value} timed out")
                continue
        
        # Sort by confidence
        all_strategies.sort(key=lambda s: s.confidence, reverse=True)
        
        return all_strategies
    
    async def _execute_parallel_layers(
        self,
        layers: List[BaseLayer],
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """
        Execute multiple layers in parallel with timeout.
        """
        tasks = []
        
        for layer in layers:
            task = asyncio.create_task(
                asyncio.wait_for(
                    layer.execute(page, context),
                    timeout=self.layer_timeout_ms / 1000
                )
            )
            tasks.append(task)
        
        # Wait for all tasks with timeout
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect successful results
        all_strategies = []
        for result in results:
            if isinstance(result, list):
                all_strategies.extend(result)
            elif isinstance(result, asyncio.TimeoutError):
                continue
            elif isinstance(result, Exception):
                print(f"Layer error: {result}")
        
        return all_strategies
    
    def _should_terminate_early(self, strategies: List[ElementStrategy]) -> bool:
        """
        Check if we should stop executing more layers.
        """
        if not strategies:
            return False
            
        # Check if we have a high-confidence result
        best_confidence = max(s.confidence for s in strategies)
        return best_confidence >= self.early_termination_confidence
    
    def get_performance_recommendations(
        self,
        response_time_ms: float,
        strategies_tried: List[ElementStrategy]
    ) -> List[str]:
        """
        Get recommendations for improving performance.
        """
        recommendations = []
        
        if response_time_ms > 5000:
            recommendations.append("Consider caching GPT-4 responses for common patterns")
            recommendations.append("Enable early termination at 0.85 confidence")
            
        if response_time_ms > 10000:
            recommendations.append("Disable visual layer for non-critical elements")
            recommendations.append("Use semantic-only mode for faster responses")
            
        # Check which layers are slowest
        layer_times = {}
        for strategy in strategies_tried:
            if hasattr(strategy, 'execution_time_ms'):
                layer_type = strategy.strategy_type
                if layer_type not in layer_times:
                    layer_times[layer_type] = []
                layer_times[layer_type].append(strategy.execution_time_ms)
        
        # Find slowest layers
        for layer_type, times in layer_times.items():
            avg_time = sum(times) / len(times)
            if avg_time > 1000:
                recommendations.append(f"Optimize {layer_type.value}: avg {avg_time:.0f}ms")
        
        return recommendations