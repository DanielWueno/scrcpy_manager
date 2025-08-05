"""
Router para endpoints de acciones de dispositivo
"""
from flask import Blueprint, jsonify, request
from ..services.action_service import ActionService
from ..schemas import ActionRequest, DeviceAction
from ..config import logger

# Crear blueprint
actions_bp = Blueprint('actions', __name__, url_prefix='/api/devices')

# Instancia del servicio
action_service = ActionService()

@actions_bp.route('/<serial>/actions', methods=['POST'])
async def execute_device_action(serial):
    """Ejecuta acciones en el dispositivo"""
    try:
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({
                'success': False,
                'error': 'Acción requerida'
            }), 400
        
        # Validar acción
        try:
            action = DeviceAction(data['action'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': f"Acción '{data['action']}' no válida"
            }), 400
        
        result = await action_service.execute_action(serial, action)
        
        response_data = result.dict()
        status_code = 200 if result.success else 400
        
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"Error en execute_device_action: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
