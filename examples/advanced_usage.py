#!/usr/bin/env python3
"""
Advanced usage examples for FlowPrep ML library
"""

import pandas as pd
import numpy as np
import flowprep_ml
from flowprep_ml import PreprocessingOptions

def create_complex_dataset():
    """Create a complex dataset with various data types and issues"""
    np.random.seed(42)
    
    # Create a more complex dataset
    n_samples = 200
    
    data = {
        # Numeric features with different distributions
        'age': np.random.normal(35, 12, n_samples),
        'salary': np.random.lognormal(10, 0.5, n_samples),
        'experience': np.random.exponential(5, n_samples),
        'score': np.random.beta(2, 5, n_samples) * 100,
        
        # Categorical features
        'department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing', 'Sales'], n_samples),
        'education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_samples),
        'level': np.random.choice(['Junior', 'Mid', 'Senior', 'Lead'], n_samples),
        'status': np.random.choice(['Active', 'Inactive', 'Pending'], n_samples),
        
        # Binary features
        'is_manager': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'has_certification': np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
    }
    
    df = pd.DataFrame(data)
    
    # Add missing values strategically
    missing_indices = np.random.choice(n_samples, 20, replace=False)
    df.loc[missing_indices[:10], 'age'] = np.nan
    df.loc[missing_indices[10:15], 'salary'] = np.nan
    df.loc[missing_indices[15:20], 'department'] = np.nan
    
    # Add outliers
    df.loc[0, 'salary'] = df['salary'].quantile(0.99) * 3  # High outlier
    df.loc[1, 'age'] = 100  # Age outlier
    df.loc[2, 'score'] = -50  # Negative score outlier
    
    return df

def demonstrate_imputation_methods():
    """Demonstrate different imputation methods"""
    print("🔧 Imputation Methods Comparison")
    print("=" * 50)
    
    # Create data with missing values
    data = pd.DataFrame({
        'numeric1': [1, 2, np.nan, 4, 5, np.nan, 7, 8],
        'numeric2': [10, np.nan, 30, 40, np.nan, 60, 70, 80],
        'categorical': ['A', 'B', np.nan, 'A', 'C', np.nan, 'B', 'C']
    })
    
    data.to_csv('imputation_test.csv', index=False)
    
    methods = ['mean', 'median', 'mode', 'drop']
    
    for method in methods:
        print(f"\n📊 Method: {method.upper()}")
        print("-" * 20)
        
        result = flowprep_ml.preprocess(
            'imputation_test.csv',
            imputation_method=method,
            save_processed=False
        )
        
        print(f"Original shape: {result['original_shape']}")
        print(f"Processed shape: {result['processed_shape']}")
        print("Log entries:")
        for log in result['preprocessing_log']:
            print(f"  - {log}")
    
    # Clean up
    import os
    os.remove('imputation_test.csv')

def demonstrate_scaling_methods():
    """Demonstrate different scaling methods"""
    print("\n📏 Scaling Methods Comparison")
    print("=" * 50)
    
    # Create data with different scales
    data = pd.DataFrame({
        'small_values': np.random.normal(0, 1, 100),
        'large_values': np.random.normal(1000, 100, 100),
        'mixed_range': np.random.uniform(0, 10, 100)
    })
    
    data.to_csv('scaling_test.csv', index=False)
    
    methods = ['minmax', 'standard', 'robust']
    
    for method in methods:
        print(f"\n📊 Method: {method.upper()}")
        print("-" * 20)
        
        result = flowprep_ml.preprocess(
            'scaling_test.csv',
            scaling_method=method,
            save_processed=False
        )
        
        train_data = result['train_data']
        print(f"Scaled data statistics:")
        print(f"  Small values: mean={train_data['small_values'].mean():.3f}, std={train_data['small_values'].std():.3f}")
        print(f"  Large values: mean={train_data['large_values'].mean():.3f}, std={train_data['large_values'].std():.3f}")
        print(f"  Mixed range: mean={train_data['mixed_range'].mean():.3f}, std={train_data['mixed_range'].std():.3f}")
    
    # Clean up
    import os
    os.remove('scaling_test.csv')

def demonstrate_encoding_methods():
    """Demonstrate different encoding methods"""
    print("\n🏷️ Encoding Methods Comparison")
    print("=" * 50)
    
    # Create data with categorical variables
    data = pd.DataFrame({
        'category1': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B'],
        'category2': ['X', 'Y', 'Z', 'X', 'Y', 'Z', 'X', 'Y'],
        'numeric': [1, 2, 3, 4, 5, 6, 7, 8]
    })
    
    data.to_csv('encoding_test.csv', index=False)
    
    methods = ['onehot', 'label']
    
    for method in methods:
        print(f"\n📊 Method: {method.upper()}")
        print("-" * 20)
        
        result = flowprep_ml.preprocess(
            'encoding_test.csv',
            encoding_method=method,
            save_processed=False
        )
        
        train_data = result['train_data']
        print(f"Encoded data shape: {train_data.shape}")
        print(f"Columns: {list(train_data.columns)}")
    
    # Clean up
    import os
    os.remove('encoding_test.csv')

