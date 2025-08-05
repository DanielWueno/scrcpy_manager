export interface Device {
  serial: string;
  alias: string;
  name: string;
  connected: boolean;
  active: boolean;
  last_seen?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  error?: string;
  message?: string;
  data?: T;
}

export interface DevicesResponse extends ApiResponse {
  devices: Device[];
  new_devices_count?: number;
}

export interface ConnectionOptions {
  stayAwake: boolean;
  showTouches: boolean;
  noAudio: boolean;
  turnScreenOff: boolean;
}

export interface ToastMessage {
  id: number;
  message: string;
  type: "success" | "error" | "warning" | "info";
  timeout?: number;
}

export type DeviceAction =
  | "screen_off"
  | "screen_on"
  | "mirror_screen_off"
  | "mirror_screen_on"
  | "home"
  | "back"
  | "recent"
  | "screenshot"
  | "record";
