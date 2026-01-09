"""
Base component class for all UI components
Provides common functionality for component interactions
"""

from playwright.sync_api import Page
from typing import Optional


class BaseComponent:
    """Base class for all UI components"""
    
    def __init__(self, page: Page, container_selector: Optional[str] = None):
        self.page = page
        self.container = container_selector
    
    def wait_for_selector_visible(self, selector: str, timeout: int = 30000):
        """Wait for selector to be visible"""
        self.page.wait_for_selector(selector, state="visible", timeout=timeout)
    
    def wait_for_selector_hidden(self, selector: str, timeout: int = 10000):
        """Wait for selector to be hidden"""
        self.page.wait_for_selector(selector, state="hidden", timeout=timeout)
    
    def wait_for_page_load(self, timeout: int = 30000):
        """Wait for page to load completely"""
        self.page.wait_for_load_state("networkidle", timeout=timeout)
    
    def wait_for_loading_to_finish(self, timeout: int = 30000):
        """Wait for page network to be idle (no loading indicator used)"""
        self.page.wait_for_load_state("networkidle", timeout=timeout)
    
    def is_visible(self, selector: str) -> bool:
        """Check if element is visible"""
        return self.page.is_visible(selector)
    
    def get_text(self, selector: str) -> str:
        """Get text content of element"""
        return self.page.locator(selector).text_content() or ""
    
    def click_if_visible(self, selector: str) -> bool:
        """Click element if it's visible, return success status"""
        if self.is_visible(selector):
            self.page.click(selector)
            return True
        return False
    
    def fill_if_visible(self, selector: str, value: str) -> bool:
        """Fill input if it's visible, return success status"""
        if self.is_visible(selector):
            self.page.fill(selector, value)
            return True
        return False
    
    def get_attribute(self, selector: str, attribute: str) -> str:
        """Get attribute value from element"""
        return self.page.locator(selector).get_attribute(attribute) or ""