# utils.py
import logging
import os
from src.application.hyperliquid_sdk.hyperliquid.info import Info

def setup_clients():
    """
    Initialise Hyperliquid Info client instance for simulation (market data only).
    This function works without credentials since it only fetches market data.

    Returns:
        Info instance for accessing market data
        
    Raises:
        Exception: If unable to initialize the Info client
    """
    try:
        logging.info("Initialising Hyperliquid Info client for simulated environment.")
        info = Info()
        
        # Test the connection by fetching a simple market data call
        try:
            # Try to get market data to verify connection
            mids = info.all_mids()
            if mids:
                logging.info("✅ Hyperliquid Info client initialized successfully")
                logging.info(f"Available markets: {len(mids)} markets")
            else:
                logging.warning("⚠️ Hyperliquid Info client initialized but no market data available")
        except Exception as e:
            logging.warning(f"⚠️ Hyperliquid Info client initialized but market data test failed: {e}")
            logging.info("This is normal for simulation mode - continuing...")
        
        return info
    except Exception as e:
        logging.error(f"❌ Failed to initialize Hyperliquid Info client: {e}")
        logging.error("This may be due to network connectivity or Hyperliquid API issues")
        raise Exception(f"Failed to initialize Hyperliquid Info client: {e}")