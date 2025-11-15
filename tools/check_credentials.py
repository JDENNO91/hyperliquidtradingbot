#!/usr/bin/env python3
"""
Hyperliquid Credentials Checker

This script checks if your Hyperliquid credentials are properly configured
and provides guidance on how to set them up.
"""

import os
import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

def setup_logging():
    """Set up logging for credential checking."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def check_env_file():
    """Check if .env file exists and is properly configured."""
    logger = logging.getLogger(__name__)
    
    env_files = [
        ".env",
        "src/application/.env",
        "config/.env"
    ]
    
    found_env = None
    for env_file in env_files:
        if os.path.exists(env_file):
            found_env = env_file
            break
    
    if not found_env:
        logger.warning("❌ No .env file found")
        logger.info("🔧 Create a .env file with your Hyperliquid credentials:")
        logger.info("   HL_API_URL=https://api.hyperliquid.xyz")
        logger.info("   HL_PRIVATE_KEY=your_private_key_here")
        logger.info("   HL_ADDRESS=your_wallet_address_here")
        return False
    
    logger.info(f"✅ Found .env file: {found_env}")
    return True

def check_environment_variables():
    """Check if required environment variables are set."""
    logger = logging.getLogger(__name__)
    
    required_vars = ["HL_API_URL", "HL_PRIVATE_KEY", "HL_ADDRESS"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Mask sensitive values
            if "PRIVATE_KEY" in var:
                masked_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                masked_value = value
            logger.info(f"✅ {var}: {masked_value}")
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def test_hyperliquid_connection():
    """Test connection to Hyperliquid API."""
    logger = logging.getLogger(__name__)
    
    try:
        from src.application.hyperliquid_sdk.hyperliquid.info import Info
        
        logger.info("🔌 Testing Hyperliquid API connection...")
        info = Info()
        
        # Test basic market data access
        mids = info.all_mids()
        if mids:
            logger.info(f"✅ Hyperliquid API connection successful")
            logger.info(f"📊 Available markets: {len(mids)}")
            logger.info("💡 Market data access works - simulation mode available")
            return True
        else:
            logger.warning("⚠️ Hyperliquid API connected but no market data available")
            return False
            
    except Exception as e:
        logger.error(f"❌ Hyperliquid API connection failed: {e}")
        logger.error("This may be due to network connectivity issues")
        return False

def test_hyperliquid_trading():
    """Test Hyperliquid trading credentials."""
    logger = logging.getLogger(__name__)
    
    try:
        from src.live.utils import setup_clients
        
        logger.info("🔐 Testing Hyperliquid trading credentials...")
        address, info, exchange = setup_clients()
        
        logger.info(f"✅ Trading credentials valid")
        logger.info(f"🏦 Account: {address}")
        logger.info("💡 Live trading mode available")
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ Trading credentials test failed: {e}")
        logger.info("💡 This is normal if you don't have trading credentials set up")
        logger.info("💡 You can still use live simulation mode without credentials")
        return False

def main():
    """Main credential checking function."""
    logger = setup_logging()
    
    logger.info("🔍 HYPERLIQUID CREDENTIALS CHECKER")
    logger.info("=" * 50)
    
    # Check .env file
    env_ok = check_env_file()
    
    # Check environment variables
    vars_ok = check_environment_variables()
    
    # Test API connection
    api_ok = test_hyperliquid_connection()
    
    # Test trading credentials
    trading_ok = test_hyperliquid_trading()
    
    logger.info("=" * 50)
    logger.info("📋 CREDENTIAL CHECK SUMMARY")
    logger.info("=" * 50)
    
    if api_ok:
        logger.info("✅ Market Data Access: AVAILABLE")
        logger.info("💡 You can run live simulation without trading credentials")
        logger.info("🚀 Run: python -m src.cli.simulate --profile live_eth")
    else:
        logger.error("❌ Market Data Access: FAILED")
        logger.error("🔧 Check your network connection and Hyperliquid API status")
    
    if trading_ok:
        logger.info("✅ Live Trading: AVAILABLE")
        logger.info("⚠️  WARNING: Live trading uses real money!")
        logger.info("🚀 Run: python -m src.cli.trade --profile live_eth --dry-run")
    else:
        logger.warning("⚠️ Live Trading: NOT AVAILABLE")
        logger.info("💡 Set up trading credentials in .env file to enable live trading")
    
    logger.info("=" * 50)
    
    if api_ok:
        logger.info("🎉 Your system is ready for live simulation!")
        return 0
    else:
        logger.error("❌ System not ready - check network connection")
        return 1

if __name__ == "__main__":
    sys.exit(main())
