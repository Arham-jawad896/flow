#!/usr/bin/env python3
"""
Test script to verify Flow ML Backend setup
"""

import sys
import importlib
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing imports...")
    
    required_modules = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pandas',
        'numpy',
        'sklearn',
        'PIL',
        'pydantic',
        'jose',
        'passlib',
        'groq'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please install missing dependencies with: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All imports successful!")
        return True

def test_database_connection():
    """Test database connection and table creation."""
    print("\n🗄️  Testing database connection...")
    
    try:
        from database import engine, Base
        from sqlalchemy import text
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Database connection successful")
        
        # Test table creation
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
        
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\n⚙️  Testing configuration...")
    
    try:
        from config import settings
        
        print(f"✓ App name: {settings.app_name}")
        print(f"✓ Database URL: {settings.database_url}")
        print(f"✓ Upload directory: {settings.upload_dir}")
        print(f"✓ Debug mode: {settings.debug}")
        
        if settings.groq_api_key:
            print("✓ Groq API key configured")
        else:
            print("⚠️  Groq API key not configured (LLM features will be disabled)")
        
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def test_directories():
    """Test if required directories exist or can be created."""
    print("\n📁 Testing directories...")
    
    directories = ['data', 'logs', 'reports']
    
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            print(f"✓ {directory}/")
        except Exception as e:
            print(f"✗ {directory}/: {e}")
            return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Flow ML Backend Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config,
        test_directories,
        test_database_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Set your Groq API key in .env file (optional)")
        print("2. Run: python start.py")
        print("3. Visit: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
