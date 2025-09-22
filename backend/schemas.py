from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class UserTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"

class FileType(str, Enum):
    CSV = "csv"
    IMAGE = "image"
    TEXT = "text"

class PreprocessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_premium: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

# Dataset schemas
class DatasetBase(BaseModel):
    name: str

class DatasetCreate(DatasetBase):
    pass

class DatasetResponse(DatasetBase):
    id: int
    original_filename: str
    file_type: FileType
    file_size: int
    rows_count: Optional[int]
    columns_count: Optional[int]
    preprocessing_status: PreprocessingStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DatasetSummary(BaseModel):
    id: int
    name: str
    file_type: FileType
    file_size: int
    rows_count: Optional[int]
    columns_count: Optional[int]
    preprocessing_status: PreprocessingStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

# Preprocessing schemas
class PreprocessingOptions(BaseModel):
    scaling_method: Optional[str] = "minmax"  # minmax, standard, robust
    missing_value_strategy: Optional[str] = "mean"  # mean, median, mode
    outlier_removal: Optional[bool] = False
    data_augmentation: Optional[bool] = False
    train_test_split: Optional[float] = 0.8
    feature_engineering: Optional[bool] = False

class PreprocessingJobResponse(BaseModel):
    id: int
    status: JobStatus
    progress: float
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# API Key schemas
class APIKeyCreate(BaseModel):
    name: str

class APIKeyResponse(BaseModel):
    id: int
    key: str
    name: str
    is_active: bool
    created_at: datetime
    last_used: Optional[datetime]
    
    class Config:
        from_attributes = True

# Usage stats schemas
class UsageStatsResponse(BaseModel):
    month: int
    year: int
    datasets_uploaded: int
    api_calls_made: int
    total_file_size: int
    
    class Config:
        from_attributes = True

# File upload schemas
class FileUploadResponse(BaseModel):
    message: str
    dataset_id: int
    file_info: dict

# Dashboard schemas
class DashboardResponse(BaseModel):
    user: UserResponse
    datasets: List[DatasetSummary]
    usage_stats: UsageStatsResponse
    recent_activity: List[dict]

# Error schemas
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

# Success schemas
class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None
