import os
import json
from typing import List, Dict
from datetime import datetime

class DeviceService:
    def __init__(self):
        self.devices_file = os.path.join(
            os.path.expanduser("~"), 
            ".scrcpy_manager", 
            "devices.json"
        )
    
    def load_devices(self) -> List[Dict]:
        """Carga dispositivos desde archivo"""
        try:
            with open(self.devices_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error cargando dispositivos: {e}")
            return []
    
    def save_devices(self, devices: List[Dict]) -> bool:
        """Guarda dispositivos en archivo"""
        try:
            os.makedirs(os.path.dirname(self.devices_file), exist_ok=True)
            with open(self.devices_file, 'w', encoding='utf-8') as f:
                json.dump(devices, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error guardando dispositivos: {e}")
            return False
    
    def update_device_alias(self, serial: str, alias: str) -> bool:
        """Actualiza alias de dispositivo"""
        devices = self.load_devices()
        
        # Buscar dispositivo existente
        device_found = False
        for device in devices:
            if device.get('serial') == serial:
                device['alias'] = alias
                device_found = True
                break
        
        # Si no se encuentra, crear nuevo registro
        if not device_found:
            devices.append({
                'serial': serial,
                'alias': alias,
                'first_seen': datetime.now().isoformat()
            })
        
        return self.save_devices(devices)