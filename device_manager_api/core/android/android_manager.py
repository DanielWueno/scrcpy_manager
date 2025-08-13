import subprocess
import os
import time
import platform
from typing import List, Dict, Optional, Any
from ..base.base_device_manager import BaseDeviceManager

class AndroidManager(BaseDeviceManager):
    def __init__(self):
        super().__init__()
        print("Inicializando AndroidManager...")
        
        self.adb_path = self._find_adb_path()
        print(f"ADB detectado en: '{self.adb_path}'")
        
        self.scrcpy_path = self._find_scrcpy_path()
        print(f"Scrcpy detectado en: '{self.scrcpy_path}'")
        
        self.is_windows = platform.system() == "Windows"
        print(f"Sistema operativo: {'Windows' if self.is_windows else 'Unix-like'}")
        
        print("AndroidManager inicializado correctamente")
    
    @property
    def platform(self) -> str:
        return "android"
        
    def _find_adb_path(self) -> str:
        if platform.system() == "Windows":
            common_paths = [
                "C:\\tools\\adb\\adb.exe",
                "C:\\platform-tools\\adb.exe",
                "C:\\Android\\Sdk\\platform-tools\\adb.exe",
                "adb.exe"
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    print(f"Encontrado ADB en: {path}")
                    return path
        
        return "adb"
    
    def _find_scrcpy_path(self) -> str:
        if platform.system() == "Windows":
            common_paths = [
                "C:\\tools\\scrcpy\\scrcpy.exe",
                "C:\\scrcpy\\scrcpy.exe",
                "C:\\Program Files\\scrcpy\\scrcpy.exe",
                "C:\\Program Files (x86)\\scrcpy\\scrcpy.exe",
                os.path.join(os.getcwd(), "scrcpy.exe"),
                "scrcpy.exe"
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    print(f"Encontrado scrcpy en: {path}")
                    return path
        
        # Intentar encontrar en PATH
        try:
            result = subprocess.run(['where', 'scrcpy'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                scrcpy_path = result.stdout.strip().split('\n')[0]
                print(f"Encontrado scrcpy en PATH: {scrcpy_path}")
                return scrcpy_path
        except:
            pass
        
        print("No se encontro scrcpy.exe")
        return "scrcpy"

    def get_connected_devices(self) -> List[str]:
        try:
            result = subprocess.run([self.adb_path, 'devices'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                print(f"Error ejecutando ADB: {result.stderr}")
                return []
            
            devices = []
            for line in result.stdout.strip().split('\n')[1:]:
                if line.strip() and '\tdevice' in line:
                    serial = line.split('\t')[0].strip()
                    devices.append(serial)
            
            print(f"Dispositivos Android encontrados: {devices}")
            return devices
            
        except Exception as e:
            print(f"Error obteniendo dispositivos Android: {e}")
            return []

    def get_device_info(self, serial: str) -> Dict:
        try:
            result = subprocess.run([
                self.adb_path, '-s', serial, 'shell', 
                'getprop ro.product.model && getprop ro.product.brand && getprop ro.build.version.release'
            ], capture_output=True, text=True, timeout=10, 
            creationflags=subprocess.CREATE_NO_WINDOW if self.is_windows else 0)
            
            if result.returncode != 0:
                return self._get_fallback_info(serial)
            
            lines = result.stdout.strip().split('\n')
            model = lines[0].strip() if len(lines) > 0 else "Desconocido"
            brand = lines[1].strip() if len(lines) > 1 else "Desconocido"
            version = lines[2].strip() if len(lines) > 2 else "Desconocido"
            
            device_info = {
                'name': model or f"Android {serial[-4:]}",
                'model': model,
                'brand': brand,
                'android_version': version,
                'platform': 'android'
            }
            
            return device_info
            
        except Exception as e:
            print(f"Error obteniendo info Android: {e}")
            return self._get_fallback_info(serial)
    
    def _get_fallback_info(self, serial: str) -> Dict:
        return {
            'name': f"Android {serial[-4:]}",
            'model': "Desconocido",
            'brand': "Desconocido", 
            'android_version': "Desconocido",
            'platform': 'android'
        }

    def is_mirror_active(self, serial: str) -> bool:
        """Verifica si el mirror está activo para un dispositivo Android específico"""
        try:
            # Verificar en active_streams primero (más confiable)
            if serial in self.active_streams:
                stream_data = self.active_streams[serial]
                process = stream_data.get('process')
                
                if process and process.poll() is None:
                    print(f"Mirror ACTIVO para {serial[-4:]} (PID: {process.pid})")
                    return True
                elif process and process.poll() is not None:
                    # Proceso terminó, limpiar
                    print(f"Proceso terminado para {serial[-4:]}, limpiando...")
                    del self.active_streams[serial]
                    return False
            
            print(f"Mirror INACTIVO para {serial[-4:]}")
            return False
            
        except Exception as e:
            print(f"Error verificando estado mirror para {serial[-4:]}: {e}")
            return False

    def start_mirror(self, serial: str, options: Dict = None) -> bool:
        """Inicia el mirror de un dispositivo Android con scrcpy"""
        try:
            print(f"INICIANDO MIRROR para {serial[-4:]}...")
            print(f"Opciones recibidas: {options}")
            
            # Verificar si ya esta activo PARA ESTE DISPOSITIVO ESPECIFICO
            if self.is_mirror_active(serial):
                print(f"Mirror ya activo para {serial[-4:]}")
                return True
            
            # Verificar scrcpy, dispositivo conectado, etc.
            
            # Verificar que scrcpy existe y funciona
            print(f"Verificando scrcpy en: '{self.scrcpy_path}'")
            
            try:
                test_result = subprocess.run(
                    [self.scrcpy_path, '--version'], 
                    capture_output=True, 
                    text=True, 
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW if self.is_windows else 0
                )
                
                if test_result.returncode != 0:
                    print(f"scrcpy --version fallo con codigo: {test_result.returncode}")
                    return False
                    
                print(f"scrcpy funciona: {test_result.stdout.strip()}")
                
            except Exception as e:
                print(f"Error verificando scrcpy: {e}")
                return False
            
            # Verificar dispositivo conectado
            connected_devices = self.get_connected_devices()
            if serial not in connected_devices:
                print(f"Dispositivo {serial[-4:]} NO conectado")
                return False
            
            # Opciones por defecto
            default_options = {
                'stayAwake': True,
                'noAudio': True,
                'showTouches': False,
                'turnScreenOff': False
            }
            
            final_options = {**default_options, **(options or {})}
            print(f"Opciones finales: {final_options}")
            
            cmd = [self.scrcpy_path, '-s', serial]
            
            # Aplicar opciones
            if final_options.get('noAudio', False):
                cmd.append('--no-audio')
            if final_options.get('stayAwake', True):
                cmd.append('--stay-awake')
            if final_options.get('showTouches', False):
                cmd.append('--show-touches')
            if final_options.get('turnScreenOff', False):
                cmd.append('--turn-screen-off')
            
            print(f"Comando: {cmd}")
            
            # Ejecutar scrcpy
            if self.is_windows:
                process = subprocess.Popen(
                    cmd,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                process = subprocess.Popen(
                    cmd, 
                    start_new_session=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            print(f"Proceso iniciado con PID: {process.pid}")
            
            # Esperar 3 segundos
            time.sleep(3)
            
            if process.poll() is None:
                # Guardar en active_streams CON EL SERIAL ESPECÍFICO
                self.active_streams[serial] = {
                    'process': process,
                    'started_at': time.time(),
                    'options': final_options,
                    'pid': process.pid,
                    'serial': serial  # Agregar serial para tracking
                }
                
                print(f"SCRCPY INICIADO EXITOSAMENTE para {serial[-4:]} (PID: {process.pid})")
                return True
            else:
                print(f"PROCESO TERMINO con codigo: {process.poll()}")
                # Leer error si hay
                try:
                    stdout, stderr = process.communicate(timeout=1)
                    if stderr:
                        print(f"ERROR: {stderr}")
                except:
                    pass
                return False
                
        except Exception as e:
            print(f"ERROR GENERAL en start_mirror para {serial[-4:]}: {e}")
            return False

    def stop_mirror(self, serial: str) -> bool:
        """Detiene el mirror de un dispositivo Android específico"""
        try:
            print(f"DETENIENDO MIRROR para {serial[-4:]}...")
            
            stopped = False
            
            # Terminar proceso específico SOLO para este serial
            if serial in self.active_streams:
                stream_data = self.active_streams[serial]
                process = stream_data.get('process')
                
                if process:
                    print(f"Terminando proceso PID: {process.pid} para {serial[-4:]}")
                    
                    if self.is_windows:
                        try:
                            process.terminate()
                            process.wait(timeout=3)
                            stopped = True
                        except subprocess.TimeoutExpired:
                            subprocess.run(['taskkill', '/F', '/PID', str(process.pid)], 
                                         capture_output=True,
                                         creationflags=subprocess.CREATE_NO_WINDOW)
                            stopped = True
                    else:
                        process.terminate()
                        process.wait(timeout=3)
                        stopped = True
                
                # Remover SOLO este dispositivo de active_streams
                del self.active_streams[serial]
                print(f"Removido {serial[-4:]} de active_streams")
            else:
                print(f"No hay stream activo para {serial[-4:]}")
            
            print(f"Mirror detenido para {serial[-4:]}")
            return True
            
        except Exception as e:
            print(f"Error deteniendo mirror para {serial[-4:]}: {e}")
            return False

    def execute_action(self, serial: str, action: str, payload: Any = None) -> bool:
        try:
            print(f"Ejecutando accion Android '{action}' en {serial}")
            print(f"Payload: {payload}")
            
            if action == "mirror_screen_on":
                return self.start_mirror(serial, payload)
            elif action == "mirror_screen_off":
                return self.stop_mirror(serial)
            elif action == "wake_device":
                result = subprocess.run([
                    self.adb_path, '-s', serial, 'shell', 'input', 'keyevent', 'KEYCODE_WAKEUP'
                ], capture_output=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if self.is_windows else 0)
                return result.returncode == 0
            elif action == "home_button":
                result = subprocess.run([
                    self.adb_path, '-s', serial, 'shell', 'input', 'keyevent', 'KEYCODE_HOME'
                ], capture_output=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if self.is_windows else 0)
                return result.returncode == 0
            elif action == "back_button":
                result = subprocess.run([
                    self.adb_path, '-s', serial, 'shell', 'input', 'keyevent', 'KEYCODE_BACK'
                ], capture_output=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if self.is_windows else 0)
                return result.returncode == 0
            elif action == "volume_up":
                result = subprocess.run([
                    self.adb_path, '-s', serial, 'shell', 'input', 'keyevent', 'KEYCODE_VOLUME_UP'
                ], capture_output=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if self.is_windows else 0)
                return result.returncode == 0
            elif action == "volume_down":
                result = subprocess.run([
                    self.adb_path, '-s', serial, 'shell', 'input', 'keyevent', 'KEYCODE_VOLUME_DOWN'
                ], capture_output=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if self.is_windows else 0)
                return result.returncode == 0
            elif action == "screenshot":
                return self.take_screenshot(serial)
            else:
                print(f"Accion Android desconocida: {action}")
                return False
                
        except Exception as e:
            print(f"Error ejecutando accion Android '{action}': {e}")
            return False
    
    def take_screenshot(self, serial: str) -> bool:
        try:
            print(f"Tomando screenshot de {serial}")
            
            result = subprocess.run([
                self.adb_path, '-s', serial, 'shell', 'screencap', '/sdcard/screenshot.png'
            ], capture_output=True, timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW if self.is_windows else 0)
            
            if result.returncode != 0:
                return False
            
            screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
            os.makedirs(screenshots_dir, exist_ok=True)
            
            timestamp = int(time.time())
            local_path = os.path.join(screenshots_dir, f'android_{serial[-4:]}_{timestamp}.png')
            
            result = subprocess.run([
                self.adb_path, '-s', serial, 'pull', '/sdcard/screenshot.png', local_path
            ], capture_output=True, timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW if self.is_windows else 0)
            
            if result.returncode == 0:
                print(f"Screenshot guardado en: {local_path}")
                return True
            return False
                
        except Exception as e:
            print(f"Error tomando screenshot: {e}")
            return False