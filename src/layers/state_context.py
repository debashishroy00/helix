"""
Layer 9: State Context Awareness
================================

This layer understands application state to find elements correctly,
solving the problem where elements appear differently based on user role,
workflow step, or application context.

Patent Justification:
- Handles elements that exist only in specific application states
- Adapts selectors based on user permissions, roles, and context
- Navigates to required state when elements are state-dependent
- Maintains state history for intelligent prediction

Example:
    Intent: "approve button"
    States: Only visible to managers, only in "pending" workflow step
    Strategy: Ensure manager role + pending state, then find button
"""

import asyncio
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import re

from src.layers.base import BaseLayer
from src.models.element import ElementStrategy, ElementContext, StrategyType


class ApplicationState(Enum):
    """Common application states across platforms."""
    LOGGED_OUT = "logged_out"
    LOGGED_IN = "logged_in"
    LOADING = "loading"
    READY = "ready"
    FORM_EDIT = "form_edit"
    FORM_VIEW = "form_view"
    LIST_VIEW = "list_view"
    DETAIL_VIEW = "detail_view"
    MODAL_OPEN = "modal_open"
    WORKFLOW_PENDING = "workflow_pending"
    WORKFLOW_APPROVED = "workflow_approved"
    ERROR_STATE = "error_state"


@dataclass
class UserContext:
    """User context information."""
    role: Optional[str] = None
    permissions: Set[str] = field(default_factory=set)
    department: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class ApplicationStateInfo:
    """Complete application state information."""
    current_state: ApplicationState
    user_context: UserContext
    workflow_step: Optional[str] = None
    data_state: Dict[str, Any] = field(default_factory=dict)
    ui_state: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.8


@dataclass
class StateStrategy:
    """A strategy that includes state requirements."""
    selector: str
    required_states: List[ApplicationState]
    required_permissions: Set[str]
    state_navigation: Optional[str] = None  # How to reach required state
    confidence: float = 0.8


