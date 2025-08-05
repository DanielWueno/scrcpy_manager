"""
Servicio de lógica de negocio para dispositivos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import List, Optional
from core.device_manager import DeviceManager
from core.scrcpy_controller import ScrcpyController
from ..config import logger, settings
from ..schemas import Device, DeviceListResponse, DeviceResponse

class DeviceService:
    """Servicio para gestión de dispositivos"""
    
    def __init__(self):
        self.device_manager = DeviceManager()
        self.scrcpy_controller = ScrcpyController()
        self.logger = logger
    
    async def get_devices(self) -> DeviceListResponse:
        """Obtiene lista de dispositivos con estado"""
        try:
            self.logger.info("Obteniendo lista de dispositivos")
            devices = self.device_manager.get_devices_status()
            
            # Agregar estado de scrcpy a cada dispositivo
            for device in devices:
                device['active'] = self.scrcpy_controller.is_active(device['serial'])
            
            self.logger.info(f"Se encontraron {len(devices)} dispositivos")
            return DeviceListResponse(
                success=True,
                devices=[Device(**device) for device in devices]
            )
            
        except Exception as e:
            self.logger.error(f"Error al obtener dispositivos: {str(e)}")
            raise
    
    async def refresh_devices(self) -> DeviceListResponse:
        """Actualiza lista de dispositivos"""
        try:
            self.logger.info("Actualizando lista de dispositivos")
            new_devices = self.device_manager.update_devices_list()
            devices = self.device_manager.get_devices_status()
            
            # Agregar estado de scrcpy a cada dispositivo
            for device in devices:
                device['active'] = self.scrcpy_controller.is_active(device['serial'])
            
            self.logger.info(f"Lista actualizada. {new_devices} dispositivos nuevos")
            return DeviceListResponse(
                success=True,
                devices=[Device(**device) for device in devices],
                new_devices_count=new_devices
            )
            
        except Exception as e:
            self.logger.error(f"Error al actualizar dispositivos: {str(e)}")
            raise
    
    async def connect_device(self, serial: str, options: List[str]) -> DeviceResponse:
        """Conecta dispositivo con scrcpy"""
        try:
            self.logger.info(f"Conectando dispositivo {serial}")
            
            device = self.device_manager.get_device_by_serial(serial)
            if not device:
                return DeviceResponse(
                    success=False,
                    error='Dispositivo no encontrado'
                )
            
            # Verificar si el dispositivo está físicamente conectado
            connected_devices = self.device_manager.get_connected_devices()
            if serial not in connected_devices:
                return DeviceResponse(
                    success=False,
                    error=f'Dispositivo {device.get("alias", serial)} no está conectado físicamente'
                )
            
            # Verificar si ya está activo
            if self.scrcpy_controller.is_active(serial):
                return DeviceResponse(
                    success=False,
                    error=f'El dispositivo {device.get("alias", serial)} ya tiene una sesión activa'
                )
            
            result = self.scrcpy_controller.start_scrcpy(device, options)
            
            if result:
                self.logger.info(f"Dispositivo {serial} conectado exitosamente")
                return DeviceResponse(
                    success=True,
                    message=f'Mirror iniciado para {device.get("alias", serial)}'
                )
            else:
                return DeviceResponse(
                    success=False,
                    error=f'Error al iniciar mirror para {device.get("alias", serial)}'
                )
                
        except Exception as e:
            self.logger.error(f"Error al conectar dispositivo {serial}: {str(e)}")
            raise
    
    async def disconnect_device(self, serial: str) -> DeviceResponse:
        """Desconecta dispositivo"""
        try:
            self.logger.info(f"Desconectando dispositivo {serial}")
            result = self.scrcpy_controller.stop_scrcpy(serial)
            
            if result:
                self.logger.info(f"Dispositivo {serial} desconectado exitosamente")
                return DeviceResponse(success=True, message='Desconectado')
            else:
                return DeviceResponse(success=False, error='Error al desconectar')
                
        except Exception as e:
            self.logger.error(f"Error al desconectar dispositivo {serial}: {str(e)}")
            raise
    
    async def get_device_status(self, serial: str):
        """Obtiene estado del dispositivo"""
        try:
            device = self.device_manager.get_device_by_serial(serial)
            if not device:
                return DeviceResponse(
                    success=False,
                    error='Dispositivo no encontrado'
                )
            
            connected = device['serial'] in self.device_manager.get_connected_devices()
            active = self.scrcpy_controller.is_active(serial)
            
            self.logger.info(f"Estado del dispositivo {serial}: conectado={connected}, activo={active}")
            
            return {
                'success': True,
                'device': device,
                'connected': connected,
                'active': active
            }
            
        except Exception as e:
            self.logger.error(f"Error al obtener estado del dispositivo {serial}: {str(e)}")
            raise
