<!-- filepath: c:\Users\DSOFT03.CORP\Documents\Soft\scrcpy_manager\scrcpy-manager-vue\src\components\ConnectionStatus.vue -->
<template>
  <v-card class="mb-4">
    <v-card-text>
      <div class="d-flex align-center justify-space-between">
        <div class="d-flex align-center">
          <!-- ✅ Indicador visual mejorado -->
          <v-avatar
            :color="isActive ? 'success' : 'grey'"
            size="12"
            class="mr-3"
          >
            <v-icon
              size="8"
              :color="isActive ? 'white' : 'grey-lighten-1'"
            >
              mdi-circle
            </v-icon>
          </v-avatar>

          <div>
            <h3 class="text-h6 mb-1">
              {{ device.name }}
            </h3>
            <div class="d-flex align-center">
              <v-chip
                :color="device.platform === 'android' ? 'green' : 'blue'"
                size="small"
                variant="elevated"
                class="mr-2"
              >
                <v-icon
                  start
                  size="16"
                >
                  {{
                    device.platform === "android" ? "mdi-android" : "mdi-apple"
                  }}
                </v-icon>
                {{ device.platform === "android" ? "Android" : "iOS" }}
              </v-chip>

              <!-- ✅ Estado del mirror más claro -->
              <v-chip
                :color="isActive ? 'success' : 'grey'"
                size="small"
                variant="tonal"
              >
                <v-icon
                  start
                  size="16"
                >
                  {{ isActive ? "mdi-monitor-eye" : "mdi-monitor-off" }}
                </v-icon>
                {{ isActive ? "Mirror Activo" : "Mirror Inactivo" }}
              </v-chip>
            </div>
          </div>
        </div>

        <!-- ✅ Solo información del dispositivo, sin botón -->
        <div class="text-right">
          <v-chip
            :color="device.platform === 'android' ? 'green' : 'blue'"
            variant="outlined"
            size="small"
          >
            {{ device.model || "Dispositivo" }}
          </v-chip>
          <div class="text-caption text-medium-emphasis mt-1">
            {{
              device.platform === "android"
                ? device.android_version
                : device.ios_version
            }}
          </div>
        </div>
      </div>

      <!-- ✅ Información adicional cuando está activo -->
      <v-expand-transition>
        <div
          v-if="isActive"
          class="mt-3"
        >
          <v-alert
            type="success"
            variant="tonal"
            density="compact"
          >
            <div class="d-flex align-center">
              <v-icon
                class="mr-2"
                size="16"
                >mdi-information</v-icon
              >
              <span>
                Mirror en ejecución - Controla el dispositivo desde la ventana
                scrcpy
              </span>
            </div>
          </v-alert>
        </div>
      </v-expand-transition>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
  import type { Device } from "../types";

  interface Props {
    device: Device;
    isActive: boolean;
    loading: boolean;
  }

  defineProps<Props>();

  // ✅ Ya no emitimos toggle-connection
  defineEmits<{
    // Eliminar: 'toggle-connection': [];
  }>();
</script>
