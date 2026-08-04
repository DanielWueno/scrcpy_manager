<template>
  <v-card class="mx-auto">
    <v-card-title class="d-flex align-center">
      <v-icon
        :color="statusColor"
        class="me-2"
      >
        {{ statusIcon }}
      </v-icon>
      Mobile Remote Toolkit Extension
    </v-card-title>

    <v-card-text>
      <div class="mb-4">
        <v-alert
          v-if="extensionError"
          type="error"
          variant="tonal"
          :text="extensionError"
          closable
          @click:close="extensionError = null"
        />

        <v-alert
          v-else-if="!isExtensionAvailable && !isExtensionLoading"
          type="warning"
          variant="tonal"
          class="mb-3"
        >
          <v-alert-title>Extensión no detectada</v-alert-title>
          La extensión Mobile Remote Toolkit no está instalada o habilitada.

          <template #append>
            <v-btn
              variant="outlined"
              size="small"
              color="primary"
              @click="openExtensionSetup"
            >
              Instalar
            </v-btn>
          </template>
        </v-alert>

        <v-alert
          v-else-if="isExtensionAvailable && !hasUsbPermission"
          type="info"
          variant="tonal"
          class="mb-3"
        >
          <v-alert-title>Permisos USB requeridos</v-alert-title>
          La extensión necesita permisos para acceder a dispositivos USB.

          <template #append>
            <v-btn
              variant="outlined"
              size="small"
              color="primary"
              :loading="requestingPermission"
              @click="requestPermission"
            >
              Conceder permisos
            </v-btn>
          </template>
        </v-alert>

        <v-alert
          v-else-if="isExtensionAvailable && hasUsbPermission"
          type="success"
          variant="tonal"
          class="mb-3"
        >
          <v-alert-title>Extensión lista</v-alert-title>
          La extensión está funcionando correctamente.
        </v-alert>
      </div>

      <!-- Estado de la extensión -->
      <v-expansion-panels
        v-if="isExtensionAvailable"
        variant="accordion"
      >
        <v-expansion-panel>
          <v-expansion-panel-title>
            <div class="d-flex align-center">
              <v-icon class="me-2">mdi-information-outline</v-icon>
              Estado de la extensión
            </div>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <div class="text-body-2">
              <v-row no-gutters>
                <v-col cols="6">
                  <div class="d-flex align-center mb-2">
                    <v-icon
                      :color="isExtensionAvailable ? 'success' : 'error'"
                      size="small"
                      class="me-2"
                    >
                      {{
                        isExtensionAvailable
                          ? "mdi-check-circle"
                          : "mdi-close-circle"
                      }}
                    </v-icon>
                    Disponible: {{ isExtensionAvailable ? "Sí" : "No" }}
                  </div>

                  <div class="d-flex align-center mb-2">
                    <v-icon
                      :color="isExtensionInitialized ? 'success' : 'warning'"
                      size="small"
                      class="me-2"
                    >
                      {{
                        isExtensionInitialized
                          ? "mdi-check-circle"
                          : "mdi-loading mdi-spin"
                      }}
                    </v-icon>
                    Inicializada: {{ isExtensionInitialized ? "Sí" : "No" }}
                  </div>
                </v-col>

                <v-col cols="6">
                  <div class="d-flex align-center mb-2">
                    <v-icon
                      :color="hasUsbPermission ? 'success' : 'warning'"
                      size="small"
                      class="me-2"
                    >
                      {{
                        hasUsbPermission
                          ? "mdi-check-circle"
                          : "mdi-alert-circle"
                      }}
                    </v-icon>
                    Permisos USB:
                    {{ hasUsbPermission ? "Concedidos" : "Pendientes" }}
                  </div>

                  <div class="d-flex align-center mb-2">
                    <v-icon
                      :color="extensionDeviceCount > 0 ? 'success' : 'info'"
                      size="small"
                      class="me-2"
                    >
                      mdi-devices
                    </v-icon>
                    Dispositivos: {{ extensionDeviceCount }}
                  </div>
                </v-col>
              </v-row>

              <!-- Estado detallado si está disponible -->
              <v-divider class="my-3" />
              <div v-if="extensionStatus">
                <div class="text-caption text-medium-emphasis mb-2">
                  Estado detallado:
                </div>
                <pre class="text-caption bg-surface-variant pa-2 rounded">{{
                  JSON.stringify(extensionStatus, null, 2)
                }}</pre>
              </div>
            </div>
          </v-expansion-panel-text>
        </v-expansion-panel>

        <!-- Lista de dispositivos -->
        <v-expansion-panel v-if="extensionDevices.length > 0">
          <v-expansion-panel-title>
            <div class="d-flex align-center">
              <v-icon class="me-2">mdi-devices</v-icon>
              Dispositivos detectados ({{ extensionDevices.length }})
            </div>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <v-list lines="two">
              <v-list-item
                v-for="device in extensionDevices"
                :key="device.serialNumber"
                :prepend-icon="getDeviceIcon(device)"
              >
                <v-list-item-title>
                  {{ device.productName || "Dispositivo Android" }}
                </v-list-item-title>

                <v-list-item-subtitle>
                  {{ device.serialNumber }}
                </v-list-item-subtitle>

                <template #append>
                  <v-chip
                    :color="getStatusColor(device.status)"
                    size="small"
                    variant="flat"
                  >
                    {{ getStatusText(device.status) }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-card-text>

    <v-card-actions v-if="isExtensionAvailable">
      <v-btn
        variant="outlined"
        :loading="isExtensionLoading"
        @click="refreshDevices"
      >
        <v-icon start>mdi-refresh</v-icon>
        Actualizar dispositivos
      </v-btn>

      <v-spacer />

      <v-btn
        v-if="!hasUsbPermission"
        color="primary"
        :loading="requestingPermission"
        @click="requestPermission"
      >
        Conceder permisos USB
      </v-btn>
    </v-card-actions>

    <!-- Dialog para setup de extensión -->
    <v-dialog
      v-model="showSetupDialog"
      max-width="600"
    >
      <v-card>
        <v-card-title>
          <v-icon class="me-2">mdi-download</v-icon>
          Instalar Mobile Remote Toolkit Extension
        </v-card-title>

        <v-card-text>
          <div class="mb-4">
            <p class="mb-3">
              Para utilizar todas las funcionalidades de gestión de dispositivos
              Android, necesitas instalar la extensión Mobile Remote Toolkit
              para Chrome.
            </p>

            <v-stepper
              v-model="setupStep"
              alt-labels
              class="elevation-0"
            >
              <v-stepper-header>
                <v-stepper-item
                  :complete="setupStep > 1"
                  :value="1"
                  title="Descargar"
                >
                  <template #icon>
                    <v-icon>mdi-download</v-icon>
                  </template>
                </v-stepper-item>

                <v-divider />

                <v-stepper-item
                  :complete="setupStep > 2"
                  :value="2"
                  title="Instalar"
                >
                  <template #icon>
                    <v-icon>mdi-puzzle</v-icon>
                  </template>
                </v-stepper-item>

                <v-divider />

                <v-stepper-item
                  :complete="setupStep > 3"
                  :value="3"
                  title="Activar"
                >
                  <template #icon>
                    <v-icon>mdi-check</v-icon>
                  </template>
                </v-stepper-item>
              </v-stepper-header>

              <v-stepper-window>
                <v-stepper-window-item :value="1">
                  <div class="pa-4">
                    <p class="mb-3">Descarga el archivo de la extensión:</p>
                    <v-btn
                      color="primary"
                      block
                      :loading="downloadingExtension"
                      @click="downloadExtension"
                    >
                      <v-icon start>mdi-download</v-icon>
                      Descargar Mobile Remote Toolkit Extension
                    </v-btn>
                  </div>
                </v-stepper-window-item>

                <v-stepper-window-item :value="2">
                  <div class="pa-4">
                    <p class="mb-3">Instala la extensión en Chrome:</p>
                    <ol class="text-body-2">
                      <li>
                        Abre Chrome y ve a <code>chrome://extensions/</code>
                      </li>
                      <li>
                        Activa el "Modo de desarrollador" (esquina superior
                        derecha)
                      </li>
                      <li>Haz clic en "Cargar extensión sin empaquetar"</li>
                      <li>
                        Selecciona la carpeta descomprimida de la extensión
                      </li>
                    </ol>
                  </div>
                </v-stepper-window-item>

                <v-stepper-window-item :value="3">
                  <div class="pa-4">
                    <p class="mb-3">
                      Activa la extensión y recarga esta página:
                    </p>
                    <v-btn
                      color="primary"
                      block
                      @click="checkExtensionStatus"
                    >
                      <v-icon start>mdi-refresh</v-icon>
                      Verificar instalación
                    </v-btn>
                  </div>
                </v-stepper-window-item>
              </v-stepper-window>
            </v-stepper>
          </div>
        </v-card-text>

        <v-card-actions>
          <v-btn
            variant="text"
            @click="showSetupDialog = false"
          >
            Cerrar
          </v-btn>

          <v-spacer />

          <v-btn
            v-if="setupStep < 3"
            @click="setupStep++"
          >
            Siguiente
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup lang="ts">
  import { ref, computed, onMounted } from "vue";
  import { useMobileRemoteToolkit } from "../composables/useMobileRemoteToolkit";
  import { extensionApi } from "../services/api";
  import type { ExtensionDevice, ExtensionStatus } from "../types/extension";

  // Composable
  const {
    extensionDevices,
    isExtensionLoading,
    extensionError,
    isExtensionAvailable,
    isExtensionInitialized,
    hasUsbPermission,
    extensionDeviceCount,
    requestExtensionUsbPermission,
    refreshExtensionDevices,
    getExtensionStatus,
  } = useMobileRemoteToolkit();

  // Estado local
  const requestingPermission = ref(false);
  const showSetupDialog = ref(false);
  const setupStep = ref(1);
  const downloadingExtension = ref(false);
  const downloadProgress = ref(0);
  const extensionStatus = ref<ExtensionStatus | null>(null);

  // Computed
  const statusColor = computed(() => {
    if (!isExtensionAvailable.value) return "error";
    if (!hasUsbPermission.value) return "warning";
    return "success";
  });

  const statusIcon = computed(() => {
    if (!isExtensionAvailable.value) return "mdi-close-circle";
    if (!hasUsbPermission.value) return "mdi-alert-circle";
    return "mdi-check-circle";
  });

  // Métodos
  async function requestPermission(): Promise<void> {
    try {
      requestingPermission.value = true;
      await requestExtensionUsbPermission();
    } catch (err) {
      console.error("Error requesting USB permission:", err);
    } finally {
      requestingPermission.value = false;
    }
  }

  async function refreshDevices(): Promise<void> {
    try {
      await refreshExtensionDevices();
      extensionStatus.value = getExtensionStatus();
    } catch (err) {
      console.error("Error refreshing devices:", err);
    }
  }

  function openExtensionSetup(): void {
    showSetupDialog.value = true;
    setupStep.value = 1;
  }

  async function downloadExtension(): Promise<void> {
    try {
      downloadingExtension.value = true;

      // Obtener información de la extensión desde la API
      const info = await extensionApi.getMobileRemoteToolkitInfo();

      if (!info.available) {
        throw new Error("Extensión no disponible en el servidor");
      }

      // Simular progreso de descarga
      const progressInterval = setInterval(() => {
        downloadProgress.value += 10;
        if (downloadProgress.value >= 100) {
          clearInterval(progressInterval);
        }
      }, 200);

      // Crear enlace de descarga usando la API
      const downloadUrl = extensionApi.getDownloadUrl();

      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = `mobile-remote-toolkit-extension-v${info.version}.zip`;
      link.target = "_blank";

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Limpiar progreso
      setTimeout(() => {
        clearInterval(progressInterval);
        setupStep.value = 2;
      }, 2000);
    } catch (err) {
      console.error("Error downloading extension:", err);
    } finally {
      downloadingExtension.value = false;
    }
  }

  function checkExtensionStatus(): void {
    // Recargar la página para verificar la extensión
    window.location.reload();
  }

  function getDeviceIcon(device: ExtensionDevice): string {
    switch (device.status) {
      case "adb_ready":
        return "mdi-check-circle";
      case "connected":
        return "mdi-usb";
      case "unauthorized":
        return "mdi-lock";
      case "no_adb":
        return "mdi-wifi-off";
      default:
        return "mdi-help-circle";
    }
  }

  function getStatusColor(status: string): string {
    switch (status) {
      case "adb_ready":
        return "success";
      case "connected":
        return "info";
      case "unauthorized":
        return "warning";
      case "no_adb":
        return "error";
      default:
        return "grey";
    }
  }

  function getStatusText(status: string): string {
    switch (status) {
      case "adb_ready":
        return "Listo";
      case "connected":
        return "Conectado";
      case "unauthorized":
        return "No autorizado";
      case "no_adb":
        return "Sin ADB";
      default:
        return "Desconocido";
    }
  }

  // Inicialización
  onMounted(() => {
    extensionStatus.value = getExtensionStatus();
  });
</script>

<style scoped>
  .v-stepper {
    background: transparent !important;
  }

  .text-caption {
    font-family: "Courier New", monospace;
  }
</style>
