#!/bin/bash

# Hyperliquid Python Trading System Setup Script
# This script sets up the environment and installs all dependencies

echo "🚀 Setting up Hyperliquid Python Trading System..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install requirements
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Install Hyperliquid SDK
echo "🔌 Installing Hyperliquid SDK..."
cd src/application/hyperliquid_sdk
pip install -e .
cd ../../..

echo "✅ Setup complete!"
echo ""
echo "To start using the system:"
echo "1. Activate the virtual environment: source .venv/bin/activate"
echo "2. Navigate to src directory: cd src"
echo "3. Run your first backtest: python -m cli.backtest --config config/core/backtest_eth.json"
echo ""
echo "For more commands, see STRATEGY_COMMANDS.md"
