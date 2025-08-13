from typing import Optional

class Device:
    def __init__(self, serial: str, platform: str, name: str, **kwargs):
        self.serial = serial
        self.platform = platform
        self.name = name
        self.alias = kwargs.get('alias')
        self.first_seen = kwargs.get('first_seen')
        self.active = kwargs.get('active', False)
        self.android_version = kwargs.get('android_version')
        self.brand = kwargs.get('brand')
        self.model = kwargs.get('model')

class ActionResponse:
    def __init__(self, success: bool, message: str = None, error: str = None, data: dict = None):
        self.success = success
        self.message = message
        self.error = error
        self.data = data