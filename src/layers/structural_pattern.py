"""
Layer 5: Structural Pattern Analysis
===================================
Analyzes DOM structure patterns, hierarchy relationships, and CSS class patterns
to identify elements based on their position in the document structure.

This layer is critical for elements that are identified by their structural context
rather than semantic meaning or visual appearance.
"""

import re
from typing import List, Optional, Any, Dict
from bs4 import BeautifulSoup, Tag
from src.models.element import ElementStrategy, ElementContext, StrategyType, PerformanceTier
from src.layers.base import BaseLayer


class StructuralPatternLayer(BaseLayer):
    """
    Layer 5: Analyzes DOM structure patterns for element identification.
    
    Uses hierarchy relationships, CSS class patterns, and structural
    positioning to generate reliable selectors.
    """
    
    def __init__(self):
        super().__init__(StrategyType.STRUCTURAL_PATTERN)
        
        # Common structural patterns for different platforms
        self.platform_patterns = {
            "salesforce_lightning": {
                "form_containers": [".slds-form", ".slds-form-element", ".forcePageBlockSectionRow"],
                "button_containers": [".slds-button-group", ".slds-form-element__control"],
                "input_containers": [".slds-form-element__control", ".slds-input__container"],
                "modal_containers": [".slds-modal", ".slds-modal__container"],
                "list_containers": [".slds-listbox", ".slds-combobox", ".slds-table"]
            },
            "servicenow": {
                "form_containers": [".form-group", ".container-fluid", ".row"],
                "button_containers": [".btn-group", ".form-actions"],
                "input_containers": [".form-control", ".input-group"],
                "modal_containers": [".modal", ".modal-dialog"],
                "list_containers": [".table", ".list-group", ".dropdown-menu"]
            },
            "workday": {
                "form_containers": [".wd-form", ".wd-card", ".form-row"],
                "button_containers": [".wd-button-group", ".action-buttons"],
                "input_containers": [".wd-input-group", ".form-field"],
                "modal_containers": [".wd-modal", ".overlay"],
                "list_containers": [".wd-table", ".wd-list", ".dropdown"]
            },
            "sap": {
                "form_containers": [".sapMForm", ".sapUiForm", ".sapMTile"],
                "button_containers": [".sapMButtonGroup", ".sapMBar"],
                "input_containers": [".sapMInputBase", ".sapMComboBox"],
                "modal_containers": [".sapMDialog", ".sapMPopover"],
                "list_containers": [".sapMTable", ".sapMList", ".sapMTree"]
            }
        }
        
        # Common structural patterns across platforms
        self.universal_patterns = {
            "navigation_structures": [
                "nav", "header nav", ".navigation", ".navbar", ".menu"
            ],
            "content_structures": [
                "main", ".content", ".main-content", "#content", ".container"
            ],
            "form_structures": [
                "form", ".form", ".form-container", "fieldset"
            ],
            "table_structures": [
                "table", ".table", ".data-table", ".grid"
            ]
        }
    
    async def generate_strategies(
        self, 
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on DOM structural patterns."""
        
        strategies = []
        
        # Get HTML content
        if hasattr(page, 'content'):
            html_content = await page.content()
        else:
            html_content = context.html_content or ""
        
        if not html_content:
            return strategies
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Strategy 1: Hierarchical positioning
        hierarchical_strategies = self._generate_hierarchical_strategies(soup, context)
        strategies.extend(hierarchical_strategies)
        
        # Strategy 2: CSS class pattern analysis
        css_pattern_strategies = self._generate_css_pattern_strategies(soup, context)
        strategies.extend(css_pattern_strategies)
        
        # Strategy 3: Container-based positioning
        container_strategies = self._generate_container_strategies(soup, context)
        strategies.extend(container_strategies)
        
        # Strategy 4: Sibling relationship analysis
        sibling_strategies = self._generate_sibling_strategies(soup, context)
        strategies.extend(sibling_strategies)
        
        # Strategy 5: Index-based positioning
        index_strategies = self._generate_index_strategies(soup, context)
        strategies.extend(index_strategies)
        
        return strategies
    
    def _generate_hierarchical_strategies(
        self, 
        soup: BeautifulSoup, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on DOM hierarchy patterns."""
        
        strategies = []
        intent_lower = context.intent.lower()
        platform = context.platform
        
        # Platform-specific hierarchy patterns
        if platform in self.platform_patterns:
            patterns = self.platform_patterns[platform]
            
            if any(word in intent_lower for word in ["button", "submit", "save", "login"]):
                # Look for buttons in button containers
                for container in patterns["button_containers"]:
                    strategies.append(ElementStrategy(
                        selector=f"{container} button",
                        confidence=0.75,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Button in {container} hierarchy"
                    ))
                    
                    strategies.append(ElementStrategy(
                        selector=f"{container} input[type='submit']",
                        confidence=0.70,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Submit input in {container} hierarchy"
                    ))
            
            if any(word in intent_lower for word in ["input", "field", "username", "password", "email"]):
                # Look for inputs in input containers
                for container in patterns["input_containers"]:
                    strategies.append(ElementStrategy(
                        selector=f"{container} input",
                        confidence=0.70,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Input in {container} hierarchy"
                    ))
                    
                    strategies.append(ElementStrategy(
                        selector=f"{container} input:not([type='hidden'])",
                        confidence=0.75,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Visible input in {container} hierarchy"
                    ))
        
        # Universal hierarchy patterns
        if "search" in intent_lower:
            strategies.extend([
                ElementStrategy(
                    selector="header input[type='search']",
                    confidence=0.85,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.INSTANT,
                    reasoning="Search input in header hierarchy"
                ),
                ElementStrategy(
                    selector="nav input[type='search']",
                    confidence=0.80,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.INSTANT,
                    reasoning="Search input in navigation hierarchy"
                )
            ])
        
        if any(word in intent_lower for word in ["home", "dashboard", "main"]):
            strategies.extend([
                ElementStrategy(
                    selector="nav a[href*='home']",
                    confidence=0.80,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.INSTANT,
                    reasoning="Home link in navigation hierarchy"
                ),
                ElementStrategy(
                    selector="header a[href*='dashboard']",
                    confidence=0.75,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.INSTANT,
                    reasoning="Dashboard link in header hierarchy"
                )
            ])
        
        return strategies
    
    def _generate_css_pattern_strategies(
        self, 
        soup: BeautifulSoup, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on CSS class patterns."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Find elements with relevant CSS classes
        all_elements = soup.find_all(True)  # Find all elements
        class_patterns = {}
        
        # Analyze class patterns
        for element in all_elements:
            if element.get('class'):
                classes = ' '.join(element.get('class', []))
                tag_name = element.name
                
                if tag_name not in class_patterns:
                    class_patterns[tag_name] = set()
                
                class_patterns[tag_name].add(classes)
        
        # Generate strategies based on intent and class patterns
        if "button" in intent_lower or "submit" in intent_lower:
            button_patterns = class_patterns.get('button', set())
            for pattern in button_patterns:
                if any(keyword in pattern.lower() for keyword in ['primary', 'submit', 'save', 'action']):
                    strategies.append(ElementStrategy(
                        selector=f"button.{pattern.replace(' ', '.')}",
                        confidence=0.70,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Button with action-related classes: {pattern}"
                    ))
        
        if any(word in intent_lower for word in ["input", "field", "username", "email"]):
            input_patterns = class_patterns.get('input', set())
            for pattern in input_patterns:
                if any(keyword in pattern.lower() for keyword in ['email', 'user', 'login', 'text']):
                    strategies.append(ElementStrategy(
                        selector=f"input.{pattern.replace(' ', '.')}",
                        confidence=0.65,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Input with relevant classes: {pattern}"
                    ))
        
        # Look for common naming patterns
        common_patterns = {
            "login": ["login", "sign-in", "auth", "signin"],
            "save": ["save", "submit", "confirm", "apply"],
            "cancel": ["cancel", "close", "dismiss", "abort"],
            "search": ["search", "find", "query", "filter"],
            "delete": ["delete", "remove", "trash", "destroy"],
            "edit": ["edit", "modify", "update", "change"]
        }
        
        for intent_key, patterns in common_patterns.items():
            if intent_key in intent_lower:
                for pattern in patterns:
                    strategies.append(ElementStrategy(
                        selector=f"[class*='{pattern}']",
                        confidence=0.60,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.MEDIUM,
                        reasoning=f"Element with {pattern} in class name"
                    ))
        
        return strategies
    
    def _generate_container_strategies(
        self, 
        soup: BeautifulSoup, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on container context."""
        
        strategies = []
        intent_lower = context.intent.lower()
        platform = context.platform
        
        # Find relevant containers
        containers = []
        
        if platform in self.platform_patterns:
            patterns = self.platform_patterns[platform]
            
            # Find form containers
            for container_class in patterns["form_containers"]:
                elements = soup.select(container_class)
                containers.extend([(elem, "form") for elem in elements])
            
            # Find modal containers
            for container_class in patterns["modal_containers"]:
                elements = soup.select(container_class)
                containers.extend([(elem, "modal") for elem in elements])
        
        # Generate strategies for each container
        for container, container_type in containers:
            container_selector = self._get_element_selector(container)
            
            if "button" in intent_lower:
                strategies.append(ElementStrategy(
                    selector=f"{container_selector} button:last-child",
                    confidence=0.65,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning=f"Last button in {container_type} container"
                ))
                
                strategies.append(ElementStrategy(
                    selector=f"{container_selector} button:first-child",
                    confidence=0.60,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning=f"First button in {container_type} container"
                ))
            
            if any(word in intent_lower for word in ["input", "field"]):
                strategies.append(ElementStrategy(
                    selector=f"{container_selector} input:not([type='hidden']):first",
                    confidence=0.65,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning=f"First input in {container_type} container"
                ))
        
        return strategies
    
    def _generate_sibling_strategies(
        self, 
        soup: BeautifulSoup, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on sibling relationships."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Common sibling patterns
        if "password" in intent_lower:
            strategies.extend([
                ElementStrategy(
                    selector="input[type='email'] + input[type='password']",
                    confidence=0.80,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning="Password field immediately after email field"
                ),
                ElementStrategy(
                    selector="input[type='text'] + input[type='password']",
                    confidence=0.75,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning="Password field immediately after text field"
                )
            ])
        
        if "submit" in intent_lower or "save" in intent_lower:
            strategies.extend([
                ElementStrategy(
                    selector="input[type='password'] ~ button[type='submit']",
                    confidence=0.75,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning="Submit button after password field"
                ),
                ElementStrategy(
                    selector="form input:last-child ~ button",
                    confidence=0.65,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning="Button after last form input"
                )
            ])
        
        if "cancel" in intent_lower:
            strategies.extend([
                ElementStrategy(
                    selector="button[type='submit'] + button",
                    confidence=0.70,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning="Button immediately after submit button"
                ),
                ElementStrategy(
                    selector="button:last-child",
                    confidence=0.60,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning="Last button (often cancel)"
                )
            ])
        
        return strategies
    
    def _generate_index_strategies(
        self, 
        soup: BeautifulSoup, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on element index positioning."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # First/last element strategies
        if "first" in intent_lower or "primary" in intent_lower:
            strategies.extend([
                ElementStrategy(
                    selector="button:first-of-type",
                    confidence=0.60,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning="First button on the page"
                ),
                ElementStrategy(
                    selector="input:first-of-type",
                    confidence=0.60,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning="First input on the page"
                )
            ])
        
        if "last" in intent_lower or "final" in intent_lower:
            strategies.extend([
                ElementStrategy(
                    selector="button:last-of-type",
                    confidence=0.60,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning="Last button on the page"
                ),
                ElementStrategy(
                    selector="input:last-of-type",
                    confidence=0.60,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning="Last input on the page"
                )
            ])
        
        # Nth-child strategies for common patterns
        strategies.extend([
            ElementStrategy(
                selector="form button:nth-child(1)",
                confidence=0.55,
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.MEDIUM,
                reasoning="First button in form"
            ),
            ElementStrategy(
                selector="form button:nth-child(2)",
                confidence=0.50,
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.MEDIUM,
                reasoning="Second button in form"
            )
        ])
        
        return strategies
    
    def _get_element_selector(self, element: Tag) -> str:
        """Generate a CSS selector for a given element."""
        
        selectors = []
        
        # Use ID if available
        if element.get('id'):
            return f"#{element['id']}"
        
        # Use classes if available
        if element.get('class'):
            classes = '.'.join(element['class'])
            selectors.append(f"{element.name}.{classes}")
        else:
            selectors.append(element.name)
        
        # Add parent context if needed
        parent = element.parent
        if parent and parent.name != 'body':
            parent_selector = self._get_simple_selector(parent)
            return f"{parent_selector} {selectors[0]}"
        
        return selectors[0] if selectors else element.name
    
    def _get_simple_selector(self, element: Tag) -> str:
        """Generate a simple CSS selector for an element."""
        
        if element.get('id'):
            return f"#{element['id']}"
        
        if element.get('class'):
            classes = '.'.join(element['class'][:2])  # Use first 2 classes
            return f"{element.name}.{classes}"
        
        return element.name