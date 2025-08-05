#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ventana principal de la GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from core.device_manager import DeviceManager
from core.scrcpy_controller import ScrcpyController
from gui.device_panel import DevicePanel
from gui.toolbar import ToolbarFrame

class ScrcpyManagerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.device_manager = DeviceManager()
        self.scrcpy_controller = ScrcpyController()
        self.selected_device = None
        
        self.setup_ui()
        self.setup_auto_refresh()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.root.title("Scrcpy Device Manager")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        self.root.resizable(True, True)
        
        # IMPORTANTE: Fijar propagación de geometría
        self.root.grid_propagate(False)
        self.root.pack_propagate(False)
        
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal con tamaño fijo
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_frame.pack_propagate(False)
        
        # Panel de dispositivos (izquierda)
        self.device_panel = DevicePanel(main_frame, self.device_manager, self.on_device_selected)
        self.device_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Panel de control (derecha) con scroll
        self.setup_scrollable_control_panel(main_frame)
        
        # Status bar con altura fija
        status_frame = ttk.Frame(self.root, height=25)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Listo")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.BOTH, expand=True)
        
        # Agregar tooltip al status bar
        from gui.tooltip import ToolTip
        ToolTip(status_bar, "Estado de la aplicación y acciones realizadas")
    
    def setup_scrollable_control_panel(self, parent):
        """Configura panel de control con scroll"""
        # Frame contenedor para el panel derecho
        control_container = ttk.Frame(parent, width=320)
        control_container.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        control_container.pack_propagate(False)
        
        # Canvas y scrollbar para scroll vertical
        canvas = tk.Canvas(control_container, width=300)
        scrollbar = ttk.Scrollbar(control_container, orient="vertical", command=canvas.yview)
        
        # Frame scrolleable que contendrá todos los controles
        self.scrollable_frame = ttk.Frame(canvas)
        
        # Configurar scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Crear ventana en canvas
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel para scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Configurar contenido del panel scrolleable
        self.setup_control_content()
    
    def setup_control_content(self):
        """Configura el contenido del panel de control"""
        # Toolbar
        self.toolbar = ToolbarFrame(self.scrollable_frame, self.scrcpy_controller, self.on_toolbar_action)
        self.toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Separador
        ttk.Separator(self.scrollable_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Botones principales (RESTAURADOS)
        self.setup_main_buttons(self.scrollable_frame)
        
        # Separador
        ttk.Separator(self.scrollable_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # Configuración rápida (RESTAURADA)
        self.setup_quick_config(self.scrollable_frame)
    
    def setup_main_buttons(self, parent):
        """Configura botones principales"""
        buttons_frame = ttk.LabelFrame(parent, text="Acciones Principales")
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botón conectar/desconectar
        self.connect_btn = ttk.Button(buttons_frame, text="Conectar Dispositivo", 
                                     command=self.toggle_connection, state=tk.DISABLED)
        self.connect_btn.pack(fill=tk.X, padx=5, pady=5)
        
        from gui.tooltip import ToolTip
        ToolTip(self.connect_btn, "Conectar o desconectar el dispositivo seleccionado")
        
        # Botón actualizar dispositivos
        refresh_btn = ttk.Button(buttons_frame, text="🔄 Actualizar Dispositivos", 
                               command=self.refresh_devices)
        refresh_btn.pack(fill=tk.X, padx=5, pady=5)
        ToolTip(refresh_btn, "Buscar nuevos dispositivos conectados")
    
    def setup_quick_config(self, parent):
        """Configura opciones de configuración rápida"""
        quick_config_frame = ttk.LabelFrame(parent, text="Configuración Rápida")
        quick_config_frame.pack(fill=tk.X, pady=(0, 10))
        
        from gui.tooltip import ToolTip
        
        # Stay awake - activado por defecto
        self.stay_awake_var = tk.BooleanVar(value=True)
        stay_awake_check = ttk.Checkbutton(quick_config_frame, text="Mantener pantalla encendida", 
                                          variable=self.stay_awake_var)
        stay_awake_check.pack(anchor=tk.W, padx=5, pady=2)
        ToolTip(stay_awake_check, "Evitar que la pantalla del dispositivo se apague automáticamente")
        
        # Show touches - desactivado por defecto
        self.show_touches_var = tk.BooleanVar(value=False)
        show_touches_check = ttk.Checkbutton(quick_config_frame, text="Mostrar toques", 
                                            variable=self.show_touches_var)
        show_touches_check.pack(anchor=tk.W, padx=5, pady=2)
        ToolTip(show_touches_check, "Mostrar círculos donde tocas la pantalla")
        
        # No audio - activado por defecto
        self.no_audio_var = tk.BooleanVar(value=True)
        no_audio_check = ttk.Checkbutton(quick_config_frame, text="Sin audio", 
                                        variable=self.no_audio_var)
        no_audio_check.pack(anchor=tk.W, padx=5, pady=2)
        ToolTip(no_audio_check, "Desactivar transmisión de audio (recomendado para mejor rendimiento)")
        
        # Opciones adicionales
        self.turn_screen_off_var = tk.BooleanVar(value=False)
        screen_off_check = ttk.Checkbutton(quick_config_frame, text="Apagar pantalla al conectar", 
                                          variable=self.turn_screen_off_var)
        screen_off_check.pack(anchor=tk.W, padx=5, pady=2)
        ToolTip(screen_off_check, "Apagar automáticamente la pantalla del dispositivo al iniciar mirror")
    
    def setup_auto_refresh(self):
        """Configura actualización automática optimizada"""
        def auto_refresh():
            while True:
                try:
                    # Solo actualizar dispositivos
                    new_devices = self.device_manager.update_devices_list()
                    
                    # Actualizar lista de dispositivos (preservando selección)
                    self.root.after(0, lambda: self.device_panel.refresh_devices(preserve_selection=True))
                    
                    # Solo mostrar mensaje si hay nuevos dispositivos
                    if new_devices > 0:
                        self.root.after(0, lambda: self.status_var.set(f"Se detectaron {new_devices} dispositivo(s) nuevo(s)"))
                    
                    # Si hay dispositivo seleccionado, actualizar solo su estado
                    if self.selected_device:
                        self.root.after(0, self.update_selected_device_status)
                    
                    time.sleep(5)  # Actualizar cada 5 segundos
                except:
                    break
        
        thread = threading.Thread(target=auto_refresh, daemon=True)
        thread.start()
    
    def on_device_selected(self, device):
        """Callback cuando se selecciona un dispositivo"""
        self.selected_device = device
        if device:
            self.connect_btn.config(state=tk.NORMAL)
            is_active = self.scrcpy_controller.is_active(device['serial'])
            self.connect_btn.config(text="Desconectar" if is_active else "Conectar Dispositivo")
            self.toolbar.set_device(device)
            self.status_var.set(f"Dispositivo seleccionado: {device['alias']}")
        else:
            self.connect_btn.config(state=tk.DISABLED, text="Conectar Dispositivo")
            self.toolbar.set_device(None)
            self.status_var.set("Listo")
    
    def update_selected_device_status(self):
        """Actualiza solo el estado del dispositivo seleccionado"""
        if self.selected_device:
            # Actualizar botón de conexión
            is_active = self.scrcpy_controller.is_active(self.selected_device['serial'])
            self.connect_btn.config(text="Desconectar" if is_active else "Conectar Dispositivo")
            
            # Actualizar toolbar
            self.toolbar.set_device(self.selected_device)
    
    def toggle_connection(self):
        """Alterna conexión del dispositivo seleccionado"""
        if not self.selected_device:
            return
        
        serial = self.selected_device['serial']
        is_active = self.scrcpy_controller.is_active(serial)
        
        if is_active:
            # Desconectar
            if self.scrcpy_controller.stop_scrcpy(serial):
                self.connect_btn.config(text="Conectar Dispositivo")
                self.status_var.set(f"Desconectado de {self.selected_device['alias']}")
                self.toolbar.set_device(self.selected_device)  # Actualizar toolbar
        else:
            # Conectar
            options = self.get_connection_options()
            if self.scrcpy_controller.start_scrcpy(self.selected_device, options):
                self.connect_btn.config(text="Desconectar")
                self.status_var.set(f"Conectado a {self.selected_device['alias']}")
                self.toolbar.set_device(self.selected_device)  # Actualizar toolbar
            else:
                messagebox.showerror("Error", "No se pudo conectar al dispositivo")
    
    def get_connection_options(self):
        """Obtiene opciones de conexión basadas en la configuración"""
        options = []
        
        if self.no_audio_var.get():
            options.append("--no-audio")
        
        if self.stay_awake_var.get():
            options.append("--stay-awake")
        
        if self.show_touches_var.get():
            options.append("--show-touches")
        
        if self.turn_screen_off_var.get():
            options.append("--turn-screen-off")
        
        return options
    
    def refresh_devices(self):
        """Actualiza lista de dispositivos manualmente"""
        new_devices = self.device_manager.update_devices_list()
        self.device_panel.refresh_devices(preserve_selection=False)  # Refresh completo manual
        self.status_var.set(f"Actualizado. {new_devices} dispositivo(s) nuevo(s)")
    
    def on_toolbar_action(self, action, *args):
        """Callback para acciones de toolbar"""
        if not self.selected_device:
            messagebox.showwarning("Advertencia", "Selecciona un dispositivo primero")
            return
        
        serial = self.selected_device['serial']
        
        try:
            if action == "screenshot":
                self.handle_screenshot(serial)
            elif action == "record":
                self.handle_recording(serial)
            elif action == "screen_off":
                if self.scrcpy_controller.screen_off(serial):
                    self.status_var.set("Pantalla apagada completamente")
                    self.toolbar.update_status_text("🖥️ Pantalla apagada completamente")
            elif action == "screen_on":
                if self.scrcpy_controller.screen_on(serial):
                    self.status_var.set("Pantalla encendida")
                    self.toolbar.update_status_text("💡 Pantalla encendida")
            elif action == "mirror_screen_off":
                if self.scrcpy_controller.mirror_screen_off(serial):
                    self.status_var.set("Pantalla del dispositivo apagada (mirror activo)")
                    self.toolbar.update_status_text("👁️ Pantalla del dispositivo apagada\nMirror sigue activo")
            elif action == "mirror_screen_on":
                if self.scrcpy_controller.mirror_screen_on(serial):
                    self.status_var.set("Pantalla del dispositivo encendida")
                    self.toolbar.update_status_text("👁️‍🗨️ Pantalla del dispositivo encendida")
        except Exception as e:
            messagebox.showerror("Error", f"Error en acción {action}: {str(e)}")
    
    def handle_screenshot(self, serial):
        """Maneja captura de pantalla de forma segura"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            title="Guardar captura de pantalla",
            initialname=f"screenshot_{self.selected_device['alias']}.png"
        )
        if filename:
            if self.scrcpy_controller.take_screenshot(serial, filename):
                self.status_var.set(f"📸 Captura guardada: {filename}")
                self.toolbar.update_status_text(f"📸 Captura de pantalla guardada:\n{filename}")
            else:
                messagebox.showerror("Error", "No se pudo tomar la captura")
                self.toolbar.update_status_text("❌ Error al tomar captura de pantalla")
    
    def handle_recording(self, serial):
        """Maneja grabación de forma segura"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4")],
            title="Guardar grabación",
            initialname=f"recording_{self.selected_device['alias']}.mp4"
        )
        if filename:
            # Usar método seguro que no cierra scrcpy
            if self.scrcpy_controller.start_recording_safe(self.selected_device, filename):
                self.status_var.set(f"🎬 Grabando a: {filename}")
                self.toolbar.update_status_text(f"🎬 Grabación iniciada:\n{filename}")
            else:
                messagebox.showerror("Error", "No se pudo iniciar la grabación")
                self.toolbar.update_status_text("❌ Error al iniciar grabación")
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()