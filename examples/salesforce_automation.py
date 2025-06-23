#!/usr/bin/env python3
"""
Salesforce Automation Example
=============================

Shows how to use Helix for real Salesforce test automation.
This example creates an Opportunity in Salesforce Lightning.
"""

import asyncio
import os
from playwright.async_api import async_playwright
import requests
import json
from typing import Optional, Dict, Any


class HelixSalesforceAutomation:
    """Salesforce automation using Helix for element identification."""
    
    def __init__(self, helix_url: str = "http://localhost:8000"):
        self.helix_url = helix_url
        self.page = None
        self.browser = None
        self.context = None
        
    async def setup(self, headless: bool = False):
        """Set up Playwright browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
    async def teardown(self):
        """Clean up browser resources."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    def find_element_with_helix(self, intent: str, page_type: str) -> Optional[str]:
        """Use Helix API to find element selector."""
        payload = {
            "platform": "salesforce_lightning",
            "url": self.page.url if self.page else "https://example.com",
            "intent": intent,
            "page_type": page_type
        }
        
        try:
            response = requests.post(
                f"{self.helix_url}/find_element",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("found"):
                    print(f"✅ Helix found: {intent}")
                    print(f"   Selector: {result.get('selector')}")
                    print(f"   Strategy: {result.get('strategy_type')}")
                    print(f"   Confidence: {result.get('confidence')}")
                    return result.get("selector")
                else:
                    print(f"❌ Helix couldn't find: {intent}")
                    return None
            else:
                print(f"❌ Helix API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error calling Helix: {str(e)}")
            return None
    
    async def click_element(self, intent: str, page_type: str):
        """Click an element using Helix to find it."""
        selector = self.find_element_with_helix(intent, page_type)
        if selector:
            try:
                # Handle different selector types
                if selector.startswith("//"):
                    # XPath selector
                    await self.page.click(f"xpath={selector}")
                else:
                    # CSS selector
                    await self.page.click(selector)
                print(f"✅ Clicked: {intent}")
                await self.page.wait_for_timeout(1000)  # Wait for any animations
            except Exception as e:
                print(f"❌ Failed to click {intent}: {str(e)}")
                # Fallback to Layer 1 semantic selector
                print("🔄 Trying fallback semantic selector...")
                fallback = self.get_semantic_only_selector(intent, page_type)
                if fallback:
                    await self.page.click(fallback)
    
    async def type_text(self, intent: str, text: str, page_type: str):
        """Type text in an element using Helix to find it."""
        selector = self.find_element_with_helix(intent, page_type)
        if selector:
            try:
                if selector.startswith("//"):
                    await self.page.fill(f"xpath={selector}", text)
                else:
                    await self.page.fill(selector, text)
                print(f"✅ Typed '{text}' in: {intent}")
            except Exception as e:
                print(f"❌ Failed to type in {intent}: {str(e)}")
    
    def get_semantic_only_selector(self, intent: str, page_type: str) -> Optional[str]:
        """Get selector using only semantic layer (no browser needed)."""
        payload = {
            "platform": "salesforce_lightning",
            "url": "https://example.com",
            "intent": intent,
            "page_type": page_type
        }
        
        try:
            response = requests.post(
                f"{self.helix_url}/find_element_semantic_only",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("found"):
                    return result.get("selector")
        except:
            pass
        
        return None
    
    async def create_opportunity(self, opp_name: str, amount: str, close_date: str):
        """Example: Create a new opportunity in Salesforce."""
        print("\n🚀 Creating Opportunity with Helix Element Finding")
        print("=" * 50)
        
        # Navigate to opportunities
        print("\n1. Navigating to Opportunities...")
        await self.click_element("app launcher", "home")
        await self.click_element("opportunities app", "app_launcher")
        
        # Click New Opportunity
        print("\n2. Creating new opportunity...")
        await self.click_element("new opportunity button", "opportunity_list")
        
        # Fill opportunity details
        print("\n3. Filling opportunity details...")
        await self.type_text("opportunity name field", opp_name, "opportunity_form")
        await self.type_text("amount field", amount, "opportunity_form")
        await self.type_text("close date field", close_date, "opportunity_form")
        
        # Select stage
        print("\n4. Selecting stage...")
        await self.click_element("stage dropdown", "opportunity_form")
        await self.click_element("prospecting stage option", "dropdown")
        
        # Save
        print("\n5. Saving opportunity...")
        await self.click_element("save button", "opportunity_form")
        
        print("\n✅ Opportunity created successfully!")


async def main():
    """Run the Salesforce automation example."""
    print("🌟 Helix Salesforce Automation Example")
    print("=" * 50)
    
    # Check if Helix is running
    try:
        health = requests.get("http://localhost:8000/")
        if health.status_code != 200:
            print("❌ Helix API is not running. Start it with: helix.bat")
            return
    except:
        print("❌ Cannot connect to Helix API. Start it with: helix.bat")
        return
    
    # Get Salesforce credentials
    sf_url = os.getenv("SALESFORCE_URL", "")
    sf_username = os.getenv("SALESFORCE_USERNAME", "")
    sf_password = os.getenv("SALESFORCE_PASSWORD", "")
    
    if not sf_url:
        print("\n📝 Enter your Salesforce Lightning URL:")
        print("   Example: https://your-domain.lightning.force.com")
        sf_url = input("URL: ").strip()
    
    if not sf_username:
        print("\n📝 Enter your Salesforce username:")
        sf_username = input("Username: ").strip()
    
    if not sf_password:
        import getpass
        print("\n📝 Enter your Salesforce password:")
        sf_password = getpass.getpass("Password: ")
    
    # Create automation instance
    automation = HelixSalesforceAutomation()
    
    try:
        # Set up browser
        await automation.setup(headless=False)  # Set to True for headless
        
        # Navigate to Salesforce
        print(f"\n🌐 Navigating to {sf_url}...")
        await automation.page.goto(sf_url)
        
        # Login if needed
        if "login" in automation.page.url.lower():
            print("\n🔐 Logging in...")
            await automation.type_text("username field", sf_username, "login")
            await automation.type_text("password field", sf_password, "login")
            await automation.click_element("login button", "login")
            
            # Wait for login
            await automation.page.wait_for_timeout(5000)
        
        # Example: Create an opportunity
        await automation.create_opportunity(
            opp_name="Helix Test Opportunity",
            amount="50000",
            close_date="12/31/2025"
        )
        
        # Wait to see results
        print("\n⏸️  Pausing to show results (press Enter to continue)...")
        input()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        
    finally:
        # Clean up
        await automation.teardown()
        print("\n✅ Automation complete!")


if __name__ == "__main__":
    asyncio.run(main())