"""
Core preprocessing functionality for FlowPrep ML
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union, Optional, Dict, Any, Tuple
import logging

from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer

from .options import PreprocessingOptions
from .utils import validate_file, get_file_type, get_output_path
from .exceptions import PreprocessingError, ValidationError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlowPrepProcessor:
    """
    Main preprocessing class for FlowPrep ML
    """
    
    def __init__(self, options: PreprocessingOptions = None):
        """
        Initialize processor with options
        
        Args:
            options: Preprocessing options configuration
        """
        self.options = options or PreprocessingOptions()
        self.scalers = {}
        self.encoders = {}
        self.imputers = {}
        self.preprocessing_log = []
    
    def preprocess(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Main preprocessing function
        
        Args:
            file_path: Path to input file
            **kwargs: Additional preprocessing options
            
        Returns:
            Dictionary containing preprocessing results
        """
        try:
            # Validate file
            validate_file(file_path)
            
            # Update options with kwargs
            if kwargs:
                options_dict = self.options.to_dict()
                options_dict.update(kwargs)
                self.options = PreprocessingOptions.from_dict(options_dict)
            
            # Load data
            data = self._load_data(file_path)
            original_shape = data.shape
            
            logger.info(f"Starting preprocessing for {original_shape[0]} rows, {original_shape[1]} columns")
            
            # Reset preprocessing log
            self.preprocessing_log = []
            
            # Apply preprocessing steps
            processed_data = self._preprocess_data(data)
            
            # Train-test split
            train_data, test_data = self._split_data(processed_data)
            
            # Save processed data if requested
            output_path = None
            if self.options.save_processed:
                output_path = self._save_data(train_data, test_data, file_path)
            
            # Prepare results
            results = {
                'success': True,
                'original_shape': original_shape,
                'processed_shape': processed_data.shape,
                'train_shape': train_data.shape,
                'test_shape': test_data.shape,
                'output_path': output_path,
                'preprocessing_log': self.preprocessing_log,
                'options_used': self.options.to_dict(),
                'train_data': train_data,
                'test_data': test_data
            }
            
            logger.info("Preprocessing completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {str(e)}")
            raise PreprocessingError(f"Preprocessing failed: {str(e)}")
    
    def _load_data(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """Load data from file"""
        file_path = Path(file_path)
        file_type = get_file_type(file_path)
        
        try:
            if file_type == 'csv':
                data = pd.read_csv(file_path)
            elif file_type == 'excel':
                data = pd.read_excel(file_path)
            else:
                raise ValidationError(f"Unsupported file type: {file_type}")
            
            self.preprocessing_log.append(f"Loaded data: {data.shape[0]} rows, {data.shape[1]} columns")
            return data
            
        except Exception as e:
            raise PreprocessingError(f"Failed to load data: {str(e)}")
    
    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply all preprocessing steps"""
        processed_data = data.copy()
        
        # 1. Handle missing values
        processed_data = self._handle_missing_values(processed_data)
        
        # 2. Remove outliers if requested
        if self.options.remove_outliers:
            processed_data = self._remove_outliers(processed_data)
        
        # 3. Encode categorical variables
        processed_data = self._encode_categorical(processed_data)
        
        # 4. Scale numerical features
        processed_data = self._scale_features(processed_data)
        
        return processed_data
    
    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values based on imputation method"""
        missing_before = data.isnull().sum().sum()
        
        if missing_before == 0:
            self.preprocessing_log.append("No missing values found")
            return data
        
        if self.options.imputation_method == 'drop':
            data = data.dropna()
            missing_after = data.isnull().sum().sum()
            self.preprocessing_log.append(f"Dropped rows with missing values: {missing_before} -> {missing_after}")
        else:
            # Separate numeric and categorical columns
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            categorical_columns = data.select_dtypes(include=['object']).columns
            
            if len(numeric_columns) > 0:
                if self.options.imputation_method == 'mean':
                    data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].mean())
                elif self.options.imputation_method == 'median':
                    data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].median())
                elif self.options.imputation_method == 'mode':
                    data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].mode().iloc[0])
            
            if len(categorical_columns) > 0:
                for col in categorical_columns:
                    data[col] = data[col].fillna(data[col].mode().iloc[0] if not data[col].mode().empty else 'Unknown')
            
            missing_after = data.isnull().sum().sum()
            self.preprocessing_log.append(f"Imputed missing values: {missing_before} -> {missing_after} (method: {self.options.imputation_method})")
        
        return data
    
    def _remove_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """Remove outliers using specified method"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) == 0:
            self.preprocessing_log.append("No numeric columns for outlier removal")
            return data
        
        outliers_before = len(data)
        
        if self.options.outlier_method == 'iqr':
            for column in numeric_columns:
                Q1 = data[column].quantile(0.25)
                Q3 = data[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                data = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]
        
        elif self.options.outlier_method == 'zscore':
            for column in numeric_columns:
                z_scores = np.abs((data[column] - data[column].mean()) / data[column].std())
                data = data[z_scores < 3]
        
        outliers_after = len(data)
        self.preprocessing_log.append(f"Removed outliers: {outliers_before} -> {outliers_after} rows (method: {self.options.outlier_method})")
        
        return data
    
    def _encode_categorical(self, data: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical variables"""
        categorical_columns = data.select_dtypes(include=['object']).columns
        
        if len(categorical_columns) == 0:
            self.preprocessing_log.append("No categorical columns to encode")
            return data
        
        if self.options.encoding_method == 'onehot':
            data = pd.get_dummies(data, columns=categorical_columns, prefix=categorical_columns)
            self.preprocessing_log.append(f"Applied one-hot encoding to {len(categorical_columns)} categorical columns")
        
        elif self.options.encoding_method == 'label':
            for column in categorical_columns:
                le = LabelEncoder()
                data[column] = le.fit_transform(data[column].astype(str))
                self.encoders[column] = le
            self.preprocessing_log.append(f"Applied label encoding to {len(categorical_columns)} categorical columns")
        
        return data
    
    def _scale_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Scale numerical features"""
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) == 0:
            self.preprocessing_log.append("No numeric columns to scale")
            return data
        
        if self.options.scaling_method == 'minmax':
            scaler = MinMaxScaler()
        elif self.options.scaling_method == 'standard':
            scaler = StandardScaler()
        elif self.options.scaling_method == 'robust':
            scaler = RobustScaler()
        else:
            scaler = MinMaxScaler()
        
        data[numeric_columns] = scaler.fit_transform(data[numeric_columns])
        self.scalers['numeric'] = scaler
        self.preprocessing_log.append(f"Scaled {len(numeric_columns)} numeric columns using {self.options.scaling_method} scaling")
        
        return data
    
    def _split_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split data into train and test sets"""
        if self.options.test_size <= 0 or self.options.test_size >= 1:
            self.preprocessing_log.append("No train-test split (test_size = 0)")
            return data, pd.DataFrame()
        
        if len(data) < 2:
            self.preprocessing_log.append("Insufficient data for train-test split")
            return data, pd.DataFrame()
        
        try:
            train_data, test_data = train_test_split(
                data,
                test_size=self.options.test_size,
                random_state=self.options.random_state,
                stratify=data.iloc[:, -1] if data.shape[1] > 1 else None
            )
            self.preprocessing_log.append(f"Split data: {len(train_data)} train, {len(test_data)} test")
        except Exception as e:
            # If stratification fails, split without it
            train_data, test_data = train_test_split(
                data,
                test_size=self.options.test_size,
                random_state=self.options.random_state
            )
            self.preprocessing_log.append(f"Split data (no stratification): {len(train_data)} train, {len(test_data)} test")
        
        return train_data, test_data
    
    def _save_data(self, train_data: pd.DataFrame, test_data: pd.DataFrame, input_path: Union[str, Path]) -> str:
        """Save processed data to file"""
        input_path = Path(input_path)
        
        if self.options.output_path:
            output_path = Path(self.options.output_path)
        else:
            output_path = get_output_path(input_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if self.options.output_format == 'csv':
                train_data.to_csv(output_path, index=False)
                if not test_data.empty:
                    test_path = output_path.parent / f"{output_path.stem}_test.csv"
                    test_data.to_csv(test_path, index=False)
            elif self.options.output_format == 'excel':
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    train_data.to_excel(writer, sheet_name='train', index=False)
                    if not test_data.empty:
                        test_data.to_excel(writer, sheet_name='test', index=False)
            
            self.preprocessing_log.append(f"Saved processed data to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            raise PreprocessingError(f"Failed to save processed data: {str(e)}")

# Main preprocessing function
def preprocess(file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
    """
    One-liner preprocessing function
    
    Args:
        file_path: Path to input file
        **kwargs: Preprocessing options
        
    Returns:
        Dictionary containing preprocessing results
        
    Example:
        >>> import flowprep_ml
        >>> result = flowprep_ml.preprocess("data.csv", scaling="standard", remove_outliers=True)
        >>> print(result['train_data'])
    """
    options = PreprocessingOptions.from_dict(kwargs) if kwargs else PreprocessingOptions()
    processor = FlowPrepProcessor(options)
    return processor.preprocess(file_path)
