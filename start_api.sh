#!/bin/bash
#
# Startup script for n8n Video Processing Pipeline API
# ===================================================
#
# This script starts the Flask API server with proper logging and error handling.
#

# Set script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_SCRIPT="$SCRIPT_DIR/n8n-video-api.py"
LOG_FILE="$SCRIPT_DIR/api.log"
PID_FILE="$SCRIPT_DIR/api.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ✅ $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ⚠️  $1"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ❌ $1"
}

# Check if API is already running
check_running() {
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # Running
        else
            rm -f "$PID_FILE"  # Clean up stale PID file
            return 1  # Not running
        fi
    fi
    return 1  # Not running
}

# Start the API
start_api() {
    print_status "Starting n8n Video Processing Pipeline API..."
    
    # Check if already running
    if check_running; then
        PID=$(cat "$PID_FILE")
        print_warning "API is already running (PID: $PID)"
        return 0
    fi
    
    # Check if Python script exists
    if [[ ! -f "$API_SCRIPT" ]]; then
        print_error "API script not found: $API_SCRIPT"
        return 1
    fi
    
    # Check dependencies
    print_status "Checking dependencies..."
    if ! python3 -c "import flask" 2>/dev/null; then
        print_error "Flask not installed. Install with: pip3 install flask"
        return 1
    fi
    
    if ! python3 -c "import requests" 2>/dev/null; then
        print_warning "Requests not installed (needed for testing). Install with: pip3 install requests"
    fi
    
    # Create necessary directories
    mkdir -p "/opt/n8n_scripts/video/_output-files"
    
    # Start the API in background
    print_status "Starting Flask server..."
    cd "$SCRIPT_DIR"
    
    # Start with nohup to keep running after terminal closes
    nohup python3 "$API_SCRIPT" >> "$LOG_FILE" 2>&1 &
    API_PID=$!
    
    # Save PID
    echo "$API_PID" > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 2
    
    if ps -p "$API_PID" > /dev/null 2>&1; then
        print_success "API started successfully (PID: $API_PID)"
        print_status "API is running on http://localhost:5000"
        print_status "Logs: tail -f $LOG_FILE"
        return 0
    else
        print_error "Failed to start API"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Stop the API
stop_api() {
    print_status "Stopping n8n Video Processing Pipeline API..."
    
    if check_running; then
        PID=$(cat "$PID_FILE")
        print_status "Stopping API (PID: $PID)..."
        
        kill "$PID"
        sleep 2
        
        # Force kill if still running
        if ps -p "$PID" > /dev/null 2>&1; then
            print_warning "Force killing API..."
            kill -9 "$PID"
        fi
        
        rm -f "$PID_FILE"
        print_success "API stopped"
    else
        print_warning "API is not running"
    fi
}

# Show status
status_api() {
    if check_running; then
        PID=$(cat "$PID_FILE")
        print_success "API is running (PID: $PID)"
        
        # Test health endpoint
        if command -v curl > /dev/null; then
            print_status "Testing health endpoint..."
            if curl -s http://localhost:5000/health > /dev/null; then
                print_success "Health check passed"
            else
                print_warning "Health check failed - API may be starting up"
            fi
        fi
    else
        print_warning "API is not running"
    fi
}

# Test the API
test_api() {
    print_status "Testing API endpoints..."
    if [[ -f "$SCRIPT_DIR/test_api.py" ]]; then
        python3 "$SCRIPT_DIR/test_api.py"
    else
        print_error "Test script not found: $SCRIPT_DIR/test_api.py"
    fi
}

# Show usage
usage() {
    echo "Usage: $0 {start|stop|restart|status|test|logs}"
    echo ""
    echo "Commands:"
    echo "  start   - Start the API server"
    echo "  stop    - Stop the API server"
    echo "  restart - Restart the API server"
    echo "  status  - Show API status"
    echo "  test    - Run API tests"
    echo "  logs    - Show recent logs"
    echo ""
    echo "API Endpoints:"
    echo "  GET  /health  - Health check"
    echo "  GET  /status  - Service status"
    echo "  POST /process - Process videos"
}

# Show logs
show_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        tail -f "$LOG_FILE"
    else
        print_warning "Log file not found: $LOG_FILE"
    fi
}

# Main script logic
case "$1" in
    start)
        start_api
        ;;
    stop)
        stop_api
        ;;
    restart)
        stop_api
        sleep 1
        start_api
        ;;
    status)
        status_api
        ;;
    test)
        test_api
        ;;
    logs)
        show_logs
        ;;
    *)
        usage
        exit 1
        ;;
esac

exit $?