"""
Test suite for updated API implementation
Validates improved schema consistency and error handling
"""
import json
import time
import sys
from updated_api import UpdatedUserAPI


def load_test_data():
    with open("../test_data.json", "r") as f:
        return json.load(f)


def run_tests():
    api = UpdatedUserAPI()
    test_data = load_test_data()
    
    results = []
    total_time = 0
    
    print("=" * 60)
    print("RUNNING TESTS - PROJECT B (UPDATED)")
    print("=" * 60)
    
    for test in test_data:
        test_id = test["id"]
        print(f"\nTest: {test_id}")
        print(f"Description: {test['description']}")
        
        input_data = test["input"]
        expected_status = test["expected_status"]
        expected_output = test["expected_output"]
        
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
        
        # Validate response
        passed = status == expected_status
        schema_valid = True
        
        # Check schema consistency
        if "status" not in response:
            schema_valid = False
        
        if status == 200:
            if expected_output.get("status") == "success":
                passed = passed and response.get("status") == "success"
        
        result = {
            "test_id": test_id,
            "passed": passed,
            "schema_valid": schema_valid,
            "expected_status": expected_status,
            "actual_status": status,
            "response": response,
            "time_ms": round(elapsed * 1000, 2),
            "improvements": []
        }
        
        # Document improvements
        if schema_valid:
            result["improvements"].append("Consistent response schema with 'status' field")
        if status == 200 and "data" in response:
            data = response["data"]
            if "user_id" in data and "email" in data:
                result["improvements"].append("Standardized field naming (user_id, email)")
        if status >= 400 and "message" in response:
            result["improvements"].append("Proper error message format")
        
        results.append(result)
        
        print(f"  Status: {status} (expected: {expected_status})")
        print(f"  Passed: {passed}")
        print(f"  Schema Valid: {schema_valid}")
        print(f"  Time: {result['time_ms']}ms")
        if result["improvements"]:
            print(f"  Improvements: {len(result['improvements'])} detected")
    
    # Summary
    passed_count = sum(1 for r in results if r["passed"])
    schema_valid_count = sum(1 for r in results if r["schema_valid"])
    total_count = len(results)
    avg_time = (total_time / total_count * 1000) if total_count > 0 else 0
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {passed_count}/{total_count}")
    print(f"Success Rate: {(passed_count/total_count*100):.1f}%")
    print(f"Schema Validity: {schema_valid_count}/{total_count}")
    print(f"Average Latency: {avg_time:.2f}ms")
    print(f"Total Improvements: {sum(len(r['improvements']) for r in results)}")
    
    return results, {"total_time": total_time, "avg_time": avg_time, "passed": passed_count, 
                     "total": total_count, "schema_valid": schema_valid_count}


if __name__ == "__main__":
    results, metrics = run_tests()
    
    # Save results
    with open("log_optimized.txt", "w") as f:
        f.write("PROJECT B - UPDATED API TEST RESULTS\n")
        f.write("=" * 60 + "\n\n")
        for r in results:
            f.write(f"Test: {r['test_id']}\n")
            f.write(f"  Passed: {r['passed']}\n")
            f.write(f"  Schema Valid: {r['schema_valid']}\n")
            f.write(f"  Status: {r['actual_status']} (expected: {r['expected_status']})\n")
            f.write(f"  Response: {json.dumps(r['response'])}\n")
            f.write(f"  Time: {r['time_ms']}ms\n")
            if r['improvements']:
                f.write(f"  Improvements: {', '.join(r['improvements'])}\n")
            f.write("\n")
    
    with open("time_optimized.txt", "w") as f:
        f.write(f"Total Time: {metrics['total_time']:.4f}s\n")
        f.write(f"Average Time: {metrics['avg_time']:.2f}ms\n")
        f.write(f"Tests Passed: {metrics['passed']}/{metrics['total']}\n")
        f.write(f"Success Rate: {(metrics['passed']/metrics['total']*100):.1f}%\n")
        f.write(f"Schema Valid: {metrics['schema_valid']}/{metrics['total']}\n")
