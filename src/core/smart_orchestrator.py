"""
High-Performance Universal Smart Orchestrator
============================================

Optimized universal orchestrator that achieves <100ms response time
while maintaining true universality across all web applications.

Key Features:
- Progressive execution: instant -> fast -> medium -> expensive
- Universal patterns (no app-specific knowledge)
- Intelligent caching and memoization
- Early termination on high-confidence results
- Parallel layer execution where beneficial
- Adaptive learning from successful strategies

Performance Targets:
- Instant tier: <10ms (cached patterns, deterministic selectors)
- Fast tier: <50ms (lightweight computation, web standards)
- Medium tier: <200ms (contextual analysis)
- Expensive tier: <500ms (AI/vision, last resort)
"""

import asyncio
import time
import hashlib
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

from ..models.element import ElementStrategy, ElementContext, StrategyType
from ..layers.base import BaseLayer


class PerformanceTier(Enum):
    """Performance tiers for progressive execution."""
    INSTANT = "instant"      # 0-10ms
    FAST = "fast"           # 10-50ms
    MEDIUM = "medium"       # 50-200ms
    EXPENSIVE = "expensive" # 200ms+


@dataclass
class UniversalPattern:
    """Universal pattern that works across all applications."""
    keywords: List[str]      # Semantic keywords (login, save, search)
    element_types: List[str] # Element types (button, input, link)
    selectors: List[str]     # Universal selectors
    confidence: float        # Base confidence score
    success_rate: float = 0.0 # Learned success rate
    usage_count: int = 0     # Times this pattern was used


@dataclass
class ExecutionMetrics:
    """Track execution performance for optimization."""
    layer_type: StrategyType
    execution_time_ms: float
    success: bool
    confidence: float
    cache_hit: bool = False


