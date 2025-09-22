#!/usr/bin/env python3
"""
Upload FlowPrep ML to TestPyPI
"""

import subprocess
import sys
import os

def main():
    """Upload to TestPyPI"""
    print("🚀 Uploading FlowPrep ML to TestPyPI...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('setup.py'):
        print("❌ Error: setup.py not found. Please run this script from the package directory.")
        sys.exit(1)
    
    # Check if dist directory exists
    if not os.path.exists('dist'):
        print("❌ Error: dist/ directory not found. Please run 'python -m build' first.")
        sys.exit(1)
    
    print("📦 Uploading to TestPyPI...")
    print("You'll need your TestPyPI API token (starts with pypi-)")
    print()
    
    try:
        # Upload to TestPyPI
        result = subprocess.run([
            sys.executable, "-m", "twine", "upload", 
            "--repository", "testpypi", 
            "dist/*"
        ], check=True)
        
        print("✅ Successfully uploaded to TestPyPI!")
        print("🔗 Check your package at: https://test.pypi.org/project/flowprep-ml/")
        print()
        print("📝 Next steps:")
        print("1. Test installation: pip install --index-url https://test.pypi.org/simple/ flowprep-ml")
        print("2. If everything works, upload to real PyPI with: python -m twine upload dist/*")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Upload failed: {e}")
        print("Make sure you have the correct TestPyPI API token")

if __name__ == "__main__":
    main()
