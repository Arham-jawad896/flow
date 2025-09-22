"""
Convenience function for preprocessing
"""

from .client import FlowClient
import os

def preprocess(
    file_path: str,
    api_key: str = None,
    imputation_method: str = "mean",
    scaling_method: str = "minmax", 
    encoding_method: str = "onehot",
    remove_outliers: bool = False,
    outlier_method: str = "iqr",
    test_size: float = 0.2,
    base_url: str = "http://localhost:8003"
) -> 'pd.DataFrame':
    """
    Preprocess a dataset using Flow ML
    
    This is a convenience function that creates a FlowClient and preprocesses the data.
    
    Args:
        file_path: Path to the CSV file
        api_key: Flow ML API key (optional, can use FLOW_API_KEY env var)
        imputation_method: Method for handling missing values (mean, median, mode, drop)
        scaling_method: Method for scaling numerical features (minmax, standard, robust)
        encoding_method: Method for encoding categorical variables (onehot, label)
        remove_outliers: Whether to remove outliers
        outlier_method: Method for outlier removal (iqr, zscore)
        test_size: Fraction of data to use for testing (0.0 to 1.0)
        base_url: Flow ML API base URL
    
    Returns:
        Preprocessed pandas DataFrame
        
    Example:
        >>> import flow_ml
        >>> df = flow_ml.preprocess("data.csv", imputation_method="median", scaling_method="standard")
    """
    client = FlowClient(api_key=api_key, base_url=base_url)
    return client.preprocess(
        file_path=file_path,
        imputation_method=imputation_method,
        scaling_method=scaling_method,
        encoding_method=encoding_method,
        remove_outliers=remove_outliers,
        outlier_method=outlier_method,
        test_size=test_size
    )
