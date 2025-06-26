"""
Icon Recognition Layer for Helix AI Engine
==========================================
Handles icon-only buttons and elements with no text content
"""

from typing import List, Dict, Any, Optional
from src.models.element import ElementStrategy, ElementContext, StrategyType, PerformanceTier
from src.layers.base import BaseLayer


class IconRecognitionLayer(BaseLayer):
    """
    Specialized layer for icon-only elements.
    Critical for modern UIs that rely heavily on icons.
    """
    
    def __init__(self):
        super().__init__(StrategyType.VISUAL_FINGERPRINT)
        
        # Comprehensive icon pattern database
        self.icon_patterns = {
            "save": {
                "font_awesome": ["fa-save", "fa-floppy-disk", "fa-disk"],
                "material": ["save", "save_outlined", "storage"],
                "glyphicons": ["glyphicon-floppy-disk", "glyphicon-save"],
                "bootstrap": ["bi-save", "bi-floppy"],
                "custom": ["icon-save", "ico-save", "icon-disk"],
                "unicode": ["💾", "💿", "💽"],
                "css_content": ["\\f0c7", "\\e161"]  # Common save icon codes
            },
            "edit": {
                "font_awesome": ["fa-edit", "fa-pen", "fa-pencil"],
                "material": ["edit", "edit_outlined", "mode_edit"],
                "glyphicons": ["glyphicon-edit", "glyphicon-pencil"],
                "bootstrap": ["bi-pencil", "bi-pen"],
                "custom": ["icon-edit", "ico-edit", "icon-pencil"],
                "unicode": ["✏️", "📝", "🖊️"]
            },
            "delete": {
                "font_awesome": ["fa-trash", "fa-delete", "fa-remove"],
                "material": ["delete", "delete_outlined", "remove"],
                "glyphicons": ["glyphicon-trash", "glyphicon-remove"],
                "bootstrap": ["bi-trash", "bi-x"],
                "custom": ["icon-delete", "ico-trash", "icon-remove"],
                "unicode": ["🗑️", "❌", "🚮"]
            },
            "search": {
                "font_awesome": ["fa-search", "fa-magnifying-glass"],
                "material": ["search", "search_outlined"],
                "glyphicons": ["glyphicon-search"],
                "bootstrap": ["bi-search"],
                "custom": ["icon-search", "ico-search"],
                "unicode": ["🔍", "🔎"]
            },
            "close": {
                "font_awesome": ["fa-times", "fa-close", "fa-x"],
                "material": ["close", "close_outlined", "cancel"],
                "glyphicons": ["glyphicon-remove"],
                "bootstrap": ["bi-x", "bi-x-circle"],
                "custom": ["icon-close", "ico-close", "icon-x"],
                "unicode": ["❌", "✖️", "×"]
            },
            "add": {
                "font_awesome": ["fa-plus", "fa-add"],
                "material": ["add", "add_outlined", "plus_one"],
                "glyphicons": ["glyphicon-plus"],
                "bootstrap": ["bi-plus", "bi-plus-circle"],
                "custom": ["icon-add", "ico-plus", "icon-new"],
                "unicode": ["➕", "+"]
            },
            "home": {
                "font_awesome": ["fa-home", "fa-house"],
                "material": ["home", "home_outlined"],
                "glyphicons": ["glyphicon-home"],
                "bootstrap": ["bi-house", "bi-home"],
                "custom": ["icon-home", "ico-home"],
                "unicode": ["🏠", "🏡"]
            },
            "settings": {
                "font_awesome": ["fa-cog", "fa-gear", "fa-settings"],
                "material": ["settings", "settings_outlined"],
                "glyphicons": ["glyphicon-cog"],
                "bootstrap": ["bi-gear", "bi-tools"],
                "custom": ["icon-settings", "ico-settings", "icon-config"],
                "unicode": ["⚙️", "🔧"]
            }
        }
        
        # ARIA patterns for icon buttons
        self.aria_patterns = {
            "save": ["save", "save document", "save file"],
            "edit": ["edit", "modify", "change"],
            "delete": ["delete", "remove", "trash"],
            "search": ["search", "find", "lookup"],
            "close": ["close", "dismiss", "cancel"],
            "add": ["add", "create", "new"],
            "home": ["home", "main", "dashboard"],
            "settings": ["settings", "configure", "options"]
        }
    
    async def generate_strategies(
        self, 
        page: Any, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate icon recognition strategies."""
        
        strategies = []
        
        # Strategy 1: Icon library patterns
        strategies.extend(self._generate_icon_library_strategies(context))
        
        # Strategy 2: ARIA label strategies
        strategies.extend(self._generate_aria_strategies(context))
        
        # Strategy 3: CSS content strategies
        strategies.extend(self._generate_css_content_strategies(context))
        
        # Strategy 4: Unicode icon strategies
        strategies.extend(self._generate_unicode_strategies(context))
        
        # Strategy 5: Contextual icon strategies
        strategies.extend(self._generate_contextual_strategies(context))
        
        return strategies
    
    def _generate_icon_library_strategies(
        self, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate strategies for common icon libraries."""
        
        strategies = []
        intent_type = self._infer_icon_intent(context.intent.lower())
        
        if intent_type and intent_type in self.icon_patterns:
            patterns = self.icon_patterns[intent_type]
            
            # Font Awesome patterns
            for fa_class in patterns.get("font_awesome", []):
                strategies.extend([
                    ElementStrategy(
                        selector=f"i.{fa_class}",
                        confidence=0.85,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Font Awesome {intent_type} icon",
                        metadata={"icon_library": "font_awesome", "icon_type": intent_type}
                    ),
                    ElementStrategy(
                        selector=f"span.{fa_class}",
                        confidence=0.80,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Font Awesome {intent_type} icon (span)",
                        metadata={"icon_library": "font_awesome", "icon_type": intent_type}
                    ),
                    # Button containing icon
                    ElementStrategy(
                        selector=f"button i.{fa_class}",
                        confidence=0.90,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Button with Font Awesome {intent_type} icon",
                        metadata={"icon_library": "font_awesome", "button_icon": True}
                    ),
                    # Parent button of icon
                    ElementStrategy(
                        selector=f"i.{fa_class}:parent(button)",
                        confidence=0.85,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Button containing {intent_type} icon",
                        metadata={"find_parent": "button"}
                    )
                ])
            
            # Material Icons
            for mat_icon in patterns.get("material", []):
                strategies.extend([
                    ElementStrategy(
                        selector=f"i.material-icons:contains('{mat_icon}')",
                        confidence=0.85,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Material {intent_type} icon",
                        metadata={"icon_library": "material", "icon_type": intent_type}
                    ),
                    ElementStrategy(
                        selector=f"span.material-icons:contains('{mat_icon}')",
                        confidence=0.80,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Material {intent_type} icon (span)",
                        metadata={"icon_library": "material"}
                    )
                ])
            
            # Bootstrap Icons
            for bs_class in patterns.get("bootstrap", []):
                strategies.append(
                    ElementStrategy(
                        selector=f"i.{bs_class}",
                        confidence=0.80,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Bootstrap {intent_type} icon",
                        metadata={"icon_library": "bootstrap", "icon_type": intent_type}
                    )
                )
            
            # Custom icon patterns
            for custom_class in patterns.get("custom", []):
                strategies.append(
                    ElementStrategy(
                        selector=f"[class*='{custom_class}']",
                        confidence=0.70,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.MEDIUM,
                        reasoning=f"Custom {intent_type} icon class",
                        metadata={"icon_library": "custom", "icon_type": intent_type}
                    )
                )
        
        return strategies
    
    def _generate_aria_strategies(
        self, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate ARIA-based icon strategies."""
        
        strategies = []
        intent_type = self._infer_icon_intent(context.intent.lower())
        
        if intent_type and intent_type in self.aria_patterns:
            aria_labels = self.aria_patterns[intent_type]
            
            for label in aria_labels:
                strategies.extend([
                    ElementStrategy(
                        selector=f"[aria-label*='{label}' i]",
                        confidence=0.80,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"ARIA label for {intent_type}: {label}",
                        metadata={"detection_method": "aria_label", "icon_type": intent_type}
                    ),
                    ElementStrategy(
                        selector=f"[title*='{label}' i]",
                        confidence=0.75,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Title attribute for {intent_type}: {label}",
                        metadata={"detection_method": "title", "icon_type": intent_type}
                    ),
                    ElementStrategy(
                        selector=f"button[aria-label*='{label}' i]",
                        confidence=0.85,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.FAST,
                        reasoning=f"Button with {intent_type} ARIA label",
                        metadata={"element_type": "button", "icon_type": intent_type}
                    )
                ])
        
        return strategies
    
    def _generate_css_content_strategies(
        self, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate CSS content-based strategies."""
        
        strategies = []
        intent_type = self._infer_icon_intent(context.intent.lower())
        
        if intent_type and intent_type in self.icon_patterns:
            css_codes = self.icon_patterns[intent_type].get("css_content", [])
            
            for css_code in css_codes:
                strategies.append(
                    ElementStrategy(
                        selector=f"[data-icon='{css_code}']",
                        confidence=0.75,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.MEDIUM,
                        reasoning=f"CSS content icon: {css_code}",
                        metadata={"detection_method": "css_content", "icon_code": css_code}
                    )
                )
        
        return strategies
    
    def _generate_unicode_strategies(
        self, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate Unicode emoji-based strategies."""
        
        strategies = []
        intent_type = self._infer_icon_intent(context.intent.lower())
        
        if intent_type and intent_type in self.icon_patterns:
            unicode_icons = self.icon_patterns[intent_type].get("unicode", [])
            
            for unicode_icon in unicode_icons:
                strategies.append(
                    ElementStrategy(
                        selector=f":contains('{unicode_icon}')",
                        confidence=0.70,
                        strategy_type=self.layer_type,
                        performance_tier=PerformanceTier.MEDIUM,
                        reasoning=f"Unicode {intent_type} icon: {unicode_icon}",
                        metadata={"detection_method": "unicode", "icon_unicode": unicode_icon}
                    )
                )
        
        return strategies
    
    def _generate_contextual_strategies(
        self, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Generate context-based icon strategies."""
        
        strategies = []
        
        # Form context strategies
        if "form" in context.page_type.lower():
            strategies.extend([
                ElementStrategy(
                    selector="form button:has(i):not(:has(text))",
                    confidence=0.65,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning="Icon-only button in form",
                    metadata={"context": "form", "icon_only": True}
                ),
                ElementStrategy(
                    selector="form [type='submit']:has(i):not(:has(text))",
                    confidence=0.70,
                    strategy_type=self.layer_type,
                    performance_tier=PerformanceTier.MEDIUM,
                    reasoning="Icon-only submit button",
                    metadata={"context": "form", "button_type": "submit"}
                )
            ])
        
        # Toolbar context
        strategies.extend([
            ElementStrategy(
                selector=".toolbar button:has(i):not(:has(text))",
                confidence=0.60,
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.MEDIUM,
                reasoning="Icon-only toolbar button",
                metadata={"context": "toolbar"}
            ),
            ElementStrategy(
                selector="[role='toolbar'] button:has(i):not(:has(text))",
                confidence=0.65,
                strategy_type=self.layer_type,
                performance_tier=PerformanceTier.MEDIUM,
                reasoning="Icon-only button in ARIA toolbar",
                metadata={"context": "toolbar", "aria": True}
            )
        ])
        
        return strategies
    
    def _infer_icon_intent(self, intent: str) -> Optional[str]:
        """Infer icon type from intent."""
        
        intent_lower = intent.lower()
        
        # Direct mapping
        for icon_type in self.icon_patterns.keys():
            if icon_type in intent_lower:
                return icon_type
        
        # Semantic mapping
        if any(word in intent_lower for word in ["save", "store", "persist"]):
            return "save"
        elif any(word in intent_lower for word in ["edit", "modify", "change", "update"]):
            return "edit"
        elif any(word in intent_lower for word in ["delete", "remove", "trash", "destroy"]):
            return "delete"
        elif any(word in intent_lower for word in ["search", "find", "lookup", "filter"]):
            return "search"
        elif any(word in intent_lower for word in ["close", "dismiss", "cancel", "exit"]):
            return "close"
        elif any(word in intent_lower for word in ["add", "create", "new", "plus"]):
            return "add"
        elif any(word in intent_lower for word in ["home", "main", "dashboard"]):
            return "home"
        elif any(word in intent_lower for word in ["settings", "config", "preferences", "options"]):
            return "settings"
        
        return None