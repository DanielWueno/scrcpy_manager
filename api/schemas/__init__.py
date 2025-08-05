"""
Esquemas de validación
"""
from .device import Device, DeviceListResponse, ConnectDeviceRequest, DeviceResponse
from .screenshot import ScreenshotRequest, ScreenshotResponse
from .action import DeviceAction, ActionRequest, ActionResponse

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
