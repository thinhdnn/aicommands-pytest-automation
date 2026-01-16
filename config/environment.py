"""
Environment configuration manager
"""
import os
import json
from typing import Dict, Any, Optional


class EnvironmentConfig:
    """Manage environment-specific configurations"""

    def __init__(self, environment: str = None):
        self.environment = environment or os.getenv("TEST_ENV", "dev")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration for current environment (single-language)."""
        config_file = f"data/environments/{self.environment}.json"

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file")

    @property
    def language(self) -> str:
        """Get current language"""
        return self.config.get("language", "en")

    @property
    def locale(self) -> str:
        """Get current locale"""
        return self.config.get("locale", "en-US")

    @property
    def ui_texts(self) -> Dict[str, str]:
        """Get UI text translations for current language"""
        return self.config.get("ui_texts", {})

    @property
    def base_url(self) -> str:
        """Get base URL for current environment"""
        return self.config.get("base_url", "http://localhost:3000")

    @property
    def api_url(self) -> str:
        """Get API URL for current environment"""
        api_config = self.config.get("api_config", {})
        return api_config.get("base_url", f"{self.base_url}/api")

    @property
    def timeouts(self) -> Dict[str, int]:
        """Get timeout configurations"""
        return self.config.get("timeouts", {
            "default": 10000,
            "page_load": 30000,
            "element_wait": 5000,
            "api_request": 15000
        })

    @property
    def browser_config(self) -> Dict[str, Any]:
        """Get complete browser configuration"""
        return self.config.get("browser_config", 
                              self.config.get("browser", {
                                  "headless": False,
                                  "viewport": {"width": 1920, "height": 1080},
                                  "video_recording": False,
                                  "screenshot_on_failure": True
                              }))

    @property 
    def viewport(self) -> Optional[Dict[str, int]]:
        """Get viewport settings (None means auto-size to window)"""
        browser_config = self.browser_config
        if browser_config.get("auto_maximize"):
            return None
        return browser_config.get("viewport", {"width": 1920, "height": 1080})

    @property
    def viewports(self) -> Dict[str, Dict[str, int]]:
        """Get all available viewport configurations"""
        return self.config.get("viewports", {
            "desktop": {"width": 1920, "height": 1080},
            "laptop": {"width": 1366, "height": 768},
            "tablet": {"width": 768, "height": 1024},
            "mobile": {"width": 375, "height": 667}
        })

    @property
    def execution_config(self) -> Dict[str, Any]:
        """Get execution configuration"""
        return self.config.get("execution_config", {})

    @property
    def data_config(self) -> Dict[str, Any]:
        """Get data management configuration"""
        return self.config.get("data_config", {})

    @property
    def data_dir(self) -> str:
        """Get data directory path"""
        return self.data_config.get("data_dir", "data")

    @property
    def test_users(self) -> Dict[str, Dict[str, str]]:
        """Get test user credentials"""
        return self.config.get("test_users", {})

    @property
    def features(self) -> Dict[str, bool]:
        """Get enabled features for current environment"""
        return self.config.get("features", {})

    @property
    def database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self.config.get("database", {})

    def get_user_credentials(self, user_type: str) -> Dict[str, str]:
        """Get credentials for specific user type"""
        users = self.test_users
        if user_type not in users:
            raise ValueError(f"User type '{user_type}' not found in configuration")
        return users[user_type]

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if feature is enabled in current environment"""
        return self.features.get(feature, False)

    def get_timeout(self, timeout_type: str) -> int:
        """Get specific timeout value"""
        timeouts = self.timeouts
        return timeouts.get(timeout_type, timeouts.get("default", 10000))

    def get_ui_text(self, key: str, default: str = None) -> str:
        """Get UI text for current language"""
        ui_texts = self.ui_texts
        return ui_texts.get(key, default or key)

    def is_production(self) -> bool:
        """Check if current environment is production"""
        return self.environment == "prod"

    def is_development(self) -> bool:
        """Check if current environment is development"""
        return self.environment == "dev"

    def get_external_service_url(self, service: str) -> str:
        """Get URL for external service"""
        services = self.config.get("external_services", {})
        return services.get(service, "")


# Global configuration instance
config = EnvironmentConfig()


# Utility functions
def get_config(environment: str = None) -> EnvironmentConfig:
    """Get configuration instance for specific environment"""
    return EnvironmentConfig(environment)


def get_base_url() -> str:
    """Get base URL for current environment"""
    return config.base_url


def get_api_url() -> str:
    """Get API URL for current environment"""
    return config.api_url


def get_user_credentials(user_type: str) -> Dict[str, str]:
    """Get user credentials for current environment"""
    return config.get_user_credentials(user_type)


def is_feature_enabled(feature: str) -> bool:
    """Check if feature is enabled"""
    return config.is_feature_enabled(feature)


def get_ui_text(key: str, default: str = None) -> str:
    """Get UI text for current language"""
    return config.get_ui_text(key, default)


def get_timeout(timeout_type: str) -> int:
    """Get timeout value"""
    return config.get_timeout(timeout_type)
