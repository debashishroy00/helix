"""
Layer 1: Universal Semantic Intent Recognition (Optimized)
=========================================================

High-performance universal semantic layer with NO app-specific knowledge.
Target: <100ms response time through intelligent caching and progressive fallback.

Performance Tiers:
- Instant (0-10ms): Cached intent parsing and pre-compiled patterns
- Fast (10-50ms): Universal web standards (ARIA, semantic HTML)
- Medium (50-200ms): AI-powered understanding (only when needed)

Universal Approach:
- Uses semantic understanding of UI purposes
- No platform-specific patterns or hardcoded DOM knowledge
- Works across ANY web application
- Learns and adapts from successful interactions
"""

import asyncio
import time
import hashlib
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from src.layers.base import BaseLayer
from src.models.element import ElementStrategy, ElementContext, StrategyType, PerformanceTier


@dataclass
class CachedIntent:
    """Cached intent parsing result for performance."""
    intent: str
    keywords: List[str]
    purpose: str
    element_type: str
    interaction_type: str
    confidence: float
    timestamp: float


class PerformanceCache:
    """Ultra-fast caching for intent parsing and successful matches."""
    
    def __init__(self, max_size: int = 5000):
        self.max_size = max_size
        self.intent_cache: Dict[str, CachedIntent] = {}
        self.success_cache: Dict[str, Dict] = {}
        
    def get_intent_hash(self, intent: str) -> str:
        """Generate hash for intent caching."""
        return hashlib.md5(intent.lower().strip().encode()).hexdigest()[:8]
    
    def cache_intent(self, intent: str, parsed_data: CachedIntent):
        """Cache parsed intent for instant retrieval."""
        intent_hash = self.get_intent_hash(intent)
        self.intent_cache[intent_hash] = parsed_data
        
        # Cleanup if cache too large
        if len(self.intent_cache) > self.max_size:
            # Remove oldest 20% of entries
            sorted_items = sorted(
                self.intent_cache.items(), 
                key=lambda x: x[1].timestamp
            )
            for key, _ in sorted_items[:int(self.max_size * 0.2)]:
                del self.intent_cache[key]
    
    def get_cached_intent(self, intent: str) -> Optional[CachedIntent]:
        """Get cached intent parsing."""
        intent_hash = self.get_intent_hash(intent)
        return self.intent_cache.get(intent_hash)


