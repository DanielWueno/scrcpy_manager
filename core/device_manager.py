#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core logic para el manejo de dispositivos
"""

import subprocess
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class DeviceManager:
    def __init__(self):
        self.devices = []
        self.config_file = "scrcpy_devices.json"
        self.adb_path = "adb.exe"
        self.load_saved_devices()
    
    def load_saved_devices(self):
        """Carga dispositivos guardados desde archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    saved_data = json.load(f)
                    self.devices = saved_data.get('devices', [])
        except:
            self.devices = []
    
    def save_devices(self):
        """Guarda dispositivos en archivo"""
        try:
            data = {
                'devices': self.devices,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error guardando dispositivos: {e}")
    
    def get_connected_devices(self) -> List[str]:
        """Obtiene lista de dispositivos conectados via ADB"""
        try:
            result = subprocess.run([self.adb_path, 'devices'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return []
            
            lines = result.stdout.strip().split('\n')[1:]
            devices = []
            
            for line in lines:
                if line.strip() and '\tdevice' in line:
                    serial = line.split('\t')[0]
                    devices.append(serial)
            
            return devices
            
        except:
            return []
    
    def get_device_info(self, serial: str) -> str:
        """Obtiene información del dispositivo"""
        try:
            # Obtener modelo
            result = subprocess.run([self.adb_path, '-s', serial, 'shell', 'getprop', 'ro.product.model'], 
                                  capture_output=True, text=True, timeout=5)
            model = result.stdout.strip() if result.returncode == 0 else "Desconocido"
            
            # Obtener marca
            result = subprocess.run([self.adb_path, '-s', serial, 'shell', 'getprop', 'ro.product.brand'], 
                                  capture_output=True, text=True, timeout=5)
            brand = result.stdout.strip() if result.returncode == 0 else "Desconocido"
            
            return f"{brand} {model}"
        except:
            return "Información no disponible"
    
    def update_devices_list(self) -> int:
        """Actualiza la lista de dispositivos y retorna cantidad de nuevos"""
        connected = self.get_connected_devices()
        new_devices_count = 0
        
        for serial in connected:
            existing = next((d for d in self.devices if d['serial'] == serial), None)
            if not existing:
                info = self.get_device_info(serial)
                device = {
                    'serial': serial,
                    'name': info,
                    'alias': f"Device_{serial[-4:]}",
                    'last_seen': datetime.now().isoformat()
                }
                self.devices.append(device)
                new_devices_count += 1
            else:
                existing['last_seen'] = datetime.now().isoformat()
        
        if new_devices_count > 0:
            self.save_devices()
        
        return new_devices_count
    
    def get_device_by_serial(self, serial: str) -> Optional[Dict]:
        """Obtiene dispositivo por serial"""
        return next((d for d in self.devices if d['serial'] == serial), None)
    
    def update_device_alias(self, serial: str, new_alias: str) -> bool:
        """Actualiza alias de dispositivo"""
        device = self.get_device_by_serial(serial)
        if device:
            device['alias'] = new_alias
            self.save_devices()
            return True
        return False
    
    def get_devices_status(self) -> List[Dict]:
        """Retorna dispositivos con su estado de conexión"""
        connected = self.get_connected_devices()
        devices_status = []
        
        for device in self.devices:
            device_data = device.copy()
            device_data['connected'] = device['serial'] in connected
            devices_status.append(device_data)
        
        return devices_status