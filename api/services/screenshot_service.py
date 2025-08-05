"""
Servicio de lógica de negocio para capturas de pantalla
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Optional
from core.scrcpy_controller import ScrcpyController
from ..config import logger, settings
from ..schemas import ScreenshotRequest, ScreenshotResponse

class ScreenshotService:
    """Servicio para gestión de capturas de pantalla"""
    
    def __init__(self):
        self.scrcpy_controller = ScrcpyController()
        self.logger = logger
    
    async def take_screenshot(self, serial: str, filename: Optional[str] = None) -> dict:
        """Toma captura de pantalla y retorna información del archivo"""
        try:
            self.logger.info(f"Tomando captura de pantalla del dispositivo {serial}")
            
            result = self.scrcpy_controller.take_screenshot(serial, filename)
            
            if result['success']:
                self.logger.info(f"Captura exitosa: {result['filename']}")
                return {
                    'success': True,
                    'filename': result['filename'],
                    'full_path': result['full_path'],
                    'folder': result['folder'],
                    'message': f'Captura guardada en: {result["folder"]}'
                }
            else:
                self.logger.error(f"Error en captura: {result.get('error', 'Error desconocido')}")
                return {
                    'success': False,
                    'error': result.get('error', 'Error desconocido al tomar captura')
                }
                
        except Exception as e:
            self.logger.error(f"Excepción al tomar captura del dispositivo {serial}: {str(e)}")
            raise
    
    async def take_screenshot_for_download(self, serial: str, filename: Optional[str] = None) -> dict:
        """Toma captura de pantalla optimizada para descarga directa"""
        try:
            self.logger.info(f"Tomando captura para descarga del dispositivo {serial}")
            
            # Usar el mismo método pero optimizado para web
            result = self.scrcpy_controller.take_screenshot(serial, filename)
            
            if result['success']:
                self.logger.info(f"Captura para descarga exitosa: {result['filename']}")
                return result
            else:
                self.logger.error(f"Error en captura para descarga: {result.get('error')}")
                return result
                
        except Exception as e:
            self.logger.error(f"Excepción al tomar captura para descarga: {str(e)}")
            raise
