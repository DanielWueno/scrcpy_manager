"""
Routers de la API
"""
from .devices import devices_bp
from .screenshots import screenshots_bp
from .actions import actions_bp

__all__ = ["devices_bp", "screenshots_bp", "actions_bp"]
