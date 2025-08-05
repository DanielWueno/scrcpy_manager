#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controlador para scrcpy con funciones en tiempo real
"""

import subprocess
import time
from typing import Dict, List, Optional

class ScrcpyController:
    def __init__(self):
        self.scrcpy_path = "scrcpy.exe"
        self.adb_path = "adb.exe"
        self.active_sessions = {}  # serial -> proceso
    
    def start_scrcpy(self, device: Dict, options: List[str] = None) -> bool:
        """Inicia scrcpy para un dispositivo"""
        serial = device['serial']
        
        # Limpiar cualquier sesión muerta antes de verificar
        self._cleanup_dead_sessions()
        
        if serial in self.active_sessions:
            print(f"Ya existe una sesión activa para {serial}")
            return False  # Ya está activo
        
        # Verificar que el dispositivo esté conectado
        if not self._device_connected(serial):
            print(f"Error: Dispositivo {serial} no está conectado físicamente")
            return False
        
        base_cmd = [self.scrcpy_path, f"--serial={serial}"]
        
        # Opciones por defecto
        default_options = ["--no-audio", "--stay-awake"]
        if options:
            base_cmd.extend(options)
        else:
            base_cmd.extend(default_options)
        
        try:
            print(f"Iniciando scrcpy para dispositivo {serial}...")
            process = subprocess.Popen(base_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Esperar un poco para que el proceso se establezca
            time.sleep(0.5)
            
            # Verificar que el proceso sigue activo
            if process.poll() is None:
                self.active_sessions[serial] = {
                    'process': process,
                    'device': device,
                    'start_time': time.time()
                }
                print(f"scrcpy iniciado correctamente para {serial} (PID: {process.pid})")
                return True
            else:
                print(f"scrcpy falló al iniciar para {serial}")
                return False
                
        except Exception as e:
            print(f"Error al iniciar scrcpy para {serial}: {e}")
            return False
    
    def stop_scrcpy(self, serial: str) -> bool:
        """Detiene scrcpy para un dispositivo"""
        if serial in self.active_sessions:
            try:
                process = self.active_sessions[serial]['process']
                process.terminate()
                del self.active_sessions[serial]
                return True
            except:
                pass
        return False
    
    def is_active(self, serial: str) -> bool:
        """Verifica si scrcpy está activo para un dispositivo"""
        if serial in self.active_sessions:
            process = self.active_sessions[serial]['process']
            is_running = process.poll() is None
            
            # Si el proceso ya no está activo, limpiar la sesión
            if not is_running:
                print(f"Limpiando sesión muerta para dispositivo {serial}")
                del self.active_sessions[serial]
                return False
            
            return True
        return False
    
    def screen_off(self, serial: str) -> bool:
        """Apaga la pantalla del dispositivo"""
        try:
            subprocess.run([self.adb_path, '-s', serial, 'shell', 'input', 'keyevent', 'KEYCODE_POWER'], 
                          timeout=5)
            return True
        except:
            return False
    
    def screen_on(self, serial: str) -> bool:
        """Enciende la pantalla del dispositivo"""
        try:
            subprocess.run([self.adb_path, '-s', serial, 'shell', 'input', 'keyevent', 'KEYCODE_WAKEUP'], 
                          timeout=5)
            return True
        except:
            return False
    
    def take_screenshot(self, serial: str, filename: str = None) -> dict:
        """Toma captura de pantalla y la guarda en la carpeta de Imágenes del usuario"""
        import os
        from datetime import datetime
        
        # Crear carpeta de destino en Imágenes del usuario
        pictures_folder = os.path.join(os.path.expanduser("~"), "Pictures", "Scrcpy Screenshots")
        os.makedirs(pictures_folder, exist_ok=True)
        
        if not filename:
            # Generar nombre con timestamp más legible
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            device_name = serial[-6:]  # Últimos 6 caracteres del serial
            filename = f"screenshot_{device_name}_{timestamp}.png"
        
        # Ruta completa del archivo
        full_path = os.path.join(pictures_folder, filename)
        
        try:
            print(f"Tomando captura de pantalla del dispositivo {serial}")
            
            # Tomar captura en el dispositivo
            result1 = subprocess.run([self.adb_path, '-s', serial, 'shell', 'screencap', '/sdcard/temp_screenshot.png'], 
                          capture_output=True, text=True, timeout=10)
            
            if result1.returncode != 0:
                print(f"Error al tomar captura en dispositivo: {result1.stderr}")
                return {'success': False, 'error': 'Error al tomar captura en dispositivo'}
            
            # Descargar a PC
            result2 = subprocess.run([self.adb_path, '-s', serial, 'pull', '/sdcard/temp_screenshot.png', full_path], 
                          capture_output=True, text=True, timeout=10)
            
            if result2.returncode != 0:
                print(f"Error al descargar captura: {result2.stderr}")
                return {'success': False, 'error': 'Error al descargar captura'}
            
            # Limpiar archivo temporal del dispositivo
            subprocess.run([self.adb_path, '-s', serial, 'shell', 'rm', '/sdcard/temp_screenshot.png'], 
                          timeout=5)
            
            print(f"Captura guardada en: {full_path}")
            return {
                'success': True, 
                'filename': filename,
                'full_path': full_path,
                'folder': pictures_folder
            }
            
        except Exception as e:
            print(f"Error al tomar captura de pantalla: {e}")
            return {'success': False, 'error': str(e)}
    
    def start_recording(self, serial: str, filename: str = None) -> bool:
        """Inicia grabación de pantalla"""
        if not filename:
            filename = f"recording_{serial}_{int(time.time())}.mp4"
        
        # Esto requiere implementación más compleja para control de grabación
        # Por ahora, reinicia scrcpy con opción de grabación
        if serial in self.active_sessions:
            self.stop_scrcpy(serial)
            time.sleep(1)
        
        device = None
        # Aquí necesitarías obtener el device data
        options = [f"--record={filename}", "--no-audio", "--stay-awake"]
        return self.start_scrcpy(device, options)
    
    def get_active_sessions(self) -> Dict:
        """Retorna sesiones activas"""
        # Limpiar sesiones terminadas
        to_remove = []
        for serial, session in self.active_sessions.items():
            if session['process'].poll() is not None:
                to_remove.append(serial)
        
        for serial in to_remove:
            del self.active_sessions[serial]
        
        return self.active_sessions
    
    def mirror_screen_off(self, serial: str) -> bool:
        """Apaga pantalla del dispositivo usando scrcpy (mantiene mirror activo)"""
        if serial not in self.active_sessions:
            print(f"No hay sesión activa para dispositivo {serial}")
            return False
            
        try:
            # Método simplificado - enviando Alt+O directamente sin DLLs complejas
            ps_command = '''
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName Microsoft.VisualBasic
$proc = Get-Process -Name "scrcpy" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($proc) {
    # Activar ventana usando VisualBasic
    [Microsoft.VisualBasic.Interaction]::AppActivate($proc.Id)
    Start-Sleep -Milliseconds 500
    # Enviar Alt+O
    [System.Windows.Forms.SendKeys]::SendWait("%o")
    Write-Host "ALT_O_SENT"
} else {
    Write-Host "NO_SCRCPY"
}
'''
            
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True, text=True, timeout=10
            )
            
            print(f"PowerShell stdout: {result.stdout}")
            print(f"PowerShell stderr: {result.stderr}")
            print(f"PowerShell returncode: {result.returncode}")
            
            if result.returncode == 0 and 'ALT_O_SENT' in result.stdout:
                print(f"Alt+O enviado exitosamente a scrcpy para dispositivo {serial}")
                return True
            else:
                print(f"Error enviando Alt+O: {result.stdout}")
                return False
                
        except Exception as e:
            print(f"Error al apagar pantalla del dispositivo {serial}: {e}")
            return False
    
    def mirror_screen_on(self, serial: str) -> bool:
        """Enciende pantalla del dispositivo usando scrcpy"""
        if serial not in self.active_sessions:
            print(f"No hay sesión activa para dispositivo {serial}")
            return False
            
        try:
            # Método simplificado - enviando Alt+Shift+O directamente sin DLLs complejas
            ps_command = '''
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName Microsoft.VisualBasic
$proc = Get-Process -Name "scrcpy" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($proc) {
    # Activar ventana usando VisualBasic
    [Microsoft.VisualBasic.Interaction]::AppActivate($proc.Id)
    Start-Sleep -Milliseconds 500
    # Enviar Alt+Shift+O
    [System.Windows.Forms.SendKeys]::SendWait("%+o")
    Write-Host "ALT_SHIFT_O_SENT"
} else {
    Write-Host "NO_SCRCPY"
}
'''
            
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True, text=True, timeout=10
            )
            
            print(f"PowerShell stdout: {result.stdout}")
            print(f"PowerShell stderr: {result.stderr}")
            print(f"PowerShell returncode: {result.returncode}")
            
            if result.returncode == 0 and 'ALT_SHIFT_O_SENT' in result.stdout:
                print(f"Alt+Shift+O enviado exitosamente a scrcpy para dispositivo {serial}")
                return True
            else:
                print(f"Error enviando Alt+Shift+O: {result.stdout}")
                return False
                
        except Exception as e:
            print(f"Error al encender pantalla del dispositivo {serial}: {e}")
            return False
    
    def start_recording_safe(self, device: Dict, filename: str) -> bool:
        """Inicia grabación de forma segura sin cerrar scrcpy actual"""
        serial = device['serial']
        
        # No detener scrcpy actual, usar comando separado para grabar
        try:
            cmd = [self.scrcpy_path, f"--serial={serial}", f"--record={filename}", 
                   "--no-display", "--no-audio"]
            
            process = subprocess.Popen(cmd)
            
            # Guardar proceso de grabación separadamente
            if serial not in self.active_sessions:
                self.active_sessions[serial] = {}
            
            self.active_sessions[serial]['recording'] = {
                'process': process,
                'filename': filename,
                'start_time': time.time()
            }
            
            return True
        except:
            return False
    
    def stop_recording(self, serial: str) -> bool:
        """Detiene grabación manteniendo mirror activo"""
        if (serial in self.active_sessions and 
            'recording' in self.active_sessions[serial]):
            try:
                recording = self.active_sessions[serial]['recording']
                recording['process'].terminate()
                del self.active_sessions[serial]['recording']
                return True
            except:
                pass
        return False
    
    def send_keycode(self, serial: str, keycode: str) -> bool:
        """Envía un keycode al dispositivo usando ADB"""
        try:
            print(f"Enviando keycode {keycode} a dispositivo {serial}")
            result = subprocess.run(
                [self.adb_path, '-s', serial, 'shell', 'input', 'keyevent', keycode],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                print(f"Keycode {keycode} enviado exitosamente a {serial}")
                return True
            else:
                print(f"Error enviando keycode {keycode} a {serial}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error enviando keycode {keycode} a dispositivo {serial}: {e}")
            return False
    
    def _device_connected(self, serial: str) -> bool:
        """Verifica si el dispositivo está físicamente conectado"""
        try:
            result = subprocess.run([self.adb_path, 'devices'], 
                                  capture_output=True, text=True, timeout=5)
            connected_devices = []
            for line in result.stdout.split('\n'):
                if '\tdevice' in line:
                    device_serial = line.split('\t')[0]
                    connected_devices.append(device_serial)
            
            return serial in connected_devices
        except Exception as e:
            print(f"Error verificando conexión del dispositivo {serial}: {e}")
            return False
    
    def _cleanup_dead_sessions(self):
        """Limpia sesiones de procesos que ya no están activos"""
        dead_serials = []
        for serial, session in self.active_sessions.items():
            process = session['process']
            if process.poll() is not None:  # El proceso ha terminado
                dead_serials.append(serial)
        
        for serial in dead_serials:
            print(f"Removiendo sesión muerta para dispositivo {serial}")
            del self.active_sessions[serial]