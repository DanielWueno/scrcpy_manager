export interface Device {
  id: string; // ✅ AGREGAR campo 'id'
  serial: string; // ✅ Mantener 'serial' para compatibilidad
  name: string;
  model: string;
  platform: "android" | "ios";
  active: boolean;

  // Campos específicos de Android
  android_version?: string;
  brand?: string;

  // Campos específicos de iOS
  ios_version?: string;
  build_version?: string;
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

// ✅ Tipos para opciones de mirror
export interface MirrorOptions {
  stayAwake: boolean;
  noAudio: boolean;
  showTouches: boolean;
  turnScreenOff: boolean;
}

export interface AndroidMirrorPayload extends MirrorOptions {
  // Puede extender con más opciones en el futuro
}
