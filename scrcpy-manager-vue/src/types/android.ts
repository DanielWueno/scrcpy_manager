import type { Device } from "./common";

export interface AndroidDevice extends Device {
  platform: "android";
}

export type AndroidAction = string;

export interface AndroidOptions {
  stayAwake?: boolean;
  noAudio?: boolean;
  showTouches?: boolean;
  turnScreenOff?: boolean;
  [key: string]: unknown;
}
