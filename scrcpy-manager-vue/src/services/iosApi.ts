import axios from "axios";
import type {
  IOSAction,
  IOSDevice,
  IOSMirrorSession,
  IOSStreamOptions,
} from "../types/ios";
import type { ApiResponse } from "../types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:59399/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

export const iosApi = {
  async getDevices(): Promise<IOSDevice[]> {
    const response = await api.get<IOSDevice[]>("/ios/devices");
    return response.data;
  },

  async getMirrorSessions(): Promise<IOSMirrorSession[]> {
    const response = await api.get<IOSMirrorSession[]>("/ios/mirror/sessions");
    return response.data;
  },

  async startMirror(
    udid: string,
    options: IOSStreamOptions,
  ): Promise<ApiResponse> {
    const response = await api.post<ApiResponse>(
      `/ios/devices/${udid}/mirror/start`,
      { options },
    );
    return response.data;
  },

  async stopMirror(udid: string): Promise<ApiResponse> {
    const response = await api.post<ApiResponse>(
      `/ios/devices/${udid}/mirror/stop`,
    );
    return response.data;
  },

  async takeScreenshot(udid: string): Promise<Blob> {
    const response = await api.post(
      `/ios/devices/${udid}/screenshot`,
      {},
      { responseType: "blob" },
    );
    return response.data;
  },

  async executeAction(
    udid: string,
    action: IOSAction,
    payload?: unknown,
  ): Promise<ApiResponse> {
    const response = await api.post<ApiResponse>(
      `/ios/devices/${udid}/action`,
      { action, payload: payload ?? {} },
    );
    return response.data;
  },
};
