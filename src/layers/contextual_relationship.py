"""
Layer 2: Contextual Relationship Mapping
========================================

Identifies elements based on their relationships to other elements.
Uses spatial, hierarchical, and semantic relationships.

Patent-critical: This is Layer 2 of the 10-layer system.
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from playwright.async_api import Page, ElementHandle

from ..models.element import ElementStrategy, ElementContext, StrategyType


@dataclass
class RelationshipContext:
    """Context about element relationships."""
    parent_text: Optional[str] = None
    sibling_texts: List[str] = None
    nearby_labels: List[str] = None
    container_type: Optional[str] = None
    relative_position: Optional[str] = None  # above, below, left-of, right-of


class ContextualRelationshipLayer:
    """
    Layer 2: Contextual Relationship Mapping
    
    Finds elements based on their relationships to other elements.
    Handles parent-child, sibling, and proximity relationships.
    """
    
    async def generate_strategies(
        self, 
        page: Page, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate relationship-based strategies."""
        strategies = []
        
        # Platform-specific relationship patterns
        relationship_patterns = self._get_platform_patterns(context.platform)
        
        # Generate strategies based on different relationship types
        strategies.extend(await self._parent_child_strategies(context, relationship_patterns))
        strategies.extend(await self._sibling_strategies(context, relationship_patterns))
        strategies.extend(await self._proximity_strategies(context, relationship_patterns))
        strategies.extend(await self._container_strategies(context, relationship_patterns))
        
        return strategies
    
    def _get_platform_patterns(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific relationship patterns."""
        patterns = {
            "salesforce_lightning": {
                "form_field_pattern": "//div[contains(@class, 'slds-form-element')]",
                "label_input_relation": "//label[text()='{label}']/following-sibling::div//input",
                "button_in_section": "//div[@class='slds-section' and .//h3[contains(text(), '{section}')]]//button[contains(text(), '{button}')]",
                "field_container": "lightning-input, lightning-textarea, lightning-combobox",
                "action_bar": "div.slds-page-header__controls, div.slds-modal__footer"
            },
            "sap_fiori": {
                "form_field_pattern": "//div[contains(@class, 'sapMInputBase')]",
                "label_input_relation": "//label[@for='{id}']/following::input[1]",
                "button_in_toolbar": "//div[@role='toolbar']//button[@aria-label='{label}']",
                "field_container": "div.sapMInputBase, div.sapMSelect",
                "action_bar": "div.sapMBar, footer.sapMPageFooter"
            },
            "workday": {
                "form_field_pattern": "//div[@data-automation-id]",
                "label_input_relation": "//label[contains(text(), '{label}')]/ancestor::div[@data-automation-id]//input",
                "button_in_section": "//div[@role='region' and @aria-label='{section}']//button[@aria-label='{button}']",
                "field_container": "div[data-automation-id*='Field']",
                "action_bar": "div[data-automation-id*='Actions'], div[role='toolbar']"
            },
            "oracle_cloud": {
                "form_field_pattern": "//tr[contains(@class, 'af_inputText')]",
                "label_input_relation": "//label[text()='{label}']/ancestor::tr[1]//input",
                "button_in_section": "//div[@class='af:panelHeader' and .//h1[contains(text(), '{section}')]]//button[@title='{button}']",
                "field_container": "tr.af_inputText, tr.af_selectOneChoice",
                "action_bar": "div.af_toolbar, div.af_panelButtonBar"
            }
        }
        
        return patterns.get(platform, self._get_generic_patterns())
    
    def _get_generic_patterns(self) -> Dict[str, Any]:
        """Get generic relationship patterns."""
        return {
            "form_field_pattern": "//div[@class='form-group' or @class='field']",
            "label_input_relation": "//label[contains(text(), '{label}')]/following::input[1]",
            "button_in_section": "//section[.//h2[contains(text(), '{section}')]]//button[contains(text(), '{button}')]",
            "field_container": "div.form-group, div.field, fieldset",
            "action_bar": "div.actions, div.button-group, footer"
        }
    
    async def _parent_child_strategies(
        self, 
        context: ElementContext,
        patterns: Dict[str, Any]
    ) -> List[ElementStrategy]:
        """Generate parent-child relationship strategies."""
        strategies = []
        
        # Strategy 1: Label-Input relationship
        if any(keyword in context.intent.lower() for keyword in ['field', 'input', 'text', 'enter']):
            label_text = self._extract_label_from_intent(context.intent)
            if label_text:
                xpath = patterns["label_input_relation"].format(label=label_text)
                strategies.append(ElementStrategy(
                    strategy_type=StrategyType.CONTEXTUAL_RELATIONSHIP,
                    selector=xpath,
                    confidence=0.85,
                    metadata={
                        "relationship_type": "label_input",
                        "label_text": label_text,
                        "pattern": "label-to-input"
                    }
                ))
        
        # Strategy 2: Button in specific section
        if 'button' in context.intent.lower() and context.page_type:
            section_name = context.page_type.replace('_', ' ').title()
            button_text = self._extract_button_text(context.intent)
            if button_text:
                xpath = patterns["button_in_section"].format(
                    section=section_name,
                    button=button_text
                )
                strategies.append(ElementStrategy(
                    strategy_type=StrategyType.CONTEXTUAL_RELATIONSHIP,
                    selector=xpath,
                    confidence=0.80,
                    metadata={
                        "relationship_type": "button_in_section",
                        "section": section_name,
                        "button": button_text
                    }
                ))
        
        return strategies
    
    async def _sibling_strategies(
        self, 
        context: ElementContext,
        patterns: Dict[str, Any]
    ) -> List[ElementStrategy]:
        """Generate sibling relationship strategies."""
        strategies = []
        
        # Strategy: Find element next to a label
        if 'next to' in context.intent.lower() or 'beside' in context.intent.lower():
            reference_text = self._extract_reference_element(context.intent)
            if reference_text:
                # Following sibling
                xpath = f"//label[contains(text(), '{reference_text}')]/following-sibling::*[1]"
                strategies.append(ElementStrategy(
                    strategy_type=StrategyType.CONTEXTUAL_RELATIONSHIP,
                    selector=xpath,
                    confidence=0.75,
                    metadata={
                        "relationship_type": "following_sibling",
                        "reference": reference_text
                    }
                ))
                
                # Preceding sibling
                xpath = f"//label[contains(text(), '{reference_text}')]/preceding-sibling::*[1]"
                strategies.append(ElementStrategy(
                    strategy_type=StrategyType.CONTEXTUAL_RELATIONSHIP,
                    selector=xpath,
                    confidence=0.70,
                    metadata={
                        "relationship_type": "preceding_sibling",
                        "reference": reference_text
                    }
                ))
        
        return strategies
    
    async def _proximity_strategies(
        self, 
        context: ElementContext,
        patterns: Dict[str, Any]
    ) -> List[ElementStrategy]:
        """Generate proximity-based strategies."""
        strategies = []
        
        # Strategy: Elements in action bars
        if any(action in context.intent.lower() for action in ['save', 'cancel', 'submit', 'delete']):
            # CSS selector for action bar buttons
            css = f"{patterns['action_bar']} button"
            strategies.append(ElementStrategy(
                strategy_type=StrategyType.CONTEXTUAL_RELATIONSHIP,
                selector=css,
                confidence=0.70,
                metadata={
                    "relationship_type": "proximity",
                    "container": "action_bar",
                    "pattern": "button-in-actions"
                }
            ))
        
        # Strategy: Form field containers
        if 'field' in context.intent.lower():
            field_name = self._extract_field_name(context.intent)
            if field_name:
                css = f"{patterns['field_container']}:has-text('{field_name}')"
                strategies.append(ElementStrategy(
                    strategy_type=StrategyType.CONTEXTUAL_RELATIONSHIP,
                    selector=css,
                    confidence=0.75,
                    metadata={
                        "relationship_type": "proximity",
                        "container": "field_container",
                        "field_name": field_name
                    }
                ))
        
        return strategies
    
    async def _container_strategies(
        self, 
        context: ElementContext,
        patterns: Dict[str, Any]
    ) -> List[ElementStrategy]:
        """Generate container-based strategies."""
        strategies = []
        
        # Strategy: Modal/Dialog buttons
        if context.page_type and 'modal' in context.page_type.lower():
            button_text = self._extract_button_text(context.intent)
            if button_text:
                xpath = f"//div[@role='dialog' or contains(@class, 'modal')]//button[contains(text(), '{button_text}')]"
                strategies.append(ElementStrategy(
                    strategy_type=StrategyType.CONTEXTUAL_RELATIONSHIP,
                    selector=xpath,
                    confidence=0.85,
                    metadata={
                        "relationship_type": "container",
                        "container_type": "modal",
                        "element": button_text
                    }
                ))
        
        # Strategy: Table cell relationships
        if 'table' in context.page_type.lower() or 'row' in context.intent.lower():
            column_name = self._extract_column_name(context.intent)
            row_identifier = self._extract_row_identifier(context.intent)
            
            if column_name and row_identifier:
                xpath = f"//tr[contains(., '{row_identifier}')]//td[count(//th[contains(text(), '{column_name}')]/preceding-sibling::th) + 1]"
                strategies.append(ElementStrategy(
                    strategy_type=StrategyType.CONTEXTUAL_RELATIONSHIP,
                    selector=xpath,
                    confidence=0.80,
                    metadata={
                        "relationship_type": "table_cell",
                        "column": column_name,
                        "row": row_identifier
                    }
                ))
        
        return strategies
    
    def _extract_label_from_intent(self, intent: str) -> Optional[str]:
        """Extract label text from intent."""
        # Remove common words and extract the field name
        remove_words = ['field', 'input', 'enter', 'type', 'in', 'the', 'a', 'an']
        words = intent.lower().split()
        label_words = [w for w in words if w not in remove_words]
        
        if label_words:
            return ' '.join(label_words).title()
        return None
    
    def _extract_button_text(self, intent: str) -> Optional[str]:
        """Extract button text from intent."""
        # Common button actions
        button_keywords = ['save', 'submit', 'cancel', 'delete', 'create', 'new', 'add', 'edit', 'close']
        
        for keyword in button_keywords:
            if keyword in intent.lower():
                return keyword.title()
        
        # Extract custom button text
        if 'button' in intent.lower():
            parts = intent.lower().split('button')
            if len(parts) > 0:
                return parts[0].strip().title()
        
        return None
    
    def _extract_reference_element(self, intent: str) -> Optional[str]:
        """Extract reference element for proximity searches."""
        proximity_words = ['next to', 'beside', 'near', 'after', 'before']
        
        for word in proximity_words:
            if word in intent.lower():
                parts = intent.lower().split(word)
                if len(parts) > 1:
                    return parts[1].strip()
        
        return None
    
    def _extract_field_name(self, intent: str) -> Optional[str]:
        """Extract field name from intent."""
        # Similar to label extraction but more specific
        field_indicators = ['field', 'input', 'textbox', 'dropdown', 'select']
        
        words = intent.lower().split()
        for i, word in enumerate(words):
            if word in field_indicators and i > 0:
                return ' '.join(words[:i]).title()
        
        return self._extract_label_from_intent(intent)
    
    def _extract_column_name(self, intent: str) -> Optional[str]:
        """Extract column name from table-related intent."""
        if 'column' in intent.lower():
            parts = intent.lower().split('column')
            if len(parts) > 1:
                return parts[1].strip().title()
        return None
    
    def _extract_row_identifier(self, intent: str) -> Optional[str]:
        """Extract row identifier from table-related intent."""
        if 'row' in intent.lower():
            parts = intent.lower().split('row')
            if len(parts) > 1:
                return parts[1].strip()
        return None