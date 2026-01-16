"""
Main conftest.py file for pytest configuration and global fixtures
"""
import pytest
from playwright.sync_api import Page
from config.environment import get_config
from utils.data_loader import TestDataLoader

# Load shared fixtures (available to all tests)
pytest_plugins = [
    "fixtures.auth_fixtures",
]


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, environment_config, browser_name):
    """Configure browser launch arguments including slow_mo"""
    browser_config = environment_config.browser_config
    
    launch_args = {
        **browser_type_launch_args,
        "headless": browser_config.get("headless", False),
        "slow_mo": browser_config.get("slow_mo", 0)
    }
    
    extra_args = []
    if browser_name == "chromium":
        extra_args = list(browser_config.get("chromium_args", []))
    elif browser_name == "firefox":
        extra_args = browser_config.get("firefox_args", [])

    if browser_config.get("auto_maximize") and browser_name == "chromium":
        if "--start-maximized" not in extra_args:
            extra_args.append("--start-maximized")

    if extra_args:
        base_args = launch_args.get("args", [])
        launch_args["args"] = [*base_args, *extra_args]

    return launch_args


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, environment_config):
    """Configure browser context with master environment settings"""
    browser_config = environment_config.browser_config  # Single source from environment.json

    viewport = environment_config.viewport
    context_args = {
        **browser_context_args,
        "viewport": viewport,  # No duplicate - from master config
        "ignore_https_errors": browser_config.get("ignore_https_errors", True),
        "permissions": browser_config.get("permissions", []),
        "locale": browser_config.get("locale", "en-US"),
        "timezone_id": browser_config.get("timezone", "UTC")
    }
    
    # Video recording from master config
    if browser_config.get("video_recording"):
        context_args["record_video_dir"] = "reports/videos/"
        if viewport:
            context_args["record_video_size"] = viewport
        
    return context_args


@pytest.fixture(autouse=True)
def page_setup(request, environment_config):
    """Setup page with master config timeouts and settings (only for UI tests)"""
    if request.node.get_closest_marker("ui"):
        page = request.getfixturevalue("page")
        # Ensure viewport matches the actual screen size when auto maximize is enabled.
        if environment_config.browser_config.get("auto_maximize"):
            screen_size = page.evaluate("() => ({ width: screen.width, height: screen.height })")
            page.set_viewport_size(screen_size)
        page.set_default_timeout(environment_config.get_timeout("default"))
        page._base_url = environment_config.base_url
        yield page
        # Take screenshot on failure using master config settings
        try:
            if hasattr(page, '_failed') and page._failed:
                browser_config = environment_config.browser_config
                if browser_config.get("screenshot_on_failure", True):
                    page.screenshot(path=f"reports/screenshots/failed_{page._test_name}.png")
        except:
            pass
    else:
        yield


@pytest.fixture(autouse=True)
def test_setup(request):
    """Setup test metadata (only for UI tests)"""
    if request.node.get_closest_marker("ui"):
        page = request.getfixturevalue("page")
        page._test_name = request.node.name
        page._failed = False
        yield
        # Mark as failed if test failed
        if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
            page._failed = True
    else:
        yield


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture
def test_user_credentials(environment_config):
    """Common test user credentials from environment config"""
    return environment_config.test_users


@pytest.fixture
def api_base_url(environment_config):
    """API base URL from environment config"""
    return environment_config.api_url

@pytest.fixture
def test_data_loader():
    """Test data loader instance"""
    return TestDataLoader()


@pytest.fixture(scope="session")
def environment_config():
    """Environment configuration instance (single-language)"""
    return get_config()


# Pytest configuration
@pytest.fixture
def current_language(environment_config):
    """Get current test language"""
    return environment_config.language


@pytest.fixture
def ui_texts(environment_config):
    """Get UI text translations for current language"""
    return environment_config.ui_texts


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as regression test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API test"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as authentication-related"
    )
    config.addinivalue_line(
        "markers", "ui: mark test as UI test (enables Playwright page autouse setup)"
    )


# Test data cleanup fixtures
@pytest.fixture(scope="function", autouse=True)
def cleanup_test_data():
    """Cleanup test data after each test"""
    yield
    # Add cleanup logic here if needed
    # e.g., delete test users, reset database state, etc.
    pass


@pytest.fixture(scope="session")
def test_environment(environment_config):
    """Provide test environment configuration"""
    return {
        "base_url": environment_config.base_url,
        "api_url": environment_config.api_url,
        "timeout": environment_config.get_timeout("default"),
        "headless": environment_config.browser_config.get("headless", True),
        "browser": "chromium",
        "environment": environment_config.environment
    }
