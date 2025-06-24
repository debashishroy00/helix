#!/usr/bin/env python3
"""
Helix Login Automation CLI
==========================

Command-line interface for running login automation within Helix project.
"""

import asyncio
import argparse
import json
import sys
import os
from datetime import datetime

# Add parent directory to path to import from Helix modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.login_automation import LoginOrchestrator


async def main():
    """Main CLI interface for Helix login automation."""
    parser = argparse.ArgumentParser(
        description="Helix Login Automation - Robust enterprise app login handler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.login_automation.cli salesforce          # Login to Salesforce
  python -m src.login_automation.cli salesforce workday  # Login to multiple apps
  python -m src.login_automation.cli --all               # Login to all configured apps
  python -m src.login_automation.cli --all --parallel    # Parallel execution
  python -m src.login_automation.cli --report            # Generate detailed report
        """
    )
    
    parser.add_argument(
        "apps", 
        nargs="*", 
        help="App names to login to (salesforce, sap, oracle, workday)"
    )
    parser.add_argument(
        "--all", 
        action="store_true", 
        help="Login to all configured apps"
    )
    parser.add_argument(
        "--parallel", 
        action="store_true", 
        help="Run logins in parallel (faster but uses more resources)"
    )
    parser.add_argument(
        "--config", 
        help="Path to custom configuration file"
    )
    parser.add_argument(
        "--report", 
        action="store_true",
        help="Save detailed report after execution"
    )
    parser.add_argument(
        "--headless", 
        action="store_true", 
        help="Run browsers in headless mode"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        help="Override default timeout in milliseconds"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    supported_apps = ["salesforce", "sap", "oracle", "workday"]
    
    if args.all:
        target_apps = supported_apps
    elif args.apps:
        target_apps = []
        for app in args.apps:
            if app.lower() in supported_apps:
                target_apps.append(app.lower())
            else:
                print(f"❌ Error: Unsupported app '{app}'. Supported apps: {', '.join(supported_apps)}")
                return 1
    else:
        print("❌ Error: Please specify apps to login to or use --all")
        parser.print_help()
        return 1
    
    # Update config if custom settings provided
    config_path = args.config
    if args.headless or args.timeout:
        # Load and update config
        from src.login_automation.config import load_login_config, update_config_setting
        
        if not config_path:
            config_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "config", 
                "login_config.json"
            )
        
        if args.headless:
            update_config_setting(config_path, "browser_settings", "headless", True)
        
        if args.timeout:
            update_config_setting(config_path, "browser_settings", "timeout", args.timeout)
    
    # Initialize orchestrator
    orchestrator = LoginOrchestrator(config_path)
    
    try:
        # Display header
        print("🚀 HELIX LOGIN AUTOMATION")
        print("=" * 50)
        print(f"Target apps: {', '.join(target_apps)}")
        print(f"Execution mode: {'Parallel' if args.parallel else 'Sequential'}")
        print(f"Browser mode: {'Headless' if args.headless else 'Headed'}")
        print("=" * 50)
        print("")
        
        # Execute logins
        start_time = datetime.now()
        results = await orchestrator.run_multiple_apps(target_apps, sequential=not args.parallel)
        total_duration = (datetime.now() - start_time).total_seconds()
        
        # Generate and display report
        report = orchestrator.generate_report(results)
        print("\n" + report)
        
        print(f"\n⏱  Total execution time: {total_duration:.2f} seconds")
        
        # Save report if requested
        if args.report:
            report_file = orchestrator.save_report(results=results)
            print(f"📄 Detailed report saved: {report_file}")
        
        # Return appropriate exit code
        failed_logins = [r for r in results if not r.get("success")]
        return 1 if failed_logins else 0
        
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def run_cli():
    """Entry point for CLI execution."""
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


if __name__ == "__main__":
    run_cli()