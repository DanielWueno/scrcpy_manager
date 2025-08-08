export interface IOSDevice {
  serial: string; // UDID
  platform: 'ios';
  name: string;
  model: string;
  ios_version: string;
  connected: boolean;
  active: boolean;
  alias?: string;
  last_seen?: string;
}

export type IOSAction = 
  | "ios_mirror"
  | "ios_stop_mirror"
  | "ios_screenshot"
  | "ios_home_button"
  | "ios_lock_device"
  | "ios_volume_up"
  | "ios_volume_down"
  | "ios_restart_device"
  | "ios_device_info";

export interface IOSStreamOptions {
  quality: 'low' | 'medium' | 'high';
  fps: 15 | 30 | 60;
  enableAudio: boolean;
  enableControl: boolean;
  port?: number;
  fullscreen?: boolean;
}

export interface IOSMirrorSession {
  udid: string;
  port: number;
  startedAt: string;
  options: IOSStreamOptions;
  status: 'starting' | 'active' | 'stopping' | 'error';
}

export interface IOSDeviceInfo {
  deviceName: string;
  productType: string;
  productVersion: string;
  buildVersion: string;
  serialNumber: string;
  wifiAddress?: string;
  bluetoothAddress?: string;
}
