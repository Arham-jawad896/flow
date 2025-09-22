#!/usr/bin/env python3
"""
Basic usage example for FlowPrep ML library
"""

import pandas as pd
import numpy as np
import flowprep_ml

def create_sample_data():
    """Create sample data for demonstration"""
    np.random.seed(42)
    
    # Create sample dataset
    data = {
        'age': np.random.normal(35, 10, 100),
        'income': np.random.normal(50000, 15000, 100),
        'education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], 100),
        'experience': np.random.normal(5, 3, 100),
        'score': np.random.normal(75, 15, 100),
        'category': np.random.choice(['A', 'B', 'C', 'D'], 100)
    }
    
    # Add some missing values
    data['age'][np.random.choice(100, 5, replace=False)] = np.nan
    data['income'][np.random.choice(100, 3, replace=False)] = np.nan
    
    # Add some outliers
    data['income'][0] = 200000  # Outlier
    data['score'][1] = 150      # Outlier
    
    df = pd.DataFrame(data)
    return df

def main():
    """Main demonstration function"""
    print("🚀 FlowPrep ML - Basic Usage Example")
    print("=" * 50)
    
    # Create sample data
    print("Creating sample data...")
    data = create_sample_data()
    print(f"Created dataset with {data.shape[0]} rows and {data.shape[1]} columns")
    print(f"Missing values: {data.isnull().sum().sum()}")
    print()
    
    # Save sample data
    data.to_csv('sample_data.csv', index=False)
    print("Saved sample data to 'sample_data.csv'")
    print()
    
    # Example 1: Basic preprocessing
    print("📊 Example 1: Basic Preprocessing")
    print("-" * 30)
    result1 = flowprep_ml.preprocess('sample_data.csv')
    
    print(f"✅ Preprocessing completed successfully!")
    print(f"Original shape: {result1['original_shape']}")
    print(f"Processed shape: {result1['processed_shape']}")
    print(f"Train shape: {result1['train_shape']}")
    print(f"Test shape: {result1['test_shape']}")
    print(f"Output saved to: {result1['output_path']}")
    print()
    
    # Example 2: Advanced preprocessing
    print("🔧 Example 2: Advanced Preprocessing")
    print("-" * 30)
    result2 = flowprep_ml.preprocess(
        'sample_data.csv',
        imputation_method='median',
        scaling_method='standard',
        encoding_method='onehot',
        remove_outliers=True,
        outlier_method='iqr',
        test_size=0.3,
        random_state=42
    )
    
    print(f"✅ Advanced preprocessing completed!")
    print(f"Options used: {result2['options_used']}")
    print()
    
    # Example 3: Using PreprocessingOptions class
    print("⚙️ Example 3: Using PreprocessingOptions Class")
    print("-" * 30)
    from flowprep_ml import PreprocessingOptions
    
    options = PreprocessingOptions(
        imputation_method='mean',
        scaling_method='robust',
        encoding_method='label',
        remove_outliers=True,
        outlier_method='zscore',
        test_size=0.2,
        random_state=123
    )
    
    result3 = flowprep_ml.preprocess('sample_data.csv', **options.to_dict())
    print(f"✅ Preprocessing with options class completed!")
    print(f"Train data shape: {result3['train_data'].shape}")
    print(f"Test data shape: {result3['test_data'].shape}")
    print()
    
    # Show preprocessing logs
    print("📝 Preprocessing Logs:")
    print("-" * 20)
    for i, log_entry in enumerate(result3['preprocessing_log'], 1):
        print(f"{i}. {log_entry}")
    print()
    
    # Show data samples
    print("📈 Sample of Processed Data:")
    print("-" * 30)
    print("Training data (first 5 rows):")
    print(result3['train_data'].head())
    print()
    
    if not result3['test_data'].empty:
        print("Test data (first 5 rows):")
        print(result3['test_data'].head())
    print()
    
    # Clean up
    import os
    if os.path.exists('sample_data.csv'):
        os.remove('sample_data.csv')
    if os.path.exists(result1['output_path']):
        os.remove(result1['output_path'])
    if os.path.exists(result2['output_path']):
        os.remove(result2['output_path'])
    if os.path.exists(result3['output_path']):
        os.remove(result3['output_path'])
    
    print("🧹 Cleaned up temporary files")
    print("✅ All examples completed successfully!")

if __name__ == "__main__":
    main()
