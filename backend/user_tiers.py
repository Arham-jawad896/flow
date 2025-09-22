from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from database import User, UsageStats, Dataset
from config import settings
import logging

logger = logging.getLogger(__name__)

class UserTierManager:
    """Manages user tier limits and usage tracking."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_dataset_upload_limit(self, user: User) -> Dict[str, Any]:
        """Check if user can upload another dataset this month."""
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Get or create usage stats for current month
        usage_stats = self._get_or_create_usage_stats(user.id, current_month, current_year)
        
        # No limits - everything is free!
        return {
            'can_upload': True,
            'remaining': -1,  # Unlimited
            'limit': -1,
            'used': usage_stats.datasets_uploaded
        }
    
    def check_file_size_limit(self, file_size: int, user: User) -> Dict[str, Any]:
        """Check if file size is within limits."""
        max_size = settings.max_file_size  # 500MB for everyone
        
        return {
            'within_limit': file_size <= max_size,
            'file_size': file_size,
            'max_size': max_size,
            'tier': 'free'  # Everyone is free now!
        }
    
    def check_row_limit(self, row_count: int, user: User) -> Dict[str, Any]:
        """Check if CSV row count is within limits."""
        max_rows = settings.max_rows  # 1M rows for everyone
        
        return {
            'within_limit': row_count <= max_rows,
            'row_count': row_count,
            'max_rows': max_rows,
            'tier': 'free'  # Everyone is free now!
        }
    
    def check_api_limit(self, user: User) -> Dict[str, Any]:
        """Check if user can make another API call this month."""
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        usage_stats = self._get_or_create_usage_stats(user.id, current_month, current_year)
        
        # No limits - everything is free!
        return {
            'can_call': True,
            'remaining': -1,  # Unlimited
            'limit': -1,
            'used': usage_stats.api_calls_made
        }
    
    def record_dataset_upload(self, user: User, file_size: int) -> None:
        """Record a dataset upload in usage stats."""
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        usage_stats = self._get_or_create_usage_stats(user.id, current_month, current_year)
        usage_stats.datasets_uploaded += 1
        usage_stats.total_file_size += file_size
        
        self.db.commit()
        logger.info(f"Recorded dataset upload for user {user.id}: {file_size} bytes")
    
    def record_api_call(self, user: User) -> None:
        """Record an API call in usage stats."""
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        usage_stats = self._get_or_create_usage_stats(user.id, current_month, current_year)
        usage_stats.api_calls_made += 1
        
        self.db.commit()
        logger.info(f"Recorded API call for user {user.id}")
    
    def get_usage_summary(self, user: User) -> Dict[str, Any]:
        """Get comprehensive usage summary for user."""
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        usage_stats = self._get_or_create_usage_stats(user.id, current_month, current_year)
        
        # Get total datasets count
        total_datasets = self.db.query(Dataset).filter(Dataset.user_id == user.id).count()
        
        # Get total file size
        total_size = self.db.query(Dataset).filter(Dataset.user_id == user.id).with_entities(
            Dataset.file_size
        ).all()
        total_file_size = sum(size[0] for size in total_size)
        
        return {
            'tier': 'free',  # Everyone is free now!
            'current_month': {
                'datasets_uploaded': usage_stats.datasets_uploaded,
                'api_calls_made': usage_stats.api_calls_made,
                'total_file_size': usage_stats.total_file_size
            },
            'total': {
                'datasets': total_datasets,
                'total_file_size': total_file_size
            },
            'limits': self._get_tier_limits(user.is_premium)
        }
    
    def _get_or_create_usage_stats(self, user_id: int, month: int, year: int) -> UsageStats:
        """Get or create usage stats for a user and month."""
        usage_stats = self.db.query(UsageStats).filter(
            UsageStats.user_id == user_id,
            UsageStats.month == month,
            UsageStats.year == year
        ).first()
        
        if not usage_stats:
            usage_stats = UsageStats(
                user_id=user_id,
                month=month,
                year=year
            )
            self.db.add(usage_stats)
            self.db.commit()
            self.db.refresh(usage_stats)
        
        return usage_stats
    
    def _get_tier_limits(self, is_premium: bool) -> Dict[str, Any]:
        """Get limits - everything is free now!"""
        return {
            'datasets_per_month': -1,  # Unlimited
            'max_file_size': settings.max_file_size,  # 500MB
            'max_rows': settings.max_rows,  # 1M rows
            'api_calls_per_month': -1,  # Unlimited
            'features': [
                'unlimited_datasets',
                'unlimited_file_size',
                'unlimited_rows',
                'unlimited_api_calls',
                'custom_preprocessing',
                'data_augmentation',
                'feature_engineering',
                'outlier_removal',
                'advanced_scaling',
                'model_training',
                'hyperparameter_tuning'
            ]
        }
    
    def upgrade_user_to_premium(self, user: User) -> bool:
        """Upgrade user to premium tier."""
        try:
            user.is_premium = True
            self.db.commit()
            logger.info(f"User {user.id} upgraded to premium")
            return True
        except Exception as e:
            logger.error(f"Error upgrading user {user.id} to premium: {str(e)}")
            self.db.rollback()
            return False
    
    def downgrade_user_to_free(self, user: User) -> bool:
        """Downgrade user to free tier."""
        try:
            user.is_premium = False
            self.db.commit()
            logger.info(f"User {user.id} downgraded to free")
            return True
        except Exception as e:
            logger.error(f"Error downgrading user {user.id} to free: {str(e)}")
            self.db.rollback()
            return False

def validate_user_limits(user: User, file_size: int, db: Session, row_count: Optional[int] = None) -> Dict[str, Any]:
    """Validate all user limits for a file upload."""
    tier_manager = UserTierManager(db)
    
    # Check file size limit (only real limit now)
    size_check = tier_manager.check_file_size_limit(file_size, user)
    if not size_check['within_limit']:
        return {
            'valid': False,
            'error': 'file_size_exceeded',
            'message': f"File size ({file_size} bytes) exceeds the maximum limit of {size_check['max_size']} bytes (500MB)."
        }
    
    # Check row limit for CSV files (only real limit now)
    if row_count is not None:
        row_check = tier_manager.check_row_limit(row_count, user)
        if not row_check['within_limit']:
            return {
                'valid': False,
                'error': 'row_limit_exceeded',
                'message': f"Dataset has {row_count} rows, which exceeds the maximum limit of {row_check['max_rows']} rows (1M rows)."
            }
    
    return {
        'valid': True,
        'message': 'All limits satisfied'
    }
