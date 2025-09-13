#!/bin/bash

# Live Simulation Persistent Bot
# Automatically restarts the live simulation if it crashes

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Starting Live Simulation Persistent Bot..."
echo "Project root: $PROJECT_ROOT"
echo "Logs will be written to: $PROJECT_ROOT/src/logs/"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/src/logs"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$PROJECT_ROOT/src/logs/persistent_bot.log"
}

# Function to check if simulation is already running
check_if_running() {
    pgrep -f "run_live_simulation.py" > /dev/null
}

# Main loop
while true; do
    if check_if_running; then
        log_message "Live simulation is already running, waiting..."
        sleep 60
        continue
    fi
    
    log_message "Starting live simulation..."
    
    # Change to project root and run simulation
    cd "$PROJECT_ROOT"
    
    # Run the simulation
    PYTHONPATH=src python3 src/live_simulation/run_live_simulation.py
    
    EXIT_CODE=$?
    log_message "Live simulation exited with code $EXIT_CODE"
    
    if [ $EXIT_CODE -eq 0 ]; then
        log_message "Simulation completed successfully, restarting in 60 seconds..."
    else
        log_message "Simulation crashed, restarting in 60 seconds..."
    fi
    
    sleep 60
done