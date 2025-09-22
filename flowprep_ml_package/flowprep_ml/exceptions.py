"""
Custom exceptions for FlowPrep ML library
"""

class FlowPrepError(Exception):
    """Base exception for FlowPrep ML library"""
    pass

class UnsupportedFileFormatError(FlowPrepError):
    """Raised when an unsupported file format is provided"""
    pass

class ValidationError(FlowPrepError):
    """Raised when data validation fails"""
    pass

class PreprocessingError(FlowPrepError):
    """Raised when preprocessing fails"""
    pass

class FileNotFoundError(FlowPrepError):
    """Raised when a file is not found"""
    pass

class InvalidParameterError(FlowPrepError):
    """Raised when invalid parameters are provided"""
    pass
