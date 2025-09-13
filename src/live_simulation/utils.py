# utils.py
import logging
from src.application.hyperliquid_sdk.hyperliquid.info import Info

def setup_clients():
    """
    Initialise Hyperliquid Info client instance for simulation (market data only).

    Returns:
        Info instance for accessing market data
    """
    logging.info("Initialising Hyperliquid Info client for simulated environment.")
    info = Info()
    return info