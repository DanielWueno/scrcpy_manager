"""
Utilidades para manejo de respuestas HTTP
"""
from typing import Dict, Any, Optional, Union
from flask import jsonify, Response
import logging

logger = logging.getLogger(__name__)

class APIResponse:
    """
    Clase para manejar respuestas de API de manera consistente
    """
    
    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = 200) -> tuple[Response, int]:
        """
        Genera una respuesta exitosa
        """
        response_data = {
            "error": False,
            "message": message,
            "status_code": status_code
        }
        
        if data is not None:
            response_data["data"] = data
        
        return jsonify(response_data), status_code
    
    @staticmethod
    def error(message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None) -> tuple[Response, int]:
        """
        Genera una respuesta de error
        """
        response_data = {
            "error": True,
            "message": message,
            "status_code": status_code
        }
        
        if details:
            response_data["details"] = details
        
        logger.error(f"API Error {status_code}: {message} - Details: {details}")
        return jsonify(response_data), status_code
    
    @staticmethod
    def not_found(resource: str = "Resource") -> tuple[Response, int]:
        """
        Genera una respuesta 404
        """
        return APIResponse.error(f"{resource} not found", 404)
    
    @staticmethod
    def bad_request(message: str = "Bad request") -> tuple[Response, int]:
        """
        Genera una respuesta 400
        """
        return APIResponse.error(message, 400)
    
    @staticmethod
    def internal_error(message: str = "Internal server error") -> tuple[Response, int]:
        """
        Genera una respuesta 500
        """
        return APIResponse.error(message, 500)
    
    @staticmethod
    def validation_error(errors: Dict[str, Any]) -> tuple[Response, int]:
        """
        Genera una respuesta de error de validación
        """
        return APIResponse.error("Validation failed", 422, {"validation_errors": errors})

def paginate_response(items: list, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """
    Pagina una lista de elementos
    """
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    
    paginated_items = items[start:end]
    
    return {
        "items": paginated_items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
            "has_next": end < total,
            "has_prev": page > 1
        }
    }

def format_device_response(device_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formatea la respuesta de un dispositivo
    """
    return {
        "id": device_data.get("id"),
        "model": device_data.get("model", "Unknown"),
        "status": device_data.get("status", "unknown"),
        "connection_type": device_data.get("connection_type", "unknown"),
        "scrcpy_active": device_data.get("scrcpy_active", False),
        "last_seen": device_data.get("last_seen"),
        "battery_level": device_data.get("battery_level"),
        "screen_resolution": device_data.get("screen_resolution")
    }

def format_screenshot_response(screenshot_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formatea la respuesta de un screenshot
    """
    return {
        "filename": screenshot_data.get("filename"),
        "device_id": screenshot_data.get("device_id"),
        "timestamp": screenshot_data.get("timestamp"),
        "file_size": screenshot_data.get("file_size"),
        "download_url": screenshot_data.get("download_url")
    }
