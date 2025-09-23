import os
import uuid
import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from datetime import datetime
from database import Dataset, PreprocessingJob, User
from preprocessing import DataPreprocessor, get_file_type, validate_file_size, validate_csv_rows
from user_tiers import UserTierManager, validate_user_limits
from schemas import PreprocessingOptions
import logging

logger = logging.getLogger(__name__)

class DatasetManager:
    """Manages dataset operations including upload, processing, and retrieval."""
    
    def __init__(self, db: Session):
        self.db = db
        self.tier_manager = UserTierManager(db)
    
    async def upload_dataset(
        self, 
        file: UploadFile, 
        user: User, 
        dataset_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload and validate a dataset file."""
        try:
            # Validate file size
            file_content = await file.read()
            file_size = len(file_content)
            
            # Check user limits
            limits_check = validate_user_limits(user, file_size, self.db)
            if not limits_check['valid']:
                raise HTTPException(
                    status_code=400,
                    detail=limits_check['message']
                )
            
            # Determine file type
            file_type = get_file_type(file.filename)
            if file_type == 'unknown':
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file type. Supported types: CSV, XLS, XLSX"
                )
            
            # For tabular files (CSV or Excel), check row/column counts by parsing
            if file_type == 'csv':
                try:
                    import io
                    suffix = Path(file.filename).suffix.lower()
                    if suffix in ['.xlsx', '.xls']:
                        # Excel files
                        df = pd.read_excel(io.BytesIO(file_content))
                    else:
                        # CSV files
                        df = pd.read_csv(io.BytesIO(file_content))
                    if df is None or df.empty:
                        raise ValueError("File contains no rows after parsing")
                    row_count = len(df)
                    
                    # Check row limit
                    row_check = self.tier_manager.check_row_limit(row_count, user)
                    if not row_check['within_limit']:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Row count ({row_count}) exceeds the maximum allowed ({row_check['max_rows']})."
                        )
                    
                    columns_count = len(df.columns)
                    if columns_count == 0:
                        raise ValueError("No columns detected. Ensure the file has a header row.")
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid tabular file: {str(e)}"
                    )
            else:
                row_count = None
                columns_count = None
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = Path(file.filename).suffix
            unique_filename = f"{file_id}{file_extension}"
            file_path = os.path.join("data", unique_filename)
            
            # Save file
            os.makedirs("data", exist_ok=True)
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            # Create dataset record
            dataset = Dataset(
                name=dataset_name or Path(file.filename).stem,
                original_filename=file.filename,
                file_path=file_path,
                file_type=file_type,
                file_size=file_size,
                rows_count=row_count,
                columns_count=columns_count,
                user_id=user.id
            )
            
            self.db.add(dataset)
            self.db.commit()
            self.db.refresh(dataset)
            
            # Record usage
            self.tier_manager.record_dataset_upload(user, file_size)
            
            logger.info(f"Dataset uploaded successfully: {dataset.id} by user {user.id}")
            
            return {
                'success': True,
                'dataset_id': dataset.id,
                'dataset_name': dataset.name,
                'file_type': file_type,
                'file_size': file_size,
                'rows_count': row_count,
                'columns_count': columns_count,
                'message': 'Dataset uploaded successfully'
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading dataset: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error uploading dataset: {str(e)}"
            )
    
    def get_user_datasets(self, user: User, limit: int = 50, offset: int = 0) -> List[Dataset]:
        """Get datasets for a user with pagination."""
        return self.db.query(Dataset).filter(
            Dataset.user_id == user.id
        ).order_by(Dataset.created_at.desc()).offset(offset).limit(limit).all()
    
    def get_dataset_by_id(self, dataset_id: int, user: User) -> Optional[Dataset]:
        """Get a specific dataset by ID, ensuring user ownership."""
        dataset = self.db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.user_id == user.id
        ).first()
        
        if not dataset:
            raise HTTPException(
                status_code=404,
                detail="Dataset not found"
            )
        
        return dataset
    
    def delete_dataset(self, dataset_id: int, user: User) -> bool:
        """Delete a dataset and its associated files."""
        try:
            dataset = self.get_dataset_by_id(dataset_id, user)
            
            # Delete related preprocessing jobs to avoid FK constraint issues
            self.db.query(PreprocessingJob).filter(
                PreprocessingJob.dataset_id == dataset.id
            ).delete(synchronize_session=False)

            # Delete physical files
            if os.path.exists(dataset.file_path):
                os.remove(dataset.file_path)
            
            if dataset.processed_file_path and os.path.exists(dataset.processed_file_path):
                os.remove(dataset.processed_file_path)
            
            # Delete from database
            self.db.delete(dataset)
            self.db.commit()
            
            logger.info(f"Dataset {dataset_id} deleted by user {user.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting dataset {dataset_id}: {str(e)}")
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting dataset: {str(e)}"
            )
    
    def start_preprocessing(
        self, 
        dataset_id: int, 
        user: User, 
        options: Optional[PreprocessingOptions] = None
    ) -> Dict[str, Any]:
        """Start preprocessing a dataset."""
        try:
            dataset = self.get_dataset_by_id(dataset_id, user)
            
            if dataset.preprocessing_status == "processing":
                raise HTTPException(
                    status_code=400,
                    detail="Dataset is already being processed"
                )
            
            # Create preprocessing job
            job = PreprocessingJob(
                dataset_id=dataset_id,
                status="pending",
                preprocessing_options=options.json() if options else "{}"
            )
            
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
            
            # Update dataset status
            dataset.preprocessing_status = "processing"
            self.db.commit()
            
            # Start preprocessing in background (in production, use Celery or similar)
            self._process_dataset_async(dataset, job, options, user.is_premium)
            
            return {
                'success': True,
                'job_id': job.id,
                'message': 'Preprocessing started'
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error starting preprocessing: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error starting preprocessing: {str(e)}"
            )
    
    def _process_dataset_async(
        self, 
        dataset: Dataset, 
        job: PreprocessingJob, 
        options: Optional[PreprocessingOptions], 
        is_premium: bool
    ):
        """Process dataset asynchronously."""
        try:
            # Update job status
            job.status = "processing"
            job.progress = 0.1
            self.db.commit()
            
            # Initialize preprocessor
            preprocessor_options = {}
            if options:
                preprocessor_options = options.dict()
            
            preprocessor = DataPreprocessor(preprocessor_options)
            
            # Process based on file type
            if dataset.file_type == "csv":
                result = preprocessor.preprocess_csv(dataset.file_path)
            elif dataset.file_type == "image":
                result = preprocessor.preprocess_images([dataset.file_path])
            elif dataset.file_type == "text":
                result = preprocessor.preprocess_text(dataset.file_path)
            else:
                raise ValueError(f"Unsupported file type: {dataset.file_type}")
            
            # Update job progress
            job.progress = 0.9
            self.db.commit()
            
            if result['success']:
                # Update dataset with processed file path
                if 'processed_file_path' in result:
                    dataset.processed_file_path = result['processed_file_path']
                
                dataset.preprocessing_status = "completed"
                dataset.preprocessing_log = "\n".join(result.get('preprocessing_log', []))
                
                # Update job
                job.status = "completed"
                job.progress = 1.0
                job.completed_at = datetime.utcnow()
                
                logger.info(f"Preprocessing completed for dataset {dataset.id}")
            else:
                # Handle preprocessing failure
                dataset.preprocessing_status = "failed"
                dataset.preprocessing_log = result.get('error', 'Unknown error')
                
                job.status = "failed"
                job.error_message = result.get('error', 'Unknown error')
                job.completed_at = datetime.utcnow()
                
                logger.error(f"Preprocessing failed for dataset {dataset.id}: {result.get('error')}")
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error in async preprocessing: {str(e)}")
            
            # Update job and dataset status
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            
            dataset.preprocessing_status = "failed"
            dataset.preprocessing_log = str(e)
            
            self.db.commit()
    
    def get_preprocessing_status(self, dataset_id: int, user: User) -> Dict[str, Any]:
        """Get preprocessing status for a dataset."""
        dataset = self.get_dataset_by_id(dataset_id, user)
        
        # Get latest preprocessing job
        job = self.db.query(PreprocessingJob).filter(
            PreprocessingJob.dataset_id == dataset_id
        ).order_by(PreprocessingJob.created_at.desc()).first()
        
        return {
            'dataset_id': dataset_id,
            'status': dataset.preprocessing_status,
            'progress': job.progress if job else 0.0,
            'error_message': job.error_message if job else None,
            'preprocessing_log': dataset.preprocessing_log,
            'created_at': job.created_at if job else None,
            'completed_at': job.completed_at if job else None
        }
    
    def download_dataset(self, dataset_id: int, user: User, processed: bool = False) -> str:
        """Get file path for dataset download."""
        dataset = self.get_dataset_by_id(dataset_id, user)
        
        if processed and dataset.processed_file_path:
            if os.path.exists(dataset.processed_file_path):
                return dataset.processed_file_path
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Processed file not found"
                )
        else:
            if os.path.exists(dataset.file_path):
                return dataset.file_path
            else:
                raise HTTPException(
                    status_code=404,
                    detail="Original file not found"
                )
    
    def get_dataset_summary(self, dataset_id: int, user: User) -> Dict[str, Any]:
        """Get comprehensive dataset summary."""
        dataset = self.get_dataset_by_id(dataset_id, user)
        
        # Get preprocessing job info
        job = self.db.query(PreprocessingJob).filter(
            PreprocessingJob.dataset_id == dataset_id
        ).order_by(PreprocessingJob.created_at.desc()).first()
        
        return {
            'id': dataset.id,
            'name': dataset.name,
            'original_filename': dataset.original_filename,
            'file_type': dataset.file_type,
            'file_size': dataset.file_size,
            'rows_count': dataset.rows_count,
            'columns_count': dataset.columns_count,
            'preprocessing_status': dataset.preprocessing_status,
            'preprocessing_log': dataset.preprocessing_log,
            'created_at': dataset.created_at,
            'updated_at': dataset.updated_at,
            'has_processed_file': bool(dataset.processed_file_path),
            'latest_job': {
                'id': job.id if job else None,
                'status': job.status if job else None,
                'progress': job.progress if job else None,
                'error_message': job.error_message if job else None,
                'created_at': job.created_at if job else None,
                'completed_at': job.completed_at if job else None
            } if job else None
        }

    def preprocess_dataset_advanced(
        self, 
        dataset: Dataset,
        imputation_method: str = "mean",
        scaling_method: str = "minmax", 
        encoding_method: str = "onehot",
        remove_outliers: bool = False,
        outlier_method: str = "iqr",
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """Preprocess a dataset with advanced custom options."""
        try:
            # Create preprocessing job
            job = PreprocessingJob(
                dataset_id=dataset.id,
                status='processing'
            )
            self.db.add(job)
            self.db.commit()
            
            # Store preprocessing options
            options = {
                'imputation_method': imputation_method,
                'scaling_method': scaling_method,
                'encoding_method': encoding_method,
                'remove_outliers': remove_outliers,
                'outlier_method': outlier_method,
                'test_size': test_size
            }
            dataset.preprocessing_options = str(options)
            
            # Run advanced preprocessing
            from preprocessing import AdvancedDataPreprocessor
            preprocessor = AdvancedDataPreprocessor()
            result = preprocessor.preprocess_file_advanced(
                dataset.file_path,
                dataset.file_type,
                output_path=dataset.file_path.replace('.csv', '_processed.csv'),
                imputation_method=imputation_method,
                scaling_method=scaling_method,
                encoding_method=encoding_method,
                remove_outliers=remove_outliers,
                outlier_method=outlier_method,
                test_size=test_size
            )
            
            if result['success']:
                # Update dataset
                dataset.preprocessing_status = 'completed'
                dataset.processed_file_path = result['output_path']
                dataset.preprocessing_log = result.get('log', '')
                dataset.rows_count = result.get('rows_count', 0)
                dataset.columns_count = result.get('columns_count', 0)
                
                # Update job
                job.status = 'completed'
                job.completed_at = datetime.utcnow()
                job.log = result.get('log', '')
                
                self.db.commit()
                
                logger.info(f"Dataset {dataset.id} preprocessed with advanced options successfully")
                return {
                    'success': True,
                    'message': 'Dataset preprocessed with advanced options successfully',
                    'job_id': job.id,
                    'output_path': result['output_path'],
                    'rows_count': result.get('rows_count', 0),
                    'columns_count': result.get('columns_count', 0),
                    'options_used': options
                }
            else:
                # Update job
                job.status = 'failed'
                job.completed_at = datetime.utcnow()
                job.log = result.get('error', 'Unknown error')
                
                # Update dataset
                dataset.preprocessing_status = 'failed'
                dataset.preprocessing_log = result.get('error', 'Unknown error')
                
                self.db.commit()
                
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"Error preprocessing dataset {dataset.id} with advanced options: {str(e)}")
            
            # Update job
            if 'job' in locals():
                job.status = 'failed'
                job.completed_at = datetime.utcnow()
                job.log = str(e)
            
            # Update dataset
            dataset.preprocessing_status = 'failed'
            dataset.preprocessing_log = str(e)
            
            self.db.commit()
            
            return {
                'success': False,
                'error': str(e)
            }
