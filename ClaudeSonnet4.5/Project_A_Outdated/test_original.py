"""
Test suite for deprecated API implementation
Exposes issues with schema inconsistency and error handling
"""
import json
import time
import sys
from original_api import DeprecatedUserAPI


def load_test_data():
    with open("../test_data.json", "r") as f:
        return json.load(f)


def run_tests():
    api = DeprecatedUserAPI()
    test_data = load_test_data()
    
    results = []
    total_time = 0
    
    print("=" * 60)
    print("RUNNING TESTS - PROJECT A (OUTDATED)")
    print("=" * 60)
    
    for test in test_data:
        test_id = test["id"]
        print(f"\nTest: {test_id}")
        print(f"Description: {test['description']}")
        
        input_data = test["input"]
        expected_status = test["expected_status"]
        
        start_time = time.time()
        response, status = api.handle_request(
            input_data["endpoint"],
            input_data["method"],
            input_data.get("headers", {}),
            input_data.get("params"),
            input_data.get("body")
        )
        elapsed = time.time() - start_time
        total_time += elapsed
        
        # Check if response matches expected
        passed = status == expected_status
        
        result = {
            "test_id": test_id,
            "passed": passed,
            "expected_status": expected_status,
            "actual_status": status,
            "response": response,
            "time_ms": round(elapsed * 1000, 2),
            "issues": []
        }
        
        # Detect schema issues
        if status == 200 and "username" in response and "userId" in response:
            result["issues"].append("Inconsistent field naming (userId vs user_id)")
        if status == 200 and "mail" in response:
            result["issues"].append("Non-standard field name (mail instead of email)")
        if status >= 400 and "error" in response and "msg" not in response:
            result["issues"].append("Inconsistent error response format")
        
        results.append(result)
        
        print(f"  Status: {status} (expected: {expected_status})")
        print(f"  Passed: {passed}")
        print(f"  Time: {result['time_ms']}ms")
        if result["issues"]:
            print(f"  Issues: {', '.join(result['issues'])}")
    
    # Summary
    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    avg_time = (total_time / total_count * 1000) if total_count > 0 else 0
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {passed_count}/{total_count}")
    print(f"Success Rate: {(passed_count/total_count*100):.1f}%")
    print(f"Average Latency: {avg_time:.2f}ms")
    print(f"Total Issues Found: {sum(len(r['issues']) for r in results)}")
    
    return results, {"total_time": total_time, "avg_time": avg_time, "passed": passed_count, "total": total_count}


if __name__ == "__main__":
    results, metrics = run_tests()
    
    # Save results
    with open("log_original.txt", "w") as f:
        f.write("PROJECT A - OUTDATED API TEST RESULTS\n")
        f.write("=" * 60 + "\n\n")
        for r in results:
            f.write(f"Test: {r['test_id']}\n")
            f.write(f"  Passed: {r['passed']}\n")
            f.write(f"  Status: {r['actual_status']} (expected: {r['expected_status']})\n")
            f.write(f"  Response: {json.dumps(r['response'])}\n")
            f.write(f"  Time: {r['time_ms']}ms\n")
            if r['issues']:
                f.write(f"  Issues: {', '.join(r['issues'])}\n")
            f.write("\n")
    
    with open("time_original.txt", "w") as f:
        f.write(f"Total Time: {metrics['total_time']:.4f}s\n")
        f.write(f"Average Time: {metrics['avg_time']:.2f}ms\n")
        f.write(f"Tests Passed: {metrics['passed']}/{metrics['total']}\n")
        f.write(f"Success Rate: {(metrics['passed']/metrics['total']*100):.1f}%\n")