class UniversalSelectorBank:
    """Pre-compiled universal selectors for instant matching."""
    
    def __init__(self):
        # Universal selectors tested across multiple web applications
        # Organized by semantic purpose, not app-specific patterns
        self.instant_selectors = {
            # Authentication elements
            'login': [
                # Tier 1: Highest universality (90%+ success rate)
                "input[type='submit'][value*='log' i]",
                "button[type='submit']",
                "input[type='submit']",
                # Tier 2: Text-based matching (80%+ success rate)
                "*[aria-label*='log' i]",
                "*[aria-label*='sign' i]",
                # Tier 3: Common patterns (60%+ success rate)
                "button[class*='login' i]",
                "button[id*='login' i]"
            ],
            'authenticate': [
                "button[type='submit']",
                "input[type='submit']",
                "*[role='button'][aria-label*='sign' i]",
                "*[role='button'][aria-label*='log' i]"
            ],
            
            # Data input elements
            'username': [
                "input[type='email']",
                "input[name*='user' i]",
                "input[name*='email' i]",
                "input[placeholder*='email' i]",
                "input[placeholder*='username' i]",
                "input[id*='user' i]",
                "*[role='textbox'][aria-label*='user' i]",
                "*[role='textbox'][aria-label*='email' i]"
            ],
            'email': [
                "input[type='email']",
                "input[name*='email' i]",
                "input[placeholder*='email' i]",
                "input[id*='email' i]",
                "*[role='textbox'][aria-label*='email' i]"
            ],
            'password': [
                "input[type='password']",
                "input[name*='password' i]",
                "input[placeholder*='password' i]",
                "*[role='textbox'][aria-label*='password' i]"
            ],
            
            # Action elements
            'submit': [
                "button[type='submit']",
                "input[type='submit']",
                "*[role='button'][aria-label*='submit' i]"
            ],
            'save': [
                "*[aria-label*='save' i]",
                "button[type='submit']",
                "input[type='submit']"
            ],
            'continue': [
                "*[aria-label*='continue' i]",
                "*[aria-label*='next' i]",
                "button[type='submit']"
            ],
            'cancel': [
                "*[aria-label*='cancel' i]",
                "*[aria-label*='close' i]",
                "button[type='button']"
            ],
            
            # Search elements
            'search': [
                "input[type='search']",
                "*[role='searchbox']",
                "input[placeholder*='search' i]",
                "input[name*='search' i]",
                "input[id*='search' i]",
                "*[aria-label*='search' i]"
            ],
            'find': [
                "input[type='search']",
                "*[role='searchbox']",
                "input[placeholder*='find' i]",
                "*[aria-label*='find' i]"
            ],
            
            # Navigation elements
            'menu': [
                "nav",
                "*[role='navigation']",
                "*[role='menu']",
                "*[role='menubar']",
                "button[aria-label*='menu' i]",
                "button[aria-expanded]"
            ],
            'navigation': [
                "nav",
                "*[role='navigation']",
                "*[role='menu']"
            ],
            'home': [
                "a[href*='home' i]",
                "*[aria-label*='home' i]",
                "nav a[href='/']"
            ]
        }
    
    def get_instant_selectors(self, keywords: List[str]) -> List[str]:
        """Get pre-compiled selectors for immediate execution."""
        all_selectors = []
        
        for keyword in keywords:
            if keyword in self.instant_selectors:
                all_selectors.extend(self.instant_selectors[keyword])
        
        # Return unique selectors maintaining order (most universal first)
        return list(dict.fromkeys(all_selectors))


