#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tooltip profesional para botones
"""

import tkinter as tk

class ToolTip:
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.after_id = None
        
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)
    
    def on_enter(self, event=None):
        self.after_id = self.widget.after(self.delay, self.show_tooltip)
    
    def on_leave(self, event=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        self.hide_tooltip()
    
    def on_motion(self, event=None):
        if self.tooltip_window:
            self.update_position(event)
    
    def show_tooltip(self, event=None):
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Estilo del tooltip
        frame = tk.Frame(self.tooltip_window, background="#ffffe0", 
                        relief="solid", borderwidth=1)
        frame.pack()
        
        label = tk.Label(frame, text=self.text, background="#ffffe0",
                        font=("Arial", 9), justify="left", padx=5, pady=3)
        label.pack()
    
    def hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def update_position(self, event):
        if self.tooltip_window:
            x = self.widget.winfo_rootx() + 25
            y = self.widget.winfo_rooty() + 25
            self.tooltip_window.wm_geometry(f"+{x}+{y}")