"""
Layer 6: Accessibility Bridge
=============================
Leverages accessibility attributes, ARIA patterns, and screen reader compatibility
to identify elements using accessibility features and standards.

This layer is crucial for robust element identification as accessibility attributes
are specifically designed to identify elements semantically and remain stable.
"""

import re
from typing import List, Optional, Any, Dict
from bs4 import BeautifulSoup, Tag
from src.models.element import ElementStrategy, ElementContext, StrategyType, PerformanceTier
from src.layers.base import BaseLayer


class AccessibilityBridgeLayer(BaseLayer):
    """
    Layer 6: Uses accessibility attributes and ARIA patterns for element identification.
    
    Focuses on ARIA roles, labels, descriptions, and other accessibility features
    that provide semantic meaning to elements.
    """
    
    def __init__(self):
        super().__init__(StrategyType.ACCESSIBILITY_BRIDGE)
        
        # ARIA role mappings to common intents
        self.aria_role_mappings = {
            "button": ["button", "submit", "save", "cancel", "confirm", "apply", "login", "signin"],
            "textbox": ["input", "field", "username", "email", "password", "search", "text"],
            "searchbox": ["search", "find", "query", "filter"],
            "combobox": ["dropdown", "select", "combo", "picker"],
            "listbox": ["list", "options", "choices"],
            "menu": ["menu", "navigation", "nav"],
            "menubar": ["menubar", "navigation", "nav"],
            "menuitem": ["menu item", "option", "choice"],
            "tab": ["tab", "panel", "section"],
            "tablist": ["tabs", "tab group"],
            "tabpanel": ["tab content", "panel"],
            "dialog": ["modal", "popup", "overlay", "dialog"],
            "alertdialog": ["alert", "warning", "error dialog"],
            "navigation": ["nav", "navigation", "menu"],
            "main": ["main", "content", "primary"],
            "banner": ["header", "banner", "top"],
            "contentinfo": ["footer", "bottom", "info"],
            "complementary": ["sidebar", "aside", "secondary"],
            "form": ["form", "input form", "data entry"],
            "search": ["search", "find", "lookup"],
            "region": ["region", "section", "area"],
            "link": ["link", "url", "href", "navigate"],
            "heading": ["heading", "title", "header"],
            "img": ["image", "picture", "photo", "icon"],
            "checkbox": ["checkbox", "check", "option"],
            "radio": ["radio", "option", "choice"],
            "switch": ["switch", "toggle", "on/off"],
            "slider": ["slider", "range", "scale"],
            "progressbar": ["progress", "loading", "completion"],
            "status": ["status", "state", "info"],
            "alert": ["alert", "warning", "notification"],
            "log": ["log", "history", "messages"],
            "marquee": ["marquee", "scrolling", "ticker"],
            "timer": ["timer", "countdown", "clock"],
            "tooltip": ["tooltip", "help", "hint"]
        }
        
        # Common ARIA label patterns
        self.aria_label_patterns = {
            "login": [
                "log in", "sign in", "signin", "login", "authenticate", "enter"
            ],
            "logout": [
                "log out", "sign out", "signout", "logout", "exit"
            ],
            "username": [
                "username", "user name", "email", "login id", "user id", "account"
            ],
            "password": [
                "password", "pass", "secret", "credentials", "pin"
            ],
            "search": [
                "search", "find", "look up", "query", "filter"
            ],
            "save": [
                "save", "submit", "confirm", "apply", "accept", "ok"
            ],
            "cancel": [
                "cancel", "close", "dismiss", "abort", "reject", "no"
            ],
            "home": [
                "home", "dashboard", "main", "start", "overview"
            ],
            "menu": [
                "menu", "navigation", "nav", "options", "settings"
            ],
            "help": [
                "help", "support", "assistance", "info", "about"
            ]
        }
        
        # Landmark roles for navigation
        self.landmark_roles = [
            "banner", "navigation", "main", "complementary", 
            "contentinfo", "search", "form", "region"
        ]
        
        # Input type to ARIA role mappings
        self.input_aria_mappings = {
            "email": "textbox",
            "password": "textbox", 
            "text": "textbox",
            "search": "searchbox",
            "tel": "textbox",
            "url": "textbox",
            "number": "spinbutton",
            "range": "slider",
            "checkbox": "checkbox",
            "radio": "radio",
            "submit": "button",
            "button": "button",
            "reset": "button"
        }
    
    async def generate_strategies(
        self, 
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on accessibility attributes and ARIA patterns."""
        
        strategies = []
        
        # Get HTML content
        if hasattr(page, 'content'):
            html_content = await page.content()
        else:
            html_content = context.html_content or ""
        
        if not html_content:
            return strategies
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Strategy 1: ARIA role-based selection
        role_strategies = self._generate_aria_role_strategies(soup, context)
        strategies.extend(role_strategies)
        
        # Strategy 2: ARIA label and labelledby
        label_strategies = self._generate_aria_label_strategies(soup, context)
        strategies.extend(label_strategies)
        
        # Strategy 3: ARIA describedby and description
        description_strategies = self._generate_aria_description_strategies(soup, context)
        strategies.extend(description_strategies)
        
        # Strategy 4: Landmark navigation
        landmark_strategies = self._generate_landmark_strategies(soup, context)
        strategies.extend(landmark_strategies)
        
        # Strategy 5: Form accessibility patterns
        form_strategies = self._generate_form_accessibility_strategies(soup, context)
        strategies.extend(form_strategies)
        
        # Strategy 6: Screen reader text patterns
        screen_reader_strategies = self._generate_screen_reader_strategies(soup, context)
        strategies.extend(screen_reader_strategies)
        
        return strategies
    
    def _generate_aria_role_strategies(
        self, 
        soup: BeautifulSoup, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on ARIA roles."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Find the most relevant ARIA role for the intent
        relevant_roles = []
        for role, keywords in self.aria_role_mappings.items():
            if any(keyword in intent_lower for keyword in keywords):
                relevant_roles.append(role)
        
        # Generate strategies for each relevant role
        for role in relevant_roles:
            confidence = 0.85 if role in ["button", "textbox", "searchbox"] else 0.75
            
            strategies.append(ElementStrategy(
                selector=f"[role='{role}']",
                confidence=confidence,
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.INSTANT,
                reasoning=f"Element with ARIA role '{role}'"
            ))
            
            # Also check for implicit roles (native HTML elements)
            if role == "button":
                strategies.append(ElementStrategy(
                    selector="button",
                    confidence=0.80,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.INSTANT,
                    reasoning="Native button element (implicit button role)"
                ))
                
                strategies.append(ElementStrategy(
                    selector="input[type='submit']",
                    confidence=0.75,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.INSTANT,
                    reasoning="Submit input (implicit button role)"
                ))
            
            elif role == "textbox":
                strategies.extend([
                    ElementStrategy(
                        selector="input[type='text']",
                        confidence=0.75,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.INSTANT,
                        reasoning="Text input (implicit textbox role)"
                    ),
                    ElementStrategy(
                        selector="input[type='email']",
                        confidence=0.80,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.INSTANT,
                        reasoning="Email input (implicit textbox role)"
                    ),
                    ElementStrategy(
                        selector="input[type='password']",
                        confidence=0.80,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.INSTANT,
                        reasoning="Password input (implicit textbox role)"
                    ),
                    ElementStrategy(
                        selector="textarea",
                        confidence=0.75,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.INSTANT,
                        reasoning="Textarea (implicit textbox role)"
                    )
                ])
            
            elif role == "searchbox":
                strategies.append(ElementStrategy(
                    selector="input[type='search']",
                    confidence=0.85,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.INSTANT,
                    reasoning="Search input (implicit searchbox role)"
                ))
        
        return strategies
    
    def _generate_aria_label_strategies(
        self, 
        soup: BeautifulSoup, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on ARIA labels."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Find relevant label patterns
        relevant_patterns = []
        for intent_key, patterns in self.aria_label_patterns.items():
            if intent_key in intent_lower:
                relevant_patterns.extend(patterns)
        
        # Also extract key words from intent
        intent_words = re.findall(r'\b\w+\b', intent_lower)
        relevant_patterns.extend(intent_words)
        
        # Generate strategies for aria-label
        for pattern in relevant_patterns:
            strategies.extend([
                ElementStrategy(
                    selector=f"[aria-label*='{pattern}' i]",
                    confidence=0.80,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.INSTANT,
                    reasoning=f"Element with aria-label containing '{pattern}'"
                ),
                ElementStrategy(
                    selector=f"[aria-label='{pattern}' i]",
                    confidence=0.85,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.INSTANT,
                    reasoning=f"Element with exact aria-label '{pattern}'"
                )
            ])
        
        # Generate strategies for aria-labelledby
        # Find elements that could be labels
        label_elements = soup.find_all(['label', 'span', 'div'], 
                                     string=lambda text: text and any(pattern in text.lower() 
                                                                    for pattern in relevant_patterns))
        
        for label_elem in label_elements:
            if label_elem.get('id'):
                strategies.append(ElementStrategy(
                    selector=f"[aria-labelledby='{label_elem['id']}']",
                    confidence=0.75,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning=f"Element labeled by '{label_elem.get_text().strip()}'"
                ))
        
        return strategies
    
    def _generate_aria_description_strategies(
        self, 
        soup: BeautifulSoup, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on ARIA descriptions."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Extract key words from intent
        intent_words = re.findall(r'\b\w+\b', intent_lower)
        
        # Generate strategies for aria-description
        for word in intent_words:
            if len(word) > 2:  # Skip very short words
                strategies.append(ElementStrategy(
                    selector=f"[aria-description*='{word}' i]",
                    confidence=0.65,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning=f"Element with aria-description containing '{word}'"
                ))
        
        # Generate strategies for aria-describedby
        description_elements = soup.find_all(['div', 'span', 'p'], 
                                           string=lambda text: text and any(word in text.lower() 
                                                                          for word in intent_words))
        
        for desc_elem in description_elements:
            if desc_elem.get('id'):
                strategies.append(ElementStrategy(
                    selector=f"[aria-describedby='{desc_elem['id']}']",
                    confidence=0.60,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning=f"Element described by '{desc_elem.get_text().strip()[:50]}...'"
                ))
        
        return strategies
    
    def _generate_landmark_strategies(
        self, 
        soup: BeautifulSoup, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on ARIA landmarks."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Map intents to landmarks
        landmark_mappings = {
            "navigation": ["nav", "menu", "home"],
            "search": ["search", "find"],
            "main": ["main", "content", "primary"],
            "banner": ["header", "top", "title"],
            "contentinfo": ["footer", "bottom", "info"],
            "form": ["form", "input", "login", "signup"],
            "complementary": ["sidebar", "aside", "secondary"]
        }
        
        for landmark, keywords in landmark_mappings.items():
            if any(keyword in intent_lower for keyword in keywords):
                # Look within the landmark
                strategies.extend([
                    ElementStrategy(
                        selector=f"[role='{landmark}'] button",
                        confidence=0.70,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Button within {landmark} landmark"
                    ),
                    ElementStrategy(
                        selector=f"[role='{landmark}'] input",
                        confidence=0.70,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Input within {landmark} landmark"
                    ),
                    ElementStrategy(
                        selector=f"[role='{landmark}'] a",
                        confidence=0.65,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Link within {landmark} landmark"
                    )
                ])
                
                # Also check native HTML5 landmarks
                if landmark == "navigation":
                    strategies.extend([
                        ElementStrategy(
                            selector="nav button",
                            confidence=0.75,
                            strategy_type=self.layer_type,
                            performance_tier=PerformanceTier.INSTANT,
                            reasoning="Button within nav element"
                        ),
                        ElementStrategy(
                            selector="nav a",
                            confidence=0.80,
                            strategy_type=self.layer_type,
                            performance_tier=PerformanceTier.INSTANT,
                            reasoning="Link within nav element"
                        )
                    ])
                
                elif landmark == "main":
                    strategies.extend([
                        ElementStrategy(
                            selector="main button",
                            confidence=0.70,
                            strategy_type=self.layer_type,
                            performance_tier=PerformanceTier.INSTANT,
                            reasoning="Button within main element"
                        ),
                        ElementStrategy(
                            selector="main input",
                            confidence=0.70,
                            strategy_type=self.layer_type,
                            performance_tier=PerformanceTier.INSTANT,
                            reasoning="Input within main element"
                        )
                    ])
        
        return strategies
    
    def _generate_form_accessibility_strategies(
        self, 
        soup: BeautifulSoup, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on form accessibility patterns."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Form label associations
        if any(word in intent_lower for word in ["input", "field", "username", "password", "email"]):
            # Look for label elements
            intent_words = re.findall(r'\b\w+\b', intent_lower)
            
            labels = soup.find_all('label')
            for label in labels:
                label_text = label.get_text().lower()
                
                # Check if label text matches intent
                if any(word in label_text for word in intent_words):
                    # If label has 'for' attribute
                    if label.get('for'):
                        strategies.append(ElementStrategy(
                            selector=f"#{label['for']}",
                            confidence=0.90,
                            strategy_type=self.layer_type,
                            performance_tier=PerformanceTier.INSTANT,
                            reasoning=f"Input labeled by '{label_text.strip()}'"
                        ))
                    
                    # If label wraps the input
                    input_in_label = label.find('input')
                    if input_in_label:
                        input_selector = self._generate_element_selector(input_in_label)
                        strategies.append(ElementStrategy(
                            selector=input_selector,
                            confidence=0.85,
                            strategy_type=self.layer_type,
                            performance_tier=PerformanceTier.INSTANT,
                            reasoning=f"Input wrapped by label '{label_text.strip()}'"
                        ))
        
        # Required field indicators
        if "required" not in intent_lower:  # Don't double-add if already specified
            strategies.extend([
                ElementStrategy(
                    selector="[required]",
                    confidence=0.60,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning="Required form field"
                ),
                ElementStrategy(
                    selector="[aria-required='true']",
                    confidence=0.60,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning="ARIA required form field"
                )
            ])
        
        # Invalid/error states
        if any(word in intent_lower for word in ["error", "invalid", "warning"]):
            strategies.extend([
                ElementStrategy(
                    selector="[aria-invalid='true']",
                    confidence=0.80,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.INSTANT,
                    reasoning="Field marked as invalid"
                ),
                ElementStrategy(
                    selector=".error, .invalid, [data-error]",
                    confidence=0.70,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning="Element with error styling or attribute"
                )
            ])
        
        return strategies
    
    def _generate_screen_reader_strategies(
        self, 
        soup: BeautifulSoup, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies based on screen reader patterns."""
        
        strategies = []
        intent_lower = context.intent.lower()
        
        # Screen reader only text (usually hidden visually)
        sr_only_classes = ['.sr-only', '.screen-reader-text', '.visually-hidden', '.sr-text']
        
        for sr_class in sr_only_classes:
            elements = soup.select(sr_class)
            for element in elements:
                element_text = element.get_text().lower()
                intent_words = re.findall(r'\b\w+\b', intent_lower)
                
                if any(word in element_text for word in intent_words):
                    # Look for interactive elements near this screen reader text
                    parent = element.parent
                    if parent:
                        buttons = parent.find_all('button')
                        inputs = parent.find_all('input')
                        links = parent.find_all('a')
                        
                        for interactive in buttons + inputs + links:
                            selector = self._generate_element_selector(interactive)
                            strategies.append(ElementStrategy(
                                selector=selector,
                                confidence=0.75,
                                strategy_type=self.layer_type,
                                performance_tier=PerformanceTier.FAST,
                                reasoning=f"Interactive element near screen reader text '{element_text.strip()}'"
                            ))
        
        # Elements with aria-hidden="false" (explicitly shown to screen readers)
        strategies.extend([
            ElementStrategy(
                selector="[aria-hidden='false']",
                confidence=0.65,
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.FAST,
                reasoning="Element explicitly shown to screen readers"
            )
        ])
        
        # Live regions for dynamic content
        if any(word in intent_lower for word in ["status", "alert", "message", "notification"]):
            strategies.extend([
                ElementStrategy(
                    selector="[aria-live='polite']",
                    confidence=0.70,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning="Polite live region for status updates"
                ),
                ElementStrategy(
                    selector="[aria-live='assertive']",
                    confidence=0.75,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning="Assertive live region for urgent updates"
                ),
                ElementStrategy(
                    selector="[role='status']",
                    confidence=0.80,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.INSTANT,
                    reasoning="Status role element"
                ),
                ElementStrategy(
                    selector="[role='alert']",
                    confidence=0.85,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.INSTANT,
                    reasoning="Alert role element"
                )
            ])
        
        return strategies
    
    def _generate_element_selector(self, element: Tag) -> str:
        """Generate a CSS selector for a given element."""
        
        # Use ID if available
        if element.get('id'):
            return f"#{element['id']}"
        
        # Use unique attribute combinations
        selectors = [element.name]
        
        # Add type if it's an input
        if element.name == 'input' and element.get('type'):
            selectors.append(f"[type='{element['type']}']")
        
        # Add important classes
        if element.get('class'):
            important_classes = [cls for cls in element['class'] 
                               if not cls.startswith(('css-', 'MuiBox-', 'makeStyles-'))]
            if important_classes:
                selectors.append(f".{'.'.join(important_classes[:2])}")  # Max 2 classes
        
        # Add name attribute if available
        if element.get('name'):
            selectors.append(f"[name='{element['name']}']")
        
        return ''.join(selectors)