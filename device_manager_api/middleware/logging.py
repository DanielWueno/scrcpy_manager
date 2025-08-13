"""
Middleware para logging de requests
"""
from flask import request, g
import time
from ..config import logger

def setup_request_logging(app):
    """Configura logging de requests"""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
        logger.info(f"REQUEST: {request.method} {request.url}")
        if request.is_json and request.get_json():
            logger.debug(f"REQUEST DATA: {request.get_json()}")
    
    @app.after_request
    def after_request(response):
        duration = time.time() - g.start_time
        logger.info(f"RESPONSE: {response.status_code} - {duration:.3f}s")
        return response
    
    return app
