export type ExtensionDeviceStatus =
  | "adb_ready"
  | "connected"
  | "unauthorized"
  | "no_adb"
  | string;

export interface ExtensionDevice {
  serialNumber: string;
  productName?: string;
  status: ExtensionDeviceStatus;
  [key: string]: unknown;
}

export interface ExtensionStatus {
  available: boolean;
  initialized: boolean;
  hasUsbPermission: boolean;
  devices: ExtensionDevice[];
  error?: string | null;
  [key: string]: unknown;
}
