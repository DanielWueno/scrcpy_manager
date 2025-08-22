<template>
  <v-app theme="light">
    <v-main>
      <v-container fluid>
        <v-row>
          <!-- Panel izquierdo: Lista de dispositivos -->
          <v-col
            cols="12"
            md="4"
          >
            <DeviceList
              :devices="allDevices"
              :selectedDevice="selectedDevice"
              :loading="refreshing"
              :monitoring="false"
              @device-selected="handleDeviceSelected"
              @refresh="refreshAllDevices"
              @toggle-monitoring="() => {}"
            />
          </v-col>

          <!-- Panel derecho: Controles del dispositivo -->
          <v-col
            cols="12"
            md="8"
          >
            <DeviceControls
              :device="selectedDevice"
              :deviceStatus="selectedDeviceStatus"
              :actionLoading="actionLoading"
              @execute-action="executeDeviceActionWithPayload"
            />
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <!-- Snackbar segmentado -->
    <AppSnackbar
      :show="snackbar.show"
      :message="snackbar.message"
      :color="snackbar.color"
      :timeout="3000"
      @update:show="snackbar.show = $event"
    />
  </v-app>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted } from "vue";
  import type { Device } from "./types";
  import DeviceList from "./components/DeviceList.vue";
  import DeviceControls from "./components/DeviceControls.vue";
  import AppSnackbar from "./components/AppSnackbar.vue";
  import { deviceApi } from "./services/api";

  const devices = ref<Device[]>([]);
  const selectedDevice = ref<Device | null>(null);
  const selectedDeviceStatus = ref<any>(null);
  const actionLoading = ref(false);
  const refreshing = ref(false);
  const snackbar = ref({ show: false, message: "", color: "info" });

  const allDevices = computed(() => devices.value);

  function showNotification(message: string, color?: string) {
    snackbar.value = { show: true, message, color: color || "info" };
  }

  async function loadDevices() {
    refreshing.value = true;
    try {
      const result = await deviceApi.getDevices();
      devices.value = result.devices || [];
      showNotification(result.message ?? "Dispositivos obtenidos", "info");
    } catch (error) {
      showNotification("Error al cargar dispositivos", "error");
    } finally {
      refreshing.value = false;
    }
  }

  async function handleDeviceSelected(device: Device) {
    selectedDevice.value = device;
    selectedDeviceStatus.value = null;
    try {
      const status = await deviceApi.getDeviceStatus(device.serial);
      selectedDeviceStatus.value = status;
    } catch (error) {
      showNotification("Error al obtener estado del dispositivo", "error");
    }
  }

  async function executeDeviceActionWithPayload(action: string, payload?: any) {
    if (!selectedDevice.value) return;
    actionLoading.value = true;
    try {
      if (action === "start_mirror") {
        // Solo enviar las opciones relevantes como objeto
        // Siempre enviar las cuatro opciones, con true/false según los switches
        const optionsObj = {
          StayAwake: Boolean(payload?.StayAwake),
          NoAudio: Boolean(payload?.NoAudio),
          ShowTouches: Boolean(payload?.ShowTouches),
          TurnScreenOff: Boolean(payload?.TurnScreenOff),
        };
        console.log("Payload enviado a la API:", { options: optionsObj });
        const res = await deviceApi.connectDevice(selectedDevice.value.serial, {
          options: optionsObj,
        });
        showNotification(
          res.message || "Mirror iniciado",
          res.success ? "success" : "error"
        );
      } else if (action === "stop_mirror") {
        const res = await deviceApi.disconnectDevice(
          selectedDevice.value.serial
        );
        showNotification(
          res.message || "Mirror detenido",
          res.success ? "success" : "error"
        );
      } else {
        // Otras acciones genéricas
        const res = await deviceApi.deviceAction(selectedDevice.value.serial, {
          type: action,
          ...payload,
        });
        showNotification(
          res.message || "Acción ejecutada",
          res.success ? "success" : "error"
        );
      }
    } catch (error) {
      showNotification("Error al ejecutar acción", "error");
    } finally {
      actionLoading.value = false;
    }
  }

  function refreshAllDevices() {
    loadDevices();
  }

  onMounted(() => {
    loadDevices();
  });
</script>

<style scoped>
  .device-list {
    max-height: 70vh;
    overflow-y: auto;
  }

  .device-item {
    cursor: pointer;
    transition: all 0.2s ease;
    border-radius: 8px;
  }

  .device-item:hover {
    transform: translateX(2px);
  }

  .device-item--active {
    border-left: 3px solid rgb(var(--v-theme-primary));
  }

  /* Scrollbar minimalista */
  .device-list::-webkit-scrollbar {
    width: 4px;
  }

  .device-list::-webkit-scrollbar-track {
    background: transparent;
  }

  .device-list::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 2px;
  }

  .device-list::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.2);
  }
</style>
