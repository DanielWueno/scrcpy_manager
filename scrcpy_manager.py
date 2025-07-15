#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrcpy Device Manager - Gestiona múltiples dispositivos Android con scrcpy
Autor: Asistente Claude
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime

class ScrcpyManager:
    def __init__(self):
        self.devices = []
        self.config_file = "scrcpy_devices.json"
        self.scrcpy_path = "scrcpy.exe"  # Cambiar si está en otra ubicación
        self.adb_path = "adb.exe"        # Cambiar si está en otra ubicación
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
    
    def get_connected_devices(self):
        """Obtiene lista de dispositivos conectados via ADB"""
        try:
            result = subprocess.run([self.adb_path, 'devices'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                print("Error: No se pudo ejecutar ADB. Verifica que esté en PATH.")
                return []
            
            lines = result.stdout.strip().split('\n')[1:]  # Saltar primera línea
            devices = []
            
            for line in lines:
                if line.strip() and '\tdevice' in line:
                    serial = line.split('\t')[0]
                    devices.append(serial)
            
            return devices
            
        except subprocess.TimeoutExpired:
            print("Error: Timeout ejecutando ADB")
            return []
        except FileNotFoundError:
            print("Error: ADB no encontrado. Verifica la instalación.")
            return []
        except Exception as e:
            print(f"Error obteniendo dispositivos: {e}")
            return []
    
    def get_device_info(self, serial):
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
    
    def update_device_list(self):
        """Actualiza la lista de dispositivos conectados"""
        print("Buscando dispositivos conectados...")
        connected = self.get_connected_devices()
        
        if not connected:
            print("ERROR: No se encontraron dispositivos conectados.")
            print("Verifica que:")
            print("   - El dispositivo esté conectado via USB")
            print("   - La depuración USB esté habilitada")
            print("   - ADB esté instalado y en PATH")
            return
        
        print(f"OK: Encontrados {len(connected)} dispositivo(s) conectado(s)")
        
        # Actualizar lista guardada
        for serial in connected:
            existing = next((d for d in self.devices if d['serial'] == serial), None)
            if not existing:
                info = self.get_device_info(serial)
                device = {
                    'serial': serial,
                    'name': info,
                    'alias': f"Device_{serial[-4:]}",  # Alias por defecto
                    'last_seen': datetime.now().isoformat()
                }
                self.devices.append(device)
                print(f"[+] Nuevo dispositivo: {device['alias']} ({info})")
            else:
                existing['last_seen'] = datetime.now().isoformat()
        
        self.save_devices()
    
    def show_devices(self):
        """Muestra lista de dispositivos"""
        if not self.devices:
            print("No hay dispositivos guardados. Usa opción 1 para buscar.")
            return
        
        print("\nDispositivos disponibles:")
        print("=" * 60)
        
        connected = self.get_connected_devices()
        
        for i, device in enumerate(self.devices, 1):
            status = "[CONECTADO]" if device['serial'] in connected else "[DESCONECTADO]"
            print(f"{i:2d}. {device['alias']:<15} | {device['name']:<20} | {status}")
            print(f"    Serial: {device['serial']}")
            print()
    
    def launch_scrcpy(self, device, options=""):
        """Lanza scrcpy para un dispositivo específico"""
        serial = device['serial']
        base_cmd = [self.scrcpy_path, "--no-audio", f"--serial={serial}"]
        
        if options:
            # Agregar opciones adicionales
            extra_options = options.split()
            base_cmd.extend(extra_options)
        
        print(f"Iniciando scrcpy para {device['alias']}...")
        print(f"Comando: {' '.join(base_cmd)}")
        
        try:
            subprocess.Popen(base_cmd)
            print(f"OK: Scrcpy iniciado para {device['alias']}")
        except FileNotFoundError:
            print("ERROR: scrcpy.exe no encontrado. Verifica la ruta.")
        except Exception as e:
            print(f"ERROR iniciando scrcpy: {e}")
    
    def launch_multiple(self, device_indices, options=""):
        """Lanza scrcpy para múltiples dispositivos"""
        if not device_indices:
            print("ERROR: No se seleccionaron dispositivos")
            return
        
        connected = self.get_connected_devices()
        
        for idx in device_indices:
            if 1 <= idx <= len(self.devices):
                device = self.devices[idx - 1]
                if device['serial'] in connected:
                    self.launch_scrcpy(device, options)
                    time.sleep(1)  # Esperar un poco entre lanzamientos
                else:
                    print(f"AVISO: {device['alias']} no está conectado")
            else:
                print(f"ERROR: Índice {idx} no válido")
    
    def manage_device_alias(self):
        """Permite cambiar el alias de un dispositivo"""
        if not self.devices:
            print("ERROR: No hay dispositivos para gestionar")
            return
        
        self.show_devices()
        try:
            idx = int(input("\nSelecciona dispositivo para cambiar alias (número): ")) - 1
            if 0 <= idx < len(self.devices):
                device = self.devices[idx]
                print(f"Alias actual: {device['alias']}")
                new_alias = input("Nuevo alias: ").strip()
                if new_alias:
                    device['alias'] = new_alias
                    self.save_devices()
                    print(f"OK: Alias cambiado a: {new_alias}")
                else:
                    print("ERROR: Alias no puede estar vacío")
            else:
                print("ERROR: Selección no válida")
        except ValueError:
            print("ERROR: Entrada no válida")
    
    def show_menu(self):
        """Muestra el menú principal"""
        print("\n" + "=" * 50)
        print("SCRCPY DEVICE MANAGER")
        print("=" * 50)
        print("1. Buscar dispositivos conectados")
        print("2. Mostrar todos los dispositivos")
        print("3. Conectar a un dispositivo")
        print("4. Conectar a múltiples dispositivos")
        print("5. Gestionar alias de dispositivos")
        print("6. Opciones avanzadas")
        print("0. Salir")
        print("=" * 50)
    
    def show_advanced_options(self):
        """Muestra opciones avanzadas de scrcpy"""
        print("\nOPCIONES COMUNES DE SCRCPY:")
        print("--stay-awake          : Mantener pantalla encendida")
        print("--turn-screen-off     : Apagar pantalla del dispositivo")
        print("--show-touches        : Mostrar toques en pantalla")
        print("--record=archivo.mp4  : Grabar sesión")
        print("--max-size=1024       : Limitar resolución")
        print("--bit-rate=2M         : Ajustar bitrate")
        print("--fullscreen          : Pantalla completa")
        print("--always-on-top       : Ventana siempre encima")
        print()
        print("Ejemplo: --stay-awake --show-touches --max-size=800")
    
    def run(self):
        """Ejecuta el programa principal"""
        print("Bienvenido a Scrcpy Device Manager")
        
        while True:
            self.show_menu()
            
            try:
                choice = input("\nSelecciona una opción: ").strip()
                
                if choice == '1':
                    self.update_device_list()
                
                elif choice == '2':
                    self.show_devices()
                
                elif choice == '3':
                    self.show_devices()
                    if self.devices:
                        device_idx = int(input("\nSelecciona dispositivo (número): ")) - 1
                        if 0 <= device_idx < len(self.devices):
                            print("\nOpciones adicionales (opcional, presiona Enter para continuar):")
                            options = input("Opciones: ").strip()
                            self.launch_scrcpy(self.devices[device_idx], options)
                        else:
                            print("ERROR: Selección no válida")
                
                elif choice == '4':
                    self.show_devices()
                    if self.devices:
                        indices_str = input("\nSelecciona dispositivos (ej: 1,3,4): ")
                        try:
                            indices = [int(x.strip()) for x in indices_str.split(',')]
                            print("\nOpciones adicionales (opcional):")
                            options = input("Opciones: ").strip()
                            self.launch_multiple(indices, options)
                        except ValueError:
                            print("ERROR: Formato no válido")
                
                elif choice == '5':
                    self.manage_device_alias()
                
                elif choice == '6':
                    self.show_advanced_options()
                
                elif choice == '0':
                    print("Hasta luego!")
                    break
                
                else:
                    print("ERROR: Opción no válida")
                    
            except KeyboardInterrupt:
                print("\n\nPrograma interrumpido por el usuario")
                break
            except ValueError:
                print("ERROR: Entrada no válida")
            except Exception as e:
                print(f"ERROR inesperado: {e}")

if __name__ == "__main__":
    manager = ScrcpyManager()
    manager.run()