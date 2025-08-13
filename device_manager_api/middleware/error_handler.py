"""
Middleware para manejo centralizado de errores
"""
from flask import jsonify, request
from ..config import logger
import traceback

def register_error_handlers(app):
    """Registra los manejadores de error globales"""
    
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"Bad Request: {request.url} - {str(error)}")
        return jsonify({
            'success': False,
            'error': 'Solicitud inválida',
            'details': str(error)
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"Not Found: {request.url}")
        return jsonify({
            'success': False,
            'error': 'Endpoint no encontrado'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        logger.warning(f"Method Not Allowed: {request.method} {request.url}")
        return jsonify({
            'success': False,
            'error': 'Método no permitido para este endpoint'
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal Server Error: {request.url} - {str(error)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled Exception: {request.url} - {str(error)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Error inesperado del servidor'
        }), 500
