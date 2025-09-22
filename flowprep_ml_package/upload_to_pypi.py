#!/usr/bin/env python3
"""
Automated script to build and upload FlowPrep ML to PyPI
"""

import subprocess
import sys
import os
import shutil

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous builds...")
    dirs_to_remove = ['build', 'dist', '*.egg-info']
    for dir_pattern in dirs_to_remove:
        if '*' in dir_pattern:
            # Handle glob patterns
            import glob
            for path in glob.glob(dir_pattern):
                if os.path.exists(path):
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
        else:
            if os.path.exists(dir_pattern):
                if os.path.isdir(dir_pattern):
                    shutil.rmtree(dir_pattern)
                else:
                    os.remove(dir_pattern)
    print("✅ Cleanup completed")

def build_package():
    """Build the package"""
    return run_command("python -m build", "Building package")

def upload_to_testpypi():
    """Upload to TestPyPI"""
    print("\n📤 Uploading to TestPyPI...")
    print("You'll need your TestPyPI API token (starts with pypi-)")
    return run_command("python -m twine upload --repository testpypi dist/*", "Uploading to TestPyPI")

def upload_to_pypi():
    """Upload to real PyPI"""
    print("\n📤 Uploading to PyPI...")
    print("You'll need your PyPI API token (starts with pypi-)")
    return run_command("python -m twine upload dist/*", "Uploading to PyPI")

def test_installation():
    """Test installation from PyPI"""
    print("\n🧪 Testing installation...")
    return run_command("pip install flowprep-ml", "Installing from PyPI")

def main():
    """Main function"""
    print("🚀 FlowPrep ML - PyPI Upload Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('setup.py'):
        print("❌ Error: setup.py not found. Please run this script from the package directory.")
        sys.exit(1)
    
    # Step 1: Clean build
    clean_build()
    
    # Step 2: Build package
    if not build_package():
        print("❌ Build failed. Please fix errors and try again.")
        sys.exit(1)
    
    # Ask user what to do
    print("\n📋 What would you like to do?")
    print("1. Upload to TestPyPI (recommended for first time)")
    print("2. Upload to real PyPI")
    print("3. Just build (don't upload)")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        # Upload to TestPyPI
        if upload_to_testpypi():
            print("\n✅ Successfully uploaded to TestPyPI!")
            print("🔗 Check your package at: https://test.pypi.org/project/flowprep-ml/")
            print("\n📝 Next steps:")
            print("1. Test installation: pip install --index-url https://test.pypi.org/simple/ flowprep-ml")
            print("2. If everything works, upload to real PyPI")
        else:
            print("❌ Upload to TestPyPI failed")
    
    elif choice == "2":
        # Upload to real PyPI
        if upload_to_pypi():
            print("\n✅ Successfully uploaded to PyPI!")
            print("🔗 Check your package at: https://pypi.org/project/flowprep-ml/")
            print("\n🎉 Your package is now available worldwide!")
            print("Anyone can install it with: pip install flowprep-ml")
            
            # Test installation
            if test_installation():
                print("✅ Installation test successful!")
            else:
                print("⚠️ Installation test failed, but package was uploaded")
        else:
            print("❌ Upload to PyPI failed")
    
    elif choice == "3":
        print("✅ Package built successfully!")
        print("📁 Built files are in the 'dist/' directory")
        print("You can upload them manually later with: python -m twine upload dist/*")
    
    else:
        print("❌ Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()
