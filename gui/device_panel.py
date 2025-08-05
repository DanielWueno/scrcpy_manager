#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Panel de dispositivos
"""

import tkinter as tk
from tkinter import ttk, messagebox

class DevicePanel(ttk.Frame):
    def __init__(self, parent, device_manager, on_device_selected):
        super().__init__(parent)
        self.device_manager = device_manager
        self.on_device_selected = on_device_selected
        self.selected_device = None
        self.selected_serial = None  # Añadir para rastrear selección
        
        self.setup_ui()
        self.refresh_devices()
    
    def setup_ui(self):
        """Configura la interfaz del panel"""
        # Título
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="📱 Dispositivos", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Botón refresh pequeño
        refresh_btn = ttk.Button(title_frame, text="🔄", width=3, 
                               command=self.manual_refresh)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Lista de dispositivos
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para dispositivos
        columns = ('status', 'alias', 'name')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        # Configurar columnas
        self.tree.heading('status', text='Estado')
        self.tree.heading('alias', text='Alias')
        self.tree.heading('name', text='Dispositivo')
        
        self.tree.column('status', width=80, minwidth=80)
        self.tree.column('alias', width=120, minwidth=100)
        self.tree.column('name', width=200, minwidth=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview y scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind eventos
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # Frame de información del dispositivo seleccionado
        info_frame = ttk.LabelFrame(self, text="Información del Dispositivo")
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.info_text = tk.Text(info_frame, height=4, wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame para cambiar alias
        alias_frame = ttk.Frame(info_frame)
        alias_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Label(alias_frame, text="Alias:").pack(side=tk.LEFT)
        self.alias_entry = ttk.Entry(alias_frame)
        self.alias_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        ttk.Button(alias_frame, text="Cambiar", command=self.change_alias).pack(side=tk.RIGHT)
    
    def refresh_devices(self, preserve_selection=True):
        """Actualiza la lista de dispositivos preservando la selección"""
        # Guardar selección actual si existe
        current_selection = None
        if preserve_selection and self.selected_serial:
            current_selection = self.selected_serial
        
        # Limpiar lista
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener dispositivos con estado
        devices_status = self.device_manager.get_devices_status()
        
        item_to_select = None
        for device in devices_status:
            status_icon = "🟢" if device['connected'] else "🔴"
            status_text = "Conectado" if device['connected'] else "Desconectado"
            
            item_id = self.tree.insert('', tk.END, values=(
                f"{status_icon} {status_text}",
                device['alias'],
                device['name']
            ), tags=(device['serial'],))
            
            # Marcar item para reselección
            if current_selection and device['serial'] == current_selection:
                item_to_select = item_id
        
        # Restaurar selección si existe
        if item_to_select:
            self.tree.selection_set(item_to_select)
            self.tree.focus(item_to_select)
            # Actualizar información sin triggerar callback
            device = self.device_manager.get_device_by_serial(current_selection)
            if device:
                self.selected_device = device
                self.update_device_info(device)
    
    def manual_refresh(self):
        """Refresh manual que no preserva selección"""
        self.refresh_devices(preserve_selection=False)
    
    def on_select(self, event):
        """Maneja selección de dispositivo"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            tags = self.tree.item(item, 'tags')
            if tags:
                serial = tags[0]
                device = self.device_manager.get_device_by_serial(serial)
                if device:
                    self.selected_device = device
                    self.selected_serial = serial  # Guardar serial para preservar selección
                    self.update_device_info(device)
                    self.on_device_selected(device)
        else:
            self.selected_device = None
            self.selected_serial = None
            self.update_device_info(None)
            self.on_device_selected(None)
    
    def on_double_click(self, event):
        """Maneja doble clic en dispositivo"""
        if self.selected_device:
            # Aquí podrías agregar acción por defecto, como conectar
            pass
    
    def update_device_info(self, device):
        """Actualiza información del dispositivo seleccionado"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        if device:
            connected = device['serial'] in self.device_manager.get_connected_devices()
            status = "🟢 CONECTADO" if connected else "🔴 DESCONECTADO"
            
            info = f"Estado: {status}\n"
            info += f"Alias: {device['alias']}\n"
            info += f"Dispositivo: {device['name']}\n"
            info += f"Serial: {device['serial']}\n"
            if 'last_seen' in device:
                info += f"Última conexión: {device['last_seen'][:19]}"
            
            self.info_text.insert(1.0, info)
            self.alias_entry.delete(0, tk.END)
            self.alias_entry.insert(0, device['alias'])
        else:
            self.info_text.insert(1.0, "Selecciona un dispositivo para ver su información")
            self.alias_entry.delete(0, tk.END)
        
        self.info_text.config(state=tk.DISABLED)
    
    def change_alias(self):
        """Cambia el alias del dispositivo seleccionado"""
        if not self.selected_device:
            messagebox.showwarning("Advertencia", "Selecciona un dispositivo primero")
            return
        
        new_alias = self.alias_entry.get().strip()
        if not new_alias:
            messagebox.showwarning("Advertencia", "El alias no puede estar vacío")
            return
        
        if self.device_manager.update_device_alias(self.selected_device['serial'], new_alias):
            self.selected_device['alias'] = new_alias
            self.refresh_devices(preserve_selection=True)  # Preservar selección al cambiar alias
            self.update_device_info(self.selected_device)
            messagebox.showinfo("Éxito", f"Alias cambiado a: {new_alias}")
        else:
            messagebox.showerror("Error", "No se pudo cambiar el alias")