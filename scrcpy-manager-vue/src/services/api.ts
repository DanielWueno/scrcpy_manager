import axios from "axios";
import type {
  Device,
  DevicesResponse,
  ApiResponse,
  DeviceAction,
} from "../types";

const API_BASE_URL = "https://localhost:5000/api"; // ✅ Puerto correcto

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
  // Obtener dispositivos Android
  async getDevices(): Promise<DevicesResponse> {
    const response = await api.get<Device[]>("/android/devices");
    return {
      success: true,
      devices: response.data,
      message: "Dispositivos obtenidos correctamente",
    };
  },

  // Actualizar lista de dispositivos (no existe endpoint, usar getDevices)
  async refreshDevices(): Promise<DevicesResponse> {
    return await this.getDevices();
  },

  // Iniciar mirror (mapear a tu endpoint)
  async connectDevice(
    serial: string,
    options: { options: Record<string, any> }
  ): Promise<ApiResponse> {
    const response = await api.post<ApiResponse>(
      `/Android/devices/${serial}/mirror/start`,
      { options: options.options }
    );
    return response.data;
  },

  // Detener mirror
  async disconnectDevice(serial: string): Promise<ApiResponse> {
    const response = await api.post<ApiResponse>(
      `/android/devices/${serial}/mirror/stop`
    );
    return response.data;
  },

  // Tomar screenshot
  async takeScreenshotDownload(
    serial: string,
    filename: string
  ): Promise<Blob> {
    const response = await api.post(
      `/android/devices/${serial}/screenshot`,
      { filename },
      {
        responseType: "blob",
      }
    );
    return response.data;
  },

  // Ejecutar acción genérica (puedes usar el endpoint de ADB)
  async deviceAction(
    serial: string,
    action: DeviceAction
  ): Promise<ApiResponse> {
    // Usar acceso seguro a las propiedades
    const actionType = (action as any).type || action.toString();
    const actionCommand = (action as any).command || actionType;

    // Para Android, mapear a endpoints específicos
    if (actionType === "start_mirror") {
      return await this.connectDevice(serial, { options: [] });
    }

    if (actionType === "stop_mirror") {
      return await this.disconnectDevice(serial);
    }

    if (actionType === "screenshot") {
      const response = await api.post<ApiResponse>(
        `/android/devices/${serial}/screenshot`
      );
      return response.data;
    }

    // Para otros comandos, usar el endpoint ADB
    const response = await api.post<ApiResponse>(
      `/android/devices/${serial}/adb`,
      {
        command: actionCommand,
      }
    );
    return response.data;
  },

  // Obtener estado del dispositivo
  async getDeviceStatus(
    serial: string
  ): Promise<
    ApiResponse & { device: Device; connected: boolean; active: boolean }
  > {
    const response = await api.get<any>(`/android/devices/${serial}/status`);

    // Adaptar respuesta
    return {
      success: true,
      device: {
        serial: serial,
        name: `Device ${serial}`,
        platform: "android",
      } as Device,
      connected: response.data.connected,
      active: response.data.mirror_active,
    };
  },

  // Actualizar alias (no implementado en API, retornar success por ahora)
  async updateDeviceAlias(
    _serial: string,
    _alias: string
  ): Promise<{
    success: boolean;
    message?: string;
    error?: string;
  }> {
    try {
      // Por ahora retornar éxito, puedes implementar esto después
      return {
        success: true,
        message: "Alias actualizado correctamente",
      };
    } catch (error) {
      console.error("Error updating device alias:", error);
      return {
        success: false,
        error: "Error al actualizar alias",
      };
    }
  },
};
