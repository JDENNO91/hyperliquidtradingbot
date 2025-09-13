"""
Utility functions for Hyperliquid trading bot application.

This module provides essential utilities for:
- Environment configuration and validation
- Hyperliquid client setup and management
- Basic logging and error handling
"""

import os
import logging
from typing import Tuple
from pathlib import Path
from dotenv import load_dotenv
from src.application.hyperliquid_sdk.hyperliquid.info import Info
from src.application.hyperliquid_sdk.hyperliquid.exchange import Exchange

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Environment variable names
ENV_VARS = {
    "API_URL": "HL_API_URL",
    "PRIVATE_KEY": "HL_PRIVATE_KEY", 
    "ADDRESS": "HL_ADDRESS",
    "LOG_LEVEL": "HL_LOG_LEVEL"
}

# Default values
DEFAULTS = {
    "LOG_LEVEL": "INFO"
}

class HyperliquidConfigError(Exception):
    """Custom exception for configuration errors."""
    pass

def validate_environment() -> dict:
    """
    Validate and load all required environment variables.
    
    Returns:
        dict: Dictionary of validated environment variables
        
    Raises:
        HyperliquidConfigError: If required variables are missing
    """
    config = {}
    missing_vars = []
    
    # Check required variables
    for key, env_var in ENV_VARS.items():
        if key == "LOG_LEVEL":
            # Optional variable with default
            value = os.getenv(env_var, DEFAULTS[key])
        else:
            # Required variables
            value = os.getenv(env_var)
            if not value:
                missing_vars.append(env_var)
        
        config[key] = value
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise HyperliquidConfigError(error_msg)
    
    # Basic validation for address format
    if not config["ADDRESS"].startswith("0x") or len(config["ADDRESS"]) != 42:
        error_msg = f"Invalid address format: {config['ADDRESS']}"
        logger.error(error_msg)
        raise HyperliquidConfigError(error_msg)
    
    logger.info("Environment validation successful")
    return config

def setup_logging(log_level: str = None) -> None:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    if log_level is None:
        log_level = os.getenv(ENV_VARS["LOG_LEVEL"], DEFAULTS["LOG_LEVEL"])
    
    # Convert string to logging level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    numeric_level = level_map.get(log_level.upper(), logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/app.log')
        ]
    )
    
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    logger.info(f"Logging configured at level: {log_level}")

def setup_clients() -> Tuple[str, Info, Exchange]:
    """
    Initialize Hyperliquid client instances with validated configuration.
    
    Returns:
        Tuple[str, Info, Exchange]: (address, info_client, exchange_client)
        
    Raises:
        HyperliquidConfigError: If configuration is invalid
    """
    try:
        # Validate environment
        config = validate_environment()
        
        # Setup logging
        setup_logging(config["LOG_LEVEL"])
        
        logger.info("Initializing Hyperliquid clients...")
        
        # Initialize Info client
        info_client = Info(base_url=config["API_URL"])
        logger.debug("Info client initialized")
        
        # Initialize Exchange client - Hyperliquid handles the wallet internally
        exchange_client = Exchange(
            private_key=config["PRIVATE_KEY"],
            base_url=config["API_URL"],
            account_address=config["ADDRESS"]
        )
        logger.debug("Exchange client initialized")
        
        logger.info("All clients initialized successfully")
        
        return config["ADDRESS"], info_client, exchange_client
        
    except HyperliquidConfigError as e:
        logger.error(f"Configuration error: {e}")
        raise
    except Exception as e:
        error_msg = f"Failed to initialize clients: {e}"
        logger.error(error_msg)
        raise HyperliquidConfigError(error_msg)

# Convenience function for backward compatibility
def get_hyperliquid_clients() -> Tuple[str, Info, Exchange]:
    """
    Alias for setup_clients() for backward compatibility.
    
    Returns:
        Tuple[str, Info, Exchange]: (address, info_client, exchange_client)
    """
    return setup_clients()

if __name__ == "__main__":
    # Test the utilities
    try:
        print("Testing Hyperliquid utilities...")
        
        # Test environment validation (will fail without .env file)
        print("Environment validation...")
        try:
            config = validate_environment()
            print(f"✅ Config loaded: {list(config.keys())}")
        except HyperliquidConfigError as e:
            print(f"⚠️  Config validation failed (expected): {e}")
        
        print("🎉 Utility tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")