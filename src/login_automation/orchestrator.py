#!/usr/bin/env python3
"""
Login Orchestrator - Coordinates Multi-App Login Automation
==========================================================

Part of Helix project - manages login automation across multiple enterprise apps.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any

from .login_handler import LoginHandler
from .config import load_credentials_from_env


class LoginOrchestrator:
    """Orchestrates login automation across multiple enterprise apps."""
    
    def __init__(self, config_path: str = None):
        """Initialize the orchestrator."""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config", "login_config.json")
            
        self.config_path = config_path
        self.login_handler = LoginHandler(config_path)
        self.results: List[Dict[str, Any]] = []
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup orchestrator logging."""
        logger = logging.getLogger("Helix.LoginOrchestrator")
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def load_app_credentials(self, app_name: str) -> Dict[str, str]:
        """Load credentials for a specific app."""
        try:
            # Try loading from environment variables first
            credentials = load_credentials_from_env(app_name)
            
            if not credentials:
                # Fallback to manual input or configuration file
                self.logger.warning(f"No credentials found in environment for {app_name}")
                return {}
            
            # Validate required credentials
            required_fields = self._get_required_credentials(app_name)
            missing_fields = [field for field in required_fields if not credentials.get(field)]
            
            if missing_fields:
                self.logger.warning(f"Missing required credentials for {app_name}: {missing_fields}")
                return {}
            
            self.logger.info(f"Credentials loaded for {app_name}")
            return credentials
            
        except Exception as e:
            self.logger.error(f"Error loading credentials for {app_name}: {e}")
            return {}
    
    def _get_required_credentials(self, app_name: str) -> List[str]:
        """Get required credential fields for each app."""
        required_creds = {
            "salesforce": ["username", "password"],
            "sap": ["username", "password", "login_url"],
            "oracle": ["username", "password", "login_url"],
            "workday": ["username", "password"]
        }
        return required_creds.get(app_name.lower(), ["username", "password"])
    
    async def login_to_app(self, app_name: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Login to a specific app and return detailed results."""
        start_time = datetime.now()
        
        result = {
            "app_name": app_name,
            "start_time": start_time.isoformat(),
            "success": False,
            "message": "",
            "duration_seconds": 0,
            "url": "",
            "page_title": "",
            "screenshot_path": ""
        }
        
        try:
            self.logger.info(f"🚀 Starting login for {app_name}...")
            
            # Attempt login
            success, message = await self.login_handler.login_to_app(app_name, credentials)
            
            # Update result
            result["success"] = success
            result["message"] = message
            result["duration_seconds"] = (datetime.now() - start_time).total_seconds()
            
            if success:
                # Verify login and get additional info
                verify_success, verify_message = await self.login_handler.verify_login_success(app_name)
                result["url"] = self.login_handler.page.url
                result["page_title"] = await self.login_handler.page.title()
                
                if not verify_success:
                    result["message"] += f" (Verification failed: {verify_message})"
                
                # Take success screenshot
                screenshot_dir = os.path.join(os.path.dirname(__file__), "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                
                screenshot_path = os.path.join(
                    screenshot_dir,
                    f"{app_name.lower()}_success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
                await self.login_handler.page.screenshot(path=screenshot_path)
                result["screenshot_path"] = screenshot_path
                
                self.logger.info(f"✅ {app_name} login successful in {result['duration_seconds']:.2f}s")
            else:
                # Take failure screenshot
                screenshot_dir = os.path.join(os.path.dirname(__file__), "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                
                screenshot_path = os.path.join(
                    screenshot_dir,
                    f"{app_name.lower()}_failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
                await self.login_handler.page.screenshot(path=screenshot_path)
                result["screenshot_path"] = screenshot_path
                
                self.logger.error(f"❌ {app_name} login failed: {message}")
        
        except Exception as e:
            result["message"] = f"Exception occurred: {str(e)}"
            result["duration_seconds"] = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"❌ {app_name} login error: {e}")
        
        return result
    
    async def run_single_app(self, app_name: str) -> Dict[str, Any]:
        """Run login automation for a single app."""
        self.logger.info(f"Running login automation for {app_name}")
        
        # Load credentials
        credentials = self.load_app_credentials(app_name)
        if not credentials:
            return {
                "app_name": app_name,
                "success": False,
                "message": "Failed to load credentials",
                "duration_seconds": 0
            }
        
        # Setup browser
        await self.login_handler.setup_browser()
        
        try:
            # Execute login
            result = await self.login_to_app(app_name, credentials)
            return result
        
        finally:
            # Cleanup
            await self.login_handler.teardown_browser()
    
    async def run_multiple_apps(self, app_names: List[str], sequential: bool = True) -> List[Dict[str, Any]]:
        """Run login automation for multiple apps."""
        self.logger.info(f"Running login automation for {len(app_names)} apps: {app_names}")
        
        if sequential:
            # Sequential execution
            results = []
            for app_name in app_names:
                result = await self.run_single_app(app_name)
                results.append(result)
                self.results.append(result)
                
                # Brief pause between apps
                await asyncio.sleep(2)
            
            return results
        else:
            # Parallel execution (requires multiple browser instances)
            tasks = []
            for app_name in app_names:
                # Create separate handler for each app
                handler = LoginHandler(self.config_path)
                credentials = self.load_app_credentials(app_name)
                
                if credentials:
                    task = self._run_app_with_handler(handler, app_name, credentials)
                    tasks.append(task)
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results and handle exceptions
                processed_results = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        processed_results.append({
                            "app_name": app_names[i],
                            "success": False,
                            "message": f"Parallel execution error: {str(result)}",
                            "duration_seconds": 0
                        })
                    else:
                        processed_results.append(result)
                
                self.results.extend(processed_results)
                return processed_results
            
            return []
    
    async def _run_app_with_handler(self, handler: LoginHandler, app_name: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Helper method for parallel execution."""
        await handler.setup_browser()
        try:
            success, message = await handler.login_to_app(app_name, credentials)
            
            result = {
                "app_name": app_name,
                "success": success,
                "message": message,
                "url": handler.page.url if success else "",
                "page_title": await handler.page.title() if success else ""
            }
            
            return result
        
        finally:
            await handler.teardown_browser()
    
    def generate_report(self, results: List[Dict[str, Any]] = None) -> str:
        """Generate a detailed report of login results."""
        if results is None:
            results = self.results
        
        if not results:
            return "No login results to report."
        
        report = []
        report.append("="*80)
        report.append("HELIX LOGIN AUTOMATION REPORT")
        report.append("="*80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Applications: {len(results)}")
        
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]
        
        report.append(f"Successful Logins: {len(successful)}")
        report.append(f"Failed Logins: {len(failed)}")
        report.append("")
        
        # Detailed results
        for i, result in enumerate(results, 1):
            status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
            report.append(f"{i}. {result['app_name'].upper()} - {status}")
            report.append(f"   Message: {result['message']}")
            
            if result.get("duration_seconds"):
                report.append(f"   Duration: {result['duration_seconds']:.2f} seconds")
            
            if result.get("url"):
                report.append(f"   Final URL: {result['url']}")
            
            if result.get("page_title"):
                report.append(f"   Page Title: {result['page_title']}")
            
            if result.get("screenshot_path"):
                report.append(f"   Screenshot: {result['screenshot_path']}")
            
            report.append("")
        
        # Summary statistics
        if successful:
            avg_duration = sum(r.get("duration_seconds", 0) for r in successful) / len(successful)
            report.append(f"Average successful login time: {avg_duration:.2f} seconds")
        
        report.append("="*80)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = None, results: List[Dict[str, Any]] = None) -> str:
        """Save the report to a file."""
        if filename is None:
            reports_dir = os.path.join(os.path.dirname(__file__), "reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(reports_dir, f"login_report_{timestamp}.txt")
        
        report_content = self.generate_report(results)
        
        with open(filename, 'w') as f:
            f.write(report_content)
        
        self.logger.info(f"Report saved to: {filename}")
        return filename