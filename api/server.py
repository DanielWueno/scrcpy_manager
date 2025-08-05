#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Server para Scrcpy Manager
"""

import sys
import os
# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import threading
import time
import os
from core.device_manager import DeviceManager
from core.scrcpy_controller import ScrcpyController

app = Flask(__name__)
CORS(app)  # Permitir requests desde Vue

device_manager = DeviceManager()
scrcpy_controller = ScrcpyController()

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Obtiene lista de dispositivos con estado"""
    try:
        devices = device_manager.get_devices_status()
        
        # Agregar estado de scrcpy a cada dispositivo
        for device in devices:
            device['active'] = scrcpy_controller.is_active(device['serial'])
        
        return jsonify({
            'success': True,
            'devices': devices
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices/refresh', methods=['POST'])
def refresh_devices():
    """Actualiza lista de dispositivos"""
    try:
        new_devices = device_manager.update_devices_list()
        devices = device_manager.get_devices_status()
        
        # Agregar estado de scrcpy a cada dispositivo
        for device in devices:
            device['active'] = scrcpy_controller.is_active(device['serial'])
        
        return jsonify({
            'success': True,
            'devices': devices,
            'new_devices_count': new_devices
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices/<serial>/connect', methods=['POST'])
def connect_device(serial):
    """Conecta dispositivo con scrcpy"""
    try:
        data = request.get_json() or {}
        options = data.get('options', [])
        
        device = device_manager.get_device_by_serial(serial)
        if not device:
            return jsonify({
                'success': False,
                'error': 'Dispositivo no encontrado'
            }), 404
        
        # Verificar si el dispositivo está físicamente conectado
        connected_devices = device_manager.get_connected_devices()
        if serial not in connected_devices:
            return jsonify({
                'success': False,
                'error': f'Dispositivo {device.get("alias", serial)} no está conectado físicamente. Conecta el dispositivo USB y prueba de nuevo.'
            }), 400
        
        # Verificar si ya está activo
        if scrcpy_controller.is_active(serial):
            return jsonify({
                'success': False,
                'error': f'El dispositivo {device.get("alias", serial)} ya tiene una sesión de mirror activa'
            }), 400
        
        result = scrcpy_controller.start_scrcpy(device, options)
        print(f"Resultado start_scrcpy: {result}")
        
        if result:
            # Verificar estado inmediatamente después
            is_active_now = scrcpy_controller.is_active(serial)
            print(f"Dispositivo {serial} activo después de iniciar: {is_active_now}")
            
            return jsonify({
                'success': True,
                'message': f'Mirror iniciado para {device.get("alias", serial)}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Error al iniciar mirror para {device.get("alias", serial)}. Verifica que el dispositivo esté desbloqueado y con USB debugging habilitado.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }), 500

@app.route('/api/devices/<serial>/disconnect', methods=['POST'])
def disconnect_device(serial):
    """Desconecta dispositivo"""
    try:
        result = scrcpy_controller.stop_scrcpy(serial)
        return jsonify({
            'success': result,
            'message': 'Desconectado' if result else 'Error al desconectar'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices/<serial>/screenshot', methods=['POST'])
def take_screenshot_download(serial):
    """Toma captura de pantalla y la descarga directamente"""
    try:
        data = request.get_json() or {}
        filename = data.get('filename', None)
        
        result = scrcpy_controller.take_screenshot(serial, filename)
        
        if result['success']:
            # Enviar el archivo directamente como descarga
            return send_file(
                result['full_path'],
                as_attachment=True,
                download_name=result['filename'],
                mimetype='image/png'
            )
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error desconocido al tomar captura')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices/<serial>/actions', methods=['POST'])
def device_action(serial):
    """Ejecuta acciones en el dispositivo"""
    try:
        data = request.get_json()
        action = data.get('action')
        
        result = False
        message = ''
        
        print(f"Ejecutando acción: {action} en dispositivo: {serial}")
        
        if action == 'screen_off':
            result = scrcpy_controller.screen_off(serial)
            message = 'Pantalla apagada' if result else 'Error al apagar pantalla'
        elif action == 'screen_on':
            result = scrcpy_controller.screen_on(serial)
            message = 'Pantalla encendida' if result else 'Error al encender pantalla'
        elif action == 'mirror_screen_off':
            print(f"Ejecutando mirror_screen_off para {serial}")
            result = scrcpy_controller.mirror_screen_off(serial)
            message = 'Pantalla dispositivo apagada (mirror activo)' if result else 'Error al apagar pantalla del dispositivo'
            print(f"Resultado mirror_screen_off: {result}")
        elif action == 'mirror_screen_on':
            print(f"Ejecutando mirror_screen_on para {serial}")
            result = scrcpy_controller.mirror_screen_on(serial)
            message = 'Pantalla dispositivo encendida' if result else 'Error al encender pantalla del dispositivo'
            print(f"Resultado mirror_screen_on: {result}")
        elif action in ['home', 'back', 'recent']:
            keycode_map = {
                'home': 'KEYCODE_HOME',
                'back': 'KEYCODE_BACK',
                'recent': 'KEYCODE_APP_SWITCH'
            }
            print(f"Enviando tecla {action} ({keycode_map[action]}) a dispositivo {serial}")
            result = scrcpy_controller.send_keycode(serial, keycode_map[action])
            message = f'Tecla {action} enviada' if result else f'Error al enviar tecla {action}'
        
        print(f"Acción completada. Resultado: {result}, Mensaje: {message}")
        
        return jsonify({
            'success': result,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices/<serial>/status', methods=['GET'])
def get_device_status(serial):
    """Obtiene estado del dispositivo"""
    try:
        device = device_manager.get_device_by_serial(serial)
        if not device:
            return jsonify({
                'success': False,
                'error': 'Dispositivo no encontrado'
            }), 404
        
        connected = device['serial'] in device_manager.get_connected_devices()
        active = scrcpy_controller.is_active(serial)
        
        print(f"Estado del dispositivo {serial}: conectado={connected}, activo={active}")
        
        return jsonify({
            'success': True,
            'device': device,
            'connected': connected,
            'active': active
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)