"""Fluent Test Helpers.

Provides a fluent API for writing tests in a natural, readable manner.
"""

from typing import Any, Dict
from playwright.sync_api import Page, Locator, expect
import time


class FluentAssertion:
    """Fluent assertion helper for more readable test assertions"""
    
    def __init__(self, locator: Locator, description: str = ""):
        self.locator = locator
        self.description = description
    
    def should_be_visible(self, timeout: int = 10000) -> 'FluentAssertion':
        """Assert that element should be visible"""
        expect(self.locator).to_be_visible(timeout=timeout)
        return self
    
    def should_be_hidden(self, timeout: int = 10000) -> 'FluentAssertion':
        """Assert that element should be hidden"""
        expect(self.locator).to_be_hidden(timeout=timeout)
        return self
    
    def should_contain_text(self, text: str, timeout: int = 10000) -> 'FluentAssertion':
        """Assert that element should contain specific text"""
        expect(self.locator).to_contain_text(text, timeout=timeout)
        return self
    
    def should_have_value(self, value: str, timeout: int = 10000) -> 'FluentAssertion':
        """Assert that input should have specific value"""
        expect(self.locator).to_have_value(value, timeout=timeout)
        return self
    
    def should_be_enabled(self, timeout: int = 10000) -> 'FluentAssertion':
        """Assert that element should be enabled"""
        expect(self.locator).to_be_enabled(timeout=timeout)
        return self
    
    def should_be_disabled(self, timeout: int = 10000) -> 'FluentAssertion':
        """Assert that element should be disabled"""
        expect(self.locator).to_be_disabled(timeout=timeout)
        return self


class FluentAction:
    """Fluent action helper for chaining actions"""
    
    def __init__(self, page: Page):
        self.page = page
        self.steps = []
    
    def navigate_to(self, url: str) -> 'FluentAction':
        """Navigate to specified URL"""
        self.page.goto(url)
        self.steps.append(f"Navigated to {url}")
        return self
    
    def fill_field(self, selector: str, value: str, description: str = "") -> 'FluentAction':
        """Fill input field with value"""
        self.page.fill(selector, value)
        step_desc = description or f"Filled field {selector} with '{value}'"
        self.steps.append(step_desc)
        return self
    
    def click_element(self, selector: str, description: str = "") -> 'FluentAction':
        """Click on element"""
        self.page.click(selector)
        step_desc = description or f"Clicked element {selector}"
        self.steps.append(step_desc)
        return self
    
    def wait_for_element(self, selector: str, timeout: int = 10000, description: str = "") -> 'FluentAction':
        """Wait for element to be visible"""
        self.page.wait_for_selector(selector, timeout=timeout)
        step_desc = description or f"Waited for element {selector}"
        self.steps.append(step_desc)
        return self
    
    def wait_for_loading(self, timeout: int = 30000) -> 'FluentAction':
        """Wait for page loading to complete"""
        self.page.wait_for_load_state("networkidle", timeout=timeout)
        self.steps.append("Waited for page loading to complete")
        return self
    
    def clear_field(self, selector: str, description: str = "") -> 'FluentAction':
        """Clear input field"""
        self.page.fill(selector, "")
        step_desc = description or f"Cleared field {selector}"
        self.steps.append(step_desc)
        return self
    
    def hover_element(self, selector: str, description: str = "") -> 'FluentAction':
        """Hover over element"""
        self.page.hover(selector)
        step_desc = description or f"Hovered over {selector}"
        self.steps.append(step_desc)
        return self
    
    def select_option(self, selector: str, value: str, description: str = "") -> 'FluentAction':
        """Select option from dropdown"""
        self.page.select_option(selector, value)
        step_desc = description or f"Selected '{value}' from {selector}"
        self.steps.append(step_desc)
        return self
    
    def pause(self, duration: float = 1.0, description: str = "") -> 'FluentAction':
        """Pause execution for specified duration"""
        time.sleep(duration)
        step_desc = description or f"Paused for {duration} seconds"
        self.steps.append(step_desc)
        return self
    
    def get_steps(self) -> list:
        """Get list of executed steps"""
        return self.steps.copy()


