"""
Helper utilities for test automation
"""
import random
import string
from typing import Dict, Any


def generate_random_email(domain: str = "test.com") -> str:
    """Generate random email address"""
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{username}@{domain}"


def generate_random_string(length: int = 10) -> str:
    """Generate random string"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_name() -> str:
    """Generate random full name"""
    first_names = ["John", "Jane", "Alex", "Sarah", "Mike", "Emma", "David", "Lisa"]
    last_names = ["Smith", "Johnson", "Brown", "Davis", "Wilson", "Miller", "Taylor", "Anderson"]
    
    first = random.choice(first_names)
    last = random.choice(last_names)
    return f"{first} {last}"


def generate_test_user(role: str = "user") -> Dict[str, Any]:
    """Generate test user data"""
    return {
        "name": generate_random_name(),
        "email": generate_random_email(),
        "role": role,
        "status": "active",
        "department": random.choice(["IT", "Marketing", "Sales", "HR", "Finance"]),
        "phone": f"+1{random.randint(1000000000, 9999999999)}"
    }


def wait_for_condition(page, condition_func, timeout: int = 5000, interval: int = 100):
    """Wait for custom condition to be true"""
    import time
    start_time = time.time()
    
    while (time.time() - start_time) * 1000 < timeout:
        if condition_func():
            return True
        time.sleep(interval / 1000)
    
    return False


def scroll_to_element(page, locator: str):
    """Scroll element into view"""
    page.locator(locator).scroll_into_view_if_needed()


def highlight_element(page, locator: str):
    """Highlight element for debugging (adds red border)"""
    page.evaluate(f"""
        document.querySelector('{locator}').style.border = '2px solid red';
    """)


def get_element_attributes(page, locator: str) -> Dict[str, str]:
    """Get all attributes of an element"""
    return page.evaluate(f"""
        (() => {{
            const element = document.querySelector('{locator}');
            const attrs = {{}};
            for (let attr of element.attributes) {{
                attrs[attr.name] = attr.value;
            }}
            return attrs;
        }})()
    """)


def wait_for_network_idle(page, timeout: int = 5000):
    """Wait for network to be idle"""
    page.wait_for_load_state("networkidle", timeout=timeout)


def clear_local_storage(page):
    """Clear browser local storage"""
    page.evaluate("window.localStorage.clear();")


def clear_session_storage(page):
    """Clear browser session storage"""
    page.evaluate("window.sessionStorage.clear();")


def get_console_logs(page):
    """Get console logs from browser"""
    logs = []
    
    def handle_console(msg):
        logs.append({
            "type": msg.type,
            "text": msg.text,
            "location": msg.location
        })
    
    page.on("console", handle_console)
    return logs


def take_element_screenshot(page, locator: str, path: str):
    """Take screenshot of specific element"""
    page.locator(locator).screenshot(path=path)


def get_page_title(page) -> str:
    """Get current page title"""
    return page.title()


def get_current_url(page) -> str:
    """Get current page URL"""
    return page.url


def is_mobile_viewport(page) -> bool:
    """Check if current viewport is mobile size"""
    viewport = page.viewport_size
    return viewport["width"] <= 768


def set_mobile_viewport(page):
    """Set mobile viewport size"""
    page.set_viewport_size({"width": 375, "height": 667})


def set_tablet_viewport(page):
    """Set tablet viewport size"""
    page.set_viewport_size({"width": 768, "height": 1024})


def set_desktop_viewport(page):
    """Set desktop viewport size"""
    page.set_viewport_size({"width": 1920, "height": 1080})


class TestDataManager:
    """Manage test data lifecycle"""
    
    def __init__(self):
        self.created_users = []
        self.created_data = []
    
    def add_user(self, user_data: Dict[str, Any]):
        """Track created user for cleanup"""
        self.created_users.append(user_data)
    
    def add_data(self, data_type: str, data_id: str):
        """Track created data for cleanup"""
        self.created_data.append({"type": data_type, "id": data_id})
    
    def cleanup(self, page):
        """Cleanup all created test data"""
        # Implement cleanup logic based on your application
        # This is a placeholder - adapt to your needs
        for user in self.created_users:
            # Delete user via API or UI
            pass
        
        for data in self.created_data:
            # Delete data via API or UI
            pass
        
        # Clear tracking
        self.created_users.clear()
        self.created_data.clear()