"""
Layer 8: Timing Synchronization
===============================

This layer handles when elements appear and become interactive, solving the
dynamic loading problem that breaks traditional automation.

Patent Justification:
- Handles AJAX/lazy loading that traditional selectors can't manage
- Predicts optimal timing for element interactions
- Creates timing-aware selectors with intelligent wait strategies
- Monitors network patterns to predict element readiness

Example:
    Intent: "submit button" 
    Pattern: Appears after form validation (2-3 seconds)
    Strategy: wait_for_element_ready(selector, validation_complete_signal)
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from src.layers.base import BaseLayer
from src.models.element import ElementStrategy, ElementContext, StrategyType


@dataclass
class LoadingPattern:
    """Represents how an element loads on a page."""
    pattern_type: str  # immediate, lazy, ajax_dependent, progressive
    average_delay_ms: float
    triggers: List[str]  # Events that trigger loading
    indicators: List[str]  # Signs that loading is complete
    confidence: float


@dataclass
class TimingSelector:
    """A selector enhanced with timing information."""
    selector: str
    wait_strategy: str  # immediate, fixed_delay, condition_based, network_idle
    max_wait_ms: int
    conditions: List[str]  # Conditions to wait for
    confidence: float


class TimingSynchronizationLayer(BaseLayer):
    """
    Layer 8: Creates timing-aware selectors that know WHEN elements appear.
    
    This layer is critical for modern web applications where elements
    load dynamically via AJAX, lazy loading, or progressive enhancement.
    """
    
    def __init__(self):
        super().__init__(StrategyType.TIMING_SYNCHRONIZATION)
        
        # Common loading patterns by platform
        self.platform_patterns = {
            "salesforce_lightning": {
                "buttons": LoadingPattern(
                    pattern_type="ajax_dependent",
                    average_delay_ms=1500,
                    triggers=["component_load", "data_fetch"],
                    indicators=["slds-button", "lightning-button"],
                    confidence=0.85
                ),
                "modals": LoadingPattern(
                    pattern_type="progressive",
                    average_delay_ms=800,
                    triggers=["user_action"],
                    indicators=["slds-modal", "slds-backdrop"],
                    confidence=0.9
                )
            },
            "sap_fiori": {
                "tables": LoadingPattern(
                    pattern_type="lazy",
                    average_delay_ms=2000,
                    triggers=["scroll", "filter_change"],
                    indicators=["sapMTable", "sapUiTableComplete"],
                    confidence=0.8
                ),
                "buttons": LoadingPattern(
                    pattern_type="immediate",
                    average_delay_ms=300,
                    triggers=["page_load"],
                    indicators=["sapMBtn"],
                    confidence=0.95
                )
            },
            "workday": {
                "dropdowns": LoadingPattern(
                    pattern_type="ajax_dependent",
                    average_delay_ms=1200,
                    triggers=["field_focus", "data_request"],
                    indicators=["wd-Dropdown", "WDFF"],
                    confidence=0.75
                ),
                "forms": LoadingPattern(
                    pattern_type="progressive",
                    average_delay_ms=2500,
                    triggers=["navigation", "context_change"],
                    indicators=["gwt-Form", "wd-Form"],
                    confidence=0.8
                )
            }
        }
    
    async def generate_strategies(
        self, 
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """
        Generate timing-aware strategies for element identification.
        """
        strategies = []
        
        try:
            # Analyze current loading pattern
            loading_pattern = await self._analyze_loading_pattern(page, context)
            
            # Generate base selectors (from other layers would normally provide these)
            base_selectors = self._generate_base_selectors(context)
            
            # Create timing-enhanced strategies
            for base_selector in base_selectors:
                timing_strategies = self._create_timing_strategies(
                    base_selector, loading_pattern, context
                )
                strategies.extend(timing_strategies)
            
            # Add pattern-specific strategies
            pattern_strategies = self._create_pattern_specific_strategies(
                loading_pattern, context
            )
            strategies.extend(pattern_strategies)
            
            return strategies
            
        except Exception as e:
            print(f"Timing synchronization error: {str(e)}")
            # Return fallback timing strategies
            return self._fallback_timing_strategies(context)
    
    async def _analyze_loading_pattern(
        self, 
        page: Any, 
        context: ElementContext
    ) -> LoadingPattern:
        """Analyze how elements load on this page."""
        platform = context.platform.value if hasattr(context.platform, 'value') else str(context.platform)
        
        # Get platform-specific pattern
        if platform in self.platform_patterns:
            patterns = self.platform_patterns[platform]
            
            # Determine which pattern applies to this intent
            if "button" in context.intent.lower():
                return patterns.get("buttons", self._default_pattern())
            elif "table" in context.intent.lower() or "list" in context.intent.lower():
                return patterns.get("tables", self._default_pattern())
            elif "modal" in context.intent.lower() or "dialog" in context.intent.lower():
                return patterns.get("modals", self._default_pattern())
            elif "dropdown" in context.intent.lower() or "select" in context.intent.lower():
                return patterns.get("dropdowns", self._default_pattern())
            elif "form" in context.intent.lower() or context.page_type == "form":
                return patterns.get("forms", self._default_pattern())
        
        # Try to detect pattern dynamically
        return await self._detect_dynamic_pattern(page, context)
    
    async def _detect_dynamic_pattern(
        self, 
        page: Any, 
        context: ElementContext
    ) -> LoadingPattern:
        """Detect loading pattern by observing page behavior."""
        
        # Mock pattern detection (would analyze real page in production)
        if hasattr(page, 'evaluate'):  # Real browser page
            try:
                # Check for common loading indicators
                has_loading_indicators = await page.evaluate("""
                    () => {
                        return {
                            spinners: document.querySelectorAll('[class*="loading"], [class*="spinner"]').length,
                            ajax_activity: !!window.jQuery && jQuery.active > 0,
                            pending_requests: fetch.pending || 0
                        }
                    }
                """)
                
                if has_loading_indicators.get('spinners', 0) > 0:
                    return LoadingPattern(
                        pattern_type="ajax_dependent",
                        average_delay_ms=1500,
                        triggers=["ajax_complete"],
                        indicators=["no_spinner"],
                        confidence=0.7
                    )
            except:
                pass
        
        # Default pattern
        return self._default_pattern()
    
    def _default_pattern(self) -> LoadingPattern:
        """Default loading pattern when detection fails."""
        return LoadingPattern(
            pattern_type="immediate",
            average_delay_ms=500,
            triggers=["page_load"],
            indicators=["dom_ready"],
            confidence=0.6
        )
    
    def _generate_base_selectors(self, context: ElementContext) -> List[str]:
        """Generate base selectors that will be enhanced with timing."""
        intent_lower = context.intent.lower()
        selectors = []
        
        # Common semantic selectors
        if "button" in intent_lower or "submit" in intent_lower:
            selectors.extend([
                'button[type="submit"]',
                'input[type="submit"]',
                'button:contains("Submit")',
                '.btn-submit, .submit-btn'
            ])
        
        elif "search" in intent_lower:
            selectors.extend([
                'input[type="search"]',
                'input[placeholder*="search" i]',
                '[class*="search"] input',
                '#search, .search-field'
            ])
        
        elif "dropdown" in intent_lower or "select" in intent_lower:
            selectors.extend([
                'select',
                '[role="combobox"]',
                '.dropdown, [class*="dropdown"]',
                '[aria-haspopup="listbox"]'
            ])
        
        # Platform-specific enhancements
        platform = context.platform.value
        if platform == "salesforce_lightning":
            if "button" in intent_lower:
                selectors.extend([
                    'lightning-button',
                    '.slds-button',
                    '[data-aura-class*="button"]'
                ])
        elif platform == "sap_fiori":
            if "button" in intent_lower:
                selectors.extend([
                    '.sapMBtn',
                    '[data-sap-ui*="Button"]'
                ])
        elif platform == "workday":
            if "dropdown" in intent_lower:
                selectors.extend([
                    '[class*="wd-Dropdown"]',
                    '[data-automation-id*="dropdown"]'
                ])
        
        return selectors[:6]  # Limit to top 6 selectors
    
    def _create_timing_strategies(
        self, 
        base_selector: str, 
        pattern: LoadingPattern, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Create timing-enhanced versions of a base selector."""
        strategies = []
        
        # Strategy 1: Immediate attempt
        strategies.append(ElementStrategy(
            strategy_type=self.layer_type,
            selector=f"immediate:{base_selector}",
            confidence=0.7 if pattern.pattern_type == "immediate" else 0.4,
            metadata={
                "timing_strategy": "immediate",
                "base_selector": base_selector,
                "pattern_type": pattern.pattern_type,
                "max_wait_ms": 100
            }
        ))
        
        # Strategy 2: Fixed delay based on pattern
        if pattern.average_delay_ms > 100:
            strategies.append(ElementStrategy(
                strategy_type=self.layer_type,
                selector=f"wait:{int(pattern.average_delay_ms)}:{base_selector}",
                confidence=min(pattern.confidence * 0.9, 0.85),
                metadata={
                    "timing_strategy": "fixed_delay",
                    "base_selector": base_selector,
                    "delay_ms": int(pattern.average_delay_ms),
                    "pattern_confidence": pattern.confidence
                }
            ))
        
        # Strategy 3: Condition-based waiting
        if pattern.indicators:
            for indicator in pattern.indicators[:2]:  # Top 2 indicators
                strategies.append(ElementStrategy(
                    strategy_type=self.layer_type,
                    selector=f"condition:{indicator}:{base_selector}",
                    confidence=min(pattern.confidence * 0.85, 0.8),
                    metadata={
                        "timing_strategy": "condition_based",
                        "base_selector": base_selector,
                        "wait_condition": indicator,
                        "max_wait_ms": int(pattern.average_delay_ms * 2)
                    }
                ))
        
        # Strategy 4: Network idle waiting
        if pattern.pattern_type == "ajax_dependent":
            strategies.append(ElementStrategy(
                strategy_type=self.layer_type,
                selector=f"network_idle:{base_selector}",
                confidence=min(pattern.confidence * 0.8, 0.75),
                metadata={
                    "timing_strategy": "network_idle",
                    "base_selector": base_selector,
                    "idle_time_ms": 500,
                    "max_wait_ms": int(pattern.average_delay_ms * 3)
                }
            ))
        
        return strategies
    
    def _create_pattern_specific_strategies(
        self, 
        pattern: LoadingPattern, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Create strategies specific to the detected loading pattern."""
        strategies = []
        
        # Progressive loading strategy
        if pattern.pattern_type == "progressive":
            strategies.append(ElementStrategy(
                strategy_type=self.layer_type,
                selector=f"progressive_scan:{context.intent}",
                confidence=0.7,
                metadata={
                    "timing_strategy": "progressive_scan",
                    "scan_interval_ms": 200,
                    "max_scans": 10,
                    "intent": context.intent
                }
            ))
        
        # Lazy loading strategy
        elif pattern.pattern_type == "lazy":
            strategies.append(ElementStrategy(
                strategy_type=self.layer_type,
                selector=f"lazy_trigger:{context.intent}",
                confidence=0.65,
                metadata={
                    "timing_strategy": "lazy_trigger",
                    "trigger_actions": pattern.triggers,
                    "wait_after_trigger_ms": int(pattern.average_delay_ms),
                    "intent": context.intent
                }
            ))
        
        return strategies
    
    def _fallback_timing_strategies(self, context: ElementContext) -> List[ElementStrategy]:
        """Generate fallback timing strategies when analysis fails."""
        base_selectors = self._generate_base_selectors(context)[:3]  # Top 3
        strategies = []
        
        for selector in base_selectors:
            # Basic timing strategy
            strategies.append(ElementStrategy(
                strategy_type=self.layer_type,
                selector=f"wait:1000:{selector}",
                confidence=0.5,
                metadata={
                    "timing_strategy": "fallback_delay",
                    "base_selector": selector,
                    "delay_ms": 1000,
                    "fallback": True
                }
            ))
        
        return strategies