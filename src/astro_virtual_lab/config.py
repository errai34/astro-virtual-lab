"""Configuration management for astro_virtual_lab."""

import os
from pathlib import Path
import yaml

def load_config() -> dict:
    """Load configuration from config.yml file.
    
    Returns:
        dict: Configuration dictionary containing API keys and settings
    """
    config_path = Path(__file__).parent / "config.yml"
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found at {config_path}. "
            "Please copy config.yml.template to config.yml and fill in your API keys."
        )
    
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Allow environment variables to override config file
    env_mapping = {
        "OPENAI_API_KEY": ("api_keys", "openai"),
        "DEEPSEEK_API_KEY": ("api_keys", "deepseek"),
        "NASA_ADS_KEY": ("api_keys", "nasa_ads"),
    }
    
    for env_var, (section, key) in env_mapping.items():
        if env_value := os.environ.get(env_var):
            if section not in config:
                config[section] = {}
            config[section][key] = env_value
    
    return config
