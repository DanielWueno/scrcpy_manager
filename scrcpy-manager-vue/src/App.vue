<template>
  <v-app>
    <v-app-bar
      :elevation="8"
      dark
      height="80"
      class="gradient-bg"
    >
      <template v-slot:prepend>
        <v-avatar
          size="50"
          class="ma-2"
        >
          <v-icon
            size="30"
            color="white"
          >
            mdi-cellphone-wireless
          </v-icon>
        </v-avatar>
      </template>

      <v-app-bar-title class="text-h4 font-weight-bold">
        <span class="gradient-text">Scrcpy Manager</span>
        <div class="text-subtitle-2 opacity-80">Device Control</div>
      </v-app-bar-title>

      <v-spacer />

      <v-btn
        icon
        variant="text"
        class="mx-1 hover-btn"
        size="large"
        color="white"
        @click="toggleTheme"
      >
        <v-icon>{{
          isDark ? "mdi-weather-sunny" : "mdi-weather-night"
        }}</v-icon>
      </v-btn>

      <v-btn
        :loading="loading"
        icon
        variant="text"
        class="mx-1 hover-btn"
        size="large"
        title="Actualizar dispositivos manualmente"
        color="white"
        @click="manualRefresh"
      >
        <v-icon>mdi-refresh</v-icon>
      </v-btn>

      <v-btn
        icon
        variant="text"
        class="mx-1 hover-btn"
        size="large"
        color="white"
      >
        <v-icon>mdi-cog</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <ConnectionStatus ref="connectionStatus" />

      <v-container
        fluid
        class="pa-5"
        style="
          background: linear-gradient(
            180deg,
            rgba(255, 107, 53, 0.05) 0%,
            rgba(0, 78, 137, 0.05) 100%
          );
        "
      >
        <v-row>
          <v-col
            cols="12"
            md="8"
          >
            <v-card
              elevation="12"
              class="glass-card device-panel"
              rounded="xl"
            >
              <v-card-title class="pa-6">
                <div class="d-flex align-center">
                  <v-icon
                    left
                    size="30"
                    color="primary"
                  >
                    mdi-devices
                  </v-icon>
                  <span class="text-h5 font-weight-bold ml-3"
                    >Dispositivos Conectados</span
                  >
                </div>
                <v-spacer />
                <v-chip
                  :color="devices.length > 0 ? 'success' : 'warning'"
                  variant="flat"
                >
                  <div class="d-flex align-center">
                    <v-icon
                      left
                      class="pr-1 mr-1"
                    >
                      mdi-circle
                    </v-icon>
                  </div>
                  {{ devices.length }} dispositivos
                </v-chip>
              </v-card-title>

              <v-divider />

              <DeviceList
                :devices="devices"
                :loading="loading"
                :selected-device="selectedDevice"
                @device-selected="selectDevice"
                @refresh="refreshDevices"
              />
            </v-card>
          </v-col>

          <v-col
            cols="12"
            md="4"
          >
            <v-card
              elevation="12"
              class="glass-card control-panel"
              rounded="xl"
            >
              <v-card-title
                class="pa-7 gradient-bg text-white d-flex align-center"
              >
                <v-icon
                  left
                  size="30"
                  color="white"
                >
                  mdi-tune-variant
                </v-icon>
                <span class="text-h5 font-weight-bold ml-3">
                  Panel de Control
                </span>
              </v-card-title>

              <v-divider />

              <v-card-text class="pa-6">
                <div class="tool-section mb-6">
                  <v-card
                    variant="tonal"
                    class="pa-4 rounded-lg"
                    color="primary"
                  >
                    <v-card-title
                      class="pa-0 text-h6 mb-3 font-weight-bold d-flex align-center"
                    >
                      <v-icon
                        left
                        class="mr-3"
                      >
                        mdi-wrench
                      </v-icon>
                      Herramientas
                    </v-card-title>
                    <ToolbarFrame
                      :device="selectedDevice"
                      :loading="actionLoading"
                      @action="executeDeviceAction"
                      @action-payload="executeDeviceActionWithPayload"
                    />
                  </v-card>
                </div>

                <div class="config-section mb-6">
                  <v-card
                    variant="tonal"
                    class="pa-4 rounded-lg"
                    color="accent"
                  >
                    <v-card-title
                      class="pa-0 text-h6 mb-3 font-weight-bold d-flex align-center"
                    >
                      <v-icon
                        left
                        class="mr-3"
                      >
                        mdi-lightning-bolt
                      </v-icon>
                      Configuración Rápida
                    </v-card-title>
                    <QuickConfig v-model="connectionOptions" />
                  </v-card>
                </div>

                <v-btn
                  :disabled="!isDeviceSelected || actionLoading"
                  :loading="actionLoading"
                  :color="isDeviceActive ? 'error' : 'success'"
                  variant="flat"
                  block
                  size="x-large"
                  class="mb-6 connection-btn"
                  rounded="xl"
                  elevation="8"
                  @click="toggleConnection"
                >
                  <v-icon
                    left
                    size="25"
                    class="mr-3"
                  >
                    {{
                      isDeviceActive ? "mdi-lan-disconnect" : "mdi-lan-connect"
                    }}
                  </v-icon>
                  {{ connectionButtonText }}
                </v-btn>

                <v-card
                  variant="tonal"
                  class="pa-4 rounded-lg"
                  color="info"
                >
                  <v-card-title
                    class="pa-0 text-h6 mb-3 font-weight-bold d-flex align-center"
                  >
                    <v-icon
                      left
                      class="mr-3"
                    >
                      mdi-information
                    </v-icon>
                    Información del Dispositivo
                  </v-card-title>
                  <DeviceInfo
                    :device="selectedDevice"
                    @alias-updated="handleAliasUpdated"
                  />
                </v-card>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <div class="toast-container">
      <v-slide-y-transition group>
        <v-alert
          v-for="toast in toasts"
          :key="toast.id"
          :type="toast.type"
          closable
          class="mb-2"
          :value="true"
          @click:close="removeToast(toast.id)"
        >
          {{ toast.message }}
        </v-alert>
      </v-slide-y-transition>
    </div>
  </v-app>
