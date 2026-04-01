"""
Simulation Logging Configuration
"""

import logging
import sys
import os
from datetime import datetime

# Create logs directory if it doesn't exist
log_dir = '/app/logs'
if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir, exist_ok=True)
    except PermissionError:
        # Fall back to current directory if /app/logs is not writable
        log_dir = './logs'
        os.makedirs(log_dir, exist_ok=True)

# Configure logging
handlers = [logging.StreamHandler(sys.stdout)]

# Try to add file handler, fall back to stdout only if not possible
try:
    handlers.append(logging.FileHandler(f'{log_dir}/simulation.log'))
except PermissionError:
    # Just use stdout if file logging is not possible
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)
