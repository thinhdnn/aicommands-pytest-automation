"""
Simplified Data Configuration Manager
"""
import os
from typing import Dict, Any, Optional
from config.environment import get_config

class DataConfigManager:
    def __init__(self, environment: str = "dev", project_root: Optional[str] = None):
        self.environment = environment
        self.config = get_config(environment)

    def get_config(self, custom_data_dir: Optional[str] = None) -> Dict[str, Any]:
        data_config = self.config.data_config
        return {
            "data_dir": data_config.get("data_dir", "data"),
            "environment": self.environment
        }

    def get_data_dir(self) -> str:
        return self.config.data_dir

    def get_file_path(self, file_type: str) -> str:
        data_dir = self.get_data_dir()
        file_mappings = {
            "users": f"{data_dir}/users.csv",
            "test_data": f"{data_dir}/test_data.json",
            "fixtures": f"{data_dir}/fixtures.json"
        }
        return file_mappings.get(file_type, f"{data_dir}/{file_type}.json")

def get_test_data_config(environment: str = None, custom_data_dir: str = None) -> Dict[str, Any]:
    env = environment or os.getenv("TEST_ENV", "dev")
    manager = DataConfigManager(env)
    return manager.get_config(custom_data_dir)
