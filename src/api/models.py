"""
API Request/Response Models
===========================

Pydantic models for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ElementRequest(BaseModel):
    """Request model for element identification."""
    platform: str = Field(..., description="Target platform (e.g., salesforce_lightning)")
    url: str = Field(..., description="URL of the page to search")
    intent: str = Field(..., description="Natural language description of element to find")
    page_type: str = Field(..., description="Type of page (e.g., login, dashboard)")
    parent_frame: Optional[str] = Field(None, description="Parent frame selector if in iframe")
    additional_context: Optional[Dict[str, Any]] = Field(None, description="Platform-specific context")
    timeout_ms: int = Field(2000, description="Timeout in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform": "salesforce_lightning",
                "url": "https://example.my.salesforce.com",
                "intent": "submit button",
                "page_type": "form",
                "timeout_ms": 2000
            }
        }


class ElementResponse(BaseModel):
    """Response model for element identification."""
    found: bool = Field(..., description="Whether element was found")
    selector: Optional[str] = Field(None, description="Selector that found the element")
    strategy_type: Optional[str] = Field(None, description="Which layer found the element")
    confidence: float = Field(0.0, description="Confidence score of the match")
    time_taken_ms: float = Field(..., description="Time taken to find element")
    attempts_count: int = Field(..., description="Number of strategies attempted")
    error: Optional[str] = Field(None, description="Error message if failed")


class TestStep(BaseModel):
    """Single step in a test scenario."""
    action: str = Field(..., description="Action to perform (click, type, select)")
    intent: str = Field(..., description="Natural language description of element")
    page_type: str = Field(..., description="Type of page for this step")
    data: Optional[str] = Field(None, description="Data for actions like type")
    additional_context: Optional[Dict[str, Any]] = Field(None)


class TestGenerationRequest(BaseModel):
    """Request to generate a complete test."""
    platform: str = Field(..., description="Target platform")
    start_url: str = Field(..., description="Starting URL for test")
    test_name: str = Field(..., description="Name of the test scenario")
    test_steps: List[TestStep] = Field(..., description="Steps to perform")
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform": "salesforce_lightning",
                "start_url": "https://example.my.salesforce.com",
                "test_name": "Create New Account",
                "test_steps": [
                    {
                        "action": "click",
                        "intent": "Accounts menu item",
                        "page_type": "home"
                    },
                    {
                        "action": "click",
                        "intent": "New button",
                        "page_type": "list"
                    },
                    {
                        "action": "type",
                        "intent": "Account Name field",
                        "page_type": "form",
                        "data": "Test Account 123"
                    },
                    {
                        "action": "click",
                        "intent": "Save button",
                        "page_type": "form"
                    }
                ]
            }
        }


class TestGenerationResponse(BaseModel):
    """Response with generated test code."""
    success: bool = Field(..., description="Whether all elements were found")
    test_code: str = Field(..., description="Generated test code")
    test_steps: List[Dict[str, Any]] = Field(..., description="Processed test steps")
    platform: str = Field(..., description="Platform the test was generated for")


class MetricsResponse(BaseModel):
    """System performance metrics."""
    total_requests: int
    success_rate: float
    average_time_ms: float
    cache_hit_rate: float
    visual_fallback_rate: float
    strategy_success_rates: Dict[str, Dict[str, Any]]
    layer_metrics: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FeedbackRequest(BaseModel):
    """User feedback on element identification."""
    feedback_id: str = Field(..., description="Unique feedback ID")
    platform: str
    intent: str
    selector_attempted: Optional[str]
    was_successful: bool
    correct_selector: Optional[str] = Field(None, description="User-provided correct selector")
    comments: Optional[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "feedback_id": "fb_123456",
                "platform": "salesforce_lightning",
                "intent": "submit button",
                "selector_attempted": "button[type='submit']",
                "was_successful": False,
                "correct_selector": "lightning-button[label='Submit']",
                "comments": "The button was a Lightning component, not standard HTML"
            }
        }