</template>

<script setup lang="ts">
  import { onMounted, onUnmounted, computed, ref } from "vue";
  import { useTheme } from "vuetify";
  import DeviceList from "./components/DeviceList.vue";
  import ToolbarFrame from "./components/ToolbarFrame.vue";
  import QuickConfig from "./components/QuickConfig.vue";
  import DeviceInfo from "./components/DeviceInfo.vue";
  import ConnectionStatus from "./components/ConnectionStatus.vue";
  import { useDeviceManager } from "./composables/useDeviceManager";
  import type { DeviceAction } from "./types";

  const theme = useTheme();

  const {
    devices,
    selectedDevice,
    loading,
    actionLoading,
    toasts,
    connectionOptions,
    isDeviceSelected,
    isDeviceActive,
    connectionButtonText,
    removeToast,
    refreshDevices,
    manualRefresh,
    selectDevice,
    updateDeviceAlias,
    toggleConnection,
    executeDeviceAction,
  } = useDeviceManager();

  const handleAliasUpdated = async (serial: string, alias: string) => {
    await updateDeviceAlias(serial, alias);
  };

  const executeDeviceActionWithPayload = (
    action: DeviceAction,
    payload: any
  ) => {
    executeDeviceAction(action, payload);
  };

  const isDark = computed(() => theme.global.name.value === "dark");

  const toggleTheme = () => {
    theme.global.name.value = theme.global.current.value.dark
      ? "light"
      : "dark";
  };

  let refreshInterval: number;
  let isPageVisible = ref(true);
  let lastActivityTime = ref(Date.now());

  // Refresh: ajusta la frecuencia basado en actividad
  const getRefreshInterval = () => {
    const timeSinceActivity = Date.now() - lastActivityTime.value;
    if (timeSinceActivity < 30000) {
      // Últimos 30 segundos
      return 5000; // 5 segundos si hay actividad reciente
    } else if (timeSinceActivity < 300000) {
      // Últimos 5 minutos
      return 15000; // 15 segundos si actividad moderada
    } else {
      return 600000; // 10 minutos si no hay actividad
    }
  };

  const startSmartRefresh = () => {
    const refresh = () => {
      if (isPageVisible.value && !loading.value && !actionLoading.value) {
        refreshDevices();
      }

      clearInterval(refreshInterval);
      const newInterval = getRefreshInterval();
      console.log(`Refresh: próximo en ${newInterval / 1000}s`);
      refreshInterval = setInterval(refresh, newInterval);
    };

    const initialInterval = getRefreshInterval();
    console.log(`Iniciando refresh cada ${initialInterval / 1000}s`);
    refreshInterval = setInterval(refresh, initialInterval);
  };

  const updateActivity = () => {
    lastActivityTime.value = Date.now();
  };

  const handleVisibilityChange = () => {
    isPageVisible.value = !document.hidden;
    if (isPageVisible.value) {
      refreshDevices();
      updateActivity();
    }
  };

  onMounted(async () => {
    await refreshDevices();

    startSmartRefresh();

    document.addEventListener("visibilitychange", handleVisibilityChange);

    document.addEventListener("click", updateActivity);
    document.addEventListener("keydown", updateActivity);
  });

  onUnmounted(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
    document.removeEventListener("visibilitychange", handleVisibilityChange);
    document.removeEventListener("click", updateActivity);
    document.removeEventListener("keydown", updateActivity);
  });
