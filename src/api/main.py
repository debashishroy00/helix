"""
Helix FastAPI Service
=====================

Main API endpoints for the Helix element identification system.
Provides REST API access to the Universal Locator functionality.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
import os
from datetime import datetime

from src.api.models import (
    ElementRequest, ElementResponse, 
    TestGenerationRequest, TestGenerationResponse,
    MetricsResponse, FeedbackRequest
)
from src.api.dependencies import get_page_handler, get_universal_locator, get_cache_client
from src.models.element import ElementContext, Platform

# Import test router with error handling
try:
    from src.api.test_endpoints import router as test_router
    TEST_ENDPOINTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Test endpoints not available: {e}")
    TEST_ENDPOINTS_AVAILABLE = False
    test_router = None


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Helix API Service...")
    # Initialize any connections, load models, etc.
    
    yield
    
    # Shutdown
    print("Shutting down Helix API Service...")
    # Clean up resources


# Create FastAPI app
app = FastAPI(
    title="Helix - Agentic RAG Test Automation Platform",
    description="Patent-pending 7-layer element identification system for test automation",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include test router if available
if TEST_ENDPOINTS_AVAILABLE and test_router:
    app.include_router(test_router)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Helix",
        "status": "operational",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/test/semantic_only")
async def test_semantic_only(request: Dict[str, Any]):
    """
    Test semantic layer without browser dependencies.
    """
    try:
        from src.layers.semantic_intent import SemanticIntentLayer
        from src.models.element import ElementContext, Platform
        
        # Create semantic layer
        layer = SemanticIntentLayer()
        
        # Create context
        context = ElementContext(
            platform=Platform(request.get("platform", "salesforce_lightning")),
            page_type=request.get("page_type", "form"),
            intent=request.get("intent", "submit button"),
            additional_context=request.get("additional_context", {})
        )
        
        # Mock page object (no browser needed)
        class MockPage:
            pass
        
        mock_page = MockPage()
        
        # Generate strategies using semantic layer only
        strategies = await layer.generate_strategies(mock_page, context)
        
        # Build response
        return {
            "success": True,
            "layer": "semantic_intent",
            "strategies_count": len(strategies),
            "strategies": [
                {
                    "selector": s.selector,
                    "confidence": s.confidence,
                    "metadata": s.metadata
                }
                for s in strategies
            ],
            "metrics": layer.get_metrics()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "layer": "semantic_intent"
        }


@app.post("/find_element_semantic_only")
async def find_element_semantic_only(request: ElementRequest):
    """
    Find elements using only semantic layer (no browser required).
    """
    try:
        from src.layers.semantic_intent import SemanticIntentLayer
        from src.models.element import ElementContext, Platform
        
        # Create semantic layer
        layer = SemanticIntentLayer()
        
        # Create context
        context = ElementContext(
            platform=Platform(request.platform),
            page_type=request.page_type,
            intent=request.intent,
            additional_context=request.additional_context or {}
        )
        
        # Mock page object
        class MockPage:
            pass
        
        mock_page = MockPage()
        
        # Generate strategies
        strategies = await layer.generate_strategies(mock_page, context)
        
        if strategies:
            best_strategy = max(strategies, key=lambda s: s.confidence)
            
            return ElementResponse(
                found=True,  # We found strategies
                selector=best_strategy.selector,
                strategy_type=best_strategy.strategy_type.value,
                confidence=best_strategy.confidence,
                time_taken_ms=100,  # Mock timing
                attempts_count=len(strategies),
                error=None
            )
        else:
            return ElementResponse(
                found=False,
                selector=None,
                strategy_type=None,
                confidence=0.0,
                time_taken_ms=100,
                attempts_count=0,
                error="No strategies generated"
            )
            
    except Exception as e:
        return ElementResponse(
            found=False,
            selector=None,
            strategy_type=None,
            confidence=0.0,
            time_taken_ms=0,
            attempts_count=0,
            error=str(e)
        )


@app.get("/test/status")
async def test_status():
    """
    Get system status for testing.
    """
    try:
        status = {
            "api": "healthy",
            "semantic_layer": "unknown",
            "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
        }
        
        # Test semantic layer
        try:
            from src.layers.semantic_intent import SemanticIntentLayer
            layer = SemanticIntentLayer()
            status["semantic_layer"] = "available"
        except Exception as e:
            status["semantic_layer"] = f"error: {str(e)}"
        
        return status
        
    except Exception as e:
        return {
            "api": "error",
            "error": str(e)
        }


@app.post("/find_element_smart", response_model=ElementResponse)
async def find_element_smart(request: ElementRequest):
    """
    Smart element finding - tries deterministic patterns first, AI only if needed.
    90% faster for common patterns.
    """
    start_time = datetime.utcnow()
    
    try:
        # Create context
        context = ElementContext(
            platform=Platform(request.platform),
            page_type=request.page_type,
            intent=request.intent,
            additional_context=request.additional_context or {}
        )
        
        # Get layers
        locator = get_universal_locator()
        
        # Use smart orchestrator
        from src.core.smart_orchestrator import SmartOrchestrator
        orchestrator = SmartOrchestrator()
        
        strategies, execution_path = await orchestrator.find_element_smart(
            locator.layers,
            None,  # No browser for fast mode
            context,
            max_time_ms=5000
        )
        
        elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        if strategies:
            best_strategy = strategies[0]
            
            # Get performance stats
            perf_stats = orchestrator.get_performance_stats(execution_path, elapsed_ms)
            
            return ElementResponse(
                found=True,
                selector=best_strategy.selector,
                strategy_type=best_strategy.strategy_type.value,
                confidence=best_strategy.confidence,
                time_taken_ms=elapsed_ms,
                attempts_count=len(strategies),
                metadata={
                    "execution_path": execution_path,
                    "performance_stats": perf_stats,
                    "source": (best_strategy.metadata or {}).get("source", "layer")
                }
            )
        else:
            return ElementResponse(
                found=False,
                time_taken_ms=elapsed_ms,
                attempts_count=0,
                error="No strategies found",
                metadata={"execution_path": execution_path}
            )
            
    except Exception as e:
        elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        return ElementResponse(
            found=False,
            time_taken_ms=elapsed_ms,
            attempts_count=0,
            error=str(e)
        )


@app.post("/find_element", response_model=ElementResponse)
async def find_element(request: ElementRequest):
    """
    Main element identification endpoint.
    
    Accepts intent and context, returns element identification result.
    """
    try:
        # Get dependencies
        page_handler = await get_page_handler(request.platform, request.url)
        universal_locator = get_universal_locator()
        
        # Create context
        context = ElementContext(
            platform=Platform(request.platform),
            page_type=request.page_type,
            intent=request.intent,
            parent_frame=request.parent_frame,
            additional_context=request.additional_context or {}
        )
        
        # Find element
        result = await universal_locator.find_element(
            page_handler.page,
            context,
            timeout_ms=request.timeout_ms
        )
        
        # Build response
        response = ElementResponse(
            found=result.found,
            selector=result.strategy_used.selector if result.strategy_used else None,
            strategy_type=result.strategy_used.strategy_type.value if result.strategy_used else None,
            confidence=result.strategy_used.confidence if result.strategy_used else 0.0,
            time_taken_ms=result.time_taken_ms,
            attempts_count=len(result.attempts),
            error=result.error
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up page handler
        if 'page_handler' in locals():
            await page_handler.cleanup()


@app.post("/generate_test", response_model=TestGenerationResponse)
async def generate_test(request: TestGenerationRequest):
    """
    Generate complete test cases using the element identification system.
    
    This endpoint combines multiple element identifications to create
    full test scenarios.
    """
    try:
        # Get dependencies
        page_handler = await get_page_handler(request.platform, request.start_url)
        universal_locator = get_universal_locator()
        
        test_steps = []
        
        for step in request.test_steps:
            # Create context for each step
            context = ElementContext(
                platform=Platform(request.platform),
                page_type=step.page_type,
                intent=step.intent,
                additional_context=step.additional_context or {}
            )
            
            # Find element
            result = await universal_locator.find_element(
                page_handler.page,
                context,
                timeout_ms=5000  # Allow more time for test generation
            )
            
            if result.found:
                test_steps.append({
                    "action": step.action,
                    "selector": result.strategy_used.selector,
                    "intent": step.intent,
                    "data": step.data
                })
            else:
                test_steps.append({
                    "action": step.action,
                    "selector": None,
                    "intent": step.intent,
                    "error": f"Element not found: {step.intent}"
                })
        
        # Generate test code (simplified for now)
        test_code = _generate_test_code(request.platform, test_steps)
        
        return TestGenerationResponse(
            success=all(step.get("selector") for step in test_steps),
            test_code=test_code,
            test_steps=test_steps,
            platform=request.platform
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if 'page_handler' in locals():
            await page_handler.cleanup()


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Get performance metrics for the element identification system.
    """
    universal_locator = get_universal_locator()
    stats = universal_locator.get_stats()
    
    # Get per-layer metrics
    layer_metrics = []
    for layer in universal_locator.layers.values():
        layer_metrics.append(layer.get_metrics())
    
    return MetricsResponse(
        total_requests=stats["total_requests"],
        success_rate=stats.get("overall_success_rate", 0.0),
        average_time_ms=stats["average_time_ms"],
        cache_hit_rate=stats.get("cache_hit_rate", 0.0),
        visual_fallback_rate=stats.get("visual_fallback_rate", 0.0),
        strategy_success_rates=stats["strategy_success_rates"],
        layer_metrics=layer_metrics
    )


