import { ref, computed } from "vue";
import type { IOSDevice, IOSAction, IOSStreamOptions, IOSMirrorSession } from "../../types/ios";
import { iosApi } from "../../services/iosApi";

export function useIOSManager() {
  const iosDevices = ref<IOSDevice[]>([]);
  const activeSessions = ref<IOSMirrorSession[]>([]);
  const loading = ref(false);
  const actionLoading = ref(false);

  // Opciones por defecto para iOS
  const defaultIOSOptions = ref<IOSStreamOptions>({
    quality: 'medium',
    fps: 30,
    enableAudio: true,
    enableControl: true,
    port: 8100,
    fullscreen: false
  });

  // Computadas
  const connectedIOSDevices = computed(() => 
    iosDevices.value.filter(device => device.connected)
  );

  const activeIOSDevices = computed(() => 
    iosDevices.value.filter(device => device.active)
  );

  // Funciones principales
  const refreshIOSDevices = async (): Promise<void> => {
    loading.value = true;
    try {
      const devices = await iosApi.getDevices();
      iosDevices.value = devices;
      
      // Actualizar sesiones activas
      const sessions = await iosApi.getMirrorSessions();
      activeSessions.value = sessions;
      
      // Sincronizar estado activo
      iosDevices.value.forEach(device => {
        device.active = sessions.some(session => 
          session.udid === device.serial && session.status === 'active'
        );
      });
    } catch (error) {
      console.error('Error refreshing iOS devices:', error);
    } finally {
      loading.value = false;
    }
  };

  const startIOSMirror = async (udid: string, options?: Partial<IOSStreamOptions>): Promise<boolean> => {
    actionLoading.value = true;
    try {
      const mirrorOptions = { ...defaultIOSOptions.value, ...options };
      const response = await iosApi.startMirror(udid, mirrorOptions);
      
      if (response.success) {
        // Actualizar estado del dispositivo
        const device = iosDevices.value.find(d => d.serial === udid);
        if (device) {
          device.active = true;
        }
        
        // Agregar sesión activa
        activeSessions.value.push({
          udid,
          port: mirrorOptions.port || 8100,
          startedAt: new Date().toISOString(),
          options: mirrorOptions,
          status: 'active'
        });
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error starting iOS mirror:', error);
      return false;
    } finally {
      actionLoading.value = false;
    }
  };

  const stopIOSMirror = async (udid: string): Promise<boolean> => {
    actionLoading.value = true;
    try {
      const response = await iosApi.stopMirror(udid);
      
      if (response.success) {
        // Actualizar estado del dispositivo
        const device = iosDevices.value.find(d => d.serial === udid);
        if (device) {
          device.active = false;
        }
        
        // Remover sesión activa
        activeSessions.value = activeSessions.value.filter(
          session => session.udid !== udid
        );
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error stopping iOS mirror:', error);
      return false;
    } finally {
      actionLoading.value = false;
    }
  };

  const executeIOSAction = async (udid: string, action: IOSAction, payload?: any): Promise<boolean> => {
    actionLoading.value = true;
    try {
      let response;

      // Manejar acciones especiales
      if (action === "ios_screenshot") {
        const blob = await iosApi.takeScreenshot(udid);
        if (blob) {
          // Descargar screenshot automáticamente
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `ios_screenshot_${udid.slice(-4)}_${Date.now()}.png`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
          return true;
        }
        return false;
      } else if (action === "ios_mirror") {
        return await startIOSMirror(udid, payload);
      } else if (action === "ios_stop_mirror") {
        return await stopIOSMirror(udid);
      } else {
        response = await iosApi.executeAction(udid, action, payload);
        return response.success;
      }
    } catch (error) {
      console.error('Error executing iOS action:', error);
      return false;
    } finally {
      actionLoading.value = false;
    }
  };

  const getIOSOptions = (): IOSStreamOptions => {
    return { ...defaultIOSOptions.value };
  };

  const updateIOSOptions = (options: Partial<IOSStreamOptions>): void => {
    defaultIOSOptions.value = { ...defaultIOSOptions.value, ...options };
  };

  const getMirrorSession = (udid: string): IOSMirrorSession | undefined => {
    return activeSessions.value.find(session => session.udid === udid);
  };

  const isIOSMirrorActive = (udid: string): boolean => {
    const session = getMirrorSession(udid);
    return session ? session.status === 'active' : false;
  };

  const getDeviceDisplayName = (device: IOSDevice): string => {
    return device.alias || device.name || `iPhone ${device.serial.slice(-4)}`;
  };

  return {
    // Estado
    iosDevices,
    activeSessions,
    loading,
    actionLoading,
    defaultIOSOptions,

    // Computadas
    connectedIOSDevices,
    activeIOSDevices,

    // Métodos principales
    refreshIOSDevices,
    startIOSMirror,
    stopIOSMirror,
    executeIOSAction,

    // Configuración
    getIOSOptions,
    updateIOSOptions,

    // Utilidades
    getMirrorSession,
    isIOSMirrorActive,
    getDeviceDisplayName,
  };
}
