"""
Punto de entrada principal de la API modular
"""
from flask import Flask
from flask_cors import CORS
import logging
import sys
import os

# Agregar el directorio raíz al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.config import settings, setup_logging
from api.middleware import register_error_handlers, setup_cors, setup_request_logging
from api.routers import device_router, screenshot_router, action_router
from api.utils import ensure_directory_exists

def create_app() -> Flask:
    """
    Factory function para crear la aplicación Flask
    """
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Crear aplicación Flask
    app = Flask(__name__)
    
    # Configuración de la app
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['DEBUG'] = settings.DEBUG
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Asegurar que existan los directorios necesarios
    ensure_directory_exists(settings.SCREENSHOT_DIR)
    
    # Configurar middleware
    setup_cors(app)
    setup_request_logging(app)
    register_error_handlers(app)
    
    # Registrar blueprints/routers
    app.register_blueprint(device_router, url_prefix='/api/devices')
    app.register_blueprint(screenshot_router, url_prefix='/api/screenshots')
    app.register_blueprint(action_router, url_prefix='/api/actions')
    
    # Ruta de health check
    @app.route('/api/health')
    def health_check():
        return {
            "status": "healthy",
            "message": "SCRCPY Manager API is running",
            "version": "1.0.0"
        }
    
    # Ruta raíz
    @app.route('/')
    def index():
        return {
            "message": "SCRCPY Manager API",
            "version": "1.0.0",
            "endpoints": {
                "health": "/api/health",
                "devices": "/api/devices",
                "screenshots": "/api/screenshots", 
                "actions": "/api/actions"
            }
        }
    
    logger.info("Flask application created successfully")
    logger.info(f"Screenshot directory: {settings.SCREENSHOT_DIR}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    return app

def main():
    """
    Función principal para ejecutar la aplicación
    """
    app = create_app()
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting SCRCPY Manager API on {settings.API_HOST}:{settings.API_PORT}")
    
    try:
        app.run(
            host=settings.API_HOST,
            port=settings.API_PORT,
            debug=settings.DEBUG,
            use_reloader=settings.DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application crashed: {e}")
        raise

if __name__ == '__main__':
    main()
