#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core logic para el manejo de dispositivos
"""

import subprocess
import json
import os
from datetime import datetime
from typing import List, Dict
from .android.android_manager import AndroidManager
from .ios.ios_manager import IOSManager
from device_manager_api.services.android.device_service import DeviceService
from device_manager_api.schemas.android.device_schema import Device, ActionResponse

class DeviceManager:
    def __init__(self):
        self.android_manager = AndroidManager()
        self.ios_manager = IOSManager()
        self.device_service = DeviceService()
    
    def get_all_devices(self) -> List[Dict]:
        """Obtiene todos los dispositivos conectados"""
        all_devices = []
        
        # Android devices
        android_devices = self.android_manager.get_connected_devices()
        for serial in android_devices:
            device_info = self.android_manager.get_device_info(serial)
            device_info['active'] = self.android_manager.is_mirror_active(serial)
            all_devices.append(device_info)
        
        # iOS devices
        ios_devices = self.ios_manager.get_connected_devices()
        for udid in ios_devices:
            device_info = self.ios_manager.get_device_info(udid)
            device_info['active'] = self.ios_manager.is_mirror_active(udid)
            all_devices.append(device_info)
        
        return all_devices
    
    def get_device_by_serial(self, serial: str) -> Dict:
        """Obtiene dispositivo por serial/udid"""
        # Buscar en Android
        if serial in self.android_manager.get_connected_devices():
            return self.android_manager.get_device_info(serial)
        
        # Buscar en iOS
        if serial in self.ios_manager.get_connected_devices():
            return self.ios_manager.get_device_info(serial)
        
        return None
    
    def execute_device_action(self, serial: str, action: str, payload=None) -> ActionResponse:
        """Ejecuta acción en dispositivo"""
        device = self.get_device_by_serial(serial)
        if not device:
            return ActionResponse(success=False, error='Dispositivo no encontrado')
        
        platform = device.get('platform')
        
        try:
            if platform == 'android':
                result = self.android_manager.execute_action(serial, action, payload)
            elif platform == 'ios':
                result = self.ios_manager.execute_action(serial, action, payload)
            else:
                return ActionResponse(success=False, error='Plataforma no soportada')
            
            return ActionResponse(success=result, message=f'Acción {action} ejecutada')
            
        except Exception as e:
            return ActionResponse(success=False, error=str(e))
    
    def update_device_alias(self, serial: str, alias: str) -> bool:
        """Actualiza alias de dispositivo"""
        return self.device_service.update_device_alias(serial, alias)