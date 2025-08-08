export interface AndroidDevice {
  serial: string;
  platform: 'android';
  android_version: string;
  brand: string;
  model: string;
}

export type AndroidAction = 
  | "mirror_screen_on"
  | "mirror_screen_off" 
  | "screenshot"
  | "power_button"
  | "home_button"
  | "back_button"
  | "volume_up"
  | "volume_down";

export interface AndroidOptions {
  noAudio: boolean;
  stayAwake: boolean;
  showTouches: boolean;
  turnScreenOff: boolean;
  maxSize?: number;
  maxFps?: number;
}