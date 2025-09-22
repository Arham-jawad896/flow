# 🚀 FlowPrep ML - PyPI Upload Commands

Your package is ready! Here are the exact commands to upload it to PyPI.

## 📋 Prerequisites

1. **Create PyPI accounts** (free):
   - TestPyPI: https://test.pypi.org/account/register/
   - Real PyPI: https://pypi.org/account/register/

2. **Get API tokens**:
   - TestPyPI: https://test.pypi.org/manage/account/ → API tokens
   - Real PyPI: https://pypi.org/manage/account/ → API tokens
   - Create tokens with name "flowprep-ml" and scope "Entire account"
   - Copy the tokens (they start with `pypi-`)

## 🎯 Upload Commands

### Step 1: Navigate to Package Directory
```bash
cd /home/arham/Desktop/Machine\ Learning/Projects/Flow/flowprep_ml_package
```

### Step 2: Build Package (if not already done)
```bash
python -m build
```

### Step 3: Upload to TestPyPI (Recommended First)
```bash
python upload_testpypi.py
```
**OR manually:**
```bash
python -m twine upload --repository testpypi dist/*
```
- Username: `__token__`
- Password: Your TestPyPI API token

### Step 4: Test Installation from TestPyPI
```bash
pip install --index-url https://test.pypi.org/simple/ flowprep-ml
```

Test it works:
```bash
python -c "import flowprep_ml; print('Success!')"
```

### Step 5: Upload to Real PyPI
```bash
python upload_pypi.py
```
**OR manually:**
```bash
python -m twine upload dist/*
```
- Username: `__token__`
- Password: Your PyPI API token

### Step 6: Install from Real PyPI
```bash
pip install flowprep-ml
```

## 🎉 After Upload

Once uploaded, anyone in the world can:

**Install your library:**
```bash
pip install flowprep-ml
```

**Use it with one line:**
```python
import flowprep_ml
result = flowprep_ml.preprocess("data.csv")
```

**Or with advanced options:**
```python
result = flowprep_ml.preprocess(
    "data.csv",
    imputation_method="median",
    scaling_method="standard",
    encoding_method="onehot",
    remove_outliers=True,
    test_size=0.2
)
```

## 🔗 Package Links

- **TestPyPI**: https://test.pypi.org/project/flowprep-ml/
- **Real PyPI**: https://pypi.org/project/flowprep-ml/

## 🛠️ Troubleshooting

### "Package already exists"
- Change version in `setup.py` (line 7) and `pyproject.toml` (line 4)
- Rebuild: `python -m build`
- Upload again

### "Invalid credentials"
- Make sure you're using API tokens, not passwords
- Username should be `__token__`
- Password should be your API token (starts with `pypi-`)

### "Package not found after upload"
- Wait a few minutes for PyPI to process
- Check the package page directly

## ✅ Success Checklist

- [x] Package builds successfully
- [x] All files are included
- [x] Tests pass
- [x] Documentation is complete
- [x] You have PyPI accounts
- [x] You have API tokens
- [x] You're ready to upload!

---

**Your FlowPrep ML library is ready to go live! 🚀**
