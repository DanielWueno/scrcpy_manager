import type { ApiResponse } from "../types/common";
import type {
  IOSDeviceResponse,
  IOSDeviceStatus,
  IOSDriverStatusResponse,
} from "../types/ios";
import { createApiClient } from "./httpClient";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:59399/api";

const api = createApiClient(API_BASE_URL);

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

  async getDriverStatus(): Promise<IOSDriverStatusResponse> {
    const response = await api.get<IOSDriverStatusResponse>(
      "/ios/drivers/status",
    );
    return response.data;
  },

  // Instala el driver "Apple Mobile Device Service" via winget con un UAC puntual;
  // la promesa no resuelve hasta que la instalación termina, así que se necesita
  // más margen que el timeout por defecto del cliente HTTP (10s).
  async installDriver(): Promise<ApiResponse> {
    const response = await api.post<ApiResponse>(
      "/ios/drivers/install",
      undefined,
      { timeout: 120000 },
    );
    return response.data;
  },
};
