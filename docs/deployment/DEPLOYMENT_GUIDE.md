# 🚀 Production Deployment Guide

This guide provides comprehensive instructions for deploying the Hyperliquid Trading Bot in production environments.

## 📋 **Prerequisites**

### **System Requirements**
- **OS**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows with WSL2
- **Python**: 3.8 or higher
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Storage**: Minimum 10GB free space
- **Network**: Stable internet connection for API access

### **Required Software**
- Python 3.8+
- Git
- curl/wget
- Docker (optional, for containerized deployment)

## 🎯 **Deployment Options**

### **Option 1: Direct Deployment (Recommended)**

#### **Step 1: Clone and Setup**
```bash
# Clone the repository
git clone <your-repo-url>
cd hyperliquidpython

# Run the deployment script
chmod +x deploy.sh
./deploy.sh
```

#### **Step 2: Configure Trading Parameters**
```bash
# Edit configuration files
nano src/config/live_eth.json
nano src/config/backtest_eth.json
```

#### **Step 3: Test Configuration**
```bash
# Validate all configurations
python3 src/config/validator.py --all

# Test the bot in dry-run mode
./start_bot.sh
```

#### **Step 4: Start Production Trading**
```bash
# Start live trading (remove --dry-run when ready)
python3 src/main.py trade --config live_eth
```

### **Option 2: Docker Deployment**

#### **Step 1: Build and Run**
```bash
# Build the Docker image
docker build -t hyperliquid-trading-bot .

# Run with docker-compose
docker-compose up -d

# Or run individual container
docker run -d \
  --name trading-bot \
  -v $(pwd)/src/config:/app/src/config:ro \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  hyperliquid-trading-bot
```

#### **Step 2: Monitor Container**
```bash
# Check container status
docker ps

# View logs
docker logs -f trading-bot

# Access container shell
docker exec -it trading-bot bash
```

### **Option 3: Cloud Deployment**

#### **AWS EC2 Deployment**
```bash
# Launch EC2 instance (t3.medium or larger)
# Install Docker
sudo apt update
sudo apt install docker.io docker-compose

# Clone and deploy
git clone <your-repo-url>
cd hyperliquidpython
docker-compose up -d
```

#### **Google Cloud Platform**
```bash
# Create Compute Engine instance
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Deploy application
git clone <your-repo-url>
cd hyperliquidpython
docker-compose up -d
```

## ⚙️ **Configuration Management**

### **Environment-Specific Configs**

#### **Development**
```bash
# Use test configurations
python3 src/main.py backtest --config backtest_eth
```

#### **Staging**
```bash
# Use simulation mode
python3 src/main.py simulate --config live_eth
```

#### **Production**
```bash
# Use live trading (after thorough testing)
python3 src/main.py trade --config live_eth
```

### **Configuration Validation**
```bash
# Validate all configurations
python3 src/config/validator.py --all

# Validate specific config
python3 src/config/validator.py src/config/live_eth.json
```

## 📊 **Monitoring and Logging**

### **Real-time Monitoring**
```bash
# Start performance monitoring
python3 src/utils/performance_monitor.py --start

# Check current status
python3 src/utils/performance_monitor.py --status

# Export metrics
python3 src/utils/performance_monitor.py --export metrics.json --hours 24
```

### **Log Management**
```bash
# View real-time logs
tail -f logs/*.log

# View structured logs
tail -f logs/trading_bot.log | jq .

# Clean old logs
python3 src/utils/enhanced_logger.py --cleanup --days 7
```

### **Dashboard Access**
```bash
# Start dashboard
streamlit run src/application/dashboard.py

# Access at http://localhost:8501
```

## 🔧 **Service Management**

### **Systemd Service (Linux)**
```bash
# Start service
sudo systemctl start hyperliquid-trading-bot

# Stop service
sudo systemctl stop hyperliquid-trading-bot

# Check status
sudo systemctl status hyperliquid-trading-bot

# Enable auto-start
sudo systemctl enable hyperliquid-trading-bot
```

### **Supervisor (Alternative)**
```bash
# Install supervisor
sudo apt install supervisor

# Copy configuration
sudo cp supervisor_trading_bot.conf /etc/supervisor/conf.d/

# Reload and start
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start trading_bot
```

