#!/usr/bin/env python3
"""
Helix Login Automation Examples
==============================

Demonstrates how to use the login automation module within Helix project.
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.login_automation import LoginHandler, LoginOrchestrator


async def example_1_single_app_login():
    """Example 1: Login to a single app (Salesforce)."""
    print("🎯 Example 1: Single App Login")
    print("=" * 40)
    
    orchestrator = LoginOrchestrator()
    
    # This would use credentials from environment variables
    # SALESFORCE_USERNAME, SALESFORCE_PASSWORD, etc.
    try:
        result = await orchestrator.run_single_app("salesforce")
        
        if result["success"]:
            print(f"✅ Login successful!")
            print(f"   URL: {result.get('url', 'N/A')}")
            print(f"   Duration: {result.get('duration_seconds', 0):.2f}s")
        else:
            print(f"❌ Login failed: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_2_multiple_apps_sequential():
    """Example 2: Login to multiple apps sequentially."""
    print("\n🎯 Example 2: Multiple Apps (Sequential)")
    print("=" * 40)
    
    orchestrator = LoginOrchestrator()
    
    # Login to multiple apps one after another
    apps = ["salesforce", "workday"]  # Add apps that have credentials configured
    
    try:
        results = await orchestrator.run_multiple_apps(apps, sequential=True)
        
        # Generate and display report
        report = orchestrator.generate_report(results)
        print(report)
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_3_parallel_execution():
    """Example 3: Login to multiple apps in parallel."""
    print("\n🎯 Example 3: Multiple Apps (Parallel)")
    print("=" * 40)
    
    orchestrator = LoginOrchestrator()
    
    # Login to multiple apps simultaneously (faster)
    apps = ["salesforce", "workday"]
    
    try:
        results = await orchestrator.run_multiple_apps(apps, sequential=False)
        
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]
        
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        
        for result in results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['app_name']}: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def example_4_direct_handler_usage():
    """Example 4: Using LoginHandler directly for fine control."""
    print("\n🎯 Example 4: Direct Handler Usage")
    print("=" * 40)
    
    handler = LoginHandler()
    
    try:
        # Setup browser
        await handler.setup_browser()
        print("✅ Browser initialized")
        
        # Example credentials (would come from environment)
        credentials = {
            "username": "demo@example.com",
            "password": "demo_password",
            "org_url": "https://demo.salesforce.com"
        }
        
        # Attempt login
        success, message = await handler.login_to_app("salesforce", credentials)
        
        if success:
            print(f"✅ Login successful: {message}")
            
            # Verify the login
            verified, verify_msg = await handler.verify_login_success("salesforce")
            print(f"🔍 Verification: {verify_msg}")
            
            # At this point, you could hand off the browser session to Helix
            print(f"🌐 Current URL: {handler.page.url}")
            print("🔄 Ready to hand off to Helix for element identification")
            
        else:
            print(f"❌ Login failed: {message}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        # Always clean up
        await handler.teardown_browser()
        print("🧹 Browser cleaned up")


async def example_5_integration_with_helix():
    """Example 5: Integration pattern with Helix core."""
    print("\n🎯 Example 5: Integration with Helix Core")
    print("=" * 40)
    
    # Step 1: Login using login automation
    handler = LoginHandler()
    
    try:
        await handler.setup_browser()
        
        # Simulate successful login
        print("🔐 1. Logging in with login automation...")
        
        # In real usage, this would be actual login
        credentials = {
            "username": "demo@example.com", 
            "password": "demo_password"
        }
        
        # Mock successful login for demonstration
        print("✅ Login successful (simulated)")
        
        # Step 2: Hand off to Helix for element identification
        print("🔄 2. Handing off to Helix 10-layer system...")
        
        # This is where you would use Helix's Universal Locator
        # Example integration pattern:
        
        try:
            # Import Helix components
            from src.core.universal_locator import UniversalLocator
            from src.models.element import ElementContext, Platform
            
            # Create Helix locator
            locator = UniversalLocator()
            
            # Create element context for finding elements after login
            context = ElementContext(
                platform=Platform.SALESFORCE_LIGHTNING,
                page_type="home",
                intent="new opportunity button"
            )
            
            print("🧠 3. Using Helix to find elements...")
            
            # This would use the authenticated session from login
            # result = await locator.find_element(handler.page, context)
            
            print("✅ Integration pattern demonstrated successfully")
            print("   - Login automation handles authentication")
            print("   - Helix handles dynamic element identification")
            
        except ImportError:
            print("ℹ️  Helix core modules not available (expected in demo)")
            print("   In real usage, this integration would work seamlessly")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        await handler.teardown_browser()


async def example_6_configuration_customization():
    """Example 6: Customizing configuration for specific needs."""
    print("\n🎯 Example 6: Configuration Customization")
    print("=" * 40)
    
    from src.login_automation.config import load_login_config, update_config_setting
    
    config_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "src",
        "login_automation",
        "config",
        "login_config.json"
    )
    
    # Load current configuration
    config = load_login_config(config_path)
    print("📋 Current browser settings:")
    print(f"   Headless: {config['browser_settings']['headless']}")
    print(f"   Timeout: {config['browser_settings']['timeout']}ms")
    
    # Example: Update settings for headless execution
    print("\n🔧 Updating configuration for headless mode...")
    
    # Note: In real usage, you might create a copy of config for modifications
    # update_config_setting(config_path, "browser_settings", "headless", True)
    print("✅ Configuration updated (demo - not actually modified)")
    
    # Show app-specific selectors
    print("\n🎯 Salesforce selector patterns:")
    sf_selectors = config["apps"]["salesforce"]["selectors"]
    for element, patterns in sf_selectors.items():
        print(f"   {element}: {patterns[:2]}...")  # Show first 2 patterns


async def example_7_error_handling_and_debugging():
    """Example 7: Error handling and debugging features."""
    print("\n🎯 Example 7: Error Handling & Debugging")
    print("=" * 40)
    
    handler = LoginHandler()
    
    try:
        await handler.setup_browser()
        
        # Simulate login attempt with invalid credentials
        print("🔐 Attempting login with invalid credentials...")
        
        invalid_credentials = {
            "username": "invalid@example.com",
            "password": "wrong_password"
        }
        
        # This would fail in real usage
        success, message = await handler.login_to_app("salesforce", invalid_credentials)
        
        if not success:
            print(f"❌ Login failed as expected: {message}")
            print("📸 Debug screenshot would be saved to:")
            print("   src/login_automation/screenshots/salesforce_failure_*.png")
            print("📋 Error details would be logged to:")
            print("   src/login_automation/logs/helix_login_automation.log")
        
        # Demonstrate retry mechanism
        print("\n🔄 Retry mechanism would:")
        print("   1. Wait 2 seconds before retry")
        print("   2. Refresh the page")
        print("   3. Attempt login again")
        print("   4. Repeat up to 3 times total")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        await handler.teardown_browser()


async def main():
    """Run all examples."""
    print("🚀 HELIX LOGIN AUTOMATION - EXAMPLES")
    print("=" * 60)
    print("Demonstrating login automation capabilities within Helix project.")
    print("Note: Examples use mock data - real credentials required for actual use.\n")
    
    # Run examples (most are simulated to avoid credential requirements)
    await example_1_single_app_login()
    await example_2_multiple_apps_sequential()
    await example_3_parallel_execution()
    await example_4_direct_handler_usage()
    await example_5_integration_with_helix()
    await example_6_configuration_customization()
    await example_7_error_handling_and_debugging()
    
    print("\n🎉 ALL EXAMPLES COMPLETED!")
    print("=" * 60)
    print("Key Features Demonstrated:")
    print("✅ Single and multi-app login automation")
    print("✅ Sequential and parallel execution modes")
    print("✅ Direct handler usage for fine control")
    print("✅ Integration pattern with Helix core")
    print("✅ Configuration customization")
    print("✅ Error handling and debugging features")
    print("\nReady for production use with real credentials! 🚀")


if __name__ == "__main__":
    asyncio.run(main())