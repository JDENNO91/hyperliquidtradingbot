#!/bin/bash
# Production Deployment Script for Hyperliquid Trading Bot

set -e  # Exit on any error

# Configuration
PROJECT_NAME="hyperliquid-trading-bot"
PYTHON_VERSION="3.8"
VENV_NAME="trading_bot_env"
LOG_DIR="logs"
CONFIG_DIR="src/config"
BACKUP_DIR="backups"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    PYTHON_VER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ $(echo "$PYTHON_VER < $PYTHON_VERSION" | bc -l) -eq 1 ]]; then
        log_error "Python $PYTHON_VERSION or higher is required. Found: $PYTHON_VER"
        exit 1
    fi
    
    log_success "Python version check passed: $PYTHON_VER"
    
    # Check for required system packages
    REQUIRED_PACKAGES=("git" "curl" "wget")
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if ! command -v $package &> /dev/null; then
            log_warning "$package is not installed. Please install it manually."
        fi
    done
}

# Create backup of existing installation
create_backup() {
    if [[ -d "$VENV_NAME" ]] || [[ -f "requirements.txt" ]]; then
        log_info "Creating backup of existing installation..."
        
        BACKUP_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        BACKUP_PATH="$BACKUP_DIR/backup_$BACKUP_TIMESTAMP"
        
        mkdir -p "$BACKUP_DIR"
        
        if [[ -d "$VENV_NAME" ]]; then
            cp -r "$VENV_NAME" "$BACKUP_PATH/"
            log_success "Virtual environment backed up to $BACKUP_PATH"
        fi
        
        if [[ -f "requirements.txt" ]]; then
            cp requirements.txt "$BACKUP_PATH/"
        fi
        
        log_success "Backup created at $BACKUP_PATH"
    fi
}

# Setup virtual environment
setup_venv() {
    log_info "Setting up Python virtual environment..."
    
    # Remove existing venv if it exists
    if [[ -d "$VENV_NAME" ]]; then
        log_info "Removing existing virtual environment..."
        rm -rf "$VENV_NAME"
    fi
    
    # Create new virtual environment
    python3 -m venv "$VENV_NAME"
    
    # Activate virtual environment
    source "$VENV_NAME/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    log_success "Virtual environment created and activated"
}

# Install dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Ensure we're in the virtual environment
    source "$VENV_NAME/bin/activate"
    
    # Install requirements
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        log_success "Dependencies installed from requirements.txt"
    else
        log_error "requirements.txt not found"
        exit 1
    fi
    
    # Install additional production dependencies
    pip install gunicorn supervisor
    
    log_success "All dependencies installed"
}

# Setup directories
setup_directories() {
    log_info "Setting up project directories..."
    
    # Create necessary directories
    mkdir -p "$LOG_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "data"
    mkdir -p "src/logs"
    
    # Set proper permissions
    chmod 755 "$LOG_DIR"
    chmod 755 "$CONFIG_DIR"
    chmod 755 "data"
    chmod 755 "src/logs"
    
    log_success "Project directories created"
}

# Validate configuration
validate_config() {
    log_info "Validating configuration files..."
    
    source "$VENV_NAME/bin/activate"
    
    # Run configuration validation
    if python3 src/config/validator.py --all; then
        log_success "All configuration files are valid"
    else
        log_error "Configuration validation failed"
        exit 1
    fi
}

# Setup systemd service (Linux only)
setup_systemd_service() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "Setting up systemd service..."
        
        SERVICE_FILE="/etc/systemd/system/$PROJECT_NAME.service"
        SERVICE_USER=$(whoami)
        PROJECT_PATH=$(pwd)
        
        sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Hyperliquid Trading Bot
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$PROJECT_PATH
Environment=PATH=$PROJECT_PATH/$VENV_NAME/bin
ExecStart=$PROJECT_PATH/$VENV_NAME/bin/python src/main.py trade --config live_eth --dry-run
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable "$PROJECT_NAME"
        
        log_success "Systemd service created and enabled"
        log_info "Use 'sudo systemctl start $PROJECT_NAME' to start the service"
    else
        log_info "Systemd service setup skipped (not on Linux)"
    fi
}

