import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler, LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
from sklearn.ensemble import IsolationForest
from PIL import Image
import json
import os
import logging
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
import uuid
from config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Main preprocessing class for handling different data types."""
    
    def __init__(self, options: Dict[str, Any] = None):
        self.options = options or {}
        self.scaling_method = self.options.get('scaling_method', 'minmax')
        self.missing_value_strategy = self.options.get('missing_value_strategy', 'mean')
        self.outlier_removal = self.options.get('outlier_removal', False)
        self.data_augmentation = self.options.get('data_augmentation', False)
        self.train_test_split = self.options.get('train_test_split', 0.8)
        self.feature_engineering = self.options.get('feature_engineering', False)
        
    def preprocess_csv(self, file_path: str, is_premium: bool = False) -> Dict[str, Any]:
        """Preprocess CSV data."""
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            original_shape = df.shape
            
            logger.info(f"Starting CSV preprocessing for {original_shape[0]} rows, {original_shape[1]} columns")
            
            # Basic preprocessing steps
            preprocessing_log = []
            
            # 1. Handle missing values
            missing_before = df.isnull().sum().sum()
            if missing_before > 0:
                if is_premium and self.missing_value_strategy in ['median', 'mode']:
                    if self.missing_value_strategy == 'median':
                        numeric_columns = df.select_dtypes(include=[np.number]).columns
                        df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
                    elif self.missing_value_strategy == 'mode':
                        categorical_columns = df.select_dtypes(include=['object']).columns
                        for col in categorical_columns:
                            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown')
                else:
                    # Free tier: use mean for numeric, mode for categorical
                    numeric_columns = df.select_dtypes(include=[np.number]).columns
                    categorical_columns = df.select_dtypes(include=['object']).columns
                    
                    if len(numeric_columns) > 0:
                        df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())
                    if len(categorical_columns) > 0:
                        for col in categorical_columns:
                            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown')
                
                missing_after = df.isnull().sum().sum()
                preprocessing_log.append(f"Handled {missing_before} missing values, {missing_after} remaining")
            
            # 2. Handle outliers (Premium only)
            outliers_removed = 0
            if is_premium and self.outlier_removal:
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                if len(numeric_columns) > 0:
                    isolation_forest = IsolationForest(contamination=0.1, random_state=42)
                    outlier_mask = isolation_forest.fit_predict(df[numeric_columns]) == -1
                    outliers_removed = outlier_mask.sum()
                    df = df[~outlier_mask]
                    preprocessing_log.append(f"Removed {outliers_removed} outliers using Isolation Forest")
            
            # 3. Encode categorical variables
            categorical_columns = df.select_dtypes(include=['object']).columns
            encoded_columns = []
            
            for col in categorical_columns:
                unique_values = df[col].nunique()
                if unique_values <= 10:  # One-hot encode if few unique values
                    dummies = pd.get_dummies(df[col], prefix=col)
                    df = pd.concat([df, dummies], axis=1)
                    df.drop(col, axis=1, inplace=True)
                    encoded_columns.extend(dummies.columns.tolist())
                else:  # Label encode if many unique values
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col].astype(str))
                    encoded_columns.append(col)
            
            if encoded_columns:
                preprocessing_log.append(f"Encoded {len(encoded_columns)} categorical columns")
            
            # 4. Scale numerical features
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                if is_premium:
                    if self.scaling_method == 'standard':
                        scaler = StandardScaler()
                    elif self.scaling_method == 'robust':
                        scaler = RobustScaler()
                    else:  # minmax
                        scaler = MinMaxScaler()
                else:
                    # Free tier: always use MinMax scaling
                    scaler = MinMaxScaler()
                
                df[numeric_columns] = scaler.fit_transform(df[numeric_columns])
                preprocessing_log.append(f"Scaled {len(numeric_columns)} numerical columns using {scaler.__class__.__name__}")
            
            # 5. Feature engineering (Premium only)
            if is_premium and self.feature_engineering:
                # Add polynomial features for numeric columns
                from sklearn.preprocessing import PolynomialFeatures
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                if len(numeric_columns) > 0:
                    poly = PolynomialFeatures(degree=2, include_bias=False, interaction_only=True)
                    poly_features = poly.fit_transform(df[numeric_columns])
                    poly_feature_names = [f"poly_{i}" for i in range(poly_features.shape[1])]
                    poly_df = pd.DataFrame(poly_features, columns=poly_feature_names, index=df.index)
                    df = pd.concat([df, poly_df], axis=1)
                    preprocessing_log.append(f"Added {poly_features.shape[1]} polynomial features")
            
            # 6. Train-test split
            if len(df) > 1:  # Only split if we have more than 1 row
                train_df, test_df = train_test_split(
                    df, 
                    test_size=1-self.train_test_split, 
                    random_state=42,
                    stratify=df.iloc[:, -1] if df.shape[1] > 1 else None
                )
            else:
                train_df = df
                test_df = pd.DataFrame()
            
            # Save processed files
            processed_file_path = self._save_processed_data(train_df, test_df, file_path)
            
            result = {
                'success': True,
                'original_shape': original_shape,
                'processed_shape': df.shape,
                'train_shape': train_df.shape,
                'test_shape': test_df.shape,
                'outliers_removed': outliers_removed,
                'preprocessing_log': preprocessing_log,
                'processed_file_path': processed_file_path,
                'columns_info': {
                    'total_columns': len(df.columns),
                    'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
                    'categorical_columns': len(encoded_columns)
                }
            }
            
            logger.info(f"CSV preprocessing completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in CSV preprocessing: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'preprocessing_log': [f"Error: {str(e)}"]
            }
    
    def preprocess_images(self, file_paths: list, is_premium: bool = False) -> Dict[str, Any]:
        """Preprocess image data."""
        try:
            preprocessing_log = []
            processed_images = []
            
            for file_path in file_paths:
                try:
                    # Load and process image
                    img = Image.open(file_path)
                    
                    # Convert to RGB if necessary
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Resize to standard size (Premium: customizable, Free: fixed)
                    if is_premium:
                        target_size = self.options.get('image_size', (224, 224))
                    else:
                        target_size = (224, 224)  # Free tier: fixed size
                    
                    img = img.resize(target_size)
                    
                    # Data augmentation (Premium only)
                    if is_premium and self.data_augmentation:
                        # Add augmentation logic here
                        pass
                    
                    # Save processed image
                    processed_path = self._save_processed_image(img, file_path)
                    processed_images.append(processed_path)
                    
                except Exception as e:
                    logger.error(f"Error processing image {file_path}: {str(e)}")
                    preprocessing_log.append(f"Error processing {file_path}: {str(e)}")
            
            result = {
                'success': True,
                'processed_images': processed_images,
                'total_images': len(file_paths),
                'successful_images': len(processed_images),
                'preprocessing_log': preprocessing_log
            }
            
            logger.info(f"Image preprocessing completed: {len(processed_images)}/{len(file_paths)} successful")
            return result
            
        except Exception as e:
            logger.error(f"Error in image preprocessing: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'preprocessing_log': [f"Error: {str(e)}"]
            }
    
    def preprocess_text(self, file_path: str, is_premium: bool = False) -> Dict[str, Any]:
        """Preprocess text data."""
        try:
            # Read text file
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            preprocessing_log = []
            
            # Basic text preprocessing
            # 1. Clean text
            import re
            text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = text.lower().strip()
            
            preprocessing_log.append("Cleaned text: removed punctuation, normalized whitespace")
            
            # 2. Tokenization and basic processing
            words = text.split()
            unique_words = len(set(words))
            total_words = len(words)
            
            preprocessing_log.append(f"Tokenized text: {total_words} words, {unique_words} unique")
            
            # 3. Data augmentation (Premium only)
            if is_premium and self.data_augmentation:
                # Add text augmentation logic here
                pass
            
            # Save processed text
            processed_file_path = self._save_processed_text(text, file_path)
            
            result = {
                'success': True,
                'original_length': len(text),
                'processed_length': len(text),
                'total_words': total_words,
                'unique_words': unique_words,
                'preprocessing_log': preprocessing_log,
                'processed_file_path': processed_file_path
            }
            
            logger.info("Text preprocessing completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in text preprocessing: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'preprocessing_log': [f"Error: {str(e)}"]
            }
    
    def _save_processed_data(self, train_df: pd.DataFrame, test_df: pd.DataFrame, original_path: str) -> str:
        """Save processed data to files."""
        # Generate unique filename
        file_id = str(uuid.uuid4())
        base_name = Path(original_path).stem
        
        # Save train and test sets
        train_path = os.path.join(settings.upload_dir, f"{file_id}_train.csv")
        test_path = os.path.join(settings.upload_dir, f"{file_id}_test.csv")
        
        train_df.to_csv(train_path, index=False)
        if not test_df.empty:
            test_df.to_csv(test_path, index=False)
        
        return train_path
    
    def _save_processed_image(self, img: Image.Image, original_path: str) -> str:
        """Save processed image."""
        file_id = str(uuid.uuid4())
        base_name = Path(original_path).stem
        processed_path = os.path.join(settings.upload_dir, f"{file_id}_processed.jpg")
        
        img.save(processed_path, 'JPEG', quality=95)
        return processed_path
    
    def _save_processed_text(self, text: str, original_path: str) -> str:
        """Save processed text."""
        file_id = str(uuid.uuid4())
        base_name = Path(original_path).stem
        processed_path = os.path.join(settings.upload_dir, f"{file_id}_processed.txt")
        
        with open(processed_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return processed_path

def get_file_type(file_path: str) -> str:
    """Determine file type based on extension. MVP supports only tabular: CSV/XLS/XLSX."""
    extension = Path(file_path).suffix.lower()
    if extension in ['.csv', '.xlsx', '.xls']:
        return 'csv'
    return 'unknown'

def validate_file_size(file_size: int, is_premium: bool = False) -> bool:
    """Validate file size based on user tier."""
    if is_premium:
        return file_size <= settings.max_file_size * 10  # Premium: 500MB
    else:
        return file_size <= settings.free_tier_max_file_size  # Free: 50MB

def validate_csv_rows(row_count: int, is_premium: bool = False) -> bool:
    """Validate CSV row count based on user tier."""
    if is_premium:
        return True  # Premium: unlimited
    else:
        return row_count <= settings.free_tier_max_rows  # Free: 50k rows

class AdvancedDataPreprocessor:
    """Advanced preprocessing class with custom options."""
    
    def preprocess_file_advanced(
        self,
        file_path: str,
        file_type: str,
        output_path: str,
        imputation_method: str = "mean",
        scaling_method: str = "minmax",
        encoding_method: str = "onehot",
        remove_outliers: bool = False,
        outlier_method: str = "iqr",
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """Advanced preprocessing with custom options."""
        try:
            if file_type == 'csv':
                return self.preprocess_csv_advanced(
                    file_path, output_path, imputation_method, 
                    scaling_method, encoding_method, remove_outliers, 
                    outlier_method, test_size
                )
            else:
                return {
                    'success': False,
                    'error': f'Advanced preprocessing not supported for {file_type} files'
                }
        except Exception as e:
            logger.error(f"Error in advanced preprocessing: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def preprocess_csv_advanced(
        self,
        file_path: str,
        output_path: str,
        imputation_method: str = "mean",
        scaling_method: str = "minmax",
        encoding_method: str = "onehot",
        remove_outliers: bool = False,
        outlier_method: str = "iqr",
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """Advanced CSV preprocessing with custom options."""
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            original_shape = df.shape
            
            logger.info(f"Starting advanced CSV preprocessing for {original_shape[0]} rows, {original_shape[1]} columns")
            
            preprocessing_log = []
            
            # 1. Handle missing values with custom method
            missing_before = df.isnull().sum().sum()
            if missing_before > 0:
                if imputation_method == 'mean':
                    numeric_columns = df.select_dtypes(include=[np.number]).columns
                    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())
                    categorical_columns = df.select_dtypes(include=['object']).columns
                    df[categorical_columns] = df[categorical_columns].fillna(df[categorical_columns].mode().iloc[0])
                elif imputation_method == 'median':
                    numeric_columns = df.select_dtypes(include=[np.number]).columns
                    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
                    categorical_columns = df.select_dtypes(include=['object']).columns
                    df[categorical_columns] = df[categorical_columns].fillna(df[categorical_columns].mode().iloc[0])
                elif imputation_method == 'mode':
                    for column in df.columns:
                        df[column] = df[column].fillna(df[column].mode().iloc[0] if not df[column].mode().empty else 'Unknown')
                elif imputation_method == 'drop':
                    df = df.dropna()
                
                missing_after = df.isnull().sum().sum()
                preprocessing_log.append(f"Missing values: {missing_before} -> {missing_after} (method: {imputation_method})")
            
            # 2. Remove outliers if requested
            if remove_outliers:
                outliers_before = len(df)
                if outlier_method == 'iqr':
                    numeric_columns = df.select_dtypes(include=[np.number]).columns
                    for column in numeric_columns:
                        Q1 = df[column].quantile(0.25)
                        Q3 = df[column].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
                elif outlier_method == 'zscore':
                    numeric_columns = df.select_dtypes(include=[np.number]).columns
                    for column in numeric_columns:
                        z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
                        df = df[z_scores < 3]
                
                outliers_after = len(df)
                preprocessing_log.append(f"Outliers removed: {outliers_before} -> {outliers_after} rows (method: {outlier_method})")
            
            # 3. Encode categorical variables
            categorical_columns = df.select_dtypes(include=['object']).columns
            if len(categorical_columns) > 0:
                if encoding_method == 'onehot':
                    df = pd.get_dummies(df, columns=categorical_columns, prefix=categorical_columns)
                    preprocessing_log.append(f"One-hot encoding applied to {len(categorical_columns)} categorical columns")
                elif encoding_method == 'label':
                    le = LabelEncoder()
                    for column in categorical_columns:
                        df[column] = le.fit_transform(df[column].astype(str))
                    preprocessing_log.append(f"Label encoding applied to {len(categorical_columns)} categorical columns")
            
            # 4. Scale numerical features
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                if scaling_method == 'minmax':
                    scaler = MinMaxScaler()
                elif scaling_method == 'standard':
                    scaler = StandardScaler()
                elif scaling_method == 'robust':
                    scaler = RobustScaler()
                else:
                    scaler = MinMaxScaler()  # Default
                
                df[numeric_columns] = scaler.fit_transform(df[numeric_columns])
                preprocessing_log.append(f"Scaling applied using {scaling_method} method to {len(numeric_columns)} numeric columns")
            
            # 5. Train-test split
            if test_size > 0 and test_size < 1:
                # For now, just save the processed data
                # In a real implementation, you'd split and save both train and test sets
                preprocessing_log.append(f"Data prepared for train-test split (test_size: {test_size})")
            
            # Save processed data
            df.to_csv(output_path, index=False)
            
            final_shape = df.shape
            preprocessing_log.append(f"Final shape: {final_shape[0]} rows, {final_shape[1]} columns")
            
            logger.info("Advanced CSV preprocessing completed successfully")
            
            return {
                'success': True,
                'output_path': output_path,
                'rows_count': final_shape[0],
                'columns_count': final_shape[1],
                'log': '\n'.join(preprocessing_log)
            }
            
        except Exception as e:
            logger.error(f"Error in advanced CSV preprocessing: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
