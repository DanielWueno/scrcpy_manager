export interface Device {
  id?: string;
  serial: string;
  name?: string;
  alias?: string;
  brand?: string;
  model?: string;
  androidVersion?: string;
  platform?: "android" | "ios" | string;
  connected?: boolean;
  active?: boolean;
  last_seen?: string;
  [key: string]: unknown;
}

export interface DevicesResponse {
  success: boolean;
  devices: Device[];
  message?: string;
  error?: string;
}

export interface ApiResponse {
  success: boolean;
  message?: string;
  error?: string;
  data?: unknown;
  [key: string]: unknown;
}

export type DeviceAction =
  | string
  | {
      type: string;
      [key: string]: unknown;
    };

export interface ConnectionOptions {
  stayAwake?: boolean;
  noAudio?: boolean;
  showTouches?: boolean;
  turnScreenOff?: boolean;
  [key: string]: unknown;
}
