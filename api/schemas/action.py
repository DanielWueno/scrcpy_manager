"""
Esquemas para acciones de dispositivo
"""
from pydantic import BaseModel, Field
from enum import Enum

class DeviceAction(str, Enum):
    SCREEN_OFF = "screen_off"
    SCREEN_ON = "screen_on"
    MIRROR_SCREEN_OFF = "mirror_screen_off"
    MIRROR_SCREEN_ON = "mirror_screen_on"
    HOME = "home"
    BACK = "back"
    RECENT = "recent"
    SCREENSHOT = "screenshot"
    RECORD = "record"

class ActionRequest(BaseModel):
    """Request para ejecutar acción"""
    action: DeviceAction = Field(..., description="Acción a ejecutar")

class ActionResponse(BaseModel):
    """Respuesta para acción ejecutada"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
