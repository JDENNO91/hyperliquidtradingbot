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
    
    # Check for missing credentials
    if not all([api_url, private_key, address]):
        missing = [v for v in ["HL_API_URL","HL_PRIVATE_KEY","HL_ADDRESS"] if not os.getenv(v)]
        logging.error(f"❌ Missing environment variables: {', '.join(missing)}")
        logging.error("🔧 To fix this, create a .env file with your Hyperliquid credentials:")
        logging.error("   HL_API_URL=https://api.hyperliquid.xyz")
        logging.error("   HL_PRIVATE_KEY=your_private_key_here")
        logging.error("   HL_ADDRESS=your_wallet_address_here")
        logging.error("")
        logging.error("⚠️  Live trading requires valid Hyperliquid credentials!")
        logging.error("💡 For testing without credentials, use live simulation instead:")
        logging.error("   python -m src.cli.simulate --profile live_eth")
        raise ValueError(f"Missing required credentials: {', '.join(missing)}")

    try:
        acct = Account.from_key(private_key)
        info = Info(base_url=api_url)
        exchange = Exchange(wallet=acct, base_url=api_url, account_address=address)
        
        # Test the connection
        try:
            account_info = info.user_state(address)
            account_value = float(account_info["marginSummary"]["accountValue"])
            logging.info(f"✅ Hyperliquid connection successful")
            logging.info(f"Account value: ${account_value:.2f}")
        except Exception as e:
            logging.warning(f"⚠️ Hyperliquid connection established but account test failed: {e}")
            logging.info("This may be due to network issues or account permissions")
        
        return address, info, exchange
    except Exception as e:
        logging.error(f"❌ Failed to initialize Hyperliquid clients: {e}")
        logging.error("Please check your credentials and network connection")
        raise Exception(f"Failed to initialize Hyperliquid clients: {e}")