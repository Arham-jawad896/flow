"""
Tests for core preprocessing functionality
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
from pathlib import Path

from flowprep_ml import preprocess, PreprocessingOptions
from flowprep_ml.exceptions import PreprocessingError, UnsupportedFileFormatError, FileNotFoundError

class TestPreprocessing:
    """Test cases for preprocessing functionality"""
    
    def setup_method(self):
        """Set up test data"""
        self.test_data = pd.DataFrame({
            'age': [25, 30, None, 45, 50, 55, 60, 65, 70, 75],
            'income': [50000, 60000, 70000, 80000, 90000, 100000, 110000, 120000, 130000, 140000],
            'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C'],
            'score': [85, 90, 78, 92, 88, 95, 87, 91, 89, 93]
        })
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()
    
    def teardown_method(self):
        """Clean up test files"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_basic_preprocessing(self):
        """Test basic preprocessing functionality"""
        result = preprocess(self.temp_file.name)
        
        assert result['success'] == True
        assert 'train_data' in result
        assert 'test_data' in result
        assert 'preprocessing_log' in result
        assert 'options_used' in result
        assert result['original_shape'] == (10, 4)
    
    def test_preprocessing_with_options(self):
        """Test preprocessing with custom options"""
        result = preprocess(
            self.temp_file.name,
            imputation_method='median',
            scaling_method='standard',
            encoding_method='onehot',
            remove_outliers=True,
            test_size=0.3
        )
        
        assert result['success'] == True
        assert result['options_used']['imputation_method'] == 'median'
        assert result['options_used']['scaling_method'] == 'standard'
        assert result['options_used']['encoding_method'] == 'onehot'
        assert result['options_used']['remove_outliers'] == True
        assert result['options_used']['test_size'] == 0.3
    
    def test_file_not_found(self):
        """Test error handling for non-existent file"""
        with pytest.raises(PreprocessingError):
            preprocess('non_existent_file.csv')
    
    def test_unsupported_format(self):
        """Test error handling for unsupported file format"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_file.write("test data")
        temp_file.close()
        
        try:
            with pytest.raises(PreprocessingError):
                preprocess(temp_file.name)
        finally:
            os.unlink(temp_file.name)
    
    def test_preprocessing_options_validation(self):
        """Test PreprocessingOptions validation"""
        # Valid options
        options = PreprocessingOptions(
            imputation_method='mean',
            scaling_method='minmax',
            encoding_method='onehot',
            remove_outliers=False,
            outlier_method='iqr',
            test_size=0.2,
            random_state=42
        )
        assert options.imputation_method == 'mean'
        
        # Invalid imputation method
        with pytest.raises(Exception):  # Should raise InvalidParameterError
            PreprocessingOptions(imputation_method='invalid')
        
        # Invalid test size
        with pytest.raises(Exception):  # Should raise InvalidParameterError
            PreprocessingOptions(test_size=1.5)
    
    def test_output_saving(self):
        """Test that processed data is saved correctly"""
        result = preprocess(
            self.temp_file.name,
            save_processed=True,
            output_format='csv'
        )
        
        assert result['output_path'] is not None
        assert os.path.exists(result['output_path'])
        
        # Check that output file contains processed data
        output_data = pd.read_csv(result['output_path'])
        assert len(output_data) > 0
        
        # Clean up output file
        os.unlink(result['output_path'])
    
    def test_train_test_split(self):
        """Test train-test splitting functionality"""
        result = preprocess(
            self.temp_file.name,
            test_size=0.4,
            random_state=42
        )
        
        train_data = result['train_data']
        test_data = result['test_data']
        
        assert len(train_data) > 0
        assert len(test_data) > 0
        assert len(train_data) + len(test_data) <= result['processed_shape'][0]
    
    def test_missing_value_handling(self):
        """Test different missing value handling methods"""
        # Test mean imputation
        result_mean = preprocess(
            self.temp_file.name,
            imputation_method='mean'
        )
        assert result_mean['success'] == True
        
        # Test median imputation
        result_median = preprocess(
            self.temp_file.name,
            imputation_method='median'
        )
        assert result_median['success'] == True
        
        # Test mode imputation
        result_mode = preprocess(
            self.temp_file.name,
            imputation_method='mode'
        )
        assert result_mode['success'] == True
        
        # Test drop rows
        result_drop = preprocess(
            self.temp_file.name,
            imputation_method='drop'
        )
        assert result_drop['success'] == True
        # Should have fewer rows due to dropping
        assert result_drop['processed_shape'][0] < result_drop['original_shape'][0]
    
    def test_scaling_methods(self):
        """Test different scaling methods"""
        scaling_methods = ['minmax', 'standard', 'robust']
        
        for method in scaling_methods:
            result = preprocess(
                self.temp_file.name,
                scaling_method=method
            )
            assert result['success'] == True
            assert result['options_used']['scaling_method'] == method
    
    def test_encoding_methods(self):
        """Test different encoding methods"""
        encoding_methods = ['onehot', 'label']
        
        for method in encoding_methods:
            result = preprocess(
                self.temp_file.name,
                encoding_method=method
            )
            assert result['success'] == True
            assert result['options_used']['encoding_method'] == method
    
    def test_outlier_removal(self):
        """Test outlier removal functionality"""
        result = preprocess(
            self.temp_file.name,
            remove_outliers=True,
            outlier_method='iqr'
        )
        assert result['success'] == True
        assert result['options_used']['remove_outliers'] == True
        assert result['options_used']['outlier_method'] == 'iqr'
    
    def test_preprocessing_log(self):
        """Test that preprocessing log is comprehensive"""
        result = preprocess(self.temp_file.name)
        
        log = result['preprocessing_log']
        assert len(log) > 0
        
        # Check for common log entries
        log_text = ' '.join(log)
        assert 'Imputed missing values' in log_text or 'rows' in log_text or 'columns' in log_text
