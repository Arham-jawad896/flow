import logging
import traceback
from typing import Dict, Any
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import os
from datetime import datetime

# Configure logging
def setup_logging():
    """Set up comprehensive logging configuration."""
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/flow_backend.log'),
            logging.StreamHandler()
        ]
    )
    
    # Create specific loggers
    error_logger = logging.getLogger('error')
    error_logger.setLevel(logging.ERROR)
    error_handler = logging.FileHandler('logs/errors.log')
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    error_logger.addHandler(error_handler)
    
    # Security logger
    security_logger = logging.getLogger('security')
    security_logger.setLevel(logging.WARNING)
    security_handler = logging.FileHandler('logs/security.log')
    security_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    security_logger.addHandler(security_handler)
    
    # Performance logger
    performance_logger = logging.getLogger('performance')
    performance_logger.setLevel(logging.INFO)
    performance_handler = logging.FileHandler('logs/performance.log')
    performance_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    performance_logger.addHandler(performance_handler)

# Custom exception classes
class FlowException(Exception):
    """Base exception for Flow application."""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class DatasetException(FlowException):
    """Exception for dataset-related errors."""
    pass

class PreprocessingException(FlowException):
    """Exception for preprocessing-related errors."""
    pass

class UserTierException(FlowException):
    """Exception for user tier/limit-related errors."""
    pass

class AuthenticationException(FlowException):
    """Exception for authentication-related errors."""
    pass

class FileProcessingException(FlowException):
    """Exception for file processing errors."""
    pass

# Error response formatter
def format_error_response(
    error: Exception, 
    request: Request = None, 
    include_traceback: bool = False
) -> Dict[str, Any]:
    """Format error response for API."""
    
    error_id = f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(error)}"
    
    response = {
        "error": True,
        "error_id": error_id,
        "message": str(error),
        "timestamp": datetime.now().isoformat()
    }
    
    if hasattr(error, 'error_code') and error.error_code:
        response["error_code"] = error.error_code
    
    if hasattr(error, 'details') and error.details:
        response["details"] = error.details
    
    if request:
        response["path"] = str(request.url)
        response["method"] = request.method
    
    if include_traceback:
        response["traceback"] = traceback.format_exc()
    
    return response

# Global exception handlers
async def flow_exception_handler(request: Request, exc: FlowException):
    """Handle custom Flow exceptions."""
    logger = logging.getLogger('error')
    logger.error(f"Flow exception: {exc.message}", exc_info=True)
    
    status_code = status.HTTP_400_BAD_REQUEST
    
    # Set specific status codes based on error type
    if isinstance(exc, AuthenticationException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, UserTierException):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, DatasetException):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(exc, FileProcessingException):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    
    return JSONResponse(
        status_code=status_code,
        content=format_error_response(exc, request)
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger = logging.getLogger('error')
    logger.warning(f"HTTP exception: {exc.detail} - {request.url}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(exc, request)
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger = logging.getLogger('error')
    logger.warning(f"Validation error: {exc.errors()} - {request.url}")
    
    error_details = {
        "validation_errors": exc.errors(),
        "body": exc.body
    }
    
    response = format_error_response(exc, request)
    response["details"] = error_details
    response["message"] = "Request validation failed"
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors."""
    logger = logging.getLogger('error')
    logger.error(f"Database error: {str(exc)}", exc_info=True)
    
    if isinstance(exc, IntegrityError):
        message = "Database integrity constraint violation"
        error_code = "DB_INTEGRITY_ERROR"
    else:
        message = "Database operation failed"
        error_code = "DB_ERROR"
    
    response = format_error_response(
        FlowException(message, error_code), 
        request
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger = logging.getLogger('error')
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    response = format_error_response(exc, request)
    response["message"] = "An unexpected error occurred"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response
    )

# Security logging functions
def log_security_event(event_type: str, details: Dict[str, Any], request: Request = None):
    """Log security-related events."""
    security_logger = logging.getLogger('security')
    
    log_data = {
        "event_type": event_type,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    
    if request:
        log_data.update({
            "ip_address": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "path": str(request.url),
            "method": request.method
        })
    
    security_logger.warning(f"Security event: {log_data}")

def log_authentication_attempt(email: str, success: bool, request: Request = None):
    """Log authentication attempts."""
    event_type = "login_success" if success else "login_failed"
    details = {"email": email, "success": success}
    log_security_event(event_type, details, request)

def log_api_key_usage(api_key: str, endpoint: str, success: bool, request: Request = None):
    """Log API key usage."""
    event_type = "api_key_used" if success else "api_key_failed"
    details = {
        "api_key": api_key[:8] + "..." if len(api_key) > 8 else api_key,
        "endpoint": endpoint,
        "success": success
    }
    log_security_event(event_type, details, request)

def log_file_upload(filename: str, file_size: int, user_id: int, success: bool, request: Request = None):
    """Log file upload events."""
    event_type = "file_upload_success" if success else "file_upload_failed"
    details = {
        "filename": filename,
        "file_size": file_size,
        "user_id": user_id,
        "success": success
    }
    log_security_event(event_type, details, request)

# Performance logging
def log_performance_metric(operation: str, duration: float, details: Dict[str, Any] = None):
    """Log performance metrics."""
    performance_logger = logging.getLogger('performance')
    
    log_data = {
        "operation": operation,
        "duration_seconds": duration,
        "timestamp": datetime.now().isoformat()
    }
    
    if details:
        log_data.update(details)
    
    performance_logger.info(f"Performance metric: {log_data}")

# Rate limiting and abuse detection
class RateLimiter:
    """Simple in-memory rate limiter for basic abuse prevention."""
    
    def __init__(self):
        self.requests = {}
        self.max_requests = 100  # per minute
        self.window_size = 60  # seconds
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed based on rate limit."""
        now = datetime.now().timestamp()
        window_start = now - self.window_size
        
        # Clean old entries
        if identifier in self.requests:
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier] 
                if req_time > window_start
            ]
        else:
            self.requests[identifier] = []
        
        # Check rate limit
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()

# Middleware for rate limiting
async def rate_limit_middleware(request: Request, call_next):
    """Middleware to enforce rate limiting."""
    # Get client identifier (IP address)
    client_ip = request.client.host if request.client else "unknown"
    
    if not rate_limiter.is_allowed(client_ip):
        logger = logging.getLogger('security')
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": True,
                "message": "Rate limit exceeded. Please try again later.",
                "error_code": "RATE_LIMIT_EXCEEDED"
            }
        )
    
    response = await call_next(request)
    return response

# Error monitoring and alerting (placeholder for production)
def send_error_alert(error: Exception, context: Dict[str, Any] = None):
    """Send error alert (placeholder for production monitoring)."""
    logger = logging.getLogger('error')
    logger.critical(f"CRITICAL ERROR ALERT: {str(error)}", exc_info=True)
    
    # In production, this would integrate with services like:
    # - Sentry
    # - DataDog
    # - New Relic
    # - Custom webhook notifications
    
    if context:
        logger.critical(f"Error context: {context}")

# Initialize logging when module is imported
setup_logging()
