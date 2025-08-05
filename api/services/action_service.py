"""
Servicio de lógica de negocio para acciones de dispositivo
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.scrcpy_controller import ScrcpyController
from ..config import logger
from ..schemas import DeviceAction, ActionResponse

class ActionService:
    """Servicio para gestión de acciones de dispositivo"""
    
    def __init__(self):
        self.scrcpy_controller = ScrcpyController()
        self.logger = logger
        
        # Mapeo de acciones a métodos
        self.action_map = {
            DeviceAction.SCREEN_OFF: self._screen_off,
            DeviceAction.SCREEN_ON: self._screen_on,
            DeviceAction.MIRROR_SCREEN_OFF: self._mirror_screen_off,
            DeviceAction.MIRROR_SCREEN_ON: self._mirror_screen_on,
            DeviceAction.HOME: self._send_home,
            DeviceAction.BACK: self._send_back,
            DeviceAction.RECENT: self._send_recent,
        }
        
        # Mapeo de keycodes para acciones rápidas
        self.keycode_map = {
            DeviceAction.HOME: 'KEYCODE_HOME',
            DeviceAction.BACK: 'KEYCODE_BACK',
            DeviceAction.RECENT: 'KEYCODE_APP_SWITCH'
        }
    
    async def execute_action(self, serial: str, action: DeviceAction) -> ActionResponse:
        """Ejecuta una acción en el dispositivo especificado"""
        try:
            self.logger.info(f"Ejecutando acción {action} en dispositivo {serial}")
            
            if action not in self.action_map:
                return ActionResponse(
                    success=False,
                    error=f"Acción '{action}' no soportada"
                )
            
            # Ejecutar la acción correspondiente
            result, message = await self.action_map[action](serial)
            
            self.logger.info(f"Acción {action} completada. Resultado: {result}")
            
            return ActionResponse(
                success=result,
                message=message if result else f"Error al ejecutar {action}"
            )
            
        except Exception as e:
            self.logger.error(f"Excepción al ejecutar acción {action} en {serial}: {str(e)}")
            raise
    
    async def _screen_off(self, serial: str) -> tuple[bool, str]:
        """Apaga la pantalla del dispositivo"""
        result = self.scrcpy_controller.screen_off(serial)
        message = 'Pantalla apagada' if result else 'Error al apagar pantalla'
        return result, message
    
    async def _screen_on(self, serial: str) -> tuple[bool, str]:
        """Enciende la pantalla del dispositivo"""
        result = self.scrcpy_controller.screen_on(serial)
        message = 'Pantalla encendida' if result else 'Error al encender pantalla'
        return result, message
    
    async def _mirror_screen_off(self, serial: str) -> tuple[bool, str]:
        """Apaga la pantalla del dispositivo manteniendo el mirror"""
        self.logger.info(f"Ejecutando mirror_screen_off para {serial}")
        result = self.scrcpy_controller.mirror_screen_off(serial)
        message = 'Pantalla dispositivo apagada (mirror activo)' if result else 'Error al apagar pantalla del dispositivo'
        self.logger.info(f"Resultado mirror_screen_off: {result}")
        return result, message
    
    async def _mirror_screen_on(self, serial: str) -> tuple[bool, str]:
        """Enciende la pantalla del dispositivo"""
        self.logger.info(f"Ejecutando mirror_screen_on para {serial}")
        result = self.scrcpy_controller.mirror_screen_on(serial)
        message = 'Pantalla dispositivo encendida' if result else 'Error al encender pantalla del dispositivo'
        self.logger.info(f"Resultado mirror_screen_on: {result}")
        return result, message
    
    async def _send_home(self, serial: str) -> tuple[bool, str]:
        """Envía tecla HOME"""
        return await self._send_keycode(serial, DeviceAction.HOME)
    
    async def _send_back(self, serial: str) -> tuple[bool, str]:
        """Envía tecla BACK"""
        return await self._send_keycode(serial, DeviceAction.BACK)
    
    async def _send_recent(self, serial: str) -> tuple[bool, str]:
        """Envía tecla RECENT/APP_SWITCH"""
        return await self._send_keycode(serial, DeviceAction.RECENT)
    
    async def _send_keycode(self, serial: str, action: DeviceAction) -> tuple[bool, str]:
        """Envía un keycode específico al dispositivo"""
        keycode = self.keycode_map[action]
        self.logger.info(f"Enviando tecla {action} ({keycode}) a dispositivo {serial}")
        
        result = self.scrcpy_controller.send_keycode(serial, keycode)
        message = f'Tecla {action.value} enviada' if result else f'Error al enviar tecla {action.value}'
        
        return result, message
