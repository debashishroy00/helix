#!/usr/bin/env python3
"""
Configuration utilities for login automation
===========================================
"""

import os
import json
from typing import Dict, Any


def load_login_config(config_path: str = None) -> Dict[str, Any]:
    """Load login configuration from JSON file."""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "config", "login_config.json")
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")


def load_credentials_from_env(app_name: str) -> Dict[str, str]:
    """Load credentials from environment variables."""
    app_upper = app_name.upper()
    
    # Common credential mapping
    cred_map = {
        "salesforce": {
            "username": f"{app_upper}_USERNAME",
            "password": f"{app_upper}_PASSWORD",
            "login_url": f"{app_upper}_LOGIN_URL",
            "org_url": f"{app_upper}_ORG_URL",
            "security_token": f"{app_upper}_SECURITY_TOKEN"
        },
        "sap": {
            "username": f"{app_upper}_USERNAME", 
            "password": f"{app_upper}_PASSWORD",
            "login_url": f"{app_upper}_LOGIN_URL",
            "client": f"{app_upper}_CLIENT"
        },
        "oracle": {
            "username": f"{app_upper}_USERNAME",
            "password": f"{app_upper}_PASSWORD", 
            "login_url": f"{app_upper}_LOGIN_URL",
            "identity_domain": f"{app_upper}_IDENTITY_DOMAIN"
        },
        "workday": {
            "username": f"{app_upper}_USERNAME",
            "password": f"{app_upper}_PASSWORD",
            "login_url": f"{app_upper}_LOGIN_URL",
            "tenant_url": f"{app_upper}_TENANT_URL"
        }
    }
    
    if app_name.lower() not in cred_map:
        raise ValueError(f"Unknown app: {app_name}")
    
    credentials = {}
    for cred_key, env_key in cred_map[app_name.lower()].items():
        value = os.getenv(env_key)
        if value:
            credentials[cred_key] = value
    
    return credentials


def update_config_setting(config_path: str, section: str, key: str, value: Any) -> None:
    """Update a specific setting in the configuration file."""
    config = load_login_config(config_path)
    
    if section in config:
        config[section][key] = value
    else:
        config[section] = {key: value}
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def get_app_selectors(app_name: str, config_path: str = None) -> Dict[str, list]:
    """Get selector patterns for a specific app."""
    config = load_login_config(config_path)
    
    if app_name.lower() not in config.get("apps", {}):
        raise ValueError(f"App '{app_name}' not found in configuration")
    
    return config["apps"][app_name.lower()]["selectors"]