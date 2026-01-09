"""
Fluent API Helpers
Provides a fluent API for writing API tests in a natural, readable manner
"""
import requests
from typing import Dict, Any, Optional, Union
import json


class FluentAPIResponse:
    """Fluent wrapper for API response validation"""
    
    def __init__(self, response: requests.Response, test_name: str = ""):
        self.response = response
        self.test_name = test_name
        self.validations = []
    
    def should_have_status(self, expected_status: Union[int, list]) -> 'FluentAPIResponse':
        """Assert response should have specific status code(s)"""
        if isinstance(expected_status, list):
            assert self.response.status_code in expected_status, \
                f"Expected status {expected_status}, got {self.response.status_code}"
            self.validations.append(f"Status code is one of {expected_status}")
        else:
            assert self.response.status_code == expected_status, \
                f"Expected status {expected_status}, got {self.response.status_code}"
            self.validations.append(f"Status code is {expected_status}")
        return self
    
    def should_be_success(self) -> 'FluentAPIResponse':
        """Assert response should be successful (2xx)"""
        assert 200 <= self.response.status_code < 300, \
            f"Expected success status (2xx), got {self.response.status_code}"
        self.validations.append(f"Response is successful ({self.response.status_code})")
        return self
    
    def should_be_client_error(self) -> 'FluentAPIResponse':
        """Assert response should be client error (4xx)"""
        assert 400 <= self.response.status_code < 500, \
            f"Expected client error (4xx), got {self.response.status_code}"
        self.validations.append(f"Response is client error ({self.response.status_code})")
        return self
    
    def should_be_server_error(self) -> 'FluentAPIResponse':
        """Assert response should be server error (5xx)"""
        assert 500 <= self.response.status_code < 600, \
            f"Expected server error (5xx), got {self.response.status_code}"
        self.validations.append(f"Response is server error ({self.response.status_code})")
        return self
    
    def should_have_content(self) -> 'FluentAPIResponse':
        """Assert response should have content"""
        assert self.response.content, "Response should have content"
        self.validations.append("Response has content")
        return self
    
    def should_be_json(self) -> 'FluentAPIResponse':
        """Assert response should be valid JSON"""
        try:
            self.response.json()
            self.validations.append("Response is valid JSON")
        except json.JSONDecodeError:
            raise AssertionError("Response is not valid JSON")
        return self
    
    def should_contain_field(self, field_name: str) -> 'FluentAPIResponse':
        """Assert response JSON should contain specific field"""
        response_data = self.response.json()
        assert field_name in response_data, f"Response should contain field '{field_name}'"
        self.validations.append(f"Response contains field '{field_name}'")
        return self
    
    def should_have_field_value(self, field_name: str, expected_value: Any) -> 'FluentAPIResponse':
        """Assert response JSON field should have specific value"""
        response_data = self.response.json()
        assert field_name in response_data, f"Response should contain field '{field_name}'"
        actual_value = response_data[field_name]
        assert actual_value == expected_value, \
            f"Field '{field_name}' should be '{expected_value}', got '{actual_value}'"
        self.validations.append(f"Field '{field_name}' has value '{expected_value}'")
        return self
    
    def should_contain_text(self, text: str) -> 'FluentAPIResponse':
        """Assert response content should contain specific text"""
        content = self.response.text
        assert text in content, f"Response should contain text '{text}'"
        self.validations.append(f"Response contains text '{text}'")
        return self
    
    def should_have_header(self, header_name: str, expected_value: str = None) -> 'FluentAPIResponse':
        """Assert response should have specific header"""
        assert header_name in self.response.headers, f"Response should have header '{header_name}'"
        if expected_value:
            actual_value = self.response.headers[header_name]
            assert actual_value == expected_value, \
                f"Header '{header_name}' should be '{expected_value}', got '{actual_value}'"
            self.validations.append(f"Header '{header_name}' is '{expected_value}'")
        else:
            self.validations.append(f"Response has header '{header_name}'")
        return self
    
    def should_match_schema(self, schema: Dict[str, Any]) -> 'FluentAPIResponse':
        """Assert response JSON should match schema (basic validation)"""
        response_data = self.response.json()
        for field_name, field_type in schema.items():
            assert field_name in response_data, f"Response should contain field '{field_name}'"
            actual_value = response_data[field_name]
            assert isinstance(actual_value, field_type), \
                f"Field '{field_name}' should be of type {field_type.__name__}, got {type(actual_value).__name__}"
        self.validations.append("Response matches expected schema")
        return self
    
    def get_json(self) -> Dict[str, Any]:
        """Get response JSON data"""
        return self.response.json()
    
    def get_field_value(self, field_name: str) -> Any:
        """Get specific field value from response JSON"""
        response_data = self.response.json()
        return response_data.get(field_name)
    
    def get_validations(self) -> list:
        """Get list of performed validations"""
        return self.validations.copy()


