"""
Updated API Implementation (v2)
Improvements: Unified schema, proper error handling, optimized processing
"""
import json
import time
import random
from typing import Dict, Tuple, Any


class UpdatedUserAPI:
    def __init__(self):
        self.valid_tokens = ["valid_token_123"]
        self.users_db = {
            "12345": {"user_id": "12345", "name": "John Doe", "email": "john@example.com"},
            "99999": {"user_id": "99999", "name": "Jane Smith", "email": "jane@example.com"}
        }
    
    def _validate_auth(self, headers: Dict) -> bool:
        """Enhanced authentication validation"""
        auth = headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return False
        token = auth.replace("Bearer ", "")
        return token in self.valid_tokens
    
    def _standard_response(self, status: str, data: Any = None, message: str = None) -> Dict:
        """Unified response format"""
        response = {"status": status}
        if data is not None:
            response["data"] = data
        if message:
            response["message"] = message
        return response
    
    def get_user(self, headers: Dict, params: Dict) -> Tuple[Dict, int]:
        """Updated endpoint with consistent response format"""
        # Optimized processing - reduced latency
        time.sleep(random.uniform(0.05, 0.15))
        
        # Enhanced authentication
        if not self._validate_auth(headers):
            return self._standard_response("error", message="Unauthorized"), 401
        
        # Input validation
        user_id = params.get("user_id")
        if not user_id:
            return self._standard_response("error", message="Bad Request"), 400
        
        user = self.users_db.get(user_id)
        if user:
            # Consistent field naming
            return self._standard_response("success", data=user), 200
        
        return self._standard_response("error", message="Not Found"), 404
    
    def create_user(self, headers: Dict, body: Dict) -> Tuple[Dict, int]:
        """Updated create with proper validation"""
        # Optimized processing
        time.sleep(random.uniform(0.08, 0.18))
        
        # Authentication check
        if not self._validate_auth(headers):
            return self._standard_response("error", message="Unauthorized"), 401
        
        # Schema validation
        if not body:
            return self._standard_response("error", message="Bad Request"), 400
        
        required_fields = ["user_id"]
        for field in required_fields:
            if field not in body:
                return self._standard_response("error", message="Bad Request"), 400
        
        user_id = body.get("user_id")
        
        # Store with consistent format
        user_data = {
            "user_id": user_id,
            "name": body.get("name", "Unknown"),
            "email": body.get("email", "")
        }
        
        # Handle nested metadata if present
        if "metadata" in body:
            user_data["metadata"] = body["metadata"]
        
        self.users_db[user_id] = user_data
        
        # Consistent success response
        return self._standard_response("success", data={"user_id": user_id}), 200
    
    def handle_request(self, endpoint: str, method: str, headers: Dict, 
                      params: Dict = None, body: Dict = None) -> Tuple[Dict, int]:
        """Main request handler with backward compatibility"""
        # Support both v1 and v2 endpoints
        if endpoint in ["/user", "/v1/user", "/v2/profile"]:
            if method == "GET":
                return self.get_user(headers, params or {})
            elif method == "POST":
                return self.create_user(headers, body or {})
        
        return self._standard_response("error", message="Not Found"), 404


if __name__ == "__main__":
    api = UpdatedUserAPI()
    
    # Test basic request
    response, status = api.handle_request(
        "/v2/profile", "GET",
        {"Authorization": "Bearer valid_token_123"},
        params={"user_id": "12345"}
    )
    print(f"Status: {status}")
    print(f"Response: {json.dumps(response, indent=2)}")
