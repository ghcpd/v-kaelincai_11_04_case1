"""
Deprecated API Implementation (v1)
Issues: Inconsistent schema, poor error handling, inefficient processing
"""
import json
import time
import random


class DeprecatedUserAPI:
    def __init__(self):
        self.valid_tokens = ["valid_token_123"]
        self.users_db = {
            "12345": {"id": "12345", "username": "johndoe", "mail": "john@example.com"},
            "99999": {"id": "99999", "username": "janesmith", "mail": "jane@example.com"}
        }
    
    def get_user(self, headers, params):
        """Old endpoint with inconsistent response format"""
        time.sleep(random.uniform(0.1, 0.3))  # Simulated latency
        
        # Poor authentication check
        auth = headers.get("Authorization", "")
        if not auth:
            return {"error": "No auth"}, 403
        
        user_id = params.get("user_id")
        if not user_id:
            return {"msg": "Missing ID"}, 400
        
        user = self.users_db.get(user_id)
        if user:
            # Inconsistent field names
            return {
                "username": user["username"],
                "mail": user["mail"],
                "userId": user["id"]
            }, 200
        return {"error": "Not found"}, 404
    
    def create_user(self, headers, body):
        """Old create with no validation"""
        time.sleep(random.uniform(0.15, 0.35))
        
        # Weak validation
        if not body:
            return {"msg": "Empty body"}, 400
        
        # No schema validation - accepts anything
        user_id = body.get("user_id", str(random.randint(10000, 99999)))
        
        # Inconsistent success response
        return {
            "result": "created",
            "id": user_id
        }, 200
    
    def handle_request(self, endpoint, method, headers, params=None, body=None):
        """Main request handler"""
        if endpoint == "/user" and method == "GET":
            return self.get_user(headers, params or {})
        elif endpoint == "/user" and method == "POST":
            return self.create_user(headers, body or {})
        else:
            return {"error": "Unknown endpoint"}, 404


if __name__ == "__main__":
    api = DeprecatedUserAPI()
    
    # Test basic request
    response, status = api.handle_request(
        "/user", "GET",
        {"Authorization": "Bearer valid_token_123"},
        params={"user_id": "12345"}
    )
    print(f"Status: {status}")
    print(f"Response: {json.dumps(response, indent=2)}")
