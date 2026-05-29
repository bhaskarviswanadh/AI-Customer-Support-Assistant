"""
Helper utility functions.

This module provides common utility functions used across the application.
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
import re


def generate_hash(text: str, algorithm: str = "sha256") -> str:
    """
    Generate hash of text.
    
    Args:
        text: Text to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)
        
    Returns:
        Hexadecimal hash string
    """
    hash_func = getattr(hashlib, algorithm)
    return hash_func(text.encode()).hexdigest()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text.
    
    Args:
        text: Text to extract keywords from
        min_length: Minimum keyword length
        
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Convert to lowercase and split
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter by length and remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    }
    
    keywords = [
        word for word in words
        if len(word) >= min_length and word not in stop_words
    ]
    
    return list(set(keywords))  # Remove duplicates


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string.
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    if not dt:
        return ""
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    Parse datetime string to datetime object.
    
    Args:
        dt_str: Datetime string
        format_str: Format string
        
    Returns:
        Datetime object or None if parsing fails
    """
    try:
        return datetime.strptime(dt_str, format_str)
    except (ValueError, TypeError):
        return None


def time_ago(dt: datetime) -> str:
    """
    Get human-readable time difference.
    
    Args:
        dt: Datetime object
        
    Returns:
        Human-readable time difference (e.g., "2 hours ago")
    """
    if not dt:
        return "unknown"
    
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    else:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely load JSON string.
    
    Args:
        json_str: JSON string
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    Safely dump object to JSON string.
    
    Args:
        obj: Object to serialize
        default: Default value if serialization fails
        
    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return default


def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries.
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def calculate_percentage(part: float, total: float, decimals: int = 2) -> float:
    """
    Calculate percentage.
    
    Args:
        part: Part value
        total: Total value
        decimals: Number of decimal places
        
    Returns:
        Percentage value
    """
    if total == 0:
        return 0.0
    return round((part / total) * 100, decimals)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    return filename.strip('_')


def get_nested_value(data: Dict, path: str, default: Any = None) -> Any:
    """
    Get nested dictionary value using dot notation.
    
    Args:
        data: Dictionary to search
        path: Dot-separated path (e.g., "user.profile.name")
        default: Default value if path not found
        
    Returns:
        Value at path or default
    """
    keys = path.split('.')
    value = data
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def set_nested_value(data: Dict, path: str, value: Any) -> Dict:
    """
    Set nested dictionary value using dot notation.
    
    Args:
        data: Dictionary to modify
        path: Dot-separated path (e.g., "user.profile.name")
        value: Value to set
        
    Returns:
        Modified dictionary
    """
    keys = path.split('.')
    current = data
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return data
