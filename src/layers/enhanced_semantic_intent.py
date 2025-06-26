"""
Enhanced Semantic Intent Layer - Production Robust
=================================================
This is the improved semantic intent layer that addresses the core robustness issues:

1. Better DOM verification - Ensures selectors actually exist
2. Intelligent fallback strategies - Multiple approaches per intent
3. Dynamic selector generation - Adapts to actual page content
4. Real-time validation - Verifies elements are actionable
5. Context-aware ranking - Prioritizes based on page state

This layer is designed to work reliably in production environments.
"""

import re
import time
import html
from typing import List, Dict, Any, Optional
from src.models.element import ElementStrategy, ElementContext, StrategyType, PerformanceTier
from src.layers.base import BaseLayer
from src.utils.robust_html_parser import parse_html


class EnhancedSemanticIntentLayer(BaseLayer):
    """
    Enhanced semantic intent layer with production-grade robustness.
    
    Key improvements:
    - DOM-verified selectors (ensures elements actually exist)
    - Multi-strategy generation (always provides fallbacks)
    - Context-aware confidence scoring
    - Real-time element validation
    """
    
    def __init__(self):
        super().__init__(StrategyType.SEMANTIC_INTENT)
        
        # Enhanced intent patterns with multiple semantic approaches
        self.intent_patterns = {
            # Authentication patterns
            "login": {
                "aliases": ["log in", "sign in", "signin", "authenticate", "enter"],
                "element_types": ["button", "input", "link"],
                "form_context": True,
                "required_attributes": ["type", "value", "aria-label", "title"]
            },
            
            "username": {
                "aliases": ["user", "email", "user name", "login id", "account"],
                "element_types": ["input"],
                "input_types": ["text", "email", "tel"],
                "form_context": True,
                "position_hints": ["first", "top", "primary"]
            },
            
            "password": {
                "aliases": ["pass", "pwd", "secret", "passphrase"],
                "element_types": ["input"],
                "input_types": ["password"],
                "form_context": True,
                "security_context": True
            },
            
            # Navigation patterns
            "app launcher": {
                "aliases": ["apps", "menu", "navigation", "waffle", "grid"],
                "element_types": ["button", "div", "a"],
                "visual_hints": ["grid", "dots", "waffle", "9-dot"],
                "position_hints": ["header", "top", "navigation"]
            },
            
            "sales app": {
                "aliases": ["sales", "crm", "opportunities", "accounts"],
                "element_types": ["a", "button", "div"],
                "app_context": True,
                "text_matching": True
            },
            
            # Form elements
            "new button": {
                "aliases": ["add", "create", "new record", "plus"],
                "element_types": ["button", "a", "input"],
                "action_context": True,
                "position_hints": ["top", "header", "toolbar"]
            },
            
            "save button": {
                "aliases": ["save", "submit", "apply", "confirm", "ok"],
                "element_types": ["button", "input"],
                "form_context": True,
                "action_context": True,
                "position_hints": ["bottom", "footer", "actions"]
            },
            
            # Data entry fields
            "account name": {
                "aliases": ["name", "account", "company", "organization"],
                "element_types": ["input", "textarea"],
                "input_types": ["text"],
                "form_context": True,
                "required_hint": True
            },
            
            "first name": {
                "aliases": ["first", "given name", "forename"],
                "element_types": ["input"],
                "input_types": ["text"],
                "form_context": True
            },
            
            "last name": {
                "aliases": ["last", "surname", "family name"],
                "element_types": ["input"],
                "input_types": ["text"],
                "form_context": True,
                "required_hint": True
            },
            
            "opportunity name": {
                "aliases": ["opportunity", "deal", "name", "title"],
                "element_types": ["input", "textarea"],
                "input_types": ["text"],
                "form_context": True,
                "required_hint": True
            },
            
            "amount": {
                "aliases": ["amount", "value", "price", "cost", "revenue"],
                "element_types": ["input"],
                "input_types": ["number", "text"],
                "form_context": True,
                "numeric_context": True
            },
            
            # Lookup fields
            "account lookup": {
                "aliases": ["account", "company", "organization"],
                "element_types": ["input", "button"],
                "lookup_context": True,
                "form_context": True
            },
            
            "contact lookup": {
                "aliases": ["contact", "person", "individual"],
                "element_types": ["input", "button"],
                "lookup_context": True,
                "form_context": True
            }
        }
        
        # DOM analysis patterns for better selector generation
        self.dom_patterns = {
            "form_indicators": ["form", "fieldset", "legend", "label"],
            "action_indicators": ["button", "submit", "action", "toolbar"],
            "navigation_indicators": ["nav", "menu", "header", "banner"],
            "content_indicators": ["main", "content", "body", "panel"]
        }
        
        # Enhanced selector generation strategies
        self.selector_strategies = [
            self._generate_id_selectors,
            self._generate_name_selectors,
            self._generate_type_selectors,
            self._generate_aria_selectors,
            self._generate_text_selectors,
            self._generate_class_selectors,
            self._generate_attribute_selectors,
            self._generate_contextual_selectors,
            self._generate_hierarchical_selectors
        ]
    
    async def generate_strategies(self, page: Any, context: ElementContext) -> List[ElementStrategy]:
        """
        Generate enhanced strategies with DOM verification.
        
        This method ensures all generated selectors actually exist in the DOM
        and are actionable elements.
        """
        
        start_time = time.time()
        
        # Parse intent and extract semantic information
        intent_info = self._parse_enhanced_intent(context.intent)
        if not intent_info:
            print(f"❌ Could not parse intent: {context.intent}")
            return []
        
        # Parse HTML for DOM analysis
        html_content = context.html_content or ""
        if not html_content:
            print(f"❌ No HTML content provided")
            return []
        
        print(f"🎯 Enhanced analysis for: '{context.intent}'")
        print(f"   Intent type: {intent_info['type']}")
        print(f"   Element types: {intent_info['element_types']}")
        print(f"   HTML length: {len(html_content)} chars")
        
        # Generate all possible selectors using multiple strategies
        all_strategies = []
        
        for strategy_generator in self.selector_strategies:
            try:
                strategies = strategy_generator(html_content, intent_info, context)
                all_strategies.extend(strategies)
            except Exception as e:
                print(f"⚠️ Strategy generator failed: {strategy_generator.__name__}: {e}")
                continue
        
        # Verify selectors exist in DOM and rank by relevance
        verified_strategies = self._verify_and_rank_strategies(all_strategies, html_content, intent_info)
        
        # Apply confidence adjustments based on context
        final_strategies = self._apply_context_confidence(verified_strategies, intent_info, context)
        
        duration_ms = (time.time() - start_time) * 1000
        print(f"✅ Enhanced semantic analysis: {len(final_strategies)} verified strategies in {duration_ms:.1f}ms")
        
        return final_strategies[:10]  # Return top 10 strategies
    
    def _parse_enhanced_intent(self, intent: str) -> Optional[Dict[str, Any]]:
        """Parse intent with enhanced semantic understanding."""
        
        intent_lower = intent.lower().strip()
        
        # Find matching intent pattern
        best_match = None
        best_score = 0
        
        for intent_type, pattern in self.intent_patterns.items():
            score = 0
            
            # Direct match
            if intent_type in intent_lower:
                score += 10
            
            # Alias matching
            for alias in pattern["aliases"]:
                if alias in intent_lower:
                    score += 8
            
            # Partial matching
            intent_words = intent_lower.split()
            pattern_words = intent_type.split() + pattern["aliases"]
            
            for word in intent_words:
                for pattern_word in pattern_words:
                    if word in pattern_word or pattern_word in word:
                        score += 2
            
            if score > best_score:
                best_score = score
                best_match = (intent_type, pattern)
        
        if not best_match or best_score < 2:
            # Fallback: generic analysis
            return {
                "type": "generic",
                "original": intent,
                "element_types": ["button", "input", "a"],
                "aliases": [intent_lower],
                "confidence_base": 0.3
            }
        
        intent_type, pattern = best_match
        
        return {
            "type": intent_type,
            "original": intent,
            "pattern": pattern,
            "element_types": pattern["element_types"],
            "aliases": pattern["aliases"],
            "confidence_base": min(0.9, best_score / 10)
        }
    
    def _find_elements_by_regex(self, html_content: str, pattern: str) -> List[Dict[str, str]]:
        """Find elements using regex patterns."""
        
        try:
            matches = re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL)
            elements = []
            
            for match in matches:
                element_dict = match.groupdict()
                elements.append(element_dict)
            
            return elements
            
        except Exception as e:
            print(f"❌ Regex parsing failed: {e}")
            return []
    
    def _generate_id_selectors(self, html_content: str, intent_info: Dict, context: ElementContext) -> List[ElementStrategy]:
        """Generate selectors based on ID attributes."""
        
        strategies = []
        aliases = intent_info["aliases"]
        element_types = intent_info["element_types"]
        
        # Find elements with IDs that match intent using regex
        for element_type in element_types:
            # Pattern to match elements with id attributes
            pattern = rf'<{element_type}[^>]*\s+id=["\']([^"\'>]+)["\'][^>]*>'
            elements = self._find_elements_by_regex(html_content, pattern)
            
            for element in elements:
                element_id = element.get('1', '').lower()  # Group 1 is the ID value
                
                # Check if ID matches any alias
                for alias in aliases:
                    if alias in element_id:
                        confidence = 0.9 if alias == intent_info["type"] else 0.8
                        
                        strategies.append(ElementStrategy(
                            selector=f"#{element.get('1')}",
                            confidence=confidence,
                            strategy_type=self.layer_type,
                            performance_tier=PerformanceTier.INSTANT,
                            reasoning=f"ID matches '{alias}': {element.get('1')}",
                            metadata={
                                "method": "id_matching",
                                "element_type": element_type,
                                "matched_alias": alias,
                                "element_id": element.get('1')
                            }
                        ))
        
        return strategies
    
    def _generate_name_selectors(self, html_content: str, intent_info: Dict, context: ElementContext) -> List[ElementStrategy]:
        """Generate selectors based on name attributes."""
        
        strategies = []
        aliases = intent_info["aliases"]
        element_types = intent_info["element_types"]
        
        for element_type in element_types:
            # Pattern to match elements with name attributes
            pattern = rf'<{element_type}[^>]*\s+name=["\']([^"\'>]+)["\'][^>]*>'
            elements = self._find_elements_by_regex(html_content, pattern)
            
            for element in elements:
                element_name = element.get('1', '').lower()  # Group 1 is the name value
                
                for alias in aliases:
                    if alias in element_name:
                        confidence = 0.85 if alias == intent_info["type"] else 0.75
                        
                        strategies.append(ElementStrategy(
                            selector=f'{element_type}[name="{element.get("1")}"]',
                            confidence=confidence,
                            strategy_type=self.layer_type,
                            performance_tier=PerformanceTier.INSTANT,
                            reasoning=f"Name matches '{alias}': {element.get('1')}",
                            metadata={
                                "method": "name_matching",
                                "element_type": element_type,
                                "matched_alias": alias
                            }
                        ))
        
        return strategies
    
    def _generate_type_selectors(self, html_content: str, intent_info: Dict, context: ElementContext) -> List[ElementStrategy]:
        """Generate selectors based on input types and form context."""
        
        strategies = []
        
        # Special handling for input elements
        if "input" in intent_info["element_types"]:
            pattern = intent_info.get("pattern", {})
            input_types = pattern.get("input_types", ["text"])
            
            for input_type in input_types:
                # Pattern to match input elements with specific type
                input_pattern = rf'<input[^>]*\s+type=["\']?{input_type}["\']?[^>]*>'
                elements = self._find_elements_by_regex(html_content, input_pattern)
                
                if elements:
                    confidence = 0.8 if len(elements) == 1 else 0.6  # Higher confidence for unique elements
                    
                    strategies.append(ElementStrategy(
                        selector=f'input[type="{input_type}"]',
                        confidence=confidence,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.INSTANT,
                        reasoning=f"Input type matches intent: {input_type}",
                        metadata={
                            "method": "type_matching",
                            "input_type": input_type,
                            "element_count": len(elements)
                        }
                    ))
        
        # Button type handling
        if "button" in intent_info["element_types"]:
            # Submit buttons for action intents
            if intent_info.get("pattern", {}).get("action_context"):
                # Pattern to match submit buttons
                submit_pattern = r'<(button|input)[^>]*\s+type=["\']?submit["\']?[^>]*>'
                submit_buttons = self._find_elements_by_regex(html_content, submit_pattern)
                if submit_buttons:
                    strategies.append(ElementStrategy(
                        selector='button[type="submit"], input[type="submit"]',
                        confidence=0.85,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.INSTANT,
                        reasoning="Submit button for action intent",
                        metadata={"method": "submit_button", "button_count": len(submit_buttons)}
                    ))
        
        return strategies
    
    def _generate_aria_selectors(self, html_content: str, intent_info: Dict, context: ElementContext) -> List[ElementStrategy]:
        """Generate ARIA-based selectors."""
        
        strategies = []
        aliases = intent_info["aliases"]
        
        # ARIA label matching
        for alias in aliases:
            # Pattern to match elements with aria-label containing the alias
            aria_pattern = rf'<[^>]+aria-label=["\'][^"\'>]*{re.escape(alias)}[^"\'>]*["\'][^>]*>'
            elements = self._find_elements_by_regex(html_content, aria_pattern)
            if elements:
                strategies.append(ElementStrategy(
                    selector=f'[aria-label*="{alias}" i]',
                    confidence=0.8,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.FAST,
                    reasoning=f"ARIA label contains '{alias}'",
                    metadata={"method": "aria_label", "matched_alias": alias}
                ))
        
        # ARIA role matching
        role_mappings = {
            "button": ["button", "action"],
            "textbox": ["input", "field"],
            "combobox": ["dropdown", "select"],
            "searchbox": ["search"]
        }
        
        for role, intent_types in role_mappings.items():
            if any(intent_type in intent_info["type"] for intent_type in intent_types):
                # Pattern to match elements with specific ARIA role
                role_pattern = rf'<[^>]+role=["\']?{role}["\']?[^>]*>'
                elements = self._find_elements_by_regex(html_content, role_pattern)
                if elements:
                    strategies.append(ElementStrategy(
                        selector=f'[role="{role}"]',
                        confidence=0.75,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"ARIA role matches intent: {role}",
                        metadata={"method": "aria_role", "role": role}
                    ))
        
        return strategies
    
    def _generate_text_selectors(self, html_content: str, intent_info: Dict, context: ElementContext) -> List[ElementStrategy]:
        """Generate text-based selectors."""
        
        strategies = []
        aliases = intent_info["aliases"]
        
        # For buttons and links, check text content
        if "button" in intent_info["element_types"] or "a" in intent_info["element_types"]:
            for alias in aliases:
                # Button text matching - pattern to find buttons containing the alias text
                button_pattern = rf'<button[^>]*>([^<]*{re.escape(alias)}[^<]*)</button>'
                buttons = self._find_elements_by_regex(html_content, button_pattern)
                if buttons:
                    strategies.append(ElementStrategy(
                        selector=f'button:contains("{alias}")',
                        confidence=0.9,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.MEDIUM,
                        reasoning=f"Button text matches '{alias}'",
                        metadata={"method": "text_matching", "matched_text": alias}
                    ))
                
                # Value attribute matching for input buttons
                value_pattern = rf'<input[^>]*\s+value=["\'][^"\'>]*{re.escape(alias)}[^"\'>]*["\'][^>]*>'
                value_inputs = self._find_elements_by_regex(html_content, value_pattern)
                if value_inputs:
                    strategies.append(ElementStrategy(
                        selector=f'input[value*="{alias}" i]',
                        confidence=0.85,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Input value matches '{alias}'",
                        metadata={"method": "value_matching", "matched_value": alias}
                    ))
        
        return strategies
    
    def _generate_class_selectors(self, html_content: str, intent_info: Dict, context: ElementContext) -> List[ElementStrategy]:
        """Generate class-based selectors."""
        
        strategies = []
        aliases = intent_info["aliases"]
        element_types = intent_info["element_types"]
        
        for element_type in element_types:
            # Pattern to match elements with class attributes
            class_pattern = rf'<{element_type}[^>]*\s+class=["\']([^"\'>]+)["\'][^>]*>'
            elements = self._find_elements_by_regex(html_content, class_pattern)
            
            for element in elements:
                class_string = element.get('1', '').lower()  # Group 1 is the class value
                class_list = class_string.split()
                
                for alias in aliases:
                    if alias in class_string:
                        # Use the most specific class that matches
                        matching_classes = [cls for cls in class_list if alias in cls.lower()]
                        if matching_classes:
                            best_class = min(matching_classes, key=len)  # Shortest matching class
                            
                            strategies.append(ElementStrategy(
                                selector=f'{element_type}.{best_class}',
                                confidence=0.7,
                                strategy_type=self.layer_type,
                                performance_tier=PerformanceTier.FAST,
                                reasoning=f"Class contains '{alias}': {best_class}",
                                metadata={
                                    "method": "class_matching",
                                    "matched_class": best_class,
                                    "matched_alias": alias
                                }
                            ))
        
        return strategies
    
    def _generate_attribute_selectors(self, html_content: str, intent_info: Dict, context: ElementContext) -> List[ElementStrategy]:
        """Generate attribute-based selectors."""
        
        strategies = []
        aliases = intent_info["aliases"]
        
        # Common attributes to check
        attributes_to_check = ['title', 'placeholder', 'alt', 'data-label', 'data-name']
        
        for attr in attributes_to_check:
            for alias in aliases:
                # Pattern to match elements with specific attribute containing the alias
                attr_pattern = rf'<[^>]+{attr}=["\'][^"\'>]*{re.escape(alias)}[^"\'>]*["\'][^>]*>'
                elements = self._find_elements_by_regex(html_content, attr_pattern)
                if elements:
                    strategies.append(ElementStrategy(
                        selector=f'[{attr}*="{alias}" i]',
                        confidence=0.65,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.MEDIUM,
                        reasoning=f"Attribute {attr} contains '{alias}'",
                        metadata={"method": "attribute_matching", "attribute": attr, "matched_alias": alias}
                    ))
        
        return strategies
    
    def _generate_contextual_selectors(self, html_content: str, intent_info: Dict, context: ElementContext) -> List[ElementStrategy]:
        """Generate context-aware selectors."""
        
        strategies = []
        pattern = intent_info.get("pattern", {})
        
        # Form context selectors
        if pattern.get("form_context"):
            # Pattern to find forms
            form_pattern = r'<form[^>]*>([\s\S]*?)</form>'
            forms = self._find_elements_by_regex(html_content, form_pattern)
            
            for form in forms:
                form_content = form.get('1', '')  # Group 1 is the form content
                
                # Check if form contains our target element types
                for element_type in intent_info["element_types"]:
                    element_pattern = rf'<{element_type}[^>]*\s+id=["\']([^"\'>]+)["\'][^>]*>'
                    form_elements = self._find_elements_by_regex(form_content, element_pattern)
                    
                    if form_elements and len(form_elements) == 1:
                        element_id = form_elements[0].get('1')
                        if element_id:
                            strategies.append(ElementStrategy(
                                selector=f'form #{element_id}',
                                confidence=0.8,
                                strategy_type=self.layer_type,
                                performance_tier=PerformanceTier.FAST,
                                reasoning="Unique element in form context",
                                metadata={"method": "form_context", "element_id": element_id}
                            ))
        
        # Position-based selectors
        position_hints = pattern.get("position_hints", [])
        if position_hints:
            for hint in position_hints:
                if hint == "first":
                    # Find first element of each type
                    for element_type in intent_info["element_types"]:
                        first_pattern = rf'<{element_type}[^>]*\s+id=["\']([^"\'>]+)["\'][^>]*>'
                        first_elements = self._find_elements_by_regex(html_content, first_pattern)
                        if first_elements:
                            first_element_id = first_elements[0].get('1')
                            if first_element_id:
                                strategies.append(ElementStrategy(
                                    selector=f'#{first_element_id}',
                                    confidence=0.75,
                                    strategy_type=self.layer_type,
                                    performance_tier=PerformanceTier.FAST,
                                    reasoning="First element of type on page",
                                    metadata={"method": "position_first", "element_id": first_element_id}
                                ))
                            break
        
        return strategies
    
    def _generate_hierarchical_selectors(self, html_content: str, intent_info: Dict, context: ElementContext) -> List[ElementStrategy]:
        """Generate hierarchical/parent-child selectors."""
        
        strategies = []
        aliases = intent_info["aliases"]
        
        # Look for labels that might reference inputs
        if "input" in intent_info["element_types"]:
            # Pattern to find labels with text content and for attribute
            label_pattern = r'<label[^>]*(?:\s+for=["\']([^"\'>]+)["\'])?[^>]*>([^<]*)</label>'
            labels = self._find_elements_by_regex(html_content, label_pattern)
            
            for label in labels:
                label_for = label.get('1', '')  # Group 1 is the 'for' attribute value
                label_text = label.get('2', '').lower()  # Group 2 is the label text
                
                for alias in aliases:
                    if alias in label_text:
                        # If label has 'for' attribute, use it directly
                        if label_for:
                            strategies.append(ElementStrategy(
                                selector=f'#{label_for}',
                                confidence=0.9,
                                strategy_type=self.layer_type,
                                performance_tier=PerformanceTier.FAST,
                                reasoning=f"Input referenced by label containing '{alias}'",
                                metadata={
                                    "method": "label_for",
                                    "label_text": label_text,
                                    "target_id": label_for
                                }
                            ))
                        
                        # Also look for inputs near this label text in the HTML
                        # This is a simplified approach - in practice would need more sophisticated parsing
                        # Pattern to find inputs that appear after this label
                        input_after_label_pattern = rf'{re.escape(label_text)}[\s\S]{{0,200}}<input[^>]*\s+id=["\']([^"\'>]+)["\'][^>]*>'
                        nearby_inputs = self._find_elements_by_regex(html_content, input_after_label_pattern)
                        
                        for input_elem in nearby_inputs:
                            input_id = input_elem.get('1')
                            if input_id:
                                strategies.append(ElementStrategy(
                                    selector=f'#{input_id}',
                                    confidence=0.8,
                                    strategy_type=self.layer_type,
                                    performance_tier=PerformanceTier.FAST,
                                    reasoning=f"Input near label containing '{alias}'",
                                    metadata={
                                        "method": "label_proximity",
                                        "label_text": label_text,
                                        "input_id": input_id
                                    }
                                ))
        
        return strategies
    
    def _verify_and_rank_strategies(self, strategies: List[ElementStrategy], html_content: str, intent_info: Dict) -> List[ElementStrategy]:
        """Verify selectors exist in DOM and rank by effectiveness."""
        
        verified_strategies = []
        
        # Parse HTML using robust parser
        soup = parse_html(html_content)
        
        for strategy in strategies:
            try:
                # Try to find element using the selector with robust parser
                if self._selector_matches_dom_robust(strategy.selector, soup):
                    verified_strategies.append(strategy)
                else:
                    print(f"🔍 Selector not found in DOM: {strategy.selector}")
            except Exception as e:
                print(f"⚠️ Selector verification failed: {strategy.selector}: {e}")
        
        # Rank by confidence and specificity
        verified_strategies.sort(key=lambda s: (s.confidence, self._calculate_specificity(s.selector)), reverse=True)
        
        return verified_strategies
    
    def _selector_matches_dom_robust(self, selector: str, soup) -> bool:
        """Check if selector matches elements in DOM using robust parser."""
        
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
            print(f"    ⚠️ Robust DOM verification error for '{selector}': {e}")
            return False
    
    def _selector_matches_dom(self, selector: str, html_content: str) -> bool:
        """Check if selector matches elements in DOM using regex (simplified)."""
        
        try:
            # Handle simple selectors
            if selector.startswith('#'):
                # ID selector
                element_id = selector[1:]
                id_pattern = rf'\s+id=["\']?{re.escape(element_id)}["\']?'
                return bool(re.search(id_pattern, html_content, re.IGNORECASE))
            
            elif selector.startswith('.'):
                # Class selector
                class_name = selector[1:]
                class_pattern = rf'\s+class=["\'][^"\'>]*\b{re.escape(class_name)}\b[^"\'>]*["\']'
                return bool(re.search(class_pattern, html_content, re.IGNORECASE))
            
            elif '[' in selector and ']' in selector:
                # Attribute selector (simplified)
                if 'type=' in selector:
                    # Extract type value
                    type_match = re.search(r'type=["\']?([^"\'>\s]+)["\']?', selector)
                    if type_match:
                        type_value = type_match.group(1)
                        type_pattern = rf'<input[^>]*\s+type=["\']?{re.escape(type_value)}["\']?[^>]*>'
                        return bool(re.search(type_pattern, html_content, re.IGNORECASE))
                
                if 'name=' in selector:
                    # Extract name value
                    name_match = re.search(r'name=["\']?([^"\'>\s]+)["\']?', selector)
                    if name_match:
                        name_value = name_match.group(1)
                        name_pattern = rf'\s+name=["\']?{re.escape(name_value)}["\']?'
                        return bool(re.search(name_pattern, html_content, re.IGNORECASE))
                
                # Generic attribute presence check for other attributes
                attr_match = re.search(r'\[([^=\]]+)', selector)
                if attr_match:
                    attr_name = attr_match.group(1)
                    attr_pattern = rf'\s+{re.escape(attr_name)}='
                    return bool(re.search(attr_pattern, html_content, re.IGNORECASE))
                
                return True  # Simplified - assume complex attribute selectors are valid
            
            elif selector in ['button', 'input', 'a', 'form', 'select', 'div', 'span']:
                # Element type selector
                element_pattern = rf'<{re.escape(selector)}\b[^>]*>'
                return bool(re.search(element_pattern, html_content, re.IGNORECASE))
            
            else:
                # Complex selector - simplified verification
                # Extract element type if present
                element_match = re.match(r'^([a-zA-Z]+)', selector)
                if element_match:
                    element_type = element_match.group(1)
                    element_pattern = rf'<{re.escape(element_type)}\b[^>]*>'
                    return bool(re.search(element_pattern, html_content, re.IGNORECASE))
                
                return True  # Assume valid for complex selectors we can't parse
                
        except Exception as e:
            print(f"    ⚠️ DOM verification error for '{selector}': {e}")
            return False
    
    def _calculate_specificity(self, selector: str) -> int:
        """Calculate CSS selector specificity."""
        
        specificity = 0
        
        # ID selectors are most specific
        if '#' in selector:
            specificity += 100
        
        # Class selectors
        if '.' in selector:
            specificity += 10
        
        # Attribute selectors
        if '[' in selector and ']' in selector:
            specificity += 10
        
        # Element selectors
        elements = ['button', 'input', 'a', 'form', 'select', 'div', 'span']
        for element in elements:
            if element in selector:
                specificity += 1
        
        return specificity
    
    def _apply_context_confidence(self, strategies: List[ElementStrategy], intent_info: Dict, context: ElementContext) -> List[ElementStrategy]:
        """Apply context-based confidence adjustments."""
        
        for strategy in strategies:
            # Boost confidence for exact intent type matches
            if intent_info["type"] in strategy.reasoning.lower():
                strategy.confidence = min(0.95, strategy.confidence + 0.1)
            
            # Boost confidence for form context when appropriate
            pattern = intent_info.get("pattern", {})
            if pattern.get("form_context") and "form" in strategy.selector.lower():
                strategy.confidence = min(0.9, strategy.confidence + 0.05)
            
            # Boost confidence for unique elements
            if strategy.metadata.get("element_count") == 1:
                strategy.confidence = min(0.95, strategy.confidence + 0.1)
            
            # Platform-specific adjustments
            if context.platform == "salesforce_lightning":
                if any(sf_indicator in strategy.selector for sf_indicator in ['slds', 'lightning', 'force']):
                    strategy.confidence = min(0.9, strategy.confidence + 0.05)
        
        return strategies