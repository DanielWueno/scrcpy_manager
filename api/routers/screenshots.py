"""
Router para endpoints de capturas de pantalla
"""
from flask import Blueprint, jsonify, request, send_file
from ..services.screenshot_service import ScreenshotService
from ..schemas import ScreenshotRequest
from ..config import logger

# Crear blueprint
screenshots_bp = Blueprint('screenshots', __name__, url_prefix='/api/devices')

# Instancia del servicio
screenshot_service = ScreenshotService()

@screenshots_bp.route('/<serial>/screenshot', methods=['POST'])
async def take_screenshot_download(serial):
    """Toma captura de pantalla y la descarga directamente"""
    try:
        data = request.get_json() or {}
        screenshot_request = ScreenshotRequest(**data)
        
        result = await screenshot_service.take_screenshot_for_download(
            serial, 
            screenshot_request.filename
        )
        
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
        logger.error(f"Error en take_screenshot_download: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
