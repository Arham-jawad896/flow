#!/usr/bin/env python3
"""
Production startup script for Flow ML Backend
"""
import uvicorn
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    """Start the production server"""
    
    # Production configuration
    config = {
        "app": "main:app",
        "host": "0.0.0.0",
        "port": int(os.getenv("PORT", 8003)),
        "workers": int(os.getenv("WORKERS", 1)),
        "reload": False,
        "log_level": "info",
        "access_log": True,
        "use_colors": False,
    }
    
    # SSL configuration for production
    ssl_keyfile = os.getenv("SSL_KEYFILE")
    ssl_certfile = os.getenv("SSL_CERTFILE")
    
    if ssl_keyfile and ssl_certfile:
        config["ssl_keyfile"] = ssl_keyfile
        config["ssl_certfile"] = ssl_certfile
    
    print("🚀 Starting Flow ML Backend in production mode...")
    print(f"📍 Host: {config['host']}")
    print(f"🔌 Port: {config['port']}")
    print(f"👥 Workers: {config['workers']}")
    print(f"🔒 SSL: {'Enabled' if ssl_keyfile else 'Disabled'}")
    
    uvicorn.run(**config)

if __name__ == "__main__":
    main()
