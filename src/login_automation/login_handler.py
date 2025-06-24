#!/usr/bin/env python3
"""
Login Handler for Enterprise Applications
========================================

Robust, app-specific login automation for Salesforce, SAP, Oracle, and Workday.
Part of the Helix project but uses deterministic patterns instead of 10-layer approach.
"""

import asyncio
import json
import logging
import os
import random
import time
from typing import Dict, List, Optional, Tuple, Any
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LoginHandler:
    """Main login handler for enterprise applications."""
    
    def __init__(self, config_path: str = None):
        """Initialize login handler with configuration."""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config", "login_config.json")
        
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("Helix.LoginHandler")
        logger.setLevel(getattr(logging, self.config["logging"]["level"]))
        
        # Create formatter
        formatter = logging.Formatter(self.config["logging"]["format"])
        
        # File handler
        log_file = os.path.join(os.path.dirname(__file__), "logs", self.config["logging"]["file"])
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    async def setup_browser(self, stealth_mode: bool = False) -> None:
        """Initialize Playwright browser and context with optional stealth features."""
        try:
            self.playwright = await async_playwright().start()
            
            browser_settings = self.config["browser_settings"]
            
            # Enhanced stealth arguments for anti-bot detection
            stealth_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-extensions-http-throttling',
                '--disable-client-side-phishing-detection',
                '--disable-sync',
                '--disable-default-apps',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-ipc-flooding-protection',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',
                '--disable-javascript-harmony-shipping',
                '--disable-component-extensions-with-background-pages',
                '--disable-background-mode'
            ] if stealth_mode else ['--disable-blink-features=AutomationControlled']
            
            self.browser = await self.playwright.chromium.launch(
                headless=browser_settings["headless"],
                args=stealth_args
            )
            
            # Enhanced context with realistic user agent and headers
            context_options = {
                "viewport": browser_settings["viewport"],
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "locale": "en-US",
                "timezone_id": "America/New_York"
            }
            
            if stealth_mode:
                context_options.update({
                    "java_script_enabled": True,
                    "bypass_csp": True,
                    "extra_http_headers": {
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate",
                        "DNT": "1",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none",
                        "Cache-Control": "max-age=0"
                    }
                })
            
            self.context = await self.browser.new_context(**context_options)
            
            self.page = await self.context.new_page()
            self.page.set_default_timeout(browser_settings["timeout"])
            
            # Remove automation indicators
            if stealth_mode:
                await self.page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    // Override the `plugins` property to use a custom getter.
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    
                    // Override the `languages` property to use a custom getter.
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en'],
                    });
                    
                    // Override the chrome property
                    window.chrome = {
                        runtime: {},
                    };
                    
                    // Override permissions API
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                """)
            
            self.logger.info(f"Browser initialized successfully (stealth: {stealth_mode})")
            
            # Mark if stealth mode is enabled
            if stealth_mode:
                self._stealth_mode_enabled = True
            
        except Exception as e:
            self.logger.error(f"Failed to setup browser: {e}")
            raise
    
    async def teardown_browser(self) -> None:
        """Clean up browser resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            
            self.logger.info("Browser cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Error during browser cleanup: {e}")
    
    async def find_element_with_fallbacks(self, selectors: List[str], timeout: int = 10000) -> Optional[str]:
        """Try multiple selectors and return the first one that exists."""
        for selector in selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=timeout)
                count = await self.page.locator(selector).count()
                if count > 0:
                    self.logger.debug(f"Found element with selector: {selector}")
                    return selector
            except Exception:
                continue
        
        self.logger.warning(f"No element found with any of these selectors: {selectors}")
        return None
    
    async def wait_for_navigation_or_element(self, success_selectors: List[str], timeout: int = 30000) -> bool:
        """Wait for either navigation or success indicators."""
        start_time = time.time()
        
        while (time.time() - start_time) * 1000 < timeout:
            # Check for success indicators
            for selector in success_selectors:
                try:
                    count = await self.page.locator(selector).count()
                    if count > 0:
                        self.logger.info(f"Success indicator found: {selector}")
                        return True
                except Exception:
                    continue
            
            # Check if URL changed (navigation occurred)
            current_url = self.page.url
            if "login" not in current_url.lower():
                self.logger.info(f"Navigation detected, current URL: {current_url}")
                return True
            
            await asyncio.sleep(1)
        
        return False
    
    async def handle_mfa(self, app_config: Dict[str, Any]) -> bool:
        """Handle Multi-Factor Authentication if prompted."""
        mfa_selectors = app_config["selectors"]["mfa_code"]
        
        # Check if MFA is required
        mfa_field = await self.find_element_with_fallbacks(mfa_selectors, timeout=5000)
        if not mfa_field:
            return True  # No MFA required
        
        self.logger.info("MFA detected, waiting for user input...")
        
        # In a production system, you might:
        # 1. Integrate with authenticator apps
        # 2. Send SMS/email notifications
        # 3. Use hardware tokens
        # For now, we'll wait for manual entry
        
        try:
            # Wait for the user to fill the MFA field
            await self.page.wait_for_function(
                f"document.querySelector('{mfa_field}').value.length >= 6",
                timeout=60000  # 1 minute for user to enter MFA
            )
            
            # Submit MFA
            submit_button = await self.find_element_with_fallbacks([
                "button[type='submit']",
                "input[type='submit']",
                "[value*='Verify' i]",
                "[value*='Submit' i]"
            ])
            
            if submit_button:
                await self.page.click(submit_button)
                self.logger.info("MFA submitted")
                return True
            
        except Exception as e:
            self.logger.error(f"MFA handling failed: {e}")
            return False
        
        return False
    
    # ============================================================================
    # SALESFORCE LOGIN
    # ============================================================================
    
    async def random_delay(self, min_ms: int = 500, max_ms: int = 2000) -> None:
        """Add random delay to simulate human behavior."""
        delay = random.uniform(min_ms / 1000, max_ms / 1000)
        await asyncio.sleep(delay)
    
    async def human_like_type(self, selector: str, text: str, typing_delay: Tuple[int, int] = (50, 150)) -> None:
        """Type text with human-like delays between keystrokes."""
        await self.page.click(selector)
        await self.random_delay(100, 300)
        
        for char in text:
            await self.page.keyboard.type(char)
            delay = random.uniform(typing_delay[0], typing_delay[1]) / 1000
            await asyncio.sleep(delay)
    
    async def simulate_mouse_movement(self) -> None:
        """Simulate natural mouse movements."""
        try:
            # Get viewport dimensions
            viewport = await self.page.viewport_size()
            width = viewport["width"]
            height = viewport["height"]
            
            # Generate random mouse movements
            for _ in range(random.randint(2, 5)):
                x = random.randint(50, width - 50)
                y = random.randint(50, height - 50)
                await self.page.mouse.move(x, y)
                await self.random_delay(100, 500)
        except Exception as e:
            self.logger.debug(f"Mouse movement simulation failed: {e}")
    
    async def login_salesforce(self, credentials: Dict[str, str]) -> Tuple[bool, str]:
        """Enhanced Salesforce login with anti-bot detection measures."""
        try:
            app_config = self.config["apps"]["salesforce"]
            
            # Determine the correct login URL
            if credentials.get("org_url"):
                # If org_url is provided, use it directly for custom domains
                org_url = credentials["org_url"]
                if "my.salesforce.com" in org_url or "develop.my.salesforce.com" in org_url:
                    # This is a custom domain, use it directly
                    login_url = org_url
                else:
                    # Generic domain, use standard login
                    login_url = credentials.get("login_url", app_config["login_url"])
            else:
                login_url = credentials.get("login_url", app_config["login_url"])
            
            self.logger.info(f"Starting enhanced Salesforce login to: {login_url}")
            
            # Ensure stealth mode is enabled for Salesforce
            # Only reinitialize if browser is not already in stealth mode
            if not self.browser or not hasattr(self, '_stealth_mode_enabled'):
                if self.browser:
                    await self.teardown_browser()
                await self.setup_browser(stealth_mode=True)
                self._stealth_mode_enabled = True
            
            # Random delay before navigation
            await self.random_delay(1000, 3000)
            
            # Navigate with realistic behavior
            await self.page.goto(login_url, wait_until="networkidle", timeout=60000)
            
            # Simulate human-like browsing behavior
            await self.simulate_mouse_movement()
            await self.random_delay(2000, 4000)
            
            # Handle custom domain if we went to generic login first
            if login_url == app_config["login_url"]:
                await self._handle_salesforce_domain(credentials, app_config)
            
            # More random delays and mouse movements
            await self.simulate_mouse_movement()
            await self.random_delay(1500, 3000)
            
            # Fill username with human-like typing
            username_selector = await self.find_element_with_fallbacks(
                app_config["selectors"]["username"]
            )
            if not username_selector:
                return False, "Username field not found"
            
            # Clear field first (human-like behavior)
            await self.page.click(username_selector)
            await self.random_delay(200, 500)
            await self.page.keyboard.press("Control+a")
            await self.random_delay(100, 300)
            
            await self.human_like_type(username_selector, credentials["username"])
            self.logger.info("Username filled with human-like typing")
            
            # Random delay between fields
            await self.random_delay(1000, 2500)
            await self.simulate_mouse_movement()
            
            # Fill password with human-like typing
            password_selector = await self.find_element_with_fallbacks(
                app_config["selectors"]["password"]
            )
            if not password_selector:
                return False, "Password field not found"
            
            # Combine password with security token if provided
            password = credentials["password"]
            if credentials.get("security_token"):
                password += credentials["security_token"]
            
            await self.page.click(password_selector)
            await self.random_delay(200, 500)
            await self.page.keyboard.press("Control+a")
            await self.random_delay(100, 300)
            
            await self.human_like_type(password_selector, password)
            self.logger.info("Password filled with human-like typing")
            
            # Pause before clicking login (human behavior)
            await self.random_delay(1500, 3500)
            await self.simulate_mouse_movement()
            
            # Find and click login button with human-like behavior
            login_button = await self.find_element_with_fallbacks(
                app_config["selectors"]["login_button"]
            )
            if not login_button:
                return False, "Login button not found"
            
            # Hover over button before clicking (human behavior)
            await self.page.hover(login_button)
            await self.random_delay(300, 800)
            
            await self.page.click(login_button)
            self.logger.info("Login button clicked with human-like behavior")
            
            # Handle MFA if prompted with enhanced timing
            await self.random_delay(3000, 5000)  # Wait longer for potential MFA prompt
            mfa_success = await self.handle_mfa(app_config)
            if not mfa_success:
                return False, "MFA handling failed"
            
            # Wait for successful login with increased timeout
            success = await self.wait_for_navigation_or_element(
                app_config["selectors"]["success_indicators"],
                timeout=45000  # Increased timeout for bot detection delays
            )
            
            if success:
                self.logger.info("Enhanced Salesforce login successful")
                # Final human-like behavior
                await self.simulate_mouse_movement()
                return True, "Login successful with anti-bot measures"
            else:
                error_msg = await self._get_salesforce_error()
                return False, f"Login failed: {error_msg}"
                
        except Exception as e:
            self.logger.error(f"Enhanced Salesforce login error: {e}")
            return False, f"Login error: {str(e)}"
    
    async def _handle_salesforce_domain(self, credentials: Dict[str, str], app_config: Dict[str, Any]) -> None:
        """Handle Salesforce custom domain requirement."""
        domain_selectors = app_config["selectors"]["domain_field"]
        domain_field = await self.find_element_with_fallbacks(domain_selectors, timeout=3000)
        
        if domain_field and credentials.get("org_url"):
            # Extract domain from org URL
            org_url = credentials["org_url"]
            if "://" in org_url:
                domain = org_url.split("://")[1].split(".")[0]
                await self.page.fill(domain_field, domain)
                
                # Click continue
                continue_button = await self.find_element_with_fallbacks([
                    "input[type='submit']",
                    "button[type='submit']",
                    ".loginButton"
                ])
                if continue_button:
                    await self.page.click(continue_button)
                    await self.page.wait_for_load_state("networkidle")
                
                self.logger.info(f"Domain '{domain}' submitted")
    
    async def _get_salesforce_error(self) -> str:
        """Extract error message from Salesforce login page."""
        error_selectors = [
            ".loginError",
            ".error",
            ".errorMsg",
            "#error",
            ".message.errorM3"
        ]
        
        for selector in error_selectors:
            try:
                error_element = await self.page.locator(selector).first
                if await error_element.count() > 0:
                    error_text = await error_element.text_content()
                    if error_text and error_text.strip():
                        return error_text.strip()
            except Exception:
                continue
        
        # Also check for specific bot detection messages
        try:
            page_content = await self.page.content()
            if "Please check your username and password" in page_content:
                return "Credentials rejected - possible bot detection or invalid credentials"
            elif "too many login attempts" in page_content.lower():
                return "Rate limited - too many attempts"
            elif "suspicious activity" in page_content.lower():
                return "Account flagged for suspicious activity"
            elif "automation" in page_content.lower():
                return "Automation detected"
        except Exception:
            pass
        
        return "Unknown error occurred"
    
    # ============================================================================
    # SAP LOGIN
    # ============================================================================
    
    async def login_sap(self, credentials: Dict[str, str]) -> Tuple[bool, str]:
        """Login to SAP with client field and session handling."""
        try:
            app_config = self.config["apps"]["sap"]
            login_url = credentials.get("login_url", app_config["login_url"])
            
            self.logger.info(f"Starting SAP login to: {login_url}")
            await self.page.goto(login_url)
            await self.page.wait_for_load_state("networkidle")
            
            # Fill client if provided
            if credentials.get("client"):
                client_selector = await self.find_element_with_fallbacks(
                    app_config["selectors"]["client_field"],
                    timeout=5000
                )
                if client_selector:
                    await self.page.fill(client_selector, credentials["client"])
                    self.logger.info("Client field filled")
            
            # Fill username
            username_selector = await self.find_element_with_fallbacks(
                app_config["selectors"]["username"]
            )
            if not username_selector:
                return False, "Username field not found"
            
            await self.page.fill(username_selector, credentials["username"])
            self.logger.info("Username filled")
            
            # Fill password
            password_selector = await self.find_element_with_fallbacks(
                app_config["selectors"]["password"]
            )
            if not password_selector:
                return False, "Password field not found"
            
            await self.page.fill(password_selector, credentials["password"])
            self.logger.info("Password filled")
            
            # Click login
            login_button = await self.find_element_with_fallbacks(
                app_config["selectors"]["login_button"]
            )
            if not login_button:
                return False, "Login button not found"
            
            await self.page.click(login_button)
            self.logger.info("Login button clicked")
            
            # Handle MFA if prompted
            await asyncio.sleep(2)
            mfa_success = await self.handle_mfa(app_config)
            if not mfa_success:
                return False, "MFA handling failed"
            
            # Wait for successful login
            success = await self.wait_for_navigation_or_element(
                app_config["selectors"]["success_indicators"]
            )
            
            if success:
                self.logger.info("SAP login successful")
                return True, "Login successful"
            else:
                return False, "Login failed - success indicators not found"
                
        except Exception as e:
            self.logger.error(f"SAP login error: {e}")
            return False, f"Login error: {str(e)}"
    
    # ============================================================================
    # ORACLE CLOUD LOGIN
    # ============================================================================
    
    async def login_oracle(self, credentials: Dict[str, str]) -> Tuple[bool, str]:
        """Login to Oracle Cloud with identity domain handling."""
        try:
            app_config = self.config["apps"]["oracle"]
            login_url = credentials.get("login_url", app_config["login_url"])
            
            self.logger.info(f"Starting Oracle login to: {login_url}")
            await self.page.goto(login_url)
            await self.page.wait_for_load_state("networkidle")
            
            # Handle identity domain if needed
            if credentials.get("identity_domain"):
                domain_selector = await self.find_element_with_fallbacks(
                    app_config["selectors"]["domain_field"],
                    timeout=5000
                )
                if domain_selector:
                    await self.page.fill(domain_selector, credentials["identity_domain"])
                    self.logger.info("Identity domain filled")
            
            # Fill username
            username_selector = await self.find_element_with_fallbacks(
                app_config["selectors"]["username"]
            )
            if not username_selector:
                return False, "Username field not found"
            
            await self.page.fill(username_selector, credentials["username"])
            self.logger.info("Username filled")
            
            # Fill password
            password_selector = await self.find_element_with_fallbacks(
                app_config["selectors"]["password"]
            )
            if not password_selector:
                return False, "Password field not found"
            
            await self.page.fill(password_selector, credentials["password"])
            self.logger.info("Password filled")
            
            # Click login
            login_button = await self.find_element_with_fallbacks(
                app_config["selectors"]["login_button"]
            )
            if not login_button:
                return False, "Login button not found"
            
            await self.page.click(login_button)
            self.logger.info("Login button clicked")
            
            # Handle MFA if prompted
            await asyncio.sleep(2)
            mfa_success = await self.handle_mfa(app_config)
            if not mfa_success:
                return False, "MFA handling failed"
            
            # Wait for successful login
            success = await self.wait_for_navigation_or_element(
                app_config["selectors"]["success_indicators"]
            )
            
            if success:
                self.logger.info("Oracle login successful")
                return True, "Login successful"
            else:
                return False, "Login failed - success indicators not found"
                
        except Exception as e:
            self.logger.error(f"Oracle login error: {e}")
            return False, f"Login error: {str(e)}"
    
    # ============================================================================
    # WORKDAY LOGIN
    # ============================================================================
    
    async def login_workday(self, credentials: Dict[str, str]) -> Tuple[bool, str]:
        """Login to Workday with tenant URL handling."""
        try:
            app_config = self.config["apps"]["workday"]
            login_url = credentials.get("login_url", app_config["login_url"])
            
            # If tenant URL is provided, use it as the login URL
            if credentials.get("tenant_url"):
                login_url = credentials["tenant_url"]
                if not login_url.endswith("/login"):
                    login_url = login_url.rstrip("/") + "/login"
            
            self.logger.info(f"Starting Workday login to: {login_url}")
            await self.page.goto(login_url)
            await self.page.wait_for_load_state("networkidle")
            
            # Fill username (email)
            username_selector = await self.find_element_with_fallbacks(
                app_config["selectors"]["username"]
            )
            if not username_selector:
                return False, "Username field not found"
            
            await self.page.fill(username_selector, credentials["username"])
            self.logger.info("Username filled")
            
            # Fill password
            password_selector = await self.find_element_with_fallbacks(
                app_config["selectors"]["password"]
            )
            if not password_selector:
                return False, "Password field not found"
            
            await self.page.fill(password_selector, credentials["password"])
            self.logger.info("Password filled")
            
            # Click login
            login_button = await self.find_element_with_fallbacks(
                app_config["selectors"]["login_button"]
            )
            if not login_button:
                return False, "Login button not found"
            
            await self.page.click(login_button)
            self.logger.info("Login button clicked")
            
            # Handle MFA if prompted
            await asyncio.sleep(2)
            mfa_success = await self.handle_mfa(app_config)
            if not mfa_success:
                return False, "MFA handling failed"
            
            # Wait for successful login
            success = await self.wait_for_navigation_or_element(
                app_config["selectors"]["success_indicators"]
            )
            
            if success:
                self.logger.info("Workday login successful")
                return True, "Login successful"
            else:
                return False, "Login failed - success indicators not found"
                
        except Exception as e:
            self.logger.error(f"Workday login error: {e}")
            return False, f"Login error: {str(e)}"
    
    # ============================================================================
    # UNIVERSAL LOGIN METHOD
    # ============================================================================
    
    async def login_to_app(self, app_name: str, credentials: Dict[str, str]) -> Tuple[bool, str]:
        """Universal login method that routes to app-specific handlers."""
        app_name = app_name.lower()
        
        # Map app names to login methods
        login_methods = {
            "salesforce": self.login_salesforce,
            "sap": self.login_sap,
            "oracle": self.login_oracle,
            "workday": self.login_workday
        }
        
        if app_name not in login_methods:
            return False, f"Unsupported app: {app_name}"
        
        # Execute login with retry logic
        max_retries = self.config["retry_settings"]["max_retries"]
        retry_delay = self.config["retry_settings"]["retry_delay"] / 1000  # Convert to seconds
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Login attempt {attempt + 1}/{max_retries} for {app_name}")
                success, message = await login_methods[app_name](credentials)
                
                if success:
                    return True, message
                
                if attempt < max_retries - 1:
                    self.logger.warning(f"Login attempt {attempt + 1} failed: {message}. Retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    
                    # Refresh the page for retry
                    await self.page.reload()
                    await self.page.wait_for_load_state("networkidle")
                
            except Exception as e:
                self.logger.error(f"Login attempt {attempt + 1} error: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
        
        return False, f"Login failed after {max_retries} attempts"
    
    async def verify_login_success(self, app_name: str) -> Tuple[bool, str]:
        """Verify that login was successful and user is authenticated."""
        app_config = self.config["apps"][app_name.lower()]
        success_indicators = app_config["selectors"]["success_indicators"]
        
        # Check for success indicators
        for indicator in success_indicators:
            try:
                count = await self.page.locator(indicator).count()
                if count > 0:
                    current_url = self.page.url
                    page_title = await self.page.title()
                    return True, f"Login verified - URL: {current_url}, Title: {page_title}"
            except Exception:
                continue
        
        # Check URL for login indicators
        current_url = self.page.url.lower()
        if any(word in current_url for word in ["login", "signin", "auth"]):
            return False, "Still on login page"
        
        # Take screenshot for debugging
        screenshot_path = f"{app_name.lower()}_login_verification.png"
        await self.page.screenshot(path=screenshot_path)
        
        return False, f"Login verification failed. Screenshot saved: {screenshot_path}"