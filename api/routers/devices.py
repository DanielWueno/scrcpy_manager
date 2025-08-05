"""
Router para endpoints de dispositivos
"""
from flask import Blueprint, jsonify, request
from ..services.device_service import DeviceService
from ..schemas import ConnectDeviceRequest
from ..config import logger

# Crear blueprint
devices_bp = Blueprint('devices', __name__, url_prefix='/api/devices')

# Instancia del servicio
device_service = DeviceService()

@devices_bp.route('', methods=['GET'])
async def get_devices():
    """Obtiene lista de dispositivos con estado"""
    try:
        result = await device_service.get_devices()
        return jsonify(result.dict())
    except Exception as e:
        logger.error(f"Error en get_devices: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@devices_bp.route('/refresh', methods=['POST'])
async def refresh_devices():
    """Actualiza lista de dispositivos"""
    try:
        result = await device_service.refresh_devices()
        return jsonify(result.dict())
    except Exception as e:
        logger.error(f"Error en refresh_devices: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@devices_bp.route('/<serial>/connect', methods=['POST'])
async def connect_device(serial):
    """Conecta dispositivo con scrcpy"""
    try:
        data = request.get_json() or {}
        connect_request = ConnectDeviceRequest(**data)
        
        result = await device_service.connect_device(serial, connect_request.options)
        
        if result.success:
            return jsonify(result.dict())
        else:
            return jsonify(result.dict()), 400
            
    except Exception as e:
        logger.error(f"Error en connect_device: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@devices_bp.route('/<serial>/disconnect', methods=['POST'])
async def disconnect_device(serial):
    """Desconecta dispositivo"""
    try:
        result = await device_service.disconnect_device(serial)
        return jsonify(result.dict())
    except Exception as e:
        logger.error(f"Error en disconnect_device: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@devices_bp.route('/<serial>/status', methods=['GET'])
async def get_device_status(serial):
    """Obtiene estado del dispositivo"""
    try:
        result = await device_service.get_device_status(serial)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error en get_device_status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
