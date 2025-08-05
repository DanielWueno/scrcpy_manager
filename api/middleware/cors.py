"""
Middleware para configuración CORS
"""
from flask_cors import CORS
from ..config import settings

def setup_cors(app):
    """Configura CORS para la aplicación"""
    
    CORS(app, 
         origins=settings.CORS_ORIGINS,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    return app
