#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Server para Scrcpy Manager
"""

import sys
import os
# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import threading
import time
import os
from core.device_manager import DeviceManager
from core.scrcpy_controller import ScrcpyController
from core.ios.ios_manager import IOSManager

app = Flask(__name__)
CORS(app)  # Permitir requests desde Vue

device_manager = DeviceManager()
scrcpy_controller = ScrcpyController()
ios_manager = IOSManager()

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Obtiene lista de todos los dispositivos conectados"""
    try:
        all_devices = []
        
        # Dispositivos Android con estado individual
        android_devices = device_manager.android_manager.get_connected_devices()
        for serial in android_devices:
            device_info = device_manager.android_manager.get_device_info(serial)
            
            # Verificar estado ESPECÍFICO para este dispositivo
            is_active = device_manager.android_manager.is_mirror_active(serial)
            
            device = {
                'id': serial,
                'serial': serial,
                'name': device_info.get('name', f'Android {serial[-4:]}'),
                'model': device_info.get('model', 'Desconocido'),
                'platform': 'android',
                'android_version': device_info.get('android_version', 'Desconocido'),
                'brand': device_info.get('brand', 'Desconocido'),
                'active': is_active
            }
            all_devices.append(device)
            
            # Log detallado del estado INDIVIDUAL
            print(f"Android {serial[-4:]}: {device['name']} - Activo: {is_active}")
        
        # Log de active_streams para debugging
        active_streams = device_manager.android_manager.active_streams
        print(f"Active streams actuales: {list(active_streams.keys())}")
        for serial, stream in active_streams.items():
            pid = stream.get('pid', 'N/A')
            print(f"  - {serial[-4:]}: PID {pid}")
        
        # Dispositivos iOS (código similar)
        ios_devices = device_manager.ios_manager.get_connected_devices()
        for udid in ios_devices:
            device_info = device_manager.ios_manager.get_device_info(udid)
            is_active = device_manager.ios_manager.is_mirror_active(udid)
            
            device = {
                'id': udid,
                'serial': udid,
                'name': device_info.get('name', f'iPhone {udid[-4:]}'),
                'model': device_info.get('model', 'iPhone'),
                'platform': 'ios',
                'ios_version': device_info.get('ios_version', 'Desconocido'),
                'build_version': device_info.get('build_version', 'Desconocido'),
                'active': is_active
            }
            all_devices.append(device)
            
            print(f"iOS {udid[-4:]}: {device['name']} - Activo: {is_active}")
        
        print(f"Total dispositivos: {len(all_devices)}")
        return jsonify(all_devices)
        
    except Exception as e:
        print(f"Error obteniendo dispositivos: {e}")
        return jsonify([]), 500

