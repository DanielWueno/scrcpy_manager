import * as signalR from "@microsoft/signalr";
import type { Ref } from "vue";
import type { Device } from "../types/common";

type Notify = (message: string, color?: string) => void;

export function useDeviceHub(
  devices: Ref<Device[]>,
  selectedDevice: Ref<Device | null>,
  selectedDeviceStatus: Ref<any>,
  notify: Notify,
) {
  const SIGNALR_URL =
    import.meta.env.VITE_SIGNALR_URL || "http://localhost:59399/hubs/android";

  const hubConnection = new signalR.HubConnectionBuilder()
    .withUrl(SIGNALR_URL)
    .withAutomaticReconnect()
    .configureLogging(signalR.LogLevel.Warning)
    .build();

  hubConnection.on("DeviceConnected", (device: any) => {
    const serial = device.serial ?? device.Serial;
    if (devices.value.find((d) => d.serial === serial)) return;
    devices.value.push({
      id: serial,
      serial,
      name: device.name ?? device.Name ?? serial,
      brand: device.brand ?? device.Brand,
      model: device.model ?? device.Model,
      androidVersion: device.androidVersion ?? device.AndroidVersion,
      platform: device.platform ?? device.Platform ?? "android",
      active: false,
    } as Device);
    notify(`Dispositivo conectado: ${device.name ?? serial}`, "success");
  });

  hubConnection.on("DeviceDisconnected", (serial: string) => {
    const idx = devices.value.findIndex((d) => d.serial === serial);
    if (idx === -1) return;
    const name = devices.value[idx].name ?? serial;
    devices.value.splice(idx, 1);
    if (selectedDevice.value?.serial === serial) {
      selectedDevice.value = null;
      selectedDeviceStatus.value = null;
    }
    notify(`Dispositivo desconectado: ${name}`, "warning");
  });

  hubConnection.on("MirrorStopped", (serial: string) => {
    const dev = devices.value.find((d) => d.serial === serial);
    if (dev) dev.active = false;
    if (selectedDevice.value?.serial === serial) {
      selectedDevice.value.active = false;
    }
    notify(`Mirror cerrado: ${serial}`, "info");
  });

  async function joinDeviceGroup(serial: string) {
    if (hubConnection.state === signalR.HubConnectionState.Connected) {
      await hubConnection.invoke("JoinDeviceGroup", serial).catch(() => {});
    }
  }

  async function leaveDeviceGroup(serial: string) {
    if (hubConnection.state === signalR.HubConnectionState.Connected) {
      await hubConnection.invoke("LeaveDeviceGroup", serial).catch(() => {});
    }
  }

  async function start() {
    await hubConnection.start();
    // Reincorporarse al grupo del dispositivo seleccionado tras reconexión
    hubConnection.onreconnected(async () => {
      if (selectedDevice.value) {
        await joinDeviceGroup(selectedDevice.value.serial);
      }
    });
  }

  async function stop() {
    await hubConnection.stop();
  }

  return { hubConnection, start, stop, joinDeviceGroup, leaveDeviceGroup };
}
