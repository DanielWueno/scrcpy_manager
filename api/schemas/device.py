"""
Esquemas de validación usando Pydantic
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class DeviceStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ACTIVE = "active"

class Device(BaseModel):
    """Esquema para dispositivo"""
    serial: str = Field(..., description="Serial del dispositivo")
    alias: str = Field(..., description="Alias del dispositivo")
    name: str = Field(..., description="Nombre del dispositivo")
    connected: bool = Field(default=False, description="Estado de conexión")
    active: bool = Field(default=False, description="Estado de mirror activo")
    last_seen: Optional[str] = Field(None, description="Última vez visto")

class DeviceListResponse(BaseModel):
    """Respuesta para lista de dispositivos"""
    success: bool = Field(default=True)
    devices: List[Device]
    new_devices_count: Optional[int] = Field(None)

class ConnectDeviceRequest(BaseModel):
    """Request para conectar dispositivo"""
    options: List[str] = Field(default_factory=list, description="Opciones de scrcpy")

class DeviceResponse(BaseModel):
    """Respuesta genérica para operaciones de dispositivo"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