</script>

<style scoped>
  .gradient-bg {
    background: linear-gradient(
      135deg,
      rgb(var(--v-theme-primary)) 0%,
      rgb(var(--v-theme-accent)) 100%
    ) !important;
  }

  .gradient-text {
    background: white;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    color: transparent;
  }

  .glass-card {
    backdrop-filter: blur(20px);
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.18);
    transition: box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .glass-card:hover {
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18) !important;
  }

  .hover-btn {
    transition: transform 0.2s;
  }

  .hover-btn::before {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: all 0.3s ease;
  }

  .hover-btn:hover::before {
    width: 100px;
    height: 100px;
  }

  .hover-btn:hover {
    transform: scale(1.04);
  }

  @keyframes pulse {
    0% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.05);
    }
    100% {
      transform: scale(1);
    }
  }

  .connection-btn {
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .connection-btn::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.3),
      transparent
    );
    transition: left 0.6s;
  }

  .connection-btn:hover::before {
    left: 100%;
  }

  .connection-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  }

  .device-panel {
    animation: slideInLeft 0.6s ease-out;
  }

  .control-panel {
    animation: slideInRight 0.6s ease-out;
  }

  @keyframes slideInLeft {
    from {
      transform: translateX(-100px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  @keyframes slideInRight {
    from {
      transform: translateX(100px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  .control-header {
    background: linear-gradient(
      135deg,
      rgb(var(--v-theme-primary)) 50%,
      white 100%
    );
    color: white;
  }

  .tool-section,
  .config-section {
    transition: all 0.3s ease;
  }

  .tool-section:hover,
  .config-section:hover {
    transform: translateY(-5px);
  }

  .toast-container {
    position: fixed;
    top: 100px;
    right: 20px;
    z-index: 9999;
    max-width: 400px;
  }

  @media (max-width: 768px) {
    .glass-card {
      margin: 10px;
    }

    .v-app-bar-title {
      font-size: 1.2rem !important;
    }
  }

  .v-theme--dark .glass-card {
    background: rgba(30, 30, 46, 0.8) !important;
    border: 1px solid rgba(255, 107, 53, 0.3);
  }

  .v-theme--light .glass-card {
    background: rgba(255, 255, 255, 0.8) !important;
    border: 1px solid rgba(0, 78, 137, 0.3);
  }

  ::-webkit-scrollbar {
    width: 8px;
  }

  ::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
  }

  ::-webkit-scrollbar-thumb {
    background: linear-gradient(
      135deg,
      rgb(var(--v-theme-primary)) 50%,
      white 100%
    );
    border-radius: 10px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(
      135deg,
      rgb(var(--v-theme-primary)) 50%,
      white 100%
    );
  }
</style>

<style scoped>
  .toast-container {
    position: fixed;
    top: 80px;
    right: 16px;
    z-index: 1000;
    max-width: 400px;
  }
</style>
