# utils.py
import os
import logging
from dotenv import load_dotenv
from eth_account import Account
from src.application.hyperliquid_sdk.hyperliquid.info import Info
from src.application.hyperliquid_sdk.hyperliquid.exchange import Exchange

load_dotenv()  # loads your .env

def setup_clients():
    """
    Load environment variables and initialise Hyperliquid client instances.

    Returns:
        tuple: (wallet address, Info instance, Exchange instance)

    Raises:
        ValueError: If any required environment variable is missing.
    """
    api_url     = os.getenv("HL_API_URL")
    private_key = os.getenv("HL_PRIVATE_KEY")
    address     = os.getenv("HL_ADDRESS")
    if not all([api_url, private_key, address]):
        missing = [v for v in ["HL_API_URL","HL_PRIVATE_KEY","HL_ADDRESS"] if not os.getenv(v)]
        logging.error(f"Missing environment variables: {', '.join(missing)}")
        raise ValueError(f"Missing: {', '.join(missing)}")

    acct = Account.from_key(private_key)
    info = Info(base_url=api_url)
    exchange = Exchange(wallet=acct, base_url=api_url, account_address=address)
    return address, info, exchange