import json
import pickle
from pathlib import Path
from typing import Any, Union


def atomic_write_json(data: Any, filepath: Union[str, Path], indent: int = 2) -> None:
    """
    Write data to a JSON file atomically
    
    Args:
        data: The data to serialize
        filepath: Destination path
        indent: JSON indentation level
    """
    path = Path(filepath)
    temp_path = path.with_suffix('.tmp')
    
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
            
        if path.exists():
            path.unlink()
        temp_path.rename(path)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise


def atomic_write_text(content: str, filepath: Union[str, Path], encoding: str = 'utf-8') -> None:
    """
    Write string content to a file
    
    Args:
        content: String content to write
        filepath: Destination path
        encoding: File encoding
    """
    path = Path(filepath)
    temp_path = path.with_suffix('.tmp')
    
    try:
        with open(temp_path, 'w', encoding=encoding) as f:
            f.write(content)
            
        if path.exists():
            path.unlink()
        temp_path.rename(path)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise


def atomic_write_binary(data: bytes, filepath: Union[str, Path]) -> None:
    """
    Write binary data to a file 
    
    Args:
        data: Bytes to write
        filepath: Destination path
    """
    path = Path(filepath)
    temp_path = path.with_suffix('.tmp')
    
    try:
        with open(temp_path, 'wb') as f:
            f.write(data)
            
        if path.exists():
            path.unlink()
        temp_path.rename(path)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise


def atomic_write_pickle(data: Any, filepath: Union[str, Path], protocol: int = pickle.HIGHEST_PROTOCOL) -> None:
    """
    Pickle data to a file
    
    Args:
        data: Object to pickle
        filepath: Destination path
        protocol: Pickle protocol version
    """
    path = Path(filepath)
    temp_path = path.with_suffix('.tmp')
    
    try:
        with open(temp_path, 'wb') as f:
            pickle.dump(data, f, protocol=protocol)
            
        if path.exists():
            path.unlink()
        temp_path.rename(path)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise
