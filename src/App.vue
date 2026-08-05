<template>
  <v-app>
    <div class="app-backdrop">
      <span class="blob blob-1"></span>
      <span class="blob blob-2"></span>
      <span class="blob blob-3"></span>
    </div>

    <v-btn
      class="theme-toggle-btn"
      icon
      variant="text"
      size="small"
      :aria-label="theme.global.current.value.dark ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'"
      @click="toggleTheme"
    >
      <v-icon>{{ theme.global.current.value.dark ? "mdi-weather-night" : "mdi-weather-sunny" }}</v-icon>
    </v-btn>

    <v-main>
      <v-container fluid>
        <IOSDriverBanner @notify="(message, color) => showNotification(message, color)" />
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
              :monitoring="monitoring"
              @device-selected="handleDeviceSelected"
              @refresh="refreshAllDevices"
              @toggle-monitoring="toggleMonitoring"
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
              @execute-action="executeDeviceAction"
              @notify="(message, color) => showNotification(message, color)"
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
      :timeout="snackbar.actionLabel ? 8000 : 3000"
      :actionLabel="snackbar.actionLabel"
      :onAction="snackbar.onAction"
      @update:show="snackbar.show = $event"
    />
  </v-app>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted, onUnmounted } from "vue";
  import type { Device } from "./types/common";
  import type { IOSDeviceResponse } from "./types/ios";
  import DeviceList from "./components/DeviceList.vue";
  import DeviceControls from "./components/DeviceControls.vue";
  import AppSnackbar from "./components/AppSnackbar.vue";
  import IOSDriverBanner from "./components/ios/IOSDriverBanner.vue";
  import { deviceApi } from "./services/api";
  import { iosApi } from "./services/iosApi";
  import { useDeviceHub } from "./composables/useDeviceHub";
  import { useDeviceActions } from "./composables/useDeviceActions";
  import { useAppTheme } from "./composables/useAppTheme";

  const { theme, toggleTheme } = useAppTheme();

  function mapIOSDevice(d: IOSDeviceResponse): Device {
    return {
      id: d.udid,
      serial: d.udid,
      name: d.name,
      model: d.model,
      iosVersion: d.iosVersion,
      platform: "ios",
      active: d.active,
    };
  }

  const devices = ref<Device[]>([]);
  const selectedDevice = ref<Device | null>(null);
  const selectedDeviceStatus = ref<any>(null);
  const actionLoading = ref(false);
  const refreshing = ref(false);
  const monitoring = ref(false);
  const snackbar = ref<{
    show: boolean;
    message: string;
    color: string;
    actionLabel?: string;
    onAction?: () => void;
  }>({ show: false, message: "", color: "info" });

  const allDevices = computed(() => devices.value);

  function showNotification(
    message: string,
    color?: string,
    actionLabel?: string,
    onAction?: () => void,
  ) {
    snackbar.value = {
      show: true,
      message,
      color: color || "info",
      actionLabel,
      onAction,
    };
  }

  const hub = useDeviceHub(
    devices,
    selectedDevice,
    selectedDeviceStatus,
    showNotification,
  );
  const { executeDeviceAction } = useDeviceActions(
    selectedDevice,
    devices,
    actionLoading,
    showNotification,
  );

  async function loadDevices() {
    refreshing.value = true;
    try {
      const [androidResult, iosDevices] = await Promise.all([
        deviceApi.getDevices(),
        iosApi.getDevices().catch(() => [] as IOSDeviceResponse[]),
      ]);
      devices.value = [
        ...(androidResult.devices || []),
        ...iosDevices.map(mapIOSDevice),
      ];
      showNotification(androidResult.message ?? "Dispositivos obtenidos", "info");
    } catch (error) {
      showNotification("Error al cargar dispositivos", "error");
    } finally {
      refreshing.value = false;
    }
  }

  async function handleDeviceSelected(device: Device) {
    // Salir del grupo del dispositivo anterior
    if (selectedDevice.value && selectedDevice.value.serial !== device.serial) {
      await hub.leaveDeviceGroup(selectedDevice.value.serial);
    }

    selectedDevice.value = device;
    selectedDeviceStatus.value = null;

    // Unirse al grupo del nuevo dispositivo para recibir MirrorStopped, MirrorStarted, etc.
    await hub.joinDeviceGroup(device.serial);

    try {
      selectedDeviceStatus.value =
        device.platform === "ios"
          ? await iosApi.getDeviceStatus(device.serial)
          : await deviceApi.getDeviceStatus(device.serial);

      // Si el mirror de iOS ya estaba corriendo (p.ej. tras recargar la app), traer
      // la URL del stream MJPEG para poder mostrarla embebida sin tener que
      // reiniciar el mirror.
      if (device.platform === "ios" && selectedDeviceStatus.value?.mirror_url) {
        device.mirrorUrl = `${selectedDeviceStatus.value.mirror_url}?t=${Date.now()}`;
      }
    } catch (error) {
      showNotification("Error al obtener estado del dispositivo", "error");
    }
  }

  async function toggleMonitoring(enabled: boolean) {
    try {
      if (enabled) {
        await deviceApi.startMonitoring();
        monitoring.value = true;
        showNotification("Monitoreo activado", "success");
      } else {
        await deviceApi.stopMonitoring();
        monitoring.value = false;
        showNotification("Monitoreo desactivado", "info");
      }
    } catch {
      showNotification("Error al cambiar estado de monitoreo", "error");
    }
  }

  function refreshAllDevices() {
    loadDevices();
  }

  onMounted(async () => {
    loadDevices();
    try {
      await hub.start();
      const status = await deviceApi.getMonitoringStatus();
      monitoring.value = status.isMonitoring;
      if (!monitoring.value) {
        await deviceApi.startMonitoring();
        monitoring.value = true;
        showNotification("Monitoreo activado al iniciar", "success");
      }
    } catch {
      // SignalR no disponible, app sigue funcionando sin tiempo real
    }
  });

  onUnmounted(async () => {
    await hub.stop();
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
