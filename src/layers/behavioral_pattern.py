"""
Layer 4: Behavioral Pattern Recognition
=======================================

Identifies elements based on their behavioral characteristics.
Detects hover effects, click behaviors, animations, and state changes.

Patent-critical: This is Layer 4 of the 10-layer system.
"""

import asyncio
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from playwright.async_api import Page, ElementHandle

from ..models.element import ElementStrategy, ElementContext, StrategyType
from .base import BaseLayer


@dataclass
class BehaviorPattern:
    """Behavioral pattern detected for an element."""
    pattern_type: str  # hover, click, focus, animation
    trigger: str       # What triggers the behavior
    effect: str        # What happens
    confidence: float


class BehavioralPatternLayer(BaseLayer):
    """
    Layer 4: Behavioral Pattern Recognition
    
    Identifies elements by their interactive behaviors:
    - Hover effects (color changes, tooltips, underlines)
    - Click behaviors (ripple effects, state changes)
    - Focus indicators (outlines, backgrounds)
    - Animation patterns (transitions, transforms)
    """
    
    def __init__(self):
        super().__init__(StrategyType.BEHAVIORAL_PATTERN)
    
    async def generate_strategies(
        self, 
        page: Page, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate behavior-based strategies."""
        strategies = []
        
        # Skip if no browser available
        if not hasattr(page, 'evaluate'):
            return self._generate_static_behavioral_strategies(context)
        
        # Platform-specific behavioral patterns
        behavior_patterns = self._get_platform_behaviors(context.platform)
        
        # Generate strategies based on expected behaviors
        strategies.extend(await self._hover_behavior_strategies(page, context, behavior_patterns))
        strategies.extend(await self._click_behavior_strategies(page, context, behavior_patterns))
        strategies.extend(await self._focus_behavior_strategies(page, context, behavior_patterns))
        strategies.extend(await self._animation_strategies(page, context, behavior_patterns))
        
        return strategies
    
    def _get_platform_behaviors(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific behavioral patterns."""
        patterns = {
            "salesforce_lightning": {
                "button_hover": {
                    "selector": "button.slds-button",
                    "hover_class": "slds-is-hovered",
                    "hover_style": "background-color",
                    "transition": "all 0.2s"
                },
                "link_hover": {
                    "selector": "a.slds-link",
                    "hover_effect": "text-decoration: underline"
                },
                "input_focus": {
                    "selector": "input.slds-input",
                    "focus_class": "slds-has-focus",
                    "focus_shadow": "0 0 3px #0070d2"
                },
                "click_ripple": {
                    "selector": ".slds-button",
                    "ripple_class": "slds-button_clicked"
                }
            },
            "sap_fiori": {
                "button_hover": {
                    "selector": "button.sapMBtn",
                    "hover_class": "sapMBtnHoverable",
                    "hover_style": "background-color",
                    "transition": "background-color 0.1s"
                },
                "tile_hover": {
                    "selector": ".sapMTile",
                    "hover_transform": "scale(1.05)",
                    "hover_shadow": "0 4px 8px rgba(0,0,0,0.1)"
                },
                "input_focus": {
                    "selector": "input.sapMInputBaseInner",
                    "focus_outline": "1px dotted",
                    "focus_color": "#0854a0"
                }
            },
            "workday": {
                "button_hover": {
                    "selector": "button[data-automation-id]",
                    "hover_background": "#f5f5f5",
                    "hover_border": "1px solid #0875e1"
                },
                "menu_hover": {
                    "selector": "[role='menuitem']",
                    "hover_class": "hover",
                    "hover_background": "#e8f4fd"
                },
                "input_focus": {
                    "selector": "input[data-automation-id]",
                    "focus_border": "2px solid #0875e1",
                    "focus_outline": "none"
                }
            },
            "oracle_cloud": {
                "button_hover": {
                    "selector": "button.af_button",
                    "hover_class": "p_AFHover",
                    "hover_style": "border-color"
                },
                "link_hover": {
                    "selector": "a.af_link",
                    "hover_decoration": "underline"
                },
                "input_focus": {
                    "selector": "input.af_inputText_content",
                    "focus_class": "p_AFFocused",
                    "focus_border": "1px solid #0572ce"
                }
            }
        }
        
        return patterns.get(platform, self._get_generic_behaviors())
    
    def _get_generic_behaviors(self) -> Dict[str, Any]:
        """Get generic behavioral patterns."""
        return {
            "button_hover": {
                "selector": "button",
                "hover_style": "background-color, color, border-color",
                "common_effects": ["opacity", "transform", "box-shadow"]
            },
            "link_hover": {
                "selector": "a",
                "hover_decoration": "underline",
                "hover_color": "color"
            },
            "input_focus": {
                "selector": "input, textarea, select",
                "focus_outline": "outline",
                "focus_border": "border-color"
            }
        }
    
    def _generate_static_behavioral_strategies(self, context: ElementContext) -> List[ElementStrategy]:
        """Generate strategies without browser interaction."""
        strategies = []
        
        # Common behavioral selectors based on intent
        if 'button' in context.intent.lower() or 'click' in context.intent.lower():
            # Buttons with hover states
            strategies.append(ElementStrategy(
                strategy_type=StrategyType.BEHAVIORAL_PATTERN,
                selector="button:hover, button[class*='hover'], button[class*='active']",
                confidence=0.65,
                metadata={
                    "behavior": "hover_state",
                    "pattern": "button_with_hover",
                    "static": True
                }
            ))
            
            # Clickable elements with cursor pointer
            strategies.append(ElementStrategy(
                strategy_type=StrategyType.BEHAVIORAL_PATTERN,
                selector="[style*='cursor: pointer'], [style*='cursor:pointer']",
                confidence=0.60,
                metadata={
                    "behavior": "clickable",
                    "pattern": "cursor_pointer",
                    "static": True
                }
            ))
        
        if 'input' in context.intent.lower() or 'field' in context.intent.lower():
            # Focusable inputs
            strategies.append(ElementStrategy(
                strategy_type=StrategyType.BEHAVIORAL_PATTERN,
                selector="input:focus, input[class*='focus'], textarea:focus, select:focus",
                confidence=0.65,
                metadata={
                    "behavior": "focusable",
                    "pattern": "input_with_focus",
                    "static": True
                }
            ))
        
        return strategies
    
    async def _hover_behavior_strategies(
        self, 
        page: Page, 
        context: ElementContext,
        patterns: Dict[str, Any]
    ) -> List[ElementStrategy]:
        """Generate strategies based on hover behaviors."""
        strategies = []
        
        if 'button' in context.intent.lower():
            button_pattern = patterns.get('button_hover', {})
            
            # Strategy: Button with hover class
            if 'hover_class' in button_pattern:
                selector = f"{button_pattern['selector']}.{button_pattern['hover_class']}"
                strategies.append(ElementStrategy(
                    strategy_type=StrategyType.BEHAVIORAL_PATTERN,
                    selector=selector,
                    confidence=0.70,
                    metadata={
                        "behavior": "hover",
                        "trigger": "mouseover",
                        "effect": f"adds class {button_pattern['hover_class']}"
                    }
                ))
            
            # Strategy: Button with hover style changes
            if 'hover_style' in button_pattern:
                js_selector = f"""
                    document.querySelectorAll('{button_pattern['selector']}')
                        .filter(el => {{
                            const computed = window.getComputedStyle(el);
                            const hoverComputed = window.getComputedStyle(el, ':hover');
                            return computed['{button_pattern['hover_style']}'] !== 
                                   hoverComputed['{button_pattern['hover_style']}'];
                        }})
                """
                strategies.append(ElementStrategy(
                    strategy_type=StrategyType.BEHAVIORAL_PATTERN,
                    selector=button_pattern['selector'],
                    confidence=0.75,
                    metadata={
                        "behavior": "hover",
                        "trigger": "mouseover",
                        "effect": f"changes {button_pattern['hover_style']}",
                        "detection": "style_comparison"
                    }
                ))
        
        return strategies
    
    async def _click_behavior_strategies(
        self, 
        page: Page, 
        context: ElementContext,
        patterns: Dict[str, Any]
    ) -> List[ElementStrategy]:
        """Generate strategies based on click behaviors."""
        strategies = []
        
        if any(action in context.intent.lower() for action in ['button', 'click', 'submit', 'save']):
            # Strategy: Elements with click handlers
            selector = "[onclick], [ng-click], [data-click], button[type='submit']"
            strategies.append(ElementStrategy(
                strategy_type=StrategyType.BEHAVIORAL_PATTERN,
                selector=selector,
                confidence=0.70,
                metadata={
                    "behavior": "click",
                    "trigger": "click",
                    "pattern": "has_click_handler"
                }
            ))
            
            # Strategy: Elements with ripple effect
            if 'click_ripple' in patterns:
                ripple_pattern = patterns['click_ripple']
                strategies.append(ElementStrategy(
                    strategy_type=StrategyType.BEHAVIORAL_PATTERN,
                    selector=ripple_pattern['selector'],
                    confidence=0.65,
                    metadata={
                        "behavior": "click",
                        "trigger": "click",
                        "effect": f"ripple effect with {ripple_pattern.get('ripple_class', 'animation')}"
                    }
                ))
        
        return strategies
    
    async def _focus_behavior_strategies(
        self, 
        page: Page, 
        context: ElementContext,
        patterns: Dict[str, Any]
    ) -> List[ElementStrategy]:
        """Generate strategies based on focus behaviors."""
        strategies = []
        
        if any(field in context.intent.lower() for field in ['input', 'field', 'text', 'search']):
            focus_pattern = patterns.get('input_focus', {})
            
            # Strategy: Input with focus class
            if 'focus_class' in focus_pattern:
                selector = f"{focus_pattern['selector']}.{focus_pattern['focus_class']}"
                strategies.append(ElementStrategy(
                    strategy_type=StrategyType.BEHAVIORAL_PATTERN,
                    selector=selector,
                    confidence=0.70,
                    metadata={
                        "behavior": "focus",
                        "trigger": "focus",
                        "effect": f"adds class {focus_pattern['focus_class']}"
                    }
                ))
            
            # Strategy: Input with focus outline
            if 'focus_outline' in focus_pattern or 'focus_border' in focus_pattern:
                strategies.append(ElementStrategy(
                    strategy_type=StrategyType.BEHAVIORAL_PATTERN,
                    selector=focus_pattern['selector'],
                    confidence=0.65,
                    metadata={
                        "behavior": "focus",
                        "trigger": "focus",
                        "effect": focus_pattern.get('focus_outline', focus_pattern.get('focus_border'))
                    }
                ))
        
        return strategies
    
    async def _animation_strategies(
        self, 
        page: Page, 
        context: ElementContext,
        patterns: Dict[str, Any]
    ) -> List[ElementStrategy]:
        """Generate strategies based on animation patterns."""
        strategies = []
        
        # Strategy: Elements with CSS transitions
        if 'transition' in str(patterns):
            selector = "[style*='transition'], [class*='transition'], [class*='animate']"
            strategies.append(ElementStrategy(
                strategy_type=StrategyType.BEHAVIORAL_PATTERN,
                selector=selector,
                confidence=0.60,
                metadata={
                    "behavior": "animated",
                    "pattern": "has_transition",
                    "detection": "css_property"
                }
            ))
        
        # Strategy: Elements with transform on hover
        if any(word in context.intent.lower() for word in ['menu', 'dropdown', 'expand']):
            selector = "[style*='transform'], [class*='transform'], [class*='expand']"
            strategies.append(ElementStrategy(
                strategy_type=StrategyType.BEHAVIORAL_PATTERN,
                selector=selector,
                confidence=0.65,
                metadata={
                    "behavior": "animated",
                    "pattern": "transform_on_interaction",
                    "effect": "scale or translate"
                }
            ))
        
        return strategies