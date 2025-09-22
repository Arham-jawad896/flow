"""
Utility functions for FlowPrep ML library
"""

import os
from pathlib import Path
from typing import List, Union
from .exceptions import UnsupportedFileFormatError, FileNotFoundError

def get_supported_formats() -> List[str]:
    """
    Get list of supported file formats
    
    Returns:
        List of supported file extensions
    """
    return ['.csv', '.xls', '.xlsx', '.xlsm']

def validate_file(file_path: Union[str, Path]) -> bool:
    """
    Validate if file exists and is supported format
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file is valid
        
    Raises:
        FileNotFoundError: If file doesn't exist
        UnsupportedFileFormatError: If file format is not supported
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not file_path.is_file():
        raise FileNotFoundError(f"Path is not a file: {file_path}")
    
    file_extension = file_path.suffix.lower()
    supported_formats = get_supported_formats()
    
    if file_extension not in supported_formats:
        raise UnsupportedFileFormatError(
            f"Unsupported file format: {file_extension}. "
            f"Supported formats: {', '.join(supported_formats)}"
        )
    
    return True

def get_file_type(file_path: Union[str, Path]) -> str:
    """
    Get file type based on extension
    
    Args:
        file_path: Path to the file
        
    Returns:
        File type string
    """
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    
    if extension in ['.csv']:
        return 'csv'
    elif extension in ['.xls', '.xlsx', '.xlsm']:
        return 'excel'
    else:
        return 'unknown'

def ensure_directory(directory: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory: Directory path
        
    Returns:
        Path object
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory

def get_output_path(input_path: Union[str, Path], output_dir: Union[str, Path] = None) -> Path:
    """
    Generate output path for processed file
    
    Args:
        input_path: Input file path
        output_dir: Output directory (optional)
        
    Returns:
        Output file path
    """
    input_path = Path(input_path)
    
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
        ensure_directory(output_dir)
    
    # Generate output filename
    stem = input_path.stem
    suffix = input_path.suffix
    output_filename = f"{stem}_processed{suffix}"
    
    return output_dir / output_filename
