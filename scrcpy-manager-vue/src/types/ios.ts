// Shape of Mobile.Remote.Toolkit.Application.Models.Responses.iOS.IOSDeviceResponse,
// serialized camelCase by ASP.NET Core (unlike the status endpoint below, which is a
// hand-built Dictionary<string, object> with snake_case keys).
export interface IOSDeviceResponse {
  id: string;
  udid: string;
  name: string;
  model?: string;
  productType?: string;
  iosVersion?: string;
  serialNumber?: string;
  platform: "ios";
  active: boolean;
}

export interface IOSDeviceCapabilities {
  screenshot: boolean;
  mirror: boolean;
  touch: boolean;
  touch_note?: string;
}

// GET /api/ios/devices/{udid}/status
export interface IOSDeviceStatus {
  connected: boolean;
  mirror_active: boolean;
  udid: string;
  platform: "ios";
  timestamp: string;
  capabilities: IOSDeviceCapabilities;
  process_id?: number;
  mirror_mode?: string;
  mirror_executable?: string;
  mirror_url?: string;
}

// data payload of POST /api/ios/devices/{udid}/mirror/start
export interface IOSMirrorStartData {
  udid: string;
  mode: string;
  executable: string;
  arguments?: string;
  pid: number;
  port?: number;
  mirror_url?: string;
  touch_supported: boolean;
}

// data payload of GET /api/ios/devices/{udid}/screenshot
export interface IOSScreenshotData {
  filename: string;
  full_path: string;
  folder: string;
  size: number;
  content_type: string;
}
