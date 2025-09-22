#!/usr/bin/env python3
"""
Upload FlowPrep ML to real PyPI
"""

import subprocess
import sys
import os

def main():
    """Upload to PyPI"""
    print("🚀 Uploading FlowPrep ML to PyPI...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('setup.py'):
        print("❌ Error: setup.py not found. Please run this script from the package directory.")
        sys.exit(1)
    
    # Check if dist directory exists
    if not os.path.exists('dist'):
        print("❌ Error: dist/ directory not found. Please run 'python -m build' first.")
        sys.exit(1)
    
    print("📦 Uploading to PyPI...")
    print("You'll need your PyPI API token (starts with pypi-)")
    print()
    
    try:
        # Upload to PyPI
        result = subprocess.run([
            sys.executable, "-m", "twine", "upload", 
            "dist/*"
        ], check=True)
        
        print("✅ Successfully uploaded to PyPI!")
        print("🔗 Check your package at: https://pypi.org/project/flowprep-ml/")
        print()
        print("🎉 Your package is now available worldwide!")
        print("Anyone can install it with: pip install flowprep-ml")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Upload failed: {e}")
        print("Make sure you have the correct PyPI API token")

if __name__ == "__main__":
    main()