class FluentValidator:
    """Fluent validator for test assertions"""
    
    def __init__(self, page: Page):
        self.page = page
        self.validations = []
    
    def element(self, selector: str, description: str = "") -> FluentAssertion:
        """Get fluent assertion for element"""
        locator = self.page.locator(selector)
        return FluentAssertion(locator, description)
    
    def url_should_contain(self, text: str) -> 'FluentValidator':
        """Validate URL contains specific text"""
        current_url = self.page.url
        assert text in current_url, f"Expected URL to contain '{text}', but got '{current_url}'"
        self.validations.append(f"URL contains '{text}'")
        return self
    
    def url_should_be(self, expected_url: str) -> 'FluentValidator':
        """Validate URL matches expected value"""
        current_url = self.page.url
        assert current_url == expected_url, f"Expected URL to be '{expected_url}', but got '{current_url}'"
        self.validations.append(f"URL is '{expected_url}'")
        return self
    
    def page_title_should_be(self, title: str) -> 'FluentValidator':
        """Validate page title"""
        current_title = self.page.title()
        assert current_title == title, f"Expected title to be '{title}', but got '{current_title}'"
        self.validations.append(f"Page title is '{title}'")
        return self
    
    def get_validations(self) -> list:
        """Get list of performed validations"""
        return self.validations.copy()


class FluentTest:
    """Main fluent test class for chaining test operations"""
    
    def __init__(self, page: Page, test_name: str = ""):
        self.page = page
        self.test_name = test_name
        self.action = FluentAction(page)
        self.validator = FluentValidator(page)
        self.context = {}
        
    def given(self) -> FluentAction:
        """Start given context setup"""
        return self.action
    
    def when(self) -> FluentAction:
        """Start when action execution"""
        return self.action
    
    def then(self) -> FluentValidator:
        """Start then verification"""
        return self.validator
    
    def and_also(self) -> FluentAction:
        """Continue with additional actions"""
        return self.action
    
    def also_verify(self) -> FluentValidator:
        """Continue with additional verifications"""
        return self.validator
    
    def store_value(self, key: str, value: Any) -> 'FluentTest':
        """Store value in test context"""
        self.context[key] = value
        return self
    
    def get_value(self, key: str) -> Any:
        """Get value from test context"""
        return self.context.get(key)
    
    def with_user_credentials(self, email: str, password: str) -> dict:
        """Create user credentials object"""
        return {"email": email, "password": password}
    
    def with_test_data(self, **kwargs) -> dict:
        """Create test data object"""
        return kwargs
    
    def log(self, message: str) -> 'FluentTest':
        """Log custom message"""
        print(f"📝 {message}")
        return self
    
    def get_summary(self) -> dict:
        """Get test execution summary"""
        return {
            "test_name": self.test_name,
            "actions_performed": self.action.get_steps(),
            "validations_performed": self.validator.get_validations(),
            "context_data": self.context
        }


def fluent_test(page: Page, test_name: str = "") -> FluentTest:
    """Factory function to create fluent test instance"""
    return FluentTest(page, test_name)


# Helper functions for backward compatibility and ease of use
def assert_element_visible(page: Page, selector: str, timeout: int = 10000):
    """Helper function for simple element visibility assertion"""
    expect(page.locator(selector)).to_be_visible(timeout=timeout)


def assert_element_contains_text(page: Page, selector: str, text: str, timeout: int = 10000):
    """Helper function for text assertion"""
    expect(page.locator(selector)).to_contain_text(text, timeout=timeout)


def assert_url_contains(page: Page, text: str):
    """Helper function for URL assertion"""
    current_url = page.url
    assert text in current_url, f"Expected URL to contain '{text}', but got '{current_url}'"


class FluentFormHelper:
    """Pure utility functions for form operations (no state management)"""
    
    @staticmethod
    def fill_multiple_fields(page, field_data: dict):
        """Fill multiple form fields (pure utility function)"""
        for selector, value in field_data.items():
            page.fill(selector, value)
    
    @staticmethod
    def submit_form(page, submit_button_selector: str):
        """Submit form (pure utility function)"""
        page.click(submit_button_selector)
    
    @staticmethod
    def clear_form_fields(page, field_selectors: list):
        """Clear multiple form fields (pure utility function)"""
        for selector in field_selectors:
            page.fill(selector, "")
    
    @staticmethod
    def verify_form_validation_error(page, error_selector: str, expected_message: str = ""):
        """Verify form validation error (pure utility function)"""
        page.wait_for_selector(error_selector, timeout=5000)
        if expected_message:
            from playwright.sync_api import expect
            expect(page.locator(error_selector)).to_contain_text(expected_message)
    
    @staticmethod
    def clear_multiple_fields(page: Page, selectors: list) -> None:
        """Pure helper function to clear multiple form fields"""
        for selector in selectors:
            page.fill(selector, "")
    
    @staticmethod
    def validate_form_errors(page: Page, error_selectors: Dict[str, str]) -> Dict[str, str]:
        """Pure helper function to check form validation errors"""
        errors = {}
        for field_name, error_selector in error_selectors.items():
            try:
                error_element = page.locator(error_selector)
                if error_element.is_visible():
                    errors[field_name] = error_element.text_content()
            except:
                pass
        return errors