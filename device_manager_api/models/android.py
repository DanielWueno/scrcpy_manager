from typing import List, Dict

class AndroidDevice:
    def __init__(self, device_id: str, name: str, model: str, manufacturer: str):
        self.device_id = device_id
        self.name = name
        self.model = model
        self.manufacturer = manufacturer

    def to_dict(self) -> Dict[str, str]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "model": self.model,
            "manufacturer": self.manufacturer
        }

class Screenshot:
    def __init__(self, screenshot_id: str, device_id: str, timestamp: str, image_path: str):
        self.screenshot_id = screenshot_id
        self.device_id = device_id
        self.timestamp = timestamp
        self.image_path = image_path

    def to_dict(self) -> Dict[str, str]:
        return {
            "screenshot_id": self.screenshot_id,
            "device_id": self.device_id,
            "timestamp": self.timestamp,
            "image_path": self.image_path
        }

class Action:
    def __init__(self, action_id: str, device_id: str, action_type: str, timestamp: str):
        self.action_id = action_id
        self.device_id = device_id
        self.action_type = action_type
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, str]:
        return {
            "action_id": self.action_id,
            "device_id": self.device_id,
            "action_type": self.action_type,
            "timestamp": self.timestamp
        }

class AndroidModel:
    def __init__(self):
        self.devices: List[AndroidDevice] = []
        self.screenshots: List[Screenshot] = []
        self.actions: List[Action] = []

    def add_device(self, device: AndroidDevice):
        self.devices.append(device)

    def add_screenshot(self, screenshot: Screenshot):
        self.screenshots.append(screenshot)

    def add_action(self, action: Action):
        self.actions.append(action)

    def get_devices(self) -> List[Dict[str, str]]:
        return [device.to_dict() for device in self.devices]

    def get_screenshots(self) -> List[Dict[str, str]]:
        return [screenshot.to_dict() for screenshot in self.screenshots]

    def get_actions(self) -> List[Dict[str, str]]:
        return [action.to_dict() for action in self.actions]