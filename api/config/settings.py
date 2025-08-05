"""
Configuraciones centralizadas para la API
"""
import os
from typing import Optional

class Settings:
    """Configuraciones de la aplicación"""
    
    # API Settings
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 5000
    DEBUG: bool = True
    
    # CORS Settings
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Screenshot Settings
    SCREENSHOT_TIMEOUT: int = 30
    SCREENSHOT_QUALITY: int = 80
    
    # Device Settings
    DEVICE_TIMEOUT: int = 10
    MAX_DEVICES: int = 10
    
    # File Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SCREENSHOTS_DIR: Optional[str] = None  # Se calculará dinámicamente
    
    @classmethod
    def get_screenshots_dir(cls) -> str:
        """Obtiene el directorio de capturas del usuario"""
        import os
        from pathlib import Path
        
        if cls.SCREENSHOTS_DIR:
            return cls.SCREENSHOTS_DIR
            
        # Directorio Pictures del usuario
        home = Path.home()
        screenshots_dir = home / "Pictures" / "Scrcpy Screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        cls.SCREENSHOTS_DIR = str(screenshots_dir)
        return cls.SCREENSHOTS_DIR

# Instancia global de configuración
settings = Settings()