@app.route('/api/devices/<device_id>/action', methods=['POST'])
def execute_device_action(device_id):
    """Ejecuta una acción en un dispositivo (Android o iOS)"""
    try:
        data = request.get_json()
        action = data.get('action')
        payload = data.get('payload')
        
        print(f"\n=========================")
        print(f"EJECUTANDO ACCION")
        print(f"Device ID: '{device_id}'")
        print(f"Action: '{action}'")
        print(f"Payload: {payload}")
        print(f"=========================")
        
        if not device_id or device_id == 'undefined':
            print(f"device_id invalido: '{device_id}'")
            return jsonify({
                'success': False,
                'error': f'ID de dispositivo invalido: {device_id}'
            }), 400
        
        # Verificar si es dispositivo Android
        android_devices = device_manager.android_manager.get_connected_devices()
        print(f"Dispositivos Android disponibles: {android_devices}")
        
        if device_id in android_devices:
            print(f"Dispositivo Android encontrado: {device_id}")
            print(f"Llamando a AndroidManager.execute_action...")
            
            success = device_manager.android_manager.execute_action(device_id, action, payload)
            
            print(f"Resultado final de la accion: {success}")
            print(f"=========================\n")
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Accion {action} ejecutada correctamente en Android'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'Error ejecutando accion {action} en Android'
                }), 400
        
        # Verificar si es dispositivo iOS
        ios_devices = device_manager.ios_manager.get_connected_devices()
        print(f"Dispositivos iOS disponibles: {ios_devices}")
        
        if device_id in ios_devices:
            print(f"Dispositivo iOS encontrado: {device_id}")
            success = device_manager.ios_manager.execute_action(device_id, action, payload)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Accion {action} ejecutada correctamente en iOS'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'Error ejecutando accion {action} en iOS'
                }), 400
        
        print(f"Dispositivo '{device_id}' no encontrado")
        return jsonify({
            'success': False,
            'error': f'Dispositivo {device_id} no encontrado'
        }), 404
        
    except Exception as e:
        print(f"Error ejecutando accion: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices/<device_id>/status', methods=['GET'])
def get_device_status(device_id):
    """Obtiene estado actual de un dispositivo específico"""
    try:
        android_devices = device_manager.android_manager.get_connected_devices()
        ios_devices = device_manager.ios_manager.get_connected_devices()
        
        if device_id in android_devices:
            device_info = device_manager.android_manager.get_device_info(device_id)
            active = device_manager.android_manager.is_mirror_active(device_id)
            
            return jsonify({
                'success': True,
                'device': {
                    'id': device_id,
                    'serial': device_id,
                    'platform': 'android',
                    'active': active,
                    **device_info
                }
            })
            
        elif device_id in ios_devices:
            device_info = device_manager.ios_manager.get_device_info(device_id)
            active = device_manager.ios_manager.is_mirror_active(device_id)
            
            return jsonify({
                'success': True,
                'device': {
                    'id': device_id,
                    'serial': device_id,
                    'platform': 'ios',
                    'active': active,
                    **device_info
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Dispositivo no encontrado'
            }), 404
            
    except Exception as e:
        print(f"❌ Error obteniendo estado: {e}")
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

@app.route('/api/devices/<serial>/alias', methods=['PUT'])
def update_device_alias(serial):
    """Actualiza el alias de un dispositivo"""
    try:
        data = request.get_json()
        
        if not data or 'alias' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere el campo "alias"'
            }), 400
        
        alias = data['alias'].strip()
        if not alias:
            return jsonify({
                'success': False,
                'error': 'El alias no puede estar vacío'
            }), 400
        
        success = device_manager.update_device_alias(serial, alias)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Alias actualizado a "{alias}"'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Dispositivo no encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# === ENDPOINTS ESPECÍFICOS PARA iOS ===

@app.route('/api/ios/devices', methods=['GET'])
def get_ios_devices():
    """Obtiene todos los dispositivos iOS conectados"""
    try:
        devices = ios_manager.get_connected_devices()
        ios_devices = []
        
        for udid in devices:
            info = ios_manager.get_device_info(udid)
            device_data = {
                'serial': udid,
                'platform': 'ios',
                'connected': True,
                'active': ios_manager.is_mirror_active(udid),
                **info
            }
            ios_devices.append(device_data)
        
        return jsonify({
            'success': True,
            'devices': ios_devices
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ios/devices/<udid>/mirror/start', methods=['POST'])
def start_ios_mirror(udid):
    """Inicia el mirror de un dispositivo iOS"""
    try:
        data = request.get_json() or {}
        options = data.get('options', {})
        
        success = ios_manager.start_mirror(udid, options)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Mirror iOS iniciado para {udid[:8]}...'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo iniciar el mirror iOS'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ios/devices/<udid>/mirror/stop', methods=['POST'])
def stop_ios_mirror(udid):
    """Detiene el mirror de un dispositivo iOS"""
    try:
        success = ios_manager.stop_mirror(udid)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Mirror iOS detenido para {udid[:8]}...'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo detener el mirror iOS'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ios/devices/<udid>/action', methods=['POST'])
def execute_ios_action(udid):
    """Ejecuta una acción en un dispositivo iOS"""
    try:
        data = request.get_json()
        action = data.get('action')
        payload = data.get('payload')
        
        if not action:
            return jsonify({
                'success': False,
                'error': 'Acción requerida'
            }), 400
        
        result = ios_manager.execute_action(udid, action, payload)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ios/mirror/sessions', methods=['GET'])
def get_ios_mirror_sessions():
    """Obtiene las sesiones de mirror activas de iOS"""
    try:
        sessions = []
        for udid, stream_data in ios_manager.active_streams.items():
            sessions.append({
                'udid': udid,
                'port': stream_data.get('port', 8000),
                'started_at': stream_data.get('started_at'),
                'stream_url': stream_data.get('stream_url', f"http://localhost:{stream_data.get('port', 8000)}"),
                'options': stream_data.get('options', {})
            })
        
        return jsonify({
            'success': True,
            'sessions': sessions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Iniciando servidor...")
    print("Verificando dispositivos conectados...")
    
    try:
        devices = device_manager.get_all_devices()
        print(f"{len(devices)} dispositivos encontrados")
    except Exception as e:
        print(f"Error inicial verificando dispositivos: {e}")
    
    print("Servidor disponible en: http://localhost:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)