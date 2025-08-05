#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Barra de herramientas estilo emulador con tooltips
"""

import tkinter as tk
from tkinter import ttk
from gui.tooltip import ToolTip

class ToolbarFrame(ttk.Frame):
    def __init__(self, parent, scrcpy_controller, on_action):
        super().__init__(parent)
        self.scrcpy_controller = scrcpy_controller
        self.on_action = on_action
        self.current_device = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la barra de herramientas"""
        # Título
        title_label = ttk.Label(self, text="🛠️ Herramientas", font=('Arial', 10, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Frame para botones principales
        main_tools_frame = ttk.LabelFrame(self, text="Captura y Control")
        main_tools_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Grid de botones principales
        buttons_grid = ttk.Frame(main_tools_frame)
        buttons_grid.pack(padx=5, pady=5)
        
        # Botones con iconos y texto
        self.create_tool_button(buttons_grid, "📸", "Screenshot", "screenshot", 
                               "Capturar pantalla del dispositivo", 0, 0)
        self.create_tool_button(buttons_grid, "🎬", "Record", "record",
                               "Grabar pantalla del dispositivo", 0, 1)
        
        # Frame para control de pantalla
        screen_frame = ttk.LabelFrame(self, text="Control de Pantalla")
        screen_frame.pack(fill=tk.X, pady=(0, 10))
        
        screen_grid = ttk.Frame(screen_frame)
        screen_grid.pack(padx=5, pady=5)
        
        # Botones diferenciados de pantalla
        self.create_tool_button(screen_grid, "🖥️", "Screen OFF", "screen_off",
                               "Apagar pantalla completamente", 0, 0)
        self.create_tool_button(screen_grid, "💡", "Screen ON", "screen_on", 
                               "Encender pantalla", 0, 1)
        self.create_tool_button(screen_grid, "👁️", "Mirror OFF", "mirror_screen_off",
                               "Apagar solo dispositivo (Alt+O)\nMantiene mirror activo", 1, 0)
        self.create_tool_button(screen_grid, "👁️‍🗨️", "Mirror ON", "mirror_screen_on",
                               "Encender pantalla en mirror (Alt+Shift+O)", 1, 1)
        
        # Separador
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Controles adicionales
        controls_frame = ttk.LabelFrame(self, text="Controles Rápidos")
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones de control con tooltips
        home_btn = ttk.Button(controls_frame, text="🏠 Home", 
                             command=lambda: self.send_keyevent("KEYCODE_HOME"))
        home_btn.pack(fill=tk.X, padx=5, pady=2)
        ToolTip(home_btn, "Ir a pantalla principal (Home)")
        
        back_btn = ttk.Button(controls_frame, text="⬅️ Atrás", 
                             command=lambda: self.send_keyevent("KEYCODE_BACK"))
        back_btn.pack(fill=tk.X, padx=5, pady=2)
        ToolTip(back_btn, "Botón Atrás")
        
        recent_btn = ttk.Button(controls_frame, text="📋 Recientes", 
                               command=lambda: self.send_keyevent("KEYCODE_APP_SWITCH"))
        recent_btn.pack(fill=tk.X, padx=5, pady=2)
        ToolTip(recent_btn, "Aplicaciones recientes")

        # Frame de estado con scroll propio si es necesario
        status_frame = ttk.LabelFrame(self, text="Estado del Dispositivo")
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Text widget con scroll para el estado
        status_container = ttk.Frame(status_frame)
        status_container.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_text = tk.Text(status_container, height=3, wrap=tk.WORD, 
                                  state=tk.DISABLED, font=("Arial", 9))
        status_scroll = ttk.Scrollbar(status_container, orient=tk.VERTICAL, 
                                     command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scroll.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        status_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Inicializar estado
        self.update_status_text("Sin dispositivo seleccionado")
        
        # Tooltip para el estado
        ToolTip(self.status_text, "Estado actual del dispositivo y última acción realizada")
    
    def create_tool_button(self, parent, icon, text, action, tooltip, row, col):
        """Crea un botón de herramienta con tooltip"""
        # Frame para botón completo
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=row, column=col, padx=3, pady=3, sticky="ew")
        
        # Botón principal
        btn = ttk.Button(btn_frame, text=f"{icon}\n{text}", width=12,
                        command=lambda: self.on_action(action))
        btn.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid weight
        parent.grid_columnconfigure(col, weight=1)
        
        # Agregar tooltip
        ToolTip(btn, tooltip)
        
        return btn
    
    def update_status_text(self, text):
        """Actualiza el texto de estado con scroll"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, text)
        self.status_text.config(state=tk.DISABLED)
        # Auto-scroll al final
        self.status_text.see(tk.END)
    
    def set_device(self, device):
        """Establece el dispositivo actual"""
        self.current_device = device
        if device:
            is_connected = self.scrcpy_controller.is_active(device['serial'])
            status_text = f"📱 Dispositivo: {device['alias']}\n"
            status_text += f"Modelo: {device['name']}\n"
            status_text += f"Serial: {device['serial']}\n"
            if is_connected:
                status_text += "🟢 Estado: Conectado y activo"
            else:
                status_text += "🔴 Estado: Desconectado"
            
            self.update_status_text(status_text)
        else:
            self.update_status_text("Sin dispositivo seleccionado\n\nSelecciona un dispositivo de la lista para ver sus controles")
    
    def send_keyevent(self, keycode):
        """Envía un evento de tecla al dispositivo"""
        if not self.current_device:
            return
        
        try:
            import subprocess
            subprocess.run(['adb.exe', '-s', self.current_device['serial'], 
                          'shell', 'input', 'keyevent', keycode], timeout=5)
        except:
            pass

import os