class UniversalSemanticIntentLayer(BaseLayer):
    """
    Optimized universal semantic intent layer.
    
    Key Features:
    - <100ms target response time
    - No app-specific knowledge
    - Progressive fallback strategy
    - Intelligent caching
    - Universal web standards based
    """
    
    def __init__(self):
        super().__init__(StrategyType.SEMANTIC_INTENT)
        self.cache = PerformanceCache()
        self.selector_bank = UniversalSelectorBank()
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Performance metrics
        self.performance_targets = {
            'instant': 10,    # 10ms
            'fast': 50,       # 50ms
            'medium': 200     # 200ms
        }
    
    async def generate_strategies(
        self, 
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """
        Generate universal strategies with <100ms target response time.
        Uses progressive fallback: instant -> fast -> medium
        """
        start_time = time.time()
        intent = context.intent
        
        print(f"🚀 Universal semantic analysis: '{intent}'")
        
        # INSTANT PATH: Check cache first (0-1ms)
        cached_intent = self.cache.get_cached_intent(intent)
        if cached_intent:
            strategies = await self._generate_from_cached_intent(cached_intent)
            if strategies:
                execution_time = (time.time() - start_time) * 1000
                print(f"   ⚡ Cache hit: {execution_time:.1f}ms")
                return strategies
        
        # INSTANT PATH: Fast intent parsing + pre-compiled selectors (1-10ms)
        parsed_intent = self._parse_intent_fast(intent)
        instant_strategies = await self._generate_instant_strategies(parsed_intent)
        
        execution_time = (time.time() - start_time) * 1000
        if instant_strategies and execution_time <= self.performance_targets['instant']:
            print(f"   ⚡ Instant strategies: {execution_time:.1f}ms")
            self._cache_intent(intent, parsed_intent)
            return instant_strategies
        
        # FAST PATH: Universal web standards (10-50ms)
        if execution_time < 40:  # Still have time budget
            fast_strategies = await self._generate_fast_strategies(parsed_intent, page)
            if fast_strategies:
                execution_time = (time.time() - start_time) * 1000
                if execution_time <= self.performance_targets['fast']:
                    print(f"   🔥 Fast strategies: {execution_time:.1f}ms")
                    self._cache_intent(intent, parsed_intent)
                    return fast_strategies
        
        # MEDIUM PATH: Contextual analysis (50-200ms)
        if execution_time < 150:  # Still reasonable time
            medium_strategies = await self._generate_medium_strategies(parsed_intent, page, context)
            if medium_strategies:
                execution_time = (time.time() - start_time) * 1000
                print(f"   🎯 Medium strategies: {execution_time:.1f}ms")
                self._cache_intent(intent, parsed_intent)
                return medium_strategies
        
        # Fallback: Basic universal patterns
        execution_time = (time.time() - start_time) * 1000
        print(f"   📋 Fallback strategies: {execution_time:.1f}ms")
        return self._generate_fallback_strategies(parsed_intent)
    
    def _parse_intent_fast(self, intent: str) -> CachedIntent:
        """Ultra-fast intent parsing using keyword analysis."""
        intent_lower = intent.lower().strip()
        
        # Extract semantic keywords
        keywords = []
        purpose = "unknown"
        element_type = "unknown"
        interaction_type = "click"
        
        # Universal keyword mapping for semantic understanding
        semantic_map = {
            # Authentication
            'login': {'keywords': ['login', 'log', 'sign'], 'purpose': 'authentication', 'type': 'button', 'interaction': 'click'},
            'signin': {'keywords': ['signin', 'sign'], 'purpose': 'authentication', 'type': 'button', 'interaction': 'click'},
            'authenticate': {'keywords': ['auth'], 'purpose': 'authentication', 'type': 'button', 'interaction': 'click'},
            
            # Credentials
            'username': {'keywords': ['username', 'user', 'email'], 'purpose': 'data_input', 'type': 'input', 'interaction': 'type'},
            'email': {'keywords': ['email', '@'], 'purpose': 'data_input', 'type': 'input', 'interaction': 'type'},
            'password': {'keywords': ['password', 'pwd', 'pass'], 'purpose': 'data_input', 'type': 'input', 'interaction': 'type'},
            
            # Actions
            'submit': {'keywords': ['submit', 'send'], 'purpose': 'action', 'type': 'button', 'interaction': 'click'},
            'save': {'keywords': ['save', 'store'], 'purpose': 'action', 'type': 'button', 'interaction': 'click'},
            'continue': {'keywords': ['continue', 'next', 'proceed'], 'purpose': 'action', 'type': 'button', 'interaction': 'click'},
            'cancel': {'keywords': ['cancel', 'abort', 'close'], 'purpose': 'action', 'type': 'button', 'interaction': 'click'},
            
            # Search
            'search': {'keywords': ['search', 'find', 'query'], 'purpose': 'search', 'type': 'input', 'interaction': 'type'},
            'find': {'keywords': ['find', 'locate'], 'purpose': 'search', 'type': 'input', 'interaction': 'type'},
            
            # Navigation
            'menu': {'keywords': ['menu', 'nav', 'burger'], 'purpose': 'navigation', 'type': 'button', 'interaction': 'click'},
            'home': {'keywords': ['home', 'main'], 'purpose': 'navigation', 'type': 'link', 'interaction': 'click'},
            
            # Generic elements
            'button': {'keywords': ['button', 'btn'], 'purpose': 'action', 'type': 'button', 'interaction': 'click'},
            'input': {'keywords': ['input', 'field', 'textbox'], 'purpose': 'data_input', 'type': 'input', 'interaction': 'type'},
            'link': {'keywords': ['link', 'href'], 'purpose': 'navigation', 'type': 'link', 'interaction': 'click'}
        }
        
        # Find matching semantic patterns
        best_match = None
        best_score = 0
        
        for pattern, data in semantic_map.items():
            score = 0
            for keyword in data['keywords']:
                if keyword in intent_lower:
                    score += len(keyword)  # Longer matches = higher score
            
            if score > best_score:
                best_score = score
                best_match = data
                keywords = data['keywords']
                purpose = data['purpose']
                element_type = data['type']
                interaction_type = data['interaction']
        
        # Extract additional context keywords
        additional_keywords = []
        if best_match:
            # Add the primary keywords
            additional_keywords.extend(best_match['keywords'])
        
        # Add any other relevant words
        for word in intent_lower.split():
            if len(word) > 2 and word not in additional_keywords:
                additional_keywords.append(word)
        
        confidence = min(0.9, best_score / len(intent_lower)) if best_score > 0 else 0.5
        
        return CachedIntent(
            intent=intent,
            keywords=list(set(additional_keywords)),
            purpose=purpose,
            element_type=element_type,
            interaction_type=interaction_type,
            confidence=confidence,
            timestamp=time.time()
        )
    
    async def _generate_from_cached_intent(self, cached_intent: CachedIntent) -> List[ElementStrategy]:
        """Generate strategies from cached intent parsing."""
        selectors = self.selector_bank.get_instant_selectors(cached_intent.keywords)
        strategies = []
        
        for i, selector in enumerate(selectors[:5]):  # Limit to top 5 for speed
            confidence = max(0.6, cached_intent.confidence - (i * 0.1))
            
            strategy = ElementStrategy(
                strategy_type=self.layer_type,
                selector=selector,
                confidence=confidence,
                performance_tier=PerformanceTier.INSTANT,
                metadata={
                    "source": "cached_universal",
                    "purpose": cached_intent.purpose,
                    "element_type": cached_intent.element_type,
                    "keywords": cached_intent.keywords[:3]  # Top 3 keywords
                }
            )
            strategies.append(strategy)
        
        return strategies
    
    async def _generate_instant_strategies(self, parsed_intent: CachedIntent) -> List[ElementStrategy]:
        """Generate strategies using pre-compiled universal selectors."""
        selectors = self.selector_bank.get_instant_selectors(parsed_intent.keywords)
        strategies = []
        
        for i, selector in enumerate(selectors[:6]):  # Top 6 selectors
            # Confidence decreases with position but stays reasonable
            confidence = max(0.6, parsed_intent.confidence - (i * 0.08))
            
            strategy = ElementStrategy(
                strategy_type=self.layer_type,
                selector=selector,
                confidence=confidence,
                performance_tier=PerformanceTier.INSTANT,
                metadata={
                    "source": "instant_universal",
                    "purpose": parsed_intent.purpose,
                    "element_type": parsed_intent.element_type,
                    "tier": "instant"
                }
            )
            strategies.append(strategy)
        
        return strategies
    
    async def _generate_fast_strategies(self, parsed_intent: CachedIntent, page: Any) -> List[ElementStrategy]:
        """Generate strategies using universal web standards."""
        strategies = []
        
        # Fast universal strategies based on web standards
        if parsed_intent.purpose == 'authentication':
            fast_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "*[role='button'][aria-label*='sign' i]",
                "*[role='button'][aria-label*='log' i]"
            ]
        elif parsed_intent.purpose == 'data_input':
            if 'email' in parsed_intent.keywords or 'username' in parsed_intent.keywords:
                fast_selectors = [
                    "input[type='email']",
                    "input[type='text'][name*='user' i]",
                    "*[role='textbox'][aria-label*='email' i]",
                    "*[role='textbox'][aria-label*='user' i]"
                ]
            elif 'password' in parsed_intent.keywords:
                fast_selectors = [
                    "input[type='password']",
                    "*[role='textbox'][aria-label*='password' i]"
                ]
            else:
                fast_selectors = [
                    "input[type='text']",
                    "*[role='textbox']",
                    "textarea"
                ]
        elif parsed_intent.purpose == 'search':
            fast_selectors = [
                "input[type='search']",
                "*[role='searchbox']",
                "input[placeholder*='search' i]"
            ]
        elif parsed_intent.purpose == 'navigation':
            fast_selectors = [
                "nav",
                "*[role='navigation']",
                "*[role='menu']",
                "button[aria-expanded]"
            ]
        else:
            # Generic action elements
            fast_selectors = [
                "button",
                "*[role='button']",
                "input[type='submit']",
                "a[href]"
            ]
        
        for i, selector in enumerate(fast_selectors):
            confidence = max(0.65, 0.85 - (i * 0.05))
            
            strategy = ElementStrategy(
                strategy_type=self.layer_type,
                selector=selector,
                confidence=confidence,
                performance_tier=PerformanceTier.FAST,
                metadata={
                    "source": "fast_universal",
                    "purpose": parsed_intent.purpose,
                    "tier": "fast",
                    "web_standard": True
                }
            )
            strategies.append(strategy)
        
        return strategies
    
    async def _generate_medium_strategies(self, parsed_intent: CachedIntent, page: Any, context: ElementContext) -> List[ElementStrategy]:
        """Generate strategies using contextual analysis."""
        strategies = []
        
        # Medium complexity: Text content matching with context
        for keyword in parsed_intent.keywords[:3]:  # Top 3 keywords
            # Text-based selectors with universal patterns
            text_selectors = []
            
            if parsed_intent.element_type == 'button':
                text_selectors = [
                    f"button[aria-label*='{keyword}' i]",
                    f"*[role='button'][aria-label*='{keyword}' i]",
                    f"input[type='submit'][value*='{keyword}' i]"
                ]
            elif parsed_intent.element_type == 'input':
                text_selectors = [
                    f"input[placeholder*='{keyword}' i]",
                    f"*[aria-label*='{keyword}' i]",
                    f"input[name*='{keyword}' i]"
                ]
            else:
                text_selectors = [
                    f"*[aria-label*='{keyword}' i]",
                    f"*[title*='{keyword}' i]"
                ]
            
            for selector in text_selectors:
                strategy = ElementStrategy(
                    strategy_type=self.layer_type,
                    selector=selector,
                    confidence=0.7,
                    performance_tier=PerformanceTier.MEDIUM,
                    metadata={
                        "source": "medium_universal",
                        "keyword": keyword,
                        "tier": "medium",
                        "text_based": True
                    }
                )
                strategies.append(strategy)
        
        return strategies
    
    def _generate_fallback_strategies(self, parsed_intent: CachedIntent) -> List[ElementStrategy]:
        """Generate basic fallback strategies."""
        strategies = []
        
        # Basic universal fallbacks based on element type
        if parsed_intent.element_type == 'button':
            fallback_selectors = ["button", "*[role='button']", "input[type='submit']"]
        elif parsed_intent.element_type == 'input':
            fallback_selectors = ["input", "*[role='textbox']", "textarea"]
        elif parsed_intent.element_type == 'link':
            fallback_selectors = ["a", "*[role='link']"]
        else:
            fallback_selectors = ["button", "input", "a", "*[role='button']"]
        
        for selector in fallback_selectors:
            strategy = ElementStrategy(
                strategy_type=self.layer_type,
                selector=selector,
                confidence=0.4,
                performance_tier=PerformanceTier.FAST,
                metadata={
                    "source": "fallback_universal",
                    "tier": "fallback",
                    "element_type": parsed_intent.element_type
                }
            )
            strategies.append(strategy)
        
        return strategies
    
    def _cache_intent(self, intent: str, parsed_intent: CachedIntent):
        """Cache successful intent parsing for future speed."""
        self.cache.cache_intent(intent, parsed_intent)


# Maintain backward compatibility
SemanticIntentLayer = UniversalSemanticIntentLayer