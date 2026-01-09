"""
Data loader utilities for test data management
Uses master environment configuration for consistency
"""
import json
import csv
import os
from typing import Dict, List, Any
from pathlib import Path
from config.environment import get_config


class DataLoader:
    """Load and manage test data from master environment configuration"""
    
    def __init__(self, data_dir: str = None):
        # Use master config for data directory
        self.config = get_config()
        self.data_dir = Path(data_dir or self.config.data_dir)
    
    def load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON test data file"""
        file_path = self.data_dir / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Test data file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file {file_path}: {e}")
    
    def load_csv(self, filename: str) -> List[Dict[str, str]]:
        """Load CSV test data file"""
        file_path = self.data_dir / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except FileNotFoundError:
            raise FileNotFoundError(f"Test data file not found: {file_path}")
    
    def get_test_users(self) -> List[Dict[str, str]]:
        """Get test users from CSV file"""
        return self.load_csv("users.csv")
    
    def get_user_by_role(self, role: str) -> Dict[str, str]:
        """Get first user with specific role"""
        users = self.get_test_users()
        for user in users:
            if user.get("role") == role:
                return user
        raise ValueError(f"No user found with role: {role}")
    
    def get_users_by_status(self, status: str) -> List[Dict[str, str]]:
        """Get all users with specific status"""
        users = self.get_test_users()
        return [user for user in users if user.get("status") == status]
    
    def get_test_data(self) -> Dict[str, Any]:
        """Get main test data from JSON file"""
        return self.load_json("test_data.json")
    
    def get_test_scenarios(self, scenario_type: str) -> Dict[str, Any]:
        """Get test scenarios of specific type"""
        test_data = self.get_test_data()
        scenarios = test_data.get("test_scenarios", {})
        if scenario_type not in scenarios:
            raise ValueError(f"Scenario type '{scenario_type}' not found")
        return scenarios[scenario_type]
    
    def get_valid_login_credentials(self) -> List[Dict[str, str]]:
        """Get valid login credentials for testing"""
        login_scenarios = self.get_test_scenarios("login")
        return login_scenarios.get("valid_credentials", [])
    
    def get_invalid_login_credentials(self) -> List[Dict[str, str]]:
        """Get invalid login credentials for testing"""
        login_scenarios = self.get_test_scenarios("login")
        return login_scenarios.get("invalid_credentials", [])
    
    def get_user_creation_data(self, data_type: str = "valid_data") -> List[Dict[str, Any]]:
        """Get user creation test data"""
        user_scenarios = self.get_test_scenarios("user_creation")
        return user_scenarios.get(data_type, [])
    
    def get_departments(self) -> List[str]:
        """Get list of available departments"""
        test_data = self.get_test_data()
        return test_data.get("departments", [])
    
    def get_roles(self) -> List[Dict[str, Any]]:
        """Get list of available roles with permissions"""
        test_data = self.get_test_data()
        return test_data.get("roles", [])
    
    def get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for specific role"""
        roles = self.get_roles()
        for role_data in roles:
            if role_data.get("name") == role:
                return role_data.get("permissions", [])
        return []


class EnvironmentDataLoader:
    """
    DEPRECATED: Load environment-specific data
    
    Use EnvironmentConfig directly instead of this class.
    This class is kept for backward compatibility only.
    """
    
    def __init__(self, environment: str = "dev", data_dir: str = None):
        import warnings
        warnings.warn(
            "EnvironmentDataLoader is deprecated. Use EnvironmentConfig directly.",
            DeprecationWarning,
            stacklevel=2
        )
        self.config = get_config(environment)
    
    def load_environment_config(self) -> Dict[str, Any]:
        """Load environment configuration - DEPRECATED"""
        return self.config.config
    
    def get_test_users_for_environment(self) -> Dict[str, Dict[str, str]]:
        """Get test users for current environment - DEPRECATED"""
        return self.config.test_users
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags for current environment - DEPRECATED"""
        return self.config.features


# Alias for backward compatibility
class TestDataLoader(DataLoader):
    """Alias for DataLoader for backward compatibility"""
    pass



# Global data loader instances
data_loader = DataLoader()
from config.environment import get_config
env_data_loader = get_config()


# Utility functions for easy access (updated to use master config)
def get_test_user_by_role(role: str) -> Dict[str, str]:
    """Get test user by role from master environment config"""
    config = get_config()
    users = config.test_users
    for user_key, user_data in users.items():
        # Check if role matches user_key or user_data role
        if user_key == role or user_data.get("role") == role:
            return user_data
    raise ValueError(f"No user found with role: {role}")


def get_valid_login_data() -> List[Dict[str, str]]:
    """Get valid login credentials from master config"""
    return data_loader.get_valid_login_credentials()


def get_invalid_login_data() -> List[Dict[str, str]]:
    """Get invalid login credentials"""
    return data_loader.get_invalid_login_credentials()


def get_user_creation_data(data_type: str = "valid_data") -> List[Dict[str, Any]]:
    """Get user creation test data"""
    return data_loader.get_user_creation_data(data_type)


def get_departments() -> List[str]:
    """Get available departments"""
    return data_loader.get_departments()


def get_role_permissions(role: str) -> List[str]:
    """Get permissions for role"""
    return data_loader.get_role_permissions(role)