def demonstrate_outlier_removal():
    """Demonstrate outlier removal methods"""
    print("\n🎯 Outlier Removal Methods")
    print("=" * 50)
    
    # Create data with outliers
    data = pd.DataFrame({
        'normal_data': np.random.normal(0, 1, 100),
        'data_with_outliers': np.concatenate([
            np.random.normal(0, 1, 95),
            np.random.normal(0, 1, 5) * 5  # Outliers
        ])
    })
    
    data.to_csv('outlier_test.csv', index=False)
    
    methods = ['iqr', 'zscore']
    
    for method in methods:
        print(f"\n📊 Method: {method.upper()}")
        print("-" * 20)
        
        result = flowprep_ml.preprocess(
            'outlier_test.csv',
            remove_outliers=True,
            outlier_method=method,
            save_processed=False
        )
        
        print(f"Original shape: {result['original_shape']}")
        print(f"Processed shape: {result['processed_shape']}")
        print("Log entries:")
        for log in result['preprocessing_log']:
            if 'outlier' in log.lower():
                print(f"  - {log}")
    
    # Clean up
    import os
    os.remove('outlier_test.csv')

def demonstrate_custom_options():
    """Demonstrate using PreprocessingOptions class"""
    print("\n⚙️ Custom PreprocessingOptions")
    print("=" * 50)
    
    # Create complex dataset
    data = create_complex_dataset()
    data.to_csv('complex_data.csv', index=False)
    
    # Create custom options
    options = PreprocessingOptions(
        imputation_method='median',
        scaling_method='robust',
        encoding_method='onehot',
        remove_outliers=True,
        outlier_method='iqr',
        test_size=0.25,
        random_state=42,
        output_format='excel',
        save_processed=True
    )
    
    print("Custom options:")
    print(options)
    print()
    
    # Apply preprocessing
    result = flowprep_ml.preprocess('complex_data.csv', **options.to_dict())
    
    print("✅ Preprocessing completed!")
    print(f"Original shape: {result['original_shape']}")
    print(f"Processed shape: {result['processed_shape']}")
    print(f"Train shape: {result['train_shape']}")
    print(f"Test shape: {result['test_shape']}")
    print(f"Output file: {result['output_path']}")
    print()
    
    print("📝 Preprocessing log:")
    for i, log in enumerate(result['preprocessing_log'], 1):
        print(f"{i:2d}. {log}")
    
    # Clean up
    import os
    os.remove('complex_data.csv')
    if os.path.exists(result['output_path']):
        os.remove(result['output_path'])

def demonstrate_performance():
    """Demonstrate performance with larger dataset"""
    print("\n⚡ Performance Test")
    print("=" * 50)
    
    # Create larger dataset
    print("Creating large dataset...")
    n_samples = 10000
    
    data = pd.DataFrame({
        'feature1': np.random.normal(0, 1, n_samples),
        'feature2': np.random.normal(5, 2, n_samples),
        'feature3': np.random.exponential(1, n_samples),
        'category1': np.random.choice(['A', 'B', 'C', 'D', 'E'], n_samples),
        'category2': np.random.choice(['X', 'Y', 'Z'], n_samples),
        'binary': np.random.choice([0, 1], n_samples)
    })
    
    # Add some missing values
    missing_indices = np.random.choice(n_samples, 100, replace=False)
    data.loc[missing_indices, 'feature1'] = np.nan
    
    data.to_csv('large_dataset.csv', index=False)
    print(f"Created dataset with {data.shape[0]} rows and {data.shape[1]} columns")
    
    # Time the preprocessing
    import time
    start_time = time.time()
    
    result = flowprep_ml.preprocess(
        'large_dataset.csv',
        imputation_method='mean',
        scaling_method='standard',
        encoding_method='onehot',
        remove_outliers=True,
        test_size=0.2
    )
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"✅ Preprocessing completed in {processing_time:.2f} seconds")
    print(f"Processed {result['processed_shape'][0]} rows, {result['processed_shape'][1]} columns")
    print(f"Train: {result['train_shape'][0]} rows, Test: {result['test_shape'][0]} rows")
    
    # Clean up
    import os
    os.remove('large_dataset.csv')
    if os.path.exists(result['output_path']):
        os.remove(result['output_path'])

def main():
    """Main demonstration function"""
    print("🚀 FlowPrep ML - Advanced Usage Examples")
    print("=" * 60)
    
    try:
        # Demonstrate different aspects
        demonstrate_imputation_methods()
        demonstrate_scaling_methods()
        demonstrate_encoding_methods()
        demonstrate_outlier_removal()
        demonstrate_custom_options()
        demonstrate_performance()
        
        print("\n🎉 All advanced examples completed successfully!")
        print("\n📚 Key Takeaways:")
        print("  • FlowPrep ML handles various data types and issues automatically")
        print("  • Multiple preprocessing options are available for fine-tuning")
        print("  • The library scales well with larger datasets")
        print("  • PreprocessingOptions class provides structured configuration")
        print("  • Comprehensive logging helps track preprocessing steps")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
