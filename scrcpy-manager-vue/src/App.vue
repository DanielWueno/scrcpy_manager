<!-- filepath: c:\Users\DSOFT03.CORP\Documents\Soft\scrcpy_manager\scrcpy-manager-vue\scrcpy-manager-vue\src\App.vue -->
<template>
  <v-app>
    <!-- App Bar con gradiente y efectos geniales -->
    <v-app-bar
      :elevation="8"
      style="background: linear-gradient(135deg, #ff6b35 0%, #004e89 100%)"
      dark
      height="80"
    >
      <template v-slot:prepend>
        <v-avatar
          size="50"
          class="ma-2"
        >
          <v-icon
            size="30"
            color="white"
            >mdi-cellphone-wireless</v-icon
          >
        </v-avatar>
      </template>

      <v-app-bar-title class="text-h4 font-weight-bold">
        <span class="gradient-text">Scrcpy Manager</span>
        <div class="text-subtitle-2 opacity-80">Pro Device Control</div>
      </v-app-bar-title>

      <v-spacer />

      <!-- Botones con efectos hover -->
      <v-btn
        @click="toggleTheme"
        icon
        variant="text"
        class="mx-1 hover-btn"
        size="large"
      >
        <v-icon>{{
          isDark ? "mdi-weather-sunny" : "mdi-weather-night"
        }}</v-icon>
      </v-btn>

      <v-btn
        @click="manualRefresh"
        :loading="loading"
        icon
        variant="text"
        class="mx-1 hover-btn"
        size="large"
        title="Actualizar dispositivos manualmente"
      >
        <v-icon>mdi-refresh</v-icon>
      </v-btn>

      <v-btn
        icon
        variant="text"
        class="mx-1 hover-btn"
        size="large"
      >
        <v-icon>mdi-cog</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <!-- Estado de conexión API con mejor diseño -->
      <ConnectionStatus ref="connectionStatus" />

      <!-- Contenido principal con efectos visuales -->
      <v-container
        fluid
        class="pa-6"
        style="
          background: linear-gradient(
            180deg,
            rgba(255, 107, 53, 0.05) 0%,
            rgba(0, 78, 137, 0.05) 100%
          );
        "
      >
        <v-row>
          <!-- Panel de dispositivos mejorado -->
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
                <v-icon
                  left
                  size="30"
                  color="primary"
                  >mdi-devices</v-icon
                >
                <span class="text-h5 font-weight-bold ml-3"
                  >Dispositivos Conectados</span
                >
                <v-spacer />
                <v-chip
                  :color="devices.length > 0 ? 'success' : 'warning'"
                  variant="flat"
                  class="pulse-animation"
                >
                  <v-icon left>mdi-circle</v-icon>
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

          <!-- Panel de control mejorado -->
          <v-col
            cols="12"
            md="4"
          >
            <v-card
              elevation="12"
              class="glass-card control-panel"
              rounded="xl"
            >
              <v-card-title class="pa-6 control-header">
                <v-icon
                  left
                  size="30"
                  color="secondary"
                  >mdi-tune-variant</v-icon
                >
                <span class="text-h5 font-weight-bold ml-3"
                  >Panel de Control</span
                >
              </v-card-title>

              <v-divider />

              <v-card-text class="pa-6">
                <!-- Herramientas con efectos -->
                <div class="tool-section mb-6">
                  <v-card
                    variant="tonal"
                    class="pa-4 rounded-lg"
                    color="primary"
                  >
                    <v-card-title class="pa-0 text-h6 mb-3">
                      <v-icon
                        left
                        color="white"
                        >mdi-wrench</v-icon
                      >
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

                <!-- Configuración rápida con estilo -->
                <div class="config-section mb-6">
                  <v-card
                    variant="tonal"
                    class="pa-4 rounded-lg"
                    color="accent"
                  >
                    <v-card-title class="pa-0 text-h6 mb-3">
                      <v-icon
                        left
                        color="white"
                        >mdi-lightning-bolt</v-icon
                      >
                      Configuración Rápida
                    </v-card-title>
                    <QuickConfig v-model="connectionOptions" />
                  </v-card>
                </div>

                <!-- Botón de conexión súper chido -->
                <v-btn
                  @click="toggleConnection"
                  :disabled="!isDeviceSelected || actionLoading"
                  :loading="actionLoading"
                  :color="isDeviceActive ? 'error' : 'success'"
                  variant="flat"
                  block
                  size="x-large"
                  class="mb-6 connection-btn"
                  rounded="xl"
                  elevation="8"
                >
                  <v-icon
                    left
                    size="25"
                  >
                    {{
                      isDeviceActive ? "mdi-lan-disconnect" : "mdi-lan-connect"
                    }}
                  </v-icon>
                  {{ connectionButtonText }}
                </v-btn>

                <!-- Info del dispositivo con mejor diseño -->
                <v-card
                  variant="tonal"
                  class="pa-4 rounded-lg"
                  color="info"
                >
                  <v-card-title class="pa-0 text-h6 mb-3">
                    <v-icon
                      left
                      color="white"
                      >mdi-information</v-icon
                    >
                    Información del Dispositivo
                  </v-card-title>
                  <DeviceInfo :device="selectedDevice" />
                </v-card>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <!-- Toast notifications -->
    <div class="toast-container">
      <v-slide-y-transition group>
        <v-alert
          v-for="toast in toasts"
          :key="toast.id"
          :type="toast.type"
          closable
          @click:close="removeToast(toast.id)"
          class="mb-2"
          :value="true"
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
    showToast,
    removeToast,
    refreshDevices,
    manualRefresh,
    selectDevice,
    toggleConnection,
    executeDeviceAction,
  } = useDeviceManager();

  // Función para manejar acciones con payload personalizado
  const executeDeviceActionWithPayload = (
    action: DeviceAction,
    payload: any
  ) => {
    executeDeviceAction(action, payload);
  };

  // Función para cambiar tema
  const isDark = computed(() => theme.global.name.value === "dark");

  const toggleTheme = () => {
    theme.global.name.value = theme.global.current.value.dark
      ? "light"
      : "dark";
  };

  let refreshInterval: number;
  let isPageVisible = ref(true);
  let lastActivityTime = ref(Date.now());

  // Smart refresh: ajusta la frecuencia basado en actividad
  const getRefreshInterval = () => {
    const timeSinceActivity = Date.now() - lastActivityTime.value;
    if (timeSinceActivity < 30000) {
      // Últimos 30 segundos
      return 5000; // 5 segundos si hay actividad reciente
    } else if (timeSinceActivity < 300000) {
      // Últimos 5 minutos
      return 15000; // 15 segundos si actividad moderada
    } else {
      return 60000; // 1 minuto si no hay actividad
    }
  };

  const startSmartRefresh = () => {
    const refresh = () => {
      if (isPageVisible.value && !loading.value && !actionLoading.value) {
        refreshDevices();
      }

      // Reconfigurar con nuevo intervalo basado en actividad
      clearInterval(refreshInterval);
      const newInterval = getRefreshInterval();
      console.log(`🔄 Refresh inteligente: próximo en ${newInterval / 1000}s`);
      refreshInterval = setInterval(refresh, newInterval);
    };

    const initialInterval = getRefreshInterval();
    console.log(
      `🔄 Iniciando refresh inteligente cada ${initialInterval / 1000}s`
    );
    refreshInterval = setInterval(refresh, initialInterval);
  };

  const updateActivity = () => {
    lastActivityTime.value = Date.now();
  };

  // Detectar visibilidad de la página
  const handleVisibilityChange = () => {
    isPageVisible.value = !document.hidden;
    if (isPageVisible.value) {
      // Cuando la página vuelve a ser visible, hacer refresh inmediato
      refreshDevices();
      updateActivity();
    }
  };

  onMounted(async () => {
    await refreshDevices();

    // Configurar refresh inteligente
    startSmartRefresh();

    // Escuchar cambios de visibilidad
    document.addEventListener("visibilitychange", handleVisibilityChange);

    // Actualizar actividad en interacciones del usuario
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
  /* Gradientes y efectos chidos */
  .gradient-text {
    background: linear-gradient(45deg, #ffffff, #ffeb3b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  /* Efectos de cristal (glassmorphism) */
  .glass-card {
    backdrop-filter: blur(20px);
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .glass-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3) !important;
  }

  /* Botones con hover súper chidos */
  .hover-btn {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
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
    transform: scale(1.1);
  }

  /* Animación de pulso para chips */
  .pulse-animation {
    animation: pulse 2s infinite;
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

  /* Botón de conexión con efectos especiales */
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

  /* Paneles con animaciones */
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

  /* Header del control panel */
  .control-header {
    background: linear-gradient(135deg, #ff6b35 0%, #004e89 100%);
    color: white;
  }

  /* Secciones de herramientas */
  .tool-section,
  .config-section {
    transition: all 0.3s ease;
  }

  .tool-section:hover,
  .config-section:hover {
    transform: translateY(-5px);
  }

  /* Container de notificaciones */
  .toast-container {
    position: fixed;
    top: 100px;
    right: 20px;
    z-index: 9999;
    max-width: 400px;
  }

  /* Efectos de neón */
  .neon-border {
    border: 2px solid;
    border-image: linear-gradient(45deg, #ff6b35, #004e89) 1;
    box-shadow: 0 0 10px rgba(255, 107, 53, 0.5),
      inset 0 0 10px rgba(0, 78, 137, 0.5);
  }

  /* Responsive mejoras */
  @media (max-width: 768px) {
    .glass-card {
      margin: 10px;
    }

    .v-app-bar-title {
      font-size: 1.2rem !important;
    }
  }

  /* Dark theme específico */
  .v-theme--dark .glass-card {
    background: rgba(30, 30, 46, 0.8) !important;
    border: 1px solid rgba(255, 107, 53, 0.3);
  }

  /* Light theme específico */
  .v-theme--light .glass-card {
    background: rgba(255, 255, 255, 0.8) !important;
    border: 1px solid rgba(0, 78, 137, 0.3);
  }

  /* Scrollbar personalizado */
  ::-webkit-scrollbar {
    width: 8px;
  }

  ::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
  }

  ::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #ff6b35, #004e89);
    border-radius: 10px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #004e89, #ff6b35);
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
