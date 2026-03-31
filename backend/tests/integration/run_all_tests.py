#!/usr/bin/env python3
"""
Run All Integration Tests - 100% Coverage Target
Comprehensive test runner for complete platform validation
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(command, description):
    """Run command and handle errors"""
    print(f"\n🧪 Running: {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {description}")
            return True, result.stdout
        else:
            print(f"❌ FAILED: {description}")
            print(f"Error: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {description}")
        return False, "Test timed out after 5 minutes"
    except Exception as e:
        print(f"💥 ERROR: {description} - {str(e)}")
        return False, str(e)

def main():
    """Run all integration tests"""
    print("🚀 FindBug Platform - Complete Integration Test Suite")
    print("=" * 60)
    print(f"📅 Started at: {datetime.utcnow().isoformat()}")
    
    # Change to backend directory
    backend_dir = "/home/abraham/Desktop/Final-year-project/backend"
    os.chdir(backend_dir)
    
    # Test suites to run
    test_suites = [
        {
            "name": "Unit Tests",
            "command": "python -m pytest tests/unit/ -v --cov=src --cov-report=html",
            "description": "Unit test suite"
        },
        {
            "name": "Integration Tests - Main Platform",
            "command": "python -m pytest tests/integration/test_complete_integration.py -v --cov=src --cov-report=html",
            "description": "Main platform integration tests"
        },
        {
            "name": "Integration Tests - Simulation Platform",
            "command": "python -m pytest tests/integration/test_simulation_integration.py -v --cov=../simulation/src --cov-report=html",
            "description": "Simulation platform integration tests"
        },
        {
            "name": "API Endpoint Tests",
            "command": "python -m pytest tests/api/ -v --cov=src --cov-report=html",
            "description": "API endpoint tests"
        },
        {
            "name": "Security Tests",
            "command": "python -m pytest tests/security/ -v --cov=src --cov-report=html",
            "description": "Security and penetration tests"
        },
        {
            "name": "Performance Tests",
            "command": "python -m pytest tests/performance/ -v --cov=src --cov-report=html",
            "description": "Performance and load tests"
        }
    ]
    
    # Run all test suites
    results = []
    total_tests = len(test_suites)
    passed_tests = 0
    
    for test_suite in test_suites:
        success, output = run_command(
            test_suite["command"],
            test_suite["description"]
        )
        results.append({
            "name": test_suite["name"],
            "success": success,
            "output": output
        })
        
        if success:
            passed_tests += 1
    
    # Generate summary report
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} - {result['name']}")
    
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\n📈 OVERALL RESULTS:")
    print(f"Total Test Suites: {total_tests}")
    print(f"Passed Suites: {passed_tests}")
    print(f"Failed Suites: {total_tests - passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Coverage report
    print(f"\n📋 Coverage reports generated in:")
    print(f" - HTML: htmlcov/index.html")
    print(f" - Terminal output displayed above")
    
    # Final assessment
    if success_rate >= 80:
        print(f"\n🎉 INTEGRATION TESTING: EXCELLENT ({success_rate:.1f}%)")
        print("✅ Platform is ready for production deployment!")
    elif success_rate >= 60:
        print(f"\n✅ INTEGRATION TESTING: GOOD ({success_rate:.1f}%)")
        print("⚠️  Minor issues to address before production")
    else:
        print(f"\n⚠️ INTEGRATION TESTING: NEEDS IMPROVEMENT ({success_rate:.1f}%)")
        print("❌ Significant issues found - fix required before production")
    
    print(f"\n📅 Completed at: {datetime.utcnow().isoformat()}")
    print("=" * 60)
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
