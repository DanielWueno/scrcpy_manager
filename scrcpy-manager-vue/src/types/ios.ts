import type { Device } from "../types";

export interface IOSDevice extends Device {
  platform: "ios";
  udid?: string;
}

export type IOSAction =
  | "ios_screenshot"
  | "ios_mirror"
  | "ios_stop_mirror"
  | string;

export interface IOSStreamOptions {
  quality: "low" | "medium" | "high" | string;
  fps: number;
  enableAudio: boolean;
  enableControl: boolean;
  port: number;
  fullscreen: boolean;
  [key: string]: unknown;
}

export interface IOSMirrorSession {
  udid: string;
  port: number;
  startedAt: string;
  options: IOSStreamOptions;
  status: "active" | "stopped" | "error" | string;
}
