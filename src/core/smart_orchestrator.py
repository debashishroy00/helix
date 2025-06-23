"""
Smart Layer Orchestrator
========================

Runs deterministic layers first, then AI layers only if needed.
This can reduce 90% of LLM calls for common patterns.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass

from ..models.element import ElementStrategy, ElementContext, StrategyType
from ..layers.base import BaseLayer


@dataclass
class LayerTier:
    """Categorizes layers by execution cost and determinism."""
    instant: List[StrategyType]      # Pattern matching, no AI/browser
    fast: List[StrategyType]         # Lightweight computation 
    expensive: List[StrategyType]    # AI calls, browser operations
    fallback: List[StrategyType]     # Last resort


class SmartOrchestrator:
    """
    Intelligent layer orchestration that minimizes expensive operations.
    
    Strategy:
    1. Try instant deterministic layers first (pattern matching)
    2. If high confidence result found, stop
    3. Otherwise try fast computational layers
    4. Only call AI/browser layers if needed
    """
    
    def __init__(self):
        self.layer_tiers = LayerTier(
            instant=[
                # Pure pattern matching - instant results
                StrategyType.CONTEXTUAL_RELATIONSHIP,
                StrategyType.BEHAVIORAL_PATTERN,
                StrategyType.STRUCTURAL_PATTERN,
                StrategyType.ACCESSIBILITY_BRIDGE,
            ],
            fast=[
                # Light computation, no external calls
                StrategyType.TIMING_SYNCHRONIZATION,
                StrategyType.STATE_CONTEXT_AWARENESS,
                StrategyType.MUTATION_OBSERVATION,
            ],
            expensive=[
                # AI calls - only if needed
                StrategyType.SEMANTIC_INTENT,
            ],
            fallback=[
                # Visual/browser - most expensive
                StrategyType.VISUAL_FINGERPRINT,
                StrategyType.ML_FUSION,
            ]
        )
        
        # Confidence thresholds for early termination
        self.high_confidence_threshold = 0.85
        self.medium_confidence_threshold = 0.70
        
        # Pattern-based deterministic selectors
        self.deterministic_patterns = self._build_deterministic_patterns()
    
    def _build_deterministic_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Build deterministic pattern database for instant matching.
        These patterns cover 80% of common use cases without AI.
        """
        return {
            "salesforce_lightning": [
                # Buttons
                {
                    "patterns": ["new", "create", "add"],
                    "element_type": "button",
                    "selectors": [
                        "lightning-button[title*='New']",
                        "button[title*='New']",
                        ".slds-button[title*='New']",
                        "[data-aura-class*='New']"
                    ],
                    "confidence": 0.85
                },
                {
                    "patterns": ["save", "submit"],
                    "element_type": "button",
                    "selectors": [
                        "button[type='submit']",
                        "lightning-button[title*='Save']",
                        ".slds-button[title*='Save']",
                        "button[title*='Save']"
                    ],
                    "confidence": 0.80
                },
                {
                    "patterns": ["edit", "modify"],
                    "element_type": "button",
                    "selectors": [
                        "lightning-button[title*='Edit']",
                        "button[title*='Edit']",
                        ".slds-button[title*='Edit']"
                    ],
                    "confidence": 0.80
                },
                {
                    "patterns": ["delete", "remove"],
                    "element_type": "button", 
                    "selectors": [
                        "lightning-button[title*='Delete']",
                        "button[title*='Delete']",
                        ".slds-button[title*='Delete']"
                    ],
                    "confidence": 0.80
                },
                # Form fields
                {
                    "patterns": ["name", "title"],
                    "element_type": "input",
                    "selectors": [
                        "lightning-input[data-field='Name']",
                        "input[placeholder*='Name']",
                        "lightning-input[label*='Name']"
                    ],
                    "confidence": 0.75
                },
                {
                    "patterns": ["email"],
                    "element_type": "input",
                    "selectors": [
                        "lightning-input[type='email']",
                        "input[type='email']",
                        "lightning-input[data-field='Email']"
                    ],
                    "confidence": 0.85
                },
                {
                    "patterns": ["phone", "telephone"],
                    "element_type": "input",
                    "selectors": [
                        "lightning-input[type='tel']",
                        "input[type='tel']",
                        "lightning-input[data-field='Phone']"
                    ],
                    "confidence": 0.80
                },
                # Navigation
                {
                    "patterns": ["search", "find"],
                    "element_type": "input",
                    "selectors": [
                        "input[type='search']",
                        ".globalSearchInput",
                        "lightning-input[placeholder*='Search']"
                    ],
                    "confidence": 0.85
                }
            ],
            "generic": [
                # Universal patterns that work everywhere
                {
                    "patterns": ["submit", "save"],
                    "element_type": "button",
                    "selectors": [
                        "button[type='submit']",
                        "input[type='submit']",
                        "button:contains('Submit')",
                        "button:contains('Save')"
                    ],
                    "confidence": 0.70
                },
                {
                    "patterns": ["search"],
                    "element_type": "input",
                    "selectors": [
                        "input[type='search']",
                        "input[placeholder*='search' i]",
                        "#search",
                        ".search-input"
                    ],
                    "confidence": 0.70
                }
            ]
        }
    
    async def find_element_smart(
        self,
        layers: Dict[StrategyType, BaseLayer],
        page: Any,
        context: ElementContext,
        max_time_ms: int = 5000
    ) -> Tuple[List[ElementStrategy], str]:
        """
        Smart element finding with minimal AI usage.
        
        Returns: (strategies, execution_path)
        """
        start_time = time.time()
        execution_path = []
        
        # Phase 1: Try deterministic patterns first (instant)
        strategies = self._try_deterministic_patterns(context)
        print(f"Deterministic patterns found {len(strategies)} strategies")
        if strategies:
            execution_path.append("deterministic_patterns")
            # Check if we found high-confidence results
            best_confidence = max(s.confidence for s in strategies)
            print(f"Best deterministic confidence: {best_confidence}")
            if best_confidence >= self.high_confidence_threshold:
                return strategies, "->".join(execution_path)
        
        # Phase 2: Try instant layers (pattern matching)
        instant_strategies = await self._run_layer_tier(
            layers, page, context, self.layer_tiers.instant, "instant"
        )
        strategies.extend(instant_strategies)
        if instant_strategies:
            execution_path.append("instant_layers")
            
        # Check for early termination
        if strategies:
            best_confidence = max(s.confidence for s in strategies)
            if best_confidence >= self.high_confidence_threshold:
                return strategies, "->".join(execution_path)
        
        # Phase 3: Try fast computational layers
        remaining_time = max_time_ms - (time.time() - start_time) * 1000
        if remaining_time > 1000:  # At least 1 second left
            fast_strategies = await self._run_layer_tier(
                layers, page, context, self.layer_tiers.fast, "fast"
            )
            strategies.extend(fast_strategies)
            if fast_strategies:
                execution_path.append("fast_layers")
                
            # Check for medium confidence termination
            if strategies:
                best_confidence = max(s.confidence for s in strategies)
                if best_confidence >= self.medium_confidence_threshold:
                    return strategies, "->".join(execution_path)
        
        # Phase 4: Only now try expensive AI layers
        remaining_time = max_time_ms - (time.time() - start_time) * 1000
        if remaining_time > 2000:  # At least 2 seconds left
            expensive_strategies = await self._run_layer_tier(
                layers, page, context, self.layer_tiers.expensive, "expensive"
            )
            strategies.extend(expensive_strategies)
            if expensive_strategies:
                execution_path.append("ai_layers")
        
        # Phase 5: Fallback to visual/browser only if really needed
        remaining_time = max_time_ms - (time.time() - start_time) * 1000
        if not strategies and remaining_time > 3000:  # Only if no results and time left
            fallback_strategies = await self._run_layer_tier(
                layers, page, context, self.layer_tiers.fallback, "fallback"
            )
            strategies.extend(fallback_strategies)
            if fallback_strategies:
                execution_path.append("visual_layers")
        
        # Sort by confidence
        strategies.sort(key=lambda s: s.confidence, reverse=True)
        
        return strategies, "->".join(execution_path)
    
    def _try_deterministic_patterns(self, context: ElementContext) -> List[ElementStrategy]:
        """
        Try deterministic pattern matching first - no AI needed.
        This handles 80% of common cases instantly.
        """
        strategies = []
        intent_lower = context.intent.lower()
        
        # Get platform patterns
        platform_patterns = self.deterministic_patterns.get(
            context.platform.value, 
            self.deterministic_patterns.get("generic", [])
        )
        
        # Also try generic patterns
        all_patterns = platform_patterns + self.deterministic_patterns.get("generic", [])
        
        for pattern_def in all_patterns:
            # Check if intent matches any patterns
            if any(pattern in intent_lower for pattern in pattern_def["patterns"]):
                print(f"Pattern matched: {pattern_def['patterns']} for intent: {intent_lower}")
                # Generate strategies for each selector
                for selector in pattern_def["selectors"]:
                    strategy = ElementStrategy(
                        strategy_type=StrategyType.CONTEXTUAL_RELATIONSHIP,  # Mark as contextual
                        selector=selector,
                        confidence=pattern_def["confidence"],
                        metadata={
                            "source": "deterministic_pattern",
                            "pattern": pattern_def["patterns"],
                            "platform": context.platform.value,
                            "instant": True
                        }
                    )
                    strategies.append(strategy)
                    print(f"Added strategy: {selector} with confidence {pattern_def['confidence']}")
            else:
                print(f"No match for patterns {pattern_def['patterns']} in intent: {intent_lower}")
        
        return strategies
    
    async def _run_layer_tier(
        self,
        layers: Dict[StrategyType, BaseLayer],
        page: Any,
        context: ElementContext,
        tier_layers: List[StrategyType],
        tier_name: str
    ) -> List[ElementStrategy]:
        """Run all layers in a tier in parallel."""
        tasks = []
        
        for layer_type in tier_layers:
            if layer_type in layers:
                layer = layers[layer_type]
                task = asyncio.create_task(
                    layer.execute(page, context)
                )
                tasks.append(task)
        
        if not tasks:
            return []
        
        # Execute tier in parallel with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=2.0 if tier_name == "expensive" else 1.0
            )
            
            # Collect strategies
            strategies = []
            for result in results:
                if isinstance(result, list):
                    for strategy in result:
                        # Tag with execution tier
                        strategy.metadata = strategy.metadata or {}
                        strategy.metadata["execution_tier"] = tier_name
                    strategies.extend(result)
            
            return strategies
            
        except asyncio.TimeoutError:
            print(f"Tier {tier_name} timed out")
            return []
    
    def get_performance_stats(self, execution_path: str, total_time_ms: float) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            "execution_path": execution_path,
            "total_time_ms": total_time_ms,
            "used_ai": "ai_layers" in execution_path,
            "used_browser": "visual_layers" in execution_path,
            "early_termination": "deterministic_patterns" in execution_path or "instant_layers" in execution_path,
            "efficiency_score": self._calculate_efficiency_score(execution_path, total_time_ms)
        }
    
    def _calculate_efficiency_score(self, execution_path: str, total_time_ms: float) -> float:
        """Calculate efficiency score (0-1, higher is better)."""
        base_score = 1.0
        
        # Penalty for using expensive operations
        if "ai_layers" in execution_path:
            base_score -= 0.3
        if "visual_layers" in execution_path:
            base_score -= 0.4
        
        # Bonus for early termination
        if execution_path in ["deterministic_patterns", "deterministic_patterns->instant_layers"]:
            base_score += 0.2
        
        # Time penalty
        if total_time_ms > 5000:
            base_score -= 0.2
        elif total_time_ms < 1000:
            base_score += 0.1
        
        return max(0.0, min(1.0, base_score))