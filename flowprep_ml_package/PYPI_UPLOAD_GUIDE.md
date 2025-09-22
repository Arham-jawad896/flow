# 🚀 PyPI Upload Guide for FlowPrep ML

This guide will walk you through uploading the FlowPrep ML library to PyPI so anyone in the world can install and use it with `pip install flowprep-ml`.

## 📁 Package Structure

Your package is now organized in the `flowprep_ml_package/` folder with this structure:

```
flowprep_ml_package/
├── flowprep_ml/              # Main package code
│   ├── __init__.py
│   ├── core.py
│   ├── options.py
│   ├── utils.py
│   └── exceptions.py
├── tests/                    # Test suite
│   ├── __init__.py
│   └── test_core.py
├── examples/                 # Usage examples
│   ├── basic_usage.py
│   └── advanced_usage.py
├── setup.py                  # Setup script
├── pyproject.toml           # Modern Python packaging
├── requirements.txt         # Dependencies
├── README.md               # Documentation
├── LICENSE                 # MIT license
├── MANIFEST.in            # Package manifest
└── PYPI_UPLOAD_GUIDE.md   # This guide
```

## 🔧 Prerequisites

Before uploading to PyPI, you need:

1. **Python 3.8+** installed
2. **pip** and **setuptools** updated
3. **PyPI account** (free at https://pypi.org)
4. **TestPyPI account** (for testing at https://test.pypi.org)

## 📋 Step-by-Step Upload Process

### Step 1: Create PyPI Accounts

1. Go to https://pypi.org and click "Register"
2. Create an account with your email and password
3. Go to https://test.pypi.org and create another account (can use same credentials)
4. **Important**: Verify your email addresses for both accounts

### Step 2: Install Required Tools

Open your terminal and run:

```bash
# Update pip and setuptools
pip install --upgrade pip setuptools wheel

# Install build tools
pip install build

# Install twine for uploading
pip install twine
```

### Step 3: Navigate to Package Directory

```bash
cd /home/arham/Desktop/Machine\ Learning/Projects/Flow/flowprep_ml_package
```

### Step 4: Clean Previous Builds

```bash
# Remove any previous build artifacts
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
```

### Step 5: Build the Package

```bash
# Build the package
python -m build
```

This will create:
- `dist/flowprep_ml-1.0.0-py3-none-any.whl` (wheel file)
- `dist/flowprep_ml-1.0.0.tar.gz` (source distribution)

### Step 6: Test on TestPyPI (Recommended)

First, test your package on TestPyPI:

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Your TestPyPI API token

**To get TestPyPI API token:**
1. Go to https://test.pypi.org/manage/account/
2. Scroll to "API tokens"
3. Click "Add API token"
4. Give it a name (e.g., "flowprep-ml")
5. Set scope to "Entire account"
6. Copy the token (starts with `pypi-`)

### Step 7: Test Installation from TestPyPI

```bash
# Install from TestPyPI to test
pip install --index-url https://test.pypi.org/simple/ flowprep-ml
```

Test the installation:

```bash
python -c "import flowprep_ml; print('FlowPrep ML installed successfully!')"
```

### Step 8: Upload to Real PyPI

Once testing is successful:

```bash
# Upload to real PyPI
python -m twine upload dist/*
```

You'll need a PyPI API token:
1. Go to https://pypi.org/manage/account/
2. Scroll to "API tokens"
3. Click "Add API token"
4. Give it a name (e.g., "flowprep-ml")
5. Set scope to "Entire account"
6. Copy the token (starts with `pypi-`)

### Step 9: Verify Upload

Check your package at: https://pypi.org/project/flowprep-ml/

### Step 10: Test Installation from PyPI

```bash
# Uninstall test version
pip uninstall flowprep-ml

# Install from real PyPI
pip install flowprep-ml

# Test it works
python -c "import flowprep_ml; print('Success!')"
```

## 🎯 Quick Commands Summary

Here are the essential commands in order:

```bash
# 1. Navigate to package directory
cd /home/arham/Desktop/Machine\ Learning/Projects/Flow/flowprep_ml_package

# 2. Clean previous builds
rm -rf build/ dist/ *.egg-info/

# 3. Build package
python -m build

# 4. Upload to TestPyPI (test first)
python -m twine upload --repository testpypi dist/*

# 5. Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ flowprep-ml

# 6. Upload to real PyPI
python -m twine upload dist/*

# 7. Install from PyPI
pip install flowprep-ml
```

## 🔍 Troubleshooting

### Common Issues:

1. **"Package already exists"**: Change version in `setup.py` and `pyproject.toml`
2. **"Invalid credentials"**: Make sure you're using API tokens, not passwords
3. **"Package not found"**: Wait a few minutes for PyPI to process
4. **"Build failed"**: Check that all dependencies are installed

### Version Updates:

To update the package:
1. Change version in `setup.py` (line 7) and `pyproject.toml` (line 4)
2. Rebuild: `python -m build`
3. Upload: `python -m twine upload dist/*`

## 🌟 After Upload

Once uploaded, anyone in the world can install your library with:

```bash
pip install flowprep-ml
```

And use it like:

```python
import flowprep_ml
result = flowprep_ml.preprocess("data.csv")
```

## 📚 Additional Resources

- [PyPI Documentation](https://packaging.python.org/tutorials/packaging-projects/)
- [TestPyPI Documentation](https://test.pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)

## ✅ Checklist

Before uploading, make sure:

- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] Package builds without errors: `python -m build`
- [ ] README.md looks good on GitHub
- [ ] Version numbers are consistent
- [ ] All dependencies are listed in requirements.txt
- [ ] LICENSE file is included
- [ ] You have PyPI and TestPyPI accounts
- [ ] You have API tokens for both

---

**Good luck with your PyPI upload! 🚀**
