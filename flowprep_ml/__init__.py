"""
FlowPrep ML - Intelligent Data Preprocessing Library

A powerful Python library for automated data preprocessing with advanced options.
Supports CSV, XLS, and XLSX files with intelligent preprocessing capabilities.

Author: Flow ML Team
Version: 1.0.0
License: MIT
"""

from .core import preprocess, PreprocessingOptions
from .utils import get_supported_formats, validate_file
from .exceptions import FlowPrepError, UnsupportedFileFormatError, ValidationError

__version__ = "1.0.0"
__author__ = "Flow ML Team"
__email__ = "support@flowml.ai"
__license__ = "MIT"

__all__ = [
    "preprocess",
    "PreprocessingOptions", 
    "get_supported_formats",
    "validate_file",
    "FlowPrepError",
    "UnsupportedFileFormatError", 
    "ValidationError"
]

# Package metadata
PACKAGE_NAME = "flowprep-ml"
DESCRIPTION = "Intelligent data preprocessing library with advanced options"
LONG_DESCRIPTION = """
FlowPrep ML is a powerful Python library that provides intelligent data preprocessing 
capabilities for machine learning workflows. It supports multiple file formats and 
offers advanced preprocessing options including:

- Missing value imputation (mean, median, mode, drop)
- Feature scaling (min-max, standard, robust)
- Categorical encoding (one-hot, label)
- Outlier detection and removal
- Train-test splitting
- And much more!

Perfect for data scientists and ML engineers who want to quickly preprocess 
their datasets with minimal code.
"""

# Supported file formats
SUPPORTED_FORMATS = ['.csv', '.xls', '.xlsx', '.xlsm']

# Default preprocessing options
DEFAULT_OPTIONS = {
    'imputation_method': 'mean',
    'scaling_method': 'minmax', 
    'encoding_method': 'onehot',
    'remove_outliers': False,
    'outlier_method': 'iqr',
    'test_size': 0.2,
    'random_state': 42
}