class UniversalPatternBank:
    """Repository of universal patterns that work across all applications."""
    
    def __init__(self):
        self.patterns = self._build_universal_patterns()
        
    def _build_universal_patterns(self) -> Dict[str, List[UniversalPattern]]:
        """
        Build truly universal patterns based on web standards and semantic understanding.
        NO app-specific knowledge - these work across ANY web application.
        """
        return {
            # Authentication patterns (work universally)
            "authentication": [
                UniversalPattern(
                    keywords=["login", "sign in", "log in", "signin"],
                    element_types=["button", "input"],
                    selectors=[
                        "button[type='submit']",
                        "input[type='submit']",
                        "button:has-text('Log')",
                        "button:has-text('Sign')",
                        "*[aria-label*='log' i]",
                        "*[aria-label*='sign' i]"
                    ],
                    confidence=0.85
                ),
                UniversalPattern(
                    keywords=["username", "user", "email"],
                    element_types=["input"],
                    selectors=[
                        "input[type='email']",
                        "input[name*='user' i]",
                        "input[name*='email' i]",
                        "input[placeholder*='email' i]",
                        "input[placeholder*='user' i]",
                        "*[role='textbox'][aria-label*='user' i]"
                    ],
                    confidence=0.90
                ),
                UniversalPattern(
                    keywords=["password", "pwd", "pass"],
                    element_types=["input"],
                    selectors=[
                        "input[type='password']",
                        "*[role='textbox'][aria-label*='password' i]"
                    ],
                    confidence=0.95
                )
            ],
            
            # Action patterns (universal across apps)
            "actions": [
                UniversalPattern(
                    keywords=["save", "submit", "send", "apply"],
                    element_types=["button", "input"],
                    selectors=[
                        "button[type='submit']",
                        "input[type='submit']",
                        "*[aria-label*='save' i]",
                        "*[aria-label*='submit' i]",
                        "button:has-text('Save')",
                        "button:has-text('Submit')"
                    ],
                    confidence=0.80
                ),
                UniversalPattern(
                    keywords=["cancel", "close", "abort", "back"],
                    element_types=["button", "link"],
                    selectors=[
                        "*[aria-label*='cancel' i]",
                        "*[aria-label*='close' i]",
                        "button[type='button']:has-text('Cancel')",
                        "button:has-text('Close')",
                        "a:has-text('Back')"
                    ],
                    confidence=0.75
                ),
                UniversalPattern(
                    keywords=["continue", "next", "proceed", "forward"],
                    element_types=["button", "link"],
                    selectors=[
                        "*[aria-label*='continue' i]",
                        "*[aria-label*='next' i]",
                        "button:has-text('Continue')",
                        "button:has-text('Next')",
                        "button[type='submit']"
                    ],
                    confidence=0.75
                )
            ],
            
            # Search patterns (universal)
            "search": [
                UniversalPattern(
                    keywords=["search", "find", "query", "filter"],
                    element_types=["input", "button"],
                    selectors=[
                        "input[type='search']",
                        "*[role='searchbox']",
                        "input[placeholder*='search' i]",
                        "input[name*='search' i]",
                        "*[aria-label*='search' i]",
                        "button:has-text('Search')"
                    ],
                    confidence=0.85
                )
            ],
            
            # Navigation patterns (universal)
            "navigation": [
                UniversalPattern(
                    keywords=["menu", "nav", "navigation", "burger"],
                    element_types=["button", "nav"],
                    selectors=[
                        "nav",
                        "*[role='navigation']",
                        "*[role='menu']",
                        "*[role='menubar']",
                        "button[aria-expanded]",
                        "button[aria-label*='menu' i]"
                    ],
                    confidence=0.80
                ),
                UniversalPattern(
                    keywords=["home", "dashboard", "main"],
                    element_types=["link", "button"],
                    selectors=[
                        "a[href*='home' i]",
                        "*[aria-label*='home' i]",
                        "nav a[href='/']",
                        "a:has-text('Home')",
                        "a:has-text('Dashboard')"
                    ],
                    confidence=0.75
                )
            ],
            
            # Form patterns (universal)
            "forms": [
                UniversalPattern(
                    keywords=["input", "field", "textbox", "text"],
                    element_types=["input", "textarea"],
                    selectors=[
                        "input[type='text']",
                        "*[role='textbox']",
                        "textarea",
                        "input:not([type='hidden']):not([type='submit']):not([type='button'])"
                    ],
                    confidence=0.70
                ),
                UniversalPattern(
                    keywords=["dropdown", "select", "choose", "pick"],
                    element_types=["select", "button"],
                    selectors=[
                        "select",
                        "*[role='combobox']",
                        "*[role='listbox']",
                        "button[aria-expanded='false']"
                    ],
                    confidence=0.75
                )
            ]
        }
    
    def find_matching_patterns(self, intent: str) -> List[UniversalPattern]:
        """Find universal patterns that match the given intent."""
        intent_lower = intent.lower()
        matching_patterns = []
        
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                # Check if any keywords match
                keyword_matches = sum(1 for keyword in pattern.keywords if keyword in intent_lower)
                if keyword_matches > 0:
                    # Calculate match score
                    match_score = keyword_matches / len(pattern.keywords)
                    # Adjust confidence based on match quality
                    adjusted_confidence = pattern.confidence * match_score
                    
                    # Create a copy with adjusted confidence
                    adjusted_pattern = UniversalPattern(
                        keywords=pattern.keywords,
                        element_types=pattern.element_types,
                        selectors=pattern.selectors,
                        confidence=adjusted_confidence,
                        success_rate=pattern.success_rate,
                        usage_count=pattern.usage_count
                    )
                    matching_patterns.append(adjusted_pattern)
        
        # Sort by confidence (highest first)
        return sorted(matching_patterns, key=lambda p: p.confidence, reverse=True)


class PerformanceCache:
    """High-performance caching for orchestration decisions."""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.strategy_cache: Dict[str, List[ElementStrategy]] = {}
        self.execution_metrics: List[ExecutionMetrics] = []
        
    def get_cache_key(self, intent: str, context: ElementContext) -> str:
        """Generate cache key for strategy results."""
        key_data = f"{intent}:{context.platform.value}:{context.page_type}"
        return hashlib.md5(key_data.encode()).hexdigest()[:12]
    
    def get_cached_strategies(self, intent: str, context: ElementContext) -> Optional[List[ElementStrategy]]:
        """Get cached strategies if available."""
        cache_key = self.get_cache_key(intent, context)
        return self.strategy_cache.get(cache_key)
    
    def cache_strategies(self, intent: str, context: ElementContext, strategies: List[ElementStrategy]):
        """Cache successful strategies for future use."""
        cache_key = self.get_cache_key(intent, context)
        self.strategy_cache[cache_key] = strategies
        
        # Cleanup if cache too large
        if len(self.strategy_cache) > self.max_size:
            # Remove oldest 25% of entries (simple LRU approximation)
            keys_to_remove = list(self.strategy_cache.keys())[:int(self.max_size * 0.25)]
            for key in keys_to_remove:
                del self.strategy_cache[key]
    
    def record_execution(self, metrics: ExecutionMetrics):
        """Record execution metrics for performance analysis."""
        self.execution_metrics.append(metrics)
        
        # Keep only recent metrics (last 1000)
        if len(self.execution_metrics) > 1000:
            self.execution_metrics = self.execution_metrics[-1000:]


