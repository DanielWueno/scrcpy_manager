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
from .android.android_manager import AndroidManager
from .ios.ios_manager import IOSManager

class DeviceManager:
    def __init__(self):
        self.android_manager = AndroidManager()
        self.ios_manager = IOSManager()
        self.devices_file = "devices.json"
        self.devices = self.load_devices()
    
    def load_devices(self) -> List[Dict]:
        """Carga dispositivos del archivo JSON"""
        if os.path.exists(self.devices_file):
            try:
                with open(self.devices_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_devices(self):
        """Guarda dispositivos al archivo JSON"""
        try:
            with open(self.devices_file, 'w', encoding='utf-8') as f:
                json.dump(self.devices, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando dispositivos: {e}")
    
    def get_all_devices(self) -> List[Dict]:
        """Obtiene todos los dispositivos de todas las plataformas"""
        all_devices = []
        
        # Dispositivos Android
        try:
            android_devices = self.android_manager.get_connected_devices()
            for serial in android_devices:
                info = self.android_manager.get_device_info(serial)
                device = {
                    'serial': serial,
                    'connected': True,
                    'active': self.android_manager.is_mirror_active(serial),
                    'last_seen': datetime.now().isoformat(),
                    **info
                }
                
                # Buscar alias guardado
                saved_device = next((d for d in self.devices if d.get('serial') == serial), None)
                if saved_device:
                    device['alias'] = saved_device.get('alias')
                
                all_devices.append(device)
        except Exception as e:
            print(f"Error obteniendo dispositivos Android: {e}")
        
        # Dispositivos iOS
        try:
            ios_devices = self.ios_manager.get_connected_devices()
            for udid in ios_devices:
                info = self.ios_manager.get_device_info(udid)
                device = {
                    'serial': udid,
                    'connected': True,
                    'active': self.ios_manager.is_mirror_active(udid),
                    'last_seen': datetime.now().isoformat(),
                    **info
                }
                
                # Buscar alias guardado
                saved_device = next((d for d in self.devices if d.get('serial') == udid), None)
                if saved_device:
                    device['alias'] = saved_device.get('alias')
                
                all_devices.append(device)
        except Exception as e:
            print(f"Error obteniendo dispositivos iOS: {e}")
        
        return all_devices
    
    def get_devices_status(self) -> List[Dict]:
        """Método de compatibilidad con la API existente"""
        return self.get_all_devices()
    
    def get_connected_devices(self) -> List[str]:
        """Obtiene seriales de dispositivos conectados"""
        devices = []
        devices.extend(self.android_manager.get_connected_devices())
        devices.extend(self.ios_manager.get_connected_devices())
        return devices
    
    def get_device_by_serial(self, serial: str) -> Optional[Dict]:
        """Obtiene dispositivo por serial/udid"""
        all_devices = self.get_all_devices()
        return next((d for d in all_devices if d['serial'] == serial), None)
    
    def update_devices_list(self) -> int:
        """Actualiza lista de dispositivos y retorna cantidad de nuevos"""
        current_devices = self.get_all_devices()
        new_count = 0
        
        for device in current_devices:
            existing = next((d for d in self.devices if d.get('serial') == device['serial']), None)
            if not existing:
                self.devices.append({
                    'serial': device['serial'],
                    'platform': device['platform'],
                    'name': device['name'],
                    'first_seen': datetime.now().isoformat()
                })
                new_count += 1
        
        self.save_devices()
        return new_count
    
    def update_device_alias(self, serial: str, alias: str) -> bool:
        """Actualiza alias de un dispositivo"""
        try:
            # Buscar en dispositivos guardados
            device = next((d for d in self.devices if d.get('serial') == serial), None)
            
            if device:
                device['alias'] = alias
            else:
                # Crear nuevo registro
                device_info = self.get_device_by_serial(serial)
                if device_info:
                    self.devices.append({
                        'serial': serial,
                        'platform': device_info['platform'],
                        'name': device_info['name'],
                        'alias': alias,
                        'first_seen': datetime.now().isoformat()
                    })
            
            self.save_devices()
            return True
            
        except Exception as e:
            print(f"Error actualizando alias: {e}")
            return False
    
    def execute_device_action(self, serial: str, action: str, payload=None) -> Dict:
        """Ejecuta acción en el dispositivo apropiado"""
        device = self.get_device_by_serial(serial)
        if not device:
            return {'success': False, 'error': 'Dispositivo no encontrado'}
        
        platform = device.get('platform')
        
        if platform == 'android':
            return self.android_manager.execute_action(serial, action, payload)
        elif platform == 'ios':
            return self.ios_manager.execute_action(serial, action, payload)
        else:
            return {'success': False, 'error': 'Plataforma no soportada'}