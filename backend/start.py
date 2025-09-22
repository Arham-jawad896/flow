#!/usr/bin/env python3
"""
Flow ML Backend Startup Script

This script initializes the database and starts the FastAPI server.
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def setup_directories():
    """Create necessary directories."""
    directories = ['data', 'logs', 'reports']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def initialize_database():
    """Initialize the database with tables."""
    try:
        from database import Base, engine
        Base.metadata.create_all(bind=engine)
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        sys.exit(1)

def check_environment():
    """Check if required environment variables are set."""
    from config import settings
    
    warnings = []
    
    if settings.secret_key == "your-secret-key-change-this-in-production":
        warnings.append("⚠️  Using default secret key - change this in production!")
    
    if not settings.groq_api_key:
        warnings.append("⚠️  Groq API key not set - LLM features will be disabled")
    
    if settings.debug:
        warnings.append("⚠️  Debug mode is enabled - disable in production")
    
    for warning in warnings:
        print(warning)
    
    print("✓ Environment check completed")

def main():
    """Main startup function."""
    print("🚀 Starting Flow ML Backend...")
    print("=" * 50)
    
    # Setup directories
    setup_directories()
    
    # Check environment
    check_environment()
    
    # Initialize database
    initialize_database()
    
    print("=" * 50)
    print("✅ Backend setup completed successfully!")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 ReDoc Documentation: http://localhost:8000/redoc")
    print("🏥 Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    # Start the server
    try:
        import uvicorn
        from config import settings
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.debug,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"✗ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
