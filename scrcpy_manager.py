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
    
    def silent_update_devices(self):
        """Actualiza dispositivos silenciosamente sin mostrar mensajes"""
        try:
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
                print(f"ℹ️  Se detectaron {new_devices_count} dispositivo(s) nuevo(s)")
        except:
            pass  # Fallar silenciosamente

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
    
    def show_devices(self, auto_update=True):
        """Muestra lista de dispositivos con auto-actualización opcional"""
        if auto_update:
            # Buscar nuevos dispositivos silenciosamente
            self.silent_update_devices()
        
        if not self.devices:
            print("No hay dispositivos guardados.")
            response = input("¿Buscar dispositivos ahora? (s/n): ").lower()
            if response == 's':
                self.update_device_list()
            return
        
        print("\nDispositivos disponibles:")
        print("=" * 70)
        
        connected = self.get_connected_devices()
        
        for i, device in enumerate(self.devices, 1):
            status = "🟢 CONECTADO" if device['serial'] in connected else "🔴 DESCONECTADO"
            print(f"{i:2d}. {device['alias']:<15} | {device['name']:<25} | {status}")
            print(f"    Serial: {device['serial']}")
            print()

    def show_scrcpy_options_menu(self):
        """Muestra menú interactivo para opciones de scrcpy"""
        print("\n" + "=" * 50)
        print("OPCIONES DE SCRCPY")
        print("=" * 50)
        print("1. 🔋 Mantener pantalla encendida (--stay-awake)")
        print("2. 🖥️  Apagar pantalla del dispositivo (--turn-screen-off)")
        print("3. 👆 Mostrar toques en pantalla (--show-touches)")
        print("4. 🎬 Grabar sesión (--record)")
        print("5. 📐 Limitar resolución (--max-size)")
        print("6. 🌐 Ajustar bitrate (--bit-rate)")
        print("7. 🖼️  Pantalla completa (--fullscreen)")
        print("8. 📌 Ventana siempre encima (--always-on-top)")
        print("9. 🔇 Sin audio (--no-audio) [Recomendado]")
        print("0. ✅ Continuar con opciones seleccionadas")
        print("=" * 50)
        
        selected_options = []
        
        while True:
            try:
                choice = input("\nSelecciona opción (0 para continuar): ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    if '--stay-awake' not in selected_options:
                        selected_options.append('--stay-awake')
                        print("✅ Mantener pantalla encendida activado")
                    else:
                        selected_options.remove('--stay-awake')
                        print("❌ Mantener pantalla encendida desactivado")
                
                elif choice == '2':
                    if '--turn-screen-off' not in selected_options:
                        selected_options.append('--turn-screen-off')
                        print("✅ Apagar pantalla activado")
                    else:
                        selected_options.remove('--turn-screen-off')
                        print("❌ Apagar pantalla desactivado")
                
                elif choice == '3':
                    if '--show-touches' not in selected_options:
                        selected_options.append('--show-touches')
                        print("✅ Mostrar toques activado")
                    else:
                        selected_options.remove('--show-touches')
                        print("❌ Mostrar toques desactivado")
                
                elif choice == '4':
                    filename = input("Nombre del archivo (ej: grabacion.mp4): ").strip()
                    if filename:
                        # Remover grabación anterior si existe
                        selected_options = [opt for opt in selected_options if not opt.startswith('--record=')]
                        selected_options.append(f'--record={filename}')
                        print(f"✅ Grabación activada: {filename}")
                
                elif choice == '5':
                    size = input("Resolución máxima (ej: 1024, 800): ").strip()
                    if size.isdigit():
                        # Remover resolución anterior si existe
                        selected_options = [opt for opt in selected_options if not opt.startswith('--max-size=')]
                        selected_options.append(f'--max-size={size}')
                        print(f"✅ Resolución máxima: {size}")
                    else:
                        print("❌ Valor no válido")
                
                elif choice == '6':
                    bitrate = input("Bitrate (ej: 2M, 8M): ").strip()
                    if bitrate:
                        # Remover bitrate anterior si existe
                        selected_options = [opt for opt in selected_options if not opt.startswith('--bit-rate=')]
                        selected_options.append(f'--bit-rate={bitrate}')
                        print(f"✅ Bitrate configurado: {bitrate}")
                
                elif choice == '7':
                    if '--fullscreen' not in selected_options:
                        selected_options.append('--fullscreen')
                        print("✅ Pantalla completa activada")
                    else:
                        selected_options.remove('--fullscreen')
                        print("❌ Pantalla completa desactivada")
                
                elif choice == '8':
                    if '--always-on-top' not in selected_options:
                        selected_options.append('--always-on-top')
                        print("✅ Ventana siempre encima activada")
                    else:
                        selected_options.remove('--always-on-top')
                        print("❌ Ventana siempre encima desactivada")
                
                elif choice == '9':
                    if '--no-audio' not in selected_options:
                        selected_options.append('--no-audio')
                        print("✅ Sin audio activado")
                    else:
                        selected_options.remove('--no-audio')
                        print("❌ Sin audio desactivado")
                
                else:
                    print("❌ Opción no válida")
                
                # Mostrar opciones actuales
                if selected_options:
                    print(f"\n📋 Opciones actuales: {' '.join(selected_options)}")
                
            except ValueError:
                print("❌ Entrada no válida")
            except KeyboardInterrupt:
                break
        
        return ' '.join(selected_options)

    def launch_scrcpy(self, device, options=""):
        """Lanza scrcpy para un dispositivo específico"""
        serial = device['serial']
        
        # Verificar si está conectado
        connected = self.get_connected_devices()
        if serial not in connected:
            print(f"❌ ERROR: {device['alias']} no está conectado")
            return False
        
        base_cmd = [self.scrcpy_path, f"--serial={serial}"]
        
        # Agregar --no-audio por defecto si no se especifica audio
        if options and '--no-audio' not in options and '--audio' not in options:
            base_cmd.append('--no-audio')
        elif not options:
            base_cmd.append('--no-audio')
        
        if options:
            extra_options = options.split()
            base_cmd.extend(extra_options)
        
        print(f"🚀 Iniciando scrcpy para {device['alias']}...")
        print(f"📋 Comando: {' '.join(base_cmd)}")
        
        try:
            subprocess.Popen(base_cmd)
            print(f"✅ Scrcpy iniciado para {device['alias']}")
            return True
        except FileNotFoundError:
            print("❌ ERROR: scrcpy.exe no encontrado. Verifica la ruta.")
            return False
        except Exception as e:
            print(f"❌ ERROR iniciando scrcpy: {e}")
            return False

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
                            print("\n¿Configurar opciones de scrcpy?")
                            print("1. Usar configuración rápida (recomendado)")
                            print("2. Configurar opciones personalizadas")
                            print("3. Sin opciones adicionales")
                            
                            config_choice = input("Selecciona (1-3): ").strip()
                            
                            if config_choice == '1':
                                # Configuración rápida recomendada
                                options = "--stay-awake --show-touches --no-audio"
                                print(f"📋 Usando configuración rápida: {options}")
                            elif config_choice == '2':
                                options = self.show_scrcpy_options_menu()
                            else:
                                options = ""
                            
                            self.launch_scrcpy(self.devices[device_idx], options)
                        else:
                            print("❌ ERROR: Selección no válida")
                
                elif choice == '4':
                    self.show_devices()
                    if self.devices:
                        indices_str = input("\nSelecciona dispositivos (ej: 1,3,4): ")
                        try:
                            indices = [int(x.strip()) for x in indices_str.split(',')]
                            
                            print("\n¿Configurar opciones de scrcpy para todos?")
                            print("1. Usar configuración rápida (recomendado)")
                            print("2. Configurar opciones personalizadas")
                            print("3. Sin opciones adicionales")
                            
                            config_choice = input("Selecciona (1-3): ").strip()
                            
                            if config_choice == '1':
                                options = "--stay-awake --show-touches --no-audio"
                                print(f"📋 Usando configuración rápida: {options}")
                            elif config_choice == '2':
                                options = self.show_scrcpy_options_menu()
                            else:
                                options = ""
                            
                            self.launch_multiple(indices, options)
                        except ValueError:
                            print("❌ ERROR: Formato no válido")
                
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
                            