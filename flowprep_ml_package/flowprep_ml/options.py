"""
Preprocessing options configuration for FlowPrep ML
"""

from dataclasses import dataclass
from typing import Optional, Union
from .exceptions import InvalidParameterError

@dataclass
class PreprocessingOptions:
    """
    Configuration class for preprocessing options
    
    Attributes:
        imputation_method: Method for handling missing values
            Options: 'mean', 'median', 'mode', 'drop'
        scaling_method: Method for scaling numerical features
            Options: 'minmax', 'standard', 'robust'
        encoding_method: Method for encoding categorical variables
            Options: 'onehot', 'label'
        remove_outliers: Whether to remove outliers
        outlier_method: Method for outlier detection
            Options: 'iqr', 'zscore'
        test_size: Fraction of data to use for testing (0.0 to 1.0)
        random_state: Random seed for reproducibility
        output_format: Output file format ('csv', 'excel')
        save_processed: Whether to save processed data to file
        output_path: Custom output path (optional)
    """
    
    # Missing value handling
    imputation_method: str = 'mean'
    
    # Feature scaling
    scaling_method: str = 'minmax'
    
    # Categorical encoding
    encoding_method: str = 'onehot'
    
    # Outlier handling
    remove_outliers: bool = False
    outlier_method: str = 'iqr'
    
    # Train-test split
    test_size: float = 0.2
    
    # Random state
    random_state: int = 42
    
    # Output options
    output_format: str = 'csv'
    save_processed: bool = True
    output_path: Optional[str] = None
    
    def __post_init__(self):
        """Validate options after initialization"""
        self._validate_options()
    
    def _validate_options(self):
        """Validate all preprocessing options"""
        # Validate imputation method
        valid_imputation = ['mean', 'median', 'mode', 'drop']
        if self.imputation_method not in valid_imputation:
            raise InvalidParameterError(
                f"Invalid imputation_method: {self.imputation_method}. "
                f"Must be one of: {', '.join(valid_imputation)}"
            )
        
        # Validate scaling method
        valid_scaling = ['minmax', 'standard', 'robust']
        if self.scaling_method not in valid_scaling:
            raise InvalidParameterError(
                f"Invalid scaling_method: {self.scaling_method}. "
                f"Must be one of: {', '.join(valid_scaling)}"
            )
        
        # Validate encoding method
        valid_encoding = ['onehot', 'label']
        if self.encoding_method not in valid_encoding:
            raise InvalidParameterError(
                f"Invalid encoding_method: {self.encoding_method}. "
                f"Must be one of: {', '.join(valid_encoding)}"
            )
        
        # Validate outlier method
        valid_outlier = ['iqr', 'zscore']
        if self.outlier_method not in valid_outlier:
            raise InvalidParameterError(
                f"Invalid outlier_method: {self.outlier_method}. "
                f"Must be one of: {', '.join(valid_outlier)}"
            )
        
        # Validate test size
        if not 0.0 <= self.test_size <= 1.0:
            raise InvalidParameterError(
                f"Invalid test_size: {self.test_size}. Must be between 0.0 and 1.0"
            )
        
        # Validate output format
        valid_output = ['csv', 'excel']
        if self.output_format not in valid_output:
            raise InvalidParameterError(
                f"Invalid output_format: {self.output_format}. "
                f"Must be one of: {', '.join(valid_output)}"
            )
    
    def to_dict(self) -> dict:
        """Convert options to dictionary"""
        return {
            'imputation_method': self.imputation_method,
            'scaling_method': self.scaling_method,
            'encoding_method': self.encoding_method,
            'remove_outliers': self.remove_outliers,
            'outlier_method': self.outlier_method,
            'test_size': self.test_size,
            'random_state': self.random_state,
            'output_format': self.output_format,
            'save_processed': self.save_processed,
            'output_path': self.output_path
        }
    
    @classmethod
    def from_dict(cls, options_dict: dict) -> 'PreprocessingOptions':
        """Create options from dictionary"""
        return cls(**options_dict)
    
    def __str__(self) -> str:
        """String representation of options"""
        return f"PreprocessingOptions({', '.join(f'{k}={v}' for k, v in self.to_dict().items() if v is not None)})"
