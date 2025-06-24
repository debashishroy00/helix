"""
Layer 7: Mutation Observation
=============================
Watches DOM changes and adapts selectors accordingly using MutationObserver patterns.
This layer handles dynamic applications where elements appear, disappear, or change
after the initial page load.

Critical for modern SPAs and applications with heavy JavaScript manipulation.
"""

import asyncio
import json
from typing import List, Optional, Any, Dict, Set
from datetime import datetime, timedelta
from src.models.element import ElementStrategy, ElementContext, StrategyType, PerformanceTier
from src.layers.base import BaseLayer


class MutationObservationLayer(BaseLayer):
    """
    Layer 7: Observes DOM mutations and adapts element finding strategies.
    
    Tracks element changes, additions, and removals to maintain reliable
    selectors in dynamic applications.
    """
    
    def __init__(self):
        super().__init__(StrategyType.MUTATION_OBSERVATION)
        
        # Cache for observed mutations
        self.mutation_cache = {}
        
        # Patterns for different types of dynamic content
        self.dynamic_patterns = {
            "lazy_loaded": {
                "indicators": ["loading", "skeleton", "placeholder", "spinner"],
                "wait_time": 3.0,
                "confidence_boost": 0.15
            },
            "ajax_content": {
                "indicators": ["ajax", "xhr", "fetch", "dynamic"],
                "wait_time": 2.0,
                "confidence_boost": 0.10
            },
            "modal_content": {
                "indicators": ["modal", "dialog", "popup", "overlay"],
                "wait_time": 1.0,
                "confidence_boost": 0.20
            },
            "dropdown_content": {
                "indicators": ["dropdown", "menu", "options", "select"],
                "wait_time": 0.5,
                "confidence_boost": 0.15
            },
            "progressive_enhancement": {
                "indicators": ["enhanced", "progressive", "upgraded"],
                "wait_time": 1.5,
                "confidence_boost": 0.10
            }
        }
        
        # Common mutation triggers for different platforms
        self.platform_mutation_triggers = {
            "salesforce_lightning": {
                "triggers": [
                    "click [data-aura-class]",
                    "click .slds-button",
                    "hover .slds-dropdown-trigger",
                    "focus .slds-combobox__input"
                ],
                "mutation_selectors": [
                    ".slds-dropdown__list",
                    ".slds-modal",
                    ".slds-popover",
                    ".slds-spinner_container"
                ]
            },
            "servicenow": {
                "triggers": [
                    "click .btn",
                    "click .dropdown-toggle", 
                    "focus .typeahead",
                    "click .nav-link"
                ],
                "mutation_selectors": [
                    ".dropdown-menu",
                    ".modal",
                    ".typeahead-menu",
                    ".loading-indicator"
                ]
            },
            "workday": {
                "triggers": [
                    "click .wd-button",
                    "click .wd-menu-trigger",
                    "focus .wd-input",
                    "click .wd-tab"
                ],
                "mutation_selectors": [
                    ".wd-menu",
                    ".wd-modal",
                    ".wd-autocomplete",
                    ".wd-loading"
                ]
            },
            "sap": {
                "triggers": [
                    "click .sapMBtn",
                    "click .sapMComboBoxArrow",
                    "focus .sapMInputBase",
                    "click .sapMTabStripItem"
                ],
                "mutation_selectors": [
                    ".sapMSelectList",
                    ".sapMDialog",
                    ".sapMPopover",
                    ".sapMBusyIndicator"
                ]
            }
        }
        
        # Mutation strategies based on element lifecycle
        self.lifecycle_strategies = {
            "appearing": {
                "description": "Elements that appear after user interaction",
                "selectors": [
                    "[style*='display: block']",
                    "[style*='visibility: visible']", 
                    ":not([hidden])",
                    ".show, .visible, .active"
                ]
            },
            "disappearing": {
                "description": "Elements that are being removed",
                "selectors": [
                    "[style*='display: none']",
                    "[style*='visibility: hidden']",
                    "[hidden]",
                    ".hide, .hidden, .removing"
                ]
            },
            "loading": {
                "description": "Elements in loading state",
                "selectors": [
                    ".loading",
                    ".spinner",
                    ".skeleton",
                    "[aria-busy='true']"
                ]
            },
            "loaded": {
                "description": "Elements that have finished loading",
                "selectors": [
                    ":not(.loading)",
                    ":not(.spinner)",
                    ":not(.skeleton)",
                    "[aria-busy='false']"
                ]
            }
        }
    
    async def generate_strategies(
        self, 
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies that account for DOM mutations and dynamic content."""
        
        strategies = []
        
        # Strategy 1: Pre-mutation baseline strategies
        baseline_strategies = await self._generate_baseline_strategies(page, context)
        strategies.extend(baseline_strategies)
        
        # Strategy 2: Post-interaction mutation strategies
        mutation_strategies = await self._generate_mutation_strategies(page, context)
        strategies.extend(mutation_strategies)
        
        # Strategy 3: Timing-based waiting strategies
        timing_strategies = await self._generate_timing_strategies(page, context)
        strategies.extend(timing_strategies)
        
        # Strategy 4: Dynamic content detection
        dynamic_strategies = await self._generate_dynamic_content_strategies(page, context)
        strategies.extend(dynamic_strategies)
        
        # Strategy 5: Mutation recovery strategies
        recovery_strategies = await self._generate_recovery_strategies(page, context)
        strategies.extend(recovery_strategies)
        
        return strategies
    
    async def _generate_baseline_strategies(
        self, 
        page: Any, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate baseline strategies before considering mutations."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Check if this is a type of element that commonly appears via mutation
        dynamic_indicators = []
        for pattern_type, pattern_info in self.dynamic_patterns.items():
            if any(indicator in intent_lower for indicator in pattern_info["indicators"]):
                dynamic_indicators.append(pattern_type)
        
        if dynamic_indicators:
            # These elements are likely to be dynamic, so use mutation-aware strategies
            strategies.append(ElementStrategy(
                selector=f"[data-dynamic='true']",
                confidence=0.60,
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.MEDIUM,
                reasoning="Element marked as dynamic content",
                metadata={"dynamic_patterns": dynamic_indicators}
            ))
        
        # Platform-specific baseline checks
        platform = context.platform
        if platform in self.platform_mutation_triggers:
            mutation_selectors = self.platform_mutation_triggers[platform]["mutation_selectors"]
            
            for selector in mutation_selectors:
                strategies.append(ElementStrategy(
                    selector=selector,
                    confidence=0.55,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning=f"Platform-specific dynamic content selector: {selector}"
                ))
        
        return strategies
    
    async def _generate_mutation_strategies(
        self, 
        page: Any, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies that trigger and wait for mutations."""
        
        strategies = []
        intent_lower = context.intent.lower()
        platform = context.platform
        
        # Get mutation triggers for the platform
        if platform in self.platform_mutation_triggers:
            triggers = self.platform_mutation_triggers[platform]["triggers"]
            
            # Create strategies that involve triggering mutations
            for trigger in triggers:
                if any(word in trigger.lower() for word in intent_lower.split()):
                    strategies.append(ElementStrategy(
                        selector=f"mutation:trigger:{trigger}",
                        confidence=0.70,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.EXPENSIVE,
                        reasoning=f"Trigger mutation then find element: {trigger}",
                        metadata={"requires_interaction": True, "trigger": trigger}
                    ))
        
        # Common mutation patterns
        mutation_patterns = {
            "dropdown": {
                "trigger": "click",
                "wait_for": ".dropdown-menu:visible, .slds-dropdown__list:visible",
                "confidence": 0.75
            },
            "modal": {
                "trigger": "click", 
                "wait_for": ".modal:visible, .slds-modal:visible, .wd-modal:visible",
                "confidence": 0.80
            },
            "autocomplete": {
                "trigger": "focus+type",
                "wait_for": ".autocomplete:visible, .typeahead:visible, .suggestions:visible",
                "confidence": 0.70
            },
            "lazy_load": {
                "trigger": "scroll",
                "wait_for": ".lazy-loaded:visible, .loaded:visible",
                "confidence": 0.65
            }
        }
        
        for pattern_name, pattern_info in mutation_patterns.items():
            if pattern_name in intent_lower:
                strategies.append(ElementStrategy(
                    selector=f"mutation:wait:{pattern_info['wait_for']}",
                    confidence=pattern_info["confidence"],
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.EXPENSIVE,
                    reasoning=f"Wait for {pattern_name} mutation: {pattern_info['wait_for']}",
                    metadata={
                        "trigger": pattern_info["trigger"],
                        "wait_selector": pattern_info["wait_for"]
                    }
                ))
        
        return strategies
    
    async def _generate_timing_strategies(
        self, 
        page: Any, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies with different timing approaches for mutations."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Determine expected mutation timing based on intent
        timing_config = None
        for pattern_type, pattern_info in self.dynamic_patterns.items():
            if any(indicator in intent_lower for indicator in pattern_info["indicators"]):
                timing_config = pattern_info
                break
        
        if timing_config:
            wait_time = timing_config["wait_time"]
            confidence_boost = timing_config["confidence_boost"]
            
            # Strategy: Wait for specific time then find element
            strategies.append(ElementStrategy(
                selector=f"timing:wait:{wait_time}",
                confidence=0.60 + confidence_boost,
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.EXPENSIVE,
                reasoning=f"Wait {wait_time}s for dynamic content to load",
                metadata={"wait_time": wait_time}
            ))
        
        # Common timing patterns
        timing_strategies = [
            {
                "name": "immediate",
                "wait": 0.1,
                "confidence": 0.50,
                "description": "Check immediately for already-loaded content"
            },
            {
                "name": "short_delay", 
                "wait": 0.5,
                "confidence": 0.60,
                "description": "Short delay for fast animations"
            },
            {
                "name": "medium_delay",
                "wait": 1.0, 
                "confidence": 0.65,
                "description": "Medium delay for standard loading"
            },
            {
                "name": "long_delay",
                "wait": 2.0,
                "confidence": 0.55,
                "description": "Long delay for slow network/complex content"
            }
        ]
        
        for timing in timing_strategies:
            strategies.append(ElementStrategy(
                selector=f"timing:delay:{timing['wait']}",
                confidence=timing["confidence"],
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.EXPENSIVE,
                reasoning=timing["description"],
                metadata={"wait_time": timing["wait"], "timing_type": timing["name"]}
            ))
        
        return strategies
    
    async def _generate_dynamic_content_strategies(
        self, 
        page: Any, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies for detecting and handling dynamic content."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Strategy: Wait for loading indicators to disappear
        loading_indicators = [
            ".loading", ".spinner", ".skeleton", ".placeholder",
            "[aria-busy='true']", ".busy", ".working"
        ]
        
        for indicator in loading_indicators:
            strategies.append(ElementStrategy(
                selector=f"mutation:wait_gone:{indicator}",
                confidence=0.65,
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.EXPENSIVE,
                reasoning=f"Wait for loading indicator to disappear: {indicator}",
                metadata={"wait_for_removal": indicator}
            ))
        
        # Strategy: Wait for content to appear
        content_indicators = [
            ".loaded", ".ready", ".complete", ".rendered",
            "[aria-busy='false']", ".content-loaded"
        ]
        
        for indicator in content_indicators:
            strategies.append(ElementStrategy(
                selector=f"mutation:wait_appear:{indicator}",
                confidence=0.70,
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.EXPENSIVE,
                reasoning=f"Wait for content indicator to appear: {indicator}",
                metadata={"wait_for_appearance": indicator}
            ))
        
        # Strategy: Observe specific element state changes
        state_changes = {
            "disabled_to_enabled": {
                "from": "[disabled]",
                "to": ":not([disabled])",
                "confidence": 0.75
            },
            "hidden_to_visible": {
                "from": "[hidden]",
                "to": ":not([hidden])",
                "confidence": 0.80
            },
            "readonly_to_editable": {
                "from": "[readonly]", 
                "to": ":not([readonly])",
                "confidence": 0.70
            }
        }
        
        for change_name, change_info in state_changes.items():
            strategies.append(ElementStrategy(
                selector=f"mutation:state_change:{change_info['to']}",
                confidence=change_info["confidence"],
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.EXPENSIVE,
                reasoning=f"Wait for state change: {change_name}",
                metadata={
                    "from_state": change_info["from"],
                    "to_state": change_info["to"]
                }
            ))
        
        return strategies
    
    async def _generate_recovery_strategies(
        self, 
        page: Any, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies to recover from mutation failures."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Recovery strategy: Force refresh and retry
        strategies.append(ElementStrategy(
            selector="mutation:recovery:refresh",
            confidence=0.40,
            strategy_type=self.layer_type,
            performance_tier=PerformanceTier.EXPENSIVE,
            reasoning="Force page refresh and retry element finding",
            metadata={"recovery_action": "refresh"}
        ))
        
        # Recovery strategy: Clear dynamic state and retry
        strategies.append(ElementStrategy(
            selector="mutation:recovery:reset_state",
            confidence=0.45,
            strategy_type=self.layer_type,
            performance_tier=PerformanceTier.EXPENSIVE,
            reasoning="Reset dynamic state and retry",
            metadata={"recovery_action": "reset_state"}
        ))
        
        # Recovery strategy: Try alternative interaction patterns
        alternative_patterns = [
            {
                "pattern": "click_and_wait",
                "confidence": 0.50,
                "description": "Click trigger element and wait for mutation"
            },
            {
                "pattern": "hover_and_wait", 
                "confidence": 0.45,
                "description": "Hover over trigger and wait for mutation"
            },
            {
                "pattern": "focus_and_wait",
                "confidence": 0.50,
                "description": "Focus trigger element and wait for mutation"
            },
            {
                "pattern": "scroll_and_wait",
                "confidence": 0.40,
                "description": "Scroll to trigger lazy loading"
            }
        ]
        
        for pattern in alternative_patterns:
            strategies.append(ElementStrategy(
                selector=f"mutation:recovery:{pattern['pattern']}",
                confidence=pattern["confidence"],
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.EXPENSIVE,
                reasoning=pattern["description"],
                metadata={"recovery_pattern": pattern["pattern"]}
            ))
        
        # Recovery strategy: Fallback to static selectors
        strategies.append(ElementStrategy(
            selector="mutation:recovery:static_fallback",
            confidence=0.35,
            strategy_type=self.layer_type,
            performance_tier=PerformanceTier.EXPENSIVE,
            reasoning="Fallback to static selectors ignoring dynamic behavior",
            metadata={"recovery_action": "static_fallback"}
        ))
        
        return strategies
    
    async def observe_mutations(
        self, 
        page: Any, 
        target_selector: str, 
        timeout: float = 5.0
    ) -> Dict[str, Any]:
        """
        Observe DOM mutations for a specific target.
        This would be implemented with actual MutationObserver in a real browser context.
        """
        
        # This is a simulation - in real implementation, this would use MutationObserver
        observation_result = {
            "mutations_detected": 0,
            "elements_added": [],
            "elements_removed": [],
            "attributes_changed": [],
            "target_found": False,
            "observation_time": timeout
        }
        
        # Simulate waiting for mutations
        await asyncio.sleep(min(timeout, 1.0))  # Cap at 1 second for simulation
        
        # In real implementation, this would contain actual mutation data
        return observation_result
    
    async def wait_for_element_mutation(
        self,
        page: Any,
        strategy: ElementStrategy,
        timeout: float = 10.0
    ) -> bool:
        """
        Wait for a specific element to appear or change based on mutation strategy.
        """
        
        if not strategy.metadata:
            return False
        
        # Handle different types of mutation strategies
        if "trigger" in strategy.metadata:
            # Trigger an interaction and wait for response
            trigger = strategy.metadata["trigger"]
            
            try:
                # This would execute the trigger action in real implementation
                await asyncio.sleep(0.1)  # Simulate trigger time
                
                # Wait for mutation response
                if "wait_selector" in strategy.metadata:
                    wait_selector = strategy.metadata["wait_selector"]
                    # In real implementation, wait for the selector to appear
                    await asyncio.sleep(0.5)  # Simulate wait time
                    return True
                    
            except Exception as e:
                print(f"Mutation trigger failed: {e}")
                return False
        
        elif "wait_time" in strategy.metadata:
            # Simple time-based waiting
            wait_time = strategy.metadata["wait_time"]
            await asyncio.sleep(min(wait_time, 2.0))  # Cap for simulation
            return True
        
        elif "recovery_action" in strategy.metadata:
            # Recovery actions
            action = strategy.metadata["recovery_action"]
            
            if action == "refresh":
                # Simulate page refresh
                await asyncio.sleep(1.0)
                return True
            elif action == "reset_state":
                # Simulate state reset
                await asyncio.sleep(0.5) 
                return True
        
        return False