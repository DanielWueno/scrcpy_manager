import subprocess
import json
import os
import time
import tempfile
import platform
from typing import List, Dict, Optional, Any
from datetime import datetime
from ..base.base_device_manager import BaseDeviceManager

class IOSManager(BaseDeviceManager):
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.ios_video_stream_path = self._find_ios_video_stream()
        self.idevice_tools_path = self._find_idevice_tools()
        self.active_streams = {}
    
    @property
    def platform(self) -> str:
        return "ios"
    
    def _find_ios_video_stream(self) -> str:
        """Encuentra el ejecutable de ios_video_stream en Windows"""
        if self.is_windows:
            possible_paths = [
                "ios_video_stream.exe",
                "C:\\tools\\ios_video_stream\\ios_video_stream.exe",
                "C:\\Program Files\\ios_video_stream\\ios_video_stream.exe",
                ".\\tools\\ios_video_stream.exe",
                os.path.join(os.getcwd(), "tools", "ios_video_stream.exe")
            ]
        else:
            possible_paths = [
                "ios_video_stream",
                "./ios_video_stream",
                "/usr/local/bin/ios_video_stream"
            ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--help"], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0 or "usage" in result.stderr.decode().lower():
                    print(f"Encontrado ios_video_stream en: {path}")
                    return path
            except Exception as e:
                continue
        
        print("WARNING: ios_video_stream no encontrado")
        print("Instálalo desde: https://github.com/nanoscopic/ios_video_stream")
        return "ios_video_stream.exe" if self.is_windows else "ios_video_stream"
    
    def _find_idevice_tools(self) -> str:
        """Encuentra las herramientas libimobiledevice en Windows"""
        if self.is_windows:
            possible_bases = [
                "C:\\tools\\libimobiledevice",
                "C:\\Program Files\\libimobiledevice",
                "C:\\libimobiledevice",
                ".\\tools\\libimobiledevice",
                os.path.join(os.getcwd(), "tools", "libimobiledevice")
            ]
            
            for base_path in possible_bases:
                idevice_id_path = os.path.join(base_path, "idevice_id.exe")
                if os.path.exists(idevice_id_path):
                    try:
                        result = subprocess.run([idevice_id_path, "--help"], 
                                              capture_output=True, timeout=5)
                        if result.returncode == 0 or "usage" in result.stderr.decode().lower():
                            print(f"Encontrado libimobiledevice en: {base_path}")
                            return base_path
                    except:
                        continue
        else:
            try:
                result = subprocess.run(["idevice_id", "--help"], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    return ""  # En PATH
            except:
                pass
        
        print("WARNING: libimobiledevice no encontrado")
        print("Para Windows, descarga desde: https://github.com/libimobiledevice-win32/imobiledevice-net/releases")
        return "C:\\tools\\libimobiledevice" if self.is_windows else ""
    
    def _get_tool_path(self, tool_name: str) -> str:
        """Obtiene la ruta completa de una herramienta"""
        if self.is_windows:
            if self.idevice_tools_path:
                return os.path.join(self.idevice_tools_path, f"{tool_name}.exe")
            else:
                return f"{tool_name}.exe"
        else:
            return tool_name
    
    def get_connected_devices(self) -> List[str]:
        """Obtiene lista de dispositivos iOS conectados"""
        try:
            idevice_id_path = self._get_tool_path("idevice_id")
            result = subprocess.run([idevice_id_path, "-l"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                print(f"Error ejecutando idevice_id: {result.stderr}")
                return []
            
            devices = []
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if line and len(line) > 10:  # UDIDs tienen más de 10 caracteres
                    devices.append(line)
            
            print(f"Dispositivos iOS encontrados: {devices}")
            return devices
            
        except Exception as e:
            print(f"Error obteniendo dispositivos iOS: {e}")
            return []
    
    def get_device_info(self, udid: str) -> Dict:
        """Obtiene información del dispositivo iOS"""
        try:
            ideviceinfo_path = self._get_tool_path("ideviceinfo")
            result = subprocess.run([ideviceinfo_path, "-u", udid], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode != 0:
                print(f"Error obteniendo info del dispositivo: {result.stderr}")
                return self._get_fallback_info(udid)
            
            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            device_info = {
                "name": info.get("DeviceName", f"iPhone {udid[-4:]}"),
                "model": info.get("ProductType", "iPhone"),
                "ios_version": info.get("ProductVersion", "Desconocido"),
                "build_version": info.get("BuildVersion", "Desconocido"),
                "platform": "ios"
            }
            
            print(f"Info del dispositivo {udid[:8]}...: {device_info['name']} ({device_info['model']})")
            return device_info
            
        except Exception as e:
            print(f"Error obteniendo info de dispositivo iOS: {e}")
            return self._get_fallback_info(udid)
    
    def _get_fallback_info(self, udid: str) -> Dict:
        """Info de fallback cuando no se puede obtener información"""
        return {
            "name": f"iPhone {udid[-4:]}",
            "model": "iPhone",
            "ios_version": "Desconocido",
            "build_version": "Desconocido",
            "platform": "ios"
        }
    
    def start_mirror(self, udid: str, options: Dict = None) -> bool:
        """Inicia el mirror de un dispositivo iOS"""
        try:
            # ✅ Limpiar procesos existentes PRIMERO
            self._kill_existing_ios_video_stream_processes()
            
            # ✅ Verificar y limpiar estado inconsistente PRIMERO
            if udid in self.active_streams:
                stream_data = self.active_streams[udid]
                process = stream_data.get('process')
                
                if not process or process.poll() is not None:
                    print(f"🧹 Limpiando estado inconsistente para {udid[:8]}...")
                    del self.active_streams[udid]
                else:
                    print(f"Mirror ya activo para {udid[:8]}...")
                    return True
            
            # ✅ Verificar si ios_video_stream existe
            if not self._check_ios_video_stream_exists():
                print("ios_video_stream no encontrado. Usando método alternativo...")
                return self._start_mirror_alternative(udid, options)
            
            # ✅ Configurar puertos dinámicos para evitar conflictos
            port = options.get('port', 8000) if options else 8000
            internal_port = self._find_available_port(7879)  # Puerto interno dinámico
            
            cmd = [self.ios_video_stream_path]
            
            # Parámetro UDID correcto
            cmd.extend(["-udid", udid])
            
            # Puerto de salida HTTP
            cmd.extend(["-port", str(port)])
            
            # ✅ Configurar puerto interno con pullSpec
            cmd.extend(["-pullSpec", f"tcp://127.0.0.1:{internal_port}"])
            
            # Configurar opciones adicionales
            if options:
                # Interfaz de red
                interface = options.get('interface', 'none')
                if interface != 'none':
                    cmd.extend(["-interface", interface])
                
                # Modo stream
                if options.get('stream', True):
                    cmd.append("-stream")
                
                # Verbose para debugging
                if options.get('verbose', False):
                    cmd.append("-v")
            else:
                # Configuración por defecto
                cmd.append("-stream")
            
            print(f"Iniciando iOS mirror: {' '.join(cmd)}")
            print(f"Puerto HTTP: {port}, Puerto interno: {internal_port}")
            
            # En Windows, usar CREATE_NEW_PROCESS_GROUP
            if self.is_windows:
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    start_new_session=True
                )
            
            # Esperar un momento para verificar que inició correctamente
            time.sleep(5)  # Aumentar tiempo de espera
            
            if process.poll() is None:  # Proceso aún corriendo
                self.active_streams[udid] = {
                    'process': process,
                    'started_at': datetime.now().isoformat(),
                    'port': port,
                    'internal_port': internal_port,
                    'options': options or {},
                    'stream_url': f"http://localhost:{port}"
                }
                print(f"✅ Mirror iOS iniciado exitosamente para {udid[:8]}...")
                print(f"🌐 Stream disponible en: http://localhost:{port}")
                return True
            else:
                # El proceso terminó, hubo un error
                stdout, stderr = process.communicate()
                print(f"❌ Error en iOS mirror - stdout: {stdout.decode()}")
                print(f"❌ Error en iOS mirror - stderr: {stderr.decode()}")
                return False
            
        except Exception as e:
            print(f"❌ Error iniciando mirror iOS: {e}")
            return False

    def _find_available_port(self, start_port: int = 7879) -> int:
        """Encuentra un puerto disponible starting from start_port"""
        import socket
        
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    print(f"Puerto {port} disponible")
                    return port
            except OSError:
                continue
        
        # Fallback al puerto original si no encuentra ninguno
        print(f"No se encontró puerto disponible, usando {start_port}")
        return start_port
    
    def _check_ios_video_stream_exists(self) -> bool:
        """Verifica si ios_video_stream existe"""
        return os.path.exists(self.ios_video_stream_path)

    def _start_mirror_alternative(self, udid: str, options: Dict = None) -> bool:
        """Método alternativo para mirror iOS sin ios_video_stream"""
        try:
            print(f"🔄 Mirror iOS simulado para {udid[:8]}... (falta ios_video_stream)")
            
            port = options.get('port', 8000) if options else 8000
            
            # Crear entrada simulada en active_streams
            self.active_streams[udid] = {
                'process': None,  # Sin proceso real
                'started_at': datetime.now().isoformat(),
                'port': port,
                'options': options or {},
                'simulated': True,  # Marcar como simulado
                'stream_url': f"http://localhost:{port} (simulado)"
            }
            
            print("📱 Para mirror real, instala ios_video_stream desde:")
            print("   https://github.com/nanoscopic/ios_video_stream/releases")
            print(f"🔧 O ejecuta: choco install ios_video_stream")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en mirror alternativo: {e}")
            return False
    
    def stop_mirror(self, udid: str) -> bool:
        """Detiene el mirror de un dispositivo iOS"""
        try:
            if udid not in self.active_streams:
                print(f"No hay mirror activo para {udid[:8]}...")
                return True
            
            stream_data = self.active_streams[udid]
            process = stream_data['process']
            
            # En Windows, usar terminate diferente
            if self.is_windows:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # En Windows, usar taskkill como fallback
                    subprocess.run(['taskkill', '/F', '/PID', str(process.pid)], 
                                 capture_output=True)
            else:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=2)
            
            # Remover de streams activos
            del self.active_streams[udid]
            print(f"Mirror iOS detenido para {udid[:8]}...")
            return True
            
        except Exception as e:
            print(f"Error deteniendo mirror iOS: {e}")
            return False
    
    # ✅ MÉTODO FALTANTE - is_mirror_active
    def is_mirror_active(self, udid: str) -> bool:
        """Verifica si el mirror está activo para un dispositivo iOS"""
        if udid not in self.active_streams:
            return False
        
        stream_data = self.active_streams[udid]
        
        # ✅ Si es simulado, siempre está "activo"
        if stream_data.get('simulated'):
            return True
        
        # ✅ Verificar proceso real
        process = stream_data.get('process')
        
        # Si no hay proceso, limpiar estado
        if not process:
            print(f"🧹 Limpiando estado fantasma para {udid[:8]}...")
            del self.active_streams[udid]
            return False
        
        # Si el proceso terminó, limpiar estado
        if process.poll() is not None:
            print(f"🧹 Proceso terminado, limpiando estado para {udid[:8]}...")
            del self.active_streams[udid]
            return False
        
        return True
    
    def take_screenshot(self, udid: str) -> Optional[bytes]:
        """Toma captura de pantalla del dispositivo iOS"""
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            # Tomar captura
            idevicescreenshot_path = self._get_tool_path("idevicescreenshot")
            result = subprocess.run([
                idevicescreenshot_path, 
                "-u", udid, 
                temp_path
            ], capture_output=True, timeout=15)
            
            if result.returncode == 0 and os.path.exists(temp_path):
                print(f"Captura iOS tomada: {temp_path}")
                # Leer el archivo y devolver bytes
                with open(temp_path, 'rb') as f:
                    screenshot_data = f.read()
                
                # Limpiar archivo temporal
                os.unlink(temp_path)
                return screenshot_data
            
            # Limpiar si falló
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            
            print(f"Error tomando captura iOS: {result.stderr.decode() if result.stderr else 'Desconocido'}")
            return None
            
        except Exception as e:
            print(f"Error tomando captura iOS: {e}")
            return None
    
    def execute_action(self, udid: str, action: str, payload: Any = None) -> Dict:
        """Ejecuta acción específica de iOS"""
        try:
            print(f"Ejecutando acción iOS '{action}' en {udid[:8]}...")
            
            if action == "ios_mirror":
                success = self.start_mirror(udid, payload)
                return {
                    'success': success,
                    'message': 'Mirror iOS iniciado' if success else 'Error iniciando mirror'
                }
            
            elif action == "ios_stop_mirror":
                success = self.stop_mirror(udid)
                return {
                    'success': success,
                    'message': 'Mirror iOS detenido' if success else 'Error deteniendo mirror'
                }
            
            elif action == "ios_screenshot":
                screenshot_data = self.take_screenshot(udid)
                if screenshot_data:
                    return {
                        'success': True,
                        'data': screenshot_data,
                        'message': 'Captura tomada'
                    }
                else:
                    return {'success': False, 'error': 'Error tomando captura'}
            
            elif action in ["ios_home_button", "ios_lock_device", "ios_volume_up", "ios_volume_down"]:
                # Para estas acciones, simular éxito ya que requieren herramientas adicionales
                return {
                    'success': True,
                    'message': f'Acción {action} simulada (requiere herramientas adicionales en Windows)'
                }
            
            else:
                return {'success': False, 'error': f'Acción iOS no soportada: {action}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def check_dependencies(self) -> Dict:
        """Verifica que las dependencias de iOS estén instaladas"""
        status = {
            'libimobiledevice': False,
            'ios_video_stream': False,
            'missing_tools': [],
            'install_instructions': []
        }
        
        # Verificar libimobiledevice
        try:
            idevice_id_path = self._get_tool_path("idevice_id")
            result = subprocess.run([idevice_id_path, "--version"], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                status['libimobiledevice'] = True
            else:
                status['missing_tools'].append('libimobiledevice')
        except:
            status['missing_tools'].append('libimobiledevice')
        
        # Verificar ios_video_stream
        try:
            result = subprocess.run([self.ios_video_stream_path, "--help"], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0 or "usage" in result.stderr.decode().lower():
                status['ios_video_stream'] = True
            else:
                status['missing_tools'].append('ios_video_stream')
        except:
            status['missing_tools'].append('ios_video_stream')
        
        # Instrucciones de instalación para Windows
        if self.is_windows and status['missing_tools']:
            status['install_instructions'] = [
                "Para Windows:",
                "1. Ejecutar: choco install libimobiledevice",
                "2. O descargar desde: https://github.com/libimobiledevice-win32/imobiledevice-net/releases",
                "3. Descargar ios_video_stream desde: https://github.com/nanoscopic/ios_video_stream/releases",
                "4. Extraer en C:\\tools\\libimobiledevice\\ y C:\\tools\\ios_video_stream\\"
            ]
        
        return status

    def _kill_existing_ios_video_stream_processes(self):
        """Mata procesos existentes de ios_video_stream que puedan estar bloqueando puertos"""
        try:
            if self.is_windows:
                # En Windows, usar tasklist y taskkill
                result = subprocess.run([
                    'tasklist', '/FI', 'IMAGENAME eq ios_video_stream.exe'
                ], capture_output=True, text=True)
                
                if 'ios_video_stream.exe' in result.stdout:
                    print("🔄 Matando procesos ios_video_stream existentes...")
                    subprocess.run([
                        'taskkill', '/F', '/IM', 'ios_video_stream.exe'
                    ], capture_output=True)
                    time.sleep(2)  # Esperar a que se liberen los puertos
            else:
                # En Linux/macOS
                subprocess.run(['pkill', '-f', 'ios_video_stream'], capture_output=True)
                time.sleep(2)
                
        except Exception as e:
            print(f"Error matando procesos existentes: {e}")