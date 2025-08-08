from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseDeviceManager(ABC):
    """Interfaz base para managers de dispositivos"""
    
    def __init__(self):
        self.active_streams = {}
    
    @property
    @abstractmethod
    def platform(self) -> str:
        """Retorna el nombre de la plataforma que maneja este manager"""
        pass
    
    @abstractmethod
    def get_connected_devices(self) -> List[str]:
        """Obtiene lista de dispositivos conectados"""
        pass
    
    @abstractmethod
    def get_device_info(self, device_id: str) -> Dict:
        """Obtiene información de un dispositivo específico"""
        pass
    
    @abstractmethod
    def start_mirror(self, device_id: str, options: Dict = None) -> bool:
        """Inicia el mirror para un dispositivo"""
        pass
    
    @abstractmethod
    def stop_mirror(self, device_id: str) -> bool:
        """Detiene el mirror para un dispositivo"""
        pass
    
    @abstractmethod
    def is_mirror_active(self, device_id: str) -> bool:
        """Verifica si el mirror está activo para un dispositivo"""
        pass
    
    @abstractmethod
    def execute_action(self, device_id: str, action: str, payload: Any = None) -> bool:
        """Ejecuta una acción en el dispositivo"""
        pass
    
    @abstractmethod
    def take_screenshot(self, device_id: str) -> bool:
        """Toma una captura de pantalla del dispositivo"""
        pass