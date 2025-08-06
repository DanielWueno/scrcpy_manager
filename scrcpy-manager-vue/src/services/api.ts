import axios from "axios";
import type {
  Device,
  DevicesResponse,
  ApiResponse,
  DeviceAction,
} from "../types";

const API_BASE_URL = "http://127.0.0.1:5000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor para request
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error("API Request Error:", error);
    return Promise.reject(error);
  }
);

// Interceptor para response
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error("API Error:", error);
    return Promise.reject(error);
  }
);

export const deviceApi = {
  // Obtener dispositivos
  async getDevices(): Promise<DevicesResponse> {
    const response = await api.get<DevicesResponse>("/devices");
    return response.data;
  },

  // Actualizar lista de dispositivos
  async refreshDevices(): Promise<DevicesResponse> {
    const response = await api.post<DevicesResponse>("/devices/refresh");
    return response.data;
  },

  // Conectar dispositivo
  async connectDevice(
    serial: string,
    options: { options: string[] }
  ): Promise<ApiResponse> {
    const response = await api.post<ApiResponse>(
      `/devices/${serial}/connect`,
      options
    );
    return response.data;
  },

  // Desconectar dispositivo
  async disconnectDevice(serial: string): Promise<ApiResponse> {
    const response = await api.post<ApiResponse>(
      `/devices/${serial}/disconnect`
    );
    return response.data;
  },

  // Tomar captura de pantalla y descargar
  async takeScreenshotDownload(
    serial: string,
    filename: string
  ): Promise<Blob> {
    const response = await api.post(
      `/devices/${serial}/screenshot`,
      { filename },
      {
        responseType: "blob",
      }
    );
    return response.data;
  },

  // Ejecutar acción en dispositivo
  async deviceAction(
    serial: string,
    action: DeviceAction
  ): Promise<ApiResponse> {
    const response = await api.post<ApiResponse>(`/devices/${serial}/actions`, {
      action,
    });
    return response.data;
  },

  // Obtener estado del dispositivo
  async getDeviceStatus(
    serial: string
  ): Promise<
    ApiResponse & { device: Device; connected: boolean; active: boolean }
  > {
    const response = await api.get<
      ApiResponse & { device: Device; connected: boolean; active: boolean }
    >(`/devices/${serial}/status`);
    return response.data;
  },

  // Actualizar alias del dispositivo
  async updateDeviceAlias(serial: string, alias: string): Promise<ApiResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/devices/${serial}/alias`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ alias: alias.trim() }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Error updating device alias:", error);
      return {
        success: false,
        error: "Error de conexión al actualizar alias",
      };
    }
  },
};
