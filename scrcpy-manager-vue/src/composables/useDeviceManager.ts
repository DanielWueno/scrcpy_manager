import { ref, computed } from "vue";
import { deviceApi } from "../services/api";
import type {
  Device,
  ConnectionOptions,
  ToastMessage,
  DeviceAction,
} from "../types";

export function useDeviceManager() {
  const devices = ref<Device[]>([]);
  const selectedDevice = ref<Device | null>(null);
  const loading = ref(false);
  const actionLoading = ref(false);
  const toasts = ref<ToastMessage[]>([]);

  const connectionOptions = ref<ConnectionOptions>({
    stayAwake: true,
    showTouches: false,
    noAudio: true,
    turnScreenOff: false,
  });

  const isDeviceSelected = computed(() => selectedDevice.value !== null);
  const isDeviceActive = computed(() => selectedDevice.value?.active ?? false);
  const connectionButtonText = computed(() => {
    if (!selectedDevice.value) return "Conectar Dispositivo";
    return selectedDevice.value.active ? "Desconectar" : "Conectar";
  });

  const showToast = (
    message: string,
    type: ToastMessage["type"] = "info",
    timeout = 5000
  ) => {
    const toast: ToastMessage = {
      id: Date.now(),
      message,
      type,
      timeout,
    };
    toasts.value.push(toast);

    setTimeout(() => {
      removeToast(toast.id);
    }, timeout);
  };

  const removeToast = (id: number) => {
    const index = toasts.value.findIndex((t) => t.id === id);
    if (index > -1) {
      toasts.value.splice(index, 1);
    }
  };

  const refreshDevices = async () => {
    loading.value = true;
    try {
      const response = await deviceApi.refreshDevices();
      if (response.success) {
        devices.value = response.devices;

        if (response.new_devices_count && response.new_devices_count > 0) {
          showToast(
            `Se detectaron ${response.new_devices_count} dispositivo(s) nuevo(s)`,
            "info"
          );
        }

        if (selectedDevice.value) {
          const updated = devices.value.find(
            (d) => d.serial === selectedDevice.value!.serial
          );
          if (updated) {
            selectedDevice.value = updated;
          }
        }
      } else {
        showToast(
          response.error || "Error al actualizar dispositivos",
          "error"
        );
      }
    } catch (error: any) {
      console.error("Error refreshing devices:", error);

      if (error.code === "ERR_NETWORK" || error.code === "ECONNREFUSED") {
        showToast(
          "Backend API no disponible - Verifica que el servidor esté corriendo en puerto 5000",
          "error",
          8000
        );
      } else {
        showToast("Error de conexión al actualizar dispositivos", "error");
      }

      devices.value = [];
    } finally {
      loading.value = false;
    }
  };

  const selectDevice = async (device: Device | null) => {
    selectedDevice.value = device;
    if (device) {
      await updateDeviceStatus(device.serial);
    }
  };

  const updateDeviceStatus = async (serial: string) => {
    try {
      const response = await deviceApi.getDeviceStatus(serial);
      if (response.success && selectedDevice.value?.serial === serial) {
        selectedDevice.value = {
          ...selectedDevice.value,
          ...response.device,
          connected: response.connected,
          active: response.active,
        };
      }
    } catch (error) {
      console.error("Error updating device status:", error);
    }
  };

  const getConnectionOptions = (): string[] => {
    const options: string[] = [];
    if (connectionOptions.value.noAudio) options.push("--no-audio");
    if (connectionOptions.value.stayAwake) options.push("--stay-awake");
    if (connectionOptions.value.showTouches) options.push("--show-touches");
    if (connectionOptions.value.turnScreenOff)
      options.push("--turn-screen-off");
    return options;
  };

  const toggleConnection = async () => {
    if (!selectedDevice.value) return;

    actionLoading.value = true;
    try {
      const isActive = selectedDevice.value.active;

      if (isActive) {
        const response = await deviceApi.disconnectDevice(
          selectedDevice.value.serial
        );
        if (response.success) {
          showToast(`Desconectado de ${selectedDevice.value.alias}`, "success");
        } else {
          showToast(response.error || "Error al desconectar", "error");
        }
      } else {
        const options = getConnectionOptions();
        const response = await deviceApi.connectDevice(
          selectedDevice.value.serial,
          { options }
        );
        if (response.success) {
          showToast(`Conectado a ${selectedDevice.value.alias}`, "success");
        } else {
          const errorMsg = response.error || "Error al conectar";

          if (errorMsg.includes("Could not find ADB device")) {
            showToast(
              `Dispositivo ${selectedDevice.value.alias} no está conectado físicamente`,
              "error"
            );
          } else if (errorMsg.includes("unauthorized")) {
            showToast(
              `Autoriza la depuración USB en ${selectedDevice.value.alias}`,
              "warning"
            );
          } else {
            showToast(`${errorMsg}`, "error");
          }
        }
      }

      setTimeout(() => {
        if (selectedDevice.value) {
          updateDeviceStatus(selectedDevice.value.serial);
        }
      }, 800);
    } catch (error) {
      showToast("Error de conexión", "error");
      console.error("Connection error:", error);
    } finally {
      actionLoading.value = false;
    }
  };

  const executeDeviceAction = async (action: DeviceAction, payload?: any) => {
    if (!selectedDevice.value) {
      showToast("Selecciona un dispositivo primero", "warning");
      return;
    }

    actionLoading.value = true;
    try {
      let response;

      if (action === "screenshot") {
        const filename =
          payload?.filename ||
          `screenshot_${selectedDevice.value.alias}_${Date.now()}.png`;

        try {
          const blob = await deviceApi.takeScreenshotDownload(
            selectedDevice.value.serial,
            filename
          );

          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);

          showToast(`Captura descargada: ${filename}`, "success", 5000);
          return;
        } catch (error) {
          showToast("Error al descargar captura", "error");
          return;
        }
      } else {
        response = await deviceApi.deviceAction(
          selectedDevice.value.serial,
          action
        );
        if (response.success) {
          showToast(response.message || "Acción ejecutada", "success");
        }
      }

      if (response && !response.success) {
        showToast(
          response.error || response.message || "Error en la acción",
          "error"
        );
      }

      if (["mirror_screen_off", "mirror_screen_on"].includes(action)) {
        setTimeout(() => {
          if (selectedDevice.value) {
            updateDeviceStatus(selectedDevice.value.serial);
          }
        }, 500);
      }
    } catch (error) {
      showToast("Error ejecutando acción", "error");
      console.error("Action error:", error);
    } finally {
      actionLoading.value = false;
    }
  };

  const manualRefresh = async () => {
    showToast("Actualizando dispositivos...", "info", 2000);
    await refreshDevices();
  };

  const updateDeviceAlias = async (serial: string, alias: string) => {
    try {
      const response = await deviceApi.updateDeviceAlias(serial, alias);

      if (response.success) {
        const deviceIndex = devices.value.findIndex((d) => d.serial === serial);
        if (deviceIndex !== -1) {
          devices.value[deviceIndex].alias = alias;
          if (!devices.value[deviceIndex].name) {
            devices.value[deviceIndex].name = alias;
          }
        }

        if (selectedDevice.value?.serial === serial) {
          selectedDevice.value.alias = alias;
          if (!selectedDevice.value.name) {
            selectedDevice.value.name = alias;
          }
        }

        showToast(
          response.message || `Alias actualizado a "${alias}"`,
          "success"
        );

        await refreshDevices();
      } else {
        showToast(response.error || "Error al actualizar alias", "error");
      }
    } catch (error) {
      showToast("Error de conexión al actualizar alias", "error");
      console.error("Alias update error:", error);
    }
  };

  return {
    devices,
    selectedDevice,
    loading,
    actionLoading,
    toasts,
    connectionOptions,
    isDeviceSelected,
    isDeviceActive,
    connectionButtonText,
    showToast,
    removeToast,
    refreshDevices,
    manualRefresh,
    selectDevice,
    updateDeviceStatus,
    updateDeviceAlias,
    toggleConnection,
    executeDeviceAction,
  };
}
