"""
Middleware de la API
"""
from .error_handler import register_error_handlers
from .cors import setup_cors
from .logging import setup_request_logging

__all__ = ["register_error_handlers", "setup_cors", "setup_request_logging"]
