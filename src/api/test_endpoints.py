"""
Test-Only API Endpoints
========================

Endpoints that test individual layers without browser dependencies.
"""

from fastapi import APIRouter
from typing import Dict, Any
import asyncio

from src.models.element import ElementContext, Platform, StrategyType
from src.layers.semantic_intent import SemanticIntentLayer

router = APIRouter(prefix="/test", tags=["testing"])


@router.post("/semantic_layer")
async def test_semantic_layer(request: Dict[str, Any]):
    """
    Test only the semantic layer without browser dependencies.
    """
    try:
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
            def __init__(self):
                pass
        
        mock_page = MockPage()
        
        # Generate strategies using semantic layer only
        strategies = await layer.generate_strategies(mock_page, context)
        
        # Build response
        response = {
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
        
        return response
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "layer": "semantic_intent"
        }


@router.post("/layer_strategies")
async def test_layer_strategies(request: Dict[str, Any]):
    """
    Test strategy generation from available layers without browser.
    """
    try:
        results = {}
        
        # Test semantic layer
        semantic_layer = SemanticIntentLayer()
        context = ElementContext(
            platform=Platform(request.get("platform", "salesforce_lightning")),
            page_type=request.get("page_type", "form"),
            intent=request.get("intent", "submit button")
        )
        
        class MockPage:
            pass
        
        mock_page = MockPage()
        
        # Get strategies from semantic layer
        semantic_strategies = await semantic_layer.generate_strategies(mock_page, context)
        
        results["semantic_intent"] = {
            "available": True,
            "strategies_count": len(semantic_strategies),
            "sample_strategies": [
                {
                    "selector": s.selector,
                    "confidence": s.confidence
                }
                for s in semantic_strategies[:3]  # First 3 strategies
            ],
            "metrics": semantic_layer.get_metrics()
        }
        
        # Visual layer would require browser, so mark as unavailable
        results["visual_fingerprint"] = {
            "available": False,
            "reason": "Requires browser automation (Playwright)"
        }
        
        # Other layers (not yet implemented)
        for layer_name in ["contextual_relationship", "behavioral_pattern", 
                          "structural_pattern", "accessibility_bridge", "ml_fusion"]:
            results[layer_name] = {
                "available": False,
                "reason": "Not yet implemented"
            }
        
        return {
            "success": True,
            "platform": request.get("platform"),
            "intent": request.get("intent"),
            "layers": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/system_status")
async def get_system_status():
    """
    Get status of all system components.
    """
    try:
        status = {
            "api": "healthy",
            "layers": {},
            "dependencies": {}
        }
        
        # Test semantic layer
        try:
            layer = SemanticIntentLayer()
            status["layers"]["semantic_intent"] = "available"
        except Exception as e:
            status["layers"]["semantic_intent"] = f"error: {str(e)}"
        
        # Check OpenAI API key
        import os
        if os.getenv("OPENAI_API_KEY"):
            status["dependencies"]["openai"] = "configured"
        else:
            status["dependencies"]["openai"] = "missing"
        
        # Check Playwright
        try:
            from playwright.async_api import async_playwright
            status["dependencies"]["playwright"] = "installed"
        except ImportError:
            status["dependencies"]["playwright"] = "not_installed"
        
        # Check browser availability (this will fail until browsers are installed)
        try:
            from playwright.async_api import async_playwright
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            await browser.close()
            await playwright.stop()
            status["dependencies"]["chromium"] = "available"
        except Exception as e:
            status["dependencies"]["chromium"] = f"unavailable: {str(e)}"
        
        return status
        
    except Exception as e:
        return {
            "api": "error",
            "error": str(e)
        }