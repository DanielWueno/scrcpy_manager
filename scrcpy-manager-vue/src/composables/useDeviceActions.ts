import type { Ref } from "vue";
import type { Device, ApiResponse } from "../types/common";
import { deviceApi } from "../services/api";
import { iosApi } from "../services/iosApi";

type Notify = (
  message: string,
  color?: string,
  actionLabel?: string,
  onAction?: () => void,
) => void;

type Platform = "android" | "ios";

interface PlatformActions {
  startMirror(serial: string, payload?: any): Promise<ApiResponse>;
  stopMirror(serial: string): Promise<ApiResponse>;
  screenshot(serial: string, payload?: any): Promise<ApiResponse>;
  // null significa "accion no soportada en esta plataforma"
  genericAction(
    serial: string,
    action: string,
    payload?: any,
  ): Promise<ApiResponse> | null;
}

const androidActions: PlatformActions = {
  startMirror: (serial, payload) =>
    deviceApi.connectDevice(serial, {
      options: {
        stayAwake: Boolean(payload?.stayAwake),
        noAudio: Boolean(payload?.noAudio),
        showTouches: Boolean(payload?.showTouches),
        turnScreenOff: Boolean(payload?.turnScreenOff),
      },
    }),
  stopMirror: (serial) => deviceApi.disconnectDevice(serial),
  screenshot: (serial, payload) =>
    deviceApi.deviceAction(serial, { type: "screenshot", ...payload }),
  genericAction: (serial, action, payload) =>
    deviceApi.deviceAction(serial, { type: action, ...payload }),
};

const iosActions: PlatformActions = {
  startMirror: (serial) => iosApi.startMirror(serial),
  stopMirror: (serial) => iosApi.stopMirror(serial),
  screenshot: (serial) => iosApi.takeScreenshot(serial),
  genericAction: () => null,
};

const labelsByPlatform: Record<
  Platform,
  { start: string; stop: string; genericError: string }
> = {
  android: {
    start: "Mirror iniciado",
    stop: "Mirror detenido",
    genericError: "Error al ejecutar acción",
  },
  ios: {
    start: "Mirror iOS iniciado",
    stop: "Mirror iOS detenido",
    genericError: "Error al ejecutar acción iOS",
  },
};

function platformFor(device: Device): Platform {
  return device.platform === "ios" ? "ios" : "android";
}

export function useDeviceActions(
  selectedDevice: Ref<Device | null>,
  devices: Ref<Device[]>,
  actionLoading: Ref<boolean>,
  notify: Notify,
) {
  function setActive(active: boolean) {
    const device = selectedDevice.value;
    if (!device) return;
    device.active = active;
    const tracked = devices.value.find((d) => d.serial === device.serial);
    if (tracked) tracked.active = active;
    if (active) {
      window.dockApi
        ?.attach(device.serial, platformFor(device))
        .then((r) => {
          if (!r.success)
            console.warn("[Dock] No se pudo hacer dock:", r.error);
        });
    } else {
      window.dockApi?.detach();
    }
  }

  async function handleScreenshot(actions: PlatformActions, device: Device, payload?: any) {
    const res = await actions.screenshot(device.serial, payload);
    if (res.success && res.data) {
      const filename = (res.data as any).filename ?? "";
      const fullPath = (res.data as any).full_path;
      let clipboardMessage = "";

      if (fullPath && window.clipboardApi) {
        const clipboardResult = await window.clipboardApi.copyImagePath(fullPath);
        clipboardMessage = clipboardResult.success
          ? " y copiada al portapapeles"
          : " (no se pudo copiar al portapapeles)";
      }

      notify(
        `Captura guardada: ${filename}${clipboardMessage}`,
        "success",
        "Abrir carpeta",
        () => deviceApi.openScreenshotsFolder().catch(() => {}),
      );
    } else {
      notify(res.message || "Error al capturar pantalla", "error");
    }
  }

  async function executeDeviceAction(action: string, payload?: any) {
    const device = selectedDevice.value;
    if (!device) return;

    const platform = platformFor(device);
    const actions = platform === "ios" ? iosActions : androidActions;
    const labels = labelsByPlatform[platform];

    actionLoading.value = true;
    try {
      if (action === "start_mirror") {
        const res = await actions.startMirror(device.serial, payload);
        if (res.success) setActive(true);
        notify(res.message || labels.start, res.success ? "success" : "error");
      } else if (action === "stop_mirror") {
        const res = await actions.stopMirror(device.serial);
        if (res.success) setActive(false);
        notify(res.message || labels.stop, res.success ? "success" : "error");
      } else if (action === "screenshot") {
        await handleScreenshot(actions, device, payload);
      } else if (platform === "ios") {
        notify("Acción todavía no soportada para iOS", "warning");
      } else {
        const res = await actions.genericAction(device.serial, action, payload);
        notify(res?.message || "Acción ejecutada", res?.success ? "success" : "error");
      }
    } catch (error) {
      notify(labels.genericError, "error");
    } finally {
      actionLoading.value = false;
    }
  }

  return { executeDeviceAction };
}
