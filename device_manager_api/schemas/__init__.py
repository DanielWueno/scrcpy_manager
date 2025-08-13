"""
Esquemas de validación
"""
from .android.device_schema import Device, ActionResponse
from .screenshot_schema import ScreenshotRequest, ScreenshotResponse
from .action_schema import DeviceAction, ActionRequest, ActionResponse

__all__ = [
    "Device",
    "DeviceListResponse", 
    "ConnectDeviceRequest",
    "DeviceResponse",
    "ScreenshotRequest",
    "ScreenshotResponse",
    "DeviceAction",
    "ActionRequest", 
    "ActionResponse"
]
