import axios from "axios";
import type { ApiResponse } from "../types/common";
import type { IOSDeviceResponse, IOSDeviceStatus } from "../types/ios";

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
  async getDevices(): Promise<IOSDeviceResponse[]> {
    const response = await api.get<IOSDeviceResponse[]>("/ios/devices");
    return response.data;
  },

  async getDeviceStatus(udid: string): Promise<IOSDeviceStatus> {
    const response = await api.get<IOSDeviceStatus>(
      `/ios/devices/${udid}/status`,
    );
    return response.data;
  },

  async startMirror(udid: string): Promise<ApiResponse> {
    const response = await api.post<ApiResponse>(
      `/ios/devices/${udid}/mirror/start`,
    );
    return response.data;
  },

  async stopMirror(udid: string): Promise<ApiResponse> {
    const response = await api.post<ApiResponse>(
      `/ios/devices/${udid}/mirror/stop`,
    );
    return response.data;
  },

  // El backend guarda la captura en disco y devuelve su ruta (mismo patrón que
  // el screenshot de Android) — no una imagen binaria.
  async takeScreenshot(udid: string, filename?: string): Promise<ApiResponse> {
    const response = await api.get<ApiResponse>(
      `/ios/devices/${udid}/screenshot`,
      { params: filename ? { filename } : undefined },
    );
    return response.data;
  },
};
