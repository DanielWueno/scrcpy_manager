export interface Device {
  id?: string;
  serial: string;
  name?: string;
  alias?: string;
  brand?: string;
  model?: string;
  androidVersion?: string;
  iosVersion?: string;
  platform?: "android" | "ios" | string;
  connected?: boolean;
  active?: boolean;
  last_seen?: string;
  // Mirror MJPEG de go-ios (solo iOS) - no hay ventana nativa que dockear, se embebe
  // directo en la UI con un <img>.
  mirrorUrl?: string;
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
