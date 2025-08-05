"""
Utilidades para manejo de archivos
"""
import os
import shutil
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

def ensure_directory_exists(directory_path: str) -> bool:
    """
    Asegura que un directorio exista, lo crea si no existe
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        return False

def clean_old_screenshots(screenshots_dir: str, max_age_hours: int = 24) -> int:
    """
    Limpia screenshots antiguos
    """
    try:
        screenshots_path = Path(screenshots_dir)
        if not screenshots_path.exists():
            return 0
        
        cleaned_count = 0
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        for file_path in screenshots_path.glob("*.png"):
            if file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                cleaned_count += 1
                logger.info(f"Deleted old screenshot: {file_path.name}")
        
        return cleaned_count
    except Exception as e:
        logger.error(f"Error cleaning old screenshots: {e}")
        return 0

def get_file_size(file_path: str) -> Optional[int]:
    """
    Obtiene el tamaño de un archivo en bytes
    """
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        logger.error(f"Error getting file size for {file_path}: {e}")
        return None

def save_json_data(data: dict, file_path: str) -> bool:
    """
    Guarda datos en formato JSON
    """
    try:
        ensure_directory_exists(os.path.dirname(file_path))
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON data saved to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving JSON data to {file_path}: {e}")
        return False

def load_json_data(file_path: str) -> Optional[dict]:
    """
    Carga datos desde un archivo JSON
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"JSON file not found: {file_path}")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"JSON data loaded from {file_path}")
        return data
    except Exception as e:
        logger.error(f"Error loading JSON data from {file_path}: {e}")
        return None

def copy_file(source: str, destination: str) -> bool:
    """
    Copia un archivo de origen a destino
    """
    try:
        ensure_directory_exists(os.path.dirname(destination))
        shutil.copy2(source, destination)
        logger.info(f"File copied from {source} to {destination}")
        return True
    except Exception as e:
        logger.error(f"Error copying file from {source} to {destination}: {e}")
        return False

def get_directory_size(directory_path: str) -> int:
    """
    Calcula el tamaño total de un directorio en bytes
    """
    try:
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, FileNotFoundError):
                    continue
        return total_size
    except Exception as e:
        logger.error(f"Error calculating directory size for {directory_path}: {e}")
        return 0

def list_files_by_extension(directory_path: str, extension: str) -> List[str]:
    """
    Lista todos los archivos con una extensión específica en un directorio
    """
    try:
        directory = Path(directory_path)
        if not directory.exists():
            return []
        
        pattern = f"*.{extension.lstrip('.')}"
        files = [str(f) for f in directory.glob(pattern)]
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        return files
    except Exception as e:
        logger.error(f"Error listing files in {directory_path}: {e}")
        return []
