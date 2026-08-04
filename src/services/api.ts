import type {
  Device,
  DevicesResponse,
  ApiResponse,
  DeviceAction,
} from "../types/common";
import { createApiClient } from "./httpClient";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:59399/api";

const api = createApiClient(API_BASE_URL);

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

  // Iniciar mirror (mapear a tu endpoint)
  async connectDevice(
    serial: string,
    options: { options: Record<string, any> },
  ): Promise<ApiResponse> {
    const response = await api.post<ApiResponse>(
      `/android/devices/${serial}/mirror/start`,
      { options: options.options },
    );
    return response.data;
  },

  // Detener mirror
  async disconnectDevice(serial: string): Promise<ApiResponse> {
    const response = await api.post<ApiResponse>(
      `/android/devices/${serial}/mirror/stop`,
    );
    return response.data;
  },

  // Ejecutar acción genérica (puedes usar el endpoint de ADB)
  async deviceAction(
    serial: string,
    action: DeviceAction,
  ): Promise<ApiResponse> {
    // Usar acceso seguro a las propiedades
    const actionType = (action as any).type || action.toString();

    // Acciones de mirror
    if (actionType === "start_mirror") {
      return await this.connectDevice(serial, { options: [] });
    }
    if (actionType === "stop_mirror") {
      return await this.disconnectDevice(serial);
    }

    // Screenshot tiene endpoint dedicado
    if (actionType === "screenshot") {
      const response = await api.post<ApiResponse>(
        `/android/devices/${serial}/screenshot`,
      );
      return response.data;
    }

    // Acciones de teclado/pantalla → endpoint /action (mapeo en el backend)
    const deviceActions = new Set([
      "home_button",
      "back_button",
      "volume_up",
      "volume_down",
      "wake_device",
    ]);
    if (deviceActions.has(actionType)) {
      const response = await api.post<ApiResponse>(
        `/android/devices/${serial}/action`,
        { action: actionType, payload: {} },
      );
      return response.data;
    }

    // Otros comandos ADB libres
    const response = await api.post<ApiResponse>(
      `/android/devices/${serial}/adb`,
      { command: actionType },
    );
    return response.data;
  },

  async openScreenshotsFolder(): Promise<void> {
    await api.post("/files/open-folder");
  },

  // Monitoreo
  async getMonitoringStatus(): Promise<{ isMonitoring: boolean }> {
    const response = await api.get<{ isMonitoring: boolean }>(
      "/monitoring/status",
    );
    return response.data;
  },

  async startMonitoring(): Promise<void> {
    await api.post("/monitoring/start");
  },

  async stopMonitoring(): Promise<void> {
    await api.post("/monitoring/stop");
  },

  // Obtener estado del dispositivo
  async getDeviceStatus(
    serial: string,
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
};

export const extensionApi = {
  async getMobileRemoteToolkitInfo(): Promise<{
    available: boolean;
    version: string;
  }> {
    try {
      const response = await api.get<{ available: boolean; version: string }>(
        "/extension/mobile-remote-toolkit",
      );
      return response.data;
    } catch {
      return { available: false, version: "0.0.0" };
    }
  },

  getDownloadUrl(): string {
    return `${API_BASE_URL}/extension/mobile-remote-toolkit/download`;
  },
};