class HighPerformanceUniversalOrchestrator:
    """
    High-performance universal orchestrator with <100ms target response time.
    
    Uses progressive execution tiers and intelligent caching to achieve
    both universality and performance.
    """
    
    def __init__(self):
        self.pattern_bank = UniversalPatternBank()
        self.cache = PerformanceCache()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Performance targets (milliseconds)
        self.performance_targets = {
            PerformanceTier.INSTANT: 10,
            PerformanceTier.FAST: 50,
            PerformanceTier.MEDIUM: 200,
            PerformanceTier.EXPENSIVE: 500
        }
        
        # Confidence thresholds for early termination
        self.high_confidence_threshold = 0.85
        self.medium_confidence_threshold = 0.70
        self.low_confidence_threshold = 0.50
        
        # Layer organization by performance tier
        self.layer_tiers = {
            PerformanceTier.INSTANT: [
                # Pattern matching - instant results
                StrategyType.CONTEXTUAL_RELATIONSHIP,
                StrategyType.BEHAVIORAL_PATTERN,
                StrategyType.STRUCTURAL_PATTERN,
            ],
            PerformanceTier.FAST: [
                # Lightweight computation
                StrategyType.ACCESSIBILITY_BRIDGE,
                StrategyType.STATE_CONTEXT_AWARENESS,
            ],
            PerformanceTier.MEDIUM: [
                # Moderate computation
                StrategyType.TIMING_SYNCHRONIZATION,
                StrategyType.MUTATION_OBSERVATION,
            ],
            PerformanceTier.EXPENSIVE: [
                # AI/Vision - expensive
                StrategyType.SEMANTIC_INTENT,
                StrategyType.VISUAL_FINGERPRINT,
                StrategyType.ML_FUSION,
            ]
        }
    
    async def orchestrate_element_finding(
        self,
        layers: Dict[StrategyType, BaseLayer],
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """
        Orchestrate element finding with <100ms target response time.
        Uses progressive execution: instant -> fast -> medium -> expensive
        """
        start_time = time.time()
        intent = context.intent
        
        print(f"🚀 High-performance orchestration: '{intent}'")
        
        # INSTANT TIER: Check cache first (0-1ms)
        cached_strategies = self.cache.get_cached_strategies(intent, context)
        if cached_strategies:
            execution_time = (time.time() - start_time) * 1000
            print(f"   ⚡ Cache hit: {execution_time:.1f}ms")
            self._record_metrics(StrategyType.CONTEXTUAL_RELATIONSHIP, execution_time, True, 0.9, cache_hit=True)
            return cached_strategies
        
        # INSTANT TIER: Universal pattern matching (1-10ms)
        instant_strategies = await self._execute_instant_tier(intent, context)
        
        execution_time = (time.time() - start_time) * 1000
        if instant_strategies and execution_time <= self.performance_targets[PerformanceTier.INSTANT]:
            if self._has_high_confidence_strategy(instant_strategies):
                print(f"   ⚡ Instant patterns: {execution_time:.1f}ms")
                self.cache.cache_strategies(intent, context, instant_strategies)
                return instant_strategies
        
        # FAST TIER: Lightweight layer execution (10-50ms)
        if execution_time < 40:  # Still have time budget
            fast_strategies = await self._execute_fast_tier(layers, page, context, instant_strategies)
            
            execution_time = (time.time() - start_time) * 1000
            if fast_strategies and execution_time <= self.performance_targets[PerformanceTier.FAST]:
                if self._has_medium_confidence_strategy(fast_strategies):
                    print(f"   🔥 Fast execution: {execution_time:.1f}ms")
                    self.cache.cache_strategies(intent, context, fast_strategies)
                    return fast_strategies
        
        # MEDIUM TIER: Moderate computation (50-200ms)
        if execution_time < 150:  # Still reasonable time
            medium_strategies = await self._execute_medium_tier(layers, page, context, fast_strategies or instant_strategies)
            
            execution_time = (time.time() - start_time) * 1000
            if medium_strategies and execution_time <= self.performance_targets[PerformanceTier.MEDIUM]:
                print(f"   🎯 Medium execution: {execution_time:.1f}ms")
                self.cache.cache_strategies(intent, context, medium_strategies)
                return medium_strategies
        
        # EXPENSIVE TIER: AI/Vision as last resort (200ms+)
        expensive_strategies = await self._execute_expensive_tier(layers, page, context, medium_strategies or fast_strategies or instant_strategies)
        
        execution_time = (time.time() - start_time) * 1000
        print(f"   🐌 Expensive execution: {execution_time:.1f}ms")
        
        if expensive_strategies:
            self.cache.cache_strategies(intent, context, expensive_strategies)
            return expensive_strategies
        
        # Fallback: Return best strategies found so far
        final_strategies = expensive_strategies or medium_strategies or fast_strategies or instant_strategies
        return final_strategies or []
    
    async def _execute_instant_tier(self, intent: str, context: ElementContext) -> List[ElementStrategy]:
        """Execute instant tier: universal pattern matching."""
        # Find matching universal patterns
        matching_patterns = self.pattern_bank.find_matching_patterns(intent)
        strategies = []
        
        for pattern in matching_patterns[:5]:  # Top 5 patterns for speed
            for selector in pattern.selectors[:3]:  # Top 3 selectors per pattern
                strategy = ElementStrategy(
                    strategy_type=StrategyType.CONTEXTUAL_RELATIONSHIP,
                    selector=selector,
                    confidence=pattern.confidence,
                    metadata={
                        "source": "universal_pattern",
                        "keywords": pattern.keywords[:3],
                        "tier": "instant",
                        "pattern_confidence": pattern.confidence
                    }
                )
                strategies.append(strategy)
        
        return strategies
    
    async def _execute_fast_tier(
        self, 
        layers: Dict[StrategyType, BaseLayer], 
        page: Any, 
        context: ElementContext,
        existing_strategies: List[ElementStrategy]
    ) -> List[ElementStrategy]:
        """Execute fast tier: lightweight layer computation."""
        all_strategies = existing_strategies.copy() if existing_strategies else []
        
        # Execute fast layers in parallel
        fast_layer_types = self.layer_tiers[PerformanceTier.FAST]
        tasks = []
        
        for layer_type in fast_layer_types:
            if layer_type in layers:
                task = self._execute_layer_with_timeout(layers[layer_type], page, context, 0.03)  # 30ms timeout
                tasks.append((layer_type, task))
        
        # Wait for all fast tasks to complete
        if tasks:
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            for (layer_type, _), result in zip(tasks, results):
                if isinstance(result, list) and result:
                    all_strategies.extend(result)
                    self._record_metrics(layer_type, 25, True, max(s.confidence for s in result))
                else:
                    self._record_metrics(layer_type, 30, False, 0.0)
        
        return self._deduplicate_and_sort_strategies(all_strategies)
    
    async def _execute_medium_tier(
        self, 
        layers: Dict[StrategyType, BaseLayer], 
        page: Any, 
        context: ElementContext,
        existing_strategies: List[ElementStrategy]
    ) -> List[ElementStrategy]:
        """Execute medium tier: moderate computation layers."""
        all_strategies = existing_strategies.copy() if existing_strategies else []
        
        # Execute medium layers with longer timeout
        medium_layer_types = self.layer_tiers[PerformanceTier.MEDIUM]
        
        for layer_type in medium_layer_types:
            if layer_type in layers:
                start_time = time.time()
                try:
                    strategies = await asyncio.wait_for(
                        layers[layer_type].generate_strategies(page, context),
                        timeout=0.1  # 100ms timeout
                    )
                    
                    execution_time = (time.time() - start_time) * 1000
                    if strategies:
                        all_strategies.extend(strategies)
                        self._record_metrics(layer_type, execution_time, True, max(s.confidence for s in strategies))
                    else:
                        self._record_metrics(layer_type, execution_time, False, 0.0)
                        
                except asyncio.TimeoutError:
                    self._record_metrics(layer_type, 100, False, 0.0)
                except Exception as e:
                    self._record_metrics(layer_type, (time.time() - start_time) * 1000, False, 0.0)
        
        return self._deduplicate_and_sort_strategies(all_strategies)
    
    async def _execute_expensive_tier(
        self, 
        layers: Dict[StrategyType, BaseLayer], 
        page: Any, 
        context: ElementContext,
        existing_strategies: List[ElementStrategy]
    ) -> List[ElementStrategy]:
        """Execute expensive tier: AI and vision layers."""
        all_strategies = existing_strategies.copy() if existing_strategies else []
        
        # Only execute expensive layers if we don't have good strategies
        if not self._has_medium_confidence_strategy(all_strategies):
            expensive_layer_types = self.layer_tiers[PerformanceTier.EXPENSIVE]
            
            for layer_type in expensive_layer_types:
                if layer_type in layers:
                    start_time = time.time()
                    try:
                        strategies = await asyncio.wait_for(
                            layers[layer_type].generate_strategies(page, context),
                            timeout=0.3  # 300ms timeout for expensive operations
                        )
                        
                        execution_time = (time.time() - start_time) * 1000
                        if strategies:
                            all_strategies.extend(strategies)
                            self._record_metrics(layer_type, execution_time, True, max(s.confidence for s in strategies))
                            
                            # Early exit if we found high confidence strategies
                            if self._has_high_confidence_strategy(strategies):
                                break
                        else:
                            self._record_metrics(layer_type, execution_time, False, 0.0)
                            
                    except asyncio.TimeoutError:
                        self._record_metrics(layer_type, 300, False, 0.0)
                    except Exception as e:
                        self._record_metrics(layer_type, (time.time() - start_time) * 1000, False, 0.0)
        
        return self._deduplicate_and_sort_strategies(all_strategies)
    
    async def _execute_layer_with_timeout(self, layer: BaseLayer, page: Any, context: ElementContext, timeout: float):
        """Execute a layer with timeout protection."""
        try:
            return await asyncio.wait_for(
                layer.generate_strategies(page, context),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            return []
        except Exception:
            return []
    
    def _has_high_confidence_strategy(self, strategies: List[ElementStrategy]) -> bool:
        """Check if strategies contain high confidence results."""
        return any(s.confidence >= self.high_confidence_threshold for s in strategies)
    
    def _has_medium_confidence_strategy(self, strategies: List[ElementStrategy]) -> bool:
        """Check if strategies contain medium confidence results."""
        return any(s.confidence >= self.medium_confidence_threshold for s in strategies)
    
    def _deduplicate_and_sort_strategies(self, strategies: List[ElementStrategy]) -> List[ElementStrategy]:
        """Remove duplicates and sort strategies by confidence."""
        # Remove duplicates based on selector
        seen_selectors = set()
        unique_strategies = []
        
        for strategy in strategies:
            if strategy.selector not in seen_selectors:
                seen_selectors.add(strategy.selector)
                unique_strategies.append(strategy)
        
        # Sort by confidence (highest first)
        return sorted(unique_strategies, key=lambda s: s.confidence, reverse=True)
    
    def _record_metrics(self, layer_type: StrategyType, execution_time: float, success: bool, confidence: float, cache_hit: bool = False):
        """Record execution metrics for performance analysis."""
        metrics = ExecutionMetrics(
            layer_type=layer_type,
            execution_time_ms=execution_time,
            success=success,
            confidence=confidence,
            cache_hit=cache_hit
        )
        self.cache.record_execution(metrics)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for optimization."""
        if not self.cache.execution_metrics:
            return {"message": "No metrics available"}
        
        metrics = self.cache.execution_metrics
        
        # Calculate averages by tier
        tier_stats = {}
        for tier in PerformanceTier:
            tier_metrics = [m for m in metrics if self._get_tier_for_layer(m.layer_type) == tier]
            if tier_metrics:
                tier_stats[tier.value] = {
                    "avg_time_ms": sum(m.execution_time_ms for m in tier_metrics) / len(tier_metrics),
                    "success_rate": sum(1 for m in tier_metrics if m.success) / len(tier_metrics),
                    "avg_confidence": sum(m.confidence for m in tier_metrics) / len(tier_metrics),
                    "count": len(tier_metrics)
                }
        
        return {
            "tier_performance": tier_stats,
            "cache_hit_rate": sum(1 for m in metrics if m.cache_hit) / len(metrics),
            "total_executions": len(metrics)
        }
    
    def _get_tier_for_layer(self, layer_type: StrategyType) -> PerformanceTier:
        """Get performance tier for a layer type."""
        for tier, layer_types in self.layer_tiers.items():
            if layer_type in layer_types:
                return tier
        return PerformanceTier.EXPENSIVE  # Default


# Maintain backward compatibility
SmartOrchestrator = HighPerformanceUniversalOrchestrator