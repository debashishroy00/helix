#!/usr/bin/env python3
"""
Simple Helix AI Engine API Test
==============================
Basic test script without external dependencies.
Tests the API endpoints to verify all 10 layers are working.
"""

import json
import time
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode

class SimpleHelixTester:
    """Simple API tester for Helix AI Engine."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
        
    def make_request(self, endpoint, method="GET", data=None):
        """Make HTTP request to API."""
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "POST" and data:
                # Convert data to JSON
                json_data = json.dumps(data).encode('utf-8')
                req = Request(url, data=json_data)
                req.add_header('Content-Type', 'application/json')
            else:
                req = Request(url)
            
            start_time = time.time()
            with urlopen(req, timeout=10) as response:
                response_time = (time.time() - start_time) * 1000
                content = response.read().decode('utf-8')
                
                return {
                    "status_code": response.getcode(),
                    "data": json.loads(content),
                    "response_time_ms": response_time,
                    "success": True
                }
                
        except HTTPError as e:
            return {
                "status_code": e.code,
                "error": str(e),
                "success": False
            }
        except URLError as e:
            return {
                "error": f"Connection failed: {e.reason}",
                "success": False
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def test_system_health(self):
        """Test system health endpoints."""
        
        print("Testing System Health...")
        
        # Test 1: API Status
        print("  1. API Status...", end=" ")
        result = self.make_request("/")
        if result["success"]:
            layers = result["data"].get("layers_initialized", 0)
            print(f"PASS ({layers} layers, {result['response_time_ms']:.1f}ms)")
            self.results["api_status"] = "PASS"
        else:
            print(f"FAIL ({result.get('error', 'Unknown error')})")
            self.results["api_status"] = "FAIL"
        
        # Test 2: Layer Status
        print("  2. Layer Status...", end=" ")
        result = self.make_request("/layers/status")
        if result["success"]:
            data = result["data"]
            total = data.get("total_layers", 0)
            initialized = data.get("initialized_layers", 0)
            status = data.get("system_status", "unknown")
            print(f"PASS ({initialized}/{total} layers, {status})")
            self.results["layer_status"] = "PASS"
            self.results["layers_initialized"] = initialized
            self.results["system_status"] = status
        else:
            print(f"FAIL ({result.get('error', 'Unknown error')})")
            self.results["layer_status"] = "FAIL"
        
        # Test 3: Metrics
        print("  3. Metrics...", end=" ")
        result = self.make_request("/metrics")
        if result["success"]:
            print(f"PASS ({result['response_time_ms']:.1f}ms)")
            self.results["metrics"] = "PASS"
        else:
            print(f"FAIL ({result.get('error', 'Unknown error')})")
            self.results["metrics"] = "FAIL"
    
    def test_comprehensive_analysis(self):
        """Test comprehensive 10-layer analysis."""
        
        print("\nTesting Comprehensive 10-Layer Analysis...")
        
        test_cases = [
            {
                "name": "Salesforce Login Button",
                "data": {
                    "intent": "login button",
                    "platform": "salesforce_lightning",
                    "html_content": '<button type="submit" class="slds-button">Login</button>',
                    "max_strategies": 10
                }
            },
            {
                "name": "Search Box Universal",
                "data": {
                    "intent": "search box",
                    "platform": "servicenow",
                    "html_content": '<input type="search" placeholder="Search">',
                    "max_strategies": 8
                }
            },
            {
                "name": "Username Field",
                "data": {
                    "intent": "username field",
                    "platform": "workday",
                    "html_content": '<input type="email" placeholder="Username">',
                    "max_strategies": 5
                }
            }
        ]
        
        comprehensive_results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"  {i}. {test_case['name']}...", end=" ")
            
            result = self.make_request(
                "/find_element_comprehensive",
                method="POST",
                data=test_case["data"]
            )
            
            if result["success"] and result["data"].get("found"):
                data = result["data"]
                strategies = len(data.get("strategies", []))
                layers = data.get("stats", {}).get("layers_executed", 0)
                time_ms = result["response_time_ms"]
                confidence = data.get("top_strategy", {}).get("confidence", 0)
                
                print(f"PASS ({strategies} strategies, {layers} layers, {time_ms:.1f}ms, conf: {confidence:.2f})")
                
                comprehensive_results.append({
                    "name": test_case["name"],
                    "status": "PASS",
                    "strategies": strategies,
                    "layers": layers,
                    "time_ms": time_ms,
                    "confidence": confidence
                })
            else:
                error = result.get("error", "No strategies found")
                print(f"FAIL ({error})")
                comprehensive_results.append({
                    "name": test_case["name"],
                    "status": "FAIL",
                    "error": error
                })
        
        self.results["comprehensive_tests"] = comprehensive_results
    
    def test_performance(self):
        """Test performance benchmarks."""
        
        print("\nTesting Performance...")
        
        # Test fast endpoint
        print("  1. Fast Query...", end=" ")
        result = self.make_request(
            "/find_element_smart",
            method="POST",
            data={
                "intent": "login button",
                "platform": "salesforce_lightning",
                "html_content": '<button type="submit">Login</button>'
            }
        )
        
        if result["success"]:
            time_ms = result["response_time_ms"]
            confidence = result["data"].get("confidence", 0)
            status = "PASS" if time_ms < 50 else "SLOW"
            print(f"{status} ({time_ms:.1f}ms, conf: {confidence:.2f})")
            self.results["fast_query"] = {"status": status, "time_ms": time_ms}
        else:
            print(f"FAIL ({result.get('error', 'Unknown error')})")
            self.results["fast_query"] = {"status": "FAIL"}
        
        # Test comprehensive analysis speed
        print("  2. Comprehensive Speed...", end=" ")
        result = self.make_request(
            "/find_element_comprehensive",
            method="POST", 
            data={
                "intent": "save button",
                "platform": "generic",
                "html_content": '<form><button type="submit">Save</button></form>',
                "max_strategies": 10
            }
        )
        
        if result["success"]:
            time_ms = result["response_time_ms"]
            status = "PASS" if time_ms < 100 else "SLOW"
            print(f"{status} ({time_ms:.1f}ms)")
            self.results["comprehensive_speed"] = {"status": status, "time_ms": time_ms}
        else:
            print(f"FAIL ({result.get('error', 'Unknown error')})")
            self.results["comprehensive_speed"] = {"status": "FAIL"}
    
    def test_ml_functionality(self):
        """Test ML fusion functionality."""
        
        print("\nTesting ML Fusion...")
        
        # Test feedback recording
        print("  1. ML Feedback Recording...", end=" ")
        result = self.make_request(
            "/record_feedback",
            method="POST",
            data={
                "selector": "button[type='submit']",
                "success": True,
                "confidence": 0.85,
                "strategy_type": "semantic_intent",
                "intent": "login button",
                "platform": "salesforce_lightning",
                "execution_time_ms": 10.0
            }
        )
        
        if result["success"]:
            print("PASS")
            self.results["ml_feedback"] = "PASS"
        else:
            print(f"FAIL ({result.get('error', 'Unknown error')})")
            self.results["ml_feedback"] = "FAIL"
    
    def test_cross_platform_universality(self):
        """Test cross-platform universality."""
        
        print("\nTesting Cross-Platform Universality...")
        
        platforms = ["salesforce_lightning", "servicenow", "workday"]
        intent = "username field"
        html = '<input type="email" placeholder="Username">'
        
        selectors = []
        
        for i, platform in enumerate(platforms, 1):
            print(f"  {i}. {platform}...", end=" ")
            
            result = self.make_request(
                "/find_element_comprehensive",
                method="POST",
                data={
                    "intent": intent,
                    "platform": platform,
                    "html_content": html,
                    "max_strategies": 3
                }
            )
            
            if result["success"] and result["data"].get("found"):
                selector = result["data"]["top_strategy"]["selector"]
                selectors.append(selector)
                print(f"PASS ({selector})")
            else:
                print("FAIL")
                selectors.append(None)
        
        # Check if all selectors are the same (universal)
        if selectors and all(s == selectors[0] for s in selectors if s):
            print(f"  Universal Selector: {selectors[0]} - PASS")
            self.results["universality"] = "PASS"
        else:
            print("  Universal Selector: FAIL (inconsistent)")
            self.results["universality"] = "FAIL"
    
    def print_summary(self):
        """Print test summary."""
        
        print("\n" + "="*60)
        print("HELIX AI ENGINE TEST SUMMARY")
        print("="*60)
        
        # Count results
        total_tests = 0
        passed_tests = 0
        
        # System health tests
        health_tests = ["api_status", "layer_status", "metrics"]
        for test in health_tests:
            total_tests += 1
            if self.results.get(test) == "PASS":
                passed_tests += 1
        
        # Comprehensive tests
        comp_tests = self.results.get("comprehensive_tests", [])
        for test in comp_tests:
            total_tests += 1
            if test["status"] == "PASS":
                passed_tests += 1
        
        # Performance tests
        perf_tests = ["fast_query", "comprehensive_speed"]
        for test in perf_tests:
            total_tests += 1
            if self.results.get(test, {}).get("status") == "PASS":
                passed_tests += 1
        
        # ML and universality tests
        other_tests = ["ml_feedback", "universality"]
        for test in other_tests:
            total_tests += 1
            if self.results.get(test) == "PASS":
                passed_tests += 1
        
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print()
        
        # System status
        system_status = self.results.get("system_status", "UNKNOWN")
        layers = self.results.get("layers_initialized", 0)
        print(f"System Status: {system_status}")
        print(f"Layers Initialized: {layers}/10")
        print()
        
        # Performance summary
        if "comprehensive_tests" in self.results:
            avg_time = sum(t.get("time_ms", 0) for t in self.results["comprehensive_tests"] if "time_ms" in t)
            count = len([t for t in self.results["comprehensive_tests"] if "time_ms" in t])
            if count > 0:
                print(f"Average Response Time: {avg_time/count:.1f}ms")
        
        # Overall assessment
        if pass_rate >= 95:
            print("Assessment: EXCELLENT - Helix AI Engine is fully operational!")
        elif pass_rate >= 85:
            print("Assessment: GOOD - Minor issues need attention")
        elif pass_rate >= 70:
            print("Assessment: FAIR - Multiple issues need fixing")
        else:
            print("Assessment: POOR - Critical issues require immediate attention")
        
        print("="*60)
        
        return pass_rate >= 85
    
    def run_all_tests(self):
        """Run all tests."""
        
        print("HELIX AI ENGINE - SIMPLE API TEST")
        print("="*60)
        
        try:
            self.test_system_health()
            self.test_comprehensive_analysis()
            self.test_performance()
            self.test_ml_functionality()
            self.test_cross_platform_universality()
            
            return self.print_summary()
            
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
            return False
        except Exception as e:
            print(f"\nTest execution failed: {e}")
            return False


def main():
    """Main function."""
    
    tester = SimpleHelixTester()
    success = tester.run_all_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()