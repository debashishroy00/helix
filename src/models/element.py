from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class Platform(Enum):
    """Supported platforms for element identification"""
    SALESFORCE_LIGHTNING = "salesforce_lightning"
    SALESFORCE_CLASSIC = "salesforce_classic"
    SAP_FIORI = "sap_fiori"
    SAP_GUI = "sap_gui"
    WORKDAY = "workday"
    ORACLE_CLOUD = "oracle_cloud"


class ElementType(Enum):
    """Common UI element types across platforms"""
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TABLE = "table"
    MODAL = "modal"
    TAB = "tab"
    MENU_ITEM = "menu_item"
    CUSTOM = "custom"


class StrategyType(Enum):
    """The 10 layers of element identification (patent-critical ordering)"""
    SEMANTIC_INTENT = "semantic_intent"  # Layer 1
    CONTEXTUAL_RELATIONSHIP = "contextual_relationship"  # Layer 2
    VISUAL_FINGERPRINT = "visual_fingerprint"  # Layer 3
    BEHAVIORAL_PATTERN = "behavioral_pattern"  # Layer 4
    STRUCTURAL_PATTERN = "structural_pattern"  # Layer 5
    ACCESSIBILITY_BRIDGE = "accessibility_bridge"  # Layer 6
    MUTATION_OBSERVATION = "mutation_observation"  # Layer 7 - NEW
    TIMING_SYNCHRONIZATION = "timing_synchronization"  # Layer 8 - NEW
    STATE_CONTEXT_AWARENESS = "state_context_awareness"  # Layer 9 - NEW
    ML_FUSION = "ml_fusion"  # Layer 10 - Enhanced


@dataclass
class ElementStrategy:
    """
    Represents a single strategy for finding an element.
    Each layer produces one or more strategies with confidence scores.
    """
    strategy_type: StrategyType
    selector: str  # CSS selector, XPath, or special format like "visual:click(x,y)"
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any]  # Layer-specific data
    
    def __post_init__(self):
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")


@dataclass
class ElementContext:
    """
    Context information needed for element identification.
    Provides hints to layers about the environment and intent.
    """
    platform: Platform
    page_type: str  # e.g., "login", "dashboard", "form"
    intent: str  # Natural language description of what we're looking for
    parent_frame: Optional[str] = None  # For iframe/shadow DOM contexts
    additional_context: Dict[str, Any] = None  # Platform-specific context
    
    def __post_init__(self):
        if self.additional_context is None:
            self.additional_context = {}


@dataclass
class ElementResult:
    """
    Result of element identification attempt.
    Contains the element handle and metadata about how it was found.
    """
    found: bool
    element: Optional[Any] = None  # Playwright/Selenium element handle
    strategy_used: Optional[ElementStrategy] = None
    time_taken_ms: float = 0.0
    attempts: List[ElementStrategy] = None  # All strategies tried
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.attempts is None:
            self.attempts = []


@dataclass
class CachedStrategy:
    """
    Cached successful strategy for faster future lookups.
    Includes metadata for cache invalidation and performance tracking.
    """
    strategy: ElementStrategy
    platform: Platform
    page_type: str
    intent: str
    success_count: int = 1
    failure_count: int = 0
    last_used: datetime = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.last_used is None:
            self.last_used = datetime.utcnow()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0
    
    @property
    def cache_key(self) -> str:
        return f"{self.platform.value}:{self.page_type}:{self.intent}"