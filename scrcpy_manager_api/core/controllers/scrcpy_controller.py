#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controlador para scrcpy con funciones en tiempo real
"""

import subprocess
import time
from typing import Dict, List
from device_manager_api.services.process_service import ProcessService
from device_manager_api.services.screenshot_service import ScreenshotService
from device_manager_api.schemas.screenshot_schema import ScreenshotResponse

class ScrcpyController:
    def __init__(self):
        self.active_sessions = {}
        self.process_service = ProcessService()
        self.screenshot_service = ScreenshotService()
    
    def take_screenshot(self, serial: str, filename: str = None) -> ScreenshotResponse:
        """Toma screenshot usando scrcpy"""
        try:
            folder = self.screenshot_service.get_pictures_folder()
            filename = self.screenshot_service.generate_filename(serial, filename)
            full_path = self.screenshot_service.get_full_path(filename, folder)
            
            # Crear carpeta si no existe
            import os
            os.makedirs(folder, exist_ok=True)
            
            # Comando para screenshot
            command = ["scrcpy", "-s", serial, "--print-fps", "--no-audio", f"--screenshot={full_path}"]
            
            result = self.process_service.run_command(command, timeout=10)
            
            if result['success']:
                return ScreenshotResponse(
                    success=True,
                    filename=filename,
                    full_path=full_path,
                    folder=folder
                )
            else:
                return ScreenshotResponse(success=False, error=result.get('error', 'Error desconocido'))
                
        except Exception as e:
            return ScreenshotResponse(success=False, error=str(e))
    
    def start_scrcpy(self, device: Dict, options: List[str] = None) -> bool:
        """Inicia scrcpy para un dispositivo"""
        serial = device['serial']
        
        if serial in self.active_sessions:
            return True
        
        try:
            command = ["scrcpy", "-s", serial]
            if options:
                command.extend(options)
            
            process = subprocess.Popen(command)
            
            self.active_sessions[serial] = {
                'process': process,
                'device': device,
                'started_at': time.time()
            }
            
            return True
            
        except Exception as e:
            print(f"Error iniciando scrcpy: {e}")
            return False
    
    def stop_scrcpy(self, serial: str) -> bool:
        """Detiene scrcpy para un dispositivo"""
        if serial not in self.active_sessions:
            return True
        
        try:
            session = self.active_sessions[serial]
            session['process'].terminate()
            
            # Esperar a que termine
            session['process'].wait(timeout=5)
            
            del self.active_sessions[serial]
            return True
            
        except Exception as e:
            print(f"Error deteniendo scrcpy: {e}")
            return False
    
    def is_active(self, serial: str) -> bool:
        """Verifica si scrcpy está activo para un dispositivo"""
        if serial not in self.active_sessions:
            return False
        
        session = self.active_sessions[serial]
        if session['process'].poll() is not None:
            # Proceso terminado, limpiar
            del self.active_sessions[serial]
            return False
        
        return True