class FluentAPIRequest:
    """Fluent wrapper for building and executing API requests"""
    
    def __init__(self, test_name: str = ""):
        self.test_name = test_name
        self.base_url = ""
        self.endpoint = ""
        self.method = "GET"
        self.headers = {}
        self.payload = None
        self.query_params = {}
        self.timeout = 30
        self.actions = []
    
    def to_endpoint(self, url: str) -> 'FluentAPIRequest':
        """Set the endpoint URL"""
        self.endpoint = url
        self.actions.append(f"Target endpoint: {url}")
        return self
    
    def with_method(self, method: str) -> 'FluentAPIRequest':
        """Set HTTP method"""
        self.method = method.upper()
        self.actions.append(f"Using method: {method}")
        return self
    
    def with_headers(self, headers: Dict[str, str]) -> 'FluentAPIRequest':
        """Set request headers"""
        self.headers.update(headers)
        self.actions.append(f"Added headers: {list(headers.keys())}")
        return self
    
    def with_header(self, key: str, value: str) -> 'FluentAPIRequest':
        """Add single header"""
        self.headers[key] = value
        self.actions.append(f"Added header: {key}")
        return self
    
    def with_auth_header(self, auth_value: str) -> 'FluentAPIRequest':
        """Add authorization header"""
        self.headers["Authorization"] = auth_value
        self.actions.append("Added authorization header")
        return self
    
    def with_content_type(self, content_type: str) -> 'FluentAPIRequest':
        """Add content-type header"""
        self.headers["Content-Type"] = content_type
        self.actions.append(f"Set content type: {content_type}")
        return self
    
    def with_json_payload(self, payload: Dict[str, Any]) -> 'FluentAPIRequest':
        """Set JSON payload"""
        self.payload = payload
        self.with_content_type("application/json")
        self.actions.append("Added JSON payload")
        return self
    
    def with_payload(self, payload: Any) -> 'FluentAPIRequest':
        """Set raw payload"""
        self.payload = payload
        self.actions.append("Added raw payload")
        return self
    
    def with_query_params(self, params: Dict[str, str]) -> 'FluentAPIRequest':
        """Set query parameters"""
        self.query_params.update(params)
        self.actions.append(f"Added query params: {list(params.keys())}")
        return self
    
    def with_timeout(self, timeout: int) -> 'FluentAPIRequest':
        """Set request timeout"""
        self.timeout = timeout
        self.actions.append(f"Set timeout: {timeout}s")
        return self
    
    def execute(self) -> FluentAPIResponse:
        """Execute the request and return fluent response"""
        kwargs = {
            'headers': self.headers,
            'timeout': self.timeout,
            'params': self.query_params
        }
        
        if self.method in ['POST', 'PUT', 'PATCH']:
            if isinstance(self.payload, dict) and 'Content-Type' in self.headers and 'json' in self.headers['Content-Type']:
                kwargs['json'] = self.payload
            else:
                kwargs['data'] = self.payload
        
        response = requests.request(self.method, self.endpoint, **kwargs)
        self.actions.append(f"Executed {self.method} request")
        
        return FluentAPIResponse(response, self.test_name)
    
    def get_actions(self) -> list:
        """Get list of actions performed"""
        return self.actions.copy()


class FluentAPITest:
    """Main fluent API test class for chaining API test operations"""
    
    def __init__(self, test_name: str = ""):
        self.test_name = test_name
        self.context = {}
        self.setup_actions = []
        self.test_actions = []
        
    def given(self) -> 'FluentAPITest':
        """Start given context setup"""
        return self
    
    def when(self) -> FluentAPIRequest:
        """Start when action - return request builder"""
        return FluentAPIRequest(self.test_name)
    
    def store_value(self, key: str, value: Any) -> 'FluentAPITest':
        """Store value in test context"""
        self.context[key] = value
        self.setup_actions.append(f"Stored {key} in context")
        return self
    
    def get_value(self, key: str) -> Any:
        """Get value from test context"""
        return self.context.get(key)
    
    def with_api_config(self, base_url: str, default_headers: Dict[str, str] = None) -> 'FluentAPITest':
        """Configure API defaults"""
        self.context['base_url'] = base_url
        if default_headers:
            self.context['default_headers'] = default_headers
        self.setup_actions.append(f"Configured API base URL: {base_url}")
        return self
    
    def with_credentials(self, auth_type: str, **credentials) -> 'FluentAPITest':
        """Store authentication credentials"""
        self.context[f'{auth_type}_credentials'] = credentials
        self.setup_actions.append(f"Configured {auth_type} credentials")
        return self
    
    def create_request(self) -> FluentAPIRequest:
        """Create new request with test context"""
        request = FluentAPIRequest(self.test_name)
        
        # Apply default headers if available
        if 'default_headers' in self.context:
            request.with_headers(self.context['default_headers'])
            
        return request
    
    def log(self, message: str) -> 'FluentAPITest':
        """Log custom message"""
        print(f"📝 {message}")
        return self
    
    def get_summary(self) -> dict:
        """Get test execution summary"""
        return {
            "test_name": self.test_name,
            "setup_actions": self.setup_actions,
            "context_data": self.context
        }


def fluent_api_test(test_name: str = "") -> FluentAPITest:
    """Factory function to create fluent API test instance"""
    return FluentAPITest(test_name)


# Helper functions for common API test patterns
def post_request(url: str, payload: Dict[str, Any], headers: Dict[str, str] = None) -> FluentAPIResponse:
    """Quick POST request helper"""
    request = FluentAPIRequest()
    request.to_endpoint(url).with_method("POST").with_json_payload(payload)
    if headers:
        request.with_headers(headers)
    return request.execute()


def get_request(url: str, headers: Dict[str, str] = None, params: Dict[str, str] = None) -> FluentAPIResponse:
    """Quick GET request helper"""
    request = FluentAPIRequest()
    request.to_endpoint(url).with_method("GET")
    if headers:
        request.with_headers(headers)
    if params:
        request.with_query_params(params)
    return request.execute()


def put_request(url: str, payload: Dict[str, Any], headers: Dict[str, str] = None) -> FluentAPIResponse:
    """Quick PUT request helper"""
    request = FluentAPIRequest()
    request.to_endpoint(url).with_method("PUT").with_json_payload(payload)
    if headers:
        request.with_headers(headers)
    return request.execute()


def delete_request(url: str, headers: Dict[str, str] = None) -> FluentAPIResponse:
    """Quick DELETE request helper"""
    request = FluentAPIRequest()
    request.to_endpoint(url).with_method("DELETE")
    if headers:
        request.with_headers(headers)
    return request.execute()