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
            <!-- Header -->
            <v-card
              variant="flat"
              class="mb-4 bg-grey-lighten-4"
            >
              <v-card-title class="d-flex align-center pa-4">
                <v-icon
                  class="mr-2"
                  color="primary"
                  size="20"
                  >mdi-devices</v-icon
                >
                <span class="text-h6">Dispositivos</span>
                <v-spacer></v-spacer>
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  @click="refreshDevices"
                  :loading="refreshing"
                >
                  <v-icon size="18">mdi-refresh</v-icon>
                </v-btn>
              </v-card-title>
            </v-card>

            <!-- Lista de dispositivos -->
            <div v-if="devices.length === 0">
              <v-card
                variant="flat"
                class="bg-grey-lighten-5"
              >
                <v-card-text class="text-center pa-6">
                  <v-icon
                    size="48"
                    color="grey-lighten-2"
                    >mdi-cellphone-off</v-icon
                  >
                  <p class="text-body-2 text-grey mt-3 mb-2">
                    No hay dispositivos conectados
                  </p>
                  <v-btn
                    color="primary"
                    variant="text"
                    size="small"
                    @click="refreshDevices"
                    :loading="refreshing"
                  >
                    <v-icon
                      class="mr-1"
                      size="16"
                      >mdi-refresh</v-icon
                    >
                    Buscar
                  </v-btn>
                </v-card-text>
              </v-card>
            </div>

            <div
              v-else
              class="device-list"
            >
              <v-card
                v-for="device in devices"
                :key="device.id"
                :class="[
                  'device-item mb-3',
                  selectedDevice?.id === device.id
                    ? 'device-item--active bg-primary-lighten-5'
                    : 'bg-grey-lighten-5',
                ]"
                variant="flat"
                @click="selectedDevice = device"
              >
                <v-card-text class="pa-3">
                  <div class="d-flex align-center">
                    <!-- Avatar del dispositivo -->
                    <v-avatar
                      :color="
                        device.platform === 'android'
                          ? 'green-lighten-1'
                          : 'blue-lighten-1'
                      "
                      size="32"
                      class="mr-3"
                    >
                      <v-icon
                        color="white"
                        size="16"
                      >
                        {{
                          device.platform === "android"
                            ? "mdi-android"
                            : "mdi-apple"
                        }}
                      </v-icon>
                    </v-avatar>

                    <!-- Información del dispositivo -->
                    <div class="flex-grow-1">
                      <h4 class="text-subtitle-2 mb-1">{{ device.name }}</h4>
                      <div class="d-flex align-center">
                        <v-chip
                          :color="
                            device.platform === 'android' ? 'green' : 'blue'
                          "
                          size="x-small"
                          variant="tonal"
                          class="mr-2"
                        >
                          {{
                            device.platform === "android" ? "Android" : "iOS"
                          }}
                        </v-chip>
                        <span class="text-caption text-grey">
                          {{
                            device.platform === "android"
                              ? device.android_version
                              : device.ios_version
                          }}
                        </span>
                      </div>
                    </div>

                    <!-- Estado -->
                    <div class="text-right">
                      <v-chip
                        :color="device.active ? 'success' : 'grey-lighten-1'"
                        size="small"
                        variant="flat"
                      >
                        {{ device.active ? "Activo" : "Inactivo" }}
                      </v-chip>
                      <div class="text-caption text-grey mt-1">
                        {{ device.serial.slice(-4) }}
                      </div>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </div>
          </v-col>

          <!-- Panel derecho: Controles del dispositivo -->
          <v-col
            cols="12"
            md="8"
          >
            <div
              v-if="!selectedDevice"
              class="text-center pa-8"
            >
              <v-card
                variant="flat"
                class="bg-grey-lighten-5"
              >
                <v-card-text class="pa-8">
                  <v-icon
                    size="64"
                    color="grey-lighten-2"
                    >mdi-hand-pointing-left</v-icon
                  >
                  <h3 class="text-h6 mt-4 text-grey">
                    Selecciona un dispositivo
                  </h3>
                  <p class="text-body-2 text-grey">
                    Elige un dispositivo de la lista para ver sus controles
                  </p>
                </v-card-text>
              </v-card>
            </div>

            <div v-else>
              <!-- Estado de conexión -->
              <ConnectionStatus
                :device="selectedDevice"
                :is-active="isDeviceActive"
                :loading="actionLoading"
              />

              <!-- Controles específicos del dispositivo -->
              <AndroidControls
                v-if="selectedDevice.platform === 'android'"
                :device="selectedDevice"
                :action-loading="actionLoading"
                @execute-action="executeDeviceActionWithPayload"
              />

              <IOSControls
                v-else-if="selectedDevice.platform === 'ios'"
                :device="selectedDevice"
                :action-loading="actionLoading"
                @execute-action="executeDeviceActionWithPayload"
              />
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <!-- Snackbar minimalista -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
      location="top right"
      variant="flat"
    >
      {{ snackbar.message }}
      <template #actions>
        <v-btn
          color="white"
          variant="text"
          size="small"
          @click="snackbar.show = false"
        >
          <v-icon size="16">mdi-close</v-icon>
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup lang="ts">
  import { ref, onMounted, computed } from "vue";
  import ConnectionStatus from "./components/ConnectionStatus.vue";
  import AndroidControls from "./components/android/AndroidControls.vue";
  import IOSControls from "./components/ios/IOSControls.vue";
  import type { Device, DeviceAction } from "./types";

  // Variables reactivas
  const devices = ref<Device[]>([]);
  const selectedDevice = ref<Device | null>(null);
  const actionLoading = ref(false);
  const isExecutingAction = ref(false);
  const refreshing = ref(false);

  // Snackbar para notificaciones
  const snackbar = ref({
    show: false,
    message: "",
    color: "info",
  });

  // Estado derivado
  const isDeviceActive = computed(() => {
    return selectedDevice.value?.active || false;
  });

  // Función para mostrar notificaciones
  const showNotification = (
    message: string,
    color: "success" | "error" | "warning" | "info" = "info"
  ) => {
    snackbar.value = {
      show: true,
      message,
      color,
    };
  };

  // Función principal para ejecutar acciones
  const executeDeviceActionWithPayload = async (
    action: DeviceAction,
    payload?: any
  ) => {
    if (!selectedDevice.value) return;

    if (isExecutingAction.value) {
      console.log("Acción ya en progreso, ignorando solicitud duplicada");
      return;
    }

    const deviceId = selectedDevice.value.id || selectedDevice.value.serial;
    if (!deviceId) {
      showNotification("Error: Dispositivo sin identificador válido", "error");
      return;
    }

    isExecutingAction.value = true;
    actionLoading.value = true;

    try {
      console.log(`Ejecutando acción: ${action} en dispositivo: ${deviceId}`);
      console.log("Payload:", payload);

      const response = await fetch(
        `http://localhost:5000/api/devices/${deviceId}/action`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            action: action,
            payload: payload,
          }),
        }
      );

      const result = await response.json();

      if (result.success) {
        showNotification(
          result.message || `Acción ${action} ejecutada`,
          "success"
        );

        // Refrescar inmediatamente después de acciones de mirror
        if (action.includes("mirror")) {
          console.log("Refrescando estado después de acción de mirror...");

          // Refrescar múltiples veces para capturar cambio de estado
          await refreshDevices();

          setTimeout(async () => {
            console.log("Refresh 1s después...");
            await refreshDevices();
          }, 1000);

          setTimeout(async () => {
            console.log("Refresh 3s después...");
            await refreshDevices();
          }, 3000);

          setTimeout(async () => {
            console.log("Refresh 5s después...");
            await refreshDevices();
          }, 5000);
        }
      } else {
        showNotification(result.error || `Error ejecutando ${action}`, "error");
      }
    } catch (error) {
      console.error("Error de red:", error);
      showNotification(`Error de conexión ejecutando ${action}`, "error");
    } finally {
      actionLoading.value = false;
      isExecutingAction.value = false;
    }
  };

  // Función para refrescar dispositivos
  const refreshDevices = async () => {
    refreshing.value = true;
    try {
      console.log("Refrescando dispositivos...");

      const response = await fetch("http://localhost:5000/api/devices");

      if (response.ok) {
        const newDevices = await response.json();

        console.log(`${newDevices.length} dispositivos encontrados:`);
        newDevices.forEach((device: Device) => {
          console.log(
            `  - ${device.platform}: ${device.name} - Activo: ${device.active}`
          );
        });

        devices.value = newDevices;

        // Si hay un dispositivo seleccionado, actualizar su estado
        if (selectedDevice.value) {
          const updatedDevice = newDevices.find(
            (d: Device) => d.id === selectedDevice.value?.id
          );

          if (updatedDevice) {
            const wasActive = selectedDevice.value.active;
            selectedDevice.value = updatedDevice;

            // Log cuando cambia el estado
            if (wasActive !== updatedDevice.active) {
              console.log(
                `Estado cambió para ${updatedDevice.name}: ${wasActive} -> ${updatedDevice.active}`
              );

              if (updatedDevice.active) {
                showNotification(
                  `Mirror iniciado para ${updatedDevice.name}`,
                  "success"
                );
              } else {
                showNotification(
                  `Mirror detenido para ${updatedDevice.name}`,
                  "info"
                );
              }
            }
          }
        }
      } else {
        console.error("Error refrescando dispositivos");
        showNotification("Error conectando con el servidor", "error");
      }
    } catch (error) {
      console.error("Error de red al refrescar:", error);
      showNotification("Error de conexión con el servidor", "error");
    } finally {
      refreshing.value = false;
    }
  };

  // Ciclo de vida
  onMounted(async () => {
    await refreshDevices();

    // Seleccionar el primer dispositivo automáticamente
    if (devices.value.length > 0) {
      selectedDevice.value = devices.value[0];
    }

    // Refresh automático cada 5 segundos
    setInterval(refreshDevices, 5000);
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