### **Manual Management**
```bash
# Start bot
./start_bot.sh

# Stop bot
./stop_bot.sh

# Check status
./status_bot.sh
```

## 🛡️ **Security Best Practices**

### **API Key Management**
```bash
# Use environment variables
export HYPERLIQUID_API_KEY="your-api-key"
export HYPERLIQUID_SECRET_KEY="your-secret-key"

# Or use .env file (add to .gitignore)
echo "HYPERLIQUID_API_KEY=your-api-key" > .env
echo "HYPERLIQUID_SECRET_KEY=your-secret-key" >> .env
```

### **File Permissions**
```bash
# Secure configuration files
chmod 600 src/config/*.json

# Secure log files
chmod 644 logs/*.log

# Secure data files
chmod 600 data/*
```

### **Firewall Configuration**
```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 8501  # Dashboard (if needed)
sudo ufw enable
```

## 📈 **Performance Optimization**

### **Resource Limits**
```bash
# Set CPU and memory limits
ulimit -c unlimited
ulimit -n 65536

# For Docker
docker run --cpus="2.0" --memory="2g" hyperliquid-trading-bot
```

### **Database Optimization**
```bash
# Optimize SQLite databases
sqlite3 data/trading.db "VACUUM;"
sqlite3 data/trading.db "ANALYZE;"
```

### **Log Rotation**
```bash
# Setup logrotate
sudo tee /etc/logrotate.d/trading-bot <<EOF
/path/to/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 trading trading
}
EOF
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Bot Won't Start**
```bash
# Check Python path
export PYTHONPATH=$PWD/src:$PYTHONPATH

# Check dependencies
pip install -r requirements.txt

# Check configuration
python3 src/config/validator.py --all
```

#### **API Connection Issues**
```bash
# Test API connectivity
python3 src/test_connections.py

# Check network connectivity
curl -I https://api.hyperliquid.xyz/info
```

#### **Performance Issues**
```bash
# Check system resources
python3 src/utils/performance_monitor.py --status

# Check logs for errors
grep -i error logs/*.log

# Restart with fresh environment
./stop_bot.sh
./start_bot.sh
```

### **Emergency Procedures**

#### **Emergency Stop**
```bash
# Immediate stop
./stop_bot.sh

# Kill all Python processes (use with caution)
pkill -f "src/main.py"

# For Docker
docker stop trading-bot
```

#### **Data Recovery**
```bash
# Restore from backup
cp backups/backup_YYYYMMDD_HHMMSS/* .

# Restore specific files
cp backups/backup_YYYYMMDD_HHMMSS/config.json src/config/
```

## 📋 **Maintenance Checklist**

### **Daily**
- [ ] Check bot status
- [ ] Review error logs
- [ ] Monitor performance metrics
- [ ] Verify API connectivity

### **Weekly**
- [ ] Review trading performance
- [ ] Clean old log files
- [ ] Update configuration if needed
- [ ] Test backup procedures

### **Monthly**
- [ ] Update dependencies
- [ ] Review and optimize configuration
- [ ] Analyze performance trends
- [ ] Update documentation

## 📞 **Support and Monitoring**

### **Health Checks**
```bash
# Automated health check script
#!/bin/bash
if ! pgrep -f "src/main.py trade" > /dev/null; then
    echo "Trading bot is not running!"
    # Send alert (email, Slack, etc.)
fi
```

### **Alerting Setup**
```bash
# Configure alert callbacks in performance monitor
python3 -c "
from src.utils.performance_monitor import get_performance_monitor
monitor = get_performance_monitor()
monitor.alert_callback = lambda alert: print(f'ALERT: {alert.message}')
"
```

## 🎉 **Deployment Complete!**

Your Hyperliquid Trading Bot is now ready for production use. Remember to:

1. **Test thoroughly** in dry-run mode before live trading
2. **Monitor continuously** using the provided tools
3. **Keep backups** of configuration and data
4. **Update regularly** to get the latest features and fixes
5. **Follow security best practices** to protect your API keys

For additional support, check the logs and use the troubleshooting section above.
