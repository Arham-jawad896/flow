#!/usr/bin/env python3
"""
Installation script for FlowPrep ML library
"""

import subprocess
import sys
import os

def install_package():
    """Install the package in development mode"""
    try:
        print("🚀 Installing FlowPrep ML...")
        
        # Install in development mode
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        
        print("✅ FlowPrep ML installed successfully!")
        print()
        print("📖 Quick Start:")
        print("  import flowprep_ml")
        print("  result = flowprep_ml.preprocess('your_data.csv')")
        print()
        print("🔧 Run examples:")
        print("  python examples/basic_usage.py")
        print()
        print("🧪 Run tests:")
        print("  python -m pytest tests/ -v")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_package()
