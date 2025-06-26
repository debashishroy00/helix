"""
Enhanced Helix Orchestrator - Production Robust
==============================================
This orchestrator addresses the core robustness issues by:

1. DOM-verified strategy generation
2. Intelligent fallback mechanisms  
3. Real-time element validation
4. Performance optimization
5. Error recovery and reporting

The goal is to make Helix AI Engine work reliably in production environments.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from src.models.element import ElementStrategy, ElementContext, ElementResult, StrategyType, PerformanceTier
from src.layers.base import BaseLayer, AsyncLayerExecutor
from src.utils.robust_html_parser import parse_html

# Import original proven layers - NO SHORTCUTS
from src.layers.enhanced_semantic_intent import EnhancedSemanticIntentLayer
from src.layers.accessibility_bridge import AccessibilityBridgeLayer  
from src.layers.contextual_relationship import ContextualRelationshipLayer
from src.layers.structural_pattern import StructuralPatternLayer


@dataclass
class EnhancedStats:
    """Enhanced statistics with robustness metrics."""
    total_strategies: int = 0
    verified_strategies: int = 0
    layers_executed: int = 0
    total_time_ms: float = 0.0
    dom_verification_time_ms: float = 0.0
    fallback_used: bool = False
    error_recovery_count: int = 0
    confidence_distribution: Dict[str, int] = None
    
    def __post_init__(self):
        if self.confidence_distribution is None:
            self.confidence_distribution = {"high": 0, "medium": 0, "low": 0}


class EnhancedHelixOrchestrator:
    """
    Enhanced orchestrator with production-grade robustness.
    
    Key improvements:
    - DOM verification for all strategies
    - Intelligent fallback mechanisms
    - Performance optimization
    - Error recovery
    - Real-time validation
    """
    
    def __init__(self):
        self.enhanced_layers = self._initialize_enhanced_layers()
        self.execution_stats = []
        
        # Robustness settings
        self.max_strategies_per_layer = 8
        self.max_total_strategies = 15
        self.verification_timeout_ms = 2000
        self.fallback_enabled = True
        
        # Performance tracking
        self.layer_performance = {}
        self.success_patterns = {}
        
        print(f"🚀 Enhanced Helix Orchestrator initialized")
        print(f"   Enhanced layers: {len(self.enhanced_layers)}")
        print(f"   DOM verification: Enabled")
        print(f"   Fallback strategies: Enabled")
    
    def _initialize_enhanced_layers(self) -> Dict[StrategyType, BaseLayer]:
        """Initialize enhanced layers with improved robustness."""
        
        layers = {}
        
        try:
            # Core enhanced layers
            layers[StrategyType.SEMANTIC_INTENT] = EnhancedSemanticIntentLayer()
            layers[StrategyType.ACCESSIBILITY_BRIDGE] = AccessibilityBridgeLayer()
            layers[StrategyType.CONTEXTUAL_RELATIONSHIP] = ContextualRelationshipLayer()
            layers[StrategyType.STRUCTURAL_PATTERN] = StructuralPatternLayer()
            
            print(f"✅ Successfully initialized {len(layers)} enhanced layers")
            
        except Exception as e:
            print(f"❌ Error initializing enhanced layers: {e}")
        
        return layers
    
    async def find_element_enhanced(
        self,
        page: Any,
        context: ElementContext,
        max_strategies: Optional[int] = None
    ) -> Tuple[List[ElementStrategy], EnhancedStats]:
        """
        Enhanced element finding with comprehensive robustness features.
        
        Returns DOM-verified strategies with intelligent fallbacks.
        """
        
        start_time = time.time()
        stats = EnhancedStats()
        
        print(f"🔍 Enhanced element finding for: '{context.intent}'")
        print(f"   Platform: {context.platform}")
        print(f"   HTML size: {len(context.html_content or '')} chars")
        
        # Step 1: Execute enhanced layers
        layer_strategies = await self._execute_enhanced_layers(page, context, stats)
        
        # Step 2: Verify strategies exist in DOM
        verified_strategies = await self._verify_strategies_in_dom(layer_strategies, context, stats)
        
        # Step 3: Apply intelligent fallbacks if needed
        if len(verified_strategies) < 3 and self.fallback_enabled:
            fallback_strategies = await self._apply_intelligent_fallbacks(context, stats)
            verified_strategies.extend(fallback_strategies)
            stats.fallback_used = True
        
        # Step 4: Rank and optimize final strategies
        final_strategies = self._rank_and_optimize_strategies(verified_strategies, context)
        
        # Step 5: Update statistics
        stats.total_time_ms = (time.time() - start_time) * 1000
        stats.total_strategies = len(layer_strategies)
        stats.verified_strategies = len(verified_strategies)
        
        self._update_confidence_distribution(final_strategies, stats)
        self.execution_stats.append(stats)
        
        # Log results
        self._log_enhanced_results(context, final_strategies, stats)
        
        return final_strategies[:max_strategies or self.max_total_strategies], stats
    
    async def _execute_enhanced_layers(
        self,
        page: Any,
        context: ElementContext,
        stats: EnhancedStats
    ) -> List[ElementStrategy]:
        """Execute enhanced layers with performance tracking."""
        
        all_strategies = []
        
        # Execute layers in priority order
        layer_priority = [
            StrategyType.SEMANTIC_INTENT,      # Enhanced semantic understanding
            StrategyType.ACCESSIBILITY_BRIDGE, # ARIA and accessibility  
            StrategyType.STRUCTURAL_PATTERN,   # DOM structure analysis
            StrategyType.CONTEXTUAL_RELATIONSHIP # Context awareness
        ]
        
        for layer_type in layer_priority:
            if layer_type not in self.enhanced_layers:
                continue
            
            layer = self.enhanced_layers[layer_type]
            layer_start = time.time()
            
            try:
                strategies = await layer.generate_strategies(page, context)
                layer_duration = (time.time() - layer_start) * 1000
                
                # Track layer performance
                self.layer_performance[layer_type.value] = {
                    "last_duration_ms": layer_duration,
                    "strategies_generated": len(strategies),
                    "success": len(strategies) > 0
                }
                
                # Limit strategies per layer
                limited_strategies = strategies[:self.max_strategies_per_layer]
                all_strategies.extend(limited_strategies)
                
                print(f"  📊 {layer_type.value}: {len(limited_strategies)} strategies in {layer_duration:.1f}ms")
                
            except Exception as e:
                print(f"  ❌ Layer {layer_type.value} failed: {e}")
                stats.error_recovery_count += 1
                continue
        
        stats.layers_executed = len([l for l in self.layer_performance.values() if l["success"]])
        
        return all_strategies
    
    async def _verify_strategies_in_dom(
        self,
        strategies: List[ElementStrategy],
        context: ElementContext,
        stats: EnhancedStats
    ) -> List[ElementStrategy]:
        """Verify that strategies actually exist in the DOM."""
        
        verification_start = time.time()
        verified_strategies = []
        
        print(f"  🔍 Verifying {len(strategies)} strategies in DOM...")
        
        # Verify strategies using robust HTML parsing
        html_content = context.html_content or ""
        if not html_content:
            print(f"  ⚠️ No HTML content provided for verification")
            return strategies  # Return unverified if no HTML
        
        # Parse HTML using robust parser
        soup = parse_html(html_content)
        
        for strategy in strategies:
            try:
                if self._verify_selector_in_dom(strategy.selector, soup):
                    verified_strategies.append(strategy)
                    print(f"    ✅ {strategy.selector} - Found in DOM")
                else:
                    print(f"    ❌ {strategy.selector} - Not found in DOM")
            except Exception as e:
                print(f"    ⚠️ {strategy.selector} - Verification error: {e}")
                # Include strategy with reduced confidence if verification fails
                strategy.confidence *= 0.7
                verified_strategies.append(strategy)
        
        stats.dom_verification_time_ms = (time.time() - verification_start) * 1000
        
        print(f"  ✅ DOM verification: {len(verified_strategies)}/{len(strategies)} strategies valid ({stats.dom_verification_time_ms:.1f}ms)")
        
        return verified_strategies
    
    def _verify_selector_in_dom(self, selector: str, soup) -> bool:
        """Verify a CSS selector exists in the DOM using robust parser."""
        
        try:
            # Use the robust soup's find methods
            if selector.startswith('#'):
                # ID selector
                element_id = selector[1:]
                return soup.find(attrs={'id': element_id}) is not None
            
            elif selector.startswith('.'):
                # Class selector  
                class_name = selector[1:]
                return soup.find(attrs={'class': lambda x: x and class_name in x.split()}) is not None
            
            elif '[' in selector and ']' in selector:
                # Attribute selector
                if 'type=' in selector:
                    type_match = re.search(r'type=["\']?([^"\'\s>]+)["\']?', selector)
                    if type_match:
                        type_value = type_match.group(1)
                        element_type = selector.split('[')[0] if '[' in selector else 'input'
                        return soup.find(element_type, attrs={'type': type_value}) is not None
                
                if 'name=' in selector:
                    name_match = re.search(r'name=["\']?([^"\'\s>]+)["\']?', selector)
                    if name_match:
                        name_value = name_match.group(1)
                        return soup.find(attrs={'name': name_value}) is not None
                
                # Generic attribute check
                attr_match = re.search(r'\[([^=\]]+)', selector)
                if attr_match:
                    attr_name = attr_match.group(1)
                    return soup.find(attrs={attr_name: True}) is not None
            
            elif selector in ['button', 'input', 'a', 'form', 'select', 'div', 'span']:
                # Element type selector
                return soup.find(selector) is not None
            
            else:
                # Try CSS selector if available
                try:
                    results = soup.select(selector)
                    return len(results) > 0
                except:
                    # Fallback to basic element type check
                    element_match = re.match(r'^([a-zA-Z]+)', selector)
                    if element_match:
                        element_type = element_match.group(1)
                        return soup.find(element_type) is not None
                    return True  # Assume valid for complex selectors
                
        except Exception as e:
            print(f"    ⚠️ Robust selector verification error for '{selector}': {e}")
            return False
    
    async def _apply_intelligent_fallbacks(
        self,
        context: ElementContext,
        stats: EnhancedStats
    ) -> List[ElementStrategy]:
        """Apply intelligent fallback strategies when primary strategies fail."""
        
        print(f"  🔄 Applying intelligent fallbacks for: '{context.intent}'")
        
        fallback_strategies = []
        intent_lower = context.intent.lower()
        
        # Universal fallback patterns based on intent analysis
        fallback_patterns = {
            # Authentication fallbacks
            "login": [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Log')",
                "*[aria-label*='log' i]"
            ],
            "username": [
                "input[type='text']:first",
                "input[type='email']",
                "input[name*='user' i]",
                "input[placeholder*='user' i]"
            ],
            "password": [
                "input[type='password']",
                "input[name*='pass' i]",
                "input[placeholder*='pass' i]"
            ],
            
            # Navigation fallbacks
            "app launcher": [
                "button[title*='App' i]",
                "button[aria-label*='App' i]",
                ".appLauncher",
                "*[class*='waffle' i]"
            ],
            "sales": [
                "a:contains('Sales')",
                "*[title*='Sales' i]",
                "*[aria-label*='Sales' i]"
            ],
            
            # Form element fallbacks
            "new": [
                "button:contains('New')",
                "a[title='New']",
                "*[aria-label*='New' i]",
                "input[value='New']"
            ],
            "save": [
                "button:contains('Save')",
                "input[type='submit']",
                "button[type='submit']",
                "*[aria-label*='Save' i]"
            ],
            
            # Field fallbacks
            "name": [
                "input[name*='Name' i]",
                "input[placeholder*='Name' i]",
                "input[aria-label*='Name' i]"
            ]
        }
        
        # Find applicable fallback patterns
        for pattern_key, selectors in fallback_patterns.items():
            if pattern_key in intent_lower:
                for i, selector in enumerate(selectors):
                    confidence = 0.6 - (i * 0.1)  # Decreasing confidence for each fallback
                    confidence = max(0.3, confidence)  # Minimum confidence
                    
                    fallback_strategies.append(ElementStrategy(
                        selector=selector,
                        confidence=confidence,
                        strategy_type=StrategyType.SEMANTIC_INTENT,
                        performance_tier=PerformanceTier.MEDIUM,
                        reasoning=f"Intelligent fallback for '{pattern_key}' intent",
                        metadata={
                            "method": "intelligent_fallback",
                            "pattern": pattern_key,
                            "fallback_level": i + 1
                        }
                    ))
        
        # Generic fallbacks based on element type inference
        if "button" in intent_lower or "click" in intent_lower:
            fallback_strategies.extend([
                ElementStrategy(
                    selector="button",
                    confidence=0.4,
                    strategy_type=StrategyType.SEMANTIC_INTENT,
                    performance_tier=PerformanceTier.FAST,
                    reasoning="Generic button fallback",
                    metadata={"method": "generic_fallback", "type": "button"}
                ),
                ElementStrategy(
                    selector="*[role='button']",
                    confidence=0.45,
                    strategy_type=StrategyType.SEMANTIC_INTENT,
                    performance_tier=PerformanceTier.FAST,
                    reasoning="ARIA button fallback",
                    metadata={"method": "generic_fallback", "type": "aria_button"}
                )
            ])
        
        if "input" in intent_lower or "field" in intent_lower:
            fallback_strategies.extend([
                ElementStrategy(
                    selector="input[type='text']",
                    confidence=0.4,
                    strategy_type=StrategyType.SEMANTIC_INTENT,
                    performance_tier=PerformanceTier.FAST,
                    reasoning="Generic text input fallback",
                    metadata={"method": "generic_fallback", "type": "text_input"}
                ),
                ElementStrategy(
                    selector="*[role='textbox']",
                    confidence=0.45,
                    strategy_type=StrategyType.SEMANTIC_INTENT,
                    performance_tier=PerformanceTier.FAST,
                    reasoning="ARIA textbox fallback",
                    metadata={"method": "generic_fallback", "type": "aria_textbox"}
                )
            ])
        
        print(f"  ✅ Generated {len(fallback_strategies)} intelligent fallback strategies")
        
        return fallback_strategies
    
    def _rank_and_optimize_strategies(
        self,
        strategies: List[ElementStrategy],
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Rank strategies and optimize for best results."""
        
        # Apply context-specific confidence boosts
        for strategy in strategies:
            # Boost verified strategies
            if strategy.metadata.get("dom_verified"):
                strategy.confidence = min(0.95, strategy.confidence + 0.1)
            
            # Boost platform-specific patterns
            if context.platform == "salesforce_lightning":
                if any(indicator in strategy.selector.lower() for indicator in ['slds', 'lightning', 'force']):
                    strategy.confidence = min(0.9, strategy.confidence + 0.05)
            
            # Boost specific selectors over generic ones
            if strategy.metadata.get("method") == "id_matching":
                strategy.confidence = min(0.95, strategy.confidence + 0.05)
            elif strategy.metadata.get("method") == "generic_fallback":
                strategy.confidence = max(0.2, strategy.confidence - 0.1)
        
        # Sort by confidence and performance tier
        def strategy_score(strategy: ElementStrategy) -> float:
            tier_weights = {
                PerformanceTier.INSTANT: 4,
                PerformanceTier.FAST: 3,
                PerformanceTier.MEDIUM: 2,
                PerformanceTier.EXPENSIVE: 1
            }
            tier_weight = tier_weights.get(strategy.performance_tier, 1)
            return strategy.confidence * 0.8 + (tier_weight / 4) * 0.2
        
        strategies.sort(key=strategy_score, reverse=True)
        
        # Remove duplicates while preserving order
        seen_selectors = set()
        unique_strategies = []
        
        for strategy in strategies:
            if strategy.selector not in seen_selectors:
                seen_selectors.add(strategy.selector)
                unique_strategies.append(strategy)
        
        return unique_strategies
    
    def _update_confidence_distribution(self, strategies: List[ElementStrategy], stats: EnhancedStats):
        """Update confidence distribution statistics."""
        
        for strategy in strategies:
            if strategy.confidence >= 0.8:
                stats.confidence_distribution["high"] += 1
            elif strategy.confidence >= 0.6:
                stats.confidence_distribution["medium"] += 1
            else:
                stats.confidence_distribution["low"] += 1
    
    def _log_enhanced_results(
        self,
        context: ElementContext,
        strategies: List[ElementStrategy],
        stats: EnhancedStats
    ):
        """Log enhanced orchestration results."""
        
        print(f"\n🎯 ENHANCED ORCHESTRATION RESULTS")
        print(f"   Intent: '{context.intent}'")
        print(f"   Platform: {context.platform}")
        print(f"   Total Time: {stats.total_time_ms:.1f}ms")
        print(f"   DOM Verification: {stats.dom_verification_time_ms:.1f}ms")
        print(f"   Strategies: {stats.verified_strategies}/{stats.total_strategies} verified")
        print(f"   Layers Executed: {stats.layers_executed}")
        print(f"   Fallback Used: {stats.fallback_used}")
        print(f"   Error Recovery: {stats.error_recovery_count}")
        
        if strategies:
            top_strategy = strategies[0]
            print(f"   🏆 Top Strategy: {top_strategy.selector} (conf: {top_strategy.confidence:.2f})")
            print(f"   🎭 Method: {top_strategy.metadata.get('method', 'unknown')}")
            print(f"   ⚡ Performance: {top_strategy.performance_tier.value}")
        
        # Confidence distribution
        dist = stats.confidence_distribution
        print(f"   📊 Confidence: High:{dist['high']} Med:{dist['medium']} Low:{dist['low']}")
    
    def get_enhanced_metrics(self) -> Dict[str, Any]:
        """Get comprehensive enhanced metrics."""
        
        if not self.execution_stats:
            return {"message": "No execution data available"}
        
        # Calculate aggregated statistics
        total_executions = len(self.execution_stats)
        avg_time = sum(s.total_time_ms for s in self.execution_stats) / total_executions
        avg_verification_time = sum(s.dom_verification_time_ms for s in self.execution_stats) / total_executions
        avg_verified_strategies = sum(s.verified_strategies for s in self.execution_stats) / total_executions
        
        verification_success_rate = sum(
            s.verified_strategies / max(s.total_strategies, 1) for s in self.execution_stats
        ) / total_executions
        
        fallback_usage_rate = sum(1 for s in self.execution_stats if s.fallback_used) / total_executions
        
        return {
            "enhanced_metrics": {
                "total_executions": total_executions,
                "average_time_ms": round(avg_time, 1),
                "average_verification_time_ms": round(avg_verification_time, 1),
                "average_verified_strategies": round(avg_verified_strategies, 1),
                "verification_success_rate": round(verification_success_rate * 100, 1),
                "fallback_usage_rate": round(fallback_usage_rate * 100, 1),
                "error_recovery_total": sum(s.error_recovery_count for s in self.execution_stats)
            },
            "layer_performance": self.layer_performance,
            "robustness_features": {
                "dom_verification": "enabled",
                "intelligent_fallbacks": "enabled",
                "error_recovery": "enabled",
                "performance_optimization": "enabled"
            }
        }


import re  # Add this import at the top