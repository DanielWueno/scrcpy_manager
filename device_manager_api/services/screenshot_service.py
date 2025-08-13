import os
import time
from typing import Dict

class ScreenshotService:
    @staticmethod
    def get_pictures_folder() -> str:
        """Obtiene la carpeta de imágenes del usuario"""
        return os.path.join(os.path.expanduser("~"), "Pictures", "ScrcpyManager")
    
    @staticmethod
    def generate_filename(serial: str, filename: str = None) -> str:
        """Genera nombre de archivo para screenshot"""
        if not filename:
            timestamp = int(time.time())
            return f"screenshot_{serial}_{timestamp}.png"
        return filename if filename.endswith('.png') else f"{filename}.png"
    
    @staticmethod
    def get_full_path(filename: str, folder: str = None) -> str:
        """Obtiene la ruta completa del archivo"""
        if not folder:
            folder = ScreenshotService.get_pictures_folder()
        return os.path.join(folder, filename)