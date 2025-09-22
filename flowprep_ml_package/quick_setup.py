#!/usr/bin/env python3
"""
Quick setup script for FlowPrep ML package
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages for building and uploading"""
    print("📦 Installing required packages...")
    
    packages = [
        "build",
        "twine",
        "setuptools",
        "wheel"
    ]
    
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")

def check_package_structure():
    """Check if package structure is correct"""
    print("🔍 Checking package structure...")
    
    required_files = [
        "setup.py",
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "flowprep_ml/__init__.py",
        "flowprep_ml/core.py",
        "flowprep_ml/options.py",
        "flowprep_ml/utils.py",
        "flowprep_ml/exceptions.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    else:
        print("✅ Package structure looks good!")
        return True

def run_tests():
    """Run tests to make sure everything works"""
    print("🧪 Running tests...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("⚠️ pytest not found, skipping tests")
        return True

def main():
    """Main setup function"""
    print("🚀 FlowPrep ML - Quick Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('setup.py'):
        print("❌ Error: Please run this script from the flowprep_ml_package directory")
        print("   cd /home/arham/Desktop/Machine\\ Learning/Projects/Flow/flowprep_ml_package")
        sys.exit(1)
    
    # Install requirements
    install_requirements()
    
    # Check package structure
    if not check_package_structure():
        print("❌ Package structure issues found. Please fix them before proceeding.")
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("❌ Tests failed. Please fix issues before uploading to PyPI.")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Create PyPI account at https://pypi.org")
    print("2. Create TestPyPI account at https://test.pypi.org")
    print("3. Get API tokens from both accounts")
    print("4. Run: python upload_to_pypi.py")
    print("\n📖 For detailed instructions, see PYPI_UPLOAD_GUIDE.md")

if __name__ == "__main__":
    main()
