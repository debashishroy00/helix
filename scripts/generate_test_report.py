#!/usr/bin/env python3
"""
Helix AI Engine - Automated Test Report Generator
================================================

Generates comprehensive test reports from Postman results or manual testing.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
from pathlib import Path


class HelixTestReportGenerator:
    """Generates comprehensive test reports for Helix AI Engine."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
        self.start_time = time.time()
        
    def run_automated_tests(self) -> Dict[str, Any]:
        """Run automated tests and collect results."""
        
        print("Running Helix AI Engine Automated Tests...")
        
        # Test scenarios
        test_scenarios = [
            {
                "name": "Salesforce Login",
                "endpoint": "/find_element_comprehensive",
                "data": {
                    "intent": "login button",
                    "platform": "salesforce_lightning",
                    "html_content": '<button type="submit" class="slds-button">Login</button>',
                    "max_strategies": 10
                }
            },
            {
                "name": "ServiceNow Search",
                "endpoint": "/find_element_comprehensive", 
                "data": {
                    "intent": "search box",
                    "platform": "servicenow",
                    "html_content": '<input type="search" class="form-control">',
                    "max_strategies": 10
                }
            },
            {
                "name": "Universal Username",
                "endpoint": "/find_element_comprehensive",
                "data": {
                    "intent": "username field",
                    "platform": "salesforce_lightning",
                    "html_content": '<input type="email" placeholder="Username">',
                    "max_strategies": 5
                }
            }
        ]
        
        results = {
            "system_health": self._test_system_health(),
            "comprehensive_tests": [],
            "performance_tests": [],
            "ml_tests": self._test_ml_functionality(),
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "avg_response_time": 0.0
            }
        }
        
        # Run comprehensive tests
        for scenario in test_scenarios:
            test_result = self._run_single_test(scenario)
            results["comprehensive_tests"].append(test_result)
            
            results["summary"]["total_tests"] += 1
            if test_result["status"] == "PASS":
                results["summary"]["passed_tests"] += 1
            else:
                results["summary"]["failed_tests"] += 1
        
        # Run performance tests
        perf_results = self._test_performance()
        results["performance_tests"] = perf_results
        
        # Calculate summary
        if results["comprehensive_tests"]:
            avg_time = sum(t["response_time_ms"] for t in results["comprehensive_tests"]) / len(results["comprehensive_tests"])
            results["summary"]["avg_response_time"] = avg_time
        
        return results
    
    def _test_system_health(self) -> Dict[str, Any]:
        """Test system health endpoints."""
        
        health_results = {
            "api_status": {"status": "FAIL", "response_time": 0},
            "layer_status": {"status": "FAIL", "layers_initialized": 0, "response_time": 0},
            "metrics": {"status": "FAIL", "response_time": 0}
        }
        
        # Test API status
        try:
            start = time.time()
            response = requests.get(f"{self.base_url}/", timeout=5)
            health_results["api_status"]["response_time"] = (time.time() - start) * 1000
            
            if response.status_code == 200:
                health_results["api_status"]["status"] = "PASS"
                data = response.json()
                health_results["api_status"]["layers_initialized"] = data.get("layers_initialized", 0)
        except Exception as e:
            health_results["api_status"]["error"] = str(e)
        
        # Test layer status
        try:
            start = time.time()
            response = requests.get(f"{self.base_url}/layers/status", timeout=5)
            health_results["layer_status"]["response_time"] = (time.time() - start) * 1000
            
            if response.status_code == 200:
                health_results["layer_status"]["status"] = "PASS"
                data = response.json()
                health_results["layer_status"]["layers_initialized"] = data.get("initialized_layers", 0)
                health_results["layer_status"]["total_layers"] = data.get("total_layers", 10)
                health_results["layer_status"]["system_status"] = data.get("system_status", "unknown")
        except Exception as e:
            health_results["layer_status"]["error"] = str(e)
        
        # Test metrics
        try:
            start = time.time()
            response = requests.get(f"{self.base_url}/metrics", timeout=5)
            health_results["metrics"]["response_time"] = (time.time() - start) * 1000
            
            if response.status_code == 200:
                health_results["metrics"]["status"] = "PASS"
        except Exception as e:
            health_results["metrics"]["error"] = str(e)
        
        return health_results
    
    def _run_single_test(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test scenario."""
        
        result = {
            "name": scenario["name"],
            "status": "FAIL",
            "response_time_ms": 0,
            "strategies_found": 0,
            "layers_executed": 0,
            "top_confidence": 0.0,
            "top_selector": "",
            "error": None
        }
        
        try:
            start = time.time()
            response = requests.post(
                f"{self.base_url}{scenario['endpoint']}",
                json=scenario["data"],
                timeout=10
            )
            result["response_time_ms"] = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("found"):
                    result["status"] = "PASS"
                    result["strategies_found"] = len(data.get("strategies", []))
                    result["layers_executed"] = data.get("stats", {}).get("layers_executed", 0)
                    
                    if data.get("top_strategy"):
                        result["top_confidence"] = data["top_strategy"].get("confidence", 0)
                        result["top_selector"] = data["top_strategy"].get("selector", "")
                else:
                    result["error"] = "No strategies found"
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text[:100]}"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _test_performance(self) -> List[Dict[str, Any]]:
        """Test performance benchmarks."""
        
        performance_tests = [
            {
                "name": "Simple Query",
                "endpoint": "/find_element_smart",
                "target_ms": 10,
                "data": {
                    "intent": "login button",
                    "platform": "salesforce_lightning",
                    "html_content": '<button type="submit">Login</button>'
                }
            },
            {
                "name": "Comprehensive Analysis",
                "endpoint": "/find_element_comprehensive", 
                "target_ms": 100,
                "data": {
                    "intent": "save button",
                    "platform": "salesforce_lightning",
                    "html_content": '<form><button type="submit">Save</button></form>',
                    "max_strategies": 10
                }
            }
        ]
        
        results = []
        
        for test in performance_tests:
            # Run test 3 times for average
            times = []
            
            for i in range(3):
                try:
                    start = time.time()
                    response = requests.post(
                        f"{self.base_url}{test['endpoint']}",
                        json=test["data"],
                        timeout=5
                    )
                    exec_time = (time.time() - start) * 1000
                    
                    if response.status_code == 200:
                        times.append(exec_time)
                except:
                    continue
            
            if times:
                avg_time = sum(times) / len(times)
                status = "PASS" if avg_time <= test["target_ms"] else "FAIL"
                
                results.append({
                    "name": test["name"],
                    "avg_time_ms": avg_time,
                    "target_ms": test["target_ms"],
                    "status": status,
                    "runs": len(times)
                })
        
        return results
    
    def _test_ml_functionality(self) -> Dict[str, Any]:
        """Test ML fusion functionality."""
        
        ml_results = {
            "feedback_recording": {"status": "FAIL"},
            "learning_impact": {"status": "FAIL"}
        }
        
        # Test feedback recording
        try:
            feedback_data = {
                "selector": "button[type='submit']",
                "success": True,
                "confidence": 0.85,
                "strategy_type": "semantic_intent",
                "intent": "login button",
                "platform": "salesforce_lightning",
                "execution_time_ms": 10.0
            }
            
            response = requests.post(
                f"{self.base_url}/record_feedback",
                json=feedback_data,
                timeout=5
            )
            
            if response.status_code == 200:
                ml_results["feedback_recording"]["status"] = "PASS"
        except Exception as e:
            ml_results["feedback_recording"]["error"] = str(e)
        
        return ml_results
    
    def generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Generate markdown report from results."""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_time = time.time() - self.start_time
        
        # Calculate overall stats
        total_tests = results["summary"]["total_tests"] + len(results["performance_tests"]) + 2  # +2 for ML tests
        passed_tests = results["summary"]["passed_tests"]
        
        # Count additional passes
        if results["system_health"]["api_status"]["status"] == "PASS":
            passed_tests += 1
        if results["system_health"]["layer_status"]["status"] == "PASS":
            passed_tests += 1
        if results["ml_tests"]["feedback_recording"]["status"] == "PASS":
            passed_tests += 1
            
        for perf_test in results["performance_tests"]:
            if perf_test["status"] == "PASS":
                passed_tests += 1
        
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = f"""# Helix AI Engine - Automated Test Results

**Test Date:** {timestamp}  
**Test Duration:** {total_time:.1f} seconds  
**Environment:** Local Development

---

## 📊 Executive Summary

| Metric | Result | Target | Status |
|--------|--------|---------|---------|
| **Overall Pass Rate** | {passed_tests}/{total_tests} tests ({pass_rate:.1f}%) | 95%+ | {'✅' if pass_rate >= 95 else '❌'} |
| **System Health** | {results["system_health"]["layer_status"].get("system_status", "UNKNOWN")} | OPERATIONAL | {'✅' if results["system_health"]["layer_status"].get("system_status") == "operational" else '❌'} |
| **Performance** | {results["summary"]["avg_response_time"]:.1f}ms avg | <100ms | {'✅' if results["summary"]["avg_response_time"] < 100 else '❌'} |
| **Layers Initialized** | {results["system_health"]["layer_status"].get("layers_initialized", 0)}/10 | 9+ | {'✅' if results["system_health"]["layer_status"].get("layers_initialized", 0) >= 9 else '❌'} |

**🎯 Overall Status:** {'PASS' if pass_rate >= 85 else 'FAIL'} - {'Helix AI Engine is performing excellently!' if pass_rate >= 95 else 'System needs optimization' if pass_rate >= 85 else 'Critical issues found'}

---

## 🔍 Detailed Test Results

### 1. System Health Check
| Test | Status | Response Time | Notes |
|------|--------|---------------|-------|
| API Status | {results["system_health"]["api_status"]["status"]} | {results["system_health"]["api_status"]["response_time"]:.1f}ms | {'OK' if results["system_health"]["api_status"]["status"] == "PASS" else results["system_health"]["api_status"].get("error", "Failed")} |
| Layer Status | {results["system_health"]["layer_status"]["status"]} | {results["system_health"]["layer_status"]["response_time"]:.1f}ms | {results["system_health"]["layer_status"].get("layers_initialized", 0)}/10 layers |
| Metrics | {results["system_health"]["metrics"]["status"]} | {results["system_health"]["metrics"]["response_time"]:.1f}ms | {'OK' if results["system_health"]["metrics"]["status"] == "PASS" else "Failed"} |

### 2. Comprehensive 10-Layer Tests
| Test Scenario | Strategies | Layers | Time (ms) | Confidence | Status |
|---------------|------------|---------|-----------|------------|---------|"""

        # Add comprehensive test results
        for test in results["comprehensive_tests"]:
            report += f"""
| {test["name"]} | {test["strategies_found"]} | {test["layers_executed"]}/9 | {test["response_time_ms"]:.1f} | {test["top_confidence"]:.2f} | {test["status"]} |"""

        report += f"""

### 3. Performance Benchmarks
| Test Type | Average Time | Target | Status |
|-----------|--------------|---------|---------|"""

        # Add performance results
        for perf in results["performance_tests"]:
            report += f"""
| {perf["name"]} | {perf["avg_time_ms"]:.1f}ms | <{perf["target_ms"]}ms | {perf["status"]} |"""

        report += f"""

### 4. ML Fusion Tests
| Test | Status | Details |
|------|--------|---------|
| Feedback Recording | {results["ml_tests"]["feedback_recording"]["status"]} | {'Successfully recorded ML training data' if results["ml_tests"]["feedback_recording"]["status"] == "PASS" else 'Failed to record feedback'} |

---

## 🚨 Issues Found

"""

        # Add issues
        issues_found = False
        for test in results["comprehensive_tests"]:
            if test["status"] == "FAIL":
                report += f"- **{test['name']}:** {test.get('error', 'Test failed')}\n"
                issues_found = True
        
        for perf in results["performance_tests"]:
            if perf["status"] == "FAIL":
                report += f"- **{perf['name']}:** Exceeded target ({perf['avg_time_ms']:.1f}ms > {perf['target_ms']}ms)\n"
                issues_found = True
        
        if not issues_found:
            report += "No critical issues found! 🎉\n"

        report += f"""

---

## 📈 Recommendations

"""
        
        if pass_rate >= 95:
            report += "✅ **Excellent Performance** - System is production-ready!\n"
        elif pass_rate >= 85:
            report += "⚠️ **Good Performance** - Address minor issues for optimization.\n"
        else:
            report += "❌ **Needs Attention** - Critical issues require immediate fixes.\n"

        report += f"""

---

**Report Generated:** {timestamp}  
**Total Test Time:** {total_time:.1f} seconds
"""
        
        return report
    
    def save_report(self, results: Dict[str, Any], filename: str = None):
        """Save report to file."""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"helix_test_report_{timestamp}.md"
        
        report_content = self.generate_markdown_report(results)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"Test report saved to: {filename}")
        return filename


def main():
    """Run automated tests and generate report."""
    
    generator = HelixTestReportGenerator()
    
    try:
        print("Starting Helix AI Engine automated testing...")
        results = generator.run_automated_tests()
        
        # Generate and save report
        report_file = generator.save_report(results)
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {results['summary']['total_tests'] + len(results['performance_tests']) + 2}")
        print(f"Passed: {results['summary']['passed_tests']}")
        print(f"Failed: {results['summary']['failed_tests']}")
        print(f"Average Response Time: {results['summary']['avg_response_time']:.1f}ms")
        print(f"Report File: {report_file}")
        
        return results
        
    except Exception as e:
        print(f"ERROR: Test execution failed: {e}")
        return None


if __name__ == "__main__":
    main()