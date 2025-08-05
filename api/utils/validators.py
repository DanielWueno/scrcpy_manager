"""
Validadores utilitarios
"""
import re
from typing import Optional
from flask import jsonify, request
import ipaddress
import logging

logger = logging.getLogger(__name__)

def validate_device_id(device_id: str) -> bool:
    """
    Valida que el device_id tenga un formato válido
    """
    if not device_id or not isinstance(device_id, str):
        return False
    
    # Formato de dispositivo USB (números y letras)
    usb_pattern = r'^[A-Za-z0-9]{8,}$'
    
    # Formato de IP:puerto
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}:\d{1,5}$'
    
    # Formato emulador
    emulator_pattern = r'^emulator-\d{4}$'
    
    return (re.match(usb_pattern, device_id) or 
            re.match(ip_pattern, device_id) or 
            re.match(emulator_pattern, device_id))

def validate_ip_address(ip: str) -> bool:
    """
    Valida que la IP sea válida
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_port(port: int) -> bool:
    """
    Valida que el puerto esté en rango válido
    """
    return isinstance(port, int) and 1 <= port <= 65535

def validate_json_request() -> Optional[dict]:
    """
    Valida que la request tenga JSON válido
    """
    if not request.is_json:
        return None
    
    try:
        return request.get_json()
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        return None

def format_error_response(message: str, status_code: int = 400, details: Optional[dict] = None) -> tuple:
    """
    Formatea respuestas de error de manera consistente
    """
    response = {
        "error": True,
        "message": message,
        "status_code": status_code
    }
    
    if details:
        response["details"] = details
    
    return jsonify(response), status_code

def format_success_response(data: dict, message: str = "Success") -> dict:
    """
    Formatea respuestas exitosas de manera consistente
    """
    return {
        "error": False,
        "message": message,
        "data": data
    }
