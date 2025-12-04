import sys
import json
import time
import threading
import ast
from concurrent.futures import ThreadPoolExecutor
import importlib.util

def count_lines_of_code(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    loc = 0
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
            loc += 1
    return loc

def calculate_cyclomatic_complexity(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    try:
        tree = ast.parse(content)
        complexity = 1  # Base complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler, ast.With, ast.Assert)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity
    except:
        return 1

def run_tests():
    solution_file = sys.argv[1]
    
    # Import solution
    spec = importlib.util.spec_from_file_location("solution", solution_file)
    solution = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(solution)
    
    results = {
        "success": True,
        "tests": {},
        "metrics": {}
    }
    
    test_results = []
    
    # Test 1: Basic allow/reject functionality
    try:
        limiter = solution.RateLimiter(3, 1.0)  # 3 requests per second
        passed = True
        message = "Success"
        
        # Should allow first 3 requests
        for i in range(3):
            if not limiter.is_allowed("user1"):
                passed = False
                message = f"Request {i+1} should be allowed but was rejected"
                break
        
        # Should reject 4th request
        if passed and limiter.is_allowed("user1"):
            passed = False
            message = "4th request should be rejected but was allowed"
            
        results["tests"]["test_basic_allow_reject"] = {
            "pass": passed,
            "category": "correctness", 
            "message": message
        }
        test_results.append(passed)
    except Exception as e:
        results["tests"]["test_basic_allow_reject"] = {
            "pass": False,
            "category": "correctness",
            "message": f"Exception: {str(e)}"
        }
        test_results.append(False)
    
    # Test 2: Multiple keys independence
    try:
        limiter = solution.RateLimiter(2, 1.0)  # 2 requests per second
        passed = True
        message = "Success"
        
        # Use up limit for user1
        limiter.is_allowed("user1")
        limiter.is_allowed("user1")
        
        # user2 should still be allowed
        if not limiter.is_allowed("user2"):
            passed = False
            message = "user2 should be allowed independently of user1"
        
        # user1 should be rejected
        if passed and limiter.is_allowed("user1"):
            passed = False
            message = "user1 should be rejected after limit exceeded"
            
        results["tests"]["test_multiple_keys"] = {
            "pass": passed,
            "category": "correctness",
            "message": message
        }
        test_results.append(passed)
    except Exception as e:
        results["tests"]["test_multiple_keys"] = {
            "pass": False,
            "category": "correctness",
            "message": f"Exception: {str(e)}"
        }
        test_results.append(False)
    
    # Test 3: Time window reset
    try:
        limiter = solution.RateLimiter(2, 0.5)  # 2 requests per 0.5 seconds
        passed = True
        message = "Success"
        
        # Use up limit
        limiter.is_allowed("user1")
        limiter.is_allowed("user1")
        
        # Should be rejected
        if limiter.is_allowed("user1"):
            passed = False
            message = "Request should be rejected immediately after limit"
        
        # Wait for time window to pass
        time.sleep(0.6)
        
        # Should be allowed again
        if passed and not limiter.is_allowed("user1"):
            passed = False
            message = "Request should be allowed after time window reset"
            
        results["tests"]["test_time_window_reset"] = {
            "pass": passed,
            "category": "correctness",
            "message": message
        }
        test_results.append(passed)
    except Exception as e:
        results["tests"]["test_time_window_reset"] = {
            "pass": False,
            "category": "correctness",
            "message": f"Exception: {str(e)}"
        }
        test_results.append(False)
    
    # Test 4: Edge cases
    try:
        passed = True
        message = "Success"
        
        # Test zero limit
        limiter = solution.RateLimiter(0, 1.0)
        if limiter.is_allowed("user1"):
            passed = False
            message = "Zero limit should reject all requests"
        
        # Test empty key
        if passed:
            limiter = solution.RateLimiter(1, 1.0)
            if not limiter.is_allowed(""):
                passed = False
                message = "Empty key should be handled gracefully"
            
        results["tests"]["test_edge_cases"] = {
            "pass": passed,
            "category": "edge_cases",
            "message": message
        }
        test_results.append(passed)
    except Exception as e:
        results["tests"]["test_edge_cases"] = {
            "pass": False,
            "category": "edge_cases",
            "message": f"Exception: {str(e)}"
        }
        test_results.append(False)
    
    # Test 5: Reset functionality
    try:
        limiter = solution.RateLimiter(1, 1.0)
        passed = True
        message = "Success"
        
        # Use up limit
        limiter.is_allowed("user1")
        limiter.is_allowed("user2")
        
        # Reset specific key
        limiter.reset("user1")
        
        # user1 should be allowed, user2 should still be rejected
        if not limiter.is_allowed("user1"):
            passed = False
            message = "user1 should be allowed after reset"
        
        if passed and limiter.is_allowed("user2"):
            passed = False
            message = "user2 should still be rejected after user1 reset"
        
        # Reset all
        limiter.reset()
        if passed and not limiter.is_allowed("user2"):
            passed = False
            message = "user2 should be allowed after global reset"
            
        results["tests"]["test_reset_functionality"] = {
            "pass": passed,
            "category": "edge_cases",
            "message": message
        }
        test_results.append(passed)
    except Exception as e:
        results["tests"]["test_reset_functionality"] = {
            "pass": False,
            "category": "edge_cases",
            "message": f"Exception: {str(e)}"
        }
        test_results.append(False)
    
    # Test 6: Performance stress test
    try:
        limiter = solution.RateLimiter(1000, 1.0)
        start_time = time.time()
        
        # Test with many requests and keys
        def make_requests():
            for i in range(100):
                limiter.is_allowed(f"user{i % 10}")
        
        # Run concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_requests) for _ in range(10)]
            for future in futures:
                future.result()
        
        duration = time.time() - start_time
        passed = duration < 1.0  # Should complete within 1 second
        message = f"Completed in {duration:.3f} seconds"
        
        results["tests"]["test_performance_stress"] = {
            "pass": passed,
            "category": "performance",
            "message": message
        }
        test_results.append(passed)
        perf_score = max(0.0, min(1.0, (1.0 - duration) / 1.0)) if duration <= 2.0 else 0.0
    except Exception as e:
        results["tests"]["test_performance_stress"] = {
            "pass": False,
            "category": "performance",
            "message": f"Exception: {str(e)}"
        }
        test_results.append(False)
        perf_score = 0.0
    
    # Calculate metrics
    correctness_score = sum(test_results) / len(test_results)
    
    # Calculate simplicity score
    loc = count_lines_of_code(solution_file)
    complexity = calculate_cyclomatic_complexity(solution_file)
    
    # Simplicity scoring (lower is better)
    loc_score = max(0.0, min(1.0, (100 - loc) / 100)) if loc <= 200 else 0.0
    complexity_score = max(0.0, min(1.0, (50 - complexity) / 50)) if complexity <= 100 else 0.0
    simplicity_score = (loc_score + complexity_score) / 2
    
    results["metrics"] = {
        "correctness_score": correctness_score,
        "simplicity_score": simplicity_score,
        "performance_score": perf_score,
        "lines_of_code": loc,
        "cyclomatic_complexity": complexity
    }
    
    # Check if all tests passed
    results["success"] = all(test_results)
    
    print(json.dumps(results, indent=2))
    return 0 if results["success"] else 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)