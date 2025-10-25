#!/bin/bash

# 🚀 Hyperliquid Python Trading Bot Setup Script
# This script sets up the trading bot environment

set -e  # Exit on any error

echo "🚀 Setting up Hyperliquid Python Trading Bot..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.9+ is installed
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        print_success "Python $PYTHON_VERSION found"
        
        # Check if version is 3.9 or higher
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 9) else 1)'; then
            print_success "Python version is compatible (3.9+)"
        else
            print_error "Python 3.9+ is required. Current version: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    
    if [ -d ".venv" ]; then
        print_warning "Virtual environment already exists. Removing old one..."
        rm -rf .venv
    fi
    
    python3 -m venv .venv
    print_success "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source .venv/Scripts/activate
    else
        source .venv/bin/activate
    fi
    
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p src/logs
    mkdir -p src/backtesting/data
    mkdir -p src/config/profiles
    
    # Create .gitkeep files for empty directories
    touch src/backtesting/data/.gitkeep
    touch logs/.gitkeep
    touch src/logs/.gitkeep
    
    print_success "Directories created"
}

# Generate sample data
generate_sample_data() {
    print_status "Generating sample market data..."
    
    if [ -f "src/backtesting/data/generate_market_data.py" ]; then
        python3 src/backtesting/data/generate_market_data.py
        print_success "Sample data generated"
    else
        print_warning "Sample data generator not found, skipping..."
    fi
}

# Run health check
run_health_check() {
    print_status "Running system health check..."
    
    if [ -f "src/utils/health_check.py" ]; then
        python3 src/utils/health_check.py
        print_success "Health check completed"
    else
        print_warning "Health check not found, skipping..."
    fi
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    if [ -f "pytest.ini" ]; then
        python3 -m pytest tests/ -v --tb=short
        print_success "Tests completed"
    else
        print_warning "pytest configuration not found, skipping tests..."
    fi
}

# Create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    
    if [ ! -f ".env" ]; then
        cp config/env.example .env
        print_success "Environment file created from template"
        print_warning "Please edit .env file with your configuration"
    else
        print_warning ".env file already exists, skipping..."
    fi
}

# Main setup function
main() {
    echo "🚀 Hyperliquid Python Trading Bot Setup"
    echo "========================================"
    echo ""
    
    check_python
    create_venv
    activate_venv
    install_dependencies
    create_directories
    create_env_file
    generate_sample_data
    run_health_check
    run_tests
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Run your first backtest:"
    echo "   python3 tools/select_strategy.py"
    echo "3. Or run directly:"
    echo "   python3 src/cli/backtest.py --config src/config/production/rsi_scalping/standard_5m.json"
    echo ""
    echo "For more information, see:"
    echo "- README.md - Project overview"
    echo "- QUICK_START.md - Getting started guide"
    echo "- QUICK_COMMANDS.md - Command reference"
    echo ""
    echo "Happy trading! 🚀"
}

# Run main function
main "$@"
