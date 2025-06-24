#!/usr/bin/env python3
"""
Salesforce Automation Example
=============================

Shows how to use Helix with login automation for real Salesforce test automation.
This example creates an Opportunity in Salesforce Lightning.
"""

import asyncio
import os
import sys
from playwright.async_api import async_playwright
import requests
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import login automation module
from src.login_automation import LoginHandler

# Load environment variables
load_dotenv()


class HelixSalesforceAutomation:
    """Salesforce automation using Helix for element identification with login automation."""
    
    def __init__(self, helix_url: str = "http://localhost:8000"):
        self.helix_url = helix_url
        
        # Initialize login automation handler
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "src",
            "login_automation", 
            "config",
            "login_config.json"
        )
        self.login_handler = LoginHandler(config_path)
        self.page = None
        
    async def setup(self, headless: bool = False):
        """Set up browser using login automation module."""
        print("🌐 Setting up browser with login automation...")
        await self.login_handler.setup_browser()
        # Get reference to the browser page
        self.page = self.login_handler.page
        print("✅ Browser setup complete")
        
    async def teardown(self):
        """Clean up browser resources using login automation module."""
        print("🧹 Cleaning up browser...")
        await self.login_handler.teardown_browser()
        print("✅ Browser cleanup complete")
    
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
    
    # Get Salesforce credentials from environment
    sf_username = os.getenv("SALESFORCE_USERNAME")
    sf_password = os.getenv("SALESFORCE_PASSWORD") 
    sf_org_url = os.getenv("SALESFORCE_ORG_URL")
    
    if not all([sf_username, sf_password]):
        print("❌ Please set SALESFORCE_USERNAME and SALESFORCE_PASSWORD in .env file")
        print("   Also set SALESFORCE_ORG_URL if using a custom domain")
        return
    
    print(f"🔐 Using credentials from environment:")
    print(f"   Username: {sf_username}")
    print(f"   Org URL: {sf_org_url}")
    
    # Create automation instance
    automation = HelixSalesforceAutomation()
    
    try:
        # Set up browser
        await automation.setup(headless=False)  # Set to True for headless
        
        # Login using login automation module
        print("\n🔐 Logging in using login automation module...")
        credentials = {
            "username": sf_username,
            "password": sf_password,
            "org_url": sf_org_url
        }
        
        success, message = await automation.login_handler.login_to_app("salesforce", credentials)
        
        if not success:
            print(f"❌ Login failed: {message}")
            return
            
        print(f"✅ Login successful: {message}")
        print(f"📍 Current URL: {automation.page.url}")
        
        # Verify login
        verified, verify_message = await automation.login_handler.verify_login_success("salesforce")
        if not verified:
            print(f"⚠️  Login verification failed: {verify_message}")
            return
        
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