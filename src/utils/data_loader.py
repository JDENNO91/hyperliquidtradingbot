"""
Data Loading Utilities

This module provides utilities for loading, processing, and saving market data.
"""

import json
import csv
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Union, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_market_data(file_path: str, 
                    file_type: Optional[str] = None,
                    **kwargs) -> List[Dict[str, Any]]:
    """
    Load market data from various file formats.
    
    Args:
        file_path: Path to the data file
        file_type: Type of file ('json', 'csv', 'parquet', 'auto')
        **kwargs: Additional arguments for specific loaders
        
    Returns:
        List of dictionaries containing market data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file type is unsupported
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    # Auto-detect file type if not specified
    if file_type is None:
        file_type = file_path.suffix.lstrip('.').lower()
    
    # Load based on file type
    if file_type in ['json', 'js']:
        return load_json_data(file_path, **kwargs)
    elif file_type in ['csv']:
        return load_csv_data(file_path, **kwargs)
    elif file_type in ['parquet', 'pq']:
        return load_parquet_data(file_path, **kwargs)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def load_json_data(file_path: Union[str, Path], 
                  **kwargs) -> List[Dict[str, Any]]:
    """
    Load market data from JSON file.
    
    Args:
        file_path: Path to JSON file
        **kwargs: Additional arguments
        
    Returns:
        List of dictionaries containing market data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ensure data is a list
        if isinstance(data, dict):
            # If it's a dict with a data key, extract it
            if 'data' in data:
                data = data['data']
            else:
                # Convert dict to list of single item
                data = [data]
        
        if not isinstance(data, list):
            raise ValueError("JSON data must be a list or dict with 'data' key")
        
        logger.info(f"Loaded {len(data)} records from {file_path}")
        return data
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON file {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to load JSON file {file_path}: {e}")
        raise

def load_csv_data(file_path: Union[str, Path], 
                 **kwargs) -> List[Dict[str, Any]]:
    """
    Load market data from CSV file.
    
    Args:
        file_path: Path to CSV file
        **kwargs: Additional arguments for pandas.read_csv
        
    Returns:
        List of dictionaries containing market data
    """
    try:
        # Use pandas to read CSV with flexible options
        df = pd.read_csv(file_path, **kwargs)
        
        # Convert DataFrame to list of dictionaries
        data = df.to_dict('records')
        
        logger.info(f"Loaded {len(data)} records from {file_path}")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load CSV file {file_path}: {e}")
        raise

def load_parquet_data(file_path: Union[str, Path], 
                     **kwargs) -> List[Dict[str, Any]]:
    """
    Load market data from Parquet file.
    
    Args:
        file_path: Path to Parquet file
        **kwargs: Additional arguments for pandas.read_parquet
        
    Returns:
        List of dictionaries containing market data
    """
    try:
        df = pd.read_parquet(file_path, **kwargs)
        data = df.to_dict('records')
        
        logger.info(f"Loaded {len(data)} records from {file_path}")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load Parquet file {file_path}: {e}")
        raise

def save_market_data(data: List[Dict[str, Any]], 
                    file_path: str, 
                    file_type: Optional[str] = None,
                    **kwargs) -> None:
    """
    Save market data to various file formats.
    
    Args:
        data: List of dictionaries containing market data
        file_path: Path to save the data
        file_type: Type of file ('json', 'csv', 'parquet', 'auto')
        **kwargs: Additional arguments for specific savers
    """
    file_path = Path(file_path)
    
    # Auto-detect file type if not specified
    if file_type is None:
        file_type = file_path.suffix.lstrip('.').lower()
    
    # Create directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save based on file type
    if file_type in ['json', 'js']:
        save_json_data(data, file_path, **kwargs)
    elif file_type in ['csv']:
        save_csv_data(data, file_path, **kwargs)
    elif file_type in ['parquet', 'pq']:
        save_parquet_data(data, file_path, **kwargs)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    logger.info(f"Saved {len(data)} records to {file_path}")

def save_json_data(data: List[Dict[str, Any]], 
                  file_path: Union[str, Path], 
                  **kwargs) -> None:
    """
    Save market data to JSON file.
    
    Args:
        data: List of dictionaries containing market data
        file_path: Path to save the JSON file
        **kwargs: Additional arguments for json.dump
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, **kwargs)
    except Exception as e:
        logger.error(f"Failed to save JSON file {file_path}: {e}")
        raise

def save_csv_data(data: List[Dict[str, Any]], 
                 file_path: Union[str, Path], 
                 **kwargs) -> None:
    """
    Save market data to CSV file.
    
    Args:
        data: List of dictionaries containing market data
        file_path: Path to save the CSV file
        **kwargs: Additional arguments for pandas.to_csv
    """
    try:
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False, **kwargs)
    except Exception as e:
        logger.error(f"Failed to save CSV file {file_path}: {e}")
        raise

def save_parquet_data(data: List[Dict[str, Any]], 
                     file_path: Union[str, Path], 
                     **kwargs) -> None:
    """
    Save market data to Parquet file.
    
    Args:
        data: List of dictionaries containing market data
        file_path: Path to save the Parquet file
        **kwargs: Additional arguments for pandas.to_parquet
    """
    try:
        df = pd.DataFrame(data)
        df.to_parquet(file_path, index=False, **kwargs)
    except Exception as e:
        logger.error(f"Failed to save Parquet file {file_path}: {e}")
        raise

def validate_market_data(data: List[Dict[str, Any]], 
                        required_fields: Optional[List[str]] = None) -> bool:
    """
    Validate market data structure and content.
    
    Args:
        data: List of dictionaries containing market data
        required_fields: List of required field names
        
    Returns:
        True if data is valid, False otherwise
    """
    if not isinstance(data, list) or len(data) == 0:
        logger.error("Data must be a non-empty list")
        return False
    
    # Default required fields for OHLCV data
    if required_fields is None:
        required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    
    # Check first record for required fields
    first_record = data[0]
    missing_fields = [field for field in required_fields if field not in first_record]
    
    if missing_fields:
        logger.error(f"Missing required fields: {missing_fields}")
        return False
    
    # Validate data types and values
    for i, record in enumerate(data):
        if not isinstance(record, dict):
            logger.error(f"Record {i} is not a dictionary")
            return False
        
        # Check numeric fields
        for field in ['open', 'high', 'low', 'close', 'volume']:
            if field in record:
                try:
                    value = float(record[field])
                    if value < 0:
                        logger.warning(f"Record {i}: {field} is negative: {value}")
                except (ValueError, TypeError):
                    logger.error(f"Record {i}: {field} is not numeric: {record[field]}")
                    return False
        
        # Check timestamp
        if 'timestamp' in record:
            timestamp = record['timestamp']
            if not (isinstance(timestamp, (int, float)) or 
                   (isinstance(timestamp, str) and timestamp.isdigit())):
                logger.warning(f"Record {i}: timestamp format may be invalid: {timestamp}")
    
    logger.info(f"Data validation passed: {len(data)} records")
    return True

def filter_market_data(data: List[Dict[str, Any]], 
                      filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filter market data based on specified criteria.
    
    Args:
        data: List of dictionaries containing market data
        filters: Dictionary of filter criteria
        
    Returns:
        Filtered list of market data
    """
    filtered_data = data.copy()
    
    for field, criteria in filters.items():
        if isinstance(criteria, dict):
            # Range filter: {'min': value, 'max': value}
            if 'min' in criteria:
                filtered_data = [r for r in filtered_data 
                               if field in r and r[field] >= criteria['min']]
            if 'max' in criteria:
                filtered_data = [r for r in filtered_data 
                               if field in r and r[field] <= criteria['max']]
        elif isinstance(criteria, (list, tuple)):
            # List filter: [value1, value2, ...]
            filtered_data = [r for r in filtered_data 
                           if field in r and r[field] in criteria]
        else:
            # Exact match filter
            filtered_data = [r for r in filtered_data 
                           if field in r and r[field] == criteria]
    
    logger.info(f"Filtered data: {len(data)} -> {len(filtered_data)} records")
    return filtered_data

def resample_market_data(data: List[Dict[str, Any]], 
                        interval: str,
                        timestamp_field: str = 'timestamp') -> List[Dict[str, Any]]:
    """
    Resample market data to different time intervals.
    
    Args:
        data: List of dictionaries containing market data
        interval: Target interval ('1m', '5m', '15m', '1h', '4h', '1d')
        timestamp_field: Name of the timestamp field
        
    Returns:
        Resampled market data
    """
    if not data:
        return data
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(data)
    
    # Convert timestamp to datetime if it's numeric
    if df[timestamp_field].dtype in ['int64', 'float64']:
        df[timestamp_field] = pd.to_datetime(df[timestamp_field], unit='s')
    else:
        df[timestamp_field] = pd.to_datetime(df[timestamp_field])
    
    # Set timestamp as index
    df.set_index(timestamp_field, inplace=True)
    
    # Resample based on interval
    resampled = df.resample(interval).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    
    # Convert back to list of dictionaries
    resampled.reset_index(inplace=True)
    resampled[timestamp_field] = resampled[timestamp_field].astype(np.int64) // 10**9
    
    result = resampled.to_dict('records')
    
    logger.info(f"Resampled data: {len(data)} -> {len(result)} records ({interval})")
    return result

def merge_market_data(data_sources: List[List[Dict[str, Any]]], 
                     merge_key: str = 'timestamp') -> List[Dict[str, Any]]:
    """
    Merge multiple market data sources.
    
    Args:
        data_sources: List of data source lists
        merge_key: Field to use for merging
        
    Returns:
        Merged market data
    """
    if not data_sources:
        return []
    
    if len(data_sources) == 1:
        return data_sources[0]
    
    # Convert all sources to DataFrames
    dfs = []
    for i, source in enumerate(data_sources):
        df = pd.DataFrame(source)
        df['_source'] = i  # Add source identifier
        dfs.append(df)
    
    # Merge DataFrames
    merged_df = pd.concat(dfs, ignore_index=True)
    
    # Sort by merge key
    if merge_key in merged_df.columns:
        merged_df.sort_values(merge_key, inplace=True)
    
    # Remove source identifier
    merged_df.drop('_source', axis=1, inplace=True)
    
    # Convert back to list of dictionaries
    result = merged_df.to_dict('records')
    
    logger.info(f"Merged {len(data_sources)} data sources: {sum(len(s) for s in data_sources)} -> {len(result)} records")
    return result
