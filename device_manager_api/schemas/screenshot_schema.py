from pydantic import BaseModel
from typing import Optional

class ScreenshotRequest(BaseModel):
    filename: Optional[str] = None

class ScreenshotResponse(BaseModel):
    success: bool
    filename: Optional[str] = None
    full_path: Optional[str] = None
    folder: Optional[str] = None
    error: Optional[str] = None