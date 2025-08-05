"""
Inicialización del paquete API
"""
from .config import settings
from .main import create_app

__version__ = "1.0.0"
__all__ = ["settings", "create_app"]
