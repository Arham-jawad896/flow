from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
import logging
from datetime import datetime, timedelta
import secrets
import string

# Import our modules
from database import get_db, User
from auth import (
    authenticate_user, create_user, get_current_active_user, 
    create_access_token, get_password_hash
)
from schemas import (
    UserCreate, UserLogin, UserResponse, Token, DatasetResponse, 
    DatasetCreate, PreprocessingOptions, PreprocessingJobResponse,
    UsageStatsResponse, DashboardResponse,
    SuccessResponse, ErrorResponse
)
from dataset_manager import DatasetManager
from user_tiers import UserTierManager
# Model training removed - focus on preprocessing only
# LLM integration removed for MVP
from error_handlers import (
    setup_logging, FlowException, flow_exception_handler,
    http_exception_handler, validation_exception_handler,
    sqlalchemy_exception_handler, general_exception_handler,
    rate_limit_middleware, log_authentication_attempt
)
from config import settings

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Flow ML Backend - End-to-End ML Autopilot",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add exception handlers
app.add_exception_handler(FlowException, flow_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Security
security = HTTPBearer()

# Root endpoint
@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Flow ML Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

# Health check
@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        user = create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        logger.info(f"New user registered: {user.email}")
        return UserResponse.from_orm(user)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@app.post("/auth/login", response_model=Token)
async def login(
    user_credentials: UserLogin, 
    request: Request,
    db: Session = Depends(get_db)
):
    """Login user and return access token."""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        log_authentication_attempt(user_credentials.email, False, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    log_authentication_attempt(user_credentials.email, True, request)
    logger.info(f"User logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return UserResponse.from_orm(current_user)

# Dataset endpoints
@app.post("/datasets/upload", response_model=dict)
async def upload_dataset(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a new dataset."""
    dataset_manager = DatasetManager(db)
    result = await dataset_manager.upload_dataset(file, current_user, dataset_name)
    return result

@app.get("/datasets", response_model=List[DatasetResponse])
async def get_datasets(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's datasets with pagination."""
    dataset_manager = DatasetManager(db)
    datasets = dataset_manager.get_user_datasets(current_user, limit, offset)
    return datasets

@app.get("/datasets/{dataset_id}", response_model=dict)
async def get_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific dataset details."""
    dataset_manager = DatasetManager(db)
    return dataset_manager.get_dataset_summary(dataset_id, current_user)

@app.delete("/datasets/{dataset_id}", response_model=SuccessResponse)
async def delete_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a dataset."""
    dataset_manager = DatasetManager(db)
    success = dataset_manager.delete_dataset(dataset_id, current_user)
    if success:
        return SuccessResponse(message="Dataset deleted successfully")
    else:
        raise HTTPException(status_code=500, detail="Failed to delete dataset")

@app.post("/datasets/{dataset_id}/preprocess", response_model=dict)
async def start_preprocessing(
    dataset_id: int,
    options: Optional[PreprocessingOptions] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start preprocessing a dataset."""
    dataset_manager = DatasetManager(db)
    result = dataset_manager.start_preprocessing(dataset_id, current_user, options)
    return result

@app.get("/datasets/{dataset_id}/preprocessing-status", response_model=dict)
async def get_preprocessing_status(
    dataset_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get preprocessing status for a dataset."""
    dataset_manager = DatasetManager(db)
    return dataset_manager.get_preprocessing_status(dataset_id, current_user)

@app.get("/datasets/{dataset_id}/download")
async def download_dataset(
    dataset_id: int,
    processed: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download a dataset file."""
    from fastapi.responses import FileResponse
    import os
    
    dataset_manager = DatasetManager(db)
    file_path = dataset_manager.download_dataset(dataset_id, current_user, processed)
    
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type='application/octet-stream'
        )
    else:
        raise HTTPException(status_code=404, detail="File not found")

# User management endpoints
@app.get("/user/usage", response_model=dict)
async def get_usage_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user usage statistics."""
    tier_manager = UserTierManager(db)
    return tier_manager.get_usage_summary(current_user)

# API key functionality removed for MVP (library handles access)

# Dashboard endpoint
@app.get("/dashboard", response_model=dict)
async def get_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard data for the user."""
    dataset_manager = DatasetManager(db)
    tier_manager = UserTierManager(db)
    
    # Get recent datasets
    datasets = dataset_manager.get_user_datasets(current_user, limit=10)
    
    # Get usage stats
    usage_stats = tier_manager.get_usage_summary(current_user)
    
    # Get recent activity (simplified)
    recent_activity = []
    for dataset in datasets[:5]:
        recent_activity.append({
            "type": "dataset_upload",
            "description": f"Uploaded {dataset.name}",
            "timestamp": dataset.created_at.isoformat(),
            "status": dataset.preprocessing_status
        })
    
    # Convert datasets to response format
    datasets_response = []
    for dataset in datasets:
        datasets_response.append({
            "id": dataset.id,
            "name": dataset.name,
            "original_filename": dataset.original_filename,
            "file_type": dataset.file_type,
            "file_size": dataset.file_size,
            "rows_count": dataset.rows_count,
            "columns_count": dataset.columns_count,
            "preprocessing_status": dataset.preprocessing_status,
            "preprocessing_options": dataset.preprocessing_options,
            "created_at": dataset.created_at.isoformat(),
            "updated_at": dataset.updated_at.isoformat()
        })
    
    return {
        "user": UserResponse.from_orm(current_user),
        "datasets": datasets_response,
        "usage_stats": usage_stats,
        "recent_activity": recent_activity
    }

# External API preprocess endpoint removed for MVP

# Advanced preprocessing options endpoint
@app.post("/datasets/{dataset_id}/preprocess-advanced", response_model=dict)
async def preprocess_advanced(
    dataset_id: int,
    imputation_method: str = Form("mean"),
    scaling_method: str = Form("minmax"),
    encoding_method: str = Form("onehot"),
    remove_outliers: bool = Form(False),
    outlier_method: str = Form("iqr"),
    test_size: float = Form(0.2),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Advanced preprocessing with custom options."""
    dataset_manager = DatasetManager(db)
    dataset = dataset_manager.get_dataset_by_id(dataset_id, current_user)
    
    if dataset.preprocessing_status == 'processing':
        raise HTTPException(
            status_code=400,
            detail="Dataset is already being processed"
        )
    
    # Update dataset status
    dataset.preprocessing_status = 'processing'
    db.commit()
    
    try:
        # Run advanced preprocessing
        preprocessing_result = dataset_manager.preprocess_dataset_advanced(
            dataset, 
            imputation_method=imputation_method,
            scaling_method=scaling_method,
            encoding_method=encoding_method,
            remove_outliers=remove_outliers,
            outlier_method=outlier_method,
            test_size=test_size
        )
        
        return preprocessing_result
        
    except Exception as e:
        dataset.preprocessing_status = 'failed'
        dataset.preprocessing_log = str(e)
        db.commit()
        logger.error(f"Advanced preprocessing failed for dataset {dataset_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Advanced preprocessing failed: {str(e)}"
        )

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=settings.debug
    )