# Setup supervisor configuration
setup_supervisor() {
    log_info "Setting up Supervisor configuration..."
    
    source "$VENV_NAME/bin/activate"
    
    SUPERVISOR_CONFIG="supervisor_trading_bot.conf"
    PROJECT_PATH=$(pwd)
    
    cat > "$SUPERVISOR_CONFIG" <<EOF
[program:trading_bot]
command=$PROJECT_PATH/$VENV_NAME/bin/python src/main.py trade --config live_eth --dry-run
directory=$PROJECT_PATH
user=$(whoami)
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$PROJECT_PATH/$LOG_DIR/trading_bot.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=5
environment=PATH="$PROJECT_PATH/$VENV_NAME/bin"
EOF
    
    log_success "Supervisor configuration created: $SUPERVISOR_CONFIG"
    log_info "Add this file to your supervisor configuration directory"
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring and logging..."
    
    source "$VENV_NAME/bin/activate"
    
    # Test enhanced logging
    python3 src/utils/enhanced_logger.py --test
    
    # Test performance monitoring
    python3 src/utils/performance_monitor.py --status
    
    log_success "Monitoring systems tested and ready"
}

# Create startup scripts
create_startup_scripts() {
    log_info "Creating startup scripts..."
    
    # Create start script
    cat > start_bot.sh <<'EOF'
#!/bin/bash
# Start Hyperliquid Trading Bot

set -e

# Configuration
VENV_NAME="trading_bot_env"
LOG_DIR="logs"

# Activate virtual environment
source "$VENV_NAME/bin/activate"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Start the bot
echo "Starting Hyperliquid Trading Bot..."
python src/main.py trade --config live_eth --dry-run
EOF
    
    chmod +x start_bot.sh
    
    # Create stop script
    cat > stop_bot.sh <<'EOF'
#!/bin/bash
# Stop Hyperliquid Trading Bot

# Find and kill the bot process
BOT_PID=$(pgrep -f "src/main.py trade")
if [[ -n "$BOT_PID" ]]; then
    echo "Stopping trading bot (PID: $BOT_PID)..."
    kill "$BOT_PID"
    echo "Trading bot stopped"
else
    echo "Trading bot is not running"
fi
EOF
    
    chmod +x stop_bot.sh
    
    # Create status script
    cat > status_bot.sh <<'EOF'
#!/bin/bash
# Check status of Hyperliquid Trading Bot

BOT_PID=$(pgrep -f "src/main.py trade")
if [[ -n "$BOT_PID" ]]; then
    echo "Trading bot is running (PID: $BOT_PID)"
    ps -p "$BOT_PID" -o pid,ppid,cmd,etime
else
    echo "Trading bot is not running"
fi
EOF
    
    chmod +x status_bot.sh
    
    log_success "Startup scripts created: start_bot.sh, stop_bot.sh, status_bot.sh"
}

# Run health check
run_health_check() {
    log_info "Running health check..."
    
    source "$VENV_NAME/bin/activate"
    
    # Test imports
    python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from cli import backtest_cli, optimize_cli, simulate_cli, trade_cli
    from config.config_manager import ConfigManager
    from utils.enhanced_logger import get_enhanced_logger
    from utils.performance_monitor import get_performance_monitor
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"
    
    # Test configuration loading
    python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from config.config_manager import ConfigManager
    config_manager = ConfigManager()
    config = config_manager.load_config('live_eth')
    print('✅ Configuration loading successful')
except Exception as e:
    print(f'❌ Configuration loading failed: {e}')
    sys.exit(1)
"
    
    log_success "Health check passed"
}

# Main deployment function
main() {
    log_info "Starting deployment of $PROJECT_NAME..."
    
    check_root
    check_requirements
    create_backup
    setup_venv
    install_dependencies
    setup_directories
    validate_config
    setup_systemd_service
    setup_supervisor
    setup_monitoring
    create_startup_scripts
    run_health_check
    
    log_success "Deployment completed successfully!"
    
    echo ""
    echo "🎉 Hyperliquid Trading Bot is ready for production!"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Review and customize configuration files in $CONFIG_DIR"
    echo "  2. Test the bot with: ./start_bot.sh"
    echo "  3. Monitor logs in: $LOG_DIR"
    echo "  4. Check status with: ./status_bot.sh"
    echo ""
    echo "🔧 Management commands:"
    echo "  Start bot:     ./start_bot.sh"
    echo "  Stop bot:      ./stop_bot.sh"
    echo "  Check status:  ./status_bot.sh"
    echo ""
    echo "📊 Monitoring:"
    echo "  Performance:   python $VENV_NAME/bin/python src/utils/performance_monitor.py --status"
    echo "  Logs:          tail -f $LOG_DIR/*.log"
    echo ""
    echo "⚠️  Remember to:"
    echo "  - Test thoroughly in dry-run mode before live trading"
    echo "  - Monitor performance and logs regularly"
    echo "  - Keep backups of your configuration and data"
    echo "  - Update dependencies regularly"
}

# Run main function
main "$@"
