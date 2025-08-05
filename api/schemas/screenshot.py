"""
Esquemas para capturas de pantalla
"""
from pydantic import BaseModel, Field
from typing import Optional

class ScreenshotRequest(BaseModel):
    """Request para captura de pantalla"""
    filename: Optional[str] = Field(None, description="Nombre del archivo (opcional)")

class ScreenshotResponse(BaseModel):
    """Respuesta para captura de pantalla"""
    success: bool
    filename: Optional[str] = None
    full_path: Optional[str] = None
    folder: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
