from typing import Optional

class DeviceAction:
    def __init__(self, action: str, payload: Optional[dict] = None):
        self.action = action
        self.payload = payload

class ActionRequest:
    def __init__(self, serial: str, action: str, payload: Optional[dict] = None):
        self.serial = serial
        self.action = action
        self.payload = payload

class ActionResponse:
    def __init__(self, success: bool, message: Optional[str] = None, error: Optional[str] = None, data: Optional[dict] = None):
        self.success = success
        self.message = message
        self.error = error
        self.data = data