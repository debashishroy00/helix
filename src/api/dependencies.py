"""
API Dependencies
================

Dependency injection for FastAPI endpoints.
Handles page management, caching, and singleton instances.
"""

from typing import Optional, Dict, Any
import os
from functools import lru_cache

from src.core.universal_locator import UniversalLocator


# Singleton instances
_universal_locator: Optional[UniversalLocator] = None
_cache_client = None
_page_handlers: Dict[str, Any] = {}


@lru_cache()
def get_universal_locator() -> UniversalLocator:
    """Get or create Universal Locator instance."""
    global _universal_locator
    
    if _universal_locator is None:
        # Initialize with cache if available
        cache_client = get_cache_client()
        _universal_locator = UniversalLocator(
            cache_client=cache_client,
            metrics_collector=None  # Would add metrics collector here
        )
    
    return _universal_locator


def get_cache_client():
    """Get Redis cache client."""
    global _cache_client
    
    if _cache_client is None and os.getenv("REDIS_URL"):
        try:
            import redis.asyncio as redis
            _cache_client = redis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                decode_responses=True
            )
        except Exception as e:
            print(f"Failed to connect to Redis: {str(e)}")
    
    return _cache_client


class PageHandler:
    """Manages browser page lifecycle for different platforms."""
    
    def __init__(self, platform: str, url: str):
        self.platform = platform
        self.url = url
        self.page = None
        self.browser = None
        self.playwright = None
    
    async def initialize(self):
        """Initialize browser and navigate to URL."""
        if self.platform in ["salesforce_lightning", "salesforce_classic"]:
            # Use Playwright for Salesforce
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=os.getenv("HEADLESS", "true").lower() == "true"
            )
            
            # Create context with Salesforce-specific settings
            context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            self.page = await context.new_page()
            
            # Navigate to URL
            await self.page.goto(self.url, wait_until="networkidle")
            
            # Wait for Salesforce to fully load
            if "lightning" in self.platform:
                try:
                    await self.page.wait_for_selector(".slds-template__container", timeout=10000)
                except:
                    pass  # Page might not have this element
        
        else:
            # Use Selenium for other platforms
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            if os.getenv("HEADLESS", "true").lower() == "true":
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            self.browser = webdriver.Chrome(options=options)
            self.browser.get(self.url)
            self.page = self.browser
            
            # Platform-specific waits
            if "sap" in self.platform:
                # Wait for SAP UI5 to load
                self.browser.implicitly_wait(10)
    
    async def cleanup(self):
        """Clean up browser resources."""
        try:
            if self.browser:
                if hasattr(self.browser, 'close'):
                    await self.browser.close()
                elif hasattr(self.browser, 'quit'):
                    self.browser.quit()
            
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            print(f"Cleanup error: {str(e)}")


async def get_page_handler(platform: str, url: str) -> PageHandler:
    """Get or create page handler for platform."""
    # In production, would implement page pooling/reuse
    handler = PageHandler(platform, url)
    try:
        await handler.initialize()
    except Exception as e:
        print(f"Warning: Browser initialization failed: {e}")
        # Create a mock page handler for semantic-only testing
        handler.page = MockPage()
    return handler


class MockPage:
    """Mock page object for when browser is not available."""
    def __init__(self):
        pass
    
    async def screenshot(self):
        # Return a minimal PNG for testing
        return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    
    def locator(self, selector):
        return MockLocator()


class MockLocator:
    """Mock locator for testing."""
    async def count(self):
        return 0
    
    @property
    def first(self):
        return None


async def cleanup_all_handlers():
    """Clean up all page handlers on shutdown."""
    global _page_handlers
    
    for handler in _page_handlers.values():
        await handler.cleanup()
    
    _page_handlers.clear()