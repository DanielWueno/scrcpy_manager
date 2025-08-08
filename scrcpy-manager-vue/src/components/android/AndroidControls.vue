<template>
  <v-card class="mb-4">
    <v-card-title class="d-flex align-center">
      <v-icon
        class="mr-2"
        color="green"
        >mdi-android</v-icon
      >
      <span>Controles Android</span>
    </v-card-title>

    <v-card-text>
      <!-- ✅ Opciones de Mirror con switches -->
      <v-card
        class="mb-4"
        variant="outlined"
      >
        <v-card-subtitle class="pb-2">
          <v-icon
            class="mr-1"
            size="16"
            >mdi-settings</v-icon
          >
          Opciones de Mirror
        </v-card-subtitle>

        <v-card-text class="pt-0">
          <!-- ✅ Switches para opciones -->
          <v-row
            dense
            class="mb-3"
          >
            <v-col cols="6">
              <v-switch
                v-model="mirrorOptions.stayAwake"
                color="success"
                hide-details
                density="compact"
              >
                <template #label>
                  <div class="d-flex align-center">
                    <v-icon
                      class="mr-1"
                      size="16"
                      >mdi-eye</v-icon
                    >
                    <span class="text-caption">Mantener Despierto</span>
                  </div>
                </template>
              </v-switch>
            </v-col>

            <v-col cols="6">
              <v-switch
                v-model="mirrorOptions.noAudio"
                color="primary"
                hide-details
                density="compact"
              >
                <template #label>
                  <div class="d-flex align-center">
                    <v-icon
                      class="mr-1"
                      size="16"
                      >mdi-volume-off</v-icon
                    >
                    <span class="text-caption">Sin Audio</span>
                  </div>
                </template>
              </v-switch>
            </v-col>

            <v-col cols="6">
              <v-switch
                v-model="mirrorOptions.showTouches"
                color="warning"
                hide-details
                density="compact"
              >
                <template #label>
                  <div class="d-flex align-center">
                    <v-icon
                      class="mr-1"
                      size="16"
                      >mdi-hand-pointing-up</v-icon
                    >
                    <span class="text-caption">Mostrar Toques</span>
                  </div>
                </template>
              </v-switch>
            </v-col>

            <v-col cols="6">
              <v-switch
                v-model="mirrorOptions.turnScreenOff"
                color="purple"
                hide-details
                density="compact"
              >
                <template #label>
                  <div class="d-flex align-center">
                    <v-icon
                      class="mr-1"
                      size="16"
                      >mdi-monitor-off</v-icon
                    >
                    <span class="text-caption">Apagar Pantalla</span>
                  </div>
                </template>
              </v-switch>
            </v-col>
          </v-row>

          <!-- ✅ Botón principal de mirror -->
          <v-btn
            :color="device.active ? 'error' : 'success'"
            :variant="'elevated'"
            :loading="actionLoading"
            :disabled="actionLoading"
            size="large"
            block
            @click="toggleMirror"
          >
            <v-icon class="mr-2">
              {{ device.active ? "mdi-stop" : "mdi-play" }}
            </v-icon>
            {{ device.active ? "Detener Mirror" : "Iniciar Mirror" }}
          </v-btn>

          <!-- ✅ Información de opciones activas -->
          <div
            v-if="hasActiveOptions"
            class="mt-2"
          >
            <v-chip-group>
              <v-chip
                v-if="mirrorOptions.stayAwake"
                size="x-small"
                color="success"
              >
                <v-icon
                  start
                  size="12"
                  >mdi-eye</v-icon
                >
                Despierto
              </v-chip>
              <v-chip
                v-if="mirrorOptions.noAudio"
                size="x-small"
                color="primary"
              >
                <v-icon
                  start
                  size="12"
                  >mdi-volume-off</v-icon
                >
                Sin Audio
              </v-chip>
              <v-chip
                v-if="mirrorOptions.showTouches"
                size="x-small"
                color="warning"
              >
                <v-icon
                  start
                  size="12"
                  >mdi-hand-pointing-up</v-icon
                >
                Toques
              </v-chip>
              <v-chip
                v-if="mirrorOptions.turnScreenOff"
                size="x-small"
                color="purple"
              >
                <v-icon
                  start
                  size="12"
                  >mdi-monitor-off</v-icon
                >
                Pantalla Off
              </v-chip>
            </v-chip-group>
          </div>
        </v-card-text>
      </v-card>

      <!-- ✅ Controles de dispositivo -->
      <v-card variant="outlined">
        <v-card-subtitle class="pb-2">
          <v-icon
            class="mr-1"
            size="16"
            >mdi-gamepad</v-icon
          >
          Controles del Dispositivo
        </v-card-subtitle>

        <v-card-text class="pt-0">
          <v-row dense>
            <!-- Despertar dispositivo -->
            <v-col cols="12">
              <v-btn
                color="orange"
                variant="outlined"
                :loading="actionLoading"
                :disabled="actionLoading"
                size="large"
                block
                @click="$emit('execute-action', 'wake_device')"
              >
                <v-icon class="mr-2">mdi-power</v-icon>
                Encender Pantalla
              </v-btn>
            </v-col>

            <!-- Botones de navegación -->
            <v-col cols="4">
              <v-btn
                color="info"
                variant="outlined"
                :loading="actionLoading"
                :disabled="actionLoading"
                size="large"
                block
                @click="$emit('execute-action', 'home_button')"
              >
                <v-icon>mdi-home</v-icon>
              </v-btn>
            </v-col>

            <v-col cols="4">
              <v-btn
                color="info"
                variant="outlined"
                :loading="actionLoading"
                :disabled="actionLoading"
                size="large"
                block
                @click="$emit('execute-action', 'back_button')"
              >
                <v-icon>mdi-arrow-left</v-icon>
              </v-btn>
            </v-col>

            <v-col cols="4">
              <v-btn
                color="success"
                variant="outlined"
                :loading="actionLoading"
                :disabled="actionLoading"
                size="large"
                block
                @click="$emit('execute-action', 'screenshot')"
              >
                <v-icon>mdi-camera</v-icon>
              </v-btn>
            </v-col>

            <!-- Controles de volumen -->
            <v-col cols="6">
              <v-btn
                color="grey"
                variant="outlined"
                :loading="actionLoading"
                :disabled="actionLoading"
                size="large"
                block
                @click="$emit('execute-action', 'volume_up')"
              >
                <v-icon class="mr-2">mdi-volume-plus</v-icon>
                Vol +
              </v-btn>
            </v-col>

            <v-col cols="6">
              <v-btn
                color="grey"
                variant="outlined"
                :loading="actionLoading"
                :disabled="actionLoading"
                size="large"
                block
                @click="$emit('execute-action', 'volume_down')"
              >
                <v-icon class="mr-2">mdi-volume-minus</v-icon>
                Vol -
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
  import { ref, computed } from "vue";
  import type { Device } from "../../types";

  interface Props {
    device: Device;
    actionLoading: boolean;
  }

  const props = defineProps<Props>();

  const emit = defineEmits<{
    "execute-action": [action: string, payload?: any];
  }>();

  // Opciones por defecto
  const mirrorOptions = ref({
    stayAwake: true,
    noAudio: true,
    showTouches: false,
    turnScreenOff: false,
  });

  // Computed para saber si hay opciones activas
  const hasActiveOptions = computed(() => {
    return (
      mirrorOptions.value.stayAwake ||
      mirrorOptions.value.noAudio ||
      mirrorOptions.value.showTouches ||
      mirrorOptions.value.turnScreenOff
    );
  });

  // Función para alternar mirror con opciones actuales
  const toggleMirror = () => {
    if (props.device.active) {
      // Si está activo, detenerlo
      emit("execute-action", "mirror_screen_off");
    } else {
      // Si está inactivo, iniciarlo con opciones actuales
      console.log("Iniciando mirror con opciones:", mirrorOptions.value);

      // ✅ Convertir a objeto plano sin Proxy
      const plainOptions = {
        stayAwake: mirrorOptions.value.stayAwake,
        noAudio: mirrorOptions.value.noAudio,
        showTouches: mirrorOptions.value.showTouches,
        turnScreenOff: mirrorOptions.value.turnScreenOff,
      };

      console.log("Opciones planas:", plainOptions);
      emit("execute-action", "mirror_screen_on", plainOptions);
    }
  };
</script>
