"""
Configuración de logging para la API
"""
import logging
import sys
from pathlib import Path
from .settings import settings

def setup_logging():
    """Configura el sistema de logging"""
    
    # Crear directorio de logs
    log_dir = Path(settings.BASE_DIR) / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configurar formato
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Logger principal
    logger = logging.getLogger("scrcpy_manager")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo
    file_handler = logging.FileHandler(log_dir / "api.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Logger global
logger = setup_logging()
