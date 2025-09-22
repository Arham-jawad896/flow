# FlowPrep ML 🚀

[![PyPI version](https://badge.fury.io/py/flowprep-ml.svg)](https://badge.fury.io/py/flowprep-ml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/flowprep-ml)](https://pepy.tech/project/flowprep-ml)

**Intelligent data preprocessing library with advanced options for machine learning workflows.**

FlowPrep ML is a powerful Python library that provides intelligent data preprocessing capabilities with minimal code. Perfect for data scientists and ML engineers who want to quickly preprocess their datasets with advanced options.

## ✨ Features

- **One-liner preprocessing**: `preprocess("data.csv")` and you're done!
- **Multiple file formats**: CSV, XLS, XLSX support
- **Advanced options**: Missing value imputation, feature scaling, categorical encoding, outlier removal
- **Intelligent defaults**: Works out of the box with sensible preprocessing choices
- **Flexible configuration**: Customize every aspect of preprocessing
- **Train-test splitting**: Automatic data splitting for ML workflows
- **Comprehensive logging**: Track every preprocessing step

## 🚀 Quick Start

### Installation

```bash
pip install flowprep-ml
```

### Basic Usage

```python
import flowprep_ml

# One-liner preprocessing
result = flowprep_ml.preprocess("data.csv")

# Access processed data
train_data = result['train_data']
test_data = result['test_data']
print(f"Processed {result['processed_shape'][0]} rows, {result['processed_shape'][1]} columns")
```

### Advanced Usage

```python
import flowprep_ml

# Custom preprocessing options
result = flowprep_ml.preprocess(
    "data.csv",
    imputation_method="median",      # Handle missing values
    scaling_method="standard",       # Scale features
    encoding_method="onehot",        # Encode categorical variables
    remove_outliers=True,            # Remove outliers
    outlier_method="iqr",            # Outlier detection method
    test_size=0.2,                   # 20% for testing
    random_state=42                  # Reproducible results
)

# Access results
print("Preprocessing log:")
for log_entry in result['preprocessing_log']:
    print(f"  - {log_entry}")

print(f"Output saved to: {result['output_path']}")
```

## 📊 Supported File Formats

- **CSV**: `.csv`
- **Excel**: `.xls`, `.xlsx`, `.xlsm`

## ⚙️ Preprocessing Options

### Missing Value Handling
- `imputation_method`: `"mean"`, `"median"`, `"mode"`, `"drop"`

### Feature Scaling
- `scaling_method`: `"minmax"`, `"standard"`, `"robust"`

### Categorical Encoding
- `encoding_method`: `"onehot"`, `"label"`

### Outlier Removal
- `remove_outliers`: `True`/`False`
- `outlier_method`: `"iqr"`, `"zscore"`

### Data Splitting
- `test_size`: Fraction for test set (0.0 to 1.0)
- `random_state`: Random seed for reproducibility

### Output Options
- `output_format`: `"csv"`, `"excel"`
- `save_processed`: `True`/`False`
- `output_path`: Custom output path

## 📖 Examples

### Example 1: Basic Preprocessing

```python
import flowprep_ml
import pandas as pd

# Create sample data
data = pd.DataFrame({
    'age': [25, 30, None, 45, 50],
    'income': [50000, 60000, 70000, 80000, 90000],
    'category': ['A', 'B', 'A', 'C', 'B'],
    'score': [85, 90, 78, 92, 88]
})
data.to_csv('sample_data.csv', index=False)

# Preprocess
result = flowprep_ml.preprocess('sample_data.csv')
print(result['preprocessing_log'])
```

### Example 2: Advanced Preprocessing

```python
import flowprep_ml

# Advanced preprocessing with custom options
result = flowprep_ml.preprocess(
    'data.csv',
    imputation_method='median',
    scaling_method='robust',
    encoding_method='onehot',
    remove_outliers=True,
    outlier_method='zscore',
    test_size=0.3,
    random_state=123
)

# Access processed data
train_data = result['train_data']
test_data = result['test_data']

print(f"Training set: {train_data.shape}")
print(f"Test set: {test_data.shape}")
print(f"Output file: {result['output_path']}")
```

### Example 3: Using PreprocessingOptions Class

```python
import flowprep_ml
from flowprep_ml import PreprocessingOptions

# Create options object
options = PreprocessingOptions(
    imputation_method='mean',
    scaling_method='standard',
    encoding_method='onehot',
    remove_outliers=True,
    outlier_method='iqr',
    test_size=0.2,
    random_state=42
)

# Use with preprocessing
result = flowprep_ml.preprocess('data.csv', **options.to_dict())
```

## 🔧 API Reference

### Main Functions

#### `preprocess(file_path, **kwargs)`

Main preprocessing function.

**Parameters:**
- `file_path` (str or Path): Path to input file
- `**kwargs`: Preprocessing options

**Returns:**
- `dict`: Preprocessing results containing:
  - `success` (bool): Whether preprocessing succeeded
  - `original_shape` (tuple): Original data shape
  - `processed_shape` (tuple): Processed data shape
  - `train_shape` (tuple): Training data shape
  - `test_shape` (tuple): Test data shape
  - `output_path` (str): Path to saved processed data
  - `preprocessing_log` (list): Log of preprocessing steps
  - `options_used` (dict): Options used for preprocessing
  - `train_data` (DataFrame): Processed training data
  - `test_data` (DataFrame): Processed test data

#### `get_supported_formats()`

Get list of supported file formats.

**Returns:**
- `list`: List of supported file extensions

#### `validate_file(file_path)`

Validate if file exists and is supported format.

**Parameters:**
- `file_path` (str or Path): Path to file

**Returns:**
- `bool`: True if file is valid

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `UnsupportedFileFormatError`: If file format is not supported

### Classes

#### `PreprocessingOptions`

Configuration class for preprocessing options.

**Attributes:**
- `imputation_method` (str): Method for handling missing values
- `scaling_method` (str): Method for scaling numerical features
- `encoding_method` (str): Method for encoding categorical variables
- `remove_outliers` (bool): Whether to remove outliers
- `outlier_method` (str): Method for outlier detection
- `test_size` (float): Fraction of data to use for testing
- `random_state` (int): Random seed for reproducibility
- `output_format` (str): Output file format
- `save_processed` (bool): Whether to save processed data
- `output_path` (str, optional): Custom output path

## 🛠️ Development

### Installation for Development

```bash
git clone https://github.com/flowml/flowprep-ml.git
cd flowprep-ml
pip install -e .
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black flowprep_ml/
flake8 flowprep_ml/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

- **Documentation**: [https://flowprep-ml.readthedocs.io/](https://flowprep-ml.readthedocs.io/)
- **Issues**: [https://github.com/flowml/flowprep-ml/issues](https://github.com/flowml/flowprep-ml/issues)
- **Email**: support@flowml.ai

## 🙏 Acknowledgments

- Built with [pandas](https://pandas.pydata.org/)
- Powered by [scikit-learn](https://scikit-learn.org/)
- Inspired by the need for simple, powerful data preprocessing

---

**Made with ❤️ by the Flow ML Team**