class StateContextLayer(BaseLayer):
    """
    Layer 9: Understands application state to find elements correctly.
    
    This layer is crucial for enterprise applications where elements
    appear/disappear based on user roles, workflow states, and permissions.
    """
    
    def __init__(self):
        super().__init__(StrategyType.STATE_CONTEXT_AWARENESS)
        
        # Platform-specific state detection patterns
        self.state_patterns = {
            "salesforce_lightning": {
                "user_role_indicators": [
                    {"selector": ".profile-card", "attribute": "data-role"},
                    {"selector": "[data-aura-class*='UserContext']", "attribute": "title"},
                    {"selector": ".userNav-item", "text_pattern": r"(Admin|Manager|User)"}
                ],
                "workflow_indicators": [
                    {"selector": ".slds-path__item", "attribute": "aria-selected"},
                    {"selector": "[data-status]", "attribute": "data-status"},
                    {"selector": ".record-status", "text_pattern": r"(Draft|Pending|Approved|Rejected)"}
                ],
                "permission_indicators": [
                    {"selector": "[data-permission]", "attribute": "data-permission"},
                    {"selector": ".slds-button[disabled]", "type": "disabled_button"},
                    {"selector": ".slds-tabs__item[aria-disabled='true']", "type": "disabled_tab"}
                ]
            },
            "sap_fiori": {
                "user_role_indicators": [
                    {"selector": ".sapMShellHead .sapMText", "text_pattern": r"Role:\s*(.+)"},
                    {"selector": "[data-sap-ui-role]", "attribute": "data-sap-ui-role"},
                    {"selector": ".sapMUserIcon", "attribute": "title"}
                ],
                "workflow_indicators": [
                    {"selector": ".sapMObjectStatus", "text_pattern": r"(Open|In Process|Completed)"},
                    {"selector": "[data-workflow-status]", "attribute": "data-workflow-status"},
                    {"selector": ".sapMProgressIndicator", "attribute": "aria-valuenow"}
                ]
            },
            "workday": {
                "user_role_indicators": [
                    {"selector": "[data-automation-id*='user']", "attribute": "title"},
                    {"selector": ".WDFF [data-role]", "attribute": "data-role"},
                    {"selector": "[aria-label*='Role']", "text_content": True}
                ],
                "workflow_indicators": [
                    {"selector": "[data-automation-id*='status']", "text_content": True},
                    {"selector": ".WDFF-workflowStatus", "attribute": "data-status"},
                    {"selector": "[class*='workflow'][class*='step']", "attribute": "data-step"}
                ]
            }
        }
        
        # Element visibility rules by state
        self.element_state_rules = {
            "approve_button": {
                "required_states": [ApplicationState.WORKFLOW_PENDING],
                "required_permissions": {"approve", "workflow_manage"},
                "blocked_states": [ApplicationState.WORKFLOW_APPROVED, ApplicationState.FORM_VIEW]
            },
            "edit_button": {
                "required_states": [ApplicationState.READY, ApplicationState.DETAIL_VIEW],
                "required_permissions": {"edit", "write"},
                "blocked_states": [ApplicationState.LOADING, ApplicationState.WORKFLOW_APPROVED]
            },
            "delete_button": {
                "required_permissions": {"delete", "admin"},
                "blocked_states": [ApplicationState.FORM_VIEW, ApplicationState.WORKFLOW_PENDING]
            },
            "submit_button": {
                "required_states": [ApplicationState.FORM_EDIT],
                "blocked_states": [ApplicationState.FORM_VIEW, ApplicationState.LOADING]
            }
        }
    
    async def generate_strategies(
        self, 
        page: Any,
        context: ElementContext
    ) -> List[ElementStrategy]:
        """
        Generate state-aware strategies for element identification.
        """
        strategies = []
        
        try:
            # Detect current application state
            app_state = await self._detect_application_state(page, context)
            
            # Generate base selectors for the intent
            base_selectors = self._generate_base_selectors(context)
            
            # Create state-aware strategies
            for base_selector in base_selectors:
                state_strategies = self._create_state_aware_strategies(
                    base_selector, app_state, context
                )
                strategies.extend(state_strategies)
            
            # Add state-specific conditional strategies
            conditional_strategies = self._create_conditional_strategies(
                app_state, context
            )
            strategies.extend(conditional_strategies)
            
            # Add state navigation strategies
            navigation_strategies = self._create_navigation_strategies(
                app_state, context
            )
            strategies.extend(navigation_strategies)
            
            return strategies
            
        except Exception as e:
            print(f"State context error: {str(e)}")
            return self._fallback_state_strategies(context)
    
    async def _detect_application_state(
        self, 
        page: Any, 
        context: ElementContext
    ) -> ApplicationStateInfo:
        """Detect the current application state."""
        
        # Initialize state info
        state_info = ApplicationStateInfo(
            current_state=ApplicationState.READY,
            user_context=UserContext()
        )
        
        platform = context.platform.value
        if platform not in self.state_patterns:
            return state_info  # Return default state
        
        patterns = self.state_patterns[platform]
        
        # Detect user context
        user_context = await self._detect_user_context(page, patterns)
        state_info.user_context = user_context
        
        # Detect workflow state
        workflow_state = await self._detect_workflow_state(page, patterns)
        if workflow_state:
            state_info.workflow_step = workflow_state
            # Map workflow state to application state
            if "pending" in workflow_state.lower():
                state_info.current_state = ApplicationState.WORKFLOW_PENDING
            elif "approved" in workflow_state.lower():
                state_info.current_state = ApplicationState.WORKFLOW_APPROVED
        
        # Detect UI state
        ui_state = await self._detect_ui_state(page, context)
        state_info.ui_state = ui_state
        
        # Adjust state based on UI indicators
        if ui_state.get("modal_open"):
            state_info.current_state = ApplicationState.MODAL_OPEN
        elif ui_state.get("form_mode") == "edit":
            state_info.current_state = ApplicationState.FORM_EDIT
        elif ui_state.get("form_mode") == "view":
            state_info.current_state = ApplicationState.FORM_VIEW
        elif ui_state.get("loading"):
            state_info.current_state = ApplicationState.LOADING
        
        return state_info
    
    async def _detect_user_context(
        self, 
        page: Any, 
        patterns: Dict[str, List[Dict]]
    ) -> UserContext:
        """Detect user role and permissions."""
        user_context = UserContext()
        
        if not hasattr(page, 'evaluate'):
            return user_context  # Mock page
        
        try:
            # Look for role indicators
            role_indicators = patterns.get("user_role_indicators", [])
            for indicator in role_indicators:
                try:
                    result = await page.evaluate(f"""
                        () => {{
                            const element = document.querySelector('{indicator["selector"]}');
                            if (!element) return null;
                            
                            if ('{indicator.get("attribute")}') {{
                                return element.getAttribute('{indicator["attribute"]}');
                            }} else if ('{indicator.get("text_pattern")}') {{
                                const text = element.textContent || element.innerText;
                                const match = text.match(/{indicator["text_pattern"]}/);
                                return match ? match[1] : null;
                            }} else {{
                                return element.textContent || element.innerText;
                            }}
                        }}
                    """)
                    
                    if result:
                        user_context.role = result.strip()
                        break
                        
                except Exception:
                    continue
            
            # Detect permissions based on role
            if user_context.role:
                user_context.permissions = self._infer_permissions_from_role(
                    user_context.role
                )
            
            # Look for permission indicators
            permission_indicators = patterns.get("permission_indicators", [])
            for indicator in permission_indicators:
                try:
                    has_permission = await page.evaluate(f"""
                        () => {{
                            const elements = document.querySelectorAll('{indicator["selector"]}');
                            return elements.length > 0;
                        }}
                    """)
                    
                    if has_permission and "permission" in indicator.get("attribute", ""):
                        # Extract permission name from attribute
                        permission = indicator["attribute"].replace("data-permission-", "")
                        user_context.permissions.add(permission)
                        
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"User context detection error: {e}")
        
        return user_context
    
    async def _detect_workflow_state(
        self, 
        page: Any, 
        patterns: Dict[str, List[Dict]]
    ) -> Optional[str]:
        """Detect current workflow state."""
        if not hasattr(page, 'evaluate'):
            return None
        
        workflow_indicators = patterns.get("workflow_indicators", [])
        for indicator in workflow_indicators:
            try:
                result = await page.evaluate(f"""
                    () => {{
                        const element = document.querySelector('{indicator["selector"]}');
                        if (!element) return null;
                        
                        if ('{indicator.get("attribute")}') {{
                            return element.getAttribute('{indicator["attribute"]}');
                        }} else {{
                            const text = element.textContent || element.innerText;
                            const pattern = /{indicator.get("text_pattern", "(.+)")}/;
                            const match = text.match(pattern);
                            return match ? match[1] : text;
                        }}
                    }}
                """)
                
                if result:
                    return result.strip()
                    
            except Exception:
                continue
        
        return None
    
    async def _detect_ui_state(
        self, 
        page: Any, 
        context: ElementContext
    ) -> Dict[str, Any]:
        """Detect current UI state."""
        ui_state = {}
        
        if not hasattr(page, 'evaluate'):
            return ui_state
        
        try:
            # Common UI state checks
            ui_checks = await page.evaluate("""
                () => {
                    return {
                        modal_open: !!document.querySelector('.modal, .slds-modal, .sapMDialog, [role="dialog"]'),
                        loading: !!document.querySelector('.loading, .spinner, .slds-spinner, .sapMBusyIndicator'),
                        form_edit: !!document.querySelector('form input:not([readonly]), form select:not([disabled])'),
                        form_view: !!document.querySelector('form input[readonly], form .readonly'),
                        error_visible: !!document.querySelector('.error, .slds-has-error, .sapMMessageToast--error')
                    }
                }
            """)
            
            ui_state.update(ui_checks)
            
            # Determine form mode
            if ui_state.get("form_edit"):
                ui_state["form_mode"] = "edit"
            elif ui_state.get("form_view"):
                ui_state["form_mode"] = "view"
            
        except Exception:
            pass
        
        return ui_state
    
    def _infer_permissions_from_role(self, role: str) -> Set[str]:
        """Infer permissions from user role."""
        role_lower = role.lower()
        permissions = set()
        
        if "admin" in role_lower:
            permissions.update({"read", "write", "delete", "admin", "approve", "workflow_manage"})
        elif "manager" in role_lower:
            permissions.update({"read", "write", "approve", "workflow_manage"})
        elif "editor" in role_lower or "author" in role_lower:
            permissions.update({"read", "write"})
        else:
            permissions.add("read")  # Default read permission
        
        return permissions
    
    def _generate_base_selectors(self, context: ElementContext) -> List[str]:
        """Generate base selectors for the intent."""
        intent_lower = context.intent.lower()
        selectors = []
        
        # Common selectors based on intent
        if "approve" in intent_lower:
            selectors.extend([
                'button:contains("Approve")',
                '[data-action="approve"]',
                '.approve-btn, .btn-approve',
                'input[type="submit"][value*="Approve"]'
            ])
        elif "reject" in intent_lower or "deny" in intent_lower:
            selectors.extend([
                'button:contains("Reject")',
                'button:contains("Deny")',
                '[data-action="reject"]',
                '.reject-btn, .btn-reject'
            ])
        elif "edit" in intent_lower:
            selectors.extend([
                'button:contains("Edit")',
                '[data-action="edit"]',
                '.edit-btn, .btn-edit',
                'a[href*="edit"]'
            ])
        elif "delete" in intent_lower:
            selectors.extend([
                'button:contains("Delete")',
                '[data-action="delete"]',
                '.delete-btn, .btn-delete',
                '.btn-danger:contains("Delete")'
            ])
        elif "submit" in intent_lower:
            selectors.extend([
                'button[type="submit"]',
                'input[type="submit"]',
                'button:contains("Submit")',
                '.submit-btn'
            ])
        
        return selectors[:5]  # Top 5 selectors
    
    def _create_state_aware_strategies(
        self, 
        base_selector: str, 
        state_info: ApplicationStateInfo, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Create strategies that are aware of current state."""
        strategies = []
        
        # Check if this element type has state rules
        element_key = self._get_element_key(context.intent)
        rules = self.element_state_rules.get(element_key, {})
        
        # Strategy 1: Current state compatible
        is_state_compatible = self._is_state_compatible(state_info, rules)
        if is_state_compatible:
            strategies.append(ElementStrategy(
                strategy_type=self.layer_type,
                selector=base_selector,
                confidence=0.85,
                metadata={
                    "state_strategy": "current_state_compatible",
                    "current_state": state_info.current_state.value,
                    "user_role": state_info.user_context.role,
                    "permissions": list(state_info.user_context.permissions),
                    "base_selector": base_selector
                }
            ))
        
        # Strategy 2: Role-specific selector
        if state_info.user_context.role:
            role_selector = f'[data-role="{state_info.user_context.role}"] {base_selector}'
            strategies.append(ElementStrategy(
                strategy_type=self.layer_type,
                selector=role_selector,
                confidence=0.7,
                metadata={
                    "state_strategy": "role_specific",
                    "required_role": state_info.user_context.role,
                    "base_selector": base_selector
                }
            ))
        
        # Strategy 3: Permission-based selector
        for permission in state_info.user_context.permissions:
            perm_selector = f'[data-permission*="{permission}"] {base_selector}'
            strategies.append(ElementStrategy(
                strategy_type=self.layer_type,
                selector=perm_selector,
                confidence=0.65,
                metadata={
                    "state_strategy": "permission_based",
                    "required_permission": permission,
                    "base_selector": base_selector
                }
            ))
        
        return strategies
    
    def _create_conditional_strategies(
        self, 
        state_info: ApplicationStateInfo, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Create strategies with state conditions."""
        strategies = []
        
        element_key = self._get_element_key(context.intent)
        rules = self.element_state_rules.get(element_key, {})
        
        # Create conditional selectors based on required states
        required_states = rules.get("required_states", [])
        for state in required_states:
            state_selector = f"state_condition:{state.value}:{context.intent}"
            strategies.append(ElementStrategy(
                strategy_type=self.layer_type,
                selector=state_selector,
                confidence=0.6,
                metadata={
                    "state_strategy": "conditional",
                    "required_state": state.value,
                    "current_state": state_info.current_state.value,
                    "state_match": state_info.current_state == state
                }
            ))
        
        return strategies
    
    def _create_navigation_strategies(
        self, 
        state_info: ApplicationStateInfo, 
        context: ElementContext
    ) -> List[ElementStrategy]:
        """Create strategies that include state navigation."""
        strategies = []
        
        element_key = self._get_element_key(context.intent)
        rules = self.element_state_rules.get(element_key, {})
        
        required_states = rules.get("required_states", [])
        current_state = state_info.current_state
        
        # If not in required state, create navigation strategy
        if required_states and current_state not in required_states:
            target_state = required_states[0]  # Use first required state
            navigation = self._get_navigation_to_state(current_state, target_state)
            
            if navigation:
                nav_selector = f"navigate:{navigation}:{context.intent}"
                strategies.append(ElementStrategy(
                    strategy_type=self.layer_type,
                    selector=nav_selector,
                    confidence=0.5,
                    metadata={
                        "state_strategy": "navigation_required",
                        "current_state": current_state.value,
                        "target_state": target_state.value,
                        "navigation_action": navigation
                    }
                ))
        
        return strategies
    
    def _get_element_key(self, intent: str) -> str:
        """Get element key for rule lookup."""
        intent_lower = intent.lower()
        
        if "approve" in intent_lower:
            return "approve_button"
        elif "edit" in intent_lower:
            return "edit_button"
        elif "delete" in intent_lower:
            return "delete_button"
        elif "submit" in intent_lower:
            return "submit_button"
        else:
            return "generic_element"
    
    def _is_state_compatible(
        self, 
        state_info: ApplicationStateInfo, 
        rules: Dict[str, Any]
    ) -> bool:
        """Check if current state is compatible with element rules."""
        
        # Check required states
        required_states = rules.get("required_states", [])
        if required_states and state_info.current_state not in required_states:
            return False
        
        # Check blocked states
        blocked_states = rules.get("blocked_states", [])
        if state_info.current_state in blocked_states:
            return False
        
        # Check required permissions
        required_permissions = rules.get("required_permissions", set())
        if required_permissions and not required_permissions.intersection(
            state_info.user_context.permissions
        ):
            return False
        
        return True
    
    def _get_navigation_to_state(
        self, 
        current: ApplicationState, 
        target: ApplicationState
    ) -> Optional[str]:
        """Get navigation action to reach target state."""
        
        # Common navigation patterns
        navigation_map = {
            (ApplicationState.LIST_VIEW, ApplicationState.DETAIL_VIEW): "click_record",
            (ApplicationState.DETAIL_VIEW, ApplicationState.FORM_EDIT): "click_edit",
            (ApplicationState.FORM_VIEW, ApplicationState.FORM_EDIT): "click_edit",
            (ApplicationState.READY, ApplicationState.WORKFLOW_PENDING): "start_workflow",
        }
        
        return navigation_map.get((current, target))
    
    def _fallback_state_strategies(self, context: ElementContext) -> List[ElementStrategy]:
        """Generate fallback strategies when state detection fails."""
        base_selectors = self._generate_base_selectors(context)[:3]
        strategies = []
        
        for selector in base_selectors:
            strategies.append(ElementStrategy(
                strategy_type=self.layer_type,
                selector=selector,
                confidence=0.4,
                metadata={
                    "state_strategy": "fallback",
                    "base_selector": selector,
                    "state_detection_failed": True
                }
            ))
        
        return strategies