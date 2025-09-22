import pandas as pd
import numpy as np
import pickle
import os
import logging
from typing import Dict, Any, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report, mean_absolute_error
from sklearn.preprocessing import LabelEncoder
import joblib

logger = logging.getLogger(__name__)

class ModelTrainer:
    """Handles model training for different types of datasets."""
    
    def __init__(self):
        self.models = {}
        self.results = {}
    
    def detect_task_type(self, df: pd.DataFrame, target_column: str = None) -> str:
        """Detect if the task is classification or regression."""
        if target_column is None:
            # Try to detect target column (last column or column with 'target' in name)
            possible_targets = [col for col in df.columns if 'target' in col.lower() or 'label' in col.lower()]
            if possible_targets:
                target_column = possible_targets[0]
            else:
                target_column = df.columns[-1]
        
        target_data = df[target_column]
        
        # Check if target is categorical (string or few unique values)
        if target_data.dtype == 'object' or target_data.nunique() < 10:
            return 'classification'
        else:
            return 'regression'
    
    def train_model(self, file_path: str, target_column: str = None, is_premium: bool = False) -> Dict[str, Any]:
        """Train a model on the dataset."""
        try:
            # Load the dataset
            df = pd.read_csv(file_path)
            
            if target_column is None:
                # Try to detect target column
                possible_targets = [col for col in df.columns if 'target' in col.lower() or 'label' in col.lower()]
                if possible_targets:
                    target_column = possible_targets[0]
                else:
                    target_column = df.columns[-1]
            
            # Separate features and target
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            # Detect task type
            task_type = self.detect_task_type(df, target_column)
            
            # Handle categorical target for classification
            if task_type == 'classification':
                le = LabelEncoder()
                y = le.fit_transform(y)
                self.label_encoder = le
            
            # Split the data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Select and train model based on task type and tier
            if task_type == 'classification':
                if is_premium:
                    # Premium: Use RandomForest with more trees
                    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
                else:
                    # Free: Use simpler LogisticRegression
                    model = LogisticRegression(random_state=42, max_iter=1000)
            else:  # regression
                if is_premium:
                    # Premium: Use RandomForest with more trees
                    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
                else:
                    # Free: Use LinearRegression
                    model = LinearRegression()
            
            # Train the model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            if task_type == 'classification':
                accuracy = accuracy_score(y_test, y_pred)
                metrics = {
                    'accuracy': accuracy,
                    'classification_report': classification_report(y_test, y_pred, output_dict=True)
                }
            else:  # regression
                mse = mean_squared_error(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                metrics = {
                    'mse': mse,
                    'mae': mae,
                    'rmse': rmse,
                    'r2_score': model.score(X_test, y_test)
                }
            
            # Cross-validation score
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy' if task_type == 'classification' else 'neg_mean_squared_error')
            
            # Save the model
            model_path = file_path.replace('.csv', '_model.pkl')
            joblib.dump(model, model_path)
            
            # Save label encoder if classification
            if task_type == 'classification' and hasattr(self, 'label_encoder'):
                encoder_path = file_path.replace('.csv', '_encoder.pkl')
                joblib.dump(self.label_encoder, encoder_path)
            
            result = {
                'success': True,
                'task_type': task_type,
                'model_type': model.__class__.__name__,
                'target_column': target_column,
                'metrics': metrics,
                'cv_scores': {
                    'mean': cv_scores.mean(),
                    'std': cv_scores.std()
                },
                'model_path': model_path,
                'feature_importance': self._get_feature_importance(model, X.columns) if hasattr(model, 'feature_importances_') else None,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
            logger.info(f"Model training completed successfully: {result['model_type']} for {task_type}")
            return result
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_feature_importance(self, model, feature_names) -> Dict[str, float]:
        """Get feature importance from tree-based models."""
        if hasattr(model, 'feature_importances_'):
            importance_dict = dict(zip(feature_names, model.feature_importances_))
            # Sort by importance
            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        return None
    
    def predict(self, model_path: str, data: pd.DataFrame, encoder_path: str = None) -> Dict[str, Any]:
        """Make predictions using a trained model."""
        try:
            # Load the model
            model = joblib.load(model_path)
            
            # Make predictions
            predictions = model.predict(data)
            
            # Load and apply label encoder if classification
            if encoder_path and os.path.exists(encoder_path):
                encoder = joblib.load(encoder_path)
                predictions = encoder.inverse_transform(predictions)
            
            return {
                'success': True,
                'predictions': predictions.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
