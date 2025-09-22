"""
Flow ML Client for API communication
"""

import requests
import pandas as pd
from typing import Optional, Dict, Any, Union
import os

class FlowClient:
    """Client for Flow ML API"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "http://localhost:8003"):
        self.api_key = api_key or os.getenv('FLOW_API_KEY')
        self.base_url = base_url
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })
    
    def preprocess(
        self,
        file_path: str,
        imputation_method: str = "mean",
        scaling_method: str = "minmax",
        encoding_method: str = "onehot",
        remove_outliers: bool = False,
        outlier_method: str = "iqr",
        test_size: float = 0.2
    ) -> pd.DataFrame:
        """
        Preprocess a dataset using Flow ML API
        
        Args:
            file_path: Path to the CSV file
            imputation_method: Method for handling missing values (mean, median, mode, drop)
            scaling_method: Method for scaling numerical features (minmax, standard, robust)
            encoding_method: Method for encoding categorical variables (onehot, label)
            remove_outliers: Whether to remove outliers
            outlier_method: Method for outlier removal (iqr, zscore)
            test_size: Fraction of data to use for testing (0.0 to 1.0)
        
        Returns:
            Preprocessed pandas DataFrame
        """
        if not self.api_key:
            raise ValueError("API key is required. Set FLOW_API_KEY environment variable or pass api_key parameter.")
        
        # Upload file
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'dataset_name': os.path.basename(file_path)}
            response = self.session.post(f"{self.base_url}/datasets/upload", files=files, data=data)
        
        if response.status_code != 200:
            raise Exception(f"Upload failed: {response.text}")
        
        dataset_id = response.json()['id']
        
        # Start advanced preprocessing
        preprocessing_data = {
            'imputation_method': imputation_method,
            'scaling_method': scaling_method,
            'encoding_method': encoding_method,
            'remove_outliers': remove_outliers,
            'outlier_method': outlier_method,
            'test_size': test_size
        }
        
        response = self.session.post(f"{self.base_url}/datasets/{dataset_id}/preprocess-advanced", data=preprocessing_data)
        
        if response.status_code != 200:
            raise Exception(f"Preprocessing failed: {response.text}")
        
        # Wait for preprocessing to complete (in production, you'd poll the status)
        import time
        time.sleep(2)  # Simple wait - in production, implement proper polling
        
        # Download processed data
        response = self.session.get(f"{self.base_url}/datasets/{dataset_id}/download?processed=true")
        
        if response.status_code != 200:
            raise Exception(f"Download failed: {response.text}")
        
        # Save to temporary file and read as DataFrame
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as tmp_file:
            tmp_file.write(response.content)
            tmp_path = tmp_file.name
        
        try:
            df = pd.read_csv(tmp_path)
            return df
        finally:
            os.unlink(tmp_path)
    
    def get_api_keys(self) -> list:
        """Get all API keys for the user"""
        response = self.session.get(f"{self.base_url}/api-keys")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get API keys: {response.text}")
    
    def create_api_key(self, name: str) -> str:
        """Create a new API key"""
        response = self.session.post(f"{self.base_url}/api-keys", json={'name': name})
        if response.status_code == 200:
            return response.json()['key']
        else:
            raise Exception(f"Failed to create API key: {response.text}")
