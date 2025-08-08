<!-- filepath: c:\Users\DSOFT03.CORP\Documents\Soft\scrcpy_manager\scrcpy-manager-vue\src\components\ios\IOSControls.vue -->
<template>
  <v-card
    v-if="device"
    class="mb-4"
  >
    <v-card-title class="d-flex align-center">
      <v-icon class="mr-2">mdi-gesture-tap</v-icon>
      Controles iOS
    </v-card-title>

    <v-card-text>
      <!-- Botón de mirror existente... -->
      <div class="mb-4">
        <v-btn
          :color="device.active ? 'error' : 'primary'"
          :loading="actionLoading"
          @click="toggleMirror"
          block
          size="large"
        >
          <v-icon class="mr-2">
            {{ device.active ? "mdi-stop" : "mdi-play" }}
          </v-icon>
          {{ device.active ? "Detener Mirror" : "Iniciar Mirror" }}
        </v-btn>
      </div>

      <!-- ✅ AGREGAR: Mostrar URL del stream cuando esté activo -->
      <v-expand-transition>
        <div v-if="device.active && mirrorSession" class="mb-4">
          <v-alert
            type="success"
            variant="outlined"
            class="mb-3"
          >
            <v-alert-title>Mirror iOS Activo</v-alert-title>
            <div class="d-flex align-center justify-space-between">
              <span>Stream: <code>{{ getStreamUrl() }}</code></span>
              <v-btn
                :href="getStreamUrl()"
                target="_blank"
                variant="outlined"
                size="small"
                color="success"
              >
                <v-icon class="mr-1">mdi-open-in-new</v-icon>
                Abrir
              </v-btn>
            </div>
          </v-alert>
        </div>
      </v-expand-transition>

      <!-- Opciones de mirror (cuando no está activo) -->
      <v-expand-transition>
        <div v-if="!device.active" class="mb-4">
          <v-divider class="mb-3" />
          <div class="text-subtitle2 mb-2">Opciones de Mirror:</div>

          <v-row dense>
            <v-col cols="6">
              <v-text-field
                v-model.number="mirrorOptions.port"
                label="Puerto"
                type="number"
                density="compact"
                variant="outlined"
                :min="8000"
                :max="9999"
              />
            </v-col>
            <v-col cols="6">
              <v-select
                v-model="mirrorOptions.interface"
                label="Interfaz"
                :items="interfaceOptions"
                density="compact"
                variant="outlined"
              />
            </v-col>
          </v-row>

          <v-row dense>
            <v-col cols="6">
              <v-checkbox
                v-model="mirrorOptions.stream"
                label="Habilitar Stream"
                density="compact"
                hide-details
              />
            </v-col>
            <v-col cols="6">
              <v-checkbox
                v-model="mirrorOptions.verbose"
                label="Modo Verbose"
                density="compact"
                hide-details
              />
            </v-col>
          </v-row>
        </div>
      </v-expand-transition>

      <!-- Controles del dispositivo -->
      <v-divider class="mb-3" />
      <div class="text-subtitle2 mb-2">Controles del Dispositivo:</div>

      <v-row dense>
        <v-col cols="6">
          <v-btn
            variant="outlined"
            block
            :loading="actionLoading"
            @click="executeAction('ios_home_button')"
          >
            <v-icon class="mr-1">mdi-home</v-icon>
            Home
          </v-btn>
        </v-col>
        <v-col cols="6">
          <v-btn
            variant="outlined"
            block
            :loading="actionLoading"
            @click="executeAction('ios_lock_device')"
          >
            <v-icon class="mr-1">mdi-lock</v-icon>
            Bloquear
          </v-btn>
        </v-col>
      </v-row>

      <v-row
        dense
        class="mt-2"
      >
        <v-col cols="4">
          <v-btn
            variant="outlined"
            block
            size="small"
            :loading="actionLoading"
            @click="executeAction('ios_volume_up')"
          >
            <v-icon>mdi-volume-plus</v-icon>
          </v-btn>
        </v-col>
        <v-col cols="4">
          <v-btn
            variant="outlined"
            block
            size="small"
            :loading="actionLoading"
            @click="executeAction('ios_volume_down')"
          >
            <v-icon>mdi-volume-minus</v-icon>
          </v-btn>
        </v-col>
        <v-col cols="4">
          <v-btn
            variant="outlined"
            block
            size="small"
            :loading="actionLoading"
            @click="executeAction('ios_screenshot')"
          >
            <v-icon>mdi-camera</v-icon>
          </v-btn>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
  import { ref, computed } from "vue";
  import type { IOSDevice, IOSAction, IOSMirrorSession } from "../../types/ios";

  interface Props {
    device: IOSDevice | null;
    actionLoading: boolean;
    mirrorSession?: IOSMirrorSession | null;
  }

  interface Emits {
    (e: "execute-action", action: IOSAction, payload?: any): void;
  }

  const props = defineProps<Props>();
  const emit = defineEmits<Emits>();

  // Opciones de mirror actualizadas
  const mirrorOptions = ref({
    port: 8000,
    interface: 'none',
    stream: true,
    verbose: false
  });

  const interfaceOptions = [
    { title: 'Ninguna (Solo local)', value: 'none' },
    { title: 'Todas (0.0.0.0)', value: '0.0.0.0' },
    { title: 'localhost', value: '127.0.0.1' }
  ];

  const getStreamUrl = () => {
    if (!props.mirrorSession) return '';
    const port = props.mirrorSession.port || 8000;
    return `http://localhost:${port}`;
  };

  const toggleMirror = () => {
    if (!props.device) return;

    if (props.device.active) {
      executeAction("ios_stop_mirror");
    } else {
      executeAction("ios_mirror", mirrorOptions.value);
    }
  };

  const executeAction = (action: IOSAction, payload?: any) => {
    emit("execute-action", action, payload);
  };
</script>
