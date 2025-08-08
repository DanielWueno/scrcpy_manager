import type { IOSDevice, IOSAction, IOSStreamOptions, IOSMirrorSession } from '../types/ios';

const API_BASE_URL = 'http://localhost:5000/api'; // ✅ Cambiado de 8000 a 5000

export interface IOSApiResponse {
  success: boolean;
  message?: string;
  error?: string;
  data?: any;
}

export const iosApi = {
  async getDevices(): Promise<IOSDevice[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/ios/devices`);
      const data = await response.json();
      return data.success ? data.devices : [];
    } catch (error) {
      console.error('Error fetching iOS devices:', error);
      return [];
    }
  },

  async getDeviceInfo(udid: string): Promise<IOSApiResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/ios/devices/${udid}/info`);
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Error de conexión' };
    }
  },

  async startMirror(udid: string, options: IOSStreamOptions): Promise<IOSApiResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/ios/devices/${udid}/mirror/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ options }),
      });
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Error iniciando mirror iOS' };
    }
  },

  async stopMirror(udid: string): Promise<IOSApiResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/ios/devices/${udid}/mirror/stop`, {
        method: 'POST',
      });
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Error deteniendo mirror iOS' };
    }
  },

  async executeAction(udid: string, action: IOSAction, payload?: any): Promise<IOSApiResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/ios/devices/${udid}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, payload }),
      });
      return await response.json();
    } catch (error) {
      return { success: false, error: 'Error ejecutando acción iOS' };
    }
  },

  async takeScreenshot(udid: string): Promise<Blob | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/ios/devices/${udid}/screenshot`);
      if (response.ok) {
        return await response.blob();
      }
      return null;
    } catch (error) {
      console.error('Error taking iOS screenshot:', error);
      return null;
    }
  },

  async getMirrorSessions(): Promise<IOSMirrorSession[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/ios/mirror/sessions`);
      const data = await response.json();
      return data.success ? data.sessions : [];
    } catch (error) {
      console.error('Error fetching mirror sessions:', error);
      return [];
    }
  }
};