@app.post("/feedback")
async def record_feedback(
    request: FeedbackRequest,
    background_tasks: BackgroundTasks
):
    """
    Record human feedback on element identification results.
    
    This helps improve the self-learning system.
    """
    # Process feedback asynchronously
    background_tasks.add_task(_process_feedback, request)
    
    return {"status": "feedback_received", "id": request.feedback_id}


def _generate_test_code(platform: str, test_steps: list) -> str:
    """Generate test code based on identified elements."""
    # Simplified test code generation
    if platform.startswith("salesforce"):
        framework = "Playwright"
    else:
        framework = "Selenium"
    
    code_lines = [
        f"# Generated by Helix - {datetime.utcnow().isoformat()}",
        f"# Platform: {platform}",
        f"# Framework: {framework}",
        "",
        "import asyncio",
        "from playwright.async_api import async_playwright" if framework == "Playwright" else "from selenium import webdriver",
        "",
        "async def test_scenario():" if framework == "Playwright" else "def test_scenario():",
    ]
    
    for step in test_steps:
        if step.get("selector"):
            if step["action"] == "click":
                if framework == "Playwright":
                    code_lines.append(f'    await page.locator("{step["selector"]}").click()')
                else:
                    code_lines.append(f'    driver.find_element_by_css_selector("{step["selector"]}").click()')
            elif step["action"] == "type":
                if framework == "Playwright":
                    code_lines.append(f'    await page.locator("{step["selector"]}").type("{step.get("data", "")}")')
                else:
                    code_lines.append(f'    driver.find_element_by_css_selector("{step["selector"]}").send_keys("{step.get("data", "")}")')
        else:
            code_lines.append(f'    # ERROR: Could not find element for "{step["intent"]}"')
    
    return "\n".join(code_lines)


async def _process_feedback(feedback: FeedbackRequest):
    """Process user feedback to improve the system."""
    # This would update the ML model weights, cache, etc.
    # For now, just log it
    print(f"Feedback received: {feedback.feedback_id} - Success: {feedback.was_successful}")
    
    if not feedback.was_successful and feedback.correct_selector:
        # User provided correct selector - learn from this
        cache_client = get_cache_client()
        if cache_client:
            # Store the correction for future use
            # This would be more sophisticated in production
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)